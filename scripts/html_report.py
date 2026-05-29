"""学术杂志风格 HTML 报告生成器

用法：
    from scripts.html_report import generate_html_report
    html = generate_html_report(
        title="...", subtitle="...",
        abstract={"bg": "...", "methods": "...", "results": "...", "conclusion": "..."},
        kpis=[{"value":..., "label":..., "sublabel":...}, ...],
        dashboard_path="dashboard.png",
        pitfalls=[...],
        scenario_table=[{"scenario":..., "evidence":..., "verdict":..., "verdict_kind":"ok|warn|bad"}, ...],
        recommendations=[{"do":...}, {"avoid":...}],
        references=["..."],
    )
    with open("报告.html", "w") as f: f.write(html)
"""
import os
import datetime
import html as ihtml

TEMPLATE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "journal_template.html",
)

SEV_LABEL = {"high": "高危", "medium": "中等", "low": "轻微"}


def _esc(s):
    return ihtml.escape(s if s is not None else "", quote=False)


def _kpi_html(kpis):
    parts = []
    for k in kpis:
        parts.append(
            f'<div class="kpi">'
            f'  <div class="v">{_esc(str(k["value"]))}</div>'
            f'  <div class="l">{_esc(k.get("label",""))}</div>'
            f'  <div class="s">{_esc(k.get("sublabel",""))}</div>'
            f'</div>'
        )
    return "\n".join(parts)


def _pitfall_table_html(pitfalls):
    sorted_p = sorted(
        pitfalls,
        key=lambda p: {"high": 0, "medium": 1, "low": 2}.get(p.get("severity", "medium"), 1),
    )
    rows = []
    for i, p in enumerate(sorted_p, 1):
        sev = p.get("severity", "medium")
        name = p["pitfall"].replace("⚠️", "").strip()
        detail = p["detail"].replace("\n", " ")
        if len(detail) > 130:
            detail = detail[:128] + "…"
        rows.append(
            f"<tr>"
            f"<td class='num'>{i}</td>"
            f"<td><span class='badge {sev}'>{SEV_LABEL[sev]}</span></td>"
            f"<td><strong>{_esc(name)}</strong></td>"
            f"<td>{_esc(detail)}</td>"
            f"</tr>"
        )
    return (
        "<table class='data'>"
        "<thead><tr><th style='width:36px'>#</th><th style='width:72px'>严重度</th>"
        "<th style='width:160px'>陷阱</th><th>关键发现</th></tr></thead>"
        "<tbody>" + "\n".join(rows) + "</tbody></table>"
    )


def _pitfall_detail_html(pitfalls):
    sorted_p = sorted(
        pitfalls,
        key=lambda p: {"high": 0, "medium": 1, "low": 2}.get(p.get("severity", "medium"), 1),
    )
    parts = []
    for i, p in enumerate(sorted_p, 1):
        sev = p.get("severity", "medium")
        name = p["pitfall"].replace("⚠️", "").strip()
        detail_p = "<p>" + _esc(p["detail"]).replace("\n", "</p><p>") + "</p>"
        parts.append(
            f'<div class="pitfall {sev}">'
            f'  <div class="head">'
            f'    <span class="num">陷阱 {i:02d}</span>'
            f'    <span class="badge {sev}">{SEV_LABEL[sev]}</span>'
            f'    <span class="name">{_esc(name)}</span>'
            f'  </div>'
            f'  {detail_p}'
            f'</div>'
        )
    return "\n".join(parts)


def _conclusion_table_html(rows):
    if not rows:
        return ""
    out = ["<table class='data'>",
           "<thead><tr><th>场景</th><th>证据来源</th><th style='width:240px'>结论</th></tr></thead>",
           "<tbody>"]
    badge_map = {"ok": ("ok", "支持"), "warn": ("medium", "存疑"), "bad": ("high", "不支持")}
    for r in rows:
        kind = r.get("verdict_kind", "warn")
        bclass, blabel = badge_map.get(kind, ("medium", "存疑"))
        # verdict 保留 HTML（允许 <mark>）
        verdict_text = r.get("verdict", "")
        out.append(
            f"<tr>"
            f"<td>{_esc(r.get('scenario',''))}</td>"
            f"<td><em>{_esc(r.get('evidence',''))}</em></td>"
            f"<td><span class='badge {bclass}'>{blabel}</span> {verdict_text}</td>"
            f"</tr>"
        )
    out.append("</tbody></table>")
    return "\n".join(out)


def _recs_html(recs):
    """recommendations: list of {do?, avoid?}；do/avoid 内容保留 HTML，允许 <mark>"""
    dos = [r["do"] for r in recs if r.get("do")]
    avoids = [r["avoid"] for r in recs if r.get("avoid")]
    return (
        '<div class="recs">'
        '<div class="col do"><h4>推荐做</h4><ul>'
        + "".join(f"<li>{d}</li>" for d in dos) +
        '</ul></div>'
        '<div class="col avoid"><h4>避免做</h4><ul>'
        + "".join(f"<li>{a}</li>" for a in avoids) +
        '</ul></div>'
        '</div>'
    )


def _five_questions_html(questions=None):
    questions = questions or [
        ("绝对差多大？（不是相对差）", "针对相对风险夸大"),
        ("主观还是客观终点？", "针对软硬终点偷换"),
        ("测了多少指标？只报了几个？", "针对多重比较"),
        ("什么人群？能套到我吗？", "针对泛化 / 异质性"),
        ("谁出的钱？谁在发声？", "针对资助偏差 / 选择偏差"),
    ]
    items = "".join(
        f"<li>{_esc(q)}<span class='tag'>{_esc(t)}</span></li>"
        for q, t in questions
    )
    return f'<div class="five"><h4>读者守则</h4><ol>{items}</ol></div>'


def _references_html(refs):
    if not refs:
        return "<p>—</p>"
    items = "".join(f"<li>{_esc(r)}</li>" for r in refs)
    return f"<ol>{items}</ol>"


def _figures_html(figures):
    """figures: list of {path, title, caption, full?: bool}"""
    if not figures:
        return ""
    parts = ['<div class="figure-grid">']
    for i, f in enumerate(figures, 1):
        cls = " full" if f.get("full") else ""
        title = f.get("title", "")
        title_html = (f'<span class="figtitle">{_esc(title)}</span>'
                      if title else "")
        parts.append(
            f'<figure class="{cls.strip()}">'
            f'  <div class="figbody"><img src="{_esc(f["path"])}" alt="{_esc(title)}"></div>'
            f'  <figcaption>'
            f'    <span class="figlabel">Figure {i}.</span>'
            f'    {title_html}'
            f'    {_esc(f.get("caption", ""))}'
            f'  </figcaption>'
            f'</figure>'
        )
    parts.append('</div>')
    return "\n".join(parts)


def _positive_findings_html(positive):
    """positive: dict with optional keys
        - lede: 一句话引导
        - items: list of {who, what, evidence?, dose?}
                 who/what/evidence/dose 都允许 HTML（mark 等）
    或直接传 list（视为 items，无 lede）
    """
    if not positive:
        return ""
    if isinstance(positive, list):
        positive = {"items": positive}
    items = positive.get("items", [])
    if not items:
        return ""

    lede = positive.get("lede",
                        "并非什么都没用——以下是经过严谨证据支持的有效场景。")

    cards = []
    for it in items:
        meta_parts = []
        if it.get("evidence"):
            meta_parts.append(f"<b>证据：</b>{it['evidence']}")
        if it.get("dose"):
            meta_parts.append(f"<b>剂量 / 方式：</b>{it['dose']}")
        meta_html = ("<div class='meta'>" + " · ".join(meta_parts) + "</div>"
                     if meta_parts else "")
        cards.append(
            f"<div class='item'>"
            f"  <div class='who'>{it.get('who','')}</div>"
            f"  <div class='what'>{it.get('what','')}</div>"
            f"  {meta_html}"
            f"</div>"
        )

    return (
        f'<div class="positive">'
        f'  <h3>✓  确定有效的场景</h3>'
        f'  <p class="lede">{lede}</p>'
        f'  <div class="grid">{"".join(cards)}</div>'
        f'</div>'
    )


def generate_html_report(
    title,
    subtitle,
    abstract,
    kpis,
    figures,
    pitfalls,
    positive_findings=None,
    scenario_table=None,
    recommendations=None,
    references=None,
    five_questions=None,
    authors="universal-pitfall-detector · 自动生成",
    template_path=TEMPLATE_PATH,
):
    """生成学术杂志风格 HTML 报告

    Args:
        figures: list of {path, title, caption, full?: bool}
                 full=True 表示该图占满双栏
        positive_findings: dict {lede?, items: [{who, what, evidence?, dose?}]}
                 或 list[item]，列出"经过严谨证据支持的有效场景"，
                 用绿色调强调框展示，避免报告整体显得过度悲观。
                 字段允许 HTML（mark 等）
    """
    with open(template_path, encoding="utf-8") as f:
        tpl = f.read()

    today = datetime.date.today().strftime("%Y 年 %m 月 %d 日")

    abstract = abstract or {}
    replacements = {
        "{{TITLE}}":            _esc(title),
        "{{SUBTITLE}}":         _esc(subtitle),
        "{{AUTHORS}}":          _esc(authors),
        "{{DATE}}":             today,
        "{{ABSTRACT_BG}}":      abstract.get("bg", ""),
        "{{ABSTRACT_METHODS}}": abstract.get("methods", ""),
        "{{ABSTRACT_RESULTS}}": abstract.get("results", ""),
        "{{ABSTRACT_CONCL}}":   abstract.get("conclusion", ""),
        "{{KPI_CARDS}}":        _kpi_html(kpis or []),
        "{{FIGURE_GRID}}":      _figures_html(figures or []),
        "{{POSITIVE_FINDINGS}}":_positive_findings_html(positive_findings),
        "{{PITFALL_TABLE}}":    _pitfall_table_html(pitfalls or []),
        "{{PITFALL_DETAIL}}":   _pitfall_detail_html(pitfalls or []),
        "{{CONCLUSION_TABLE}}": _conclusion_table_html(scenario_table or []),
        "{{RECOMMENDATIONS}}":  _recs_html(recommendations or []),
        "{{FIVE_QUESTIONS}}":   _five_questions_html(five_questions),
        "{{REFERENCES}}":       _references_html(references or []),
    }
    for k, v in replacements.items():
        tpl = tpl.replace(k, v)
    return tpl
