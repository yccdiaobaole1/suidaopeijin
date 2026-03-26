import random
import math
import copy
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor
from src.calculator import TunnelCalculator
from src.rebar_manager import RebarManager
from src.concrete_manager import ConcreteManager
from src.code_constraints import CodeConstraints
from src.structural_solver import StructuralSolver
from src.hv_indicator import compute_hypervolume, compute_hv_reference

class Individual:
    def __init__(self, gene: List[int]):
        # gene: [grade_idx, diameter_idx, spacing_idx]
        self.gene = gene
        self.objs = [float('inf'), float('inf'), float('inf')] # [Cost, Crack, -Spacing]
        self.raw_objs = [float('inf'), float('inf'), float('inf')]  # 原始物理值（不被归一化覆盖）
        self.rank = 0
        self.crowding_distance = 0.0
        self.is_valid = False
        self.info = {} # 存储具体的d, s, grade 等信息
class HybridNSGA2Solver:
    """
    鍩轰簬娣峰悎鍚彂寮?NSGA-II 的明洞衬砌配筋优化器
    对应论文算法流程
    """
    def __init__(self):
        self.rm = RebarManager()
        self.cm = ConcreteManager()
        self.calc = TunnelCalculator(self.rm, self.cm)
        self.constraints = CodeConstraints()
        self.helper_solver = StructuralSolver() # 用于Step 0逆向定界
        
        # 离散域定义
        self.GRADES = ['HRB400', 'HRB500']
        # 直径范围根据 CodeConstraints.MIN_DIA_MAIN ~ MAX_DIA_MAIN (8~25)
        self.DIAMETERS = [6, 8, 10, 12, 14, 16, 18, 20, 22, 25]
        # 间距范围根据 CodeConstraints.MAX_SPACING_DISTRIBUTION (<=250)
        self.SPACINGS = list(range(100, 251, 10)) # 100, 110 ... 250
        self._max_spacing_idx = len(self.SPACINGS) - 1

    def solve(self, section_params: Dict, force_envelope: List[Dict],
              pop_size: int = 200, max_gen: int = 200,
              plot_path: str = "pareto_front.png", preference: str = "balanced",
              seed: Optional[int] = None,
              exhaustive_front: Optional[List['Individual']] = None,
              preference_selections: Optional[Dict] = None) -> Dict:
        """
        主优化流程
        """
        if seed is not None:
            random.seed(seed)
        print(f"Start Hybrid NSGA-II Optimization...")
        
        # Step 0: Heuristic feasible-region bounding.
        # StructuralSolver._inverse_solve_min_area is used as a baseline estimator.
        print("Step 0: Calculating heuristic bounds...")
        a_base = self.helper_solver._inverse_solve_min_area(section_params, force_envelope)
        
        # 定义有效搜索区间 (兼容 HRB500, 涓嬮檺鏀惧鑷?0.8)
        valid_min_area = 0.8 * a_base
        valid_max_area = 1.5 * a_base
        print(f"  > Base Area: {a_base:.0f} mm2")
        print(f"  > Valid Range: [{valid_min_area:.0f}, {valid_max_area:.0f}] mm2")
        max_s = self.constraints.get_max_spacing_main(section_params.get('h', 500))
        valid_spacing_indices = [i for i, sv in enumerate(self.SPACINGS) if sv <= max_s]
        self._max_spacing_idx = valid_spacing_indices[-1] if valid_spacing_indices else 0
        
        # Step 1: 鍚彂寮忓垵濮嬪寲
        population = self._initialize_population(pop_size, valid_min_area, valid_max_area, section_params)
        self._evaluate_population(population, section_params, force_envelope)

        # 检测裂缝维度退化：全部有效解 crack ≈ 0 时切换为 SF 目标
        valid_init = [ind for ind in population if ind.is_valid]
        use_sf_objective = False
        if valid_init:
            all_zero_crack = all(ind.raw_objs[1] < 1e-9 for ind in valid_init)
            if all_zero_crack:
                use_sf_objective = True
                print("  > [Adaptive] All crack widths ≈ 0, switching obj[1] to -Safety Factor")

        if use_sf_objective:
            self._apply_sf_objective(population)

        self._normalize_objectives(population)
        fronts = self._fast_non_dominated_sort(population)
        self._update_crowding_for_fronts(fronts)

        gen_history = []  # 逐代收敛记录

        # 计算 Hypervolume 参考点（首代最差有效解各维 x1.1）
        if valid_init:
            if use_sf_objective:
                init_objs = [[ind.raw_objs[0], -ind.info.get('min_sf', 0), -ind.raw_objs[2]] for ind in valid_init]
            else:
                init_objs = [[ind.raw_objs[0], ind.raw_objs[1], -ind.raw_objs[2]] for ind in valid_init]
            hv_ref = compute_hv_reference(init_objs, margin=1.1)
        else:
            hv_ref = None

        # Step 2: 进化迭代
        for gen in range(max_gen):
            if gen % 10 == 0:
                print(f"  > Generation {gen}/{max_gen}, Front[0] size: {len(fronts[0])}")

            # 生成子代
            offspring = self._make_offspring(population, pop_size)
            self._evaluate_population(offspring, section_params, force_envelope)
            if use_sf_objective:
                self._apply_sf_objective(offspring)

            # 合并前重置population的objs为原始值（避免归一化值污染）
            for ind in population:
                ind.objs = [ind.raw_objs[0], ind.raw_objs[1], -ind.raw_objs[2]]

            # 合并
            combined_pop = population + offspring
            self._normalize_objectives(combined_pop)
            fronts = self._fast_non_dominated_sort(combined_pop)
            
            # 精英保留策略选择下一代
            new_pop = []
            for front in fronts:
                self._calculate_crowding_distance(front)
                if len(new_pop) + len(front) <= pop_size:
                    new_pop.extend(front)
                else:
                    # 截断，按拥挤度排序(降序)
                    front.sort(key=lambda x: x.crowding_distance, reverse=True)
                    needed = pop_size - len(new_pop)
                    new_pop.extend(front[:needed])
                    break
            
            population = new_pop
            fronts = self._fast_non_dominated_sort(population)
            self._update_crowding_for_fronts(fronts)

            # 记录当代 Pareto 前沿指标
            gen_history.append(self._snapshot_front(fronts[0] if fronts else [], hv_ref=hv_ref, use_sf_objective=use_sf_objective))

            # 收敛判断：连续5代HV变化率 < 0.1%（多目标整体收敛）
            if gen >= 5:
                recent = gen_history[-5:]
                hvs = [h['hv'] for h in recent if h['hv'] > 0]
                if len(hvs) == 5:
                    max_change = max(abs(hvs[i] - hvs[i-1]) / hvs[i-1] for i in range(1, 5) if hvs[i-1] > 0)
                    if max_change < 0.001:
                        print(f"  > Converged at generation {gen} (HV change rate: {max_change:.4f})")
                        break

        # Step 3: 最终决策（用户偏好选择）
        # 取 Pareto 前沿
        final_front = fronts[0] if fronts else []
        best_sol = self.select_solution_by_preference(final_front, preference)
        pareto_payload = self._build_pareto_payload(final_front, use_sf_objective=use_sf_objective)
        plot_files = self._export_pareto_plot(
            final_front, plot_path,
            exhaustive_front=exhaustive_front,
            preference_selections=preference_selections,
            use_sf_objective=use_sf_objective
        ) if plot_path else None
        conv_result = self._export_convergence_plot(gen_history, plot_path, use_sf_objective=use_sf_objective) if plot_path else None
        if conv_result:
            conv_file, obj_conv_file = conv_result
        else:
            conv_file, obj_conv_file = None, None

        if best_sol is None:
            return None
        best_sol["pareto_front"] = pareto_payload
        best_sol["gen_history"] = gen_history
        best_sol["hv_ref"] = hv_ref
        best_sol["final_front"] = final_front
        best_sol["use_sf_objective"] = use_sf_objective
        best_sol["objective_labels"] = [
            "Cost",
            "Safety Factor" if use_sf_objective else "Crack Width",
            "Spacing"
        ]
        all_plots = list(plot_files) if plot_files else []
        if conv_file:
            all_plots.append(conv_file)
        if obj_conv_file:
            all_plots.append(obj_conv_file)
        if all_plots:
            best_sol["pareto_plot"] = all_plots

        return best_sol

    @staticmethod
    def _apply_sf_objective(pop: List[Individual]):
        """将有效个体的 objs[1] 从 crack 切换为 -min_sf（最小化方向）"""
        for ind in pop:
            if ind.is_valid:
                min_sf = ind.info.get('min_sf', 0.0)
                ind.objs = [ind.objs[0], -min_sf, ind.objs[2]]

    def _initialize_population(self, size: int, min_a: float, max_a: float, section_params: Dict) -> List[Individual]:
        """
        启发式初始化：仅生成位于有效面积区间内的个体
        """
        pop = []
        attempts = 0
        max_s = self.constraints.get_max_spacing_main(section_params.get('h', 500))
        valid_spacing_indices = [i for i, sv in enumerate(self.SPACINGS) if sv <= max_s]
        if not valid_spacing_indices:
            valid_spacing_indices = [0]
        self._max_spacing_idx = valid_spacing_indices[-1] if valid_spacing_indices else 0
        while len(pop) < size and attempts < size * 100:
            attempts += 1
            # 随机生成基因
            g_idx = random.randint(0, len(self.GRADES)-1)
            d_idx = random.randint(0, len(self.DIAMETERS)-1)
            s_idx = random.choice(valid_spacing_indices)
            d = self.DIAMETERS[d_idx]
            s = self.SPACINGS[s_idx]
            b = section_params['b']
            c = section_params.get('cover', self.constraints.DEFAULT_COVER)
            b_eff = b - 2 * c - d
            if b_eff <= 0:
                continue
            s_limit = min(s, max_s)
            count = max(2, int(math.ceil(b_eff / s_limit)) + 1)
            actual_spacing = b_eff / (count - 1) if count > 1 else b_eff
            area = count * (math.pi * d**2 / 4)
            # 面积筛选
            if min_a <= area <= max_a:
                # 构造约束预筛
                clear_spacing = actual_spacing - d
                if clear_spacing >= self.constraints.MIN_CLEAR_SPACING_ABS and clear_spacing >= d:
                    pop.append(Individual([g_idx, d_idx, s_idx]))
        # 如果启发式生成不足，随机填充剩余
        while len(pop) < size:
            g_idx = random.randint(0, len(self.GRADES)-1)
            d_idx = random.randint(0, len(self.DIAMETERS)-1)
            s_idx = random.choice(valid_spacing_indices)
            pop.append(Individual([g_idx, d_idx, s_idx]))
        return pop
    def _make_offspring(self, parent_pop: List[Individual], size: int) -> List[Individual]:
        offspring = []
        while len(offspring) < size:
            # 锦标赛选择
            p1 = self._tournament_select(parent_pop)
            p2 = self._tournament_select(parent_pop)
            # 交叉
            c1_gene, c2_gene = self._discrete_crossover(p1.gene, p2.gene)
            # 变异
            self._discrete_mutation(c1_gene)
            self._discrete_mutation(c2_gene)
            offspring.append(Individual(c1_gene))
            offspring.append(Individual(c2_gene))
        return offspring[:size]
    def _tournament_select(self, pop: List[Individual]) -> Individual:
        a, b = random.sample(pop, 2)
        # 优先Rank小(好，其次 CrowdingDistance 大(稀疏
        if a.rank < b.rank:
            return a
        elif a.rank > b.rank:
            return b
        else:
            return a if a.crowding_distance > b.crowding_distance else b
    def _discrete_crossover(self, g1: List[int], g2: List[int]) -> Tuple[List[int], List[int]]:
        """
        绂绘暎交叉绠楀瓙
        - 牌号(0) 鍜?直径(1): 鍧囧寑交叉 (Uniform)
        - 间距(2): 模拟二进制交叉(SBX) 鐨勭鏁ｇ増 (均值邻域
        """
        c1 = g1[:]
        c2 = g2[:]
        # 1. 鍧囧寑交叉 (Grade, Diameter)
        for i in [0, 1]:
            if random.random() < 0.5:
                c1[i], c2[i] = c2[i], c1[i]
        # 2. 间距 (Ordinal) - 模拟 SBX：在两点的均值邻域展开
        if random.random() < 0.8:
            i1, i2 = g1[2], g2[2]
            if i1 != i2:
                mid = (i1 + i2) / 2.0
                spread = abs(i1 - i2)
                offset = random.uniform(-0.5, 0.5) * spread
                c1_idx = int(round(mid + offset))
                max_idx = self._max_spacing_idx if hasattr(self, "_max_spacing_idx") else (len(self.SPACINGS) - 1)
                c2_idx = int(round(mid - offset))
                c1[2] = max(0, min(max_idx, c1_idx))
                c2[2] = max(0, min(max_idx, c2_idx))
        return c1, c2
    def _discrete_mutation(self, gene: List[int]):
        """
        离散变异：对索引进行 +/- 1 的微扰        """
        # 牌号变异
        if random.random() < 0.1:
            gene[0] = random.randint(0, len(self.GRADES)-1)
        # 直径变异 (局部微扰
        if random.random() < 0.1:
            delta = random.choice([-1, 1])
            new_idx = gene[1] + delta
            gene[1] = max(0, min(len(self.DIAMETERS)-1, new_idx))
        # 间距变异 (局部微扰
        if random.random() < 0.1:
            delta = random.choice([-1, 1, -2, 2])
            new_idx = gene[2] + delta
            max_idx = self._max_spacing_idx if hasattr(self, "_max_spacing_idx") else (len(self.SPACINGS) - 1)
            gene[2] = max(0, min(max_idx, new_idx))

    def _evaluate_single(self, ind: Individual, section_params: Dict, force_envelope: List[Dict], max_s: float):
        """评估单个个体"""
        grade = self.GRADES[ind.gene[0]]
        d = self.DIAMETERS[ind.gene[1]]
        s = self.SPACINGS[ind.gene[2]]
        b = section_params['b']
        c = section_params.get('cover', self.constraints.DEFAULT_COVER)

        # 保护层厚度校核
        if c < d:
            ind.is_valid = False
            ind.objs = [float('inf'), float('inf'), float('inf')]
            ind.raw_objs = [float('inf'), float('inf'), float('inf')]
            return

        b_eff = b - 2 * c - d
        if b_eff <= 0:
            ind.is_valid = False
            ind.objs = [float('inf'), float('inf'), float('inf')]
            ind.raw_objs = [float('inf'), float('inf'), float('inf')]
            return

        s_limit = min(s, max_s)
        count = max(2, int(math.ceil(b_eff / s_limit)) + 1)
        actual_spacing = b_eff / (count - 1) if count > 1 else b_eff
        actual_spacing = math.floor(actual_spacing)  # 施工间距取整数（向下取整，偏安全）
        n_calc = count
        rebar_params = {
            'grade': grade,
            'diameter': d,
            'spacing': actual_spacing,
            'count': n_calc
        }
        ind.info = rebar_params

        # 净距检查
        clear_spacing = actual_spacing - d
        min_clear = self.constraints.get_min_clear_spacing(d)
        if clear_spacing < min_clear or actual_spacing > max_s:
            ind.is_valid = False
            ind.objs = [float('inf'), float('inf'), float('inf')]
            ind.raw_objs = [float('inf'), float('inf'), float('inf')]
            return

        # 全性能验算
        is_safe = True
        max_w = 0.0
        min_sf = float('inf')
        for forces in force_envelope:
            res = self.calc.verify_structure(section_params, forces, rebar_params)
            if not res['is_safe']:
                is_safe = False
                break
            max_w = max(max_w, res['crack_width'])
            sf = res.get('safety_factor', float('inf'))
            if sf < min_sf:
                min_sf = sf

        if not is_safe:
            ind.is_valid = False
            ind.objs = [float('inf'), float('inf'), float('inf')]
            ind.raw_objs = [float('inf'), float('inf'), float('inf')]
        else:
            ind.is_valid = True
            props = self.rm.get_bar_properties(d)
            weight_per_m = props['weight']
            total_weight_per_m = weight_per_m * n_calc
            price_unit = self.rm.get_price(grade, d)
            cost = (total_weight_per_m / 1000.0) * price_unit
            ind.objs = [cost, max_w, -actual_spacing]
            ind.raw_objs = [cost, max_w, actual_spacing]  # 保存原始物理值（间距为正值）
            ind.info['min_sf'] = min_sf

    def _evaluate_population(self, pop: List[Individual], section_params: Dict, force_envelope: List[Dict]):
        max_s = self.constraints.get_max_spacing_main(section_params.get("h", 500))
        with ThreadPoolExecutor(max_workers=4) as executor:
            list(executor.map(lambda ind: self._evaluate_single(ind, section_params, force_envelope, max_s), pop))

    def _normalize_objectives(self, pop: List[Individual]):
        """归一化目标函数到[0,1]"""
        valid_pop = [ind for ind in pop if ind.is_valid]
        if not valid_pop:
            return

        n_obj = 3
        mins = [float('inf')] * n_obj
        maxs = [float('-inf')] * n_obj

        for ind in valid_pop:
            for i in range(n_obj):
                mins[i] = min(mins[i], ind.objs[i])
                maxs[i] = max(maxs[i], ind.objs[i])

        for ind in valid_pop:
            normalized = []
            for i in range(n_obj):
                if maxs[i] - mins[i] > 1e-9:
                    normalized.append((ind.objs[i] - mins[i]) / (maxs[i] - mins[i]))
                else:
                    normalized.append(0.0)
            ind.objs = normalized

    def _fast_non_dominated_sort(self, pop: List[Individual]) -> List[List[Individual]]:
        fronts = [[]]
        for p in pop:
            p.S = []
            p.n = 0
            for q in pop:
                if self._dominates(p, q):
                    p.S.append(q)
                elif self._dominates(q, p):
                    p.n += 1
            if p.n == 0:
                p.rank = 0
                fronts[0].append(p)
        i = 0
        while i < len(fronts) and fronts[i]:
            Q = []
            for p in fronts[i]:
                for q in p.S:
                    q.n -= 1
                    if q.n == 0:
                        q.rank = i + 1
                        Q.append(q)
            i += 1
            if Q:
                fronts.append(Q)
        return [f for f in fronts if f]
    def _dominates(self, p: Individual, q: Individual) -> bool:
        # p dominates q if p is better or equal in all objs, and strictly better in at least one
        better_in_one = False
        for o1, o2 in zip(p.objs, q.objs):
            if o1 > o2: # We minimize all objectives
                return False
            if o1 < o2:
                better_in_one = True
        return better_in_one
    def _calculate_crowding_distance(self, front: List[Individual]):
        l = len(front)
        if l == 0: return
        for p in front:
            p.crowding_distance = 0
        for m in range(3): # 3 objectives
            front.sort(key=lambda x: x.objs[m])
            front[0].crowding_distance = float('inf')
            front[l-1].crowding_distance = float('inf')
            obj_range = front[l-1].objs[m] - front[0].objs[m]
            if obj_range == 0: continue
            for i in range(1, l-1):
                front[i].crowding_distance += (front[i+1].objs[m] - front[i-1].objs[m]) / obj_range
    def _update_crowding_for_fronts(self, fronts: List[List[Individual]]):
        for front in fronts:
            self._calculate_crowding_distance(front)
    def _build_pareto_payload(self, front: List[Individual], use_sf_objective: bool = False) -> List[Dict]:
        payload = []
        for ind in front:
            if not ind.is_valid:
                continue
            info = ind.info or {}
            entry = {
                "grade": info.get("grade"),
                "diameter": info.get("diameter"),
                "spacing": info.get("spacing"),
                "count": int(info.get("count", 0)),
                "metrics": {
                    "cost": ind.raw_objs[0],
                    "max_crack": ind.raw_objs[1],
                    "spacing": ind.raw_objs[2],
                    "min_sf": info.get("min_sf"),
                },
                "objective_mode": "sf" if use_sf_objective else "crack",
            }
            payload.append(entry)
        return payload

    @staticmethod
    def _snapshot_front(front: List['Individual'], hv_ref: Optional[List[float]] = None,
                        use_sf_objective: bool = False) -> Dict:
        """记录单代 Pareto 前沿的统计指标"""
        valid = [ind for ind in front if ind.is_valid]
        if not valid:
            snap = {"size": 0, "min_cost": float('inf'), "mean_cost": float('inf'),
                    "min_crack": float('inf'), "mean_crack": float('inf'),
                    "max_spacing": 0, "mean_spacing": 0, "hv": 0.0}
            if use_sf_objective:
                snap.update({"min_sf": 0, "mean_sf": 0, "max_sf": 0})
            return snap
        costs = [ind.raw_objs[0] for ind in valid]
        cracks = [ind.raw_objs[1] for ind in valid]
        spacings = [ind.raw_objs[2] for ind in valid]
        n = len(valid)

        hv = 0.0
        if hv_ref is not None:
            if use_sf_objective:
                front_objs = [[ind.raw_objs[0], -ind.info.get('min_sf', 0), -ind.raw_objs[2]] for ind in valid]
            else:
                front_objs = [[ind.raw_objs[0], ind.raw_objs[1], -ind.raw_objs[2]] for ind in valid]
            hv = compute_hypervolume(front_objs, hv_ref)

        snap = {
            "size": n,
            "min_cost": min(costs), "mean_cost": sum(costs) / n,
            "min_crack": min(cracks), "mean_crack": sum(cracks) / n,
            "max_spacing": max(spacings), "mean_spacing": sum(spacings) / n,
            "hv": hv,
        }
        if use_sf_objective:
            sfs = [ind.info.get('min_sf', 0) for ind in valid]
            snap.update({
                "min_sf": min(sfs), "mean_sf": sum(sfs) / n, "max_sf": max(sfs),
            })
        return snap

    @staticmethod
    def _export_convergence_plot(gen_history: List[Dict], plot_path: str,
                                 multi_run_histories: Optional[List[List[Dict]]] = None,
                                 use_sf_objective: bool = False) -> str:
        """绘制算法收敛曲线 (3×2 = 6 子图)，SCI 期刊规格"""
        if not gen_history:
            return None
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            import matplotlib.font_manager as fm
        except Exception:
            print("  > matplotlib not available, skip convergence plot.")
            return None

        # 论文字体：Times New Roman
        plt.rcParams.update({
            'font.family': 'serif',
            'font.serif': ['Times New Roman'],
            'axes.unicode_minus': False,
            'font.size': 9,
            'axes.labelsize': 9,
            'axes.titlesize': 10,
            'legend.fontsize': 8,
            'xtick.labelsize': 8,
            'ytick.labelsize': 8,
        })

        has_multi = multi_run_histories and len(multi_run_histories) > 1
        n_runs_label = len(multi_run_histories) if has_multi else 1

        gens = list(range(1, len(gen_history) + 1))
        sizes = [g["size"] for g in gen_history]
        min_costs = [g["min_cost"] for g in gen_history]
        mean_costs = [g["mean_cost"] for g in gen_history]
        if use_sf_objective:
            min_cracks = [g.get("max_sf", 0) for g in gen_history]  # SF: max is best
            mean_cracks = [g.get("mean_sf", 0) for g in gen_history]
        else:
            min_cracks = [g["min_crack"] for g in gen_history]
            mean_cracks = [g["mean_crack"] for g in gen_history]
        max_spacings = [g["max_spacing"] for g in gen_history]
        mean_spacings = [g["mean_spacing"] for g in gen_history]
        hvs = [g.get("hv", 0.0) for g in gen_history]

        fig, axes = plt.subplots(3, 2, figsize=(7.0, 9.0))
        fig.suptitle("NSGA-II Convergence", fontsize=11, fontweight="bold")

        # Helper: 计算多次运行的 mean±std
        def _multi_run_stats(key, histories):
            if not histories:
                return None, None, None
            max_len = max(len(h) for h in histories)
            means, stds = [], []
            for gi in range(max_len):
                vals = [h[gi].get(key, 0.0) for h in histories if gi < len(h)]
                if not vals:
                    means.append(0.0)
                    stds.append(0.0)
                    continue
                m = sum(vals) / len(vals)
                s = math.sqrt(sum((v - m) ** 2 for v in vals) / max(len(vals) - 1, 1)) if len(vals) > 1 else 0.0
                means.append(m)
                stds.append(s)
            x = list(range(1, max_len + 1))
            return x, means, stds

        def _plot_with_band(ax, x, mean, std, color, label):
            mean_arr = mean
            lo = [m - s for m, s in zip(mean, std)]
            hi = [m + s for m, s in zip(mean, std)]
            ax.plot(x, mean_arr, '-', color=color, linewidth=1.2, label=label)
            ax.fill_between(x, lo, hi, color=color, alpha=0.15)

        # (a) Pareto Front Size
        ax = axes[0][0]
        if has_multi:
            x, m, s = _multi_run_stats('size', multi_run_histories)
            _plot_with_band(ax, x, m, s, "#2563eb", f"Mean ± 1σ (N={n_runs_label})")
        else:
            ax.plot(gens, sizes, "o-", color="#2563eb", markersize=2, linewidth=1.0)
        ax.set_xlabel("Generation")
        ax.set_ylabel("Front Size")
        ax.set_title("(a) Pareto Front Size")
        ax.grid(True, alpha=0.3)
        if has_multi:
            ax.legend(fontsize=7)

        # (b) Cost Convergence
        ax = axes[0][1]
        if has_multi:
            x, m, s = _multi_run_stats('min_cost', multi_run_histories)
            _plot_with_band(ax, x, m, s, "#dc2626", "Min (Mean ± 1σ)")
            x2, m2, s2 = _multi_run_stats('mean_cost', multi_run_histories)
            _plot_with_band(ax, x2, m2, s2, "#f97316", "Mean (Mean ± 1σ)")
        else:
            ax.plot(gens, min_costs, "s-", color="#dc2626", markersize=2, linewidth=1.0, label="Min")
            ax.plot(gens, mean_costs, "^--", color="#f97316", markersize=2, linewidth=0.8, label="Mean")
        ax.set_xlabel("Generation")
        ax.set_ylabel("Cost (CNY/m)")
        ax.set_title("(b) Cost Convergence")
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)

        # (c) Crack Width / Safety Factor Convergence
        ax = axes[1][0]
        if use_sf_objective:
            sf_key_min, sf_key_mean = 'max_sf', 'mean_sf'
            c_ylabel = "Safety Factor"
            c_title = "(c) Safety Factor Convergence"
            c_label_min, c_label_mean = "Max (Mean ± 1σ)", "Mean (Mean ± 1σ)"
            c_label_min_s, c_label_mean_s = "Max", "Mean"
        else:
            sf_key_min, sf_key_mean = 'min_crack', 'mean_crack'
            c_ylabel = "Crack Width (mm)"
            c_title = "(c) Crack Width Convergence"
            c_label_min, c_label_mean = "Min (Mean ± 1σ)", "Mean (Mean ± 1σ)"
            c_label_min_s, c_label_mean_s = "Min", "Mean"
        if has_multi:
            x, m, s = _multi_run_stats(sf_key_min, multi_run_histories)
            _plot_with_band(ax, x, m, s, "#7c3aed", c_label_min)
            x2, m2, s2 = _multi_run_stats(sf_key_mean, multi_run_histories)
            _plot_with_band(ax, x2, m2, s2, "#a78bfa", c_label_mean)
        else:
            ax.plot(gens, min_cracks, "s-", color="#7c3aed", markersize=2, linewidth=1.0, label=c_label_min_s)
            ax.plot(gens, mean_cracks, "^--", color="#a78bfa", markersize=2, linewidth=0.8, label=c_label_mean_s)
        ax.set_xlabel("Generation")
        ax.set_ylabel(c_ylabel)
        ax.set_title(c_title)
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)

        # (d) Spacing Convergence
        ax = axes[1][1]
        if has_multi:
            x, m, s = _multi_run_stats('max_spacing', multi_run_histories)
            _plot_with_band(ax, x, m, s, "#059669", "Max (Mean ± 1σ)")
            x2, m2, s2 = _multi_run_stats('mean_spacing', multi_run_histories)
            _plot_with_band(ax, x2, m2, s2, "#34d399", "Mean (Mean ± 1σ)")
        else:
            ax.plot(gens, max_spacings, "s-", color="#059669", markersize=2, linewidth=1.0, label="Max")
            ax.plot(gens, mean_spacings, "^--", color="#34d399", markersize=2, linewidth=0.8, label="Mean")
        ax.set_xlabel("Generation")
        ax.set_ylabel("Spacing (mm)")
        ax.set_title("(d) Spacing Convergence")
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)

        # (e) Hypervolume Indicator
        ax = axes[2][0]
        if has_multi:
            x, m, s = _multi_run_stats('hv', multi_run_histories)
            _plot_with_band(ax, x, m, s, "#0891b2", f"Mean ± 1σ (N={n_runs_label})")
        else:
            ax.plot(gens, hvs, "o-", color="#0891b2", markersize=2, linewidth=1.0)
        ax.set_xlabel("Generation")
        ax.set_ylabel("Hypervolume")
        ax.set_title("(e) Hypervolume Indicator")
        ax.grid(True, alpha=0.3)
        if has_multi:
            ax.legend(fontsize=7)

        # (f) Multi-run HV distribution or convergence rate
        ax = axes[2][1]
        if has_multi:
            # 每次运行的最终 HV 箱线图
            final_hvs = []
            for h in multi_run_histories:
                if h:
                    final_hvs.append(h[-1].get('hv', 0.0))
            if final_hvs:
                bp = ax.boxplot(final_hvs, vert=True, patch_artist=True,
                                boxprops=dict(facecolor='#dbeafe', edgecolor='#2563eb'),
                                medianprops=dict(color='#dc2626', linewidth=1.5))
                ax.set_ylabel("Final Hypervolume")
                ax.set_title(f"(f) HV Distribution (N={n_runs_label})")
                ax.set_xticklabels([f"N={n_runs_label}"])
            else:
                ax.set_visible(False)
        else:
            # 单次运行：HV 变化率
            if len(hvs) > 1:
                hv_rate = [0.0]
                for i in range(1, len(hvs)):
                    if hvs[i - 1] > 1e-12:
                        hv_rate.append((hvs[i] - hvs[i - 1]) / hvs[i - 1] * 100)
                    else:
                        hv_rate.append(0.0)
                ax.plot(gens, hv_rate, "o-", color="#e11d48", markersize=2, linewidth=1.0)
                ax.axhline(y=0.1, color='gray', linestyle='--', linewidth=0.8, label='0.1% threshold')
                ax.set_xlabel("Generation")
                ax.set_ylabel("HV Change Rate (%)")
                ax.set_title("(f) HV Convergence Rate")
                ax.legend(fontsize=7)
                ax.grid(True, alpha=0.3)
            else:
                ax.set_visible(False)

        fig.tight_layout(rect=[0, 0, 1, 0.96])

        base_path = Path(plot_path)
        out_path = base_path.parent / f"{base_path.stem}_convergence.png"
        base_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(str(out_path), dpi=300, bbox_inches='tight')
        plt.close(fig)
        plt.rcParams.update(plt.rcParamsDefault)  # 恢复默认

        # 额外导出：目标收敛子图（Cost / Crack or SF / Spacing）
        obj_conv_file = HybridNSGA2Solver._export_objective_convergence_plot(
            gen_history, plot_path,
            multi_run_histories=multi_run_histories,
            use_sf_objective=use_sf_objective,
        )

        return str(out_path), obj_conv_file

    @staticmethod
    def _export_objective_convergence_plot(gen_history: List[Dict], plot_path: str,
                                           multi_run_histories: Optional[List[List[Dict]]] = None,
                                           use_sf_objective: bool = False) -> Optional[str]:
        """导出目标收敛子图（Cost / Crack or SF / Spacing），1×3 布局"""
        if not gen_history:
            return None
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        except Exception:
            return None

        # 论文字体：Times New Roman
        plt.rcParams.update({
            'font.family': 'serif',
            'font.serif': ['Times New Roman'],
            'axes.unicode_minus': False,
            'font.size': 9,
            'axes.labelsize': 9,
            'axes.titlesize': 10,
            'legend.fontsize': 8,
            'xtick.labelsize': 8,
            'ytick.labelsize': 8,
        })

        has_multi = multi_run_histories and len(multi_run_histories) > 1
        n_runs_label = len(multi_run_histories) if has_multi else 1

        gens = list(range(1, len(gen_history) + 1))
        min_costs = [g["min_cost"] for g in gen_history]
        mean_costs = [g["mean_cost"] for g in gen_history]
        max_spacings = [g["max_spacing"] for g in gen_history]
        mean_spacings = [g["mean_spacing"] for g in gen_history]

        if use_sf_objective:
            min_cracks = [g.get("max_sf", 0) for g in gen_history]
            mean_cracks = [g.get("mean_sf", 0) for g in gen_history]
        else:
            min_cracks = [g["min_crack"] for g in gen_history]
            mean_cracks = [g["mean_crack"] for g in gen_history]

        def _multi_run_stats(key, histories):
            if not histories:
                return None, None, None
            max_len = max(len(h) for h in histories)
            means, stds = [], []
            for gi in range(max_len):
                vals = [h[gi].get(key, 0.0) for h in histories if gi < len(h)]
                if not vals:
                    means.append(0.0)
                    stds.append(0.0)
                    continue
                m = sum(vals) / len(vals)
                s = math.sqrt(sum((v - m) ** 2 for v in vals) / max(len(vals) - 1, 1)) if len(vals) > 1 else 0.0
                means.append(m)
                stds.append(s)
            x = list(range(1, max_len + 1))
            return x, means, stds

        def _plot_with_band(ax, x, mean, std, color, label):
            lo = [m - s for m, s in zip(mean, std)]
            hi = [m + s for m, s in zip(mean, std)]
            ax.plot(x, mean, '-', color=color, linewidth=1.2, label=label)
            ax.fill_between(x, lo, hi, color=color, alpha=0.15)

        fig, axes = plt.subplots(1, 3, figsize=(10.0, 3.5))

        # (a) Cost Convergence
        ax = axes[0]
        if has_multi:
            x, m, s = _multi_run_stats('min_cost', multi_run_histories)
            _plot_with_band(ax, x, m, s, "#dc2626", "Min (Mean ± 1σ)")
            x2, m2, s2 = _multi_run_stats('mean_cost', multi_run_histories)
            _plot_with_band(ax, x2, m2, s2, "#f97316", "Mean (Mean ± 1σ)")
        else:
            ax.plot(gens, min_costs, "s-", color="#dc2626", markersize=2, linewidth=1.0, label="Min")
            ax.plot(gens, mean_costs, "^--", color="#f97316", markersize=2, linewidth=0.8, label="Mean")
        ax.set_xlabel("Generation")
        ax.set_ylabel("Cost (CNY/m)")
        ax.set_title("(a) Cost Convergence")
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)

        # (b) Crack Width / Safety Factor Convergence
        ax = axes[1]
        if use_sf_objective:
            sf_key_min, sf_key_mean = 'max_sf', 'mean_sf'
            c_ylabel = "Safety Factor"
            c_title = "(b) Safety Factor Convergence"
            c_label_min, c_label_mean = "Max (Mean ± 1σ)", "Mean (Mean ± 1σ)"
            c_label_min_s, c_label_mean_s = "Max", "Mean"
        else:
            sf_key_min, sf_key_mean = 'min_crack', 'mean_crack'
            c_ylabel = "Crack Width (mm)"
            c_title = "(b) Crack Width Convergence"
            c_label_min, c_label_mean = "Min (Mean ± 1σ)", "Mean (Mean ± 1σ)"
            c_label_min_s, c_label_mean_s = "Min", "Mean"
        if has_multi:
            x, m, s = _multi_run_stats(sf_key_min, multi_run_histories)
            _plot_with_band(ax, x, m, s, "#7c3aed", c_label_min)
            x2, m2, s2 = _multi_run_stats(sf_key_mean, multi_run_histories)
            _plot_with_band(ax, x2, m2, s2, "#a78bfa", c_label_mean)
        else:
            ax.plot(gens, min_cracks, "s-", color="#7c3aed", markersize=2, linewidth=1.0, label=c_label_min_s)
            ax.plot(gens, mean_cracks, "^--", color="#a78bfa", markersize=2, linewidth=0.8, label=c_label_mean_s)
        ax.set_xlabel("Generation")
        ax.set_ylabel(c_ylabel)
        ax.set_title(c_title)
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)

        # (c) Spacing Convergence
        ax = axes[2]
        if has_multi:
            x, m, s = _multi_run_stats('max_spacing', multi_run_histories)
            _plot_with_band(ax, x, m, s, "#059669", "Max (Mean ± 1σ)")
            x2, m2, s2 = _multi_run_stats('mean_spacing', multi_run_histories)
            _plot_with_band(ax, x2, m2, s2, "#34d399", "Mean (Mean ± 1σ)")
        else:
            ax.plot(gens, max_spacings, "s-", color="#059669", markersize=2, linewidth=1.0, label="Max")
            ax.plot(gens, mean_spacings, "^--", color="#34d399", markersize=2, linewidth=0.8, label="Mean")
        ax.set_xlabel("Generation")
        ax.set_ylabel("Spacing (mm)")
        ax.set_title("(c) Spacing Convergence")
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)

        fig.tight_layout()

        base_path = Path(plot_path)
        obj_out = base_path.parent / f"{base_path.stem}_obj_convergence.png"
        base_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(str(obj_out), dpi=300, bbox_inches='tight')
        plt.close(fig)
        plt.rcParams.update(plt.rcParamsDefault)
        print(f"  > Objective convergence plot saved: {obj_out}")
        return str(obj_out)

    def _export_pareto_plot(self, front: List[Individual], plot_path: str,
                            exhaustive_front: Optional[List['Individual']] = None,
                            preference_selections: Optional[Dict] = None,
                            use_sf_objective: bool = False) -> List[str]:
        """绘制 2×2 帕累托前沿图（SCI 期刊规格）

        Parameters
        ----------
        front : NSGA-II Pareto 前沿
        plot_path : 输出路径基础
        exhaustive_front : 穷举 Pareto 前沿（灰色底层）
        preference_selections : Dict[str, Individual] — 4种偏好各自选中的解
        """
        valid = [ind for ind in front if ind.is_valid]
        if not valid:
            return None
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
        except Exception:
            print("  > matplotlib not available, skip pareto plot.")
            return None

        # 论文字体：Times New Roman
        plt.rcParams.update({
            'font.family': 'serif',
            'font.serif': ['Times New Roman'],
            'axes.unicode_minus': False,
            'font.size': 9,
            'axes.labelsize': 9,
            'axes.titlesize': 10,
            'legend.fontsize': 7,
            'xtick.labelsize': 8,
            'ytick.labelsize': 8,
        })

        costs = [ind.raw_objs[0] for ind in valid]
        if use_sf_objective:
            cracks = [ind.info.get('min_sf', 0) for ind in valid]  # SF 值（正数，越大越好）
        else:
            cracks = [ind.raw_objs[1] for ind in valid]
        spacings = [ind.raw_objs[2] for ind in valid]
        diameters = [ind.info.get('diameter', 0) for ind in valid]

        # 自适应标签
        obj2_label = "Safety Factor" if use_sf_objective else "Crack Width (mm)"
        obj2_short = "SF" if use_sf_objective else "Crack"

        base_path = Path(plot_path)
        base_path.parent.mkdir(parents=True, exist_ok=True)
        base_name = base_path.stem
        out_dir = base_path.parent
        out_files = []

        # 穷举前沿数据
        ex_costs, ex_cracks, ex_spacings = [], [], []
        if exhaustive_front:
            ex_valid = [ind for ind in exhaustive_front if ind.is_valid]
            ex_costs = [ind.raw_objs[0] for ind in ex_valid]
            if use_sf_objective:
                ex_cracks = [ind.info.get('min_sf', 0) for ind in ex_valid]
            else:
                ex_cracks = [ind.raw_objs[1] for ind in ex_valid]
            ex_spacings = [ind.raw_objs[2] for ind in ex_valid]

        # Colorblind-friendly 调色板（按直径离散着色）
        unique_dias = sorted(set(diameters))
        # Wong palette extended
        _palette = ['#0072B2', '#E69F00', '#009E73', '#CC79A7',
                     '#56B4E9', '#D55E00', '#F0E442', '#000000',
                     '#882255', '#117733']
        dia_colors = {}
        for i, d in enumerate(unique_dias):
            dia_colors[d] = _palette[i % len(_palette)]
        colors = [dia_colors[d] for d in diameters]

        # 偏好标记
        pref_markers = {
            'cost': ('*', 180, 'Cost-optimal'),
            'safety': ('D', 80, 'Safety-optimal'),
            'construction': ('^', 80, 'Construction-optimal'),
            'balanced': ('o', 100, 'Balanced (TOPSIS)'),
        }

        def _plot_2d(ax, x_all, y_all, xlabel, ylabel, title,
                     ex_x=None, ex_y=None, constraint_lines=None):
            # 穷举底层
            if ex_x and ex_y:
                ax.scatter(ex_x, ex_y, c='#d1d5db', edgecolors='#9ca3af',
                           s=15, alpha=0.5, zorder=1, label='Exhaustive Pareto')
            # NSGA-II 前沿（按直径着色）
            for d in unique_dias:
                mask = [i for i, dia in enumerate(diameters) if dia == d]
                if mask:
                    ax.scatter([x_all[i] for i in mask], [y_all[i] for i in mask],
                               c=dia_colors[d], s=20, alpha=0.8, zorder=2,
                               label=f'D{d}', edgecolors='none')
            # 偏好高亮
            if preference_selections:
                for pref, pref_ind in preference_selections.items():
                    if pref_ind is not None and pref_ind.is_valid:
                        marker, size, label = pref_markers.get(pref, ('o', 80, pref))
                        def _pref_val(ind, axis_label):
                            if 'Cost' in axis_label:
                                return ind.raw_objs[0]
                            elif 'Crack' in axis_label or 'Safety' in axis_label:
                                return ind.info.get('min_sf', 0) if use_sf_objective else ind.raw_objs[1]
                            else:
                                return ind.raw_objs[2]
                        px = _pref_val(pref_ind, xlabel)
                        py = _pref_val(pref_ind, ylabel)
                        ax.scatter([px], [py], marker=marker, s=size,
                                   c='none', edgecolors='#dc2626', linewidths=1.5,
                                   zorder=4, label=label)
            # 约束线
            if constraint_lines:
                for val, axis, style, clabel in constraint_lines:
                    if axis == 'h':
                        ax.axhline(y=val, color='#ef4444', linestyle=style,
                                   linewidth=0.8, alpha=0.7)
                    else:
                        ax.axvline(x=val, color='#6b7280', linestyle=style,
                                   linewidth=0.8, alpha=0.7)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.set_title(title)
            ax.grid(True, alpha=0.2)

        # 提取偏好选中解的原始值用于定位
        def _get_pref_val(pref_ind, idx):
            """idx: 0=cost, 1=crack/sf, 2=spacing"""
            if pref_ind is None or not pref_ind.is_valid:
                return None
            if idx == 1 and use_sf_objective:
                return pref_ind.info.get('min_sf', 0)
            return pref_ind.raw_objs[idx]

        fig, axes = plt.subplots(2, 2, figsize=(7.0, 6.5))

        # (a) Cost vs Crack Width / Safety Factor
        ax = axes[0][0]
        if ex_costs and ex_cracks:
            ax.scatter(ex_costs, ex_cracks, c='#d1d5db', edgecolors='#9ca3af',
                       s=15, alpha=0.5, zorder=1, label='Exhaustive')
        for d in unique_dias:
            mask = [i for i, dia in enumerate(diameters) if dia == d]
            if mask:
                ax.scatter([costs[i] for i in mask], [cracks[i] for i in mask],
                           c=dia_colors[d], s=20, alpha=0.8, zorder=2,
                           label=f'D{d}', edgecolors='none')
        if preference_selections:
            for pref, pref_ind in preference_selections.items():
                if pref_ind and pref_ind.is_valid:
                    marker, size, label = pref_markers.get(pref, ('o', 80, pref))
                    ax.scatter([_get_pref_val(pref_ind, 0)], [_get_pref_val(pref_ind, 1)],
                               marker=marker, s=size, c='none', edgecolors='#dc2626',
                               linewidths=1.5, zorder=4, label=label)
        if use_sf_objective:
            ax.axhline(y=1.0, color='#ef4444', linestyle='--', linewidth=0.8, alpha=0.7)
        else:
            ax.axhline(y=0.2, color='#ef4444', linestyle='--', linewidth=0.8, alpha=0.7)
        ax.set_xlabel("Cost (CNY/m)")
        ax.set_ylabel(obj2_label)
        ax.set_title(f"(a) Cost vs {obj2_short}")
        ax.grid(True, alpha=0.2)

        # (b) Cost vs Spacing
        ax = axes[0][1]
        if ex_costs and ex_spacings:
            ax.scatter(ex_costs, ex_spacings, c='#d1d5db', edgecolors='#9ca3af',
                       s=15, alpha=0.5, zorder=1, label='Exhaustive')
        for d in unique_dias:
            mask = [i for i, dia in enumerate(diameters) if dia == d]
            if mask:
                ax.scatter([costs[i] for i in mask], [spacings[i] for i in mask],
                           c=dia_colors[d], s=20, alpha=0.8, zorder=2,
                           label=f'D{d}', edgecolors='none')
        if preference_selections:
            for pref, pref_ind in preference_selections.items():
                if pref_ind and pref_ind.is_valid:
                    marker, size, label = pref_markers.get(pref, ('o', 80, pref))
                    ax.scatter([_get_pref_val(pref_ind, 0)], [_get_pref_val(pref_ind, 2)],
                               marker=marker, s=size, c='none', edgecolors='#dc2626',
                               linewidths=1.5, zorder=4, label=label)
        ax.axhline(y=250, color='#6b7280', linestyle='--', linewidth=0.8, alpha=0.7)
        ax.set_xlabel("Cost (CNY/m)")
        ax.set_ylabel("Spacing (mm)")
        ax.set_title("(b) Cost vs Spacing")
        ax.grid(True, alpha=0.2)

        # (c) Crack Width / Safety Factor vs Spacing
        ax = axes[1][0]
        if ex_cracks and ex_spacings:
            ax.scatter(ex_cracks, ex_spacings, c='#d1d5db', edgecolors='#9ca3af',
                       s=15, alpha=0.5, zorder=1, label='Exhaustive')
        for d in unique_dias:
            mask = [i for i, dia in enumerate(diameters) if dia == d]
            if mask:
                ax.scatter([cracks[i] for i in mask], [spacings[i] for i in mask],
                           c=dia_colors[d], s=20, alpha=0.8, zorder=2,
                           label=f'D{d}', edgecolors='none')
        if preference_selections:
            for pref, pref_ind in preference_selections.items():
                if pref_ind and pref_ind.is_valid:
                    marker, size, label = pref_markers.get(pref, ('o', 80, pref))
                    ax.scatter([_get_pref_val(pref_ind, 1)], [_get_pref_val(pref_ind, 2)],
                               marker=marker, s=size, c='none', edgecolors='#dc2626',
                               linewidths=1.5, zorder=4, label=label)
        if use_sf_objective:
            ax.axvline(x=1.0, color='#ef4444', linestyle='--', linewidth=0.8, alpha=0.7)
        else:
            ax.axvline(x=0.2, color='#ef4444', linestyle='--', linewidth=0.8, alpha=0.7)
        ax.axhline(y=250, color='#6b7280', linestyle='--', linewidth=0.8, alpha=0.7)
        ax.set_xlabel(obj2_label)
        ax.set_ylabel("Spacing (mm)")
        ax.set_title(f"(c) {obj2_short} vs Spacing")
        ax.grid(True, alpha=0.2)

        # (d) 3D View (supplementary)
        ax = fig.add_subplot(2, 2, 4, projection='3d')
        if ex_costs and ex_cracks and ex_spacings:
            ax.scatter(ex_costs, ex_cracks, ex_spacings, c='#d1d5db',
                       s=10, alpha=0.3, zorder=1)
        for d in unique_dias:
            mask = [i for i, dia in enumerate(diameters) if dia == d]
            if mask:
                ax.scatter([costs[i] for i in mask], [cracks[i] for i in mask],
                           [spacings[i] for i in mask],
                           c=dia_colors[d], s=15, alpha=0.8, zorder=2, label=f'D{d}')
        ax.set_xlabel("Cost", fontsize=7, labelpad=2)
        ax.set_ylabel(obj2_short, fontsize=7, labelpad=2)
        ax.set_zlabel("Spacing", fontsize=7, labelpad=2)
        ax.set_title("(d) 3D View", fontsize=9)
        ax.view_init(elev=25, azim=-45)
        ax.tick_params(labelsize=6)

        # 合并图例（只在 (a) 子图显示）
        handles, labels = axes[0][0].get_legend_handles_labels()
        # 去重
        seen = set()
        unique_handles, unique_labels = [], []
        for h, l in zip(handles, labels):
            if l not in seen:
                seen.add(l)
                unique_handles.append(h)
                unique_labels.append(l)
        if len(unique_labels) <= 12:
            fig.legend(unique_handles, unique_labels, loc='lower center',
                       ncol=min(6, len(unique_labels)), fontsize=7,
                       bbox_to_anchor=(0.5, -0.02), frameon=True, edgecolor='#d1d5db')

        fig.tight_layout(rect=[0, 0.04, 1, 0.98])

        out_path = out_dir / f"{base_name}_pareto.png"
        fig.savefig(str(out_path), dpi=300, bbox_inches='tight')
        plt.close(fig)
        out_files.append(str(out_path))

        plt.rcParams.update(plt.rcParamsDefault)
        return out_files

    def select_solution_by_preference(self, front: List[Individual], preference: str = "balanced") -> Dict:
        """根据用户偏好从帕累托前沿选择方案"""
        valid = [ind for ind in front if ind.is_valid]
        if not valid:
            return None

        if preference == "cost":
            best_ind = min(valid, key=lambda x: x.objs[0])
        elif preference == "safety":
            best_ind = min(valid, key=lambda x: x.objs[1])
        elif preference == "construction":
            best_ind = min(valid, key=lambda x: x.objs[2])
        else:
            return self._topsis_decision(front)

        summary = {
            "grade": best_ind.info.get("grade"),
            "diameter": best_ind.info.get("diameter"),
            "count": int(best_ind.info.get("count", 0)),
            "type": f"{best_ind.info.get('grade')} D{best_ind.info.get('diameter')}",
        }
        return {
            "main_rebar": best_ind.info,
            "summary": summary,
            "metrics": {
                "cost": best_ind.raw_objs[0],
                "max_crack": best_ind.raw_objs[1],
                "spacing": best_ind.raw_objs[2],
                "min_sf": best_ind.info.get("min_sf"),
            }
        }

    def _topsis_decision(self, front: List[Individual]) -> Dict:
        """
        基于 熵权 TOPSIS 的多属性决策，从 Pareto 前沿中选出最优解
        """
        if not front: return None
        # 仅考虑有效解
        valid_front = [ind for ind in front if ind.is_valid]
        if not valid_front: return None
        # --- 1) 熵权 (Entropy Weight) ---
        objs_matrix = [ind.objs for ind in valid_front]
        m = len(objs_matrix)
        n = len(objs_matrix[0])
        if m == 1:
            best_ind = valid_front[0]
            summary = {
                "grade": best_ind.info.get("grade"),
                "diameter": best_ind.info.get("diameter"),
                "count": int(best_ind.info.get("count", 0)),
                "type": f"{best_ind.info.get('grade')} D{best_ind.info.get('diameter')}",
            }
            return {
                "main_rebar": best_ind.info,
                "summary": summary,
                "metrics": {
                    "cost": best_ind.raw_objs[0],
                    "max_crack": best_ind.raw_objs[1],
                    "spacing": best_ind.raw_objs[2],
                    "min_sf": best_ind.info.get("min_sf"),
                }
            }
        # 全部为 Min 问题，先做平移处理以确保非负
        min_vals = [min(col) for col in zip(*objs_matrix)]
        shifted = [
            [val - min_vals[j] + 1e-9 for j, val in enumerate(row)]
            for row in objs_matrix
        ]
        k = 1.0 / math.log(m)
        diversities = []
        for j in range(n):
            col_sum = sum(row[j] for row in shifted)
            if col_sum <= 0:
                diversities.append(0.0)
                continue
            entropy = 0.0
            for i in range(m):
                p = shifted[i][j] / col_sum
                if p > 0:
                    entropy += p * math.log(p)
            entropy = -k * entropy
            diversities.append(1.0 - entropy)
        d_sum = sum(diversities)
        if d_sum <= 1e-12:
            weights = [1.0 / n] * n
        else:
            weights = [d / d_sum for d in diversities]
        # --- 2) TOPSIS ---
        # 向量归一化
        norm_denoms = []
        for j in range(n):
            denom = math.sqrt(sum(row[j] ** 2 for row in shifted))
            norm_denoms.append(denom if denom > 0 else 1.0)
        weighted = []
        for row in shifted:
            weighted.append([
                (row[j] / norm_denoms[j]) * weights[j]
                for j in range(n)
            ])
        # Min 问题: Ideal = min, Nadir = max
        ideal = [min(col) for col in zip(*weighted)]
        nadir = [max(col) for col in zip(*weighted)]
        scores = []
        for idx, wrow in enumerate(weighted):
            dist_pos = math.sqrt(sum((wrow[j] - ideal[j]) ** 2 for j in range(n)))
            dist_neg = math.sqrt(sum((wrow[j] - nadir[j]) ** 2 for j in range(n)))
            if dist_pos + dist_neg <= 1e-12:
                closeness = 0.0
            else:
                closeness = dist_neg / (dist_pos + dist_neg)
            scores.append((closeness, valid_front[idx]))
        # 贴近理想解程度越大越好
        scores.sort(key=lambda x: x[0], reverse=True)
        best_ind = scores[0][1]
        summary = {
            "grade": best_ind.info.get("grade"),
            "diameter": best_ind.info.get("diameter"),
            "count": int(best_ind.info.get("count", 0)),
            "type": f"{best_ind.info.get('grade')} D{best_ind.info.get('diameter')}",
        }
        return {
            "main_rebar": best_ind.info,
            "summary": summary,
            "metrics": {
                "cost": best_ind.raw_objs[0],
                "max_crack": best_ind.raw_objs[1],
                "spacing": best_ind.raw_objs[2],
                "min_sf": best_ind.info.get("min_sf"),
            }
        }

    def exhaustive_enumerate(self, section_params: Dict, force_envelope: List[Dict],
                             use_sf_objective: bool = False) -> Dict:
        """穷举全部 2×10×16=320 种组合，返回穷举 Pareto 前沿

        用作 NSGA-II 的 ground truth 对比（搜索空间小，可穷举）。

        Returns
        -------
        Dict with keys:
            all_valid: List[Individual] — 所有有效解
            pareto_front: List[Individual] — 穷举 Pareto 前沿
            total: int — 总组合数
            valid_count: int — 有效解数量
        """
        print("Exhaustive enumeration: evaluating all combinations...")
        max_s = self.constraints.get_max_spacing_main(section_params.get("h", 500))
        valid_spacing_indices = [i for i, sv in enumerate(self.SPACINGS) if sv <= max_s]
        if not valid_spacing_indices:
            valid_spacing_indices = [0]

        # 生成全部组合
        all_inds = []
        for g_idx in range(len(self.GRADES)):
            for d_idx in range(len(self.DIAMETERS)):
                for s_idx in valid_spacing_indices:
                    all_inds.append(Individual([g_idx, d_idx, s_idx]))

        total = len(all_inds)
        print(f"  > Total combinations: {total}")

        # 并行评估
        self._evaluate_population(all_inds, section_params, force_envelope)

        # 过滤有效解
        all_valid = [ind for ind in all_inds if ind.is_valid]
        valid_count = len(all_valid)
        print(f"  > Valid solutions: {valid_count}/{total}")

        if not all_valid:
            return {
                'all_valid': [],
                'pareto_front': [],
                'total': total,
                'valid_count': 0,
            }

        # 对有效解做非支配排序（使用原始 raw_objs 做支配比较）
        # 需要先设置 objs 为最小化方向
        for ind in all_valid:
            ind.objs = [ind.raw_objs[0], ind.raw_objs[1], -ind.raw_objs[2]]

        # 检测是否需要 SF 目标（穷举时也自适应）
        if not use_sf_objective:
            all_zero_crack = all(ind.raw_objs[1] < 1e-9 for ind in all_valid)
            if all_zero_crack:
                use_sf_objective = True
                print("  > [Adaptive] Exhaustive: all crack ≈ 0, switching to SF objective")

        if use_sf_objective:
            self._apply_sf_objective(all_valid)

        fronts = self._fast_non_dominated_sort(all_valid)
        pareto_front = fronts[0] if fronts else []
        print(f"  > Exhaustive Pareto front size: {len(pareto_front)}")

        return {
            'all_valid': all_valid,
            'pareto_front': pareto_front,
            'total': total,
            'valid_count': valid_count,
        }

    def solve_multi_run(self, section_params: Dict, force_envelope: List[Dict],
                        n_runs: int = 10, pop_size: int = 200, max_gen: int = 200,
                        seed: int = 42, plot_path: str = "pareto_front.png",
                        preference: str = "balanced",
                        exhaustive_front: Optional[List['Individual']] = None) -> Dict:
        """多次独立运行 NSGA-II，收集统计数据

        Parameters
        ----------
        n_runs : int
            独立运行次数，SCI 标准推荐 10 次以上
        seed : int
            基础随机种子，每次运行 seed = base_seed + run_index

        Returns
        -------
        Dict with keys:
            runs: List[Dict] — 每次运行的结果
            stats: Dict — 汇总统计（hv_mean, hv_std, conv_gen_mean, ...）
            best_run: Dict — HV 最优的单次运行结果
            all_gen_histories: List[List[Dict]] — 所有运行的逐代历史
        """
        print(f"\nMulti-run NSGA-II: {n_runs} independent runs (seed base={seed})")
        runs = []
        all_gen_histories = []

        for i in range(n_runs):
            run_seed = seed + i
            print(f"\n--- Run {i+1}/{n_runs} (seed={run_seed}) ---")
            result = self.solve(
                section_params, force_envelope,
                pop_size=pop_size, max_gen=max_gen,
                plot_path=None,  # 不在每次运行时生成图
                preference=preference,
                seed=run_seed,
                exhaustive_front=exhaustive_front,
            )
            if result is None:
                continue

            gen_history = result.get('gen_history', [])
            all_gen_histories.append(gen_history)
            hv_values = [g.get('hv', 0.0) for g in gen_history]
            final_hv = hv_values[-1] if hv_values else 0.0

            # 收敛代数：找到 HV 达到最终值 99% 的代数
            conv_gen = len(gen_history)
            if hv_values and final_hv > 0:
                threshold = 0.99 * final_hv
                for gi, hv in enumerate(hv_values):
                    if hv >= threshold:
                        conv_gen = gi + 1
                        break

            front_size = gen_history[-1].get('size', 0) if gen_history else 0

            runs.append({
                'run_index': i,
                'seed': run_seed,
                'final_hv': final_hv,
                'conv_gen': conv_gen,
                'front_size': front_size,
                'result': result,
                'gen_history': gen_history,
            })

        if not runs:
            return {'runs': [], 'stats': {}, 'best_run': None, 'all_gen_histories': []}

        # 统计汇总
        hvs = [r['final_hv'] for r in runs]
        conv_gens = [r['conv_gen'] for r in runs]
        front_sizes = [r['front_size'] for r in runs]

        def _mean(lst):
            return sum(lst) / len(lst) if lst else 0.0

        def _std(lst):
            if len(lst) < 2:
                return 0.0
            m = _mean(lst)
            return math.sqrt(sum((x - m) ** 2 for x in lst) / (len(lst) - 1))

        stats = {
            'hv_mean': _mean(hvs),
            'hv_std': _std(hvs),
            'hv_min': min(hvs),
            'hv_max': max(hvs),
            'conv_gen_mean': _mean(conv_gens),
            'conv_gen_std': _std(conv_gens),
            'conv_gen_min': min(conv_gens),
            'conv_gen_max': max(conv_gens),
            'front_size_mean': _mean(front_sizes),
            'front_size_std': _std(front_sizes),
            'front_size_min': min(front_sizes),
            'front_size_max': max(front_sizes),
            'n_runs': n_runs,
        }

        # 选出 HV 最优的运行
        best_run = max(runs, key=lambda r: r['final_hv'])

        print(f"\nMulti-run statistics:")
        print(f"  HV: {stats['hv_mean']:.4f} ± {stats['hv_std']:.4f}")
        print(f"  Conv gen: {stats['conv_gen_mean']:.1f} ± {stats['conv_gen_std']:.1f}")
        print(f"  Front size: {stats['front_size_mean']:.1f} ± {stats['front_size_std']:.1f}")

        # 生成多次运行的收敛图（使用最优运行的 gen_history + 全部运行的 multi_run_histories）
        if plot_path and best_run:
            use_sf = best_run['result'].get('use_sf_objective', False)
            self._export_convergence_plot(
                best_run['gen_history'], plot_path,
                multi_run_histories=all_gen_histories,
                use_sf_objective=use_sf,
            )

        return {
            'runs': runs,
            'stats': stats,
            'best_run': best_run,
            'all_gen_histories': all_gen_histories,
        }

if __name__ == "__main__":
    solver = HybridNSGA2Solver()
    # C 鍨嬬鐗?(顶拱)
    section = {
        'b': 1000, 
        'h': 500,  
        'cover': 40,
        'concrete_grade': 'C50'
    }
    f1 = {'design': {'N': 2000, 'M': 400, 'V': 200}, 'quasi':  {'N': 1800, 'M': 300}, 'gamma_d': 1.0}
    f2 = {'design': {'N': 1000, 'M': 600, 'V': 100}, 'quasi':  {'N': 900, 'M': 450}, 'gamma_d': 1.0}
    envelope = [f1, f2]
    result = solver.solve(section, envelope)
    if result:
        summary = result.get("summary", {})
        print(f"\nNSGA-II Final Result: {summary.get('type')} x {summary.get('count')}")
        plots = result.get("pareto_plot")
        if plots:
            if isinstance(plots, list):
                for p in plots:
                    print(f"   Pareto plot: {p}")
            else:
                print(f"   Pareto plot: {plots}")
    else:
        print("Failed to find solution.")
