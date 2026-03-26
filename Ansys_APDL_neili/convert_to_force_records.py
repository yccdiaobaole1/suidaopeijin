#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将ANSYS内力数据转换为配筋系统输入格式
"""
import csv

# 导入ANSYS数据
from 内力数据_代码输入格式_6度 import internal_forces

def convert_to_force_records(output_path='../force_records.csv'):
    """
    转换ANSYS数据为配筋系统格式

    荷载性质说明：
    - ANSYS模型施加的是标准值（BL=1.0，无分项系数）：
        竖向土压 Q1=Q2=174400 Pa，侧向土压 E1~E4=29900~68100 Pa，结构自重 ACEL=9.8
    - 本模型无活载，全部为永久作用（土压+自重）

    荷载分项系数（Q/CR 9129-2018 4.1.5，偏安全取值）：
    - 设计值（ULS）：γ_G = 1.4（永久不利，土压控制，偏安全统一取1.4）
    - 准永久值（SLS）：系数 = 1.0（永久荷载准永久值系数为1.0，无活载）
    """
    # ULS分项系数：永久不利取1.4（土压控制，偏安全）
    GAMMA_G = 1.4
    # SLS准永久值系数：纯永久荷载取1.0
    PSI_Q = 1.0

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # 写入表头
        writer.writerow(['angle', 'design_N', 'design_M', 'design_V',
                        'quasi_N', 'quasi_M', 'quasi_V', 'gamma_d'])

        # 转换每个角度点
        for angle, M, N, V in internal_forces:
            # 设计值（ULS）：标准值 × γ_G = 1.4
            design_N = N * GAMMA_G
            design_M = M * GAMMA_G
            design_V = V * GAMMA_G

            # 准永久值（SLS）：标准值 × 1.0（无活载，永久荷载系数=1.0）
            quasi_N = N * PSI_Q
            quasi_M = M * PSI_Q
            quasi_V = V * PSI_Q

            # 结构重要性系数
            gamma_d = 1.0

            writer.writerow([
                angle,
                f'{design_N:.2f}',
                f'{design_M:.2f}',
                f'{design_V:.2f}',
                f'{quasi_N:.2f}',
                f'{quasi_M:.2f}',
                f'{quasi_V:.2f}',
                gamma_d
            ])

    print(f'[OK] 转换完成：{len(internal_forces)}个角度点')
    print(f'输出文件：{output_path}')
    print(f'数据范围：')
    print(f'  角度：{internal_forces[0][0]} ~ {internal_forces[-1][0]} deg')
    print(f'  轴力：{min(f[2] for f in internal_forces):.1f} ~ {max(f[2] for f in internal_forces):.1f} kN')
    print(f'  弯矩：{min(f[1] for f in internal_forces):.1f} ~ {max(f[1] for f in internal_forces):.1f} kN.m')
    print(f'  剪力：{min(f[3] for f in internal_forces):.1f} ~ {max(f[3] for f in internal_forces):.1f} kN')

if __name__ == '__main__':
    convert_to_force_records()
