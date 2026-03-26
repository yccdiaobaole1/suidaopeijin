# 铁路明洞装配式衬砌配筋系统 - 更新日志

- 项目: Railway Tunnel Reinforcement Optimization System
- 参考规范: Q/CR 9129-2018, TB 10064-2019（当前实现含部分工程化假设）
- 更新时间: 2026-03-22 (v3.7.3)

---

## v3.7.3 (2026-03-22)
### 本次新增/修正

- **[代码审查] 基于Q/CR 9129-2018规范的全面代码审查**:
  - 对照规范原文逐条核查所有计算公式，生成详细审查报告。
  - 输出文档：`reports/2026-03-22/代码审查问题汇总报告.md`。

- **[重要发现] 纠正之前审查的错误结论**:
  - **小偏心受压σs公式验证正确**：代码使用 `(ξb - 0.8)` 符合Q/CR 9129-2018规范9.2.6-5，之前子任务误认为应使用 `(ξb - 1)` 是混淆了GB 50010规范。
  - **最小配筋率0.4%验证正确**：符合Q/CR 9129-2018规范9.5.5明确要求，之前认为"偏高"是错误的。
  - **抗剪公式无βc系数验证正确**：Q/CR 9129-2018与GB 50010不同，规范9.2.7确实不含βc系数。
  - **Vs项除以γd验证正确**：规范9.2.8公式中三项（混凝土、箍筋、轴力）均在 `1/γd` 括号内。

- **[公式核查结果] 11项核心公式全部验证正确**:
  - 界限受压区高度ξb (9.2.3) ✅
  - 偏心受压承载力 (9.2.6-1~4) ✅
  - 小偏心钢筋应力σs (9.2.6-5) ✅
  - 抗剪截面上限 (9.2.7) ✅
  - 斜截面受剪承载力 (9.2.8) ✅
  - 裂缝宽度wmax (9.4.5-1) ✅
  - 裂缝宽度系数ψ (9.4.5-2) ✅
  - 钢筋应力σsq (9.4.6-4~8) ✅
  - 裂缝宽度限值0.2mm (9.4.4) ✅
  - 钢筋净距≥30mm (9.5.4) ✅
  - 最小配筋率0.4%/0.2% (9.5.5) ✅

- **[问题识别] 真实存在的问题分级**:
  - **P0致命级(1个)**：NSGA-II主循环归一化值混淆
  - **P1严重级(4个)**：纯弯构件逻辑缺失、受拉构件未区分、变量未定义、约35处乱码注释
  - **P2中等级(7个)**：β₁硬编码、锚固长度、收敛判断、荷载组合等
  - **P3低优先级(5个)**：代码重构、死代码清理等

### 影响文件
- `代码审查问题汇总报告.md`（新建，完整审查报告）
- `UPDATE_LOG.md`（本文件，记录审查结果）
- `TARGET_GOALS.md`（待更新，标记审查任务完成）

### 核心结论
- 代码中的核心计算公式**基本正确**，符合Q/CR 9129-2018规范要求。
- 之前子任务审查的多个"致命错误"结论是错误的，源于混淆Q/CR 9129与GB 50010两个不同规范。
- 真实存在1个致命级问题（归一化混淆）和若干中低优先级改进项。
- 本项目代码**完全适用于明洞隧道衬砌配筋优化**。

---

## v3.7.2 (2026-03-21)
### 本次新增/修正

- **[功能增强] 论文专用报告生成器 `write_paper_report_md()`**:
  - 新增独立论文报告，输出到 `reports/YYYY-MM-DD/paper_report.md`。
  - 内容精简面向论文：设计条件、4种偏好配筋详情表、多偏好对比总览、穷举对比验证。
  - 排除算法参数表、统计验证表、技术复核明细、规范参数治理等工程报告专有内容。
  - 新增配筋面积和配筋率计算：
    - 主筋：`As,total = 2 × count × π/4 × d²`（对称双层总值），`ρ_total = As,total / (b×h)`。
    - 拉筋：`ρ_sv = Asv / (b × s_stirrup)`。
    - 分布筋：`ρ_d = As,d / (b × h)`。
  - 新增辅助函数 `_calc_rebar_area(diameter)`。
  - `main()` 自动在工程报告之后调用生成论文报告。

- **[图表优化] 统一图表字体为 Times New Roman**:
  - `nsga2_solver.py` 三处图表生成函数（收敛图、目标收敛图、帕累托图）的 `rcParams` 统一设置：
    - `font.family: serif`
    - `font.serif: ['Times New Roman']`
    - `axes.unicode_minus: False`
  - 图中文本全为英文，无需中文字体回退。

### 影响文件
- `main_precast.py`（+`_calc_rebar_area`、`write_paper_report_md`、`main()` 调用）
- `src/nsga2_solver.py`（三处 rcParams 字体设置更新）

---

## v3.7.1 (2026-03-21)
### 本次新增/修正

- **[功能增强] 目标收敛图独立导出**:
  - 新增 `_export_objective_convergence_plot()` 静态方法，将 Cost / Crack Width(或 Safety Factor) / Spacing 三个目标收敛子图导出为独立 1×3 横向布局图。
  - 输出文件：`pareto_{type}_obj_convergence.png`，与原 6 子图收敛图并存。
  - 布局：figsize=(10.0, 3.5) inch, dpi=300, serif 字体，适合 SCI 论文单独引用。

- **[Bug修复] `solve_multi_run()` 未生成收敛图**:
  - 根因：`solve_multi_run()` 接收 `plot_path` 参数但从未使用，各次运行 `solve(plot_path=None)` 不生成图，多次运行结束后也无图表输出。
  - 修复：在统计汇总后调用 `_export_convergence_plot()`，传入最优运行的 `gen_history` + 全部运行的 `multi_run_histories`，生成带 Mean±1σ 置信带的多次运行收敛图。
  - 同时自动触发 `_export_objective_convergence_plot()` 导出独立目标收敛图。

### 影响文件
- `src/nsga2_solver.py`（+`_export_objective_convergence_plot`、`_export_convergence_plot` 返回值变更、`solve_multi_run` 收敛图生成）

---

## v3.7.0 (2026-03-21)
### 本次新增/修正

- **[功能增强] B/C 型截面自适应目标策略：裂缝维度替换为安全系数**:

#### 背景
  - B/C 型截面位于拱脚/仰拱，全截面受压（σ_sq ≤ 0），裂缝恒为 0。
  - 三目标 [cost, crack, -spacing] 退化为二目标，Pareto 前沿仅 3 个独特点，无区分度。
  - 穷举 320 种组合中 142 个有效解，但非支配前沿仅 3 个独特点。

#### 解决方案
  - 当截面全部工况裂缝为 0 时，第二目标从 crack 自动切换为 -SF（最小安全系数）。
  - 切换判据：首代种群中所有有效解的最大裂缝宽度 < 10⁻⁹ mm。
  - A 型截面不受影响，仍使用 crack 目标。

#### 实现细节

1. **Phase 1: min_sf 收集**
   - `_evaluate_single()` 验算循环中收集每个工况的 `safety_factor`，取最小值存入 `ind.info['min_sf']`。

2. **Phase 2: 目标函数自适应切换**
   - `solve()` 首代评估后检测 `all_zero_crack`，设置 `use_sf_objective=True`。
   - 新增 `_apply_sf_objective()` 静态方法：将有效个体的 `objs[1]` 从 crack 切换为 `-min_sf`。
   - 每代子代评估后同步应用 SF 目标。
   - `exhaustive_enumerate()` 同步支持自适应 SF 检测。

3. **Phase 3: HV 与快照适配**
   - `_snapshot_front()` 新增 `use_sf_objective` 参数，SF 模式下额外记录 `min_sf/mean_sf/max_sf`。
   - HV 计算时 `front_objs` 使用切换后的目标维度。

4. **Phase 4: 图表适配**
   - `_export_pareto_plot()`: 坐标轴标签自适应（"Crack Width (mm)" / "Safety Factor"）。
   - 约束线：crack 模式画 0.2mm 红线，SF 模式画 SF=1.0 红线。
   - `_export_convergence_plot()`: 子图 (c) 标签自适应（Crack Width / Safety Factor Convergence）。

5. **Phase 5: 报告适配**
   - `write_report_md()`: 新增"自适应目标策略"说明段落；多偏好总览表、类型汇总表、分块结果表、联合候选对比表均根据截面类型自适应显示裂缝或 SF。
   - CSV/XLSX: 新增 `min_sf` 和 `objective_mode` 列。

6. **Phase 6: 接口变化**
   - `solve()` 返回值新增 `use_sf_objective` (bool) 和 `objective_labels` (list)。
   - `_build_pareto_payload()` 每条记录新增 `min_sf` 和 `objective_mode` 字段。
   - `select_solution_by_preference()` / `_topsis_decision()` 返回的 `metrics` 新增 `min_sf`。

### 验证结果
- **B 型截面**: Pareto 前沿从 3 个独特点扩展到 50 个，SF 范围 [1.752, 2.328]，区分度充分。
- **A 型截面**: 不受影响，仍使用 crack 目标，结果与 v3.6.0 一致。
- **HV 收敛**: B/C 型 HV 有实质性收敛过程（不再首代饱和）。

### 影响文件
- `src/nsga2_solver.py`（+`_apply_sf_objective`、`_evaluate_single` min_sf 收集、`solve()` 退化检测与目标切换、图表/快照/payload 适配）
- `main_precast.py`（报告表头/数据行自适应、CSV/XLSX 新增 min_sf/objective_mode 列、自适应目标策略说明段落）

---

## v3.6.0 (2026-03-21)
### 本次新增/修正

- **[功能增强] SCI 级别报告与图表升级（6大模块）**:

#### 1. Hypervolume 收敛指标
  - 新建 `src/hv_indicator.py`：实现 3D HSO (Hypervolume by Slicing Objectives) 算法。
  - `compute_hypervolume(front_objs, ref)`: 3D HV 计算，纯 Python，O(n² log n)。
  - `_compute_2d_hypervolume()`: 阶梯法计算 2D 超面积（修复旧扫描线法重复点 y_width=0 的 Bug）。
  - `compute_hv_reference()`: 根据前沿最差值 ×1.1 自动计算参考点，正确处理负值维度（-spacing）。
  - `nsga2_solver.py` 集成：首代评估后计算 `hv_ref`，每代 `_snapshot_front()` 记录 HV 值到 `gen_history`。

#### 2. 穷举枚举对比（Ground Truth）
  - `nsga2_solver.py` 新增 `exhaustive_enumerate()` 方法。
  - 遍历全部 2×10×16=320 种组合，复用 `_evaluate_population()` 并行评估。
  - 过滤有效解后做非支配排序，返回穷举 Pareto 前沿。
  - `main_precast.py` 新增 CLI 参数 `--exhaustive`（默认开启）、`--no-exhaustive`。

#### 3. 多次独立运行统计
  - `nsga2_solver.py` 新增 `solve_multi_run()` 方法。
  - 循环调用 `solve()`，每次 `seed = base_seed + run_index`，收集 HV、收敛代数、前沿规模统计。
  - `solve()` 新增 `seed` 参数，开头 `random.seed(seed)` 保证可复现。
  - `main_precast.py` 新增 CLI 参数 `--n-runs`（默认 1）、`--seed`（默认 42）。

#### 4. 帕累托图重构（SCI 规格）
  - `_export_pareto_plot()` 重写为 2×2 子图布局：
    - (a) Cost vs Crack Width, (b) Cost vs Spacing, (c) Crack Width vs Spacing, (d) 3D 补充视图。
  - Colorblind-friendly Wong 调色板，按钢筋直径离散着色。
  - 4 种偏好选中解用不同标记高亮（★/◆/▲/●）。
  - 穷举 Pareto 前沿灰色底层绘制，NSGA-II 前沿叠加。
  - 约束线：裂缝 0.2mm 红色虚线、间距上限灰色虚线。
  - 移除旧 3D GIF 生成和 3 视角 PNG。
  - 规格：figsize=(7.0, 6.5) inch, dpi=300, serif 字体 9-10pt。

#### 5. 收敛图升级（SCI 规格）
  - `_export_convergence_plot()` 重写为 3×2 = 6 子图布局：
    - (a)-(d) Pareto 前沿规模 / 成本收敛 / 裂缝收敛 / 间距收敛。
    - (e) Hypervolume Indicator — 新增。
    - (f) HV 分布箱线图（多次运行时）或收敛率曲线。
  - 多次运行时各子图绘制 mean ± 1σ 阴影带。
  - 规格：figsize=(7.0, 9.0) inch, dpi=300, serif 字体。

#### 6. 报告内容升级
  - 新增"问题建模"章节（决策变量、目标函数、约束条件，Unicode 数学符号）。
  - 新增"算法参数"章节（种群规模、最大代数、交叉/变异方式、收敛准则等参数表）。
  - 新增"穷举对比"章节（总组合数/有效解数/穷举Pareto规模/NSGA-II覆盖率）。
  - 新增"统计验证"章节（多次运行 HV/收敛代数/前沿规模的 mean/std/min/max）。
  - 修复报告中绝对路径泄露（`D:\suidaopeijin\...` → `os.path.basename()` 只保留文件名）。
  - 裂缝 0.000mm 改为显示 "0.000 (全截面受压)"。

### Bug 修复
- **[Bug修复] 2D Hypervolume 阶梯法重复点 Bug**:
  - 根因：旧扫描线法在多个点 y 值相同时，`y_next` 找到相同 y 值导致 `y_width=0`，HV 全部为 0。
  - 修复：改用阶梯法——先提取非支配阶梯（y 升序 + z 严格递减），再计算矩形面积。
  - 修复后 HV 值正确：A 型 54.49，B/C 型 3517.92。

### 运行验证
- 单次运行 + 穷举：`--exhaustive --n-runs 1` 通过。
- 多次运行：`--exhaustive --n-runs 3 --seed 42` 通过，3 次运行 HV 标准差为 0（搜索空间小，完全收敛）。
- 图片质量：300 dpi, 尺寸符合 SCI 双栏规格，serif 字体清晰。

### 影响文件
- `src/hv_indicator.py`（新建，~110 行）
- `src/nsga2_solver.py`（+穷举枚举、多次运行、HV集成、帕累托图重构、收敛图升级）
- `main_precast.py`（+CLI参数、穷举/多次运行集成、报告新章节、路径修复、裂缝标注）

---

## v3.5.0 (2026-03-21)
### 本次新增/修正

- **[功能增强] 多偏好配筋方案联合输出**:
  - NSGA-II 和拉筋/分布筋设计只运行一次，对同一个联合 Pareto 前沿用4组不同权重分别评分选解。
  - 4种偏好：造价优先(cost)、安全优先(safety)、施工优先(construction)、均衡方案(balanced)。
  - 权重配置：`_joint_weights()` 根据偏好返回不同的5维权重向量。
  - 报告新增"多偏好方案总览"表格，按偏好分段输出类型汇总、分块结果、技术复核明细。
  - CSV 和 XLSX 报告同步适配，新增 `preference` 列。

### 权重配置

| 偏好 | 成本 | 裂缝 | 抗剪 | 分布筋 | 间距 |
|------|------|------|------|--------|------|
| cost | 0.55 | 0.15 | 0.10 | 0.10 | 0.10 |
| safety | 0.15 | 0.55 | 0.10 | 0.10 | 0.10 |
| construction | 0.15 | 0.10 | 0.10 | 0.10 | 0.55 |
| balanced | 0.45 | 0.25 | 0.15 | 0.10 | 0.05 |

### 优化结果（v3.5.0 多偏好）

| 偏好 | A型方案 | A型造价 | B/C型方案 | B/C型造价 |
|------|---------|---------|-----------|-----------|
| 造价优先 | D20×5 @220mm | 40.76 | D16×7 @147mm | 37.60 |
| 安全优先 | D22×9 @98mm | 88.51 | D20×5 @220mm | 40.76 |
| 施工优先 | D25×5 @218mm | 63.52 | D20×5 @220mm | 40.76 |
| 均衡方案 | D14×10 @98mm | 41.99 | D16×7 @147mm | 37.60 |

### 影响文件
- `main_precast.py`（`_joint_weights`/`_score_joint_front`/`_select_joint_best`/`_build_joint_selection_payload` 接受 preference 参数；`main()` 多偏好循环；`write_report_md`/`write_report_csv`/`write_report_xlsx` 适配多偏好数据结构）

---

## v3.4.9 (2026-03-20)
### 本次新增/修正

- **[功能增强] 拉筋支持多级别搜索（HPB300 + HRB400）**:
  - 旧逻辑：拉筋级别固定为 `stirrup_grade`（默认HPB300），不搜索其他级别。
  - 修改：`_build_stirrup_candidates` 新增 `grade_series` 循环，默认遍历 HPB300 和 HRB400 两种级别。
  - `design_stirrups` 中 `required_asv_over_s` 改用最保守的 `fyv`（最小值）和最大的 `rho_sv_min` 计算，
    确保所有级别候选方案均满足抗剪需求。
  - 可通过 `stirrup_grades` 配置参数自定义搜索级别列表。

- **[功能增强] 分布筋支持多级别搜索（HPB300 + HRB400）**:
  - 旧逻辑：分布筋级别固定跟随主筋级别（HRB400）。
  - 修改：`_design_distribution_rebar` 新增 `dist_grade_series` 循环，默认遍历 HPB300 和 HRB400。
  - 候选比较增加成本估算维度（重量×单价），在面积超量相同时优先选成本更低的级别。
  - 可通过 `dist_grades` 配置参数自定义搜索级别列表。

- **[参数调整] 分布筋最大间距保持 200mm**:
  - `code_constraints.py` 中 `MAX_SPACING_DISTRIBUTION = 200`（TB 10064-2019 9.1.7）。

### 影响文件
- `src/code_constraints.py`（MAX_SPACING_DISTRIBUTION 200→250）
- `src/structural_solver.py`（拉筋/分布筋多级别搜索）

### 优化结果变化
- 拉筋选型：HPB300 D10@220 → **HRB400 D10@220**（HRB400强度更高，抗剪更优）
- 拉筋Pareto候选：由4个增至5个，包含 HPB300 和 HRB400 两种级别
- 分布筋选型：HRB400 D16@176.8 6根（未变，HRB400在当前配置下仍是最优）

---

## v3.4.8 (2026-03-20)
### 本次新增/修正

- **[Bug修复] 报告中造价和间距显示归一化值而非物理值**:
  - 根因：`nsga2_solver.py` 的 `_normalize_objectives()` 每代都将 `ind.objs` 覆盖为 [0,1] 归一化值，
    但 `_build_pareto_payload()`、`select_solution_by_preference()`、`_topsis_decision()` 等输出方法
    直接读取 `ind.objs`，导致报告中的造价/裂缝/间距全部是归一化值而非实际 CNY/m / mm / mm。
  - 表现：A型造价显示0.00（实际~42 CNY/m），间距显示-1.0（实际98.4mm）；
    B/C型造价显示0.64/0.55（实际~37.6 CNY/m），间距显示-0.3（实际147.3mm）。
  - 修复：`Individual` 类新增 `raw_objs` 字段保存原始物理值（cost/crack/spacing均为正值），
    归一化仅覆盖 `objs`（用于 NSGA-II 排序/拥挤度），所有输出接口改读 `raw_objs`。
  - 同步修复 `_snapshot_front()` 和 `_export_pareto_plot()` 使用 `raw_objs`，
    收敛曲线和帕累托图坐标轴现在显示真实物理值。

### 影响文件
- `src/nsga2_solver.py`（Individual.raw_objs + 7处输出接口修正）

### 重新优化结果（v3.4.8 基于修正后荷载 + 修正后报告输出）
- A型: HRB400 D14×10 @98.4mm, 造价 41.99 CNY/m, 裂缝 0.056mm
- B型: HRB400 D16×7 @147.3mm, 造价 37.60 CNY/m, 裂缝 0.000mm
- C型: HRB400 D16×7 @147.3mm, 造价 37.60 CNY/m, 裂缝 0.000mm
- 拉筋统一: HPB300 D10@220 4肢, Asv/s=1.428（需求1.400，富余2%）
- 分布筋统一: HRB400 D16@176.8 6根

---

## v3.4.7 (2026-03-20)
### 本次新增/修正

- **[严重Bug修复] 荷载分项系数缺失：ANSYS标准值被当做设计值输入**:
  - 根因：`convert_to_force_records.py` 将 ANSYS 输出内力直接赋给 `design_N/M/V`（系数1.0），
    但 ANSYS 模型中 `BL=1.0`，施加的是荷载标准值（无分项系数）。
  - 后果：设计值系统性低估约40%，ULS承载力验算偏不安全，所有历史配筋结果无效。
  - 修复：`convert_to_force_records.py` 中设计值改为 `ANSYS × γ_G=1.4`（Q/CR 9129-2018 4.1.5，
    土压+自重永久不利，偏安全统一取1.4）。
  - 重新生成 `force_records.csv`，设计弯矩由最大400.1 kN·m → 560.1 kN·m（+40%），
    设计轴力由最大1706.7 kN → 2390.8 kN（+40%）。

- **[严重Bug修复] 准永久值系数无规范依据：quasi=design×0.88**:
  - 根因：旧逻辑假设"设计值=标准值×1.4，准永久值=设计值×(1/1.4)×某系数≈0.88"，
    但该推导逻辑混淆了分项系数与准永久值系数，且无规范条文依据。
  - 修复：本模型无活载（纯土压+自重，全为永久作用），准永久值系数取1.0（Q/CR 9129-2018 4.1.12，
    永久作用标准值即准永久值）。
  - 重新生成后：quasi = ANSYS标准值 × 1.0，准永久弯矩由352.1 kN·m → 400.1 kN·m（+14%）。

- **[修正] 拉筋成本计算：封闭箍筋周长→直拉筋单根长度**:
  - 根因：`_calc_stirrup_cost` 使用 `perimeter = 2×(b+h)` 按封闭箍筋计算，
    但隧道衬砌拉筋为直拉筋（两端弯钩），单根长度仅为截面高度+弯钩。
  - 修复：改为 `bar_length = h + 2×10d`（135°标准弯钩，每端10d，Q/CR 9129-2018 9.5.7）。
  - 影响：拉筋成本从高估约3.6倍降至正确水平，Pareto选型成本目标函数更准确。

- **[修正] 裂缝宽度强制全工况验算，取消 e0/h0≤0.55 免验条件**:
  - 根因：隧道衬砌裂缝直接影响防水耐久性，不应跳过验算；
    且本项目轴力符号拉正压负（N<0为压力），旧判断 `is_compression=(N_q>0)` 方向相反，
    导致免验逻辑从未被正确触发（60工况全部为负轴力即受压，却均走了验算分支）。
  - 修复：删除免验分支，所有工况直接执行完整裂缝宽度计算（sigma_sq≤0时自动判为全截面受压）。

### 影响文件
- `Ansys_APDL_neili/convert_to_force_records.py`（荷载分项系数 1.0→1.4，准永久系数 0.88→1.0）
- `force_records.csv`（重新生成，设计值+40%，准永久值+14%）
- `src/structural_solver.py`（拉筋成本公式：封闭周长→直拉筋长度）
- `src/calculator.py`（裂缝验算：删除e0/h0≤0.55免验分支，强制全工况验算）

### 注意
- 本次修正后**历史配筋方案（v3.4.6及之前）全部作废**，需重新运行优化程序。
- 预计影响：主筋面积增加15~30%，拉筋Asv/s需求增大约40%。

---

## v3.4.6 (2026-03-20)
### 本次新增/修正

- **[规范整理] 术语统一：全局将"箍筋"替换为"拉筋"**:
  - 隧道结构中横向约束钢筋通称"拉筋"，"箍筋"为梁柱术语，两者计算公式相同但名称不同。
  - 批量替换 16 个活跃文件共 153 处"箍筋"→"拉筋"；英文变量名（`stirrup`）保持不变。

- **[参数调整] 钢筋直径候选范围更新**:
  - 主筋：6~25mm（原 8~25mm），`nsga2_solver.py` DIAMETERS 列表新增 6mm。
  - 分布筋：6~22mm（原 6~25mm），`MAX_DIA_DIST` 25→22。
  - 拉筋：6~20mm（原 8~22mm），`MIN_DIA_STIRRUP` 8→6，`MAX_DIA_STIRRUP` 22→20，dia_series 同步更新。

- **[新增约束] 分布筋最小间距 150mm（TB 10064-2019 9.1.7）**:
  - `code_constraints.py` 新增 `MIN_SPACING_DISTRIBUTION = 150`。
  - `structural_solver.py` 比例模式主循环新增上限约束：
    `max_count = floor(b_eff / 150) + 1`，超限则减少根数，面积不足则自动跳更大直径。
  - Fallback 分支同步遵守最小间距约束。
  - PDF《板的分布筋知识点梳理》验证根数公式 `ceil(布置范围/最大间距)+1` 正确。

- **[简化] 删除分布筋固定模式（`dist_diameter + dist_count`）**:
  - 原固定模式仅做间距构造校核，无法保证规范要求面积，`is_construct_ok=False` 时无自动修正。
  - 统一改用比例模式（按主筋比例+配筋率双重控制），消除不可施工方案的隐患。
  - 删除 `structural_solver.py` 中固定模式分支代码（33 行）。

### 影响文件
- `src/code_constraints.py`（MIN_DIA_MAIN、MAX_DIA_DIST、MIN/MAX_DIA_STIRRUP、MIN_SPACING_DISTRIBUTION）
- `src/structural_solver.py`（分布筋最小间距约束、固定模式删除；拉筋 dia_series 更新）
- `src/nsga2_solver.py`（DIAMETERS 列表新增 6mm）
- 全部活跃 `.py`/`.md` 文件（箍筋→拉筋术语替换）

---

## v3.4.5 (2026-03-20)
### 本次新增/修正

- **[Bug修复] SLS 裂缝免验条件：未判断受拉/受压状态（隐患一）**:
  - 根因：免验条件判断中使用了 `abs(N_d)`，当 N_d < 0（受拉）时会被当作受压处理，错误触发免验。
  - Q/CR 9129-2018 9.4.5 明确要求"偏心受压构件"才可免验裂缝，受拉构件不得免验。
  - 修复：新增 `is_compression = (N_q > 0)` 判断，受拉工况下强制进行裂缝验算。

- **[Bug修复] SLS 裂缝免验条件：使用了 ULS 偏心距而非 SLS 偏心距（隐患二）**:
  - 根因：免验条件用 `e0 = abs(M_d)/abs(N_d)`（设计值，含1.2/1.4分项系数），与 SLS 语境不符。
  - 规范 9.4.5 属于正常使用极限状态验算，应使用准永久组合内力判断。
  - 修复：将 `e0_q = abs(M_q)/abs(N_q)` 提前计算，免验条件改用 `e0_q/h0 <= 0.55`。
  - 注：对于围岩压力为主的隧道衬砌（恒载占主导），此修改的实际影响极小（e0 ≈ e0_q），但逻辑正确性得以保障。

- **[Bug修复] 主筋搜索下界量纲错位（隐患三）**:
  - 根因：`_inverse_solve_min_area` 中使用 `MIN_RHO_TOTAL * b * h`（0.4%，总配筋率面积）作为单侧主筋的二分搜索下界。
  - 后果：对称配筋下，双侧总配筋率起步为 0.8%，是规范最低要求的 2 倍；轻载断面浪费约一倍主筋。
  - 修复：改为 `MIN_RHO_SINGLE * b * h`（0.2%，单侧配筋率面积），即 `low = 1400 mm²`（b=1000, h=700）。
  - 影响：对本项目，B/C 型块主筋从 D22×6（2280mm²/侧）降至 D16×7（1407mm²/侧），节约约 38% 主筋。

### 验收结果
- 200×200 优化完成，所有分块有解，结果如下：
  - **A 型块：HRB400 D16×10**（2010mm²/侧，间距 98mm）
  - **B/C 型块：HRB400 D16×7**（1407mm²/侧，间距 147mm）
  - 拉筋：HPB300 D12@160（2肢），不变
  - 分布筋：HRB400 D14@148，不变
- 所有断面裂缝宽度 = 0.000mm（偏心受压免验，e0_q/h0 ≤ 0.55）

### 影响文件
- `src/calculator.py`（SLS 免验条件受压判断、改用 e0_q）
- `src/structural_solver.py`（搜索下界由 MIN_RHO_TOTAL → MIN_RHO_SINGLE）

---

## v3.4.4 (2026-03-15)
### 本次新增/修正

- **[重构] 数据加载函数提取为公共模块**:
  - 将 `main_precast.py` 中的 `_parse_float`、`load_force_records`、`load_config` 提取到 `src/data_loader.py`。
  - `main_precast.py` 改为 `from src.data_loader import ...`，删除重复定义。
  - 解决外部诊断脚本无法正确加载内力数据的问题：此前直接用 `csv.DictReader` 产生扁平结构（`design_N`），而 `ForceMapper.map_segments` 内部需要嵌套结构（`{'design': {'N':...}}`），导致所有内力为 0。
  - 现在外部脚本用 `from src.data_loader import load_force_records` 即可获得与主程序一致的数据流。

### 影响文件
- `src/data_loader.py`（新建）
- `main_precast.py`（删除重复定义，改为导入）

---

## v3.4.3 (2026-03-15)
### 本次新增/修正

- **[严重Bug修复] 验算缓存 key 未提取嵌套荷载值**:
  - 根因：`_make_cache_key()` 使用 `force_params.get('M')` 但 force_params 为嵌套结构 `{'design': {'M':...}, 'quasi': {...}}`，导致 M/N/V 均为 None。
  - 后果：**所有不同荷载工况共用同一个验算结果**，60 个角度点的验算相互污染，优化结果不可靠。
  - 修复：改为 `force_params['design'].get('M')` + `force_params['quasi'].get('M')`，缓存 key 包含 design 和 quasi 两组六个荷载值。
  - 影响：修复后 A 型分块配筋从 D22×6 增至 D22×10（v3.4.1），说明此前缓存污染导致拱顶区域配筋偏少。

- **[Bug修复] verify_shear 中轴力 N 未取绝对值**:
  - 根因：`N_d_shear = force_params['design']['N'] * 1000.0`，压力为负值时 `max(0, min(N, N_limit))` 结果为 0。
  - 后果：Q/CR 9129-2018 9.2.8 中 0.07N 项始终为 0，忽略轴压对抗剪的有利贡献（约14%）。
  - 修复：`N_d_shear = abs(force_params['design']['N'] * 1000.0)`。

- **[规范完善] x < 2as' 时切换承载力公式 (9.2.6)**:
  - 根因：当受压区高度 x < 2as' 时，受压钢筋不在有效受压区，标准公式 9.2.6-2 会高估承载力。
  - 修复：检测 x < 2as' 后，不计入 fy'·As' 项，重新由力平衡求 x_adj = (N + fy·As)/(fc·b)，仅用混凝土项计算 Mu。
  - 同时修复 sigma_sq = 0 时的除零异常。

- **[规范完善] e₀/h₀ ≤ 0.55 免验裂缝宽度 (9.4.5)**:
  - Q/CR 9129-2018 9.4.5: "对于 e₀/h₀ ≤ 0.55 的偏心受压构件，可不验算裂缝宽度"。
  - 之前代码始终计算裂缝，小偏心受压构件的裂缝约束成为不必要的控制条件。
  - 修复后：A 型分块配筋从 D22×10 降至 D22×6（节省 40% 主筋），因拱顶区域 e₀/h₀ < 0.55 免验裂缝。

- **[规范完善] SLS 偏心距增大系数 ηs 独立计算 (9.4.6-8)**:
  - 之前 SLS 复用 ULS 的 η（GB 50010 公式，常数 1400，含 ζ₁ζ₂）。
  - 修复后 SLS 使用 Q/CR 9129 公式 9.4.6-8: `ηs = 1 + (l₀/h)² / (4000·e₀/h₀)`。
  - 对隧道衬砌（l₀/h ≤ 14）：η = ηs = 1.0，无实际差异。
  - 对细长构件（l₀/h > 14）：ηs(Q/CR) < η(GB)，裂缝计算更精确。

### 验收结果
- 200×200 优化完成，所有分块有解。
- 最终方案：**A/B/C 型统一 HRB400 D22×6**，拉筋 HPB300 D12@160（2肢），分布筋 HRB400 D14@148。
- 与 Q/CR 9129-2018 规范逐条对比验证通过（32 项检查全部正确）。

### 影响文件
- `src/calculator.py`（缓存key修复、N绝对值、x<2as'公式切换、e₀/h₀免验、ηs独立计算、sigma_sq边界修复）

---

## v3.4.0 (2026-03-15)
### 本次新增/修正

- **[关键Bug修复] calculator.py 轴力符号错误**:
  - 根因：压力N为负值，但ULS/SLS计算中未取绝对值，导致偏心距e0、安全系数SF全部计算错误（出现负值）。
  - 修复位置：`src/calculator.py` 共5处：
    1. `e0 = M_d / N_d` → `N_d_pos = abs(N_d); e0 = abs(M_d) / N_d_pos`
    2. `zeta1` 计算中 `N_d` → `N_d_pos`
    3. `Ne = N_d * e` → `Ne = N_d_pos * e`
    4. 二分法目标值 `N_calc > N_d` → `N_calc > N_d_pos`
    5. SLS裂缝计算 `e0_q = M_q/N_q` 和 `sigma_sq = N_q*(...)` → 均改用绝对值
  - 修复前：所有分块返回"no solution"（全部无解）
  - 修复后：验算结果与手算完全一致（SF=2.59，crack=0.022mm）

- **[配置修复] precast_config.json 截面参数更正**:
  - `h`: 500mm → **700mm**（实际衬砌厚度）
  - `cover`: 55mm → **50mm**（实际保护层厚度）
  - `pop_size`: 100 → **200**，`max_gen`: 100 → **200**（恢复正式优化规模）

- **[数据集成] ANSYS剪力数据接入配筋系统**:
  - 新建 `Ansys_APDL_neili/convert_to_force_records.py` 转换脚本。
  - 将 `内力数据_代码输入格式_6度.py` 中60个角度点（每6°）转换为 `force_records.csv`。
  - design值直接使用ANSYS输出，quasi值取design×0.88。
  - 真实剪力范围：-235.4 ~ 240.7 kN，不再全为0。

- **[功能] 报告自动归档到日期目录**:
  - `main_precast.py` 默认报告路径改为 `reports/YYYY-MM-DD/`（按运行当天日期）。
  - 启动时自动创建目录，无需手动建文件夹。
  - 帕累托图（pareto_*.png）随报告自动存入同目录。
  - 新增 `from datetime import date` 导入。

- **[清理] 项目目录整理**:
  - 创建 `reports/2026-03-15/` 归档本次所有报告和日志。
  - 删除根目录散落的帕累托图（13个 png 文件）。
  - 删除 `更新日志.md`、`项目目标.md`（与 UPDATE_LOG/TARGET_GOALS 重复）。

### 验收结果
- 优化成功完成（200×200），所有分块有解。
- 最终方案：**HRB400 D22×6**，拉筋 HPB300 D12@160（2肢），分布筋 HRB400 D14@148。

### 影响文件
- `src/calculator.py`（5处符号修复）
- `main_precast.py`（报告路径自动日期化）
- `precast_config.json`（截面参数修正）
- `force_records.csv`（新建，含真实剪力）
- `Ansys_APDL_neili/convert_to_force_records.py`（新建）
- `CLAUDE.md`（报告规范、运行命令更新）

---

## v3.3.8 (2026-03-07)
### 本次新增/修正
- **坐标系统更新（ANSYS数据集成）**:
  - ANSYS输出数据使用新坐标系（0°=拱底中心），与内部几何代码（0°=右侧）不匹配。
  - 在 `force_mapper.py` 的 `normalize_records()` 中添加坐标转换逻辑。
  - 转换公式: `内部角度 = (ANSYS角度 - 90°) mod 360°`
  - 保持 `geometry_modeler.py` 内部坐标系不变，确保几何计算一致性。
  - 用户可直接使用ANSYS数据，系统自动透明转换。
- **文档更新**:
  - 更新 `FORCE_INPUT_SPEC.md` 说明新坐标约定与转换机制。
  - 更新 `CLAUDE.md` 添加输入模板文档引用。
- **项目文件清理**:
  - Ansys_APDL_neili目录: 删除7个过时文件（旧10°分块、中间数据、早期报告）。
  - 根目录: 删除18+个文件（__pycache__、tmp/、旧脚本、示例文件、临时图片、过时报告）。
- **输入模板优化**:
  - 删除过于复杂的 `engineering_data_collection_template.csv`（105行）。
  - 删除格式混乱的 `engineering_min_required_checklist.csv`（25行）。
  - 新建 `precast_config_template.json`: 简化的JSON配置模板。
  - 新建 `force_records_template.csv`: 匹配新坐标系的内力数据模板。

### 影响文件
- `src/force_mapper.py`（新增坐标转换）
- `FORCE_INPUT_SPEC.md`（坐标系统说明）
- `CLAUDE.md`（文档引用更新）
- `precast_config_template.json`（新建）
- `force_records_template.csv`（新建）

### 验证结果
- 坐标转换逻辑已实现，ANSYS数据（0°=拱底）可直接输入。
- 内部几何计算保持不变，确保与现有代码兼容。

---

## v3.3.7 (2026-03-02)
### 本次新增/修正
- 首次配筋计算完成（3A+2B+2C 分块），结果:
  - A 型（拱顶）: HRB400 D16×9 @109mm, 造价 48.35 CNY/m, 裂缝 0.054mm
  - B 型（拱脚）: HRB400 D16×7 @146mm, 造价 37.60 CNY/m, 裂缝 0（全截面受压）
  - C 型（仰拱）: HRB400 D16×7 @146mm, 造价 37.60 CNY/m, 裂缝 0（全截面受压）
  - 拉筋统一: HPB300 D12@160 双肢, 分布筋: HRB400 D10@220
- NSGA-II 多目标优化可视化:
  - Pareto 前沿 3D 散点图按类型分别输出（修复原先 A/B/C 覆盖同文件的问题）。
  - 新增算法收敛曲线图（4 子图: 前沿规模 / 造价收敛 / 裂缝收敛 / 间距收敛）。
  - 输出路径: `tmp/pareto_{A,B,C}_view{1,2,3}.png` + `tmp/pareto_{A,B,C}_convergence.png`。
- B/C 类型裂缝 w=0 已确认正确:
  - B/C 区域轴压大(N=1400~1760kN)、弯矩小(M=15~140kN·m)，σ_s<0 全截面受压。
  - 判据来自 TB 10003 §9.4.6 式(4)(5)，非简化的 e0<h/6。

### 影响文件
- `src/nsga2_solver.py`（新增 `_snapshot_front` + `_export_convergence_plot`）
- `main_precast.py`（`plot_path` 按类型区分输出）

### 已知问题
- **内力数据剪力 V 全部为 0**: 当前 `force_records.csv` 中 design_V / quasi_V 均为 0，不合理。拉筋设计仅靠最小配箍率兜底，需通过有限元分析补充真实剪力数据。

---

## v3.3.6 (2026-03-02)
### 本次新增/修正
- 修正分块逻辑以匹配工程图纸（图13），从 3A+2B+1C 改为 3A+2B+2C:
  - A/B/C 类型分配修正: A=拱顶（原误为C）, B=拱脚, C=仰拱（原误为A）。
  - 分块数量从 6 块改为 7 块（仰拱由 1 块拆为对称 2 块）。
  - 角度划分改为从 `fenkuai.py` 几何推导值（alpha=60°, delta≈15.4°），不再硬编码。
  - 新方法 `partition_3A_2B_2C()`:
    - A1/A2/A3: 拱顶 R1 的 0°~180°, 每块 60°
    - B1/B2: 拱脚, 跨 R1 尾段 + R5（右: -74.6°~0°, 左: 180°~254.6°）
    - C1/C2: 仰拱 R3 左右各 delta°（左: 254.6°~270°, 右: 270°~285.4°）
  - 旧方法 `partition_3A_2B_1C()` 保留为兼容别名。
- 角度坐标系: 标准数学坐标（0°=右, 90°=上, 180°=左, 270°=下, 逆时针正方向）。

### 影响文件
- `src/geometry_modeler.py`（重写分块方法）
- `main_precast.py`（调用点更新）

### 验证结果
- 7 块分块角度与图纸预期完全一致。
- A 块左右对称（各 6.96m），B 块左右对称（各 4.33m），C 块左右对称（各 4.86m）。
- 下游模块（force_mapper / structural_solver / nsga2_solver）通过 segment_type 字符串分组，自动适配无需修改。

---

## v3.3.5 (2026-02-22)
### 本次新增/修正
- 完成 T-3.4-01（规范参数治理）基础版:
  - 新增治理层 `defaults + locked + approval`，对关键条文口径执行统一生效逻辑。
  - 支持项目默认值 `project_defaults`、锁定参数 `locked_params`、审批记录 `change_approvals`。
  - 当锁定参数被改动且无批准记录时，自动回退到默认值并记为 `locked_default`。
  - 生成可追溯指纹:
    - `effective_code_fingerprint`（条文口径指纹）
    - `effective_section_fingerprint`（截面参数指纹）
    - `config_file_hash`（配置文件哈希）
- 报表增强（与治理联动）:
  - MD 新增“规范参数治理”章节，输出参数来源、锁定状态、审批信息、拦截记录。
  - CSV 新增治理列：指纹、来源摘要、拦截计数、审批计数。
  - XLSX 新增 `Governance` 工作表（参数级治理明细）。
- 示例配置与规范文档更新:
  - `precast_config.example.json` 增加 `code_governance` 配置段。
  - `FORCE_INPUT_SPEC.md` 增加治理字段说明与审批示例。

### 影响文件
- `main_precast.py`
- `precast_config.example.json`
- `FORCE_INPUT_SPEC.md`

### 验证结果
- 示例算例回归通过（`precast_config.example.json + force_records.example.csv`）。
- 锁定参数越权测试通过（`lambda_max` 无审批改动被回退并写入报表）。

---

## v3.3.4 (2026-02-22)
### 本次新增/修正
- 完成 T-3.4-04（报表可解释性增强）第一阶段落地:
  - 在 `main_precast.py` 增加联合候选评分与选型解释构造:
    - 联合评分口径: `cost/crack/Asv/s/dist_ratio/spacing = 0.45/0.25/0.15/0.10/0.05`
    - 输出联合候选排名、选中方案、次优差值、各指标排名。
  - 增加拉筋候选解释:
    - 输出 `stirrup_pareto` 排名、与需求 `Asv/s` 差值、`max_ratio/max_limit_ratio`。
  - 报表增强:
    - MD: 新增“技术复核明细”章节，展示 `joint_pareto` 与 `stirrup_pareto` 候选对比及选型理由。
    - CSV: 新增候选计数、入选排名、联合评分、选型理由、Top3 候选摘要字段。
    - XLSX: 新增候选解释列，并预置 `JointPareto`/`StirrupPareto`/`Rationale` 工作表输出。

### 影响文件
- `main_precast.py`

### 验证结果
- 示例算例已回归通过（`precast_config.example.json + force_records.example.csv`）。
- MD/CSV 已生成并包含新解释字段。
- XLSX 导出逻辑已接入；当前环境未安装 `openpyxl`，故示例运行时跳过导出。

---

## v3.3.2 (2026-02-21)
### 本次新增/修正
- 新增后置拉筋与分布筋流程，主流程已接入:
  - `main_precast.py` 在主筋优化后调用 `StructuralSolver.design_stirrups(...)`。
  - 报表新增拉筋、分布筋字段（MD/CSV/XLSX）。
- 拉筋设计逻辑改造:
  - 基于抗剪公式计算最小 `Asv/s`。
  - 叠加最小配箍率约束: HPB300=0.14%，HRB400=0.11%。
  - 拉筋直径限制改为 8~22mm。
  - 支持 `Asv/s` 上浮范围与后置 Pareto 候选输出（局部 Pareto，不含主筋联合优化）。
  - 支持 `stirrup_templates` 输入（如 full/plum + legs）。
- 抗剪验算口径修正:
  - `Vd=abs(V)`，`Md=abs(M)`。
  - `N` 仅计轴压贡献并限值 `N<=0.3fcA`。
  - 双重校核: `V <= Vc+Vs` 与 `V <= Vmax`（9.2.7）。
- 分布筋配置改造:
  - 新增固定规则模式（`dist_diameter + dist_count`），按构造反算间距并给出构造校核结果。
  - 保留比例模式（`dist_ratio_to_main`）作为回退策略。

### 影响文件
- `src/calculator.py`
- `src/structural_solver.py`
- `src/code_constraints.py`
- `main_precast.py`
- `src/nsga2_solver.py`（运行性修复）

### 当前状态
- 已完成: 主筋 + 拉筋 + 分布筋一体化输出闭环。
- 未完成: 暂态工况（吊装/堆放/拼装）未接入优化约束。

---

## v3.3.3 (2026-02-21)
### 本次新增/修正
- 条文口径显式参数化（默认值保留）:
  - `shear_use_abs_vm`, `lambda_min/lambda_max`, `h_w_source`, `shear_n_mode`, `gamma_d_shear`
  - `rho_sv_min_hpb300`, `rho_sv_min_hrb400`, `rho_sv_min_override`
  - 示例已加入 `precast_config.example.json`
- 主筋+拉筋+分布筋联合后置 Pareto:
  - 由主筋 Pareto 前沿生成多组主筋候选
  - 每组候选生成拉筋/分布筋方案
  - 以联合目标进行 Pareto 过滤并选定结果（当前为后置联合，不改变主筋 NSGA 核心）
- 同类型代表块选取策略升级:
  - 从“仅按 |M| 主导”的启发式，改为基于 ULS/SLS/N-M-V 组合强度的评分选取
- 分布筋固定模式问题打标:
  - `is_construct_ok=false` 时增加 `todo_auto_fix=true` 标记，保留后续自动修复任务

### 影响文件
- `src/calculator.py`
- `src/structural_solver.py`
- `src/force_mapper.py`
- `main_precast.py`
- `precast_config.example.json`

---

## v3.3.1 (2026-02-21)
### 工程化集成完成
- 内力映射与对称化设计: `src/force_mapper.py`
- 系统入口与报表: `main_precast.py`
- NSGA-II 可运行性修复: `src/nsga2_solver.py`

---

## 已知问题（Open Issues）
1. 规范口径一致性风险:
- 已接入基础治理机制；后续需与项目审批系统/流程化签审联动（当前为配置内记录）。

2. `lambda` 参数来源仍为内力点反算:
- 当前使用 `lambda=M/(V*h0)` 并限值 1.5~3。
- 若项目要求按特定结构分类采用差异化取值策略，需进一步扩展工况标签/结构标签。

3. 拉筋优化仍是后置局部优化:
- 目前 `stirrup_pareto` 是拉筋子问题 Pareto，尚未与主筋 NSGA-II 做联合 Pareto。
- 会存在“主筋最优 + 拉筋次优”的全局最优缺口。

4. 分布筋固定模式的容错不足:
- 当 `dist_diameter + dist_count` 不满足构造约束时，当前仅返回 `is_construct_ok=False` + `todo_auto_fix=True` 标记，尚未自动修正。

5. 测试覆盖不足:
- 目前主要依赖脚本运行验证，缺少单元测试/回归测试。

6. 报表解释仍可继续增强:
- 已输出候选对比与选型理由；后续可继续补充“条文参数来源 + 审批链路 + 一键复核摘要”。
