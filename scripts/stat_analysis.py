"""核心统计检验与效应量计算"""
import numpy as np
from scipy import stats


def cohens_d(mean1, mean2, sd1, sd2, n1, n2):
    """计算 Cohen's d 效应量"""
    pooled_sd = np.sqrt(((n1 - 1) * sd1**2 + (n2 - 1) * sd2**2) / (n1 + n2 - 2))
    if pooled_sd == 0:
        return 0.0
    return (mean1 - mean2) / pooled_sd


def interpret_d(d):
    d = abs(d)
    if d < 0.2:
        return "可忽略(<0.2)"
    elif d < 0.5:
        return "小(0.2~0.5)"
    elif d < 0.8:
        return "中(0.5~0.8)"
    return "大(>0.8)"


def risk_metrics(rate_treat, rate_ctrl):
    """ARR / RRR / NNT"""
    arr = rate_ctrl - rate_treat            # 绝对风险降低
    rrr = arr / rate_ctrl if rate_ctrl else 0  # 相对风险降低
    nnt = 1 / arr if arr > 0 else float('inf')
    return {"ARR": arr, "RRR": rrr, "NNT": nnt}


def two_prop_test(x1, n1, x2, n2):
    """两组率的卡方检验，返回 p 值"""
    table = np.array([[x1, n1 - x1], [x2, n2 - x2]])
    chi2, p, dof, exp = stats.chi2_contingency(table, correction=False)
    return p


def power_warning(n_events_treat, n_events_ctrl):
    """低事件数 → 检验效能不足警告"""
    total_events = n_events_treat + n_events_ctrl
    if total_events < 30:
        return f"⚠️事件数仅{total_events}，检验效能不足，'不显著'≠'无差异'"
    return None
