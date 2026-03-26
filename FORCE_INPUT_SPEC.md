# ForceMapper 输入格式说明

文档日期: 2026-02-21

## 角度约定
- 角度单位为度(°)。
- **输入数据坐标系**: 0° 在拱底中心(仰拱底部)，90° 在右侧拱脚，180° 在拱顶，270° 在左侧拱脚。
- 角度按逆时针方向增加。
- 注: 此定义与ANSYS APDL输出的角度系统一致(从拱底开始逆时针)。
- **内部处理**: 系统会自动将输入角度转换为内部坐标系进行计算，用户无需关心转换细节。

## 单位约定
- 轴力 N: kN
- 弯矩 M: kN·m
- 剪力 V: kN (可选)

## 格式 A: 已组合内力(默认/推荐)
每个角度点直接给出 design 与 quasi。

```json
[
  {
    "angle": 0,
    "design": {"N": 2000, "M": 400, "V": 200},
    "quasi": {"N": 1800, "M": 300, "V": 150},
    "gamma_d": 1.0
  },
  {
    "angle": 10,
    "design": {"N": 2100, "M": 420},
    "quasi": {"N": 1850, "M": 310}
  }
]
```

## 格式 B: 标准内力分量
每个角度点提供标准值分量，由系统按规范组合为 design 与 quasi。

```json
[
  {
    "angle": 0,
    "components": {
      "self_weight": {"N": 500, "M": 50, "V": 20},
      "earth_pressure": {"N": 2000, "M": 300, "V": 80},
      "live_load": {"N": 100, "M": 30, "V": 10}
    },
    "gamma_d": 1.0
  }
]
```

## 输出说明
`ForceMapper.map_segments(...)` 返回结构如下:

```json
{
  "A1": [
    {"design": {"N": 2000, "M": 400, "V": 200}, "quasi": {"N": 1800, "M": 300, "V": 150}, "gamma_d": 1.0},
    {"design": {"N": 2100, "M": 420, "V": 210}, "quasi": {"N": 1850, "M": 310, "V": 155}, "gamma_d": 1.0}
  ],
  "C1": [
    {"design": {"N": 1900, "M": 380, "V": 180}, "quasi": {"N": 1700, "M": 280, "V": 140}, "gamma_d": 1.0}
  ]
}
```

## 对称性设计
如需同类型分块采用同一配筋（对称、便捷施工），使用:

```python
result = mapper.map_segments_symmetric(segments, records, mode="all")
segment_forces = result["symmetric"]   # 同类型取内力最大块
source = result["type_source"]         # 记录每个类型选中的代表块
```

## CLI 示例 (main_precast.py)

```bash
python main_precast.py --config precast_config.example.json --force-file force_records.json
```

## CSV 模板
仓库已提供 `force_records.example.csv`，字段如下:

```
angle,design_N,design_M,design_V,quasi_N,quasi_M,quasi_V,gamma_d
```

## 配置治理（T-3.4-01）
`precast_config` 支持可追溯的条文参数治理：

```json
"code_governance": {
  "project_defaults": {
    "shear_use_abs_vm": true,
    "lambda_min": 1.5,
    "lambda_max": 3.0,
    "h_w_source": "h0",
    "shear_n_mode": "compression_only",
    "gamma_d_shear": 1.0,
    "rho_sv_min_hpb300": 0.0014,
    "rho_sv_min_hrb400": 0.0011
  },
  "locked_params": ["shear_use_abs_vm", "lambda_min", "lambda_max", "h_w_source", "shear_n_mode", "gamma_d_shear"],
  "change_approvals": [
    {
      "param": "lambda_max",
      "approved": true,
      "approved_by": "chief_engineer",
      "date": "2026-02-22",
      "ticket": "DESIGN-123",
      "reason": "Project-specific calibrated lambda upper bound"
    }
  ]
}
```

规则：
- 若 `section` 中某锁定参数偏离默认值，且无 `change_approvals` 批准记录，系统会回退到默认值并在报表中标注 `locked_default`。
- 报表会输出参数来源（`project_default/config_override/approved_override/locked_default`）和配置指纹（SHA256），用于复现与追溯。

## 报表输出
默认输出:
- `report.md` (Markdown)
- `report.csv` (可直接用 Excel 打开)

可通过参数修改:

```bash
python main_precast.py --config precast_config.example.json --force-file force_records.json --report-md out.md --report-csv out.csv
```

如需 xlsx（需要 `openpyxl`）:

```bash
python main_precast.py --config precast_config.example.json --force-file force_records.json --report-xlsx out.xlsx
```

## 备注
- 默认输入应为已组合内力（`design/quasi`）；如需自动组合请按“格式 B”。  
- `mode="all"` 返回分块内的全部角度点（默认）。
- `mode="extreme"` 仅保留设计与准永久的 N/M 极值点，可降低计算量。
- 角度数据越密，优化精度越高。
