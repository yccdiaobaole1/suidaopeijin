import json
import os


class ConcreteManager:
    def __init__(self, json_path=None):
        """
        初始化混凝土管理器
        """
        if json_path is None:
            # 自动寻找 data 目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            json_path = os.path.join(project_root, 'data', 'concrete_data.json')

        if not os.path.exists(json_path):
            raise FileNotFoundError(f"❌ 找不到混凝土数据文件: {json_path} (请运行 generate_concrete_data.py)")

        with open(json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def get_concrete(self, grade):
        """
        获取指定等级混凝土的所有参数
        :param grade: 如 'C30', 'C50'
        :return: 包含 fc, ft, Ec 等的字典
        """
        grade = grade.upper()  # 容错处理 (c30 -> C30)
        if grade not in self.data:
            raise ValueError(f"未知的混凝土等级: {grade} (支持 C15-C80)")
        return self.data[grade]

    def get_fc(self, grade):
        """获取轴心抗压强度设计值 (承载力计算用)"""
        return self.get_concrete(grade)['fc']

    def get_ft(self, grade):
        """获取轴心抗拉强度设计值 (抗裂验算用)"""
        return self.get_concrete(grade)['ft']

    def get_ftk(self, grade):
        """获取轴心抗拉强度标准值 (裂缝公式相关系数用)"""
        return self.get_concrete(grade)['ftk']

    def get_Ec(self, grade):
        """获取弹性模量 (MPa)"""
        return self.get_concrete(grade)['Ec']


