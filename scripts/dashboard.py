"""一站式 Dashboard（v3 叙事版）

布局：
  ┌──────────────────────────────────────────┐
  │ 大标题 + 副标题                           │
  │ TL;DR 醒目色框                            │
  ├──────┬──────┬──────┬──────────────────────┤
  │ KPI1 │ KPI2 │ KPI3 │ KPI4   （大字卡片） │
  ├──────┴──────┴──────┴──────────────────────┤
  │ 主图区（1-2 个核心证据图）                 │
  ├──────────────────────────────────────────┤
  │ 陷阱卡片网格（2 列，按严重度排序）         │
  ├──────────────────────────────────────────┤
  │ 5 问护身符 footer                         │
  └──────────────────────────────────────────┘
"""
import textwrap

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch, Rectangle

from scripts.visualize import (
    COLORS,
    plot_endpoint_heatmap,
    plot_survivorship_iceberg,
    plot_simpson,
    plot_contamination,
    plot_risk_breakdown,
)

PANEL_DRAWERS = {
    "endpoints":     plot_endpoint_heatmap,
    "iceberg":       plot_survivorship_iceberg,
    "simpson":       plot_simpson,
    "contamination": plot_contamination,
    "risk":          plot_risk_breakdown,
}

SEVERITY_COLOR = {
    "high":   COLORS["danger"],
    "medium": COLORS["warning"],
    "low":    COLORS["neutral"],
}
SEVERITY_LABEL = {"high": "高危", "medium": "中等", "low": "轻微"}


# ---------------- 内部组件 ----------------

def _draw_panel(ax, panel):
    fn = PANEL_DRAWERS.get(panel["type"])
    if fn is None:
        ax.text(0.5, 0.5, f"未知 panel: {panel['type']}", ha="center", va="center")
        return
    kwargs = dict(panel.get("kwargs", {}))
    kwargs["ax"] = ax
    fn(**kwargs)


def _draw_kpi(ax, kpi):
    """KPI 卡片：顶部色条 + 大数字 + 标签 + 副标签"""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    color = kpi.get("color") or COLORS["primary"]

    # 卡片背景
    bg = FancyBboxPatch(
        (0.02, 0.04), 0.96, 0.92,
        boxstyle="round,pad=0,rounding_size=0.03",
        facecolor=COLORS["panel"], edgecolor=COLORS["muted"],
        linewidth=0.6, transform=ax.transAxes,
    )
    ax.add_patch(bg)
    # 顶部色条
    ax.add_patch(Rectangle(
        (0.02, 0.88), 0.96, 0.08,
        facecolor=color, transform=ax.transAxes, zorder=2,
    ))
    # 大字数值
    ax.text(0.5, 0.52, kpi["value"],
            fontsize=30, fontweight="bold", color=color,
            ha="center", va="center", transform=ax.transAxes)
    # 主标签
    ax.text(0.5, 0.24, kpi["label"],
            fontsize=10.5, color=COLORS["primary"], fontweight="bold",
            ha="center", va="center", transform=ax.transAxes)
    # 副标签
    if kpi.get("sublabel"):
        ax.text(0.5, 0.10, kpi["sublabel"],
                fontsize=8.5, color=COLORS["neutral"],
                ha="center", va="center", transform=ax.transAxes)


def _draw_pitfall_card(ax, p, idx=None):
    """陷阱卡片：左色带 + 严重度标签 + 标题 + wrap 详情"""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    sev = p.get("severity", "medium")
    color = SEVERITY_COLOR[sev]
    sev_label = SEVERITY_LABEL[sev]

    # 卡片底
    bg = FancyBboxPatch(
        (0.0, 0.0), 1.0, 1.0,
        boxstyle="round,pad=0,rounding_size=0.025",
        facecolor=COLORS["panel"], edgecolor=COLORS["muted"],
        linewidth=0.6, transform=ax.transAxes,
    )
    ax.add_patch(bg)
    # 左色带
    ax.add_patch(Rectangle(
        (0, 0), 0.025, 1,
        facecolor=color, transform=ax.transAxes,
    ))
    # 严重度小标签
    sev_box = FancyBboxPatch(
        (0.06, 0.78), 0.14, 0.16,
        boxstyle="round,pad=0.005,rounding_size=0.025",
        facecolor=color, edgecolor="none", transform=ax.transAxes,
    )
    ax.add_patch(sev_box)
    ax.text(0.13, 0.86, sev_label,
            fontsize=9, fontweight="bold", color="white",
            ha="center", va="center", transform=ax.transAxes)

    # 标题
    title = p["pitfall"].replace("⚠️", "").strip()
    if idx is not None:
        ax.text(0.225, 0.86, f"# {idx}",
                fontsize=10, fontweight="bold", color=COLORS["muted"],
                ha="left", va="center", transform=ax.transAxes)
        title_x = 0.275
    else:
        title_x = 0.225
    ax.text(title_x, 0.86, title,
            fontsize=12, fontweight="bold", color=COLORS["primary"],
            ha="left", va="center", transform=ax.transAxes)

    # 详情（中文宽度 ~22-26 个字符/行）
    detail = textwrap.fill(p["detail"], width=26,
                           break_long_words=False, break_on_hyphens=False)
    ax.text(0.06, 0.66, detail,
            fontsize=9.5, color=COLORS["neutral"],
            ha="left", va="top", transform=ax.transAxes,
            linespacing=1.55)


def _draw_title(ax, title, subtitle, tldr):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    if tldr:
        # 标题占上半，TLDR 占下半
        ax.text(0, 0.92, title, fontsize=26, fontweight="bold",
                color=COLORS["primary"], va="top", transform=ax.transAxes)
        if subtitle:
            ax.text(0, 0.62, subtitle, fontsize=10.5,
                    color=COLORS["neutral"], va="top", transform=ax.transAxes)
        # TLDR 框
        rect = FancyBboxPatch(
            (0, 0.04), 1.0, 0.40,
            boxstyle="round,pad=0,rounding_size=0.015",
            facecolor="#FFF6F4", edgecolor=COLORS["danger"],
            linewidth=1.4, transform=ax.transAxes,
        )
        ax.add_patch(rect)
        ax.add_patch(Rectangle(
            (0, 0.04), 0.008, 0.40,
            facecolor=COLORS["danger"], transform=ax.transAxes,
        ))
        wrapped = textwrap.fill(tldr, width=70,
                                break_long_words=False, break_on_hyphens=False)
        ax.text(0.025, 0.245, f"核心结论    {wrapped}",
                fontsize=12.5, fontweight="bold", color=COLORS["primary"],
                va="center", transform=ax.transAxes)
    else:
        ax.text(0, 0.78, title, fontsize=26, fontweight="bold",
                color=COLORS["primary"], va="top", transform=ax.transAxes)
        if subtitle:
            ax.text(0, 0.30, subtitle, fontsize=10.5,
                    color=COLORS["neutral"], va="top", transform=ax.transAxes)


def _draw_footer(ax, questions, source=None):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    rect = FancyBboxPatch(
        (0, 0), 1.0, 1.0,
        boxstyle="round,pad=0,rounding_size=0.012",
        facecolor=COLORS["panel"], edgecolor=COLORS["muted"],
        linewidth=0.4, transform=ax.transAxes,
    )
    ax.add_patch(rect)

    ax.text(0.02, 0.86, "看到统计结论时的 5 问护身符",
            fontsize=11.5, fontweight="bold", color=COLORS["primary"],
            transform=ax.transAxes, va="center")

    # 问题分两行三列展示（5 个问题）
    cols = 3
    rows = (len(questions) + cols - 1) // cols
    ys = [0.50, 0.22] if rows >= 2 else [0.50]
    for i, q in enumerate(questions):
        c = i % cols
        r = i // cols
        x = 0.02 + c * 0.33
        y = ys[r] if r < len(ys) else 0.10
        ax.text(x, y, q, fontsize=9.2, color=COLORS["neutral"],
                transform=ax.transAxes, va="center")

    if source:
        ax.text(0.98, 0.06, source, fontsize=8, color=COLORS["muted"],
                ha="right", va="bottom", transform=ax.transAxes,
                style="italic")


# ---------------- 主入口 ----------------

DEFAULT_QUESTIONS = [
    "1. 绝对差多大？（不是相对差）",
    "2. 主观还是客观终点？",
    "3. 测了多少指标？挑了几个？",
    "4. 什么人群？能套到我吗？",
    "5. 谁出的钱？谁在发声？",
]


def plot_dashboard(title, subtitle, pitfalls, panels,
                   tldr=None, kpis=None,
                   footer_questions=None, footer_source=None,
                   save="dashboard.png"):
    """生成叙事化 dashboard

    Args:
        title:    主标题（大字）
        subtitle: 元信息行（数据源 / 置信度等）
        tldr:     一句话核心结论（用红框醒目展示）
        kpis:     list of {value, label, sublabel?, color?} —— 推荐 3-4 个
        panels:   list of {type, kwargs}（type 见 PANEL_DRAWERS）
        pitfalls: list of {pitfall, detail, severity}
        footer_questions: list[str]，默认用 5 问护身符
        footer_source:    底部小字注脚（可放数据源/版权）
    """
    n_panels = len(panels)
    n_kpis = len(kpis) if kpis else 0
    n_pitfalls = len(pitfalls)

    panel_cols = 2 if n_panels >= 2 else 1
    panel_rows = (n_panels + panel_cols - 1) // panel_cols

    pitfall_cols = 2
    pitfall_rows = (n_pitfalls + pitfall_cols - 1) // pitfall_cols

    # 各区高度（inch）
    title_h = 2.2 if tldr else 1.4
    kpi_h = 1.9 if n_kpis else 0
    panel_h = 4.5 * panel_rows if n_panels else 0
    pitfall_h = (0.5 + 1.55 * pitfall_rows) if n_pitfalls else 0
    footer_h = 1.0

    fig_w = 14
    fig_h = title_h + kpi_h + panel_h + pitfall_h + footer_h + 0.6
    fig = plt.figure(figsize=(fig_w, fig_h), facecolor=COLORS["bg"])

    height_ratios = [title_h]
    if n_kpis: height_ratios.append(kpi_h)
    if n_panels: height_ratios.append(panel_h)
    if n_pitfalls: height_ratios.append(pitfall_h)
    height_ratios.append(footer_h)

    main_gs = gridspec.GridSpec(
        len(height_ratios), 1, figure=fig,
        height_ratios=height_ratios,
        hspace=0.25, left=0.04, right=0.96, top=0.985, bottom=0.015,
    )

    idx = 0
    # --- 标题 ---
    _draw_title(fig.add_subplot(main_gs[idx]), title, subtitle, tldr)
    idx += 1

    # --- KPI ---
    if n_kpis:
        kpi_gs = gridspec.GridSpecFromSubplotSpec(
            1, n_kpis, subplot_spec=main_gs[idx], wspace=0.18,
        )
        for i, k in enumerate(kpis):
            _draw_kpi(fig.add_subplot(kpi_gs[i]), k)
        idx += 1

    # --- 主图 ---
    if n_panels:
        p_gs = gridspec.GridSpecFromSubplotSpec(
            panel_rows, panel_cols, subplot_spec=main_gs[idx],
            hspace=0.55, wspace=0.30,
        )
        for i, panel in enumerate(panels):
            r, c = divmod(i, panel_cols)
            if i == n_panels - 1 and n_panels % panel_cols == 1 and panel_cols == 2:
                ax = fig.add_subplot(p_gs[r, :])
            else:
                ax = fig.add_subplot(p_gs[r, c])
            _draw_panel(ax, panel)
        idx += 1

    # --- 陷阱卡片 ---
    if n_pitfalls:
        sorted_p = sorted(
            pitfalls,
            key=lambda p: {"high": 0, "medium": 1, "low": 2}.get(p.get("severity", "medium"), 1),
        )
        pf_outer = gridspec.GridSpecFromSubplotSpec(
            2, 1, subplot_spec=main_gs[idx],
            height_ratios=[0.45, 1.55 * pitfall_rows],
            hspace=0.2,
        )
        ax_h = fig.add_subplot(pf_outer[0])
        ax_h.axis("off")
        n_high = sum(1 for p in pitfalls if p.get("severity") == "high")
        n_med = sum(1 for p in pitfalls if p.get("severity") == "medium")
        n_low = sum(1 for p in pitfalls if p.get("severity") == "low")
        ax_h.text(0, 0.6, f"陷阱清单",
                  fontsize=15, fontweight="bold", color=COLORS["primary"],
                  va="center", transform=ax_h.transAxes)
        breakdown = f"共 {n_pitfalls} 项 · 高危 {n_high} · 中等 {n_med}" + (
            f" · 轻微 {n_low}" if n_low else ""
        )
        ax_h.text(0.13, 0.6, breakdown,
                  fontsize=10.5, color=COLORS["neutral"],
                  va="center", transform=ax_h.transAxes)

        cards_gs = gridspec.GridSpecFromSubplotSpec(
            pitfall_rows, pitfall_cols, subplot_spec=pf_outer[1],
            hspace=0.25, wspace=0.13,
        )
        for i, p in enumerate(sorted_p):
            r, c = divmod(i, pitfall_cols)
            ax = fig.add_subplot(cards_gs[r, c])
            _draw_pitfall_card(ax, p, idx=i + 1)
        idx += 1

    # --- Footer ---
    _draw_footer(
        fig.add_subplot(main_gs[idx]),
        footer_questions or DEFAULT_QUESTIONS,
        footer_source,
    )

    plt.savefig(save, dpi=140, facecolor=COLORS["bg"])
    plt.close()
    return save
