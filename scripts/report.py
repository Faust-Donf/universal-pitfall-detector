"""报告生成（v2 升级版）：输出 Markdown 而非 ASCII 边框。

排版改进：
  - emoji 分级标题
  - 陷阱按 severity 排序、表格化
  - TL;DR 区块
  - 5 问护身符模板
  - 文件清单与运行指引
"""

SEVERITY_LABEL = {
    "high":   "🔴 高",
    "medium": "🟠 中",
    "low":    "⚪ 低",
}


def _normalize(p):
    """补齐 severity 默认值"""
    sev = p.get("severity", "medium")
    if sev not in SEVERITY_LABEL:
        sev = "medium"
    return {**p, "severity": sev}


def generate_report(title, data_source, pitfalls, conclusion, confidence,
                    charts=None, tldr=None, recommendations=None,
                    five_questions=True):
    """生成 Markdown 报告

    Args:
        title:           报告主题
        data_source:     数据源描述
        pitfalls:        list of {'pitfall', 'detail', 'severity'}
        conclusion:      最终结论文本（支持多行）
        confidence:      高 / 中 / 低
        charts:          图表文件名列表（用于文件清单）
        tldr:            一句话结论（强烈推荐）
        recommendations: 实操建议列表 [{'do': str}, {'avoid': str}]
        five_questions:  是否在尾部追加"5 问护身符"模板
    """
    pitfalls = [_normalize(p) for p in pitfalls]
    pitfalls.sort(key=lambda p: {"high": 0, "medium": 1, "low": 2}[p["severity"]])
    charts = charts or []

    out = []

    # 标题 + 元信息
    out.append(f"# {title}")
    out.append("")
    out.append(f"> **数据源**：{data_source}")
    out.append(f"> **置信度**：{confidence}")
    out.append(f"> **检出陷阱**：共 {len(pitfalls)} 项 "
               f"（{sum(1 for p in pitfalls if p['severity']=='high')} 高 · "
               f"{sum(1 for p in pitfalls if p['severity']=='medium')} 中 · "
               f"{sum(1 for p in pitfalls if p['severity']=='low')} 低）")
    out.append("")
    out.append("---")
    out.append("")

    # TL;DR
    if tldr:
        out.append("## 🎯 一句话结论")
        out.append("")
        out.append(f"> **{tldr}**")
        out.append("")

    # 陷阱总表
    if pitfalls:
        out.append("## ⚠️ 陷阱速览")
        out.append("")
        out.append("| 严重度 | 陷阱 | 关键发现 |")
        out.append("|:------:|------|---------|")
        for p in pitfalls:
            name = p["pitfall"].replace("⚠️", "").strip()
            detail = p["detail"].replace("\n", " ")
            if len(detail) > 90:
                detail = detail[:88] + "…"
            out.append(f"| {SEVERITY_LABEL[p['severity']]} | **{name}** | {detail} |")
        out.append("")

        # 陷阱详解
        out.append("## 🔍 陷阱详解")
        out.append("")
        for i, p in enumerate(pitfalls, 1):
            name = p["pitfall"].replace("⚠️", "").strip()
            out.append(f"### {i}. {SEVERITY_LABEL[p['severity']]} {name}")
            out.append("")
            out.append(p["detail"])
            out.append("")
    else:
        out.append("## ✓ 未检测到明显统计陷阱")
        out.append("")

    # 结论
    out.append("## 📌 结论")
    out.append("")
    for line in conclusion.split("\n"):
        out.append(line)
    out.append("")

    # 实操建议
    if recommendations:
        out.append("## 💡 实操建议")
        out.append("")
        dos = [r.get("do") for r in recommendations if r.get("do")]
        avoids = [r.get("avoid") for r in recommendations if r.get("avoid")]
        if dos:
            out.append("**✅ 推荐做**")
            out.append("")
            for d in dos:
                out.append(f"- {d}")
            out.append("")
        if avoids:
            out.append("**❌ 避免做**")
            out.append("")
            for a in avoids:
                out.append(f"- {a}")
            out.append("")

    # 5 问护身符
    if five_questions:
        out.append("## 🛡️ 看到统计结论时的 5 问护身符")
        out.append("")
        out.append("| # | 问题 | 抓什么陷阱 |")
        out.append("|:-:|------|----------|")
        out.append("| 1 | 绝对差多大？（不是相对差） | 相对风险夸大 |")
        out.append("| 2 | 主要终点还是次要终点？（客观 vs 主观） | 软硬终点偷换 |")
        out.append("| 3 | 测了多少指标？只报了几个？ | 多重比较 |")
        out.append("| 4 | 什么人群得出的结论？能套到我吗？ | 泛化 / 异质性 |")
        out.append("| 5 | 谁出的钱？谁会发声？ | 资助偏差 / 选择偏差 |")
        out.append("")

    # 文件清单
    if charts:
        out.append("## 📁 输出文件")
        out.append("")
        for c in charts:
            out.append(f"- `{c}`")
        out.append("")

    return "\n".join(out)


def generate_text_report(title, data_source, pitfalls, conclusion, confidence, charts):
    """旧 ASCII 边框格式（向后兼容，不推荐使用）"""
    lines = []
    lines.append("=" * 60)
    lines.append(f"  统计陷阱检测报告：{title}")
    lines.append("=" * 60)
    lines.append(f"\n【数据来源】{data_source}")
    lines.append(f"\n【检测到的陷阱】共 {len(pitfalls)} 项")
    if not pitfalls:
        lines.append("  ✓ 未检测到明显统计陷阱")
    for i, p in enumerate(pitfalls, 1):
        lines.append(f"  {i}. {p['pitfall']}")
        lines.append(f"     {p['detail']}")
    lines.append(f"\n【生成图表】{', '.join(charts or [])}")
    lines.append(f"\n【结论】（置信度：{confidence}）")
    lines.append(f"  {conclusion}")
    lines.append("=" * 60 + "\n")
    return "\n".join(lines)
