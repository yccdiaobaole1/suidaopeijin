import math
import sys
import os
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional

# 添加项目根目录到 sys.path，解决直接运行时的 ModuleNotFoundError
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.fenkuai import calculate_precast_geometry_comprehensive

@dataclass
class Point:
    x: float
    y: float

@dataclass
class ArcSegment:
    radius: float
    center: Point
    start_angle: float  # Degrees, standard math (0 = Right, 90 = Top)
    end_angle: float
    length: float

@dataclass
class TunnelSegment:
    segment_id: str
    segment_type: str  # 'A', 'B', 'C'
    geometry: List[ArcSegment]
    start_angle: float
    end_angle: float
    chord_length: float
    arc_length: float

class GeometryModeler:
    """
    铁路隧道明洞几何建模模块
    集成 src.fenkuai 核心算法，实现精准的 "3A+2B+2C" 装配式分块建模
    """
    
    def __init__(self, clearance_width: float, clearance_height: float):
        """
        初始化几何建模器
        :param clearance_width: 隧道净宽 (m) -> w
        :param clearance_height: 隧道净高 (m) -> h
        """
        self.W = clearance_width
        self.H = clearance_height
        
        # 默认参数 (参考周晓军论文 V级围岩)
        # 用户应通过 update_parameters 更新
        self.params = {
            'a': 4.8, 'b': 1.5, 'c': 0.35, 'd': 1.42, 
            'h': self.H, 'w': self.W, 
            'e': 0.7, 't': 0.7
        }
        
        self.profile_arcs: List[ArcSegment] = []
        self.segments: List[TunnelSegment] = []
        self.geo_data = None

    def update_parameters(self, **kwargs):
        """更新几何计算参数 (a, b, c, d, h, w, e, t)"""
        for k, v in kwargs.items():
            if k in self.params:
                self.params[k] = v
        # 参数更新后清除缓存
        self.geo_data = None
        self.profile_arcs = []

    def build_rigorous_profile(self):
        """
        调用 fenkuai.py 核心算法，构建精确的内轮廓 (3段或5段圆弧)
        """
        # 1. 调用核心算法
        try:
            self.geo_data = calculate_precast_geometry_comprehensive(
                self.params['a'], self.params['b'], self.params['c'], 
                self.params['d'], self.params['h'], self.params['w'], 
                self.params['e'], self.params['t']
            )
        except Exception as e:
            print(f"Geometry Calculation Failed: {e}")
            return []

        # 2. 提取几何数据
        radii = self.geo_data['Radii']
        angles = self.geo_data['Angles']
        offsets = self.geo_data['Offsets']
        
        R1 = radii['R1'] # 顶拱
        R3 = radii['R3'] # 仰拱
        R5 = radii['R5'] # 拱脚
        
        beta = angles['beta']
        delta = angles['delta']
        theta = angles['theta']
        
        # 3. 构建圆弧 (ArcSegment)
        # 坐标系: O1 (顶拱圆心) = (0, 0)
        # 角度系: 0=右, 90=上, 180=左, 270=下 (内部坐标系)
        
        self.profile_arcs = []
        
        # --- 3.1 顶拱 (Top Arch, R1) ---
        # 范围: 右侧接头 -> 顶部 -> 左侧接头
        # 右侧接头角度: -beta (即 360 - beta)
        # 左侧接头角度: 180 + beta
        # 注意: beta 是 O1-O3 连线与水平线的夹角 (向下倾斜)
        # 根据 fenkuai 推导，O1-O3 连线角度确为 -beta
        # R1 覆盖范围: [ -beta, 180 + beta ]
        # 分为两段方便处理: [-beta, 90] 和 [90, 180+beta]
        
        arc_top = ArcSegment(
            radius=R1,
            center=Point(0, 0),
            start_angle=-beta, 
            end_angle=180 + beta,
            length=2 * math.pi * R1 * ((180 + 2*beta)/360)
        )
        self.profile_arcs.append(arc_top) # Index 0: Top Arch
        
        # --- 3.2 右拱脚 (Right Arch Foot, R5) ---
        # 圆心 O3_right
        # O3_right 位于 O1O3 距离，角度 -beta
        o1o3_dist = offsets['O1O3']
        o3_right = Point(
            o1o3_dist * math.cos(math.radians(-beta)),
            o1o3_dist * math.sin(math.radians(-beta))
        )
        
        # R5 范围: 上接 R1 (-beta), 下接 R3
        # 下接角度: -90 + delta (即仰拱截止角)
        # R5 覆盖: [-90 + delta, -beta]
        
        # 检查 R5 是否存在 (退化情况)
        if R5 > 0.01:
            arc_foot_right = ArcSegment(
                radius=R5,
                center=o3_right,
                start_angle=-90 + delta,
                end_angle=-beta,
                length=2 * math.pi * R5 * (theta / 360) # theta = beta - (90-delta)? No, theta spans the arc
            )
            self.profile_arcs.append(arc_foot_right) # Index 1: Right Foot
        
        # --- 3.3 左拱脚 (Left Arch Foot, R5) ---
        o3_left = Point(-o3_right.x, o3_right.y) # 对称
        # 范围: [180+beta, 270-delta]
        # 270-delta 等价于 -90-delta? No. 270 is Bottom.
        # Bottom is -90. Left side of invert is -90 - delta (or 270 - delta)
        # Start: 180 + beta. End: 270 - delta.
        
        if R5 > 0.01:
            arc_foot_left = ArcSegment(
                radius=R5,
                center=o3_left,
                start_angle=180 + beta,
                end_angle=270 - delta,
                length=2 * math.pi * R5 * (theta / 360)
            )
            self.profile_arcs.append(arc_foot_left) # Index 2: Left Foot
            
        # --- 3.4 仰拱 (Invert, R3) ---
        # 圆心 O2
        # O2 位于 Y轴，O1O2 下方
        o1o2_dist = offsets['O1O2']
        o2 = Point(0, -o1o2_dist)
        
        # R3 范围: [270 - delta, 270 + delta] (跨越底部)
        # 或者 [-90 - delta, -90 + delta]
        # 为了连续性，我们可以用负角度表示: [-90-delta, -90+delta]
        # 但为了 slice 方便，可能需要归一化
        
        arc_invert = ArcSegment(
            radius=R3,
            center=o2,
            start_angle=270 - delta,
            end_angle=270 + delta + 360 if (270+delta)<(270-delta) else 270+delta, # Handle wrapping if needed, but usually 270-delta < 270+delta
            length=2 * math.pi * R3 * ((2*delta)/360)
        )
        # 修正: 270-delta 到 270+delta 是顺时针? No. standard is CCW.
        # Invert is at bottom. 
        # Right end is -90 + delta (approx -30 deg). 
        # Left end is -90 - delta (approx -150 deg).
        # CCW from Left to Right: -150 -> -30.
        # So start_angle = 270 - delta (Left), end_angle = 270 + delta (Right)?
        # Wait. 270 is -90.
        # 270 - 60 = 210 (Left bottom).
        # 270 + 60 = 330 (Right bottom).
        # CCW from 330 to 210 goes through top. That's the roof.
        # CCW from 210 to 330 goes through bottom. That's the invert.
        # So start = 270 - delta, end = 270 + delta (which is 330 or -30).
        
        arc_invert = ArcSegment(
            radius=R3,
            center=o2,
            start_angle=270 - delta, 
            end_angle=270 + delta,
            length=2 * math.pi * R3 * ((2*delta)/360)
        )
        self.profile_arcs.append(arc_invert) # Index 3: Invert
        
        return self.profile_arcs

    def partition_3A_2B_2C(self):
        """
        基于构建好的精确轮廓，执行 3A+2B+2C 分块 (匹配工程图纸图13)
        A: 拱顶 3 块 (R1 的 0°~180°, 每块 alpha=60°)
        B: 拱脚 2 块 (R1 尾段 + R5)
        C: 仰拱 2 块 (R3 左右各 delta°)
        """
        if not self.profile_arcs:
            self.build_rigorous_profile()

        angles = self.geo_data['Angles']
        alpha = angles['alpha']   # 60° — 拱顶三等分圆心角
        delta = angles['delta']   # ≈15.4° — 仰拱半圆心角

        self.segments = []

        # --- A 型: 拱顶 3 等分, 覆盖 R1 的 [0°, 180°] ---
        self.segments.append(self._slice_profile("A1", "A", 0, alpha))           # 0° -> 60°
        self.segments.append(self._slice_profile("A2", "A", alpha, 2 * alpha))   # 60° -> 120°
        self.segments.append(self._slice_profile("A3", "A", 2 * alpha, 180))     # 120° -> 180°

        # --- B 型: 拱脚, 跨 R1 尾段(beta°) + R5 全段(theta°) ---
        # B1 (右): [-90+delta, 0°]
        self.segments.append(self._slice_profile("B1", "B", -90 + delta, 0))
        # B2 (左): [180°, 270-delta]
        self.segments.append(self._slice_profile("B2", "B", 180, 270 - delta))

        # --- C 型: 仰拱, 覆盖 R3 ---
        # C1 (左): [270-delta, 270°]
        self.segments.append(self._slice_profile("C1", "C", 270 - delta, 270))
        # C2 (右): [270°, 270+delta]
        self.segments.append(self._slice_profile("C2", "C", 270, 270 + delta))

        return self.segments

    def partition_3A_2B_1C(self, ocs_exclusion_angle: float = 20.0):
        """向后兼容别名，调用 partition_3A_2B_2C"""
        return self.partition_3A_2B_2C()

    def _slice_profile(self, sid, stype, start_deg, end_deg) -> TunnelSegment:
        """
        从完整的 profile_arcs 中截取一段 [start_deg, end_deg]
        支持跨越圆弧段的截取 (Composite Segment)
        """
        # 归一化角度到 [0, 360) 用于比较? 
        # 或者保持连续性。我们使用的 profile 是分段定义的。
        # R1: [-beta, 180+beta]
        # R5_right: [-90+delta, -beta]
        # R5_left: [180+beta, 270-delta]
        # R3: [270-delta, 270+delta]
        
        # 为了方便，我们将所有角度映射到 [0, 360) 进行处理
        # 0=Right, 90=Top, 180=Left, 270=Bottom
        
        def normalize(a):
            return a % 360
            
        s = normalize(start_deg)
        e = normalize(end_deg)
        
        # 如果跨越 0 度 (e.g. 330 -> 30), e < s
        is_crossing = e < s
        
        sliced_arcs = []
        total_len = 0
        chord_start_pt = None
        chord_end_pt = None
        
        # 遍历所有基础圆弧，检查重叠部分
        for arc in self.profile_arcs:
            # Arc range
            as_n = normalize(arc.start_angle)
            ae_n = normalize(arc.end_angle)
            arc_cross = ae_n < as_n
            
            # 判断重叠逻辑略复杂，简化为：采样点判断 or 区间交集
            # 这里采用区间交集法
            # 将 Segment 区间 [s, e] 与 Arc 区间 [as, ae] 求交
            
            # 简单处理：仅考虑包含关系。
            # 实际上，Segment 可能只取 Arc 的一部分。
            # 我们需要计算 "交集区间" [max(s, as), min(e, ae)]
            # 但要注意周期性。
            
            # 这里的核心难点是角度的周期性处理。
            # 临时方案：将所有角度转为 "距 C1 中心 (90度)" 的相对角度?
            # 或者，由于我们知道 segment 的大致位置，直接按类型匹配?
            # 不，为了通用性，应该计算交集。
            
            # 让我们定义一个 helper 来计算两个角度区间的交集
            intersection = self._get_angle_intersection(s, e, as_n, ae_n)
            
            if intersection:
                int_s, int_e = intersection
                # 构建新的圆弧段
                # 弧长
                span = (int_e - int_s) % 360
                length = 2 * math.pi * arc.radius * (span / 360)
                
                new_arc = ArcSegment(
                    radius=arc.radius,
                    center=arc.center,
                    start_angle=int_s,
                    end_angle=int_e,
                    length=length
                )
                sliced_arcs.append(new_arc)
                total_len += length
                
                # 记录端点用于计算弦长
                # Start point of the FIRST arc piece
                if len(sliced_arcs) == 1:
                    chord_start_pt = self._get_point_on_arc(arc, int_s)
                
                # End point of the LAST arc piece
                # (Update every time, final one is correct)
                chord_end_pt = self._get_point_on_arc(arc, int_e)

        # 计算弦长
        chord = 0
        if chord_start_pt and chord_end_pt:
            dx = chord_start_pt.x - chord_end_pt.x
            dy = chord_start_pt.y - chord_end_pt.y
            chord = math.sqrt(dx*dx + dy*dy)
            
        return TunnelSegment(
            segment_id=sid,
            segment_type=stype,
            geometry=sliced_arcs,
            start_angle=start_deg,
            end_angle=end_deg,
            chord_length=chord,
            arc_length=total_len
        )

    def _get_point_on_arc(self, arc: ArcSegment, angle_deg: float) -> Point:
        rad = math.radians(angle_deg)
        return Point(
            arc.center.x + arc.radius * math.cos(rad),
            arc.center.y + arc.radius * math.sin(rad)
        )

    def _get_angle_intersection(self, s1, e1, s2, e2) -> Optional[Tuple[float, float]]:
        """
        计算两个角度区间的交集 (CCW from s to e)
        Inputs are normalized [0, 360)
        Returns (start, end) or None
        """
        # 展开 s1, e1 到线性轴，处理跨越
        if e1 < s1: e1 += 360
        if e2 < s2: e2 += 360
        
        # 现在区间是 [s1, e1] 和 [s2, e2]
        # 还需要考虑 s2 可能在 s1 之前一圈，或者之后一圈
        # 尝试 s2, s2+360, s2-360
        
        candidates = []
        for shift in [-360, 0, 360]:
            S2, E2 = s2 + shift, e2 + shift
            
            start = max(s1, S2)
            end = min(e1, E2)
            
            if start < end: # 有交集
                # 归一化输出
                return (start % 360, end % 360)
        
        return None

if __name__ == "__main__":
    # Test Integration
    modeler = GeometryModeler(13.3, 10.88)
    modeler.update_parameters(a=4.8, b=1.5, c=0.35, d=1.42, e=0.7, t=0.7)
    
    print(">>> Building Rigorous Profile...")
    modeler.build_rigorous_profile()
    for i, arc in enumerate(modeler.profile_arcs):
        print(f"Arc {i}: R={arc.radius:.2f}, Ang=[{arc.start_angle:.1f}, {arc.end_angle:.1f}]")
        
    print("\n>>> Partitioning 3A+2B+2C...")
    segs = modeler.partition_3A_2B_2C()
    for s in segs:
        print(f"Segment {s.segment_id} ({s.segment_type}): {s.start_angle:.1f}° -> {s.end_angle:.1f}° L={s.arc_length:.2f}m")
