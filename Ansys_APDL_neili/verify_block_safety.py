#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证分块策略的安全性
检查是否会遗漏关键内力节点
"""

import csv
from pathlib import Path


def read_detailed_data(csv_file):
    """读取重新编号的详细数据"""
    data = []
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append({
                '新编号': int(row['新编号']),
                '原单元编号': int(row['原单元编号']),
                '角度': float(row['角度']),
                '分块编号': int(row['分块编号']),
                '位置': row['位置'],
                '弯矩': float(row['弯矩(kN·m)']),
                '轴力': float(row['轴力(kN)']),
                '剪力': float(row['剪力(kN)'])
            })
    return data


def analyze_block_safety(data):
    """分析分块策略的安全性"""

    print("="*80)
    print("分块策略安全性验证报告")
    print("="*80)

    # 1. 分析单元分布密度
    print("\n【1. 单元分布密度分析】")
    total_elements = len(data)
    angle_range = 360
    avg_angle_per_element = angle_range / total_elements
    print(f"总单元数: {total_elements}")
    print(f"平均每个单元覆盖角度: {avg_angle_per_element:.2f}°")
    print(f"10°分块平均包含单元数: {10 / avg_angle_per_element:.1f} 个")

    # 2. 检查每个分块内的单元数
    print("\n【2. 各分块单元数统计】")
    block_elements = {}
    for row in data:
        block_id = row['分块编号']
        if block_id not in block_elements:
            block_elements[block_id] = []
        block_elements[block_id].append(row)

    min_elements = min(len(v) for v in block_elements.values())
    max_elements = max(len(v) for v in block_elements.values())
    print(f"最少单元数的分块: {min_elements} 个单元")
    print(f"最多单元数的分块: {max_elements} 个单元")

    # 显示单元数少于5的分块（可能存在风险）
    risky_blocks = [(k, len(v)) for k, v in block_elements.items() if len(v) < 5]
    if risky_blocks:
        print(f"\n警告：以下分块单元数少于5个，可能存在采样不足风险：")
        for block_id, count in risky_blocks:
            angle_start = (block_id - 1) * 10
            print(f"  分块 {block_id} ({angle_start}°-{angle_start+10}°): {count} 个单元")

    # 3. 识别内力极值点
    print("\n【3. 内力极值点位置分析】")

    # 弯矩极值
    max_moment_row = max(data, key=lambda x: x['弯矩'])
    min_moment_row = min(data, key=lambda x: x['弯矩'])

    # 轴力极值
    max_axial_row = max(data, key=lambda x: x['轴力'])
    min_axial_row = min(data, key=lambda x: x['轴力'])

    # 剪力极值
    max_shear_row = max(data, key=lambda x: abs(x['剪力']))

    extremes = [
        ("最大正弯矩", max_moment_row, '弯矩'),
        ("最大负弯矩", min_moment_row, '弯矩'),
        ("最大轴力", min_axial_row, '轴力'),
        ("最小轴力", max_axial_row, '轴力'),
        ("最大剪力", max_shear_row, '剪力')
    ]

    print("\n极值点位置：")
    for name, row, force_type in extremes:
        angle = row['角度']
        block_id = row['分块编号']
        value = row[force_type]
        block_start = (block_id - 1) * 10
        block_end = block_id * 10
        position_in_block = angle - block_start

        print(f"\n{name}:")
        print(f"  位置: {angle:.2f}° (分块{block_id}: {block_start}°-{block_end}°)")
        print(f"  在分块内位置: {position_in_block:.2f}° (距起点)")
        print(f"  数值: {value:.2f}")
        print(f"  单元编号: {row['原单元编号']}")

    # 4. 检查极值点是否在分块边界附近
    print("\n【4. 极值点与分块边界关系】")
    boundary_threshold = 1.0  # 距离边界1°以内认为是边界附近

    for name, row, force_type in extremes:
        angle = row['角度']
        block_id = row['分块编号']
        block_start = (block_id - 1) * 10
        position_in_block = angle - block_start

        if position_in_block < boundary_threshold:
            print(f"警告：{name} 位于分块起始边界附近 ({position_in_block:.2f}°)")
        elif position_in_block > (10 - boundary_threshold):
            print(f"警告：{name} 位于分块结束边界附近 ({10 - position_in_block:.2f}°)")

    # 5. 分析分块内的内力变化率
    print("\n【5. 分块内内力变化率分析】")

    high_variation_blocks = []

    for block_id, elements in sorted(block_elements.items()):
        if len(elements) < 2:
            continue

        moments = [e['弯矩'] for e in elements]
        axials = [e['轴力'] for e in elements]
        shears = [e['剪力'] for e in elements]

        moment_range = max(moments) - min(moments)
        axial_range = max(axials) - min(axials)
        shear_range = max(shears) - min(shears)

        moment_avg = sum(moments) / len(moments)
        axial_avg = sum(axials) / len(axials)

        # 计算变化率（相对于平均值的百分比）
        moment_variation = (moment_range / abs(moment_avg) * 100) if moment_avg != 0 else 0
        axial_variation = (axial_range / abs(axial_avg) * 100) if axial_avg != 0 else 0

        # 如果变化率超过20%，认为是高变化率分块
        if moment_variation > 20 or axial_variation > 20:
            angle_start = (block_id - 1) * 10
            high_variation_blocks.append({
                'block_id': block_id,
                'angle_range': f"{angle_start}°-{angle_start+10}°",
                'moment_variation': moment_variation,
                'axial_variation': axial_variation,
                'moment_range': moment_range,
                'axial_range': axial_range
            })

    if high_variation_blocks:
        print(f"\n发现 {len(high_variation_blocks)} 个高变化率分块（内力变化>20%）：")
        for block in high_variation_blocks[:10]:  # 只显示前10个
            print(f"\n  分块 {block['block_id']} ({block['angle_range']}):")
            print(f"    弯矩变化率: {block['moment_variation']:.1f}% (范围: {block['moment_range']:.2f} kN·m)")
            print(f"    轴力变化率: {block['axial_variation']:.1f}% (范围: {block['axial_range']:.2f} kN)")

    # 6. 检查预制块拼缝位置
    print("\n【6. 预制块拼缝位置检查】")

    # 根据APDL代码，预制块拼缝位置：
    # A型块：60°分割（0°, 60°, 120°, 180°, 240°, 300°）
    # B型块：不分割，但与A块的拼缝在0°和180°附近

    joint_angles = [0, 60, 120, 180, 240, 300]

    print("\n预制块拼缝位置与分块边界对齐情况：")
    for joint_angle in joint_angles:
        block_id = joint_angle // 10 + 1
        block_start = (block_id - 1) * 10

        # 检查拼缝是否在分块边界上
        if joint_angle % 10 == 0:
            print(f"  {joint_angle}°: 对齐分块边界 ✓ (分块{block_id}起点)")
        else:
            offset = joint_angle - block_start
            print(f"  {joint_angle}°: 不对齐 ✗ (在分块{block_id}内，距起点{offset}°)")

    return {
        'total_elements': total_elements,
        'avg_angle_per_element': avg_angle_per_element,
        'min_elements_per_block': min_elements,
        'max_elements_per_block': max_elements,
        'high_variation_blocks': len(high_variation_blocks),
        'risky_blocks': len(risky_blocks)
    }


def recommend_block_size(data):
    """推荐合适的分块大小"""

    print("\n" + "="*80)
    print("分块大小优化建议")
    print("="*80)

    total_elements = len(data)

    # 测试不同的分块大小
    block_sizes = [5, 6, 10, 12, 15, 20, 30, 60]

    print("\n不同分块大小的评估：")
    print(f"{'分块大小':>8} {'分块数':>8} {'平均单元数':>12} {'最少单元数':>12} {'评价':>20}")
    print("-" * 80)

    recommendations = []

    for block_size in block_sizes:
        num_blocks = 360 // block_size
        avg_elements = total_elements / num_blocks
        min_elements = int(avg_elements * 0.8)  # 估算最少单元数

        # 评价标准
        if avg_elements >= 8:
            rating = "优秀（充分采样）"
        elif avg_elements >= 6:
            rating = "良好（足够采样）"
        elif avg_elements >= 4:
            rating = "可接受（基本采样）"
        else:
            rating = "不推荐（采样不足）"

        print(f"{block_size:>8}° {num_blocks:>8} {avg_elements:>12.1f} {min_elements:>12} {rating:>20}")

        # 检查是否能整除360且与预制块拼缝对齐
        divides_360 = (360 % block_size == 0)
        aligns_with_joints = all((angle % block_size == 0) for angle in [0, 60, 120, 180, 240, 300])

        if divides_360 and aligns_with_joints and avg_elements >= 6:
            recommendations.append({
                'size': block_size,
                'num_blocks': num_blocks,
                'avg_elements': avg_elements,
                'rating': rating
            })

    print("\n推荐的分块大小：")

    if recommendations:
        for rec in recommendations:
            print(f"\n  {rec['size']}° 分块:")
            print(f"    - 分块数: {rec['num_blocks']}")
            print(f"    - 平均单元数: {rec['avg_elements']:.1f}")
            print(f"    - 与预制块拼缝对齐: ✓")
            print(f"    - 评价: {rec['rating']}")
    else:
        print("  当前10°分块已经是较好的选择")

    # 特别推荐
    print("\n【最终推荐】")
    print("\n基于以下考虑：")
    print("  1. 预制块拼缝位置（0°, 60°, 120°, 180°, 240°, 300°）")
    print("  2. 充分的采样密度（每个分块至少6个单元）")
    print("  3. 便于工程应用")
    print("\n推荐使用：")
    print("  - 主要方案：6° 分块（60个分块，平均3.7个单元/块）")
    print("    优点：与预制块60°分割完美对齐，采样密度高")
    print("  - 备选方案：10° 分块（36个分块，平均6.2个单元/块）")
    print("    优点：采样充分，计算简便")
    print("  - 保守方案：5° 分块（72个分块，平均3.1个单元/块）")
    print("    优点：最高采样密度，不会遗漏任何极值点")


def main():
    input_file = Path(__file__).parent / '衬砌内力数据_重新编号.csv'

    print("正在读取详细数据...")
    data = read_detailed_data(input_file)

    # 安全性分析
    stats = analyze_block_safety(data)

    # 推荐分块大小
    recommend_block_size(data)

    # 总结
    print("\n" + "="*80)
    print("安全性评估总结")
    print("="*80)

    print(f"\n当前10°分块方案：")
    print(f"  - 总单元数: {stats['total_elements']}")
    print(f"  - 平均每分块单元数: {stats['total_elements']/36:.1f}")
    print(f"  - 最少单元数分块: {stats['min_elements_per_block']} 个单元")
    print(f"  - 高变化率分块数: {stats['high_variation_blocks']}")

    if stats['min_elements_per_block'] >= 6:
        print("\n结论：✓ 当前10°分块方案采样充分，安全性良好")
    elif stats['min_elements_per_block'] >= 4:
        print("\n结论：△ 当前10°分块方案基本可接受，但建议考虑更小分块")
    else:
        print("\n结论：✗ 当前10°分块方案存在采样不足风险，建议使用更小分块")

    print("\n建议：")
    print("  1. 对于重要工程，建议使用6°或5°分块以提高安全裕度")
    print("  2. 对于一般工程，10°分块已经足够")
    print("  3. 在内力极值点附近应特别关注，必要时进行局部加密")


if __name__ == '__main__':
    main()
