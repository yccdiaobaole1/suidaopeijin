class CodeConstraints:
    """Design/code constraints used by optimization and checks."""

    # 1) Geometry limits
    MIN_LINING_THICKNESS = 250

    # 2) Reinforcement ratio limits
    MIN_RHO_TOTAL = 0.004
    MIN_RHO_SINGLE = 0.002
    MIN_SAFETY_FACTOR_ULS = 1.1
    MAX_RHO_TOTAL = 0.05

    # 3) Detailing limits
    DEFAULT_COVER = 35

    MIN_DIA_MAIN = 6
    MAX_DIA_MAIN = 25

    # 3) Distribution rebar (分布筋) - TB 10064-2019 9.1.7
    MIN_DIA_DIST = 6  # 直径不宜小于6mm
    MAX_DIA_DIST = 22
    MIN_RATIO_DIST = 0.0015  # 配筋率不宜小于0.15%

    MIN_DIA_STIRRUP = 6
    MAX_DIA_STIRRUP = 20
    MAX_SPACING_STIRRUP = 400

    MIN_BAR_DIAMETER = 6
    MIN_CLEAR_SPACING_ABS = 30

    MIN_SPACING_DISTRIBUTION = 150  # 分布筋最小间距150mm
    MAX_SPACING_DISTRIBUTION = 200  # 分布筋最大间距200mm（TB 10064-2019 9.1.7）

    # 4) Anchorage factors (La/d)
    ANCHORAGE_FACTORS = {
        ('HPB300', 'C20'): 35,
        ('HPB300', 'C25'): 30,
        ('HPB300', 'C30'): 25,
        ('HPB300', 'C35'): 25,
        ('HPB300', 'C40'): 20,
        ('HPB300', 'C45'): 20,
        ('HPB300', 'C50'): 20,

        ('HRB400', 'C20'): 40,
        ('HRB400', 'C25'): 35,
        ('HRB400', 'C30'): 30,
        ('HRB400', 'C35'): 30,
        ('HRB400', 'C40'): 25,
        ('HRB400', 'C45'): 25,
        ('HRB400', 'C50'): 25,

        ('HRB500', 'C20'): 45,
        ('HRB500', 'C25'): 40,
        ('HRB500', 'C30'): 35,
        ('HRB500', 'C35'): 35,
        ('HRB500', 'C40'): 30,
        ('HRB500', 'C45'): 30,
        ('HRB500', 'C50'): 30,
    }

    FACTOR_BIG_DIAMETER = 1.10
    FACTOR_EPOXY = 1.25
    FACTOR_DISTURBED = 1.10

    # 5) Precast-specific limits
    TYPE_RECTANGULAR = 'rectangular'
    TYPE_PRECAST_ARCH = 'precast_arch'

    JOINT_FORBIDDEN_ZONE_WIDTH = 150
    PRECAST_COVER_OUTER = 40
    PRECAST_COVER_INNER = 35
    MIN_RHO_PRECAST_WALL = 0.0025

    @classmethod
    def get_min_clear_spacing(cls, d: float) -> float:
        return max(cls.MIN_CLEAR_SPACING_ABS, d)

    @classmethod
    def get_max_spacing_main(cls, h: float) -> float:
        if h <= 150:
            return 200.0
        return min(1.5 * h, 250.0)

    @classmethod
    def get_constraints(cls, tunnel_type: str, component_type: str, h: float = None) -> dict:
        max_spacing = cls.get_max_spacing_main(h) if h is not None else 250

        constraints = {
            'min_thickness': cls.MIN_LINING_THICKNESS,
            'max_spacing': max_spacing,
            'min_bar_dia': cls.MIN_DIA_MAIN,
            'max_bar_dia': cls.MAX_DIA_MAIN,
            'cover': cls.DEFAULT_COVER,
        }

        if tunnel_type == cls.TYPE_RECTANGULAR:
            if component_type == 'roof':
                constraints['min_bar_dia'] = 10
            elif component_type == 'wall':
                constraints['min_bar_dia'] = 12

        elif tunnel_type == cls.TYPE_PRECAST_ARCH:
            constraints['cover'] = cls.PRECAST_COVER_OUTER
            constraints['min_bar_dia'] = 14
            if component_type == 'C':
                pass

        return constraints
