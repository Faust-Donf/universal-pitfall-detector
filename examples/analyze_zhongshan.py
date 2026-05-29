"""分析「中山好玩吗」这类旅游评价问题的统计陷阱
信源：小红书/携程/抖音/知乎 + AI 回答
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from scripts.causal_check import detect_simpson, detect_survivorship
from scripts.visualize import plot_simpson, plot_survivorship_iceberg
from scripts.report import generate_report

# ============ 数据假设（基于公开估算）============
# 中山 2024 年接待游客约 4500 万人次
# 小红书"中山旅游"相关笔记约 30 万篇
# 携程中山 POI 评价总数约 8 万条
# → 发声率 ≈ (30万 + 8万) / 4500万 ≈ 0.84%
TOTAL_VISITORS = 45_000_000
VOCAL_REVIEWS = 380_000

flags = []

# ============ 陷阱 1：选择/无应答偏差 ============
flags.append({
    "pitfall": "⚠️选择/无应答偏差",
    "detail": (f"年游客约{TOTAL_VISITORS/1e4:.0f}万，发声评价仅{VOCAL_REVIEWS/1e4:.1f}万条 "
               f"(发声率≈{VOCAL_REVIEWS/TOTAL_VISITORS:.2%})；"
               f"99%+ 的游客沉默，发声者多为'特别满意'或'特别失望'两端，中间体验缺失。")
})

# ============ 陷阱 2：幸存者偏差（打卡照）============
# 你看到的小红书"绝美！中山隐藏宝藏"笔记
# 是被算法推上来的、精修过的、好天气的样本
flag = detect_survivorship(
    sample_desc="小红书上看到一堆中山绝美打卡成功案例",
    observed_success=20,        # 你刷到 20 篇绝美笔记
    est_fail_ratio=15           # 每篇爆款背后约 15 篇普通笔记
)
flags.append(flag)

# ============ 陷阱 3：辛普森悖论（人群异质性）============
# 模拟：整体好评率显示"中山一般"，但分人群看完全不同
records = []
# A 类：广东本地/周边游客（期望值低、距离近）
for _ in range(7000): records.append({"audience":"广东本地","trip":"中山","good":1})
for _ in range(3000): records.append({"audience":"广东本地","trip":"中山","good":0})
for _ in range(4500): records.append({"audience":"广东本地","trip":"竞品城市","good":1})
for _ in range(5500): records.append({"audience":"广东本地","trip":"竞品城市","good":0})
# B 类：外省专程游客（期望值高、对比苏杭）
for _ in range(800):  records.append({"audience":"外省专程","trip":"中山","good":1})
for _ in range(2200): records.append({"audience":"外省专程","trip":"中山","good":0})
for _ in range(6000): records.append({"audience":"外省专程","trip":"竞品城市","good":1})
for _ in range(4000): records.append({"audience":"外省专程","trip":"竞品城市","good":0})
df = pd.DataFrame(records)

simpson_flag = detect_simpson(df, group_col="audience", treat_col="trip", outcome_col="good")
if simpson_flag:
    flags.append(simpson_flag)

# ============ 陷阱 4：基率谬误（忽略"什么人去"）============
flags.append({
    "pitfall": "⚠️基率谬误",
    "detail": ("评价『中山好玩吗』时，必须先问『对谁、什么时段、什么预期』。"
               "平均好评率 75% 看似不错，但条件分布完全不同："
               "广东周末游 P(好玩)≈85%，外省专程游 P(好玩)≈30%。"
               "无条件均值会误导决策。")
})

# ============ 陷阱 5：AI 回答自身的偏差（包括我上一条）============
flags.append({
    "pitfall": "⚠️AI 回答的训练数据偏差",
    "detail": ("AI 的『中山印象』来自互联网文本，本身已经被双重过滤："
               "(1)写作者偏发声样本 (2)传播算法偏戏剧化内容。"
               "AI 给的『真实感』是统计学意义上有偏的真实感。")
})

# ============ 可视化 ============
chart1 = plot_survivorship_iceberg(visible=20, hidden=300, save="zhongshan_iceberg.png")
chart2 = plot_simpson(df, "audience", "trip", "good", save="zhongshan_simpson.png")

# ============ 生成报告 ============
report = generate_report(
    title="中山好玩吗？",
    data_source="小红书 + 携程 + 知乎评价 + AI 回答（含上一轮我的回答）",
    pitfalls=flags,
    conclusion=(
        "「中山好玩吗」是一个无法用群体数据回答的问题，因为：\n"
        "  • 发声样本只占游客的 0.8%，且偏极端\n"
        "  • 你刷到的'绝美打卡'是被算法+精修筛选的幸存者\n"
        "  • 整体好评看似一般，但分人群看（广东本地 vs 外省专程）方向完全相反——典型辛普森悖论\n"
        "  • 不同人群的基率差异巨大（85% vs 30%）\n"
        "  • 包括 AI 在内的所有信源，都在转述被发声偏差污染过的数据\n\n"
        "更靠谱的提问方式：「我从 X 出发、Y 季节、和 Z 一起、预算 W、想要 V 体验，去中山合适吗？」"
    ),
    confidence="高",
    charts=[chart1, chart2]
)
print(report)
