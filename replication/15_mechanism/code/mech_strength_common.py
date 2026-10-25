"""Study M X3 (PLAN_X3.md): does the stronger single-item commitment win the reversed bundle, and does economics win at equal strength?"""
import json
import numpy as np, pandas as pd
import mech_common as xc

L = xc.K / "04_bundled_choices"
B = 10_000; SEED = 20261020; MIN_UNITS = 100
ECON = ["health", "regulation", "taxes", "unions", "wage", "welfare"]
SOC = ["abortion", "exemption", "faith", "family", "gender", "marriage", "sexed", "transgender", "values"]

def logit(p, clip): p = np.clip(p, clip, 1 - clip); return np.log(p / (1 - p))

def units(model, clip=1e-4, scale="logit"):
    u = pd.read_csv(L / f"out/{model}/tables/units.csv"); u = u[u.cond == "NONE"]
    s = u[(u.family == "single") & u.party.isin(["Democrat", "Republican"])].copy()
    s["str"] = logit(s.own_p.values, clip) if scale == "logit" else s.own_p
    S = s.groupby(["party", "topic"])["str"].mean()
    assert set(S.index.get_level_values(1)) == set(ECON + SOC)
    r = u[(u.family == "reversed") & u.decided & u.party.isin(["Democrat", "Republican"])].copy()
    r[["e", "s"]] = r.topic.str.split("|", expand=True)
    r["ds"] = [S[(p, e)] - S[(p, so)] for p, e, so in zip(r.party, r.e, r.s)]
    r["y"] = (r.winner == "econ").astype(float); r["psign"] = np.where(r.party == "Democrat", 1.0, -1.0)
    r["z"] = r.ds / r.ds.std()      # scaled, not centred: the intercept a is the economic share at delta s = 0 (PLAN_X3 3)
    return r.reset_index(drop=True), S

def check_baseline(model):
    R = json.load(open(L / f"out/{model}/RESULTS.json", encoding="utf-8"))["blockB_natural_cross_pressure"]["tests"]
    r, _ = units(model)
    for p in ["Democrat", "Republican"]:
        g = r[r.party == p]; assert len(g) == R["decided_units_by_party"][p], (model, p)
        assert abs(round(float(g.y.mean()), 3) - R["economic_dominance_share_by_party"][p]) < 1e-9, (model, p)
    return True

def ols(r, w=None, cols=("z", "psign")):
    X = np.column_stack([np.ones(len(r))] + [r[c].values for c in cols]); y = r.y.values
    if w is None: return np.linalg.lstsq(X, y, rcond=None)[0]
    XtW = X.T * w; return np.linalg.solve(XtW @ X, XtW @ y)

def pigeonhole(r, seed, cols=("z", "psign")):
    rng = np.random.default_rng(seed); ei = {e: i for i, e in enumerate(ECON)}; si = {s: i for i, s in enumerate(SOC)}
    E = r.e.map(ei).values; S_ = r.s.map(si).values; out = np.empty((B, len(cols) + 1))
    for b in range(B):
        we = np.bincount(rng.integers(0, 6, 6), minlength=6); ws = np.bincount(rng.integers(0, 9, 9), minlength=9)
        w = (we[E] * ws[S_]).astype(float); keep = w > 0
        try: out[b] = ols(r[keep], w[keep], cols) if keep.sum() > len(cols) + 1 else np.nan
        except np.linalg.LinAlgError: out[b] = np.nan   # 2026-10-18 fix after the first run crashed in S4: singular draws are NaN and counted
    return out

def persona_boot(r, seed, cols=("z", "psign")):
    rng = np.random.default_rng(seed); ids = r.pid.unique(); idx = {p: np.where(r.pid.values == p)[0] for p in ids}; out = np.empty((B, len(cols) + 1))
    for b in range(B):
        pick = rng.choice(ids, len(ids)); rows = np.concatenate([idx[p] for p in pick]); out[b] = ols(r.iloc[rows], None, cols)
    return out

def ci(a): return [float(np.nanpercentile(a, 2.5)), float(np.nanpercentile(a, 97.5))]

def verdict(n, cib, cia):
    if n < MIN_UNITS: return {"b": "not judged (decided units < 100)", "a": "not judged"}
    vb = "strength predicts the winner" if cib[0] > 0 else ("not shown" if cib[1] >= 0 else "weaker commitment wins (unexpected)")
    va = "economic advantage beyond strength" if cia[0] > 0.5 else ("social advantage" if cia[1] < 0.5 else "economic share explained by strength and lean")
    return {"b": vb, "a": va}
