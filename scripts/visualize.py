"""可视化模块（v2 升级版）
- 统一配色（品牌色板）
- 中文字体优先级：PingFang SC > Hiragino Sans GB > Microsoft YaHei > SimHei
- 合理留白、清晰数据标签、轻量边框
"""
import matplotlib.pyplot as plt
import matplotlib as mpl

# ========== 全局风格 ==========
COLORS = {
    "primary":  "#2E5266",   # 深蓝绿，主标题/正面陈述
    "danger":   "#D72638",   # 红，陷阱/不利
    "success":  "#3FA34D",   # 绿，显著/有效
    "warning":  "#F4A261",   # 橙，中等警示
    "neutral":  "#6C757D",   # 灰，次要/对照
    "muted":    "#ADB5BD",   # 浅灰，背景文字
    "ice":      "#3498DB",   # 蓝，水面上
    "deep":     "#7F8C8D",   # 深灰，水面下
    "bg":       "#FFFFFF",
    "panel":    "#FAFBFC",
}

mpl.rcParams.update({
    "font.sans-serif": ["PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
                        "SimHei", "Arial Unicode MS"],
    "axes.unicode_minus": False,
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": COLORS["muted"],
    "axes.linewidth": 0.8,
    "xtick.color": COLORS["neutral"],
    "ytick.color": COLORS["neutral"],
    "figure.facecolor": COLORS["bg"],
    "savefig.facecolor": COLORS["bg"],
    "savefig.bbox": "tight",
    "savefig.dpi": 150,
})


def _style_ax(ax):
    ax.set_facecolor(COLORS["bg"])
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_color(COLORS["muted"])


# ========== 终点显著性热图 ==========
def plot_endpoint_heatmap(endpoints, save="endpoint_heatmap.png", ax=None):
    """endpoints: list of {name, type:'subjective'|'objective', p, is_primary?}"""
    standalone = ax is None
    if standalone:
        fig, ax = plt.subplots(figsize=(9, 0.55 * len(endpoints) + 1.5))

    for i, e in enumerate(endpoints):
        sig = e["p"] < 0.05
        is_subj = e["type"] == "subjective"
        # 显著主观=橙（可疑），显著客观=绿，不显著=灰
        if sig and is_subj:
            color = COLORS["warning"]
            tag = "主观显著"
        elif sig and not is_subj:
            color = COLORS["success"]
            tag = "客观显著"
        else:
            color = COLORS["muted"]
            tag = "不显著"
        ax.barh(i, 1, color=color, alpha=0.9, height=0.6)
        ax.text(1.04, i, f"p = {e['p']:<6}  {tag}",
                va="center", fontsize=10, color=COLORS["neutral"])

    ax.set_yticks(range(len(endpoints)))
    ax.set_yticklabels([e["name"] for e in endpoints], fontsize=10)
    ax.set_xlim(0, 2.4)
    ax.set_xticks([])
    ax.set_title("终点显著性分布   橙=主观显著(可疑)  绿=客观显著  灰=不显著",
                 loc="left", color=COLORS["primary"], pad=12)
    _style_ax(ax)
    ax.spines["bottom"].set_visible(False)

    if standalone:
        plt.tight_layout()
        plt.savefig(save)
        plt.close()
        return save


# ========== 幸存者偏差冰山图 ==========
def plot_survivorship_iceberg(visible, hidden, save="iceberg.png",
                              visible_label="看到的", hidden_label="被忽略的",
                              ax=None):
    standalone = ax is None
    if standalone:
        fig, ax = plt.subplots(figsize=(7, 7))

    width = 0.55
    ax.bar([0], [visible], width=width, color=COLORS["ice"], zorder=3)
    ax.bar([0], [-hidden], width=width, color=COLORS["deep"], alpha=0.85, zorder=3)
    ax.axhline(0, color=COLORS["primary"], lw=1.8, zorder=4)

    # 标签
    ax.text(0, visible / 2, f"{visible}",
            ha="center", va="center", color="white", fontsize=22, fontweight="bold")
    ax.text(0, visible + max(visible, hidden) * 0.04, visible_label,
            ha="center", color=COLORS["primary"], fontsize=11)
    ax.text(0, -hidden / 2, f"{hidden}\n(沉默)",
            ha="center", va="center", color="white", fontsize=16, fontweight="bold")
    ax.text(0, -hidden - max(visible, hidden) * 0.04, hidden_label,
            ha="center", va="top", color=COLORS["neutral"], fontsize=11)

    # 海平面
    ax.text(0.42, max(visible, hidden) * 0.02, "海平面",
            color=COLORS["primary"], fontsize=9, alpha=0.8)

    # 真实成功率
    rate = visible / (visible + hidden)
    ax.set_title(f"幸存者偏差   真实成功率 ≈ {rate:.1%}",
                 loc="left", color=COLORS["primary"], pad=12)

    ax.set_xticks([])
    ax.set_xlim(-0.6, 0.6)
    ax.set_ylim(-hidden * 1.15, visible * 1.4)
    _style_ax(ax)
    ax.spines["left"].set_visible(False)
    ax.set_yticks([])

    if standalone:
        plt.tight_layout()
        plt.savefig(save)
        plt.close()
        return save


# ========== 辛普森/异质性交叉线图 ==========
def plot_simpson(df, group_col, treat_col, outcome_col, save="simpson.png", ax=None):
    standalone = ax is None
    if standalone:
        fig, ax = plt.subplots(figsize=(9, 6))

    palette = [COLORS["danger"], COLORS["primary"], COLORS["warning"], COLORS["success"]]
    for i, (treat, sub) in enumerate(df.groupby(treat_col)):
        rates = sub.groupby(group_col)[outcome_col].mean()
        color = palette[i % len(palette)]
        ax.plot(rates.index.astype(str), rates.values, "o-",
                color=color, lw=2.5, markersize=10,
                label=f"{treat_col} = {treat}")
        for x, y in zip(rates.index.astype(str), rates.values):
            ax.text(x, y + 0.02, f"{y:.0%}", ha="center", color=color,
                    fontsize=10, fontweight="bold")

    ax.set_xlabel(group_col, fontsize=11, color=COLORS["neutral"])
    ax.set_ylabel(f"{outcome_col} 平均", fontsize=11, color=COLORS["neutral"])
    ax.set_title("分组趋势 vs 整体  ——  人群异质性 / 辛普森悖论",
                 loc="left", color=COLORS["primary"], pad=12)
    ax.legend(frameon=False, loc="best", fontsize=10)
    ax.grid(axis="y", alpha=0.25, linestyle="--")
    _style_ax(ax)

    if standalone:
        plt.tight_layout()
        plt.savefig(save)
        plt.close()
        return save


# ========== 数据/资助污染分解柱图 ==========
def plot_contamination(clean, contaminated, baseline,
                       labels=("宣传分(污染集)", "真实分(干净集)", "对照基线"),
                       ylabel="得分",
                       save="contamination.png", ax=None):
    standalone = ax is None
    if standalone:
        fig, ax = plt.subplots(figsize=(8, 6))

    values = [contaminated, clean, baseline]
    colors = [COLORS["danger"], COLORS["success"], COLORS["muted"]]
    bars = ax.bar(labels, values, color=colors, width=0.55, zorder=3)
    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width() / 2, v + max(values) * 0.02,
                f"{v}", ha="center", color=COLORS["primary"],
                fontsize=12, fontweight="bold")

    # 高估幅度注释
    gap = contaminated - clean
    if gap > 0:
        ax.annotate("",
                    xy=(0, contaminated), xytext=(0, clean),
                    arrowprops=dict(arrowstyle="<->", color=COLORS["danger"], lw=1.5))
        ax.text(0.18, (contaminated + clean) / 2, f"高估 {gap:.1f}",
                color=COLORS["danger"], fontsize=10, fontweight="bold")

    ax.set_ylabel(ylabel, color=COLORS["neutral"])
    ax.set_title("分数分解：宣传 vs 真实 vs 基线",
                 loc="left", color=COLORS["primary"], pad=12)
    ax.grid(axis="y", alpha=0.25, linestyle="--")
    _style_ax(ax)
    ax.set_ylim(0, max(values) * 1.18)

    if standalone:
        plt.tight_layout()
        plt.savefig(save)
        plt.close()
        return save


# ========== 风险拆解条图（ARR / RRR / NNT 一图看清）==========
def plot_risk_breakdown(rate_treat, rate_ctrl, save="risk_breakdown.png",
                        labels=("治疗组", "对照组"), ax=None):
    standalone = ax is None
    if standalone:
        fig, ax = plt.subplots(figsize=(9, 5.5))

    arr = rate_ctrl - rate_treat
    rrr = arr / rate_ctrl if rate_ctrl else 0
    nnt = 1 / arr if arr > 0 else float("inf")

    # 左：两组发生率
    x = [0, 1]
    rates = [rate_ctrl, rate_treat]
    colors = [COLORS["muted"], COLORS["primary"]]
    bars = ax.bar(x, rates, color=colors, width=0.5, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    for b, v in zip(bars, rates):
        ax.text(b.get_x() + b.get_width() / 2, v + max(rates) * 0.02,
                f"{v:.1%}", ha="center", color=COLORS["primary"],
                fontsize=12, fontweight="bold")

    # 标题区显示 ARR / RRR / NNT
    nnt_str = f"{nnt:.0f}" if nnt != float("inf") else "∞"
    summary = (f"ARR(绝对降低) {arr:.2%}    "
               f"RRR(相对降低) {rrr:.0%}    "
               f"NNT(获益人数) {nnt_str}")
    ax.set_title(summary, loc="left", color=COLORS["primary"], pad=12)

    ax.set_ylabel("发生率", color=COLORS["neutral"])
    ax.grid(axis="y", alpha=0.25, linestyle="--")
    _style_ax(ax)
    ax.set_ylim(0, max(rates) * 1.25)

    if standalone:
        plt.tight_layout()
        plt.savefig(save)
        plt.close()
        return save
