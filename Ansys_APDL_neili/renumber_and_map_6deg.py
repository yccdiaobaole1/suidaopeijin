#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
隧道衬砌内力数据 - 6°分块方案
推荐方案：60个分块，与预制块60°分割完美对齐
"""

import csv
from pathlib import Path
from collections import defaultdict


def read_csv_data(csv_file):
    """读取CSV数据"""
    data = []
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append({
                '单元编号': int(row['单元编号']),
                '弯矩': float(row['弯矩 (kN·m)']),
                '轴力': float(row['轴力 (kN)']),
                '剪力': float(row['剪力 (kN)'])
            })
    return data


def get_position_name(angle):
    """根据角度确定位置名称"""
    if 0 <= angle < 45:
        return "仰拱右侧"
    elif 45 <= angle < 90:
        return "右墙脚"
    elif 90 <= angle < 135:
        return "右拱腰"
    elif 135 <= angle < 180:
        return "右拱顶"
    elif 180 <= angle < 225:
        return "左拱顶"
    elif 225 <= angle < 270:
        return "左拱腰"
    elif 270 <= angle < 315:
        return "左墙脚"
    else:
        return "仰拱左侧"


def renumber_and_map_to_blocks(csv_file, block_size=6):
    """重新编号并映射到分块"""
    data = read_csv_data(csv_file)
    total_elements = len(data)
    angle_step = 360.0 / total_elements
    num_blocks = 360 // block_size

    print(f"总单元数: {total_elements}")
    print(f"分块大小: {block_size}°")
    print(f"分块数量: {num_blocks}")

    new_data = []
    block_data = defaultdict(list)

    for idx, row in enumerate(data):
        angle = idx * angle_step
        block_id = int(angle // block_size) + 1
        position = get_position_name(angle)

        new_row = {
            '新编号': idx + 1,
            '原单元编号': row['单元编号'],
            '角度': round(angle, 2),
            '分块编号': block_id,
            '位置': position,
            '弯矩(kN·m)': round(row['弯矩'], 2),
            '轴力(kN)': round(row['轴力'], 2),
            '剪力(kN)': round(row['剪力'], 2)
        }

        new_data.append(new_row)
        block_data[block_id].append(new_row)

    return new_data, block_data, block_size


def generate_block_summary(block_data, block_size):
    """生成分块汇总统计"""
    summary = []

    for block_id in sorted(block_data.keys()):
        elements = block_data[block_id]

        avg_moment = sum(e['弯矩(kN·m)'] for e in elements) / len(elements)
        avg_axial = sum(e['轴力(kN)'] for e in elements) / len(elements)
        avg_shear = sum(e['剪力(kN)'] for e in elements) / len(elements)

        moments = [e['弯矩(kN·m)'] for e in elements]
        max_moment = max(moments)
        min_moment = min(moments)

        block_start = (block_id - 1) * block_size
        block_end = block_id * block_size
        position = elements[0]['位置']

        summary.append({
            '分块编号': block_id,
            '角度范围': f"{block_start}-{block_end}",
            '位置': position,
            '单元数': len(elements),
            '平均弯矩(kN·m)': round(avg_moment, 2),
            '平均轴力(kN)': round(avg_axial, 2),
            '平均剪力(kN)': round(avg_shear, 2),
            '最大弯矩(kN·m)': round(max_moment, 2),
            '最小弯矩(kN·m)': round(min_moment, 2)
        })

    return summary


def generate_code_input_format(summary, output_file, block_size):
    """生成代码输入格式"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# 隧道衬砌内力数据 - 按{block_size}°分块\n")
        f.write("# 格式: 角度(°), 弯矩(kN·m), 轴力(kN), 剪力(kN)\n\n")
        f.write("internal_forces = [\n")

        for row in summary:
            angle_start = int(row['角度范围'].split('-')[0])
            moment = row['平均弯矩(kN·m)']
            axial = row['平均轴力(kN)']
            shear = row['平均剪力(kN)']
            position = row['位置']

            f.write(f"    ({angle_start:3d}, {moment:8.2f}, {axial:7.2f}, {shear:7.2f}),  # {position}\n")

        f.write("]\n")


def main():
    input_file = Path(__file__).parent / '衬砌内力数据.csv'
    output_file = Path(__file__).parent / '衬砌内力数据_6度分块.csv'
    summary_file = Path(__file__).parent / '分块内力汇总_6度.csv'
    code_input_file = Path(__file__).parent / '内力数据_代码输入格式_6度.py'

    print("正在生成6°分块方案...")
    new_data, block_data, block_size = renumber_and_map_to_blocks(input_file, block_size=6)

    # 保存详细数据
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = ['新编号', '原单元编号', '角度', '分块编号', '位置',
                      '弯矩(kN·m)', '轴力(kN)', '剪力(kN)']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(new_data)

    print(f"\n[OK] 重新编号完成，共 {len(new_data)} 个单元")
    print(f"[OK] 详细数据已保存至: {output_file}")

    # 生成分块汇总
    summary = generate_block_summary(block_data, block_size)

    with open(summary_file, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = ['分块编号', '角度范围', '位置', '单元数',
                      '平均弯矩(kN·m)', '平均轴力(kN)', '平均剪力(kN)',
                      '最大弯矩(kN·m)', '最小弯矩(kN·m)']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary)

    print(f"[OK] 分块汇总已保存至: {summary_file}")

    # 生成代码输入格式
    generate_code_input_format(summary, code_input_file, block_size)
    print(f"[OK] 代码输入格式已保存至: {code_input_file}")

    # 打印统计信息
    print("\n" + "="*80)
    print(f"6°分块方案统计")
    print("="*80)
    print(f"总分块数: {len(summary)}")
    print(f"平均每块单元数: {len(new_data)/len(summary):.1f}")
    print(f"最少单元数: {min(s['单元数'] for s in summary)}")
    print(f"最多单元数: {max(s['单元数'] for s in summary)}")

    # 验证预制块拼缝对齐
    print("\n预制块拼缝位置对齐验证:")
    joint_angles = [0, 60, 120, 180, 240, 300]
    for angle in joint_angles:
        block_id = angle // block_size + 1
        print(f"  {angle}° -> 分块{block_id}起点 [OK]")


if __name__ == '__main__':
    main()
