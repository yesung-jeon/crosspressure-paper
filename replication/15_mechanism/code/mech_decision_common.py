"""Study M X5 (PLAN_X5.md): decision weights of the economic and social commitments from the 2x2 (family x order) design.
m* = m * sgn (oriented toward the own-party economic passage; pkgL is always economic-left); order means cancel the label bias;
beta_e = (M_PL + M_REV) / 4, beta_s = (M_PL - M_REV) / 4 per persona x item pair; r = mean beta_s / mean beta_e."""
import numpy as np, pandas as pd
import mech_common as xc

L = xc.K / "04_bundled_choices"
B = 10_000; SEED = 20261021; BAND = 0.10
ECON = ["health", "regulation", "taxes", "unions", "wage", "welfare"]
SOC = ["abortion", "exemption", "faith", "family", "gender", "marriage", "sexed", "transgender", "values"]
KEYS = ["pid", "party", "topic", "family", "order"]

def load_L_none(model):
    d = pd.concat([pd.read_csv(f) for f in sorted((L / f"out/{model}/main").glob("part_*.csv.gz"))], ignore_index=True)
    d = d[(d.cond == "NONE") & d.party.isin(["Democrat", "Republican"]) & d.family.isin(["party_like", "reversed"])]
    return d[KEYS + ["m_final", "DL", "flips", "pA", "pB"]].reset_index(drop=True)

def sgn(d): return np.where((d.party == "Democrat") == (d.order == 0), 1.0, -1.0)

def decompose(d, cols):
    """d: one row per prompt with columns KEYS + cols (margins). Returns units (pid, party, topic, e, s) and arrays be, bs of shape (units, len(cols))."""
    X = d[cols].values * sgn(d)[:, None]
    t = pd.DataFrame(X, columns=cols); t[KEYS] = d[KEYS].values
    g = t.groupby(["pid", "party", "topic", "family"])[cols].mean()
    n = t.groupby(["pid", "party", "topic", "family"]).size(); assert (n == 2).all(), "each unit needs both orders"
    PL = g.xs("party_like", level="family"); RV = g.xs("reversed", level="family")
    PL, RV = PL.align(RV, join="inner"); assert len(PL) == len(g) // 2, "every pair needs both families"
    be = (PL.values + RV.values) / 4; bs = (PL.values - RV.values) / 4
    u = PL.index.to_frame(index=False); u[["e", "s"]] = u.topic.str.split("|", expand=True)
    return u, be, bs

def item_index(u):
    return u.e.map({e: i for i, e in enumerate(ECON)}).values, u.s.map({s: i for i, s in enumerate(SOC)}).values

def ratio(be, bs, w=None):
    if w is None: return bs.mean(0) / be.mean(0)
    return (w @ bs) / (w @ be)

def boot_ratio(u, be, bs, seed, kind="pigeonhole", fn=None):
    """bootstrap of fn(be, bs, w) (default: r per column). pigeonhole over items, or persona clusters."""
    fn = fn or ratio; rng = np.random.default_rng(seed); E, S = item_index(u); P = pd.factorize(u.pid)[0]; nP = P.max() + 1; out = []
    for b in range(B):
        if kind == "pigeonhole":
            w = (np.bincount(rng.integers(0, 6, 6), minlength=6)[E] * np.bincount(rng.integers(0, 9, 9), minlength=9)[S]).astype(float)
        elif kind == "three_way":   # 2026-10-18 (X6 A0): personas x economic items x social items
            w = (np.bincount(rng.integers(0, 6, 6), minlength=6)[E] * np.bincount(rng.integers(0, 9, 9), minlength=9)[S]
                 * np.bincount(rng.integers(0, nP, nP), minlength=nP)[P]).astype(float)
        else:
            w = np.bincount(rng.integers(0, nP, nP), minlength=nP)[P].astype(float)
        out.append(fn(be, bs, w))
    return np.array(out)

def ci(a, axis=0): return np.nanpercentile(a, [2.5, 97.5], axis=axis)

def verdict_A(lo, hi):
    if hi < BAND: return "social commitment ignored or negligible at the decision"   # A0 (pre-run): was CI within +-0.10; too strict for 9 social items
    if lo > BAND and hi < 1: return "social commitment down-weighted at the decision"
    if lo > BAND and hi >= 1 and lo < 1: return "equal weight not excluded"
    if lo >= 1: return "social commitment heavier"
    return "undetermined"

def layer_set(be, bs, Lsteer, N):
    """eligible layers (0-based columns): Lsteer-1 .. N-3 (1-based Lsteer .. N-2) with total weight >= 10% of the final layer's"""
    T = be.mean(0) + bs.mean(0); return [l for l in range(Lsteer - 1, N - 2) if T[l] >= 0.10 * T[-1]]

def delta_r(be, bs, w, I):
    r = ratio(be, bs, w); return np.nanmean(r[I]) - r[-1]

def verdict_B(est, lo, hi):
    if est >= BAND and lo > 0: return "social weight larger in intermediate readout, reduced at output (late suppression)"
    if lo > -BAND and hi < BAND: return "no late suppression"
    if est <= -BAND and hi < 0: return "social weight grows late"
    return "undetermined"
