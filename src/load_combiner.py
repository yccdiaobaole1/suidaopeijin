class LoadCombiner:
    """
    荷载组合器 (适用于隧道及明洞)
    功能：将用户输入的"内力标准值分量"组合成"设计值"和"准永久值"
    依据：Q/CR 9129-2018 4.1节
    """

    def __init__(self, safety_level=2):
        # 结构重要性系数 (一级1.1，二级1.0) [cite: 295]
        self.gamma_0 = 1.1 if safety_level == 1 else 1.0

        # 分项系数 (4.1.5) [cite: 315]
        # 明洞土压力属于永久作用，不利时取 1.4
        self.gamma_G_earth = 1.4
        # 结构自重，不利时取 1.2
        self.gamma_G_self = 1.2
        # 可变作用 (列车/汽车)，取 1.4
        self.gamma_Q = 1.4

        # 准永久值系数 (4.1.12 & 表4.1.4) [cite: 314]
        # 根据明洞顶部实际荷载类型选择：
        # - 铁路活载: 0.9
        # - 公路车辆: 0.7
        # - 人群/轻载: 0.5
        self.psi_q_live = 0.5

    def calculate_loads(self, internal_forces_standard):
        """
        :param internal_forces_standard: 字典，包含各分项内力标准值
            {
                'earth_pressure': {'N': 2000, 'M': 400}, # 明洞回填土压力产生的内力
                'self_weight':    {'N': 500,  'M': 50},  # 自重产生的内力
                'live_load':      {'N': 100,  'M': 20}   # 活载(列车/汽车)产生的内力
            }
        """
        # 1. 提取各分项内力 (标准值)
        # 这里的 N, M 是用户通过有限元软件算出来的，不是代码算出来的
        N_earth = internal_forces_standard.get('earth_pressure', {}).get('N', 0)
        M_earth = internal_forces_standard.get('earth_pressure', {}).get('M', 0)

        N_self = internal_forces_standard.get('self_weight', {}).get('N', 0)
        M_self = internal_forces_standard.get('self_weight', {}).get('M', 0)

        N_live = internal_forces_standard.get('live_load', {}).get('N', 0)
        M_live = internal_forces_standard.get('live_load', {}).get('M', 0)

        # 2. 组合一：承载力极限状态 (ULS) - 设计值
        # 公式：gamma_0 * (1.2*自重 + 1.4*土压 + 1.4*活载)
        # 依据：规范 4.1.4 [cite: 297]
        N_design = self.gamma_0 * (
                self.gamma_G_self * N_self +
                self.gamma_G_earth * N_earth +
                self.gamma_Q * N_live
        )
        M_design = self.gamma_0 * (
                self.gamma_G_self * M_self +
                self.gamma_G_earth * M_earth +
                self.gamma_Q * M_live
        )

        # 3. 组合二：正常使用极限状态 (SLS) - 准永久值
        # 公式：1.0*自重 + 1.0*土压 + psi*活载 (通常系数为1.0)
        # 依据：规范 4.1.12 [cite: 346]
        # 注意：算裂缝时，恒载分项系数取 1.0，不放大！
        N_quasi = (
                1.0 * N_self +
                1.0 * N_earth +
                self.psi_q_live * N_live
        )
        M_quasi = (
                1.0 * M_self +
                1.0 * M_earth +
                self.psi_q_live * M_live
        )

        return {
            'design': {'N': N_design, 'M': M_design},  # 用于算强度安全系数
            'quasi': {'N': N_quasi, 'M': M_quasi},  # 用于算裂缝宽度
            'gamma_d': 1.0
        }
