# 装配式明洞配筋优化报告（多偏好方案）

- 生成时间: 2026-03-21 12:25:27
- 配置文件: D:\suidaopeijin\precast_config.json
- 内力文件: D:\suidaopeijin\force_records.csv
- 模式: all

## 代表块选择

| 类型 | 代表块 |
| --- | --- |
| A | A3 |
| B | B2 |
| C | C2 |

## 多偏好方案总览

| 偏好 | 权重(成本/裂缝/抗剪/分布筋/间距) | A型方案 | A型造价 | A型裂缝 | B型方案 | B型造价 | B型裂缝 | C型方案 | C型造价 | C型裂缝 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 造价优先 | 0.55/0.15/0.10/0.10/0.10 | HRB400 D20 x5 | 40.76 | 0.070 | HRB400 D16 x7 | 37.60 | 0.000 | HRB400 D16 x7 | 37.60 | 0.000 |
| 安全优先 | 0.15/0.55/0.10/0.10/0.10 | HRB400 D22 x9 | 88.51 | 0.034 | HRB400 D20 x5 | 40.76 | 0.000 | HRB400 D20 x5 | 40.76 | 0.000 |
| 施工优先 | 0.15/0.10/0.10/0.10/0.55 | HRB400 D25 x5 | 63.52 | 0.053 | HRB400 D20 x5 | 40.76 | 0.000 | HRB400 D20 x5 | 40.76 | 0.000 |
| 均衡方案 | 0.45/0.25/0.15/0.10/0.05 | HRB400 D14 x10 | 41.99 | 0.056 | HRB400 D16 x7 | 37.60 | 0.000 | HRB400 D16 x7 | 37.60 | 0.000 |

## 造价优先 (COST)

- 权重(成本/裂缝/抗剪/分布筋/间距): 0.55/0.15/0.10/0.10/0.10

### 类型汇总

| 类型 | 方案 | 根数 | 主筋间距(mm) | 拉筋 | 分布筋 | 造价(CNY/m) | 最大裂缝(mm) | 施工间距(mm) | 联合候选数 | 拉筋候选数 | 联合评分 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | HRB400 D20 | 5 | 220.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 40.76 | 0.070 | 220.0 | 24 | 5 | 0.2662 |
| B | HRB400 D16 | 7 | 147.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 37.60 | 0.000 | 147.0 | 3 | 5 | 0.2000 |
| C | HRB400 D16 | 7 | 147.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 37.60 | 0.000 | 147.0 | 3 | 5 | 0.2000 |

### 分块结果

| 分块 | 类型 | 采用代表块 | 方案 | 根数 | 主筋间距(mm) | 拉筋 | 分布筋 | 造价(CNY/m) | 最大裂缝(mm) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | A | A3 | HRB400 D20 | 5 | 220.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 40.76 | 0.070 |
| A2 | A | A3 | HRB400 D20 | 5 | 220.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 40.76 | 0.070 |
| A3 | A | A3 | HRB400 D20 | 5 | 220.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 40.76 | 0.070 |
| B1 | B | B2 | HRB400 D16 | 7 | 147.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 37.60 | 0.000 |
| B2 | B | B2 | HRB400 D16 | 7 | 147.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 37.60 | 0.000 |
| C1 | C | C2 | HRB400 D16 | 7 | 147.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 37.60 | 0.000 |
| C2 | C | C2 | HRB400 D16 | 7 | 147.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 37.60 | 0.000 |

### 技术复核明细

#### 类型 A
- 联合Pareto候选数: 24
- 拉筋Pareto候选数: 5
- 联合选型理由: joint_score_min=0.2662; metric_rank(cost/crack/asv/dist/spacing)=3/24/1/21/1; delta_vs_runner_up(selected-#2): cost=1.16, crack=0.003, Asv/s=0.00000, dist_ratio=-0.0221, spacing=44.0
- 拉筋选型理由: min_delta_to_required=0.02800; status=ok; max_ratio=0.178; max_limit_ratio=0.062
- 拉筋所需 Asv/s: 1.40000
- 联合相对次优差值(入选-次优): cost=1.16, crack=0.003, Asv/s=0.00000, dist_ratio=-0.0221, spacing=44.0

##### 联合候选对比

| 排名 | 入选 | 主筋 | 拉筋 | 分布筋 | 造价(CNY/m) | 最大裂缝(mm) | Asv/s | 分布筋比 | 主筋间距(mm) | 联合评分 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Y | HRB400 D20 x5 @ 220.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 40.76 | 0.070 | 1.42800 | 0.7680 | 220.0 | 0.2662 |
| 2 |  | HRB400 D18 x6 @ 176.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 39.60 | 0.067 | 1.42800 | 0.7902 | 176.0 | 0.2803 |
| 3 |  | HRB400 D16 x7 @ 147.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 37.60 | 0.067 | 1.42800 | 0.8571 | 147.0 | 0.2955 |
| 4 |  | HRB400 D22 x5 @ 219.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 49.17 | 0.062 | 1.42800 | 0.6349 | 219.0 | 0.2973 |
| 5 |  | HRB400 D18 x7 @ 147.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 46.20 | 0.057 | 1.42800 | 0.6773 | 147.0 | 0.3120 |
| 6 |  | HRB400 D16 x8 @ 126.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 42.98 | 0.058 | 1.42800 | 0.7500 | 126.0 | 0.3137 |
| 7 |  | HRB400 D20 x6 @ 176.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 48.91 | 0.058 | 1.42800 | 0.6400 | 176.0 | 0.3147 |
| 8 |  | HRB400 D14 x10 @ 98.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 41.99 | 0.056 | 1.42800 | 0.7840 | 98.0 | 0.3217 |
| 9 |  | HRB400 D16 x9 @ 110.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 48.35 | 0.052 | 1.42800 | 0.6667 | 110.0 | 0.3404 |
| 10 |  | HRB400 D18 x8 @ 126.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 52.80 | 0.050 | 1.42800 | 0.5926 | 126.0 | 0.3528 |
| 11 |  | HRB400 D16 x10 @ 98.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 53.72 | 0.047 | 1.42800 | 0.6000 | 98.0 | 0.3726 |
| 12 |  | HRB400 D20 x7 @ 146.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 57.06 | 0.050 | 1.42800 | 0.5486 | 146.0 | 0.3731 |
| 13 |  | HRB400 D22 x6 @ 175.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 59.00 | 0.052 | 1.42800 | 0.5291 | 175.0 | 0.3739 |
| 14 |  | HRB400 D25 x5 @ 218.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 63.52 | 0.053 | 1.42800 | 0.4916 | 218.0 | 0.3851 |
| 15 |  | HRB400 D18 x9 @ 110.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 59.40 | 0.044 | 1.42800 | 0.5268 | 110.0 | 0.4000 |
| 16 |  | HRB400 D20 x8 @ 125.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 65.21 | 0.044 | 1.42800 | 0.4800 | 125.0 | 0.4376 |
| 17 |  | HRB400 D18 x10 @ 98.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 66.00 | 0.040 | 1.42800 | 0.4741 | 98.0 | 0.4513 |
| 18 |  | HRB400 D22 x7 @ 146.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 68.84 | 0.044 | 1.42800 | 0.4535 | 146.0 | 0.4567 |
| 19 |  | HRB400 D25 x6 @ 175.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 76.23 | 0.044 | 1.42800 | 0.4097 | 175.0 | 0.5027 |
| 20 |  | HRB400 D20 x9 @ 110.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 73.36 | 0.039 | 1.42800 | 0.4267 | 110.0 | 0.5061 |
| 21 |  | HRB400 D22 x8 @ 125.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 78.67 | 0.039 | 1.42800 | 0.3968 | 125.0 | 0.5445 |
| 22 |  | HRB400 D20 x10 @ 97.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 81.51 | 0.035 | 1.42800 | 0.3840 | 97.0 | 0.5791 |
| 23 |  | HRB400 D25 x7 @ 145.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 88.93 | 0.038 | 1.42800 | 0.3511 | 145.0 | 0.6250 |
| 24 |  | HRB400 D22 x9 @ 109.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 88.51 | 0.034 | 1.42800 | 0.3527 | 109.0 | 0.6360 |

##### 拉筋候选对比

| 排名 | 入选 | 拉筋 | 提供Asv/s | 与需求差值 | max_ratio | max_limit_ratio |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Y | HRB400 D10@220.0 (4 legs layout) | 1.42800 | 0.02800 | 0.178 | 0.062 |
| 2 |  | HRB400 D8@140.0 (4 legs layout) | 1.43616 | 0.03616 | 0.178 | 0.062 |
| 3 |  | HRB400 D18@350.0 (2 legs layout) | 1.45411 | 0.05411 | 0.177 | 0.062 |
| 4 |  | HPB300 D12@300.0 (4 legs layout) | 1.50796 | 0.10796 | 0.188 | 0.062 |
| 5 |  | HPB300 D14@400.0 (4 legs layout) | 1.53938 | 0.13938 | 0.187 | 0.062 |

#### 类型 B
- 联合Pareto候选数: 3
- 拉筋Pareto候选数: 5
- 联合选型理由: joint_score_min=0.2000; metric_rank(cost/crack/asv/dist/spacing)=1/1/1/3/3; delta_vs_runner_up(selected-#2): cost=-2.00, crack=0.000, Asv/s=0.00000, dist_ratio=0.0670, spacing=-29.0
- 拉筋选型理由: min_delta_to_required=0.02800; status=ok; max_ratio=0.252; max_limit_ratio=0.091
- 拉筋所需 Asv/s: 1.40000
- 联合相对次优差值(入选-次优): cost=-2.00, crack=0.000, Asv/s=0.00000, dist_ratio=0.0670, spacing=-29.0

##### 联合候选对比

| 排名 | 入选 | 主筋 | 拉筋 | 分布筋 | 造价(CNY/m) | 最大裂缝(mm) | Asv/s | 分布筋比 | 主筋间距(mm) | 联合评分 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Y | HRB400 D16 x7 @ 147.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 37.60 | 0.000 | 1.42800 | 0.8571 | 147.0 | 0.2000 |
| 2 |  | HRB400 D18 x6 @ 176.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 39.60 | 0.000 | 1.42800 | 0.7902 | 176.0 | 0.4335 |
| 3 |  | HRB400 D20 x5 @ 220.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 40.76 | 0.000 | 1.42800 | 0.7680 | 220.0 | 0.5500 |

##### 拉筋候选对比

| 排名 | 入选 | 拉筋 | 提供Asv/s | 与需求差值 | max_ratio | max_limit_ratio |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Y | HRB400 D10@220.0 (4 legs layout) | 1.42800 | 0.02800 | 0.252 | 0.091 |
| 2 |  | HRB400 D8@140.0 (4 legs layout) | 1.43616 | 0.03616 | 0.251 | 0.091 |
| 3 |  | HRB400 D18@350.0 (2 legs layout) | 1.45411 | 0.05411 | 0.251 | 0.091 |
| 4 |  | HPB300 D12@300.0 (4 legs layout) | 1.50796 | 0.10796 | 0.265 | 0.091 |
| 5 |  | HPB300 D14@400.0 (4 legs layout) | 1.53938 | 0.13938 | 0.264 | 0.091 |

#### 类型 C
- 联合Pareto候选数: 3
- 拉筋Pareto候选数: 5
- 联合选型理由: joint_score_min=0.2000; metric_rank(cost/crack/asv/dist/spacing)=1/1/1/3/3; delta_vs_runner_up(selected-#2): cost=-2.00, crack=0.000, Asv/s=0.00000, dist_ratio=0.0670, spacing=-29.0
- 拉筋选型理由: min_delta_to_required=0.02800; status=ok; max_ratio=0.048; max_limit_ratio=0.013
- 拉筋所需 Asv/s: 1.40000
- 联合相对次优差值(入选-次优): cost=-2.00, crack=0.000, Asv/s=0.00000, dist_ratio=0.0670, spacing=-29.0

##### 联合候选对比

| 排名 | 入选 | 主筋 | 拉筋 | 分布筋 | 造价(CNY/m) | 最大裂缝(mm) | Asv/s | 分布筋比 | 主筋间距(mm) | 联合评分 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Y | HRB400 D16 x7 @ 147.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 37.60 | 0.000 | 1.42800 | 0.8571 | 147.0 | 0.2000 |
| 2 |  | HRB400 D18 x6 @ 176.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 39.60 | 0.000 | 1.42800 | 0.7902 | 176.0 | 0.4335 |
| 3 |  | HRB400 D20 x5 @ 220.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 40.76 | 0.000 | 1.42800 | 0.7680 | 220.0 | 0.5500 |

##### 拉筋候选对比

| 排名 | 入选 | 拉筋 | 提供Asv/s | 与需求差值 | max_ratio | max_limit_ratio |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Y | HRB400 D10@220.0 (4 legs layout) | 1.42800 | 0.02800 | 0.048 | 0.013 |
| 2 |  | HRB400 D8@140.0 (4 legs layout) | 1.43616 | 0.03616 | 0.048 | 0.013 |
| 3 |  | HRB400 D18@350.0 (2 legs layout) | 1.45411 | 0.05411 | 0.048 | 0.013 |
| 4 |  | HPB300 D12@300.0 (4 legs layout) | 1.50796 | 0.10796 | 0.051 | 0.013 |
| 5 |  | HPB300 D14@400.0 (4 legs layout) | 1.53938 | 0.13938 | 0.051 | 0.013 |

## 安全优先 (SAFETY)

- 权重(成本/裂缝/抗剪/分布筋/间距): 0.15/0.55/0.10/0.10/0.10

### 类型汇总

| 类型 | 方案 | 根数 | 主筋间距(mm) | 拉筋 | 分布筋 | 造价(CNY/m) | 最大裂缝(mm) | 施工间距(mm) | 联合候选数 | 拉筋候选数 | 联合评分 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | HRB400 D22 | 9 | 109.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 88.51 | 0.034 | 109.0 | 24 | 5 | 0.2393 |
| B | HRB400 D20 | 5 | 220.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 40.76 | 0.000 | 220.0 | 3 | 5 | 0.1500 |
| C | HRB400 D20 | 5 | 220.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 40.76 | 0.000 | 220.0 | 3 | 5 | 0.1500 |

### 分块结果

| 分块 | 类型 | 采用代表块 | 方案 | 根数 | 主筋间距(mm) | 拉筋 | 分布筋 | 造价(CNY/m) | 最大裂缝(mm) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | A | A3 | HRB400 D22 | 9 | 109.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 88.51 | 0.034 |
| A2 | A | A3 | HRB400 D22 | 9 | 109.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 88.51 | 0.034 |
| A3 | A | A3 | HRB400 D22 | 9 | 109.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 88.51 | 0.034 |
| B1 | B | B2 | HRB400 D20 | 5 | 220.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 40.76 | 0.000 |
| B2 | B | B2 | HRB400 D20 | 5 | 220.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 40.76 | 0.000 |
| C1 | C | C2 | HRB400 D20 | 5 | 220.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 40.76 | 0.000 |
| C2 | C | C2 | HRB400 D20 | 5 | 220.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 40.76 | 0.000 |

### 技术复核明细

#### 类型 A
- 联合Pareto候选数: 24
- 拉筋Pareto候选数: 5
- 联合选型理由: joint_score_min=0.2393; metric_rank(cost/crack/asv/dist/spacing)=23/1/1/2/20; delta_vs_runner_up(selected-#2): cost=7.00, crack=-0.001, Asv/s=0.00000, dist_ratio=-0.0313, spacing=12.0
- 拉筋选型理由: min_delta_to_required=0.02800; status=ok; max_ratio=0.178; max_limit_ratio=0.062
- 拉筋所需 Asv/s: 1.40000
- 联合相对次优差值(入选-次优): cost=7.00, crack=-0.001, Asv/s=0.00000, dist_ratio=-0.0313, spacing=12.0

##### 联合候选对比

| 排名 | 入选 | 主筋 | 拉筋 | 分布筋 | 造价(CNY/m) | 最大裂缝(mm) | Asv/s | 分布筋比 | 主筋间距(mm) | 联合评分 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Y | HRB400 D22 x9 @ 109.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 88.51 | 0.034 | 1.42800 | 0.3527 | 109.0 | 0.2393 |
| 2 |  | HRB400 D20 x10 @ 97.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 81.51 | 0.035 | 1.42800 | 0.3840 | 97.0 | 0.2428 |
| 3 |  | HRB400 D25 x7 @ 145.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 88.93 | 0.038 | 1.42800 | 0.3511 | 145.0 | 0.2626 |
| 4 |  | HRB400 D22 x8 @ 125.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 78.67 | 0.039 | 1.42800 | 0.3968 | 125.0 | 0.2730 |
| 5 |  | HRB400 D20 x9 @ 110.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 73.36 | 0.039 | 1.42800 | 0.4267 | 110.0 | 0.2770 |
| 6 |  | HRB400 D18 x10 @ 98.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 66.00 | 0.040 | 1.42800 | 0.4741 | 98.0 | 0.2928 |
| 7 |  | HRB400 D25 x6 @ 175.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 76.23 | 0.044 | 1.42800 | 0.4097 | 175.0 | 0.3102 |
| 8 |  | HRB400 D22 x7 @ 146.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 68.84 | 0.044 | 1.42800 | 0.4535 | 146.0 | 0.3243 |
| 9 |  | HRB400 D20 x8 @ 125.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 65.21 | 0.044 | 1.42800 | 0.4800 | 125.0 | 0.3268 |
| 10 |  | HRB400 D18 x9 @ 110.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 59.40 | 0.044 | 1.42800 | 0.5268 | 110.0 | 0.3431 |
| 11 |  | HRB400 D16 x10 @ 98.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 53.72 | 0.047 | 1.42800 | 0.6000 | 98.0 | 0.3847 |
| 12 |  | HRB400 D25 x5 @ 218.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 63.52 | 0.053 | 1.42800 | 0.4916 | 218.0 | 0.3910 |
| 13 |  | HRB400 D20 x7 @ 146.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 57.06 | 0.050 | 1.42800 | 0.5486 | 146.0 | 0.3963 |
| 14 |  | HRB400 D22 x6 @ 175.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 59.00 | 0.052 | 1.42800 | 0.5291 | 175.0 | 0.4013 |
| 15 |  | HRB400 D18 x8 @ 126.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 52.80 | 0.050 | 1.42800 | 0.5926 | 126.0 | 0.4100 |
| 16 |  | HRB400 D16 x9 @ 110.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 48.35 | 0.052 | 1.42800 | 0.6667 | 110.0 | 0.4527 |
| 17 |  | HRB400 D20 x6 @ 176.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 48.91 | 0.058 | 1.42800 | 0.6400 | 176.0 | 0.4952 |
| 18 |  | HRB400 D18 x7 @ 147.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 46.20 | 0.057 | 1.42800 | 0.6773 | 147.0 | 0.5011 |
| 19 |  | HRB400 D22 x5 @ 219.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 49.17 | 0.062 | 1.42800 | 0.6349 | 219.0 | 0.5180 |
| 20 |  | HRB400 D14 x10 @ 98.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 41.99 | 0.056 | 1.42800 | 0.7840 | 98.0 | 0.5276 |
| 21 |  | HRB400 D16 x8 @ 126.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 42.98 | 0.058 | 1.42800 | 0.7500 | 126.0 | 0.5410 |
| 22 |  | HRB400 D18 x6 @ 176.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 39.60 | 0.067 | 1.42800 | 0.7902 | 176.0 | 0.6283 |
| 23 |  | HRB400 D20 x5 @ 220.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 40.76 | 0.070 | 1.42800 | 0.7680 | 220.0 | 0.6416 |
| 24 |  | HRB400 D16 x7 @ 147.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 37.60 | 0.067 | 1.42800 | 0.8571 | 147.0 | 0.6585 |

#### 类型 B
- 联合Pareto候选数: 3
- 拉筋Pareto候选数: 5
- 联合选型理由: joint_score_min=0.1500; metric_rank(cost/crack/asv/dist/spacing)=3/1/1/1/1; delta_vs_runner_up(selected-#2): cost=1.16, crack=0.000, Asv/s=0.00000, dist_ratio=-0.0221, spacing=44.0
- 拉筋选型理由: min_delta_to_required=0.02800; status=ok; max_ratio=0.252; max_limit_ratio=0.091
- 拉筋所需 Asv/s: 1.40000
- 联合相对次优差值(入选-次优): cost=1.16, crack=0.000, Asv/s=0.00000, dist_ratio=-0.0221, spacing=44.0

##### 联合候选对比

| 排名 | 入选 | 主筋 | 拉筋 | 分布筋 | 造价(CNY/m) | 最大裂缝(mm) | Asv/s | 分布筋比 | 主筋间距(mm) | 联合评分 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Y | HRB400 D20 x5 @ 220.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 40.76 | 0.000 | 1.42800 | 0.7680 | 220.0 | 0.1500 |
| 2 |  | HRB400 D18 x6 @ 176.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 39.60 | 0.000 | 1.42800 | 0.7902 | 176.0 | 0.1801 |
| 3 |  | HRB400 D16 x7 @ 147.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 37.60 | 0.000 | 1.42800 | 0.8571 | 147.0 | 0.2000 |

#### 类型 C
- 联合Pareto候选数: 3
- 拉筋Pareto候选数: 5
- 联合选型理由: joint_score_min=0.1500; metric_rank(cost/crack/asv/dist/spacing)=3/1/1/1/1; delta_vs_runner_up(selected-#2): cost=1.16, crack=0.000, Asv/s=0.00000, dist_ratio=-0.0221, spacing=44.0
- 拉筋选型理由: min_delta_to_required=0.02800; status=ok; max_ratio=0.048; max_limit_ratio=0.013
- 拉筋所需 Asv/s: 1.40000
- 联合相对次优差值(入选-次优): cost=1.16, crack=0.000, Asv/s=0.00000, dist_ratio=-0.0221, spacing=44.0

##### 联合候选对比

| 排名 | 入选 | 主筋 | 拉筋 | 分布筋 | 造价(CNY/m) | 最大裂缝(mm) | Asv/s | 分布筋比 | 主筋间距(mm) | 联合评分 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Y | HRB400 D20 x5 @ 220.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 40.76 | 0.000 | 1.42800 | 0.7680 | 220.0 | 0.1500 |
| 2 |  | HRB400 D18 x6 @ 176.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 39.60 | 0.000 | 1.42800 | 0.7902 | 176.0 | 0.1801 |
| 3 |  | HRB400 D16 x7 @ 147.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 37.60 | 0.000 | 1.42800 | 0.8571 | 147.0 | 0.2000 |

## 施工优先 (CONSTRUCTION)

- 权重(成本/裂缝/抗剪/分布筋/间距): 0.15/0.10/0.10/0.10/0.55

### 类型汇总

| 类型 | 方案 | 根数 | 主筋间距(mm) | 拉筋 | 分布筋 | 造价(CNY/m) | 最大裂缝(mm) | 施工间距(mm) | 联合候选数 | 拉筋候选数 | 联合评分 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | HRB400 D25 | 5 | 218.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 63.52 | 0.053 | 218.0 | 24 | 5 | 0.1644 |
| B | HRB400 D20 | 5 | 220.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 40.76 | 0.000 | 220.0 | 3 | 5 | 0.1500 |
| C | HRB400 D20 | 5 | 220.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 40.76 | 0.000 | 220.0 | 3 | 5 | 0.1500 |

### 分块结果

| 分块 | 类型 | 采用代表块 | 方案 | 根数 | 主筋间距(mm) | 拉筋 | 分布筋 | 造价(CNY/m) | 最大裂缝(mm) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | A | A3 | HRB400 D25 | 5 | 218.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 63.52 | 0.053 |
| A2 | A | A3 | HRB400 D25 | 5 | 218.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 63.52 | 0.053 |
| A3 | A | A3 | HRB400 D25 | 5 | 218.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 63.52 | 0.053 |
| B1 | B | B2 | HRB400 D20 | 5 | 220.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 40.76 | 0.000 |
| B2 | B | B2 | HRB400 D20 | 5 | 220.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 40.76 | 0.000 |
| C1 | C | C2 | HRB400 D20 | 5 | 220.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 40.76 | 0.000 |
| C2 | C | C2 | HRB400 D20 | 5 | 220.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 40.76 | 0.000 |

### 技术复核明细

#### 类型 A
- 联合Pareto候选数: 24
- 拉筋Pareto候选数: 5
- 联合选型理由: joint_score_min=0.1644; metric_rank(cost/crack/asv/dist/spacing)=15/16/1/10/3; delta_vs_runner_up(selected-#2): cost=14.35, crack=-0.009, Asv/s=0.00000, dist_ratio=-0.1433, spacing=-1.0
- 拉筋选型理由: min_delta_to_required=0.02800; status=ok; max_ratio=0.179; max_limit_ratio=0.062
- 拉筋所需 Asv/s: 1.40000
- 联合相对次优差值(入选-次优): cost=14.35, crack=-0.009, Asv/s=0.00000, dist_ratio=-0.1433, spacing=-1.0

##### 联合候选对比

| 排名 | 入选 | 主筋 | 拉筋 | 分布筋 | 造价(CNY/m) | 最大裂缝(mm) | Asv/s | 分布筋比 | 主筋间距(mm) | 联合评分 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Y | HRB400 D25 x5 @ 218.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 63.52 | 0.053 | 1.42800 | 0.4916 | 218.0 | 0.1644 |
| 2 |  | HRB400 D22 x5 @ 219.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 49.17 | 0.062 | 1.42800 | 0.6349 | 219.0 | 0.1720 |
| 3 |  | HRB400 D20 x5 @ 220.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 40.76 | 0.070 | 1.42800 | 0.7680 | 220.0 | 0.1916 |
| 4 |  | HRB400 D22 x6 @ 175.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 59.00 | 0.052 | 1.42800 | 0.5291 | 175.0 | 0.3475 |
| 5 |  | HRB400 D25 x6 @ 175.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 76.23 | 0.044 | 1.42800 | 0.4097 | 175.0 | 0.3528 |
| 6 |  | HRB400 D20 x6 @ 176.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 48.91 | 0.058 | 1.42800 | 0.6400 | 176.0 | 0.3540 |
| 7 |  | HRB400 D18 x6 @ 176.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 39.60 | 0.067 | 1.42800 | 0.7902 | 176.0 | 0.3802 |
| 8 |  | HRB400 D22 x7 @ 146.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 68.84 | 0.044 | 1.42800 | 0.4535 | 146.0 | 0.4701 |
| 9 |  | HRB400 D20 x7 @ 146.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 57.06 | 0.050 | 1.42800 | 0.5486 | 146.0 | 0.4704 |
| 10 |  | HRB400 D18 x7 @ 147.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 46.20 | 0.057 | 1.42800 | 0.6773 | 147.0 | 0.4800 |
| 11 |  | HRB400 D25 x7 @ 145.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 88.93 | 0.038 | 1.42800 | 0.3511 | 145.0 | 0.4947 |
| 12 |  | HRB400 D16 x7 @ 147.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 37.60 | 0.067 | 1.42800 | 0.8571 | 147.0 | 0.5172 |
| 13 |  | HRB400 D18 x8 @ 126.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 52.80 | 0.050 | 1.42800 | 0.5926 | 126.0 | 0.5564 |
| 14 |  | HRB400 D20 x8 @ 125.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 65.21 | 0.044 | 1.42800 | 0.4800 | 125.0 | 0.5570 |
| 15 |  | HRB400 D22 x8 @ 125.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 78.67 | 0.039 | 1.42800 | 0.3968 | 125.0 | 0.5660 |
| 16 |  | HRB400 D16 x8 @ 126.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 42.98 | 0.058 | 1.42800 | 0.7500 | 126.0 | 0.5821 |
| 17 |  | HRB400 D18 x9 @ 110.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 59.40 | 0.044 | 1.42800 | 0.5268 | 110.0 | 0.6185 |
| 18 |  | HRB400 D20 x9 @ 110.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 73.36 | 0.039 | 1.42800 | 0.4267 | 110.0 | 0.6237 |
| 19 |  | HRB400 D16 x9 @ 110.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 48.35 | 0.052 | 1.42800 | 0.6667 | 110.0 | 0.6346 |
| 20 |  | HRB400 D22 x9 @ 109.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 88.51 | 0.034 | 1.42800 | 0.3527 | 109.0 | 0.6454 |
| 21 |  | HRB400 D18 x10 @ 98.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 66.00 | 0.040 | 1.42800 | 0.4741 | 98.0 | 0.6685 |
| 22 |  | HRB400 D16 x10 @ 98.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 53.72 | 0.047 | 1.42800 | 0.6000 | 98.0 | 0.6762 |
| 23 |  | HRB400 D20 x10 @ 97.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 81.51 | 0.035 | 1.42800 | 0.3840 | 97.0 | 0.6862 |
| 24 |  | HRB400 D14 x10 @ 98.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 41.99 | 0.056 | 1.42800 | 0.7840 | 98.0 | 0.7039 |

#### 类型 B
- 联合Pareto候选数: 3
- 拉筋Pareto候选数: 5
- 联合选型理由: joint_score_min=0.1500; metric_rank(cost/crack/asv/dist/spacing)=3/1/1/1/1; delta_vs_runner_up(selected-#2): cost=1.16, crack=0.000, Asv/s=0.00000, dist_ratio=-0.0221, spacing=44.0
- 拉筋选型理由: min_delta_to_required=0.02800; status=ok; max_ratio=0.252; max_limit_ratio=0.091
- 拉筋所需 Asv/s: 1.40000
- 联合相对次优差值(入选-次优): cost=1.16, crack=0.000, Asv/s=0.00000, dist_ratio=-0.0221, spacing=44.0

##### 联合候选对比

| 排名 | 入选 | 主筋 | 拉筋 | 分布筋 | 造价(CNY/m) | 最大裂缝(mm) | Asv/s | 分布筋比 | 主筋间距(mm) | 联合评分 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Y | HRB400 D20 x5 @ 220.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 40.76 | 0.000 | 1.42800 | 0.7680 | 220.0 | 0.1500 |
| 2 |  | HRB400 D18 x6 @ 176.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 39.60 | 0.000 | 1.42800 | 0.7902 | 176.0 | 0.4514 |
| 3 |  | HRB400 D16 x7 @ 147.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 37.60 | 0.000 | 1.42800 | 0.8571 | 147.0 | 0.6500 |

#### 类型 C
- 联合Pareto候选数: 3
- 拉筋Pareto候选数: 5
- 联合选型理由: joint_score_min=0.1500; metric_rank(cost/crack/asv/dist/spacing)=3/1/1/1/1; delta_vs_runner_up(selected-#2): cost=1.16, crack=0.000, Asv/s=0.00000, dist_ratio=-0.0221, spacing=44.0
- 拉筋选型理由: min_delta_to_required=0.02800; status=ok; max_ratio=0.048; max_limit_ratio=0.013
- 拉筋所需 Asv/s: 1.40000
- 联合相对次优差值(入选-次优): cost=1.16, crack=0.000, Asv/s=0.00000, dist_ratio=-0.0221, spacing=44.0

##### 联合候选对比

| 排名 | 入选 | 主筋 | 拉筋 | 分布筋 | 造价(CNY/m) | 最大裂缝(mm) | Asv/s | 分布筋比 | 主筋间距(mm) | 联合评分 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Y | HRB400 D20 x5 @ 220.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 40.76 | 0.000 | 1.42800 | 0.7680 | 220.0 | 0.1500 |
| 2 |  | HRB400 D18 x6 @ 176.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 39.60 | 0.000 | 1.42800 | 0.7902 | 176.0 | 0.4514 |
| 3 |  | HRB400 D16 x7 @ 147.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 37.60 | 0.000 | 1.42800 | 0.8571 | 147.0 | 0.6500 |

## 均衡方案 (BALANCED)

- 权重(成本/裂缝/抗剪/分布筋/间距): 0.45/0.25/0.15/0.10/0.05

### 类型汇总

| 类型 | 方案 | 根数 | 主筋间距(mm) | 拉筋 | 分布筋 | 造价(CNY/m) | 最大裂缝(mm) | 施工间距(mm) | 联合候选数 | 拉筋候选数 | 联合评分 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | HRB400 D14 | 10 | 98.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 41.99 | 0.056 | 98.0 | 24 | 5 | 0.3236 |
| B | HRB400 D16 | 7 | 147.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 37.60 | 0.000 | 147.0 | 3 | 5 | 0.1500 |
| C | HRB400 D16 | 7 | 147.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 37.60 | 0.000 | 147.0 | 3 | 5 | 0.1500 |

### 分块结果

| 分块 | 类型 | 采用代表块 | 方案 | 根数 | 主筋间距(mm) | 拉筋 | 分布筋 | 造价(CNY/m) | 最大裂缝(mm) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | A | A3 | HRB400 D14 | 10 | 98.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 41.99 | 0.056 |
| A2 | A | A3 | HRB400 D14 | 10 | 98.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 41.99 | 0.056 |
| A3 | A | A3 | HRB400 D14 | 10 | 98.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 41.99 | 0.056 |
| B1 | B | B2 | HRB400 D16 | 7 | 147.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 37.60 | 0.000 |
| B2 | B | B2 | HRB400 D16 | 7 | 147.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 37.60 | 0.000 |
| C1 | C | C2 | HRB400 D16 | 7 | 147.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 37.60 | 0.000 |
| C2 | C | C2 | HRB400 D16 | 7 | 147.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 37.60 | 0.000 |

### 技术复核明细

#### 类型 A
- 联合Pareto候选数: 24
- 拉筋Pareto候选数: 5
- 联合选型理由: joint_score_min=0.3236; metric_rank(cost/crack/asv/dist/spacing)=4/17/1/22/21; delta_vs_runner_up(selected-#2): cost=-6.36, crack=0.004, Asv/s=0.00000, dist_ratio=0.1173, spacing=-12.0
- 拉筋选型理由: min_delta_to_required=0.02800; status=ok; max_ratio=0.177; max_limit_ratio=0.061
- 拉筋所需 Asv/s: 1.40000
- 联合相对次优差值(入选-次优): cost=-6.36, crack=0.004, Asv/s=0.00000, dist_ratio=0.1173, spacing=-12.0

##### 联合候选对比

| 排名 | 入选 | 主筋 | 拉筋 | 分布筋 | 造价(CNY/m) | 最大裂缝(mm) | Asv/s | 分布筋比 | 主筋间距(mm) | 联合评分 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Y | HRB400 D14 x10 @ 98.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 41.99 | 0.056 | 1.42800 | 0.7840 | 98.0 | 0.3236 |
| 2 |  | HRB400 D16 x9 @ 110.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 48.35 | 0.052 | 1.42800 | 0.6667 | 110.0 | 0.3238 |
| 3 |  | HRB400 D16 x10 @ 98.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 53.72 | 0.047 | 1.42800 | 0.6000 | 98.0 | 0.3261 |
| 4 |  | HRB400 D18 x8 @ 126.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 52.80 | 0.050 | 1.42800 | 0.5926 | 126.0 | 0.3289 |
| 5 |  | HRB400 D18 x7 @ 147.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 46.20 | 0.057 | 1.42800 | 0.6773 | 147.0 | 0.3296 |
| 6 |  | HRB400 D16 x8 @ 126.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 42.98 | 0.058 | 1.42800 | 0.7500 | 126.0 | 0.3323 |
| 7 |  | HRB400 D18 x9 @ 110.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 59.40 | 0.044 | 1.42800 | 0.5268 | 110.0 | 0.3411 |
| 8 |  | HRB400 D20 x6 @ 176.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 48.91 | 0.058 | 1.42800 | 0.6400 | 176.0 | 0.3419 |
| 9 |  | HRB400 D20 x7 @ 146.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 57.06 | 0.050 | 1.42800 | 0.5486 | 146.0 | 0.3489 |
| 10 |  | HRB400 D18 x6 @ 176.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 39.60 | 0.067 | 1.42800 | 0.7902 | 176.0 | 0.3494 |
| 11 |  | HRB400 D22 x5 @ 219.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 49.17 | 0.062 | 1.42800 | 0.6349 | 219.0 | 0.3521 |
| 12 |  | HRB400 D16 x7 @ 147.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 37.60 | 0.067 | 1.42800 | 0.8571 | 147.0 | 0.3566 |
| 13 |  | HRB400 D20 x5 @ 220.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 40.76 | 0.070 | 1.42800 | 0.7680 | 220.0 | 0.3600 |
| 14 |  | HRB400 D18 x10 @ 98.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 66.00 | 0.040 | 1.42800 | 0.4741 | 98.0 | 0.3621 |
| 15 |  | HRB400 D22 x6 @ 175.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 59.00 | 0.052 | 1.42800 | 0.5291 | 175.0 | 0.3624 |
| 16 |  | HRB400 D20 x8 @ 125.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 65.21 | 0.044 | 1.42800 | 0.4800 | 125.0 | 0.3713 |
| 17 |  | HRB400 D25 x5 @ 218.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 63.52 | 0.053 | 1.42800 | 0.4916 | 218.0 | 0.3857 |
| 18 |  | HRB400 D22 x7 @ 146.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 68.84 | 0.044 | 1.42800 | 0.4535 | 146.0 | 0.3935 |
| 19 |  | HRB400 D20 x9 @ 110.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 73.36 | 0.039 | 1.42800 | 0.4267 | 110.0 | 0.4041 |
| 20 |  | HRB400 D25 x6 @ 175.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 76.23 | 0.044 | 1.42800 | 0.4097 | 175.0 | 0.4363 |
| 21 |  | HRB400 D22 x8 @ 125.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 78.67 | 0.039 | 1.42800 | 0.3968 | 125.0 | 0.4380 |
| 22 |  | HRB400 D20 x10 @ 97.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 81.51 | 0.035 | 1.42800 | 0.3840 | 97.0 | 0.4450 |
| 23 |  | HRB400 D22 x9 @ 109.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 88.51 | 0.034 | 1.42800 | 0.3527 | 109.0 | 0.4917 |
| 24 |  | HRB400 D25 x7 @ 145.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 88.93 | 0.038 | 1.42800 | 0.3511 | 145.0 | 0.5039 |

#### 类型 B
- 联合Pareto候选数: 3
- 拉筋Pareto候选数: 5
- 联合选型理由: joint_score_min=0.1500; metric_rank(cost/crack/asv/dist/spacing)=1/1/1/3/3; delta_vs_runner_up(selected-#2): cost=-2.00, crack=0.000, Asv/s=0.00000, dist_ratio=0.0670, spacing=-29.0
- 拉筋选型理由: min_delta_to_required=0.02800; status=ok; max_ratio=0.252; max_limit_ratio=0.091
- 拉筋所需 Asv/s: 1.40000
- 联合相对次优差值(入选-次优): cost=-2.00, crack=0.000, Asv/s=0.00000, dist_ratio=0.0670, spacing=-29.0

##### 联合候选对比

| 排名 | 入选 | 主筋 | 拉筋 | 分布筋 | 造价(CNY/m) | 最大裂缝(mm) | Asv/s | 分布筋比 | 主筋间距(mm) | 联合评分 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Y | HRB400 D16 x7 @ 147.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 37.60 | 0.000 | 1.42800 | 0.8571 | 147.0 | 0.1500 |
| 2 |  | HRB400 D18 x6 @ 176.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 39.60 | 0.000 | 1.42800 | 0.7902 | 176.0 | 0.3400 |
| 3 |  | HRB400 D20 x5 @ 220.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 40.76 | 0.000 | 1.42800 | 0.7680 | 220.0 | 0.4500 |

#### 类型 C
- 联合Pareto候选数: 3
- 拉筋Pareto候选数: 5
- 联合选型理由: joint_score_min=0.1500; metric_rank(cost/crack/asv/dist/spacing)=1/1/1/3/3; delta_vs_runner_up(selected-#2): cost=-2.00, crack=0.000, Asv/s=0.00000, dist_ratio=0.0670, spacing=-29.0
- 拉筋选型理由: min_delta_to_required=0.02800; status=ok; max_ratio=0.048; max_limit_ratio=0.013
- 拉筋所需 Asv/s: 1.40000
- 联合相对次优差值(入选-次优): cost=-2.00, crack=0.000, Asv/s=0.00000, dist_ratio=0.0670, spacing=-29.0

##### 联合候选对比

| 排名 | 入选 | 主筋 | 拉筋 | 分布筋 | 造价(CNY/m) | 最大裂缝(mm) | Asv/s | 分布筋比 | 主筋间距(mm) | 联合评分 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Y | HRB400 D16 x7 @ 147.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 37.60 | 0.000 | 1.42800 | 0.8571 | 147.0 | 0.1500 |
| 2 |  | HRB400 D18 x6 @ 176.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 39.60 | 0.000 | 1.42800 | 0.7902 | 176.0 | 0.3400 |
| 3 |  | HRB400 D20 x5 @ 220.0 | HRB400 D10@220.0 (4 legs layout) | HRB400 D16@176.0 (6 bars ratio) | 40.76 | 0.000 | 1.42800 | 0.7680 | 220.0 | 0.4500 |


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
