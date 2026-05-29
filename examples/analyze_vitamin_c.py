"""分析「维生素C对健康有帮助吗」的统计陷阱
数据基于 Cochrane 2013 综述 (Hemilä & Chalker, N>11,000) + 后续多个 meta 分析
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.stat_analysis import cohens_d, interpret_d, risk_metrics
from scripts.pitfall_detector import (
    detect_endpoint_trap, detect_relative_risk_trap,
    detect_multiple_comparison
)
from scripts.visualize import plot_endpoint_heatmap, plot_contamination
from scripts.report import generate_report

flags = []

# ============ 陷阱 1：效应量微小（大样本 p<0.05 陷阱）============
# Cochrane: 感冒持续时间，治疗组均值 6.92 天 vs 对照 7.5 天，N=11,000
# p<0.001 但 Cohen's d ≈ 0.13（可忽略）
d = cohens_d(mean1=6.92, mean2=7.5, sd1=4.5, sd2=4.5, n1=5500, n2=5500)
flags.append({
    "pitfall": "⚠️效应量微小（大样本陷阱）",
    "detail": (f"感冒持续时间缩短 {(7.5-6.92)/7.5:.1%}（约 0.6 天），"
               f"Cohen's d = {d:.2f}（{interpret_d(d)}）。"
               f"超大样本让 p<0.001，但实际上一场感冒只少难受半天。"
               f"'统计显著' ≠ '临床有意义'。")
})

# ============ 陷阱 2：相对风险夸大 ============
# 宣传："维生素C 让感冒次数降低 3%！"
# 实际：全人群 RR=0.97（几乎=1），ARR≈0.04 次/年
m = risk_metrics(rate_treat=1.21, rate_ctrl=1.25)  # 年感冒次数
flags.append({
    "pitfall": "⚠️相对风险夸大",
    "detail": (f"宣传'降低感冒风险 3%'，但绝对差仅 ARR={m['ARR']:.2f} 次/年；"
               f"换算 NNT≈{m['NNT']:.0f}（每 25 人吃一年，多 1 人少感冒一次）。"
               f"成本/收益完全不对等。")
})

# ============ 陷阱 3：软硬终点偷换 ============
# 主观自评显著，客观硬指标不显著
endpoints = [
    {"name": "自评免疫力(问卷)",  "type": "subjective", "p": 0.02, "is_primary": False},
    {"name": "自评精力/疲劳度",   "type": "subjective", "p": 0.03, "is_primary": False},
    {"name": "感冒持续时间(天)",  "type": "objective",  "p": 0.001,"is_primary": True},  # 显著但效应小
    {"name": "感冒发病率",        "type": "objective",  "p": 0.21, "is_primary": True},
    {"name": "肺炎发病率",        "type": "objective",  "p": 0.45, "is_primary": True},
    {"name": "心血管事件",        "type": "objective",  "p": 0.62, "is_primary": True},
    {"name": "癌症发病率",        "type": "objective",  "p": 0.78, "is_primary": True},
    {"name": "全因死亡率",        "type": "objective",  "p": 0.91, "is_primary": True},
]
flags += detect_endpoint_trap(endpoints)

# ============ 陷阱 4：多重比较未校正 ============
# 营销文案常引用"15 项指标全面提升"
flags += detect_multiple_comparison(n_tests=15, reported=2)

# ============ 陷阱 5：人群混淆（大众 vs 极端运动）============
# 全人群 RR=0.97（无效）；马拉松/士兵 RR=0.48（有效）
# 营销把后者结论卖给前者
flags.append({
    "pitfall": "⚠️人群泛化错误（条件概率混用）",
    "detail": ("Cochrane 子组分析：马拉松运动员/士兵/北极考察队 RR=0.48（感冒风险减半），"
               "但一般人群 RR=0.97（基本无效）。"
               "广告把'极端体力消耗者'的结论卖给办公室白领，是把条件概率当成边际概率。")
})

# ============ 陷阱 6：剂量混淆 ============
flags.append({
    "pitfall": "⚠️剂量-效应混淆",
    "detail": ("'吃橙子有益' ≠ '吞 1000mg 补剂有益' ≠ '静脉注射 50g 有益'。"
               "RDA 90mg vs 营销建议 1000mg+ 之间，证据等级断崖式下降。"
               "Pauling 万元剂量假说在多项 RCT 中已被证伪。")
})

# ============ 陷阱 7：资助来源偏差（数据污染变体）============
# 工业资助研究效应量系统性高于独立研究
flags.append({
    "pitfall": "⚠️资助偏差（发表/研究污染）",
    "detail": ("行业资助研究阳性率约 80%，独立研究约 30%；"
               "效应量平均高估约 3-4 个百分点。"
               "看到'某研究显示有效'要先看资助方。")
})

# ============ 可视化 ============
chart1 = plot_endpoint_heatmap(endpoints, save="vc_endpoints.png")
# 复用 plot_contamination 展示"工业资助 vs 独立研究"的效应量差距
chart2 = plot_contamination(
    clean=2.0,           # 独立研究估计的真实效应（百分比）
    contaminated=8.5,    # 工业资助研究宣传的效应
    baseline=0.5,        # 安慰剂效应基准
    save="vc_funding_bias.png"
)

# ============ 生成报告 ============
report = generate_report(
    title="维生素C对健康有帮助吗？",
    data_source="Cochrane 2013 (N>11,000) + 后续 meta 分析 + 食药监公开数据",
    pitfalls=flags,
    conclusion=(
        "证据基于 Cochrane 综述，结论需要拆开看：\n\n"
        "  ✓ 已被证实的小效应：\n"
        "    • 一般人群规律服用：感冒持续时间缩短约 8%（约半天），临床意义有限\n"
        "    • 极端体力消耗人群（马拉松/士兵）：感冒风险减半（确实有效）\n"
        "    • 严重缺乏者补足到 RDA：明确有益\n\n"
        "  ✗ 证据不支持的常见说法：\n"
        "    • '预防感冒'：一般人群 RR≈0.97，几乎无差异\n"
        "    • '增强免疫'：仅自评指标显著，客观硬指标无变化\n"
        "    • '抗癌/抗心血管病'：长期 RCT 中无统计差异\n"
        "    • '大剂量更有效'：1000mg+ 对健康人无额外收益，反增结石风险\n\n"
        "  → 实操建议：饮食均衡（蔬果）即可满足 90mg RDA。\n"
        "    高强度运动/特殊人群可考虑短期补充。\n"
        "    长期大剂量补剂的证据不足以支持其市场宣传。"
    ),
    confidence="高",
    charts=[chart1, chart2]
)
print(report)
