import json
import os


class RebarManager:
    def __init__(self, json_path=None):
        """
        初始化钢筋管理器，自动加载 data/rebar_data.json
        """
        if json_path is None:
            # 自动向上寻找 data 目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            json_path = os.path.join(project_root, 'data', 'rebar_data.json')

        if not os.path.exists(json_path):
            raise FileNotFoundError(f"❌ 找不到钢筋数据文件: {json_path}")

        with open(json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        self.pricing = self.data.get('pricing', {})
        self.pricing_rules = self.pricing.get('rules', [])

    def get_design_value(self, grade):
        """
        获取抗拉强度设计值 fy
        支持 HRB400E 自动映射到 HRB400
        """
        if grade in self.data['strengths']:
            return self.data['strengths'][grade]['fy']

        # 尝试去掉 'E' 后查找
        base_grade = grade.replace('E', '')
        if base_grade in self.data['strengths']:
            return self.data['strengths'][base_grade]['fy']

        raise ValueError(f"未知的钢筋牌号: {grade}")

    def get_standard_value(self, grade):
        """获取屈服强度标准值 fyk"""
        if grade in self.data['strengths']:
            return self.data['strengths'][grade]['fyk']
        return self.data['strengths'][grade.replace('E', '')]['fyk']

    def get_bar_properties(self, diameter):
        """获取几何属性 (面积、重量)"""
        # 尝试字符串匹配
        d_key = str(diameter)
        if d_key in self.data['specs']:
            return self.data['specs'][d_key]

        # 尝试整数匹配 (防止传入 25.0 找不到 "25")
        try:
            d_int_key = str(int(float(diameter)))
            if d_int_key in self.data['specs']:
                return self.data['specs'][d_int_key]
        except:
            pass

        raise ValueError(f"库中没有直径为 {diameter}mm 的钢筋数据")

    def get_Es(self, grade):
        """获取钢筋弹性模量 Es (MPa)，用于裂缝计算"""
        # 优先查直接匹配的牌号
        if grade in self.data['strengths']:
            return self.data['strengths'][grade]['Es']
        # 查不到则尝试去掉 'E' (如 HRB400E -> HRB400)
        base = grade.replace('E', '')
        if base in self.data['strengths']:
            return self.data['strengths'][base]['Es']
        raise ValueError(f"缺少弹性模量数据: {grade}")

    def get_nu(self, grade):
        """获取相对黏结特性系数 nu，用于裂缝计算"""
        if grade in self.data['strengths']:
            return self.data['strengths'][grade]['nu']
        base = grade.replace('E', '')
        if base in self.data['strengths']:
            return self.data['strengths'][base]['nu']
        raise ValueError(f"缺少黏结系数数据: {grade}")

    def get_price(self, grade, diameter):
        """
        【智能定价核心】
        根据牌号和直径，遍历规则库匹配最精准的市场价
        """
        target_price = None
        d_val = float(diameter)

        # 归一化查找牌号 (HRB400E -> HRB400)
        search_grade = grade.replace('E', '')

        # 判断是否为盘螺范围 (通常 <=10mm 的螺纹钢视为盘螺)
        # 这里为了简化，仅通过直径和牌号去匹配 JSON 中的规则

        for rule in self.pricing_rules:
            # 1. 牌号匹配 (模糊包含，如规则 HRB400 匹配 HRB400)
            if rule['grade'] in search_grade:
                # 2. 直径范围匹配
                if rule['min_d'] <= d_val <= rule['max_d']:
                    # 3. 优先匹配 (在JSON中顺序很重要，特殊的放前面)
                    # 如果有 is_coiled 标记，且直径小，通常指盘螺，这里简化处理，直接取价格
                    target_price = rule['price']
                    break

                    # 兜底逻辑
        if target_price is None:
            # 如果是 HRB500 但没匹配到规则，尝试找 HRB400 的价格 + 差价
            if "500" in search_grade:
                base_price = self.get_price("HRB400", diameter)
                return base_price + 300  # 估算差价

            target_price = self.pricing.get('default_price', 3450)

        return target_price

    def calculate_cost(self, diameter, total_length_m, grade='HRB400'):
        """
        计算总造价 (元)
        """
        props = self.get_bar_properties(diameter)
        weight_per_m = props['weight']

        # 获取智能单价
        price_per_ton = self.get_price(grade, diameter)

        total_weight_ton = (weight_per_m * total_length_m) / 1000.0
        return total_weight_ton * price_per_ton

