"""Estimators and W1 rows used by analyze.py, copied unchanged from the entropy follow-up analysis of 2026-10-29
, so this stage reads only package paths.
oneway = Study N estimator (FE absorbed, one-way CR1 by member); tw = W1 v5.twoway (party x roll-call FE, two-way clustering)."""
import sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import norm

REP = Path(__file__).resolve().parents[2]; V = REP / "10_vote_prediction"
sys.path.insert(0, str(V / "code"))
import estimate_votes as v5  # noqa: E402  (twoway: W1 estimator)
from cluster_fit import cr1_cov  # noqa: E402


def hb(p):
    p = np.clip(np.asarray(p, dtype=float), 1e-12, 1 - 1e-12); return -(p * np.log2(p) + (1 - p) * np.log2(1 - p))


def oneway(d, y, x, fe, cl):
    """Study N estimator (10-22 grid_other.py): FE absorbed, one-way CR1 by cl, K = 1 + FE cells"""
    d = d[[y, x, fe, cl]].dropna()
    g = d.groupby(fe); yt = d[y] - g[y].transform("mean"); xt = d[x] - g[x].transform("mean")
    X = xt.values[:, None]; b = float(np.linalg.lstsq(X, yt.values, rcond=None)[0][0]); u = yt.values - X[:, 0] * b
    Vc, G = cr1_cov(X, u, pd.factorize(d[cl].astype(str))[0])
    n, K = len(d), 1 + d[fe].nunique(); se = float(np.sqrt(Vc[0, 0] * (n - 1) / (n - K)))
    return dict(b=b, se=se, lo95=b - 1.96 * se, hi95=b + 1.96 * se, lo90=b - 1.645 * se, hi90=b + 1.645 * se,
                p=float(2 * norm.sf(abs(b / se))), n=n, clusters=int(G))


def tw(d, y):
    t = v5.twoway(d.assign(y=d[y]))
    return dict(b=t["b"], se=t["se"], lo95=t["ci95"][0], hi95=t["ci95"][1], lo90=t["ci90"][0], hi90=t["ci90"][1],
                p=float(2 * norm.sf(abs(t["b"] / t["se"]))), n=t["n"])


def holm(g, fam):
    g = g.copy(); g["p_holm"] = np.nan
    for _, h in g.groupby(fam):
        p = h.p.fillna(1.0).values; o = np.argsort(p); adj = np.empty(len(p)); run = 0
        for k, i in enumerate(o): run = max(run, min(1, (len(p) - k) * p[i])); adj[i] = run
        g.loc[h.index, "p_holm"] = adj
    return g


def w1_rows(m):
    """W1U rows (R6): abortion, economic from frame_v2; guns (abortion CP) and guns_gcp (gun_cp_loo) from g2; format failures dropped"""
    a = pd.read_parquet(V / "out" / "v5" / f"frame_v2_{m}_abortion_economic.parquet")
    g = pd.read_parquet(V / "out" / "g2" / f"frame_{m}.parquet")
    assert len(a) == 102285 and not a.pid.duplicated().any() and not g.pid.duplicated().any()
    cols = ["pid", "key", "icpsr", "party", "issue", "cp", "fe", "year", "actual", "party_yea_share", "party_tie", "share_yf", "share_nf",
            "share_avg", "pred_yf", "pred_nf", "pred_avg", "correct_avg", "format_fail"]
    a = a[cols]; g0 = g[cols + ["gun_cp_loo"]]
    gg = [g0.drop(columns="gun_cp_loo").assign(issue="guns"),
          g0[g0.gun_cp_loo.notna()].assign(issue="guns_gcp", cp=lambda x: x.gun_cp_loo.astype(int)).drop(columns="gun_cp_loo")]
    d = pd.concat([a] + gg, ignore_index=True)
    d = d[~d.format_fail].copy()
    d["H"] = (hb(d.share_yf) + hb(d.share_nf)) / 2
    d["wrong"] = (d.correct_avg == 0).astype(int)
    return d


def add_plan1(d):
    d = d[~d.party_tie].copy()                                                                   # R1
    maj = d.party_yea_share > 0.5
    d["P_party"] = np.where(maj, d.share_avg, 1 - d.share_avg)
    d["P_party_yf"] = np.where(maj, d.share_yf, 1 - d.share_yf); d["P_party_nf"] = np.where(maj, d.share_nf, 1 - d.share_nf)
    d["act_party"] = (d.actual == maj.astype(int)).astype(float)
    d["o"] = d.P_party - d.act_party; d["o_yf"] = d.P_party_yf - d.act_party; d["o_nf"] = d.P_party_nf - d.act_party
    d["conf"] = (np.maximum(d.share_yf, 1 - d.share_yf) + np.maximum(d.share_nf, 1 - d.share_nf)) / 2  # R2
    d["pred_party"] = (d.pred_avg == maj.astype(int)).astype(int)
    return d
