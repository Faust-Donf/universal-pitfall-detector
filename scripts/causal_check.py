"""因果推断 / 混杂 / 偏差检测"""
import pandas as pd


def detect_simpson(df, group_col, treat_col, outcome_col):
    """辛普森悖论自动检测"""
    overall = df.groupby(treat_col)[outcome_col].mean()
    overall_winner = overall.idxmax()

    subgroup_winners = []
    for g, sub in df.groupby(group_col):
        rate = sub.groupby(treat_col)[outcome_col].mean()
        subgroup_winners.append(rate.idxmax())

    if len(set(subgroup_winners)) == 1 and subgroup_winners[0] != overall_winner:
        return {
            "pitfall": "⚠️辛普森悖论",
            "detail": (f"整体看 [{overall_winner}] 占优，"
                       f"但每个分组都是 [{subgroup_winners[0]}] 占优；"
                       f"混杂变量为 [{group_col}]")
        }
    return None


def detect_survivorship(sample_desc, observed_success, est_fail_ratio=20):
    """幸存者偏差检测 + 估算真实基率"""
    red_flags = ["成功", "幸存", "返航", "上市", "盈利", "存活", "富翁", "暴富"]
    if any(f in sample_desc for f in red_flags):
        hidden_failures = observed_success * est_fail_ratio
        true_rate = observed_success / (observed_success + hidden_failures)
        return {
            "pitfall": "⚠️幸存者偏差",
            "detail": (f"样本仅含存活者({observed_success}例)，"
                       f"被忽略的失败者约{hidden_failures}例；"
                       f"真实成功率≈{true_rate:.1%}（而非直觉上的'很常见'）")
        }
    return None


def bayes_update(prior, sensitivity, false_positive):
    """基率谬误纠正：贝叶斯后验"""
    p_pos = sensitivity * prior + false_positive * (1 - prior)
    posterior = sensitivity * prior / p_pos if p_pos else 0
    return posterior
