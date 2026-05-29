"""案例：大模型评测刷分 → 数据污染 + 多重比较未校正"""
from scripts.pitfall_detector import detect_contamination, detect_multiple_comparison
from scripts.visualize import plot_contamination
from scripts.report import generate_report

# 同一模型在 含训练污染的测试集 vs 干净的全新测试集 上的得分
contaminated_score = 87.5   # 公开榜单
clean_score        = 71.2   # 重新构造的同分布测试集
baseline           = 73.0   # 一个未刷榜的对照模型

flags = []
flags += detect_contamination(clean_score, contaminated_score, threshold=5)
# 论文报告：测了 12 个 benchmark，只挑 3 个亮眼的展示
flags += detect_multiple_comparison(n_tests=12, reported=3)

chart = plot_contamination(clean_score, contaminated_score, baseline)

report = generate_report(
    title="大模型 X 在 BenchY 上超过 GPT-4？",
    data_source="官方榜单分数 + 复现实验",
    pitfalls=flags,
    conclusion=("污染集分数比干净集高 16+ 分，且对照模型在干净集上反而更高，"
                "强烈提示训练数据泄露。再叠加 12 个指标中挑 3 个汇报，"
                "应以 Bonferroni 校正后的阈值（0.05/12≈0.004）重新评估显著性。"
                "宣传分不能代表真实能力。"),
    confidence="高",
    charts=[chart]
)
print(report)
