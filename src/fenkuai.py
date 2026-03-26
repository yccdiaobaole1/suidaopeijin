import math

def calculate_precast_geometry_comprehensive(a, b, c, d, h, w, e, t):
    """
    根据周晓军论文公式(4)至(22)实现，产出图中所有几何参数
    依据：Q/CR 9129-2018 铁路隧道设计规范与论文推导
    """
    # ==========================================
    # 1. 基础输入参数 (Basic Input)
    # ==========================================
    # a: 限界宽度, b: 疏散通道宽度, c: 作业空间宽度
    # d: O1P1距离, h: 隧道净高, w: 隧道净宽, e: 仰拱矢高, t: 衬砌厚度

    # ==========================================
    # 2. 核心几何推导 (Core Derivation)
    # ==========================================
    
    # 2.1 拱部内径与外径 [式20]
    R1 = a + b + c #
    R2 = R1 + t    #

    # 2.2 几何高度 MK5 (用于求角度 beta) [式3, 式4]
    mk5 = math.sqrt(c**2 + 2*c*(a+b)) #
    beta_rad = math.atan(mk5 / (a + b)) #
    beta_deg = math.degrees(beta_rad)

    # 2.3 圆心偏移与拱脚半径 [式6, 式12, 式20]
    # O1O3 是圆心 O1 到 O3 的斜距 (d * csc_beta)
    O1O3 = d / math.sin(beta_rad) #
    R5 = R1 - O1O3 # 拱脚内侧半径
    R6 = R5 + t    # 拱脚外侧半径
    R7 = R5        # 对称侧
    R8 = R6        # 对称侧

    # 2.4 仰拱角度推导 (omega1, omega2) [式10, 式14, 式16]
    # omega1: O1K1P2 角度
    o1p2 = h - R1 - e #
    omega1_rad = math.atan(o1p2 / a) #
    
    # omega2: O1O3K1 角度
    phi1 = R1**2 + a**2 + o1p2**2 - 2 * R1 * O1O3 #
    phi2 = 2 * (R1 - O1O3) * math.sqrt(o1p2**2 + a**2) #
    omega2_rad = math.acos(phi1 / phi2) #
    
    # 组合角 (combined_angle = omega1 + omega2)
    combined_angle = omega1_rad + omega2_rad #

    # 2.5 仰拱半径与圆心偏移 [式18, 式19, 式20]
    R3 = a / math.cos(combined_angle) # 仰拱内径
    R4 = R3 + t                      # 仰拱外径
    O1O2 = a * math.tan(combined_angle) - o1p2 #

    # 2.6 分块角度计算 [式21, 式22]
    delta_rad = (math.pi / 2) - combined_angle # 仰拱半圆心角
    delta_deg = math.degrees(delta_rad)
    
    theta_rad = combined_angle - beta_rad      # 拱脚圆心角
    theta_deg = math.degrees(theta_rad)

    # 2.7 辅助长度段
    k1p2 = a # K1P2 = NO1 = a

    # ==========================================
    # 3. 参数化产出 (Complete Output)
    # ==========================================
    return {
        "Radii": {
            "R1": round(R1, 4), "R2": round(R2, 4),
            "R3": round(R3, 4), "R4": round(R4, 4),
            "R5": round(R5, 4), "R6": round(R6, 4),
            "R7": round(R7, 4), "R8": round(R8, 4)
        },
        "Angles": {
            "beta": round(beta_deg, 3),
            "delta": round(delta_deg, 3),
            "theta": round(theta_deg, 3),
            "omega1": round(math.degrees(omega1_rad), 3),
            "omega2": round(math.degrees(omega2_rad), 3),
            "alpha": 60.0  # 拱顶预制块三等分圆心角
        },
        "Offsets": {
            "O1O2": round(O1O2, 4),
            "O1O3": round(O1O3, 4),
            "O1P1_d": round(d, 4),
            "O1P2": round(o1p2, 4)
        },
        "Segments": {
            "MK5": round(mk5, 4),
            "K1P2": round(k1p2, 4),
            "NO1": round(a, 4)
        },
        "Basic_Params": {
            "a": a, "b": b, "c": c, "h": h, "w": w, "e": e, "t": t
        }
    }

# 使用表3/表4 V级围岩数据验证
if __name__ == "__main__":
    # a=4.8, b=1.5, c=0.35, d=1.42, h=10.88, w=13.3, e=0.7, t=0.7
    results = calculate_precast_geometry_comprehensive(4.8, 1.5, 0.35, 1.42, 10.88, 13.3, 0.7, 0.7)
    
    import json
    print(json.dumps(results, indent=4, ensure_ascii=False))