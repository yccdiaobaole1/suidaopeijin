# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

隧道明洞衬砌配筋优化系统 - 基于 NSGA-II 多目标优化算法的铁路隧道衬砌配筋设计工具。

## Running the System

```bash
# 主程序入口（报告自动存入 reports/YYYY-MM-DD/ 目录）
python main_precast.py --config precast_config.json --force-file force_records.csv \
  --report-md reports/$(date +%Y-%m-%d)/report.md \
  --report-csv reports/$(date +%Y-%m-%d)/report.csv

# Windows 示例（手动指定日期）
python main_precast.py --config precast_config.json --force-file force_records.csv \
  --report-md reports/2026-03-15/report.md \
  --report-csv reports/2026-03-15/report.csv
```

### 报告存放规范（强制）

**每次运行必须将报告输出到 `reports/YYYY-MM-DD/` 目录，禁止直接放在根目录。**

```
reports/
├── 2026-03-15/
│   ├── report_v340.md      # 主报告
│   ├── report_v340.csv     # CSV明细
│   └── ...
├── 2026-03-20/
│   └── ...
```

- 日期格式：`YYYY-MM-DD`（运行当天日期）
- 同一天多次运行：在文件名中加版本标识，如 `report_v1.md`、`report_v2.md`
- 根目录不得存放任何 `.md`/`.csv` 报告文件

## Architecture

### Three-Stage Optimization Pipeline

系统采用三阶段串行优化流程，每个阶段生成帕累托前沿：

**Stage 1: 主筋优化 (NSGA-II)**
- 文件: `src/nsga2_solver.py`
- 算法: NSGA-II 多目标进化算法
- 变量: 钢筋等级(HRB400/500)、直径(8-25mm)、间距(100-250mm)
- 目标: 最小化成本、最小化裂缝、最大化间距
- 输出: 帕累托前沿(默认200×200种群规模)
- 关键方法: `HybridNSGA2Solver.solve()`

**Stage 2: 拉筋设计 (启发式搜索)**
- 文件: `src/structural_solver.py`
- 方法: `StructuralSolver.design_stirrups()`
- 流程: 计算所需Asv/s → 生成候选方案 → 并行验算 → 帕累托筛选
- 优化: 使用4线程并行验算候选方案

**Stage 3: 分布筋设计**
- 文件: `src/structural_solver.py`
- 方法: `StructuralSolver._design_distribution_rebar()`
- 规则: 按主筋面积15%配置(TB 10064-2019 9.1.7)

### Core Modules

**验算引擎** (`src/calculator.py`)
- `TunnelCalculator.verify_structure()` - 承载力全面验算
- `TunnelCalculator.verify_shear()` - 抗剪验算
- 规范: Q/CR 9129-2018 (铁路混凝土结构设计规范)
- 特点: 二分法精确求解受压区高度(50次迭代)、缓存机制

**约束管理** (`src/code_constraints.py`)
- `CodeConstraints` - 集中管理所有设计约束和规范限值
- 关键约束: 最小配筋率、最大间距、保护层厚度、锚固长度

**报告生成** (`src/report_generator.py`)
- `ReportGenerator.generate_report()` - 生成Markdown格式优化报告
- 包含: 配筋方案、验算结果、帕累托前沿表格

## Key Design Patterns

### 并行优化
- 主筋种群评估: ThreadPoolExecutor (4 workers)
- 拉筋候选验算: ThreadPoolExecutor (4 workers)
- 预期性能提升: 2-3倍

### 缓存机制
- 验算结果缓存: `calculator.py` 中的 `_verify_cache`
- 缓存命中率: 20-30%
- 性能提升: 1.2-1.5倍

### 收敛判断
- 监测连续5代平均成本变化率
- 阈值: < 0.1%
- 提前终止避免不必要迭代

## Code Standards

### 规范引用
- **Q/CR 9129-2018**: 铁路混凝土结构设计规范(主要)
- **TB 10064-2019**: 铁路混凝土结构设计规范(分布筋)
- **GB 50010**: 混凝土结构设计规范(参考)

所有规范引用必须注明条款号，例如：
```python
# Q/CR 9129-2018 9.2.6: 结构调整系数 gamma_d = 1.0
# TB 10064-2019 9.1.7: 配筋不宜小于受力钢筋的15%
```

### 编码规范
- 文件编码: UTF-8 (已修复历史乱码问题)
- 中文注释: 使用规范的专业术语
- 变量命名: 遵循工程习惯(如 As, Asv, h0, fyv)

## Important Notes

### 优化参数调整
- 重要项目: `pop_size=200, max_gen=200`
- 快速测试: `pop_size=50, max_gen=50`
- 用户偏好: `preference="cost"|"safety"|"construction"|"balanced"`

### 验算失败处理
- 构造配筋不足会返回 `is_safe=False`
- 不可行解会被自动过滤
- 最终帕累托前沿仅包含可行解

### 数据流
```
荷载包络 → 主筋优化(NSGA-II) → 帕累托前沿(top 24) →
每个主筋方案设计拉筋 → 联合帕累托优化 → 用户偏好选择 →
最终方案 + 分布筋 → 报告生成
```

## Documentation

关键文档位于项目根目录：
- `配筋优化系统评估报告.md` - 系统评估和优化历史
- `配筋优化系统架构说明.md` - 详细架构说明
- `乱码修复报告.md` - 编码问题修复记录
- `UPDATE_LOG.md` - 系统更新记录
- `TARGET_GOALS.md` - 开发路线图

输入数据模板：
- `precast_config_template.json` - 配置文件模板
- `force_records_template.csv` - 内力数据模板

### 文档维护规范

**重要更新后必须同步更新文档：**

每次完成以下类型的重要更新后，必须立即更新相应文档：

1. **UPDATE_LOG.md** - 记录所有代码变更：
   - 新功能实现
   - Bug修复
   - 架构调整
   - 算法优化
   - 数据格式变更
   - 依赖更新

2. **TARGET_GOALS.md** - 更新项目状态：
   - 将完成的任务从"未完成"移至"已完成"
   - 更新当前版本号
   - 更新文档日期
   - 调整优先级和待办事项

**更新时机：**
- 在完成功能开发并验证通过后立即更新
- 在提交代码前确保文档已同步
- 每个版本发布前检查文档完整性

---

## ANSYS APDL 专项指导

本项目涉及隧道衬砌内力计算，使用 ANSYS APDL 进行有限元分析。

### APDL 命令流标准结构

**六阶段串行流程：**

1. **前处理 (/PREP7)** - 几何建模、关键点定义
2. **材料与单元定义** - 混凝土参数、弹簧刚度、单元类型
3. **网格划分** - 线网格(梁单元)、面网格(平面单元)
4. **荷载施加** - 重力、非均匀水土压力循环
5. **边界条件与求解 (/SOLU)** - 约束、弹簧生成、SOLVE
6. **后处理 (/POST1)** - 内力提取、结果输出

### 几何建模原则

**关键点分层定义：**
```apdl
! 中心线关键点 (K1-K9) - 用于提取内力
K, 1, 0.00000, -4.52400, 0
K, 2, 4.89643, -3.85960, 0
...

! 内轮廓关键点 (K11-K19) - 衬砌内侧
K, 11, 0.00000, -4.17400, 0
...

! 外轮廓关键点 (K21-K29) - 衬砌外侧
K, 21, 0.00000, -4.87400, 0
...

! 圆弧中间点 (K31-K59) - 用于三点画弧
K, 41, 2.47000, -4.35700, 0
...
```

**三点画弧法（避免精度警告）：**
```apdl
LARC, P1, P2, P_mid    ! 不指定半径，让ANSYS自动贴合
```
- 坐标精度：关键点6位小数，中间点5位小数
- 避免四舍五入误差导致的几何警告

**预制块分割原则：**
- **A型预制块**：上半拱60°三等分（3块），在拼缝处创建关键点
- **B型预制块**：保持整体，不在中间分块（即使由两个不同圆心的圆弧组成）
- 目的：避免在拼缝处产生应力集中，确保内力分布合理

### 材料参数定义

**混凝土参数：**
```apdl
E_C = 34.5e9      ! 弹性模量 (Pa)
U_C = 0.2         ! 泊松比
DENS_C = 2420     ! 密度 (kg/m³)
TH = 0.7          ! 衬砌厚度 (m)
```

**围岩弹簧刚度：**
```apdl
KS = 143.8e6      ! 弹性反力系数 (N/m³)
```
- 好地层：400e6
- 中等地层：200e6
- 差地层：100e6

**单元类型：**
- **PLANE182**：二维实体混凝土面
- **BEAM188**：梁单元（虚拟荷载梁、真实内力梁）
- **LINK10**：弹簧单元（围岩反力）

### 荷载施加方法

**非均匀水土压力循环算法：**
```apdl
*DO, I, 1, NNODE
  *GET, Y_I, NODE, I, LOC, Y    ! 获取节点Y坐标
  *IF, Y_I, GT, Y_TOP, THEN
    Q_I = Q_TOP + (Q_BOT - Q_TOP) * (Y_TOP - Y_I) / (Y_TOP - Y_BOT)
  *ENDIF
  F, I, FY, -Q_I                ! 施加竖向荷载
*ENDDO
```

**关键注意事项：**
- 使用精确的Y坐标范围判断，避免浮点数判断失效
- 梯形分布：顶部压力小，底部压力大，线性插值过渡
- 荷载单位统一为 Pa（帕斯卡）

### 网格划分策略

**映射网格（推荐）：**
```apdl
MSHAPE, 0, 2D      ! 2D四边形网格
MSHKEY, 1          ! 启用映射网格
LESIZE, ALL, 0.2   ! 单元尺寸0.2m
```

**关键要求：**
- 使用规则四边形面（12-18个面）
- 径向切割线将截面分割
- 网格点与预制块拼缝对齐
- 单元尺寸：0.1-0.3m（根据精度要求）

### 边界条件与弹簧支座

**约束设置：**
```apdl
D, ALL, UX, 0     ! 约束水平位移（防止刚体平移）
D, ALL, ROTY, 0   ! 约束转角（如需要）
```

**弹簧生成逻辑：**
- 在外轮廓节点处生成LINK10单元
- 连接外轮廓节点→固定基础
- 刚度 = KS × 单元长度

### 后处理与内力提取

**内力提取命令：**
```apdl
/POST1             ! 进入后处理
SET, LAST          ! 读取最后一步结果（关键！）
ESEL, S, TYPE, , 3 ! 选择Type 3单元（真实梁）
ETABLE, WJI, SMISC, 3   ! 弯矩 I端
ETABLE, WJJ, SMISC, 16  ! 弯矩 J端
ETABLE, ZLI, SMISC, 1   ! 轴力 I端
ETABLE, ZLJ, SMISC, 14  ! 轴力 J端
ETABLE, JLI, SMISC, 6   ! 剪力 I端
ETABLE, JLJ, SMISC, 19  ! 剪力 J端

PLLS, WJI, WJJ, -1      ! 绘制弯矩图
PRETAB, WJI, ZLI, JLI   ! 输出内力表格
```

**SMISC索引对应关系：**
- SMISC,1 = 轴力 I端
- SMISC,3 = 弯矩 I端
- SMISC,6 = 剪力 I端
- SMISC,14 = 轴力 J端
- SMISC,16 = 弯矩 J端
- SMISC,19 = 剪力 J端

### 常见问题与解决方案

| 问题 | 原因 | 解决方案 |
|------|------|--------|
| 圆弧几何警告 | 半径与点位精度不匹配 | 使用三点画弧，省略半径参数 |
| 网格划分失败 | 面定义不规则 | 确保四边形面，使用映射网格 |
| 内力结果为零 | 未读取求解结果 | 添加 `SET, LAST` 命令 |
| 弯矩突变 | 网格点不与拼缝对齐 | 按预制块分割创建关键点 |
| 刚度翻倍 | 实体和梁重复赋材料 | 虚拟梁用虚拟材料(E=1) |
| 自重计算错误 | 实体和梁都计算密度 | 虚拟梁密度设为0 |
| 水土压力分布异常 | Y坐标判断范围错误 | 精确定义Y_TOP和Y_BOT |
| B型预制块被分割 | 中间点作为分块点 | 仅用于画弧，不创建径向切割线 |

### APDL 代码生成规范

**编写APDL代码时必须遵循：**

1. **精度控制**：关键点坐标保留6位小数，避免几何警告
2. **注释规范**：每个阶段添加分隔注释，说明功能
3. **变量命名**：使用工程习惯命名（R_TOP, E_C, KS等）
4. **单位统一**：长度(m)、力(N)、压力(Pa)、密度(kg/m³)
5. **结构清晰**：按六阶段流程组织代码
6. **错误预防**：添加 `SET, LAST` 避免内力为零
7. **预制块原则**：A型块分割，B型块整体
8. **荷载精确**：使用循环算法施加非均匀压力

### 与配筋优化系统的集成

APDL计算的内力结果（弯矩、轴力、剪力）将作为输入传递给配筋优化系统：

```
APDL内力计算 → 荷载包络 → NSGA-II主筋优化 → 拉筋设计 → 分布筋设计 → 报告生成
```

确保APDL输出的内力单位与配筋优化系统的输入单位一致（N, N·m）。
