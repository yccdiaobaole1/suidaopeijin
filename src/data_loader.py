"""
数据加载工具 - 从 main_precast.py 提取，供外部脚本复用

用法:
    from src.data_loader import load_force_records, load_config
    records = load_force_records('force_records.csv')
    config = load_config('precast_config.json')
"""
import csv
import json
import os
from typing import Any, Dict, List, Optional


def _parse_float(value, default=None):
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if text == "":
        return default
    return float(text)


def load_force_records(path: str) -> List[Dict[str, Any]]:
    """
    加载内力数据文件 (CSV 或 JSON)，返回嵌套结构列表:
    [{'angle': float, 'design': {'N':, 'M':, 'V':}, 'quasi': {...}, 'gamma_d': float}, ...]
    """
    ext = os.path.splitext(path)[1].lower()
    if ext in ('.json', '.jsn'):
        with open(path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError('force json must be a list of records')
        return data

    if ext in ('.csv', '.txt'):
        records: List[Dict[str, Any]] = []
        with open(path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                angle = _parse_float(row.get('angle') or row.get('theta'))
                if angle is None:
                    continue
                design = {
                    'N': _parse_float(row.get('design_N')),
                    'M': _parse_float(row.get('design_M')),
                    'V': _parse_float(row.get('design_V'), 0.0)
                }
                quasi = {
                    'N': _parse_float(row.get('quasi_N')),
                    'M': _parse_float(row.get('quasi_M')),
                    'V': _parse_float(row.get('quasi_V'), 0.0)
                }
                if design['N'] is None or design['M'] is None or quasi['N'] is None or quasi['M'] is None:
                    raise ValueError('csv missing required columns: design_N, design_M, quasi_N, quasi_M')
                gamma_d = _parse_float(row.get('gamma_d'), 1.0)
                records.append({
                    'angle': angle,
                    'design': design,
                    'quasi': quasi,
                    'gamma_d': gamma_d
                })
        return records

    raise ValueError(f'unsupported force file format: {ext}')


def load_config(path: str) -> Dict[str, Any]:
    """加载配置 JSON 文件"""
    with open(path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError('config json must be an object')
    return data
