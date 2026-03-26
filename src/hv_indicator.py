"""
Hypervolume Indicator — 3D HSO (Hypervolume by Slicing Objectives) 算法

纯 Python 实现，O(n² log n)，n<200 时 <1ms/代。
用于多目标优化收敛性评估（SCI 论文硬性指标）。

所有目标均为最小化方向：[cost, crack, -spacing]
"""

from typing import List


def compute_hypervolume(front_objs: List[List[float]], ref: List[float]) -> float:
    """计算 3D Hypervolume Indicator (HSO 切片法)

    Parameters
    ----------
    front_objs : List[List[float]]
        Pareto 前沿各解的目标值，最小化空间 [cost, crack, -spacing]。
    ref : List[float]
        参考点（各维度均大于前沿最差值），例如首代最差有效解各维 ×1.1。

    Returns
    -------
    float
        被前沿支配的超体积。
    """
    if not front_objs or not ref:
        return 0.0

    # 过滤掉被参考点支配不了的点（任一维度 >= ref 则无贡献）
    points = [p for p in front_objs if all(p[i] < ref[i] for i in range(3))]
    if not points:
        return 0.0

    # 按第一维排序（升序）
    points.sort(key=lambda p: p[0])

    hv = 0.0
    n = len(points)

    for i in range(n):
        # 当前切片在第一维的宽度
        if i + 1 < n:
            x_width = points[i + 1][0] - points[i][0]
        else:
            x_width = ref[0] - points[i][0]

        if x_width <= 0:
            continue

        # 收集当前切片中有贡献的 2D 点（第 2、3 维）
        # 包含 points[0..i] 中所有点在 (obj2, obj3) 平面的投影
        slice_2d = [(points[j][1], points[j][2]) for j in range(i + 1)]

        area_2d = _compute_2d_hypervolume(slice_2d, (ref[1], ref[2]))
        hv += x_width * area_2d

    return hv


def _compute_2d_hypervolume(points_2d: List[tuple], ref_2d: tuple) -> float:
    """计算 2D Hypervolume（阶梯法）

    Parameters
    ----------
    points_2d : List[tuple]
        2D 点集 [(obj2, obj3), ...]，最小化方向。
    ref_2d : tuple
        2D 参考点 (ref_obj2, ref_obj3)。

    Returns
    -------
    float
        2D 超面积。
    """
    # 过滤无效点
    pts = [(y, z) for y, z in points_2d if y < ref_2d[0] and z < ref_2d[1]]
    if not pts:
        return 0.0

    # 按第一维排序（y 升序）
    pts.sort(key=lambda p: p[0])

    # 提取非支配阶梯：y 升序遍历，仅保留 z 严格递减的点
    staircase = []
    min_z = ref_2d[1]
    for y_val, z_val in pts:
        if z_val < min_z:
            staircase.append((y_val, z_val))
            min_z = z_val

    if not staircase:
        return 0.0

    # 计算阶梯面积
    area = 0.0
    for i in range(len(staircase)):
        y_val, z_val = staircase[i]
        y_next = staircase[i + 1][0] if i + 1 < len(staircase) else ref_2d[0]
        y_width = y_next - y_val
        z_height = ref_2d[1] - z_val
        if y_width > 0 and z_height > 0:
            area += y_width * z_height

    return area


def compute_hv_reference(front_objs: List[List[float]], margin: float = 1.1) -> List[float]:
    """根据前沿最差值计算参考点

    Parameters
    ----------
    front_objs : List[List[float]]
        前沿目标值列表。
    margin : float
        各维度最差值的放大系数，默认 1.1。

    Returns
    -------
    List[float]
        参考点 [ref_cost, ref_crack, ref_neg_spacing]。
    """
    if not front_objs:
        return [1.0, 1.0, 1.0]

    n_obj = len(front_objs[0])
    ref = []
    for i in range(n_obj):
        worst = max(p[i] for p in front_objs)
        # 参考点必须严格大于前沿中所有点的对应维度值
        # worst 已经是该维度的最大值，乘以 margin 使其更大
        if worst > 0:
            ref.append(worst * margin)
        elif worst < 0:
            # 负值情况（如 -spacing）：worst=-100, 需要 ref > -100
            # 使用 worst * (2 - margin) 使结果更接近 0（更大）
            # e.g. -100 * 0.9 = -90 > -100 ✓
            ref.append(worst * (2.0 - margin))
        else:
            ref.append(margin)
    return ref
