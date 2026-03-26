# 装配式明洞配筋优化报告

- 生成时间: 2026-03-07 18:31:27
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
| A | 无解 | - | - | - | - | - | - | - | - | - | - |
| B | 无解 | - | - | - | - | - | - | - | - | - | - |
| C | 无解 | - | - | - | - | - | - | - | - | - | - |

## 分块结果

| 分块 | 类型 | 采用代表块 | 方案 | 根数 | 主筋间距(mm) | 箍筋 | 分布筋 | 造价(CNY/m) | 最大裂缝(mm) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | A | A3 | 无解 | - | - | - | - | - | - |
| A2 | A | A3 | 无解 | - | - | - | - | - | - |
| A3 | A | A3 | 无解 | - | - | - | - | - | - |
| B1 | B | B2 | 无解 | - | - | - | - | - | - |
| B2 | B | B2 | 无解 | - | - | - | - | - | - |
| C1 | C | C2 | 无解 | - | - | - | - | - | - |
| C2 | C | C2 | 无解 | - | - | - | - | - | - |

## 技术复核明细

### 类型 A
- 无可行解。

### 类型 B
- 无可行解。

### 类型 C
- 无可行解。


## 规范参数治理

- 治理模式: defaults+locked+approval
- 配置文件哈希(SHA256): 23cc031a80d695306ae5fef0631646d76743fe686337bc11085cae56989d23ab
- 生效条文口径指纹(SHA256): e98a0246dfa6a1e6e8f622c5e9fd72426e302519133cbd73a1e166c8d2e1c79c
- 生效截面参数指纹(SHA256): 7bc6269f0414418481874a2e1f025c252e84e196e0fe3cd3c6ce84e33bb51006
- 锁定参数数量: 6
- 已审批变更数量: 0
- 被拦截变更数量: 0
- 被拦截参数: none

| 参数 | 代码参数 | 锁定 | 默认值 | 输入值 | 生效值 | 来源 | 审批 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| b |  |  |  | 1000 | 1000 | config_input |  |
| concrete_grade |  |  |  | C50 | C50 | config_input |  |
| cover |  |  |  | 55 | 55 | config_input |  |
| gamma_d_shear | Y | Y | 1.0 |  | 1.0 | project_default |  |
| h |  |  |  | 500 | 500 | config_input |  |
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
| cover | 55 |
| gamma_d_shear | 1.0 |
| h | 500 |
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
