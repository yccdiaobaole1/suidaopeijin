import math
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor

from src.calculator import TunnelCalculator
from src.rebar_manager import RebarManager
from src.concrete_manager import ConcreteManager
from src.code_constraints import CodeConstraints


class StructuralSolver:
    """
    Helper solver used by NSGA-II:
    1) inverse solve minimum steel area for ULS/SLS bounds
    2) post-design stirrups and distribution rebars
    """

    def __init__(self):
        self.rm = RebarManager()
        self.cm = ConcreteManager()
        self.calc = TunnelCalculator(self.rm, self.cm)
        self.constraints = CodeConstraints()

    def _inverse_solve_min_area(self, section_params: Dict, force_envelope: List[Dict]) -> float:
        """
        Inverse solve minimum required area across all envelope points.
        - ULS by bisection
        - SLS by bisection with reference diameter D22
        """
        b = section_params['b']
        h = section_params['h']

        # Code minimum total ratio (仅用于参考，不用作单侧下界)
        as_min_code = self.constraints.MIN_RHO_TOTAL * b * h

        # Part A: ULS requirement
        # 修正: 对称配筋下，单侧面积下界应为 MIN_RHO_SINGLE（0.2%），
        # 而非 MIN_RHO_TOTAL（0.4%）；否则双侧总配筋率起步为 0.8%，浪费钢筋
        low = self.constraints.MIN_RHO_SINGLE * b * h
        high = 0.04 * b * h

        min_sf = section_params.get("min_safety_factor_uls", self.constraints.MIN_SAFETY_FACTOR_ULS)
        temp_rebar_uls = {
            'grade': 'HRB400',
            'diameter': 20,
            'count': 0,
            'spacing': 150,
        }

        for _ in range(20):
            mid_as = (low + high) / 2.0
            area_20 = 314.16
            temp_rebar_uls['count'] = mid_as / area_20

            all_safe_uls = True
            for forces in force_envelope:
                res = self.calc.verify_structure(section_params, forces, temp_rebar_uls)
                if (not res.get('is_safe', False)) or (res.get('safety_factor', 0.0) < min_sf):
                    all_safe_uls = False
                    break

            if all_safe_uls:
                high = mid_as
            else:
                low = mid_as

        as_req_uls = high
        print(f"  > ULS Req: {as_req_uls:.0f} mm2")

        # Part B: SLS requirement (reference D22)
        low_sls = as_req_uls
        high_sls = 0.05 * b * h

        ref_area = 380.13  # D22
        temp_rebar_sls = {
            'grade': 'HRB400',
            'diameter': 22,
            'count': 0,
            'spacing': 150,
        }

        temp_rebar_sls['count'] = as_req_uls / ref_area
        all_pass_sls_initial = True
        for forces in force_envelope:
            res = self.calc.verify_structure(section_params, forces, temp_rebar_sls)
            if not res.get('is_safe', False):
                all_pass_sls_initial = False
                break

        if all_pass_sls_initial:
            final_as_sls = as_req_uls
            print(f"  > SLS Req (D22): <= ULS ({final_as_sls:.0f} mm2)")
        else:
            for _ in range(15):
                mid_as = (low_sls + high_sls) / 2.0
                temp_rebar_sls['count'] = mid_as / ref_area

                all_pass = True
                for forces in force_envelope:
                    res = self.calc.verify_structure(section_params, forces, temp_rebar_sls)
                    if not res.get('is_safe', False):
                        all_pass = False
                        break

                if all_pass:
                    high_sls = mid_as
                else:
                    low_sls = mid_as

            final_as_sls = high_sls
            print(f"  > SLS Req (D22): {final_as_sls:.0f} mm2")

        return max(as_req_uls, final_as_sls)

    def _calc_shear_without_stirrup(self, section_params: Dict, force_params: Dict, rebar_params: Dict) -> Dict:
        # 与 calculator.verify_shear 共用同一套口径，避免公式实现分叉
        trial_rebar = dict(rebar_params)
        trial_rebar.pop('stirrup', None)
        res = self.calc.verify_shear(section_params, force_params, trial_rebar)
        return {
            'V_d': res.get('shear_demand', 0.0),
            'Vc': res.get('Vc', 0.0),
            'V_max': res.get('shear_limit', 0.0),
            'h0': res.get('h0', 1.0),
            'lambda': res.get('lambda', 3.0),
            'N_calc': res.get('N_calc', 0.0),
            'shear_assumptions': res.get('shear_assumptions', {}),
        }

    def _build_stirrup_candidates(self, section_params: Dict, main_rebar: Dict, required_asv_over_s: float) -> List[Dict]:
        main_d = float(main_rebar.get('diameter', 20))
        min_dia = max(self.constraints.MIN_DIA_STIRRUP, int(math.ceil(0.25 * main_d)))
        max_dia = self.constraints.MAX_DIA_STIRRUP
        max_spacing = int(section_params.get('stirrup_max_spacing', self.constraints.MAX_SPACING_STIRRUP))
        max_spacing = min(max_spacing, self.constraints.MAX_SPACING_STIRRUP)
        min_spacing = int(section_params.get('stirrup_min_spacing', 100))
        min_spacing = max(80, min_spacing)

        dia_series = [6, 8, 10, 12, 14, 16, 18, 20]
        dia_series = [d for d in dia_series if min_dia <= d <= max_dia]
        fixed_dia = section_params.get('stirrup_diameter')
        if fixed_dia is not None:
            d_fix = int(fixed_dia)
            if min_dia <= d_fix <= max_dia:
                dia_series = [d_fix]
        if not dia_series:
            dia_series = [min(max_dia, max(min_dia, 8))]

        spacing_series = section_params.get('stirrup_spacing_series')
        if isinstance(spacing_series, list) and spacing_series:
            candidate_spacings = [int(x) for x in spacing_series]
        else:
            candidate_spacings = [400, 350, 300, 250, 220, 200, 180, 160, 150, 140, 125, 120, 100]
        candidate_spacings = [s for s in candidate_spacings if min_spacing <= s <= max_spacing]
        candidate_spacings = sorted(set(candidate_spacings), reverse=True)
        if not candidate_spacings:
            candidate_spacings = [max_spacing]

        grade = section_params.get('stirrup_grade', 'HPB300')
        # 拉筋级别搜索：支持多级别候选（默认 HPB300 + HRB400）
        stirrup_grades_cfg = section_params.get('stirrup_grades')
        if isinstance(stirrup_grades_cfg, list) and stirrup_grades_cfg:
            grade_series = list(stirrup_grades_cfg)
        else:
            grade_series = [grade] if grade != 'HPB300' else ['HPB300', 'HRB400']
        uplift = max(0.0, float(section_params.get('stirrup_asv_over_s_uplift', 0.35)))
        upper_asv_over_s = required_asv_over_s * (1.0 + uplift)

        template_items = section_params.get('stirrup_templates')
        templates = []
        if isinstance(template_items, list) and template_items:
            for item in template_items:
                if not isinstance(item, dict):
                    continue
                name = str(item.get('name', '')).strip() or 'layout'
                legs = max(2, int(item.get('legs', section_params.get('stirrup_legs', 2))))
                templates.append({'name': name, 'legs': legs})
        if not templates:
            # 优化：同时考虑2肢和4肢
            templates = [{'name': 'layout', 'legs': 2}, {'name': 'layout', 'legs': 4}]

        candidates: List[Dict] = []
        for g in grade_series:
            fyv_g = self.rm.get_design_value(g)
            if fyv_g <= 1e-9:
                continue
            for tpl in templates:
                legs = tpl['legs']
                layout = tpl['name']
                for dia in dia_series:
                    area = math.pi * dia * dia / 4.0
                    asv = legs * area
                    for spacing in candidate_spacings:
                        spacing = float(spacing)
                        asv_over_s = asv / spacing if spacing > 0 else 0.0
                        if asv_over_s + 1e-9 < required_asv_over_s:
                            continue
                        within_uplift = asv_over_s <= upper_asv_over_s + 1e-9
                        candidates.append({
                            'grade': g,
                            'diameter': dia,
                            'legs': legs,
                            'layout': layout,
                            'spacing': spacing,
                            'Asv': asv,
                            'Asv_over_s': asv_over_s,
                            'fyv': fyv_g,
                            'within_uplift': within_uplift,
                        })

        # 若上浮范围过窄导致无候选，回退到仅满足下限 Asv/s
        if candidates and any(c['within_uplift'] for c in candidates):
            candidates = [c for c in candidates if c['within_uplift']]
        return candidates

    def _calc_stirrup_cost(self, stirrup: Dict, section_params: Dict) -> float:
        """计算拉筋成本（元/m）
        隧道衬砌拉筋为直拉筋（两端弯钩），单根长度 = h + 2×弯钩长。
        弯钩按135°标准弯钩：HPB300取10d，HRB400/500取10d（工程惯例）。
        """
        d = stirrup['diameter']
        s = stirrup['spacing']
        grade = stirrup['grade']
        legs = stirrup.get('legs', 2)

        props = self.rm.get_bar_properties(d)
        weight_per_m = props['weight']
        price_unit = self.rm.get_price(grade, d)

        h = section_params['h']
        # 直拉筋：单根长度 = 截面高度 + 两端弯钩（每端10d）
        hook_length = 10 * d  # mm，135°弯钩工程惯例
        bar_length_m = (h + 2 * hook_length) / 1000.0

        # legs根直拉筋每延米用量：legs × bar_length_m × (1000/s)
        total_weight_per_m = weight_per_m * bar_length_m * legs * (1000.0 / s)
        cost = (total_weight_per_m / 1000.0) * price_unit

        return cost

    @staticmethod
    def _pareto_front(candidates: List[Dict]) -> List[Dict]:
        if not candidates:
            return []

        def dominates(a: Dict, b: Dict) -> bool:
            oa = a['objs']
            ob = b['objs']
            no_worse = all(x <= y for x, y in zip(oa, ob))
            strictly_better = any(x < y for x, y in zip(oa, ob))
            return no_worse and strictly_better

        front = []
        for i, a in enumerate(candidates):
            dominated = False
            for j, b in enumerate(candidates):
                if i == j:
                    continue
                if dominates(b, a):
                    dominated = True
                    break
            if not dominated:
                front.append(a)
        return front

    def _design_distribution_rebar(
        self,
        main_rebar: Dict,
        section_params: Dict,
        stirrup: Optional[Dict],
    ) -> Dict:
        b = section_params['b']
        c = section_params.get('cover', self.constraints.DEFAULT_COVER)

        main_d = main_rebar.get('diameter', 20)
        main_n = max(2, int(round(main_rebar.get('count', 2))))
        main_bar_area = self.rm.get_bar_properties(main_d)['area']
        as_main = main_n * main_bar_area

        dist_grade = section_params.get('dist_grade', main_rebar.get('grade', 'HRB400'))
        # 分布筋级别搜索：支持多级别候选（默认 HPB300 + HRB400）
        dist_grades_cfg = section_params.get('dist_grades')
        if isinstance(dist_grades_cfg, list) and dist_grades_cfg:
            dist_grade_series = list(dist_grades_cfg)
        else:
            dist_grade_series = ['HPB300', 'HRB400']

        # TB 10064-2019 9.1.7: 配筋不宜小于受力钢筋的15%，且配筋率不宜小于0.15%
        ratio = section_params.get('dist_ratio_to_main', 0.15)
        as_required_by_main = max(0.0, ratio * as_main)

        # 配筋率检查: ρ = As/(b×h) ≥ 0.0015
        h = section_params.get('h', 500)
        as_required_by_ratio = self.constraints.MIN_RATIO_DIST * b * h

        as_required = max(as_required_by_main, as_required_by_ratio)

        min_dist_dia = int(section_params.get('dist_min_dia', self.constraints.MIN_DIA_DIST))
        min_dist_dia = max(self.constraints.MIN_DIA_DIST, min_dist_dia)

        max_dist_spacing = int(section_params.get('dist_max_spacing', self.constraints.MAX_SPACING_DISTRIBUTION))
        max_dist_spacing = min(max_dist_spacing, self.constraints.MAX_SPACING_DISTRIBUTION)

        # TB 10064-2019 9.1.7: 分布筋间距不宜小于150mm
        min_dist_spacing = int(section_params.get('dist_min_spacing', self.constraints.MIN_SPACING_DISTRIBUTION))
        min_dist_spacing = max(min_dist_spacing, self.constraints.MIN_SPACING_DISTRIBUTION)

        follow_stirrup = section_params.get('dist_follow_stirrup', False)
        if follow_stirrup and stirrup:
            max_dist_spacing = min(max_dist_spacing, int(stirrup.get('spacing', max_dist_spacing)))

        diameters = [6, 8, 10, 12, 14, 16, 18, 20, 22]
        diameters = [d for d in diameters if min_dist_dia <= d <= self.constraints.MAX_DIA_DIST]
        if not diameters:
            diameters = [self.constraints.MIN_DIA_DIST]

        best = None
        for g in dist_grade_series:
            price_factor = self.rm.get_price(g, 10)  # 用于成本比较的参考单价
            for dia in diameters:
                area = self.rm.get_bar_properties(dia)['area']
                b_eff = b - 2 * c - dia
                if b_eff <= 0:
                    continue

                min_count_by_spacing = max(2, int(math.ceil(b_eff / max_dist_spacing)) + 1)
                min_count_by_area = max(2, int(math.ceil(as_required / area)))
                count = max(min_count_by_spacing, min_count_by_area)

                # 最小间距约束：间距≥min_dist_spacing → 根数不超过上限
                # max_count = floor(b_eff / min_dist_spacing) + 1
                if min_dist_spacing > 0:
                    max_count_by_min_spacing = int(math.floor(b_eff / min_dist_spacing)) + 1
                    count = min(count, max_count_by_min_spacing)

                actual_spacing = b_eff / (count - 1) if count > 1 else b_eff
                actual_spacing = math.floor(actual_spacing)  # 施工间距取整数
                clear_spacing = actual_spacing - dia
                if clear_spacing < self.constraints.get_min_clear_spacing(dia):
                    continue

                as_provided = count * area
                if as_provided + 1e-9 < as_required:
                    continue

                overuse = as_provided - as_required
                # 成本估算：重量 × 单价
                weight_per_m = self.rm.get_bar_properties(dia)['weight']
                unit_price = self.rm.get_price(g, dia)
                cost_est = weight_per_m * count * unit_price
                candidate = {
                    'mode': 'ratio',
                    'grade': g,
                    'diameter': dia,
                    'count': count,
                    'spacing': actual_spacing,
                    'target_spacing': max_dist_spacing,
                    'area_required': as_required,
                    'area_provided': as_provided,
                    'ratio_to_main': as_provided / as_main if as_main > 0 else 0.0,
                    'todo_auto_fix': False,
                }
                key = (overuse, cost_est, dia, -actual_spacing)
                if best is None or key < best[0]:
                    best = (key, candidate)

        if best:
            return best[1]

        # Fallback: use dense spacing to maximize provided distribution steel.
        # 选成本最低的级别
        fallback_grade = min(dist_grade_series, key=lambda g: self.rm.get_price(g, diameters[0]))
        dia = diameters[0]
        area = self.rm.get_bar_properties(dia)['area']
        b_eff = max(1.0, b - 2 * c - dia)
        # 初始化target_spacing默认值
        target_spacing = max_dist_spacing
        # Fallback 也须遵守最小间距：用 floor 求最大允许根数
        if min_dist_spacing > 0:
            count = max(2, int(math.floor(b_eff / min_dist_spacing)) + 1)
        else:
            target_spacing = max(80, min(100, max_dist_spacing))
            count = max(2, int(math.ceil(b_eff / target_spacing)) + 1)
        # 至少满足最大间距约束（不能太少）
        min_count_by_spacing_fb = max(2, int(math.ceil(b_eff / max_dist_spacing)) + 1)
        count = max(count, min_count_by_spacing_fb)
        actual_spacing = b_eff / (count - 1) if count > 1 else b_eff
        actual_spacing = math.floor(actual_spacing)  # 施工间距取整数
        as_provided = count * area

        return {
            'mode': 'ratio',
            'grade': fallback_grade,
            'diameter': dia,
            'count': count,
            'spacing': actual_spacing,
            'target_spacing': target_spacing,
            'area_required': as_required,
            'area_provided': as_provided,
            'ratio_to_main': as_provided / as_main if as_main > 0 else 0.0,
            'note': 'fallback_distribution_scheme',
            'todo_auto_fix': True,
        }

    def _evaluate_stirrup_candidate(self, cand: Dict, section_params: Dict, force_envelope: List[Dict], rebar_params: Dict) -> Dict:
        """并行验算单个拉筋候选方案"""
        trial_stirrup = {
            'diameter': cand['diameter'],
            'spacing': cand['spacing'],
            'grade': cand['grade'],
            'legs': cand['legs'],
            'layout': cand.get('layout', 'full'),
        }
        trial_rebar = dict(rebar_params)
        trial_rebar['stirrup'] = trial_stirrup

        all_pass = True
        max_ratio = 0.0
        max_limit_ratio = 0.0
        for forces in force_envelope:
            res = self.calc.verify_shear(section_params, forces, trial_rebar)
            max_ratio = max(max_ratio, res.get('ratio', 999.0))
            max_limit_ratio = max(max_limit_ratio, res.get('limit_ratio', 999.0))
            if not res.get('is_safe', False):
                all_pass = False

        stirrup_cost = self._calc_stirrup_cost(trial_stirrup, section_params)

        return {
            'stirrup': trial_stirrup,
            'score': {
                'provided_Asv_over_s': cand['Asv_over_s'],
                'max_ratio': max_ratio,
                'max_limit_ratio': max_limit_ratio,
            },
            'objs': (
                stirrup_cost,
                -trial_stirrup['spacing'],
                trial_stirrup['diameter'],
            ),
            'is_safe': all_pass,
        }

    def design_stirrups(self, main_scheme: Dict, section_params: Dict, force_envelope: List[Dict]) -> Dict:
        """
        后置配筋:
        1) 按抗剪公式计算所需最小 Asv/s
        2) 叠加最小配箍率约束，得到控制 Asv/s
        3) 在默认规格体系中配置拉筋
        4) 基于主筋面积配置分布筋
        """
        rebar_params = main_scheme['main_rebar'] if 'main_rebar' in main_scheme else dict(main_scheme)

        if not force_envelope:
            dist_rebar = self._design_distribution_rebar(rebar_params, section_params, None)
            result = {
                'main_rebar': rebar_params,
                'stirrup': None,
                'stirrup_pareto': [],
                'dist_rebar': dist_rebar,
                'shear_design': {
                    'status': 'no_force_envelope',
                    'required_Asv_over_s_strength': 0.0,
                    'required_Asv_over_s_min_ratio': 0.0,
                    'required_Asv_over_s': 0.0,
                    'provided_Asv_over_s': 0.0,
                    'max_ratio': 0.0,
                },
            }
            for key in ('summary', 'metrics', 'pareto_front', 'pareto_plot'):
                if key in main_scheme:
                    result[key] = main_scheme[key]
            return result

        stirrup_grade = section_params.get('stirrup_grade', 'HPB300')
        # 拉筋级别搜索范围
        stirrup_grades_cfg = section_params.get('stirrup_grades')
        if isinstance(stirrup_grades_cfg, list) and stirrup_grades_cfg:
            stirrup_grade_series = list(stirrup_grades_cfg)
        else:
            stirrup_grade_series = [stirrup_grade] if stirrup_grade != 'HPB300' else ['HPB300', 'HRB400']

        # 用最保守的 fyv（最小值）计算统一的 required_asv_over_s
        fyv_values = [self.rm.get_design_value(g) for g in stirrup_grade_series]
        fyv_values = [v for v in fyv_values if v > 1e-9]
        if not fyv_values:
            fyv_values = [self.rm.get_design_value('HPB300')]
        fyv = min(fyv_values)

        rho_sv_min_hpb300 = float(section_params.get('rho_sv_min_hpb300', 0.0014))
        rho_sv_min_hrb400 = float(section_params.get('rho_sv_min_hrb400', 0.0011))
        rho_sv_min_override = section_params.get('rho_sv_min_override')
        if rho_sv_min_override is not None:
            rho_sv_min = float(rho_sv_min_override)
        else:
            # 多级别搜索时取最大的最小配箍率（最保守）
            rho_sv_min = max(rho_sv_min_hpb300, rho_sv_min_hrb400)

        shear_cases = []
        max_section_limit_ratio = 0.0
        for idx, forces in enumerate(force_envelope):
            raw = self._calc_shear_without_stirrup(section_params, forces, rebar_params)
            h0 = raw['h0']
            deficit = max(0.0, raw['V_d'] - raw['Vc'])
            required_strength = deficit / (fyv * h0) if (fyv > 1e-9 and h0 > 1e-9) else float('inf')
            limit_ratio = raw['V_d'] / raw['V_max'] if raw.get('V_max', 0.0) > 0 else 999.0
            max_section_limit_ratio = max(max_section_limit_ratio, limit_ratio)

            shear_cases.append({
                'index': idx,
                'V_d': raw['V_d'],
                'Vc': raw['Vc'],
                'V_max': raw.get('V_max', 0.0),
                'h0': h0,
                'deficit': deficit,
                'required_strength': required_strength,
                'limit_ratio': limit_ratio,
                'shear_assumptions': raw.get('shear_assumptions', {}),
            })

        critical_strength_case = max(shear_cases, key=lambda x: x['required_strength'])
        critical_limit_case = max(shear_cases, key=lambda x: x['limit_ratio'])

        b = section_params['b']
        required_asv_over_s_strength = critical_strength_case['required_strength']
        required_asv_over_s_min_ratio = rho_sv_min * b
        required_asv_over_s = max(required_asv_over_s_strength, required_asv_over_s_min_ratio)

        candidates = self._build_stirrup_candidates(section_params, rebar_params, required_asv_over_s)

        # 并行验算候选方案
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(
                lambda cand: self._evaluate_stirrup_candidate(cand, section_params, force_envelope, rebar_params),
                candidates
            ))

        candidate_results = [r for r in results if r['is_safe']]
        best_effort = min(results, key=lambda r: r['score']['max_ratio']) if results else None

        stirrup_pareto_payload = []
        if candidate_results:
            pareto_front = self._pareto_front(candidate_results)
            for item in pareto_front:
                st = item['stirrup']
                sc = item['score']
                stirrup_pareto_payload.append({
                    'diameter': st['diameter'],
                    'spacing': st['spacing'],
                    'grade': st['grade'],
                    'legs': st['legs'],
                    'layout': st.get('layout', 'full'),
                    'provided_Asv_over_s': sc['provided_Asv_over_s'],
                    'max_ratio': sc['max_ratio'],
                    'max_limit_ratio': sc['max_limit_ratio'],
                    'cost': item['objs'][0],
                    'spacing_value': -item['objs'][1],
                    'diameter_value': item['objs'][2],
                })

            # 从 Pareto 前沿中选默认方案：先靠近最小 Asv/s，再优先较大间距
            chosen = min(
                pareto_front,
                key=lambda x: (
                    abs(x['score']['provided_Asv_over_s'] - required_asv_over_s),
                    x['stirrup']['diameter'],
                    -x['stirrup']['spacing'],
                )
            )
            final_stirrup = chosen['stirrup']
            provided_asv_over_s = chosen['score']['provided_Asv_over_s']
            max_ratio = chosen['score']['max_ratio']
            max_limit_ratio = chosen['score']['max_limit_ratio']
            shear_status = 'ok'
        else:
            final_stirrup = best_effort['stirrup'] if best_effort else {
                'diameter': max(self.constraints.MIN_DIA_STIRRUP, 8),
                'spacing': 100.0,
                'grade': stirrup_grade,
                'legs': max(2, int(section_params.get('stirrup_legs', 2))),
                'layout': str(section_params.get('stirrup_layout', 'full')),
            }
            area = math.pi * final_stirrup['diameter'] ** 2 / 4.0
            provided_asv_over_s = final_stirrup['legs'] * area / final_stirrup['spacing']
            max_ratio = best_effort['score']['max_ratio'] if best_effort else 999.0
            max_limit_ratio = best_effort['score']['max_limit_ratio'] if best_effort else 999.0
            shear_status = 'unsafe'

        if max_section_limit_ratio > 1.0 + 1e-9:
            # 截面上限不满足时，拉筋无法修复该问题，状态单独标记
            shear_status = 'section_limit_exceeded'

        dist_rebar = self._design_distribution_rebar(rebar_params, section_params, final_stirrup)

        result = {
            'main_rebar': rebar_params,
            'stirrup': final_stirrup,
            'stirrup_pareto': stirrup_pareto_payload,
            'dist_rebar': dist_rebar,
            'shear_design': {
                'status': shear_status,
                'critical_index_strength': critical_strength_case['index'],
                'critical_index_limit': critical_limit_case['index'],
                'critical_V_d': critical_strength_case['V_d'],
                'critical_Vc': critical_strength_case['Vc'],
                'critical_V_max': critical_limit_case['V_max'],
                'critical_h0': critical_strength_case['h0'],
                'rho_sv_min': rho_sv_min,
                'rho_sv_min_hpb300': rho_sv_min_hpb300,
                'rho_sv_min_hrb400': rho_sv_min_hrb400,
                'required_Asv_over_s_strength': required_asv_over_s_strength,
                'required_Asv_over_s_min_ratio': required_asv_over_s_min_ratio,
                'required_Asv_over_s': required_asv_over_s,
                'provided_Asv_over_s': provided_asv_over_s,
                'asv_over_s_uplift': float(section_params.get('stirrup_asv_over_s_uplift', 0.35)),
                'shear_assumptions': critical_strength_case.get('shear_assumptions', {}),
                'max_ratio': max_ratio,
                'max_limit_ratio': max_limit_ratio,
            },
        }

        for key in ('summary', 'metrics', 'pareto_front', 'pareto_plot'):
            if key in main_scheme:
                result[key] = main_scheme[key]

        return result


if __name__ == "__main__":
    solver = StructuralSolver()
    section = {'b': 1000, 'h': 500, 'cover': 40, 'concrete_grade': 'C50'}
    f1 = {'design': {'N': 2000, 'M': 400, 'V': 200}, 'quasi': {'N': 1800, 'M': 300}, 'gamma_d': 1.0}
    envelope = [f1]

    print("Testing Inverse Solve...")
    min_area = solver._inverse_solve_min_area(section, envelope)
    print(f"Min Area: {min_area:.2f} mm2")
