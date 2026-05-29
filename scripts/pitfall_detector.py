"""规则引擎：汇总所有检测"""
from scripts.stat_analysis import cohens_d, interpret_d, risk_metrics, power_warning


def detect_endpoint_trap(endpoints):
    """软硬终点偷换检测
    endpoints: list of dict(name, type['subjective'/'objective'], p, is_primary)
    """
    flags = []
    subj_sig = [e for e in endpoints if e["type"] == "subjective" and e["p"] < 0.05]
    obj_nonsig = [e for e in endpoints if e["type"] == "objective" and e["p"] >= 0.05]
    if subj_sig and obj_nonsig:
        flags.append({
            "pitfall": "⚠️软硬终点偷换",
            "detail": (f"主观终点显著({[e['name'] for e in subj_sig]})，"
                       f"但客观硬终点不显著({[e['name'] for e in obj_nonsig]})")
        })
    return flags


def detect_relative_risk_trap(rate_treat, rate_ctrl, p_value):
    m = risk_metrics(rate_treat, rate_ctrl)
    flags = []
    if m["RRR"] > 0.3 and m["ARR"] < 0.05:
        flags.append({
            "pitfall": "⚠️相对风险夸大",
            "detail": (f"相对降低 RRR={m['RRR']:.0%}（宣传口径）"
                       f"，但绝对降低 ARR={m['ARR']:.1%}，NNT={m['NNT']:.0f}"
                       f"，p={p_value}")
        })
    return flags


def detect_contamination(clean_score, contaminated_score, threshold=5):
    if contaminated_score - clean_score > threshold:
        return [{
            "pitfall": "⚠️数据泄露/污染",
            "detail": (f"污染集得分{contaminated_score} vs 干净集{clean_score}，"
                       f"高估{contaminated_score-clean_score}分，真实能力以干净集为准")
        }]
    return []


def detect_multiple_comparison(n_tests, reported):
    if n_tests > 5:
        return [{
            "pitfall": "⚠️多重比较未校正",
            "detail": (f"共测{n_tests}项只报告{reported}项；"
                       f"Bonferroni校正后阈值应为 0.05/{n_tests}={0.05/n_tests:.4f}")
        }]
    return []
