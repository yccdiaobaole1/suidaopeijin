"""配筋优化报告生成模块"""
from typing import Dict, List
from datetime import datetime


class ReportGenerator:
    """生成配筋优化报告（Markdown格式）"""

    @staticmethod
    def generate_report(optimization_result: Dict, output_path: str = None) -> str:
        """生成优化报告

        Args:
            optimization_result: 优化结果字典
            output_path: 输出文件路径（可选）

        Returns:
            报告内容（Markdown格式）
        """
        lines = []
        lines.append("# 隧道衬砌配筋优化报告\n")
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        lines.append("---\n")

        # 1. 主筋方案
        if 'main_rebar' in optimization_result:
            lines.append("## 1. 主筋配筋方案\n")
            main = optimization_result['main_rebar']
            lines.append(f"- **钢筋等级**: {main.get('grade', 'N/A')}")
            lines.append(f"- **钢筋直径**: {main.get('diameter', 'N/A')} mm")
            lines.append(f"- **钢筋间距**: {main.get('spacing', 'N/A')} mm")
            lines.append(f"- **钢筋根数**: {main.get('count', 'N/A')} 根")
            lines.append(f"- **配筋面积**: {main.get('area', 'N/A'):.0f} mm²")
            lines.append(f"- **成本**: {optimization_result.get('cost', 'N/A'):.2f} 元/m\n")

        # 2. 拉筋方案
        if 'stirrup' in optimization_result and optimization_result['stirrup']:
            lines.append("## 2. 拉筋配筋方案\n")
            stirrup = optimization_result['stirrup']
            lines.append(f"- **钢筋等级**: {stirrup.get('grade', 'N/A')}")
            lines.append(f"- **钢筋直径**: {stirrup.get('diameter', 'N/A')} mm")
            lines.append(f"- **拉筋间距**: {stirrup.get('spacing', 'N/A')} mm")
            lines.append(f"- **拉筋肢数**: {stirrup.get('legs', 'N/A')} 肢\n")

        # 3. 分布筋方案
        if 'dist_rebar' in optimization_result and optimization_result['dist_rebar']:
            lines.append("## 3. 分布筋配筋方案\n")
            dist = optimization_result['dist_rebar']
            lines.append(f"- **钢筋直径**: {dist.get('diameter', 'N/A')} mm")
            lines.append(f"- **钢筋间距**: {dist.get('spacing', 'N/A')} mm")
            lines.append(f"- **配筋面积**: {dist.get('area_provided', 'N/A'):.0f} mm²\n")

        # 4. 验算结果
        if 'verification' in optimization_result:
            lines.append("## 4. 承载力验算结果\n")
            verif = optimization_result['verification']
            lines.append(f"- **承载力安全**: {'✓ 通过' if verif.get('is_safe', False) else '✗ 不通过'}")
            lines.append(f"- **安全系数**: {verif.get('safety_factor', 'N/A'):.2f}")
            lines.append(f"- **裂缝宽度**: {verif.get('crack_width', 'N/A'):.3f} mm\n")

        # 5. 帕累托前沿
        if 'pareto_front' in optimization_result:
            pareto = optimization_result['pareto_front']
            if isinstance(pareto, list) and len(pareto) > 0:
                lines.append(f"## 5. 帕累托前沿方案\n")
                lines.append(f"**共 {len(pareto)} 个非支配解**\n")
                lines.append("| 序号 | 成本(元/m) | 裂缝(mm) | 间距(mm) |")
                lines.append("|------|-----------|---------|---------|")
                for i, sol in enumerate(pareto[:10], 1):
                    cost = sol.get('cost', 0)
                    crack = sol.get('crack_width', 0)
                    spacing = sol.get('spacing', 0)
                    lines.append(f"| {i} | {cost:.2f} | {crack:.3f} | {spacing} |")
                lines.append("")

        # 6. 图表
        if 'pareto_plot' in optimization_result:
            plots = optimization_result['pareto_plot']
            if isinstance(plots, list):
                lines.append("## 6. 优化图表\n")
                for plot in plots:
                    lines.append(f"- [{plot}]({plot})")
                lines.append("")

        report_content = "\n".join(lines)

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)

        return report_content
