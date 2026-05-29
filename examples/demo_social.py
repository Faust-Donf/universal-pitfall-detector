"""案例：社交媒体差评 → 选择偏差 + 辛普森悖论"""
import pandas as pd
from scripts.causal_check import detect_simpson
from scripts.visualize import plot_simpson
from scripts.report import generate_report

# 模拟数据：A/B 两款产品在不同用户群上的好评率
records = []
# 重度用户：B 更好
for _ in range(800): records.append({"product": "A", "user_type": "重度", "good": 1})
for _ in range(200): records.append({"product": "A", "user_type": "重度", "good": 0})
for _ in range(900): records.append({"product": "B", "user_type": "重度", "good": 1})
for _ in range(100): records.append({"product": "B", "user_type": "重度", "good": 0})
# 轻度用户：B 更好
for _ in range(100): records.append({"product": "A", "user_type": "轻度", "good": 1})
for _ in range(900): records.append({"product": "A", "user_type": "轻度", "good": 0})
for _ in range(20):  records.append({"product": "B", "user_type": "轻度", "good": 1})
for _ in range(180): records.append({"product": "B", "user_type": "轻度", "good": 0})
# 但整体：A 的"重度用户占比高"导致 A 看起来更好

df = pd.DataFrame(records)

flag = detect_simpson(df, group_col="user_type", treat_col="product", outcome_col="good")
flags = [flag] if flag else []

# 选择偏差：发声样本比例
flags.append({
    "pitfall": "⚠️选择/无应答偏差",
    "detail": "评论区好评率 90%，但实际购买后评价率仅 15%；85% 的沉默用户口碑未知。"
})

chart = plot_simpson(df, "user_type", "product", "good")

report = generate_report(
    title="网友都说 A 比 B 好用？",
    data_source="社交媒体抓取 2 万条评论 + 销量数据",
    pitfalls=flags,
    conclusion=("分组看 B 在两类用户上都更优，整体看 A 占优是因为用户群分布不同（辛普森悖论）。"
                "且只有极端体验者发声，沉默样本（85%）口碑未知。"
                "'网友都说 A 好'不能作为决策依据。"),
    confidence="中",
    charts=[chart]
)
print(report)
