# 装配式明洞配筋优化报告

- 生成时间: 2026-03-15 16:23:05
- 配置文件: D:\suidaopeijin\precast_config.json
- 内力文件: D:\suidaopeijin\force_records.csv
- 模式: all

## 代表块选择

| 类型 | 代表块 |
| --- | --- |
| A | A3 |
| B | B2 |
| C | C2 |

## 类型汇总

| 类型 | 方案 | 根数 | 主筋间距(mm) | 箍筋 | 分布筋 | 造价(CNY/m) | 最大裂缝(mm) | 施工间距(mm) | 联合候选数 | 箍筋候选数 | 联合评分 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | HRB400 D22 | 6 | 175.6 | HPB300 D12@160.0 (2 legs layout) | HRB400 D14@147.7 (7 bars ratio) | 0.00 | 0.000 | -1.0 | 3 | 6 | 0.0500 |
| B | HRB400 D22 | 6 | 175.6 | HPB300 D12@160.0 (2 legs layout) | HRB400 D14@147.7 (7 bars ratio) | 0.00 | 0.000 | -1.0 | 3 | 6 | 0.0500 |
| C | HRB400 D22 | 6 | 175.6 | HPB300 D12@160.0 (2 legs layout) | HRB400 D14@147.7 (7 bars ratio) | 0.00 | 0.000 | -1.0 | 3 | 6 | 0.0500 |

## 分块结果

| 分块 | 类型 | 采用代表块 | 方案 | 根数 | 主筋间距(mm) | 箍筋 | 分布筋 | 造价(CNY/m) | 最大裂缝(mm) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | A | A3 | HRB400 D22 | 6 | 175.6 | HPB300 D12@160.0 (2 legs layout) | HRB400 D14@147.7 (7 bars ratio) | 0.00 | 0.000 |
| A2 | A | A3 | HRB400 D22 | 6 | 175.6 | HPB300 D12@160.0 (2 legs layout) | HRB400 D14@147.7 (7 bars ratio) | 0.00 | 0.000 |
| A3 | A | A3 | HRB400 D22 | 6 | 175.6 | HPB300 D12@160.0 (2 legs layout) | HRB400 D14@147.7 (7 bars ratio) | 0.00 | 0.000 |
| B1 | B | B2 | HRB400 D22 | 6 | 175.6 | HPB300 D12@160.0 (2 legs layout) | HRB400 D14@147.7 (7 bars ratio) | 0.00 | 0.000 |
| B2 | B | B2 | HRB400 D22 | 6 | 175.6 | HPB300 D12@160.0 (2 legs layout) | HRB400 D14@147.7 (7 bars ratio) | 0.00 | 0.000 |
| C1 | C | C2 | HRB400 D22 | 6 | 175.6 | HPB300 D12@160.0 (2 legs layout) | HRB400 D14@147.7 (7 bars ratio) | 0.00 | 0.000 |
| C2 | C | C2 | HRB400 D22 | 6 | 175.6 | HPB300 D12@160.0 (2 legs layout) | HRB400 D14@147.7 (7 bars ratio) | 0.00 | 0.000 |

## 技术复核明细

### 类型 A
- 联合Pareto候选数: 3
- 箍筋Pareto候选数: 6
- 联合选型理由: joint_score_min=0.0500; metric_rank(cost/crack/asv/dist/spacing)=1/1/1/1/3; delta_vs_runner_up(selected-#2): cost=-0.69, crack=0.000, Asv/s=0.00000, dist_ratio=-0.2134, spacing=-44.4
- 箍筋选型理由: min_delta_to_required=0.01372; status=ok; max_ratio=0.140; max_limit_ratio=0.044
- 箍筋所需 Asv/s: 1.40000
- 联合相对次优差值(入选-次优): cost=-0.69, crack=0.000, Asv/s=0.00000, dist_ratio=-0.2134, spacing=-44.4

#### 联合候选对比

| 排名 | 入选 | 主筋 | 箍筋 | 分布筋 | 造价(CNY/m) | 最大裂缝(mm) | Asv/s | 分布筋比 | 主筋间距(mm) | 联合评分 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Y | HRB400 D22 x6 @ 175.6 | HPB300 D12@160.0 (2 legs layout) | HRB400 D14@147.7 (7 bars ratio) | 0.00 | 0.000 | 1.41372 | 0.4724 | 175.6 | 0.0500 |
| 2 |  | HRB400 D20 x5 @ 220.0 | HPB300 D12@160.0 (2 legs layout) | HRB400 D14@147.7 (7 bars ratio) | 0.69 | 0.000 | 1.41372 | 0.6857 | 220.0 | 0.5415 |
| 3 |  | HRB400 D18 x6 @ 176.4 | HPB300 D12@160.0 (2 legs layout) | HRB400 D14@147.7 (7 bars ratio) | 0.67 | 0.000 | 1.41372 | 0.7055 | 176.4 | 0.5863 |

#### 箍筋候选对比

| 排名 | 入选 | 箍筋 | 提供Asv/s | 与需求差值 | max_ratio | max_limit_ratio |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Y | HPB300 D12@160.0 (2 legs layout) | 1.41372 | 0.01372 | 0.140 | 0.044 |
| 2 |  | HPB300 D10@220.0 (4 legs layout) | 1.42800 | 0.02800 | 0.139 | 0.044 |
| 3 |  | HPB300 D8@140.0 (4 legs layout) | 1.43616 | 0.03616 | 0.139 | 0.044 |
| 4 |  | HPB300 D18@350.0 (2 legs layout) | 1.45411 | 0.05411 | 0.139 | 0.044 |
| 5 |  | HPB300 D12@300.0 (4 legs layout) | 1.50796 | 0.10796 | 0.138 | 0.044 |
| 6 |  | HPB300 D14@400.0 (4 legs layout) | 1.53938 | 0.13938 | 0.137 | 0.044 |

### 类型 B
- 联合Pareto候选数: 3
- 箍筋Pareto候选数: 6
- 联合选型理由: joint_score_min=0.0500; metric_rank(cost/crack/asv/dist/spacing)=1/1/1/1/3; delta_vs_runner_up(selected-#2): cost=-0.59, crack=0.000, Asv/s=0.00000, dist_ratio=-0.2134, spacing=-44.4
- 箍筋选型理由: min_delta_to_required=0.01372; status=ok; max_ratio=0.200; max_limit_ratio=0.065
- 箍筋所需 Asv/s: 1.40000
- 联合相对次优差值(入选-次优): cost=-0.59, crack=0.000, Asv/s=0.00000, dist_ratio=-0.2134, spacing=-44.4

#### 联合候选对比

| 排名 | 入选 | 主筋 | 箍筋 | 分布筋 | 造价(CNY/m) | 最大裂缝(mm) | Asv/s | 分布筋比 | 主筋间距(mm) | 联合评分 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Y | HRB400 D22 x6 @ 175.6 | HPB300 D12@160.0 (2 legs layout) | HRB400 D14@147.7 (7 bars ratio) | 0.00 | 0.000 | 1.41372 | 0.4724 | 175.6 | 0.0500 |
| 2 |  | HRB400 D20 x5 @ 220.0 | HPB300 D12@160.0 (2 legs layout) | HRB400 D14@147.7 (7 bars ratio) | 0.59 | 0.000 | 1.41372 | 0.6857 | 220.0 | 0.5415 |
| 3 |  | HRB400 D18 x6 @ 176.4 | HPB300 D12@160.0 (2 legs layout) | HRB400 D14@147.7 (7 bars ratio) | 0.58 | 0.000 | 1.41372 | 0.7055 | 176.4 | 0.5863 |

#### 箍筋候选对比

| 排名 | 入选 | 箍筋 | 提供Asv/s | 与需求差值 | max_ratio | max_limit_ratio |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Y | HPB300 D12@160.0 (2 legs layout) | 1.41372 | 0.01372 | 0.200 | 0.065 |
| 2 |  | HPB300 D10@220.0 (4 legs layout) | 1.42800 | 0.02800 | 0.200 | 0.065 |
| 3 |  | HPB300 D8@140.0 (4 legs layout) | 1.43616 | 0.03616 | 0.199 | 0.065 |
| 4 |  | HPB300 D18@350.0 (2 legs layout) | 1.45411 | 0.05411 | 0.199 | 0.065 |
| 5 |  | HPB300 D12@300.0 (4 legs layout) | 1.50796 | 0.10796 | 0.197 | 0.065 |
| 6 |  | HPB300 D14@400.0 (4 legs layout) | 1.53938 | 0.13938 | 0.197 | 0.065 |

### 类型 C
- 联合Pareto候选数: 3
- 箍筋Pareto候选数: 6
- 联合选型理由: joint_score_min=0.0500; metric_rank(cost/crack/asv/dist/spacing)=1/1/1/1/3; delta_vs_runner_up(selected-#2): cost=-0.69, crack=0.000, Asv/s=0.00000, dist_ratio=-0.2134, spacing=-44.4
- 箍筋选型理由: min_delta_to_required=0.01372; status=ok; max_ratio=0.040; max_limit_ratio=0.010
- 箍筋所需 Asv/s: 1.40000
- 联合相对次优差值(入选-次优): cost=-0.69, crack=0.000, Asv/s=0.00000, dist_ratio=-0.2134, spacing=-44.4

#### 联合候选对比

| 排名 | 入选 | 主筋 | 箍筋 | 分布筋 | 造价(CNY/m) | 最大裂缝(mm) | Asv/s | 分布筋比 | 主筋间距(mm) | 联合评分 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Y | HRB400 D22 x6 @ 175.6 | HPB300 D12@160.0 (2 legs layout) | HRB400 D14@147.7 (7 bars ratio) | 0.00 | 0.000 | 1.41372 | 0.4724 | 175.6 | 0.0500 |
| 2 |  | HRB400 D20 x5 @ 220.0 | HPB300 D12@160.0 (2 legs layout) | HRB400 D14@147.7 (7 bars ratio) | 0.69 | 0.000 | 1.41372 | 0.6857 | 220.0 | 0.5415 |
| 3 |  | HRB400 D18 x6 @ 176.4 | HPB300 D12@160.0 (2 legs layout) | HRB400 D14@147.7 (7 bars ratio) | 0.67 | 0.000 | 1.41372 | 0.7055 | 176.4 | 0.5863 |

#### 箍筋候选对比

| 排名 | 入选 | 箍筋 | 提供Asv/s | 与需求差值 | max_ratio | max_limit_ratio |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Y | HPB300 D12@160.0 (2 legs layout) | 1.41372 | 0.01372 | 0.040 | 0.010 |
| 2 |  | HPB300 D10@220.0 (4 legs layout) | 1.42800 | 0.02800 | 0.039 | 0.010 |
| 3 |  | HPB300 D8@140.0 (4 legs layout) | 1.43616 | 0.03616 | 0.039 | 0.010 |
| 4 |  | HPB300 D18@350.0 (2 legs layout) | 1.45411 | 0.05411 | 0.039 | 0.010 |
| 5 |  | HPB300 D12@300.0 (4 legs layout) | 1.50796 | 0.10796 | 0.039 | 0.010 |
| 6 |  | HPB300 D14@400.0 (4 legs layout) | 1.53938 | 0.13938 | 0.039 | 0.010 |


## 规范参数治理

- 治理模式: defaults+locked+approval
- 配置文件哈希(SHA256): 11adaef93f3666318ccc12960c21a66450734674b16b22de692e5764cd3eb9aa
- 生效条文口径指纹(SHA256): e98a0246dfa6a1e6e8f622c5e9fd72426e302519133cbd73a1e166c8d2e1c79c
- 生效截面参数指纹(SHA256): e9ff13ff8b8059d1b9756de6db1d30432c0ebb6814c37f31e0a950cc968ad8dd
- 锁定参数数量: 6
- 已审批变更数量: 0
- 被拦截变更数量: 0
- 被拦截参数: none

| 参数 | 代码参数 | 锁定 | 默认值 | 输入值 | 生效值 | 来源 | 审批 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| b |  |  |  | 1000 | 1000 | config_input |  |
| concrete_grade |  |  |  | C50 | C50 | config_input |  |
| cover |  |  |  | 50 | 50 | config_input |  |
| gamma_d_shear | Y | Y | 1.0 |  | 1.0 | project_default |  |
| h |  |  |  | 700 | 700 | config_input |  |
| h_w_source | Y | Y | h0 |  | h0 | project_default |  |
| lambda_max | Y | Y | 3.0 |  | 3.0 | project_default |  |
| lambda_min | Y | Y | 1.5 |  | 1.5 | project_default |  |
| min_safety_factor_uls |  |  |  | 1.1 | 1.1 | config_input |  |
| rho_sv_min_hpb300 | Y |  | 0.0014 |  | 0.0014 | project_default |  |
| rho_sv_min_hrb400 | Y |  | 0.0011 |  | 0.0011 | project_default |  |
| shear_n_mode | Y | Y | compression_only |  | compression_only | project_default |  |
| shear_use_abs_vm | Y | Y | True |  | True | project_default |  |


## 输入摘要

### 截面参数

| 参数 | 值 |
| --- | --- |
| b | 1000 |
| concrete_grade | C50 |
| cover | 50 |
| gamma_d_shear | 1.0 |
| h | 700 |
| h_w_source | h0 |
| lambda_max | 3.0 |
| lambda_min | 1.5 |
| min_safety_factor_uls | 1.1 |
| rho_sv_min_hpb300 | 0.0014 |
| rho_sv_min_hrb400 | 0.0011 |
| shear_n_mode | compression_only |
| shear_use_abs_vm | True |

### 几何参数

| 参数 | 值 |
| --- | --- |
| clearance_width | 13.3 |
| clearance_height | 10.88 |
