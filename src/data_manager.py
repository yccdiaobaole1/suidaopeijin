import json
import random
import os


class RockParameterManager:
    def __init__(self, json_path=None):
        """
        初始化围岩参数管理器
        """
        # 自动定位策略：无论在哪个目录下运行，都能找到 data/rock_parameters.json
        if json_path is None:
            # 获取当前脚本(data_manager.py)所在的目录 -> src/
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 获取项目根目录 (src 的上一级) -> 铁路明洞装配式衬砌配筋/
            project_root = os.path.dirname(current_dir)
            # 拼接出 JSON 文件的绝对路径-
            json_path = os.path.join(project_root, 'data', 'rock_parameters.json')

        # 检查文件是否存在
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"找不到围岩参数文件，请检查路径: {json_path}")

        with open(json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def get_params(self, grade, strategy='average'):
        """
        根据策略获取具体的数值参数
        :param grade: 围岩等级 key，如 'IV_1'
        :param strategy:
            'average' (平均值 - 推荐用于一般计算)
            'conservative' (保守值 - 结构设计推荐，取最不利情况)
            'random' (随机值 - 推荐用于随机森林数据生成)
        :return: 包含具体数值的字典
        """
        if grade not in self.data:
            # 打印出所有可用的 key，方便调试
            available_keys = ", ".join(self.data.keys())
            raise ValueError(f"未找到围岩等级: {grade}。可用的等级有: {available_keys}")

        raw = self.data[grade]
        result = {}

        # 定义每个参数的"保守"方向
        # K值越小越不利（围岩约束弱），重度越大越不利（荷载大）
        conservative_rules = {
            'unit_weight': max,  # 取大值
            'elastic_k': min,  # 取小值
            'elastic_modulus': min,  # 取小值
            'poisson_ratio': max,  # 泊松比越大侧压力通常越大
            'friction_angle': min,  # 取小值
            'cohesion': min  # 取小值
        }

        for key, value_range in raw.items():
            if key == 'description':
                continue

            min_v, max_v = value_range[0], value_range[1]

            if strategy == 'average':
                result[key] = (min_v + max_v) / 2.0
            elif strategy == 'random':
                result[key] = random.uniform(min_v, max_v)
            elif strategy == 'conservative':
                # 根据物理意义取最不利值
                rule = conservative_rules.get(key, min)
                result[key] = rule(value_range)

        return result


