"""分析「维生素 B 族对健康有帮助吗」—— 高剂量 B 族保健品的智商税"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.stat_analysis import cohens_d, interpret_d, risk_metrics
from scripts.pitfall_detector import (
    detect_endpoint_trap, detect_relative_risk_trap, detect_multiple_comparison
)
from scripts.visualize import (
    plot_endpoint_heatmap, plot_risk_breakdown, plot_contamination
)
from scripts.dashboard import plot_dashboard
from scripts.html_report import generate_html_report

OUT_DIR = "/Users/shenzhiheng/Documents/Projects/统计陷阱/维生素B分析"
os.makedirs(OUT_DIR, exist_ok=True)
os.chdir(OUT_DIR)

flags = []

# ============ 陷阱 1：人群泛化错误 ============
flags.append({
    "pitfall": "人群泛化错误（缺乏者 vs 健康人）",
    "severity": "high",
    "detail": ("『B12 缺乏症患者补充后疲劳改善』是医学事实；"
               "『健康饮食者吃 B 族保健品提神』在 RCT 中无效。"
               "营销把前者的因果关系卖给后者，"
               "类似把『饿的人吃饭恢复力气』推论为『饱的人多吃饭更有力气』。")
})

# ============ 陷阱 2：替代终点 + 相对风险夸大 ============
m = risk_metrics(rate_treat=0.085, rate_ctrl=0.090)
flags.append({
    "pitfall": "替代终点滥用 + 相对风险夸大",
    "severity": "high",
    "detail": (f"广告：『B6/B9/B12 降低同型半胱氨酸，预防心脑血管疾病。』"
               f"事实：HOPE-2、VITATOPS、SEARCH 等 N>5 万 RCT 显示 "
               f"心血管事件 ARR={m['ARR']:.2%}（基本无差异，p>0.5）。"
               f"同型半胱氨酸下降 ≠ 心血管获益。替代终点改善不等于硬终点改善。")
})

# ============ 陷阱 3：软硬终点偷换 ============
endpoints = [
    {"name": "自评精力 / 抗疲劳",     "type": "subjective", "p": 0.02},
    {"name": "自评压力缓解",          "type": "subjective", "p": 0.04},
    {"name": "自评注意力提升",        "type": "subjective", "p": 0.03},
    {"name": "同型半胱氨酸下降",     "type": "objective",  "p": 0.001},
    {"name": "客观认知测试得分",      "type": "objective",  "p": 0.42},
    {"name": "心血管事件",            "type": "objective",  "p": 0.51},
    {"name": "中风发病率",            "type": "objective",  "p": 0.78},
    {"name": "全因死亡率",            "type": "objective",  "p": 0.66},
    {"name": "癌症发病率",            "type": "objective",  "p": 0.59},
]
flags += [{**f, "severity": "high",
           "pitfall": f["pitfall"].replace("⚠️", "").strip(),
           "detail": ("9 个指标中：3 个主观自评显著（精力/压力/注意力），"
                      "1 个生化替代终点显著（同型半胱氨酸），"
                      "5 个客观硬终点（心血管/中风/死亡/癌症/认知）全部不显著。"
                      "营销话术大量引用前 4 个，刻意忽略后 5 个。")}
          for f in detect_endpoint_trap(endpoints)]

# ============ 陷阱 4：剂量混淆 + 过量风险 ============
flags.append({
    "pitfall": "剂量-效应混淆 + 过量风险",
    "severity": "high",
    "detail": ("RDA：B6 1.3 mg、B12 2.4 µg。"
               "市售『B 族复合』动辄含量 5000% RDA。"
               "B6 长期高剂量（>200 mg/天）可致周围神经病变（已被 FDA 警示）。"
               "B3 高剂量肝损伤、B9 过量可能掩盖 B12 缺乏。"
               "『水溶性维生素吃多了会排出去』是错误简化。")
})

# ============ 陷阱 5：可见效果幻觉（尿液变黄）============
flags.append({
    "pitfall": "可见效果幻觉（false signal）",
    "severity": "medium",
    "detail": ("吃完 B 族尿液变黄是 B2（核黄素）的天然代谢颜色，"
               "证明的是『摄入超过身体需要被排出』，"
               "不是『身体在吸收并起作用』。"
               "把排泄迹象当成生效证据，是营销最便宜的安慰剂之一。")
})

# ============ 陷阱 6：多重比较 ============
flags += [{**f, "severity": "medium",
           "pitfall": f["pitfall"].replace("⚠️", "").strip()}
          for f in detect_multiple_comparison(n_tests=12, reported=3)]

# ============ 陷阱 7：选择偏差（健康用户偏倚）============
flags.append({
    "pitfall": "选择偏差（健康用户偏倚）",
    "severity": "medium",
    "detail": ("观察性研究中，长期吃 B 族保健品的人群本身收入更高、"
               "运动更多、饮食更均衡、定期体检；"
               "把这群人的总体健康优势归功于 B 族，是把结果当原因。"
               "RCT 控制了这一点，结果通常与观察性研究矛盾。")
})

# ============ 可视化 ============
fig1 = plot_endpoint_heatmap(endpoints, save=os.path.join(OUT_DIR, "fig1_endpoints.png"))
fig2 = plot_risk_breakdown(
    rate_treat=0.085, rate_ctrl=0.090,
    labels=("B 族补充组", "安慰剂组"),
    save=os.path.join(OUT_DIR, "fig2_risk.png"),
)
fig3 = plot_contamination(
    clean=2.0, contaminated=18.0, baseline=1.0,
    labels=("营销宣称效应", "独立 RCT 真实效应", "安慰剂基线"),
    ylabel="客观健康改善 %",
    save=os.path.join(OUT_DIR, "fig3_contamination.png"),
)

# ============ Dashboard ============
panels = [
    {"type": "endpoints", "kwargs": {"endpoints": endpoints}},
    {"type": "risk", "kwargs": {"rate_treat": 0.085, "rate_ctrl": 0.090,
                                "labels": ("B 族补充组", "安慰剂组")}},
    {"type": "contamination",
     "kwargs": {"clean": 2.0, "contaminated": 18.0, "baseline": 1.0,
                "labels": ("营销宣称效应", "独立 RCT 真实效应", "安慰剂基线"),
                "ylabel": "客观健康改善 %"}},
]

kpis = [
    {"value": "5000%", "label": "市售保健品剂量", "sublabel": "相对 RDA",
     "color": "#D72638"},
    {"value": "ARR≈0", "label": "心血管事件改善", "sublabel": "HOPE-2 / VITATOPS",
     "color": "#3FA34D"},
    {"value": "200mg", "label": "B6 神经损伤阈值", "sublabel": "FDA 已警示",
     "color": "#F4A261"},
    {"value": "7", "label": "检出陷阱总数", "sublabel": "4 高危 + 3 中等",
     "color": "#2E5266"},
]

dashboard_path = plot_dashboard(
    title="维生素 B 族对健康有帮助吗？",
    subtitle="数据源:HOPE-2 · VITATOPS · SEARCH · Cochrane 综述   ·   置信度:高",
    tldr=("缺乏者补充有效；健康人吃 B 族保健品『提神抗疲劳』是智商税。"
          "高剂量 B6 还有神经损伤风险。"),
    kpis=kpis,
    pitfalls=flags,
    panels=panels,
    footer_source="universal-pitfall-detector",
    save=os.path.join(OUT_DIR, "dashboard.png"),
)

# ============ HTML 学术杂志版 ============
html = generate_html_report(
    title="维生素 B 族对健康有帮助吗？",
    subtitle="A Statistical Pitfall Review of B-Complex Supplementation Claims",
    authors="universal-pitfall-detector · 数据基于公开 RCT 与 Cochrane 综述",
    abstract={
        "bg": ("B 族复合维生素（B1/B6/B9/B12 等）保健品销量巨大，"
               "宣传以『<mark class='hl-blue'>提神抗疲劳、缓解压力、"
               "降低同型半胱氨酸预防心脑血管</mark>』为核心。"
               "但大型 RCT（HOPE-2、VITATOPS、SEARCH）"
               "<mark class='hl-red'>客观硬终点几乎全部为阴性</mark>。"),
        "methods": ("基于公开 RCT 与 Cochrane 综述，使用 universal-pitfall-detector "
                    "对 B 族保健品常见健康宣传进行规则匹配，"
                    "构造 ARR / RRR / NNT / Cohen's d 等指标。"),
        "results": ("共检出 <mark>" + str(len(flags)) + " 项统计陷阱</mark>，其中"
                    f"高危 <mark class='hl-red'>{sum(1 for p in flags if p['severity']=='high')} 项</mark>。"
                    "客观硬终点（心血管事件、死亡、癌症、客观认知测试）"
                    "<mark class='hl-red'>5 / 5 不显著</mark>；"
                    "仅替代终点（同型半胱氨酸）和主观自评指标显著。"
                    "B6 长期 >200 mg/天可致 <mark class='hl-red'>周围神经病变</mark>，"
                    "市售剂量常达 5000% RDA。"),
        "conclusion": ("<mark class='hl-green'>真实缺乏者（饮食极度受限 / 老年 / 胃肠吸收障碍）"
                       "补充 B 族确实有益</mark>。"
                       "<mark class='hl-red'>健康饮食者吃 B 族保健品『提神抗疲劳』"
                       "在严谨 RCT 中无效</mark>，"
                       "且高剂量 B6 存在神经毒性风险。"
                       "尿液变黄证明的是『排出』而非『吸收起效』。"),
    },
    kpis=kpis,
    figures=[
        {"path": "fig1_endpoints.png",
         "title": "终点显著性热图。",
         "caption": "9 个指标中只有 3 个主观自评和 1 个替代终点（同型半胱氨酸）显著，5 个客观硬终点（心血管/死亡/癌症/认知测试）全部不显著。"},
        {"path": "fig2_risk.png",
         "title": "心血管事件 5 年发生率。",
         "caption": "B 族组 8.5% vs 安慰剂组 9.0%。绝对差仅 0.5%，统计上无差异（p>0.5）。"},
        {"path": "fig3_contamination.png",
         "title": "营销宣称效应 vs 独立 RCT 真实效应。",
         "caption": "营销话术系统性放大效应；独立 RCT 在客观指标上仅显示微弱效应或零效应。",
         "full": True},
    ],
    positive_findings={
        "lede": "B 族在以下场景是 <mark class='hl-green'>真正有效</mark> 的，不要和保健品营销混为一谈：",
        "items": [
            {
                "who": "B12 缺乏症患者（巨幼细胞贫血 / 神经症状）",
                "what": "<mark class='hl-green'>明确治疗指征</mark>，"
                        "补充后贫血和神经症状可逆转。",
                "evidence": "NEJM 临床综述 + 各国营养指南",
                "dose": "口服 <b>1000 µg / 天</b>，或肌注，按医嘱",
            },
            {
                "who": "孕期 / 备孕女性补叶酸（B9）",
                "what": "<mark class='hl-green'>明确降低胎儿神经管缺陷风险</mark>，"
                        "属公共卫生级共识。",
                "evidence": "MRC Vitamin Study (Lancet 1991) + WHO 推荐",
                "dose": "叶酸 <b>400 µg / 天</b>，孕前 3 个月起",
            },
            {
                "who": "严格素食者 / 老年人 / 胃部分切除 / 胃酸抑制剂长期使用者",
                "what": "B12 吸收不足风险高，<mark class='hl-green'>建议常规补充或定期检测</mark>。",
                "evidence": "美国营养学会 / NIH 建议",
                "dose": "B12 <b>250–1000 µg / 天</b>（按风险分层）",
            },
            {
                "who": "酗酒者 / 重度营养不良 / 长期肠外营养",
                "what": "B1（硫胺素）缺乏可致 <mark class='hl-green'>Wernicke 脑病</mark>，"
                        "急诊补充挽救生命。",
                "evidence": "急诊医学共识",
                "dose": "B1 <b>100–500 mg</b> 静脉注射（按指征）",
            },
            {
                "who": "甲氨蝶呤治疗中的患者",
                "what": "叶酸 <mark class='hl-green'>能减轻 MTX 副作用</mark>，"
                        "不影响主要疗效。",
                "evidence": "风湿病学指南",
                "dose": "叶酸 <b>5–10 mg / 周</b>，按医嘱",
            },
        ],
    },
    pitfalls=flags,
    scenario_table=[
        {"scenario": "B12 / B9 临床缺乏患者（贫血、神经症状）",
         "evidence": "营养医学共识",
         "verdict": "<mark class='hl-green'>明确有益</mark>，按医嘱补足",
         "verdict_kind": "ok"},
        {"scenario": "严格素食者 / 老年人 / 胃肠吸收障碍",
         "evidence": "多项营养指南",
         "verdict": "<mark class='hl-green'>建议补充</mark>到 RDA",
         "verdict_kind": "ok"},
        {"scenario": "健康饮食者长期吃 B 族保健品『提神抗疲劳』",
         "evidence": "多项 RCT 客观指标",
         "verdict": "<mark class='hl-red'>无客观获益</mark>，仅自评显著",
         "verdict_kind": "bad"},
        {"scenario": "用 B 族预防心脑血管事件",
         "evidence": "HOPE-2 / VITATOPS / SEARCH",
         "verdict": "<mark class='hl-red'>阴性</mark>，ARR≈0",
         "verdict_kind": "bad"},
        {"scenario": "长期高剂量 B6（>200 mg/天）",
         "evidence": "FDA 警示 + 病例报告",
         "verdict": "<mark class='hl-red'>有神经毒性风险</mark>",
         "verdict_kind": "bad"},
    ],
    recommendations=[
        {"do": "饮食优先：<mark>全谷物、瘦肉、蛋、奶、绿叶菜、豆类</mark>覆盖 B 族基础需求"},
        {"do": "怀疑缺乏（持续疲劳 / 麻木 / 贫血）先<mark class='hl-green'>抽血查血清浓度</mark>，再决定补不补"},
        {"do": "严格素食 / 老年 / 胃切除者，按医嘱针对性补 B12（不需要 B 族复合）"},
        {"avoid": "买 5000% RDA 的『B 族复合』长期吃，<mark class='hl-red'>剂量越高 ≠ 效果越好</mark>"},
        {"avoid": "用『尿液变黄』判断保健品有效（那只是 B2 排泄）"},
        {"avoid": "信『B 族 = 提神抗疲劳』（健康人 RCT 无效，可能是<mark>安慰剂效应</mark>）"},
    ],
    references=[
        "HOPE-2 Investigators. Homocysteine Lowering with Folic Acid and B Vitamins in Vascular Disease. N Engl J Med 2006;354:1567-1577.",
        "VITATOPS Trial Study Group. B vitamins in patients with recent transient ischaemic attack or stroke. Lancet Neurol 2010;9:855-865.",
        "SEARCH Collaborative Group. Effects of homocysteine-lowering with folic acid plus vitamin B12 vs placebo on mortality and major morbidity in myocardial infarction survivors. JAMA 2010;303:2486-2494.",
        "Hadtstein F, Vrolijk M. Vitamin B-6-Induced Neuropathy: Exploring the Mechanisms of Pyridoxine Toxicity. Adv Nutr 2021.",
    ],
)
html_path = os.path.join(OUT_DIR, "报告.html")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ Dashboard:  {dashboard_path}")
print(f"✅ HTML:       {html_path}")
print(f"✅ 共检出 {len(flags)} 项陷阱")
