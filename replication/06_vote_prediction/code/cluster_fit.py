"""Estimation helpers for kim-estimate: fixed-effects OLS with clustered SE, independently reconstructed.

Every fit is checked by recomputing the coefficients (least squares on the same design matrix) and the CR1
cluster-robust covariance by matrix algebra; the call stops if either differs from statsmodels by more than
1e-6 (norm-relative). Each fit saves: the exact input rows (.csv.gz), a spec JSON (formula, clusters, coefficients,
covariance, N, number of clusters), and appends key coefficients to coefficients.csv.

Sources: principles I8 (S08: model and item fixed effects, CR1 clustered on model x item; S04: problem fixed
effects with log length control, clustered by task), A18 (S19: interval fixed effects).
Global rule (2026-10-02): never name a variable `C` in a formula data frame; it shadows patsy's C().

Library use:
    from cluster_fit import fit_fe
    res = fit_fe(df, "score ~ treat + np.log(length) + C(model) + C(item)", cluster=["model", "item"],
                 name="main_steer", out="estimates", key=["treat"])

Mixed-effects models (S20 used model-level random effects) can be fitted with statsmodels MixedLM; they are
not reconstructed here, so report them as a sensitivity alongside an FE specification.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


def _cluster_ids(df, cluster):
    if isinstance(cluster, str):
        cluster = [cluster]
    return pd.Series(pd.factorize(df[cluster].astype(str).agg("|".join, axis=1))[0], index=df.index), cluster


def cr1_cov(X, resid, groups):
    """CR1 cluster-robust covariance: (G/(G-1)) * ((N-1)/(N-K)) * (X'X)^-1 (sum_g X_g'u_g u_g'X_g) (X'X)^-1."""
    N, K = X.shape
    XtX_inv = np.linalg.pinv(X.T @ X)
    G = len(np.unique(groups))
    meat = np.zeros((K, K))
    for g in np.unique(groups):
        m = groups == g
        s = X[m].T @ resid[m]
        meat += np.outer(s, s)
    c = (G / (G - 1)) * ((N - 1) / (N - K))
    return c * XtX_inv @ meat @ XtX_inv, G


def fit_fe(df: pd.DataFrame, formula: str, cluster, name: str, out="estimates", key=None, tol=1e-6):
    import statsmodels.formula.api as smf

    if "C" in df.columns:
        raise ValueError("A column named 'C' shadows patsy's C(); rename it (global rule 2026-10-02).")
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    model = smf.ols(formula, data=df)
    used = df.loc[model.data.row_labels]
    groups, cl_cols = _cluster_ids(used, cluster)
    res = model.fit(cov_type="cluster", cov_kwds={"groups": groups.values, "use_correction": True, "df_correction": True})

    # independent reconstruction
    X = model.exog
    y = model.endog
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    V, G = cr1_cov(X, resid, groups.values)
    b_sm = res.params.values
    V_sm = res.cov_params().values
    # norm-based relative error: elementwise ratios explode for coefficients near zero (P2, 2026-10-03)
    rel = lambda a, b: float(np.linalg.norm(a - b) / max(1e-12, np.linalg.norm(b)))
    err_b, err_V = rel(beta, b_sm), rel(V, V_sm)
    if err_b > tol or err_V > tol:
        raise RuntimeError(f"reconstruction mismatch in {name}: coef rel err {err_b:.2e}, cov rel err {err_V:.2e}")

    used.to_csv(out / f"{name}_input.csv.gz", index=False)
    names = list(res.params.index)
    spec = {"name": name, "formula": formula, "cluster": cl_cols, "n": int(res.nobs), "n_clusters": int(G),
            "coef": dict(zip(names, map(float, b_sm))), "se": dict(zip(names, map(float, res.bse))),
            "cov": V_sm.tolist(), "reconstruction_rel_error": {"coef": err_b, "cov": err_V},
            "cov_type": "CR1 (statsmodels cluster, use_correction & df_correction)"}
    (out / f"{name}_spec.json").write_text(json.dumps(spec, indent=1), encoding="utf-8")
    rows = []
    for k in (key or names):
        if k in res.params.index:
            ci = res.conf_int().loc[k]
            rows.append({"model": name, "term": k, "estimate": float(res.params[k]), "se": float(res.bse[k]),
                         "ci_low": float(ci[0]), "ci_high": float(ci[1]), "p": float(res.pvalues[k]),
                         "n": int(res.nobs), "n_clusters": int(G)})
    coef_path = out / "coefficients.csv"
    pd.DataFrame(rows).to_csv(coef_path, mode="a", header=not coef_path.exists(), index=False)
    return res


if __name__ == "__main__":
    # self-test on simulated data with a known effect
    rng = np.random.default_rng(0)
    n_model, n_item, reps = 3, 40, 10
    d = pd.DataFrame([(m, i, r) for m in range(n_model) for i in range(n_item) for r in range(reps)], columns=["model", "item", "rep"])
    d["treat"] = rng.integers(0, 2, len(d))
    item_eff = rng.normal(0, 1, n_item)[d["item"]]
    d["score"] = 0.5 * d["treat"] + item_eff + 0.3 * d["model"] + rng.normal(0, 1, len(d))
    import tempfile

    with tempfile.TemporaryDirectory() as t:
        r = fit_fe(d, "score ~ treat + C(model) + C(item)", cluster=["model", "item"], name="selftest", out=t, key=["treat"])
        print(f"self-test: treat = {r.params['treat']:.3f} (true 0.5), se = {r.bse['treat']:.3f}; reconstruction passed")
