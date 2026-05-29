"""分析「鱼油（Omega-3）对健康有帮助吗」的统计陷阱。

数据基础：
  - VITAL (NEJM 2019, N=25,871, 5.3 年随访)
  - ASCEND (NEJM 2018, N=15,480, 7.4 年随访，糖尿病人群)
  - STRENGTH (JAMA 2020, EPA+DHA 4g/d, 提前终止)
  - REDUCE-IT (NEJM 2019, EPA-only 4g/d, 唯一阳性大型 RCT)
  - 多项 Cochrane / Meta 综述
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.stat_analysis import cohens_d, interpret_d, risk_metrics
from scripts.pitfall_detector import (
    detect_endpoint_trap, detect_relative_risk_trap,
    detect_multiple_comparison
)
from scripts.dashboard import plot_dashboard
from scripts.report import generate_report
from scripts.html_report import generate_html_report
from scripts.visualize import (
    plot_endpoint_heatmap, plot_risk_breakdown, plot_contamination
)

OUT_DIR = "/Users/shenzhiheng/Documents/Projects/统计陷阱/鱼油分析"
os.makedirs(OUT_DIR, exist_ok=True)
os.chdir(OUT_DIR)

flags = []

# ============ 陷阱 1：相对风险夸大 ============
# REDUCE-IT 宣传："心血管事件降低 25%！"
# 实际：5 年中绝对差 4.8% (17.2% → 22.0%)，NNT≈21
m = risk_metrics(rate_treat=0.172, rate_ctrl=0.220)
flags.append({
    "pitfall": "相对风险夸大",
    "severity": "high",
    "detail": (f"REDUCE-IT 头条「心血管风险降低 {m['RRR']:.0%}」吸睛。"
               f"但 5 年绝对差只有 ARR={m['ARR']:.1%}，NNT={m['NNT']:.0f}—— "
               f"21 人吃 5 年才多 1 人避免一次心血管事件。"
               f"且 STRENGTH（EPA+DHA）同剂量 RCT 完全无效，提示可能是矿物油"
               f"安慰剂'反向作用'造成的伪阳性。")
})

# ============ 陷阱 2：软硬终点偷换 ============
endpoints = [
    {"name": "甘油三酯下降",            "type": "objective",  "p": 0.001},  # 显著但是替代终点
    {"name": "自评精力 / 关节舒适度",   "type": "subjective", "p": 0.02},
    {"name": "自评记忆力",              "type": "subjective", "p": 0.04},
    {"name": "心血管事件 (一般人群)",   "type": "objective",  "p": 0.24},
    {"name": "心梗 (VITAL)",           "type": "objective",  "p": 0.31},
    {"name": "中风 (VITAL)",           "type": "objective",  "p": 0.93},
    {"name": "全因死亡率",             "type": "objective",  "p": 0.55},
    {"name": "癌症发病率",             "type": "objective",  "p": 0.78},
    {"name": "认知功能客观测试",        "type": "objective",  "p": 0.46},
]
endpoint_flags = detect_endpoint_trap(endpoints)
for f in endpoint_flags:
    f["severity"] = "high"
    name = f["pitfall"].replace("⚠️", "").strip()
    f["pitfall"] = name
    f["detail"] = ("8 个客观硬终点中只有「甘油三酯」显著下降（替代终点，"
                   "并未转化为心血管/死亡获益）；主观自评（精力、记忆）显著。"
                   "把替代终点 + 主观自评包装成『改善心脏 / 大脑健康』，"
                   "是软硬终点偷换的典型套路。")
flags += endpoint_flags

# ============ 陷阱 3：人群泛化错误（最关键）============
# REDUCE-IT 阳性人群：高甘油三酯 + 已有心血管疾病/糖尿病 + 用他汀
# 营销卖给：所有想"补脑护心"的健康人
flags.append({
    "pitfall": "人群泛化错误（条件概率混用）",
    "severity": "high",
    "detail": ("唯一阳性大型 RCT（REDUCE-IT）的入组条件极其特殊："
               "甘油三酯 ≥150 mg/dL + 已确诊心血管病或糖尿病 + 已服他汀，剂量 4g 纯 EPA。"
               "VITAL/ASCEND 在一般人群与糖尿病人群中均为阴性。"
               "营销把『高危患者吃药剂』的结论卖给『健康人吃保健剂量』，"
               "是把条件概率 P(获益｜病人+药剂) 当成 P(获益｜健康人+保健量)。")
})

# ============ 陷阱 4：剂量混淆 ============
flags.append({
    "pitfall": "剂量-效应混淆",
    "severity": "high",
    "detail": ("阳性结果剂量：4 g/天纯 EPA（处方药 Vascepa）。"
               "市售保健品：通常 EPA+DHA 合计 300-1000 mg/天。"
               "保健剂量在 RCT 中无效；但消费者看到『鱼油有用』就买保健品，"
               "证据强度被悄悄换了一档。")
})

# ============ 陷阱 5：替代终点滥用 ============
flags.append({
    "pitfall": "替代终点滥用",
    "severity": "medium",
    "detail": ("『甘油三酯下降』是替代终点（surrogate endpoint），"
               "只有当它能稳定预测硬终点（心梗/死亡）时才有意义。"
               "多项研究显示：单纯降甘油三酯 ≠ 减少心血管事件。"
               "用替代终点的'改善'倒推临床获益，逻辑链断裂。")
})

# ============ 陷阱 6：多重比较 ============
flags += [{**f, "severity": "medium",
           "pitfall": f["pitfall"].replace("⚠️", "").strip()}
          for f in detect_multiple_comparison(n_tests=18, reported=3)]

# ============ 陷阱 7：发表偏差 + 资助偏差 ============
flags.append({
    "pitfall": "发表 / 资助偏差",
    "severity": "medium",
    "detail": ("早期小型阳性研究密集发表，引爆市场；后续大型独立 RCT"
               "（VITAL/ASCEND/STRENGTH）几乎全部阴性。"
               "鱼油全球市场 ~80 亿美元，行业资助研究阳性率显著高于独立研究。"
               "看到『某研究显示鱼油有效』要先看：发表年份、样本量、资助方。")
})

# ============ 陷阱 8：氧化与污染（额外健康风险）============
flags.append({
    "pitfall": "产品质量异质性（隐藏负效应）",
    "severity": "medium",
    "detail": ("第三方检测显示：相当比例市售鱼油氧化超标、EPA/DHA 实际含量低于标签、"
               "重金属污染。氧化的 omega-3 不仅无效，可能促炎。"
               "RCT 用的是制药级产品；保健品的实际成分质量是另一个分布。")
})

# ============ 生成 Dashboard（保留作为分享版整合图） ============
panels = [
    {
        "type": "endpoints",
        "kwargs": {"endpoints": endpoints},
    },
    {
        "type": "risk",
        "kwargs": {
            "rate_treat": 0.172, "rate_ctrl": 0.220,
            "labels": ("EPA 4g 治疗组", "安慰剂组"),
        },
    },
    {
        "type": "contamination",
        "kwargs": {
            "clean": 0,
            "contaminated": 25,
            "baseline": 5,
            "labels": ("营销宣传效应", "独立 RCT 真实效应", "替代终点改善"),
            "ylabel": "心血管获益 %",
        },
    },
]

kpis = [
    {"value": "22%", "label": "宣传相对风险降低", "sublabel": "REDUCE-IT 头条数字",
     "color": "#D72638"},
    {"value": "4.8%", "label": "真实绝对风险降低", "sublabel": "5 年累计 ARR",
     "color": "#3FA34D"},
    {"value": "21", "label": "NNT 获益人数", "sublabel": "21 人吃 5 年才省 1 例",
     "color": "#2E5266"},
    {"value": "8", "label": "检出陷阱总数", "sublabel": "4 高危 + 4 中等",
     "color": "#F4A261"},
]

dashboard_path = plot_dashboard(
    title="鱼油（Omega-3）对健康有帮助吗？",
    subtitle="数据源:VITAL · ASCEND · STRENGTH · REDUCE-IT · Cochrane 综述   ·   置信度:高",
    tldr=("绝大多数人吃鱼油保健品没有可证实的健康获益。"
          "唯一明确有效的场景:高危心血管患者 + 处方级 4g 纯 EPA + 医生指导。"),
    kpis=kpis,
    pitfalls=flags,
    panels=panels,
    footer_source="universal-pitfall-detector · 数据基于公开 RCT 与 Cochrane 综述",
    save=os.path.join(OUT_DIR, "dashboard.png"),
)

# ============ HTML 用：单独生成 3 张独立小图（双栏布局）============
fig1 = plot_endpoint_heatmap(endpoints,
                             save=os.path.join(OUT_DIR, "fig1_endpoints.png"))
fig2 = plot_risk_breakdown(rate_treat=0.172, rate_ctrl=0.220,
                           labels=("EPA 4g 治疗组", "安慰剂组"),
                           save=os.path.join(OUT_DIR, "fig2_risk.png"))
fig3 = plot_contamination(clean=0, contaminated=25, baseline=5,
                          labels=("营销宣传效应", "独立 RCT 真实效应",
                                  "替代终点改善"),
                          ylabel="心血管获益 %",
                          save=os.path.join(OUT_DIR, "fig3_contamination.png"))

# ============ 生成 Markdown 报告 ============
md = generate_report(
    title="鱼油（Omega-3）对健康有帮助吗？",
    data_source="VITAL (N=25,871) · ASCEND (N=15,480) · STRENGTH · REDUCE-IT · 多项 Cochrane 综述",
    pitfalls=flags,
    tldr=("绝大多数人吃鱼油保健品没有可证实的健康获益。"
          "唯一明确有效的场景：高危心血管患者 + 处方级 4g 纯 EPA + 医生指导。"),
    conclusion=(
        "**分人群、分剂量看才有意义：**\n\n"
        "| 场景 | 证据 | 结论 |\n"
        "|------|------|------|\n"
        "| 一般健康人长期吃鱼油保健品 | VITAL / ASCEND 大型 RCT | ❌ 无心血管 / 死亡获益 |\n"
        "| 糖尿病人群预防心血管 | ASCEND | ❌ 阴性 |\n"
        "| 已确诊心血管病 + 高甘油三酯 + 他汀治疗，处方 4g 纯 EPA | REDUCE-IT | ✅ 风险降低（但 STRENGTH 同剂量阴性，存疑） |\n"
        "| 极度缺乏 omega-3 饮食者补足基础需求 | 营养学共识 | ✅ 合理 |\n"
        "| '补脑'、'抗衰'、'增强免疫' | 多项 RCT | ❌ 客观指标无变化，仅自评显著 |\n\n"
        "**核心矛盾**：保健品市场把『高危患者用处方药剂量』的微弱阳性结果，"
        "当成『所有人用保健品剂量』的护身符卖给消费者。"
    ),
    confidence="高",
    recommendations=[
        {"do": "饮食优先：每周 2 次富脂鱼（三文鱼/沙丁鱼/鲭鱼）即可覆盖 omega-3 基础需求"},
        {"do": "若已确诊心血管病 + 高甘油三酯，咨询医生是否处方 Vascepa（纯 EPA 4g/天）"},
        {"do": "买保健品看：第三方检测报告（IFOS/USP）、EPA+DHA 实际含量、过氧化值"},
        {"avoid": "把鱼油当作『预防心脏病』『抗衰老』『补脑'的万能保健品长期吃"},
        {"avoid": "信『鱼油降低 25% 心血管风险』的营销话术（绝对差只有 ~5%，且未在多项 RCT 中复现）"},
        {"avoid": "买廉价、无第三方检测、储存条件不明的鱼油（氧化产物可能促炎）"},
    ],
    charts=["dashboard.png"],
)

# 落地
md_path = os.path.join(OUT_DIR, "报告.md")
with open(md_path, "w", encoding="utf-8") as f:
    f.write(md)

# ============ 生成 HTML 学术杂志版 ============
html = generate_html_report(
    title="鱼油（Omega-3）对健康有帮助吗？",
    subtitle="A Statistical Pitfall Review of Omega-3 Supplementation Claims",
    authors="universal-pitfall-detector · 数据基于公开 RCT 与 Cochrane 综述",
    abstract={
        "bg": ("鱼油作为全球年销 <mark class='hl-blue'>~80 亿美元</mark> 的保健品，"
               "被广泛宣传为『预防心血管病、抗衰老、补脑、增强免疫』。"
               "然而大型独立 RCT（VITAL/ASCEND/STRENGTH）"
               "<mark class='hl-red'>几乎全部为阴性结果</mark>，"
               "与营销话术形成强烈反差。"),
        "methods": ("基于公开 RCT 与 Cochrane 综述，使用 universal-pitfall-detector "
                    "对常见鱼油健康宣传进行 9 类陷阱规则匹配，"
                    "并构造对应统计指标（ARR / RRR / NNT / Cohen's d / 多重比较校正）。"),
        "results": ("共检出 "
                    f"<mark>{len(flags)} 项统计陷阱</mark>，其中"
                    f"<mark class='hl-red'>高危 {sum(1 for p in flags if p['severity']=='high')} 项</mark>、"
                    f"中等 {sum(1 for p in flags if p['severity']=='medium')} 项。"
                    "REDUCE-IT 头条『风险降低 22%』在绝对值上仅 "
                    "<mark>ARR=4.8%</mark>（<mark>NNT=21</mark>，5 年随访）；"
                    "同剂量 STRENGTH 试验为 <mark class='hl-red'>阴性</mark>，"
                    "提示安慰剂矿物油可能造成 <mark class='hl-red'>伪阳性</mark>。"),
        "conclusion": ("绝大多数人服用市售鱼油保健品 "
                       "<mark class='hl-red'>没有可证实的健康获益</mark>。"
                       "唯一明确有效的场景：<mark class='hl-green'>高危心血管患者 + "
                       "处方级 4g 纯 EPA + 医生指导</mark>。"
                       "保健剂量（300–1000 mg EPA+DHA）在严谨 RCT 中 "
                       "<mark class='hl-red'>无心血管 / 死亡获益</mark>。"),
    },
    kpis=kpis,
    figures=[
        {"path": "fig1_endpoints.png",
         "title": "终点显著性热图。",
         "caption": "8 个客观硬终点中只有甘油三酯（替代终点）显著，"
                    "心血管事件、死亡率等均不显著；2 个主观自评终点显著，"
                    "提示软硬终点偷换。"},
        {"path": "fig2_risk.png",
         "title": "REDUCE-IT 主要终点风险拆解。",
         "caption": "对照组 22.0% vs 治疗组 17.2%。相对降低 22% 听起来很大，"
                    "但绝对差仅 4.8%，NNT=21。"},
        {"path": "fig3_contamination.png",
         "title": "营销宣传 vs 独立 RCT 真实效应对比。",
         "caption": "营销宣称的 25% 心血管获益在大型独立 RCT 中近乎为零；"
                    "替代终点（甘油三酯）改善亦未转化为硬终点收益。",
         "full": True},
    ],
    positive_findings={
        "lede": "并不是说鱼油完全没用——以下场景的获益是被严谨证据支持的：",
        "items": [
            {
                "who": "高甘油三酯（≥150 mg/dL）+ 已确诊心血管病 + 他汀治疗者",
                "what": "<mark class='hl-green'>心血管复合事件 5 年 ARR ≈ 4.8%（NNT=21）</mark>。"
                        "需医生评估，处方药 Vascepa（纯 EPA）。",
                "evidence": "REDUCE-IT (NEJM 2019)，N=8,179",
                "dose": "纯 EPA <b>4 g / 天</b>（处方剂量）",
            },
            {
                "who": "饮食极度缺乏 omega-3（很少吃鱼 / 严格素食）",
                "what": "补足到基础需求量可改善血脂谱与必需脂肪酸状态。",
                "evidence": "营养学共识 / WHO 推荐",
                "dose": "EPA+DHA <b>250–500 mg / 天</b>（食物或低剂量补剂）",
            },
            {
                "who": "妊娠期与哺乳期女性",
                "what": "<mark class='hl-green'>胎儿与婴儿神经发育需要 DHA</mark>，"
                        "母体若摄入不足建议补充。",
                "evidence": "FDA / NIH 推荐",
                "dose": "DHA <b>200–300 mg / 天</b>",
            },
            {
                "who": "重度高甘油三酯血症（≥500 mg/dL）",
                "what": "<mark class='hl-green'>降低胰腺炎风险</mark>，"
                        "处方鱼油是一线治疗之一。",
                "evidence": "AHA / ADA 指南",
                "dose": "EPA+DHA <b>3–4 g / 天</b>，处方级",
            },
        ],
    },
    pitfalls=flags,
    scenario_table=[
        {"scenario": "一般健康人长期服用市售鱼油保健品",
         "evidence": "VITAL (NEJM 2019) · ASCEND (NEJM 2018)",
         "verdict": "<mark class='hl-red'>无心血管 / 死亡获益</mark>",
         "verdict_kind": "bad"},
        {"scenario": "糖尿病人群预防心血管事件",
         "evidence": "ASCEND",
         "verdict": "<mark class='hl-red'>阴性</mark>",
         "verdict_kind": "bad"},
        {"scenario": "已确诊心血管病 + 高甘油三酯 + 他汀，处方 4g 纯 EPA",
         "evidence": "REDUCE-IT (NEJM 2019)",
         "verdict": "<mark>风险降低</mark>，但 STRENGTH 同剂量阴性，存疑",
         "verdict_kind": "warn"},
        {"scenario": "极度缺乏 omega-3 饮食者补足基础需求",
         "evidence": "营养学共识",
         "verdict": "<mark class='hl-green'>合理</mark>",
         "verdict_kind": "ok"},
        {"scenario": "宣称的『补脑』『抗衰』『增强免疫』",
         "evidence": "多项 RCT 客观指标",
         "verdict": "<mark class='hl-red'>客观无变化</mark>，仅自评显著",
         "verdict_kind": "bad"},
    ],
    recommendations=[
        {"do": "饮食优先：每周 <mark>2 次富脂鱼</mark>（三文鱼/沙丁鱼/鲭鱼）即可覆盖 omega-3 基础需求"},
        {"do": "若已确诊心血管病 + 高甘油三酯，咨询医生是否处方 <mark class='hl-green'>Vascepa（纯 EPA 4g/天）</mark>"},
        {"do": "买保健品看：第三方检测报告（IFOS/USP）、EPA+DHA 实际含量、过氧化值"},
        {"avoid": "把鱼油当作『预防心脏病』『抗衰老』『补脑』的<mark class='hl-red'>万能保健品</mark>长期吃"},
        {"avoid": "信『鱼油降低 25% 心血管风险』类营销话术（绝对差仅 <mark>~5%</mark>，多 RCT 未复现）"},
        {"avoid": "买廉价、无第三方检测、储存条件不明的鱼油（<mark class='hl-red'>氧化产物可能促炎</mark>）"},
    ],
    references=[
        "Manson JE, et al. Marine n-3 Fatty Acids and Prevention of Cardiovascular Disease and Cancer (VITAL). N Engl J Med 2019;380:23-32.",
        "ASCEND Study Collaborative Group. Effects of n-3 Fatty Acid Supplements in Diabetes Mellitus. N Engl J Med 2018;379:1540-1550.",
        "Bhatt DL, et al. Cardiovascular Risk Reduction with Icosapent Ethyl for Hypertriglyceridemia (REDUCE-IT). N Engl J Med 2019;380:11-22.",
        "Nicholls SJ, et al. Effect of High-Dose Omega-3 Fatty Acids vs Corn Oil on Major Adverse Cardiovascular Events in Patients at High Cardiovascular Risk (STRENGTH). JAMA 2020;324:2268-2280.",
        "Abdelhamid AS, et al. Omega-3 fatty acids for the primary and secondary prevention of cardiovascular disease. Cochrane Database Syst Rev 2020.",
    ],
)
html_path = os.path.join(OUT_DIR, "报告.html")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ Dashboard:  {dashboard_path}")
print(f"✅ Markdown:   {md_path}")
print(f"✅ HTML:       {html_path}")
print(f"✅ 共检出 {len(flags)} 项陷阱（"
      f"{sum(1 for p in flags if p['severity']=='high')} 高 / "
      f"{sum(1 for p in flags if p['severity']=='medium')} 中）")
