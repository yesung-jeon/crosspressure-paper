"""Estimators for Studies S and D: FE (within) OLS with several regressors and member-clustered CR1 whose K counts every regressor
plus the FE cells (M88); equals the Study N `oneway` for a single regressor (asserted in check()). W1 uses estimate_votes.twoway."""
import sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import norm

KIM = Path(__file__).resolve().parents[2]                       # replication/ (rebuild); cluster_fit.py is the package copy
sys.path.insert(0, str(KIM / "06_vote_prediction" / "code"))
from cluster_fit import cr1_cov  # noqa: E402
import estimate_votes as v5  # noqa: E402


def fe_ols(d, y, xs, fe, cl):
    """coefficients on xs with fe absorbed; CR1 by cl with K = len(xs) + number of FE cells. Returns {x: dict(b, se, ci95, p)} + n, clusters"""
    xs = [xs] if isinstance(xs, str) else list(xs)
    e = d[[y, *xs, fe, cl]].dropna()
    g = e.groupby(fe); Y = (e[y] - g[y].transform("mean")).values
    X = np.column_stack([(e[x] - g[x].transform("mean")).values for x in xs])
    b = np.linalg.lstsq(X, Y, rcond=None)[0]; u = Y - X @ b
    V, G = cr1_cov(X, u, pd.factorize(e[cl].astype(str))[0])
    N, k, nf = len(e), len(xs), e[fe].nunique(); V = V * (N - k) / (N - k - nf)
    out = {}
    for i, x in enumerate(xs):
        se = float(np.sqrt(V[i, i])); bi = float(b[i])
        out[x] = dict(b=bi, se=se, ci95=[bi - 1.96 * se, bi + 1.96 * se], p=float(2 * norm.sf(abs(bi / se))))
    out["_n"], out["_clusters"], out["_fe_cells"] = int(N), int(G), int(nf)
    return out


def check():
    """single-regressor equality with the Study N oneway (entropy_warning grid_other.py)"""
    sys.path.insert(0, str(KIM / "08_error_warning" / "code"))
    import fe_estimators; ns = vars(fe_estimators)                    # rebuild: the grid_other.py preamble as a module
    rng = np.random.default_rng(3); n = 3000
    d = pd.DataFrame(dict(fe=rng.integers(0, 40, n).astype(str), cl=rng.integers(0, 300, n), x=rng.normal(size=n)))
    d["y"] = 0.3 * d.x + rng.normal(size=n) + d.fe.astype(int) * 0.01
    a = ns["oneway"](d, "y", "x", "fe", "cl"); b = fe_ols(d, "y", ["x"], "fe", "cl")["x"]
    assert abs(a["b"] - b["b"]) < 1e-12 and abs(a["se"] - b["se"]) < 1e-12, (a, b)
    return True
