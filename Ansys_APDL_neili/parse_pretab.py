#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ANSYS PRETAB.lis 内力数据解析器
将ANSYS输出的内力表格转换为易读的CSV格式
"""

import re
import csv
from pathlib import Path


def parse_pretab_lis(input_file, output_file):
    """
    解析PRETAB.lis文件并转换为CSV格式

    Args:
        input_file: PRETAB.lis文件路径
        output_file: 输出CSV文件路径
    """
    data_rows = []

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 解析数据行
    for line in lines:
        # 匹配数据行格式：单元号 + 三个数值
        # 示例: "    1785  0.13443E+006 -1709.1      0.83803"
        match = re.match(r'\s+(\d+)\s+([-+]?\d+\.?\d*E?[+-]?\d*)\s+([-+]?\d+\.?\d*)\s+([-+]?\d+\.?\d*)', line)
        if match:
            elem_id = int(match.group(1))
            wji = float(match.group(2)) / 1000  # 弯矩 (N·m -> kN·m)
            zli = float(match.group(3))  # 轴力 (kN，原始单位已经是kN)
            jli = float(match.group(4))  # 剪力 (kN，原始单位已经是kN)

            data_rows.append({
                '单元编号': elem_id,
                '弯矩 (kN·m)': wji,
                '轴力 (kN)': zli,
                '剪力 (kN)': jli
            })

    # 按单元编号排序
    data_rows.sort(key=lambda x: x['单元编号'])

    # 写入CSV文件
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        if data_rows:
            fieldnames = ['单元编号', '弯矩 (kN·m)', '轴力 (kN)', '剪力 (kN)']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data_rows)

    # 计算统计信息
    if data_rows:
        wji_values = [row['弯矩 (kN·m)'] for row in data_rows]
        zli_values = [row['轴力 (kN)'] for row in data_rows]
        jli_values = [row['剪力 (kN)'] for row in data_rows]

        stats = {
            '弯矩': {
                '最大值': max(wji_values),
                '最小值': min(wji_values),
                '最大值单元': data_rows[wji_values.index(max(wji_values))]['单元编号'],
                '最小值单元': data_rows[wji_values.index(min(wji_values))]['单元编号']
            },
            '轴力': {
                '最大值': max(zli_values),
                '最小值': min(zli_values),
                '最大值单元': data_rows[zli_values.index(max(zli_values))]['单元编号'],
                '最小值单元': data_rows[zli_values.index(min(zli_values))]['单元编号']
            },
            '剪力': {
                '最大值': max(jli_values),
                '最小值': min(jli_values),
                '最大值单元': data_rows[jli_values.index(max(jli_values))]['单元编号'],
                '最小值单元': data_rows[jli_values.index(min(jli_values))]['单元编号']
            }
        }

        return len(data_rows), stats

    return 0, None


def main():
    input_file = Path(__file__).parent / 'PRETAB.lis'
    output_file = Path(__file__).parent / '衬砌内力数据.csv'

    print("正在解析 PRETAB.lis 文件...")
    count, stats = parse_pretab_lis(input_file, output_file)

    if count > 0:
        print(f"\n[OK] 成功解析 {count} 个单元的内力数据")
        print(f"[OK] CSV文件已保存至: {output_file}")

        print("\n" + "="*60)
        print("内力统计信息")
        print("="*60)

        print("\n【弯矩】")
        print(f"  最大值: {stats['弯矩']['最大值']:>15.2f} kN*m  (单元 {stats['弯矩']['最大值单元']})")
        print(f"  最小值: {stats['弯矩']['最小值']:>15.2f} kN*m  (单元 {stats['弯矩']['最小值单元']})")

        print("\n【轴力】")
        print(f"  最大值: {stats['轴力']['最大值']:>15.2f} kN    (单元 {stats['轴力']['最大值单元']})")
        print(f"  最小值: {stats['轴力']['最小值']:>15.2f} kN    (单元 {stats['轴力']['最小值单元']})")

        print("\n【剪力】")
        print(f"  最大值: {stats['剪力']['最大值']:>15.2f} kN    (单元 {stats['剪力']['最大值单元']})")
        print(f"  最小值: {stats['剪力']['最小值']:>15.2f} kN    (单元 {stats['剪力']['最小值单元']})")

        print("\n" + "="*60)
    else:
        print("[ERROR] 未找到有效数据")


if __name__ == '__main__':
    main()
