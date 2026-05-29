---
name: universal-pitfall-detector
description: 检测数据分析与论断中的常见统计陷阱（效应量微小、相对风险夸大、软硬终点偷换、辛普森悖论、幸存者偏差、基率谬误、选择偏差、数据污染、多重比较未校正等9类），并自动生成统计检验、可视化图表与带置信等级的结论报告。当用户提供数据集询问"是否真的有差异/有效/更好"、引用某统计结论（"研究显示…""网友都说…""模型超过…"）请求核实，或出现关键词"显著/p值/有效率/超过/碾压/都说/成功案例/相关性"时使用。适用于医药功效、个人决策、社交媒体分析、大模型评测等任何"用数据下结论"的场景。
---

# Universal Statistical Pitfall Detector

检测数据论断中的统计陷阱，输出可视化 + 带置信等级的结论。

## 何时使用

- 用户提供数据，询问"是否真的有差异/有效/更好"
- 用户引用统计结论（论文、新闻、网帖）请求核实
- 出现关键词：显著、p 值、有效率、碾压、超过、成功案例、相关性、网友都说

## 核心能力

| 能力 | 实现位置 |
|------|---------|
| 9 类陷阱规则库 | `references/pitfall_rules.yaml` |
| 统计检验 + 效应量 | `scripts/stat_analysis.py` |
| 因果 / 偏差检测 | `scripts/causal_check.py` |
| 规则引擎汇总 | `scripts/pitfall_detector.py` |
| 单图可视化（5 种） | `scripts/visualize.py` |
| 总览 dashboard 拼图 | `scripts/dashboard.py` |
| Markdown 报告生成 | `scripts/report.py` |
| **学术杂志 HTML 报告（推荐）** | `scripts/html_report.py` + `assets/journal_template.html` |
| 数据接入 | `scripts/data_ingest.py` |
| 文献检索（占位） | `scripts/literature_search.py` |

## 标准工作流

```
数据 → 统计检验 → 规则匹配 → 因果检查 → 可视化 → 带置信度的结论
```

### 第 1 步：接入数据

- CSV → `data_ingest.load_csv(path)`
- 字典列表 → `data_ingest.load_dict(records)`
- 无原始数据 → `literature_search.search_literature(query)`（部署时接入 ai_search 工具）

### 第 2 步：选择对应检测器

根据用户问题类型选择，必要时组合调用：

| 用户问题类型 | 调用函数 |
|------------|---------|
| "差异显著？" | `cohens_d` + `interpret_d` 看效应量是否微不足道 |
| "有效率 X%？" | `risk_metrics` 拆 ARR / RRR / NNT |
| 多终点报告 | `detect_endpoint_trap` 看软硬终点是否被偷换 |
| 分组数据 | `detect_simpson` 检测辛普森悖论 |
| 看到的"成功案例" | `detect_survivorship` 估算沉默的失败基数 |
| 阳性 / 阴性诊断 | `bayes_update` 用先验纠正基率谬误 |
| 模型刷分 | `detect_contamination` 干净集 vs 污染集对比 |
| 多指标论文 | `detect_multiple_comparison` 提示 Bonferroni 校正 |

### 第 3 步：可视化

**强烈推荐**用 `dashboard.plot_dashboard()` 生成总览拼图，把多个 panel + 标题 + 陷阱徽章拼成一张可分享的大图。也可单独使用各 panel：

| panel type | 函数 | 用途 |
|-----------|------|------|
| `endpoints` | `plot_endpoint_heatmap` | 多终点显著性热图（橙=主观显著可疑/绿=客观显著/灰=不显著） |
| `iceberg` | `plot_survivorship_iceberg` | 幸存者偏差冰山图（水面上 vs 沉默） |
| `simpson` | `plot_simpson` | 分组趋势 vs 整体的交叉线图 |
| `contamination` | `plot_contamination` | 宣传分 vs 真实分 vs 基线柱图（带"高估"标注） |
| `risk` | `plot_risk_breakdown` | 一图看清 ARR / RRR / NNT |

dashboard 调用范式：

```python
from scripts.dashboard import plot_dashboard

plot_dashboard(
    title="主题",
    subtitle="数据源 · 置信度 · ……",
    pitfalls=[{"pitfall": "...", "detail": "...", "severity": "high"}, ...],
    panels=[
        {"type": "endpoints", "kwargs": {"endpoints": [...]}},
        {"type": "risk",      "kwargs": {"rate_treat": ..., "rate_ctrl": ...}},
        {"type": "contamination", "kwargs": {"clean": ..., "contaminated": ..., "baseline": ...}},
    ],
    save="dashboard.png",
)
```

### 第 4 步：生成 Markdown 报告

`report.generate_report()` 输出结构化 Markdown，含：
TL;DR、陷阱速览表、详解、结论、实操建议、5 问护身符、文件清单。

```python
from scripts.report import generate_report

md = generate_report(
    title="...", data_source="...", pitfalls=[...],
    tldr="一句话结论",
    conclusion="多行详细结论...",
    confidence="高",
    recommendations=[{"do": "..."}, {"avoid": "..."}],
    charts=["dashboard.png"],
)
```

### 第 5 步（推荐）：生成学术杂志风格 HTML

`html_report.generate_html_report()` 输出 NEJM/JAMA 风格的单文件 HTML，
含：报头、标题副标题、IMRaD 结构摘要框、KPI 卡片、**BI 风格双栏 figure grid**、
陷阱表 + 详解、分场景结论表、实操建议、5 问护身符、参考文献区。
模板位置：`assets/journal_template.html`，可独立打开 / 打印 / 截图。

#### 完整调用范式

```python
from scripts.visualize import (
    plot_endpoint_heatmap, plot_risk_breakdown, plot_contamination,
    plot_survivorship_iceberg, plot_simpson,
)
from scripts.html_report import generate_html_report

# 1. 单独生成各小图（不要再用 dashboard.png 嵌进 HTML）
plot_endpoint_heatmap(endpoints, save="fig1.png")
plot_risk_breakdown(rate_treat=0.17, rate_ctrl=0.22, save="fig2.png")
plot_contamination(clean=0, contaminated=25, baseline=5, save="fig3.png")

# 2. 生成 HTML
html = generate_html_report(
    title="...",
    subtitle="...",
    abstract={
        "bg": "背景段（支持 <mark> 高亮）",
        "methods": "方法段",
        "results": "结果段",
        "conclusion": "结论段",
    },
    kpis=[
        {"value": "22%", "label": "...", "sublabel": "...", "color": "#D72638"},
        # ... 推荐 4 个
    ],
    figures=[
        {"path": "fig1.png", "title": "终点显著性热图。", "caption": "..."},
        {"path": "fig2.png", "title": "风险拆解。",       "caption": "..."},
        {"path": "fig3.png", "title": "宣传 vs 真实。",   "caption": "...", "full": True},
    ],
    pitfalls=[...],
    scenario_table=[
        {"scenario": "...", "evidence": "...",
         "verdict": "...（支持 <mark>）", "verdict_kind": "ok|warn|bad"},
    ],
    recommendations=[
        {"do": "...（支持 <mark>）"},
        {"avoid": "...（支持 <mark>）"},
    ],
    references=["NEJM 2019..."],
)
with open("报告.html", "w", encoding="utf-8") as f:
    f.write(html)
```

#### figures 参数：BI 风格双栏布局

每张图独立 `figure` 卡片（图区 + caption），用 CSS Grid 双栏排版，
窄屏自动堆叠为单栏。**不要把多图拼成一张 dashboard 嵌入 HTML**——那是
分享/截图场景；HTML 报告里图分开放阅读体验更好。

| 字段 | 作用 |
|------|------|
| `path` | 图相对路径（与 HTML 同目录） |
| `title` | 加粗标题（嵌在 caption 开头） |
| `caption` | 一句话解读 |
| `full: True` | 该图占满双栏宽度（用于核心结论图） |

#### 荧光笔高亮（关键结果一眼可见）

允许在以下字段直接写 `<mark>` 标签做荧光笔高亮：

- `abstract.bg / methods / results / conclusion`
- `scenario_table[].verdict`
- `recommendations[].do / avoid`

| 标签 | 颜色 | 适用场景 |
|------|------|---------|
| `<mark>` 或 `<mark class="hl-yellow">` | 🟨 黄色 | 关键数字（NNT、ARR、p 值） |
| `<mark class="hl-red">` | 🟥 红粉 + 红字 | 阴性 / 失败 / 不显著 / 不支持 |
| `<mark class="hl-green">` | 🟩 浅绿 + 深绿字 | 阳性 / 有效 / 推荐 |
| `<mark class="hl-blue">` | 🟦 浅蓝 | 中性数字 / 背景信息 |

示例：

```python
abstract={
    "results": "<mark>ARR=4.8%</mark>，同剂量 STRENGTH 试验为 "
               "<mark class='hl-red'>阴性</mark>。",
    "conclusion": "<mark class='hl-red'>没有可证实的健康获益</mark>。"
                  "唯一例外：<mark class='hl-green'>高危患者 + 4g 纯 EPA</mark>",
}
```

> ⚠ 这些字段**不做 HTML escape**，调用方负责内容安全（不要把外部 / 用户输入直接喂入）。

## 一键运行示例

```bash
pip install -r requirements.txt
python run.py decision    # 幸存者偏差（创业成功率）
python run.py social      # 选择偏差 + 辛普森悖论
python run.py medical     # 软硬终点偷换（连花清瘟式）
python run.py llm         # 大模型数据污染
python examples/analyze_fish_oil.py   # 全功能示范：dashboard + Markdown + HTML 学术版
```

## 输出产物对照表

| 产物 | 何时用 | 生成函数 |
|------|-------|---------|
| `dashboard.png` | 截图发朋友圈 / 幻灯片单图分享 | `dashboard.plot_dashboard` |
| 单图 `fig*.png` | 嵌入 HTML 双栏布局 | `visualize.plot_*` |
| `报告.md` | GitHub / Notion / 内部文档 | `report.generate_report` |
| `报告.html` | 给非技术读者看 / 打印 / PDF 导出 | `html_report.generate_html_report` |

## 规则扩展

新增陷阱：在 `references/pitfall_rules.yaml` 追加规则条目（含 `id` / `name` / `desc` / `trigger` / `severity`），然后在 `scripts/pitfall_detector.py` 或 `scripts/causal_check.py` 实现对应检测函数。

## 边界声明

- 仅作"警示性"分析，不替代专业统计/医学/法律意见
- 联网检索结果质量取决于信源，需标注可信度
- `literature_search.py` 为占位实现，部署时需接入实际搜索 API
