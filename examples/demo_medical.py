"""案例：连花清瘟式临床试验 → 软硬终点偷换 + 相对风险夸大"""
from scripts.pitfall_detector import detect_endpoint_trap, detect_relative_risk_trap
from scripts.visualize import plot_endpoint_heatmap
from scripts.report import generate_report

# 多个终点的检验结果（主观显著、客观不显著 → 偷换嫌疑）
endpoints = [
    {"name": "症状自评(发热/咳嗽)", "type": "subjective", "p": 0.02, "is_primary": False},
    {"name": "症状缓解时间(自述)",   "type": "subjective", "p": 0.04, "is_primary": False},
    {"name": "重症转化率",           "type": "objective",  "p": 0.31, "is_primary": True},
    {"name": "住院时间",             "type": "objective",  "p": 0.42, "is_primary": True},
    {"name": "死亡率",               "type": "objective",  "p": 0.88, "is_primary": True},
]

flags = []
flags += detect_endpoint_trap(endpoints)
# 假设宣传"症状改善率提升30%"，实际绝对差只有2%
flags += detect_relative_risk_trap(rate_treat=0.05, rate_ctrl=0.07, p_value=0.04)

chart = plot_endpoint_heatmap(endpoints)

report = generate_report(
    title="某中成药对新冠是否真的有效？",
    data_source="某 RCT 临床试验报告（开放标签）",
    pitfalls=flags,
    conclusion=("主观终点显著但客观硬终点全部不显著，宣传口径放大了相对值。"
                "高度怀疑安慰剂效应 + 软硬终点偷换 + 相对风险夸大组合。"
                "建议读者关注主要硬终点（重症/死亡）。"),
    confidence="高",
    charts=[chart]
)
print(report)
