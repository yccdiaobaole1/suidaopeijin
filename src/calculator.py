import math
from functools import lru_cache
from src.code_constraints import CodeConstraints
from src.rebar_manager import RebarManager
from src.concrete_manager import ConcreteManager


class TunnelCalculator:
    def __init__(self, rebar_manager: RebarManager, concrete_manager: ConcreteManager):
        self.rm = rebar_manager
        self.cm = concrete_manager
        self.constraints = CodeConstraints()
        self._verify_cache = {}

    @staticmethod
    def _get_beta1(fc_value):
        """根据混凝土强度等级确定等效矩形应力图系数β₁

        Q/CR 9129-2018 表9.2.3:
        - fc ≤ 50 MPa: β₁ = 0.8
        - 50 < fc ≤ 80 MPa: 线性插值
        - fc > 80 MPa: β₁ = 0.74
        """
        if fc_value <= 50:
            return 0.8
        elif fc_value <= 80:
            return 0.8 - (fc_value - 50) * 0.002  # 线性插值
        else:
            return 0.74

    @staticmethod
    def _resolve_lambda_bounds(section_params):
        lam_min = float(section_params.get('lambda_min', 1.5))
        lam_max = float(section_params.get('lambda_max', 3.0))
        if lam_min > lam_max:
            lam_min, lam_max = lam_max, lam_min
        return lam_min, lam_max

    @staticmethod
    def _resolve_h_w(section_params, h0, h):
        # 显式口径:
        # - h0: 使用有效高度
        # - section_h: 使用截面总高 h
        # - section_h_w: 使用 section_params['h_w']
        hw_source = str(section_params.get('h_w_source', 'h0')).strip().lower()
        if hw_source == 'section_h':
            return h, hw_source
        if hw_source == 'section_h_w':
            return float(section_params.get('h_w', h0)), hw_source
        # 兼容旧输入: 若直接给 h_w 且未指定来源，默认取 section_h_w
        if 'h_w' in section_params and section_params.get('h_w') is not None and 'h_w_source' not in section_params:
            return float(section_params.get('h_w')), 'section_h_w'
        return h0, 'h0'

    @staticmethod
    def _resolve_n_for_shear(section_params, n_design, n_limit):
        # 默认仅轴压参与（更符合条文“轴向压力设计值”的工程口径）
        # 可切换:
        # - compression_only: max(0, min(N, N_limit))
        # - raw: min(N, N_limit)
        mode = str(section_params.get('shear_n_mode', 'compression_only')).strip().lower()
        if mode == 'raw':
            return min(n_design, n_limit), mode
        return max(0.0, min(n_design, n_limit)), 'compression_only'

    def verify_shear(self, section_params, force_params, rebar_params):
        """
        斜截面受剪验算:
        - 抗剪承载力: V <= Vc + Vs
        - 受剪截面上限: V <= V_max (Q/CR 9129 9.2.7)
        """
        b = section_params['b']
        h = section_params['h']
        c = section_params.get('cover', self.constraints.DEFAULT_COVER)
        conc_grade = section_params.get('concrete_grade', 'C30')

        # 显式口径: V/M 是否按绝对值参与受剪计算（默认 True）
        use_abs_vm = bool(section_params.get('shear_use_abs_vm', True))
        if use_abs_vm:
            V_d = abs(force_params['design']['V'] * 1000.0)
            M_d_shear = abs(force_params['design']['M'] * 1e6)
        else:
            V_d = force_params['design']['V'] * 1000.0
            M_d_shear = force_params['design']['M'] * 1e6

        # 铁路规范中该处通常取 1.0，保持兼容后续扩展
        _gamma_d = force_params.get('gamma_d', 1.0)

        ft = self.cm.get_ft(conc_grade)
        fc = self.cm.get_fc(conc_grade)

        d_main = rebar_params.get('diameter', 20)
        h0 = h - c - d_main / 2.0
        if h0 <= 1e-6:
            h0 = 1e-6

        # 1) 剪跨比 lambda
        lam_min, lam_max = self._resolve_lambda_bounds(section_params)
        if V_d > 1e-3 and h0 > 1e-9:
            lam = M_d_shear / (V_d * h0)
        else:
            lam = lam_max
        lam = max(lam_min, min(lam_max, lam))

        # 2) 轴力项 N，压应力贡献按上限 0.3fcA
        # Q/CR 9129-2018 9.2.8: N 为轴向压力设计值(正值)，取绝对值
        N_d_shear = abs(force_params['design']['N'] * 1000.0)
        A_gross = b * h
        N_limit = 0.3 * fc * A_gross
        N_calc, n_mode = self._resolve_n_for_shear(section_params, N_d_shear, N_limit)

        # 3) 混凝土抗剪贡献 Vc
        alpha_1 = 1.75 / (lam + 1.0)
        Vc = alpha_1 * ft * b * h0 + 0.07 * N_calc

        # 4) 拉筋抗剪贡献 Vs
        stirrup = rebar_params.get('stirrup', None)
        Vs = 0.0
        fyv = 0.0
        Asv = 0.0
        s_v = None
        if stirrup:
            d_v = stirrup['diameter']
            s_v = stirrup['spacing']
            n_legs = stirrup.get('legs', 2)
            grade_v = stirrup.get('grade', 'HPB300')
            fyv = self.rm.get_design_value(grade_v)
            Asv = n_legs * (math.pi * d_v**2 / 4)
            if s_v and s_v > 0:
                Vs = fyv * (Asv / s_v) * h0

        # 5) 承载力验算
        EFFECTIVE_GAMMA_D_SHEAR = float(section_params.get('gamma_d_shear', 1.0))
        if EFFECTIVE_GAMMA_D_SHEAR <= 1e-9:
            EFFECTIVE_GAMMA_D_SHEAR = 1.0
        V_capacity = (Vc + Vs) / EFFECTIVE_GAMMA_D_SHEAR

        # 6) 受剪截面上限验算 (Q/CR 9129 9.2.7)
        h_w, hw_source = self._resolve_h_w(section_params, h0, h)
        ratio_hw_b = h_w / b if b > 1e-9 else 999.0
        if ratio_hw_b <= 4.0:
            coeff = 0.25
        elif ratio_hw_b >= 6.0:
            coeff = 0.20
        else:
            # 4~6 线性插值
            coeff = 0.25 - 0.05 * ((ratio_hw_b - 4.0) / 2.0)
        V_max = coeff * fc * b * h0 / EFFECTIVE_GAMMA_D_SHEAR

        is_safe = (V_capacity >= V_d) and (V_max >= V_d)
        return {
            'is_safe': is_safe,
            'shear_capacity': V_capacity,
            'shear_limit': V_max,
            'shear_demand': V_d,
            'Vc': Vc,
            'Vs': Vs,
            'h0': h0,
            'h_w': h_w,
            'N_calc': N_calc,
            'fyv': fyv,
            'Asv': Asv,
            'stirrup_spacing': s_v,
            'lambda': lam,
            'shear_assumptions': {
                'shear_use_abs_vm': use_abs_vm,
                'lambda_min': lam_min,
                'lambda_max': lam_max,
                'h_w_source': hw_source,
                'shear_n_mode': n_mode,
                'gamma_d_shear': EFFECTIVE_GAMMA_D_SHEAR,
            },
            'ratio': V_d / V_capacity if V_capacity > 0 else 999.0,
            'limit_ratio': V_d / V_max if V_max > 0 else 999.0,
        }


    def _make_cache_key(self, section_params, force_params, rebar_params):
        """生成缓存key"""
        design = force_params.get('design', {})
        quasi = force_params.get('quasi', {})
        return (
            section_params.get('b'), section_params.get('h'), section_params.get('cover'),
            design.get('M'), design.get('N'), design.get('V'),
            quasi.get('M'), quasi.get('N'), quasi.get('V'),
            rebar_params.get('grade'), rebar_params.get('diameter'),
            rebar_params.get('spacing'), rebar_params.get('count')
        )

    def verify_structure(self, section_params, force_params, rebar_params):
        """
        全面验算：承载力(ULS) + 裂缝(SLS) + 构造要求

        精度等级：高 (完全依据规范公式，不使用经验简化值)
        规范依据：Q/CR 9129-2018 铁路隧道设计规范
        """
        # 缓存检查
        cache_key = self._make_cache_key(section_params, force_params, rebar_params)
        if cache_key in self._verify_cache:
            return self._verify_cache[cache_key]

        # ==========================================
        # 1. 数据准备 & 解包
        # ==========================================
        b = section_params['b']
        h = section_params['h']
        c = section_params.get('cover', self.constraints.DEFAULT_COVER)
        conc_grade = section_params.get('concrete_grade', 'C30')

        # 提取荷载 (鍗曚綅杞崲: kN->N, kN.m->N.mm)
        # 承载力验算用设计值(Design Values)
        N_d = force_params['design']['N'] * 1000
        M_d = force_params['design']['M'] * 1e6

        # 裂缝验算用准永久值(Quasi-permanent Values)
        N_q = force_params['quasi']['N'] * 1000
        M_q = force_params['quasi']['M'] * 1e6

        gamma_d = force_params.get('gamma_d', 1.0)  # 结构系数 9.2.6
        # 修正：Q/CR 9129-2018 第9.2.6 鏉¤瀹氱粨鏋勮皟鏁寸郴鏁?gamma_d = 1.0
        # 如果 force_params 中传入了其他值，将被覆盖或作为安全储备
        # 浣嗘牴鎹浘鐗囪瘉鎹紝必须强制 gamma_d = 1.0 鐢ㄤ簬鍏紡 9.2.6-1 ~ 4
        # 为了兼容性，这里修正保持变量名，但计算时需注意是否强制使用
        
        # 获取材料参数
        # 混凝土
        fc = self.cm.get_fc(conc_grade)
        ftk = self.cm.get_ftk(conc_grade)

        # 钢筋
        grade = rebar_params['grade']
        d = rebar_params['diameter']
        n = rebar_params['count']

        fy = self.rm.get_design_value(grade)
        fy_prime = fy
        Es = self.rm.get_Es(grade)

        # 几何属性
        props = self.rm.get_bar_properties(d)
        As = n * props['area']
        As_prime = As

        # 有效高度
        h0 = h - c - d / 2
        as_prime = c + d / 2

        result_msg = []
        is_safe = True

        # ==========================================
        # 2. 鏋勯€犱笌閰嶇瓔鐜囨鏌?(9.5.5)
        # ==========================================
        rho = (As + As_prime) / (b * h)
        if rho < self.constraints.MIN_RHO_TOTAL:
            return {'is_safe': False, 'message': f'配筋率过低({rho:.2%})'}

        rho_single = As / (b * h)
        if rho_single < self.constraints.MIN_RHO_SINGLE:
            return {'is_safe': False, 'message': f'单侧配筋率不足({rho_single:.2%})'}

        # ==========================================
        # 3. 承载力极限状态验算(ULS)
        # ==========================================
        # 3.1 偏心距计算 (9.2.6-3, 9.2.6-4)
        N_d_pos = abs(N_d)  # Q/CR 9129: N pressure is positive
        e0 = abs(M_d) / N_d_pos if N_d_pos > 1e-3 else 0
        ea = max(20, h / 30.0)  # 附加偏心距
        ei = e0 + ea

        # 3.1.1 偏心距增大系数η（规范9.4.6条）
        l0 = section_params.get('l0', h)
        slenderness_ratio = l0 / h

        if slenderness_ratio <= 14:
            eta = 1.0
        else:
            zeta1 = min(1.0, 0.5 * fc * b * h / N_d_pos)
            zeta2 = max(1.0, 1.15 - 0.01 * slenderness_ratio)
            eta = 1.0 + 1.0 / (1400.0 * ei / h0) * (slenderness_ratio ** 2) * zeta1 * zeta2 if ei > 0 and h0 > 0 else 1.0

        ei_modified = eta * ei
        e = ei_modified + h / 2 - as_prime  # 轴力到受拉钢筋距离

        # 3.2 相对界限受压区高度 (9.2.3)
        # 【修正】不再使用固定值.518，而是动态计算，适应HRB500等高强钢筋
        # epsilon_cu = 0.0033 (混凝土极限压应变)
        beta_1 = self._get_beta1(fc)  # 根据混凝土强度动态计算
        xi_b = beta_1 / (1 + fy / (0.0033 * Es))
        xb = xi_b * h0

        # 3.3 迭代求解受压区高度 x (不节省算力，求精解)
        # 平衡方程: N*gamma_d = fc*b*x + fy'*As' - sigma_s*As
        def get_capacity_at_x(x_trial):
            # 根据几何协调条件计算钢筋应力 sigma_s (9.2.6-5 及其推导)
            if x_trial == 0: return 0

            if x_trial <= xb:  # 大偏心受压
                sigma_s = fy
            else:  # 小偏心受压
                # 线性插值近似公式(9.2.6-5)
                # sigma_s = fy * ( (xi/xi_b - 1) / ... ) 的简化形式
                # 规范鍏紡: sigma_s = fy * ( (x/h0 - 0.8)/(xi_b - 0.8) )
                sigma_s = fy * ((x_trial / h0 - 0.8) / (xi_b - 0.8))

            # 物理截断: 应力不能超过强度设计值
            sigma_s = max(-fy_prime, min(fy, sigma_s))

            # 计算当前 x 下能平衡的轴力N_calc
            # 规范 9.2.6-1 变形: N_calc * gamma_d = ...
            # 修正：根据 Q/CR 9129-2018 9.2.6 鏉″浘绀猴紝鍏紡涓殑 gamma_d 固定取1.0
            EFFECTIVE_GAMMA_D = 1.0 
            N_calc = (1.0 / EFFECTIVE_GAMMA_D) * (fc * b * x_trial + fy_prime * As_prime - sigma_s * As)
            return N_calc, sigma_s

        # 二分法精确求解 x，使得 N_calc(x) == N_d
        low, high = 0, h
        final_x = 0
        final_sigma_s = 0

        # 澧炲姞杩唬娆℃暟鑷?50 娆★紝修正濊瘉姣背绾х簿搴?
        for _ in range(50):
            mid = (low + high) / 2
            N_calc, _ = get_capacity_at_x(mid)
            if N_calc > N_d_pos:
                high = mid  # 承载力过大-> 减小 x (瀵逛簬灏忓亸蹇冿紝x减小N减小)
            else:
                low = mid
        final_x = (low + high) / 2
        _, final_sigma_s = get_capacity_at_x(final_x)

        # 3.4 承载力验算 (Q/CR 9129-2018 9.2.6)
        EFFECTIVE_GAMMA_D = 1.0

        if final_x >= 2 * as_prime:
            # 标准公式 9.2.6-2: x >= 2as', 受压钢筋有效
            Mu = (1.0 / EFFECTIVE_GAMMA_D) * (fc * b * final_x * (h0 - final_x / 2.0) + fy_prime * As_prime * (h0 - as_prime))
        else:
            # 9.2.6 要求2: x < 2as', 受压钢筋不在有效受压区
            # 不计入 fy'*As', 重新由力平衡求 x_adj: N = fc*b*x_adj - fy*As
            x_adj = (N_d_pos + fy * As) / (fc * b) if (fc * b) > 1e-9 else final_x
            x_adj = max(0.0, min(x_adj, h))
            Mu = (1.0 / EFFECTIVE_GAMMA_D) * fc * b * x_adj * (h0 - x_adj / 2.0)

        Ne = N_d_pos * e
        if abs(Ne) < 1e-9:
            safety_factor_uls = float('inf')
        else:
            safety_factor_uls = Mu / Ne

        min_sf = section_params.get("min_safety_factor_uls", self.constraints.MIN_SAFETY_FACTOR_ULS)
        if safety_factor_uls < min_sf:
            is_safe = False
            result_msg.append(f"承载力不足(SF={safety_factor_uls:.2f})")
        else:
            result_msg.append("ULS satisfied")
        # 3.5 构造配筋判断（规范9.5.5条）
        As_min = 0.002 * b * h  # 单侧最小配筋率0.2%
        if As < As_min:
            is_safe = False
            result_msg.append(f"配筋不足，需As≥{As_min:.0f}mm²，当前{As:.0f}mm²")

        # ==========================================
        # 4. 正常使用极限状态验算(SLS) - 裂缝宽度
        # ==========================================
        # Q/CR 9129-2018 9.4.4 & 9.4.5 & 9.4.6
        # 隧道衬砌裂缝宽度验算不可跳过，对所有工况均执行完整计算。
        # 规范9.4.5条虽允许 e0/h0≤0.55 的偏心受压构件免验，但为工程安全
        # 及可追溯性，本系统取消该免验条件，全工况强制验算。

        # 4.1 准永久组合偏心距 e0_q (9.4.6-7)
        # 符号约定：本项目轴力拉正压负（N_q<0 为压力）
        # e0 = |Mq|/|Nq|，取绝对值
        e0_q = abs(M_q) / abs(N_q) if abs(N_q) > 1e-3 else 0

        # 4.2 SLS偏心距增大系数 eta_s (Q/CR 9129-2018 9.4.6-8)
        # lo/h <= 14 时取 1.0；否则按公式计算
        if slenderness_ratio <= 14:
            eta_s = 1.0
        else:
            denom = 4000.0 * e0_q / h0 if (h0 > 1e-9 and e0_q > 1e-9) else 1e9
            eta_s = 1.0 + (slenderness_ratio ** 2) / denom if denom > 1e-9 else 1.0

        # 4.3 轴力作用点至纵向受拉钢筋合力点距离 e (9.4.6-6)
        # e = eta_s * e0 + (h/2 - as')
        e_crack = eta_s * e0_q + (h / 2 - as_prime)

        # 4.4 力臂 z (9.4.6-5)
        # z = [0.87 - 0.12*(h0/e)^2]*h0，矩形截面 gamma_f'=0
        # 规范限制：z 不大于 0.87h0
        ratio_he = h0 / e_crack if e_crack > 1e-9 else 0
        z_coef = 0.87 - 0.12 * (ratio_he ** 2)
        z_coef = min(0.87, max(0.7, z_coef))
        z = z_coef * h0

        # 4.5 纵向受拉钢筋应力 sigma_sq (9.4.6-4)
        # sigma_sq = Nq*(e-z) / (As*z)
        if z <= 0 or As <= 0:
            sigma_sq = 0.0
        else:
            sigma_sq = (abs(N_q) * (e_crack - z)) / (As * z)

        # 4.6 判断是否开裂（sigma_sq <= 0 表示全截面受压，无裂缝）
        if sigma_sq <= 0:
            w_max = 0.0
            result_msg.append("SLS: full compression, no crack")
        else:
            # 4.7 有效受拉混凝土面积 Ate (9.4.5): 矩形截面取 0.5bh
            Ate = 0.5 * b * h
            rho_te = As / Ate
            if rho_te < 0.01:
                rho_te = 0.01  # 9.4.5 下限

            # 4.8 裂缝间纵向受拉钢筋应变不均匀系数 psi (9.4.5-2)
            psi = 1.1 - 0.65 * (ftk / (rho_te * sigma_sq))
            psi = max(0.2, min(1.0, psi))

            # 4.9 最大裂缝宽度 wmax (9.4.5-1)
            alpha_cr = 1.9          # 表9.4.5-1：受弯、偏心受压构件
            cs_calc = max(20, min(30, c))  # 9.4.5：cs 限制 20~30mm
            deq = d                 # 同直径带肋钢筋，等效直径 = d

            w_max = alpha_cr * psi * (sigma_sq / Es) * (1.9 * cs_calc + 0.08 * (deq / rho_te))

            LIMIT_CRACK = 0.2  # 9.4.4：最大裂缝宽度限值 0.2mm
            if w_max > LIMIT_CRACK:
                is_safe = False
                result_msg.append(f"crack exceeded({w_max:.3f}mm)")
            else:
                result_msg.append(f"crack OK({w_max:.3f}mm)")

        result = {
            'is_safe': is_safe,
            'safety_factor': safety_factor_uls,
            'crack_width': w_max,
            'sigma_steel': sigma_sq if 'sigma_sq' in locals() else 0,
            'xi_b': xi_b,  # 返回界限高度系数供调试查看
            'message': ", ".join(result_msg)
        }
        self._verify_cache[cache_key] = result
        return result


if __name__ == "__main__":
    # 单元测试
    pass
