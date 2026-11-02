"""Shared estimators formerly at the top of  (lines above "base = {}"), copied
verbatim apart from paths. grid_other.py itself (the E subgroup grid) is not part of the paper; NOM 02_gmp_fit.py used
to exec this preamble and now imports it. cr1_cov comes from the package's 10_vote_prediction/code/fit.py (the same estimator as cluster_fit.py)."""
import sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import norm

KIM = Path(__file__).resolve().parents[2]                       # replication/
sys.path.insert(0, str(KIM / "10_vote_prediction" / "code")); sys.path.insert(0, str(KIM / "05_directions_and_map" / "code"))
from cluster_fit import cr1_cov  # noqa: E402
import map_common as dc  # noqa: E402

MODELS = list(dc.MODELS)
ALIGNED = ["EL-SP", "ER-ST"]


def hb(p):
    p = np.clip(p, 1e-12, 1 - 1e-12); return -(p * np.log2(p) + (1 - p) * np.log2(1 - p))


def oneway(d, y, x, fe, cl):
    """coefficient on x with FE absorbed (within), one-way CR1 by cl; K = 1 + number of FE cells (as v5.twoway)"""
    d = d[[y, x, fe, cl]].dropna()
    g = d.groupby(fe); yt = d[y] - g[y].transform("mean"); xt = d[x] - g[x].transform("mean")
    X = xt.values[:, None]; b = float(np.linalg.lstsq(X, yt.values, rcond=None)[0][0]); u = yt.values - X[:, 0] * b
    V, G = cr1_cov(X, u, pd.factorize(d[cl].astype(str))[0])
    N, K = len(d), 1 + d[fe].nunique(); se = float(np.sqrt(V[0, 0] * (N - 1) / (N - K)))
    return dict(b=b, se=se, lo95=b - 1.96 * se, hi95=b + 1.96 * se, lo90=b - 1.645 * se, hi90=b + 1.645 * se, p=float(2 * norm.sf(abs(b / se))),
                n=N, clusters=int(G))


def verdict(r):
    if pd.isna(r.get("b")): return "below minimum size"
    # Holm applied
    if (r["lo95"] > 0 or r["hi95"] < 0) and abs(r["b"]) >= 0.05 and r.get("p_holm", 1.0) < 0.05: return "more uncertain" if r["b"] > 0 else "less uncertain"
    if r["lo90"] >= -0.05 and r["hi90"] <= 0.05: return "no meaningful difference"
    return "undetermined"


def holm_by(g, fam):
    for _, h in g.groupby(fam):
        p = h.p.fillna(1.0).values; o = np.argsort(p); adj = np.empty(len(p)); run = 0
        for k, i in enumerate(o): run = max(run, min(1, (len(p) - k) * p[i])); adj[i] = run
        g.loc[h.index, "p_holm"] = adj
    g["verdict"] = [verdict(r) for r in g.to_dict("records")]
    return g
