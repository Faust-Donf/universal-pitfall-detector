"""案例：低学历创业成功 → 幸存者偏差检测"""
from scripts.causal_check import detect_survivorship
from scripts.visualize import plot_survivorship_iceberg
from scripts.report import generate_report

# 用户观察到的"成功案例"
observed_success = 5
flag = detect_survivorship("看到5个低学历创业富翁", observed_success, est_fail_ratio=20)

chart = plot_survivorship_iceberg(visible=5, hidden=100)

report = generate_report(
    title="低学历也能创业成功？",
    data_source="用户观察 + 联网检索创业失败率(>80%)",
    pitfalls=[flag],
    conclusion=("你只看到了被'死亡筛选'后的幸存者。真实创业成功率约15-20%，"
                "用成功个例估算概率会严重高估。理性决策应基于总体基率。"),
    confidence="高",
    charts=[chart]
)
print(report)
