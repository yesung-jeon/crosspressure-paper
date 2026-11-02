"""Study M X2 (PLAN_X2.md): within-party tracking of the map coordinates. Same sample and standardization as 05_directions_and_map/code/s4d_era.py."""
import json
import numpy as np, pandas as pd
import mech_common as xc

dc = xc.dc
S4D_DIR = {m: f"s4d{xc.TAG}" for m in xc.MODELS}   # rebuild PROTOCOL_GUNSYM
B = 10_000; SEED = 20261019; BAND = 0.10

def within_party(model, known_only=True):
    sc = pd.read_csv(dc.ISSUE_SCALES); sc = sc[sc.issue.isin(["economic", "abortion"]) & (sc.congress >= 93)]
    w = sc.pivot_table(index=["congress", "chamber", "icpsr"], columns="issue", values="rc_score").reset_index().dropna()
    m = pd.read_csv(dc.OUT / model / "s3" / "temporal_member_scores.csv"); m["y"] = -m.social_orth; m["x"] = -m.econ_orth
    keep = m.party.isin(["Democrat", "Republican"]) & (m.known.astype(bool) if known_only else True)
    d = m[keep].merge(w, on=["congress", "chamber", "icpsr"], validate="one_to_one")
    grp = d.groupby(["congress", "chamber", "party"])
    for src, dst in [("y", "z_y"), ("x", "z_x"), ("abortion", "z_ab"), ("economic", "z_ec")]:
        d[dst] = (d[src] - grp[src].transform("mean")) / grp[src].transform("std")
    d = d.dropna(subset=["z_y", "z_x", "z_ab", "z_ec"])
    d["era"] = pd.cut(d.year, [1972, 1989, 2005, 2024], labels=["1973-89", "1991-2005", "2007-23"]).astype(str)
    return d

def member_moments(g):
    """Per member: X'X for X = [z_ab, z_ec] and X'y for y = z_y, z_x. Columns: aa, ae, ee, ay, ey, ax, ex."""
    t = pd.DataFrame({"icpsr": g.icpsr, "aa": g.z_ab ** 2, "ae": g.z_ab * g.z_ec, "ee": g.z_ec ** 2, "ay": g.z_ab * g.z_y, "ey": g.z_ec * g.z_y,
                      "ax": g.z_ab * g.z_x, "ex": g.z_ec * g.z_x})
    return t.groupby("icpsr").sum()

def coefs(s):
    """s: summed moments (aa, ae, ee, ay, ey, ax, ex) -> b_soc, b_cpl (y on ab, ec), b_x_ab, b_eco (x on ab, ec), gap, cpl_minus_soc."""
    XtX = np.array([[s[0], s[1]], [s[1], s[2]]]); by = np.linalg.solve(XtX, [s[3], s[4]]); bx = np.linalg.solve(XtX, [s[5], s[6]])
    return np.array([by[0], by[1], bx[0], bx[1], bx[1] - by[0], by[1] - by[0]])
NAMES = ["b_soc", "b_cpl", "b_x_ab", "b_eco", "gap_eco_minus_soc", "cpl_minus_soc"]

def summarize(g, seed):
    Mm = member_moments(g); A = Mm.values; est = coefs(A.sum(0)); rng = np.random.default_rng(seed); n = len(A); bs = np.empty((B, len(NAMES)))
    for b in range(B):
        w = np.bincount(rng.integers(0, n, n), minlength=n).astype(float); bs[b] = coefs(w @ A)
    ci = {k: [float(np.percentile(bs[:, i], 2.5)), float(np.percentile(bs[:, i], 97.5))] for i, k in enumerate(NAMES)}
    r = {"est": {k: float(est[i]) for i, k in enumerate(NAMES)}, "ci95": ci, "n_rows": int(len(g)), "n_members": int(n)}
    r["verdict"] = verdict(r); r["verdict_old_rule"] = verdict_old_rule(r)
    r["small_social_effect"] = bool(r["ci95"]["b_soc"][0] < BAND)       # lower bound under the 0.10 small-effect line (reported, not a verdict)
    return r

def verdict(r):
    """Author 2026-11-01: the 10-30 rule, no size band. A
    coefficient reads in its direction when its 95% interval excludes zero. Supersedes the PLAN_X2 0.10 band (kept as verdict_old_rule)."""
    lo, hi = r["ci95"]["b_soc"]; glo, ghi = r["ci95"]["gap_eco_minus_soc"]
    if lo > 0 and glo > 0: return "encoded but down-weighted relative to economic (H-E side)"
    if lo > 0 and ghi < 0: return "encoded more strongly than economic"
    if lo > 0: return "encoded as strongly as economic (neither H-E nor H-B)"
    if hi < 0: return "social coefficient negative"
    return "social information not detected within party (H-B side)"

def verdict_old_rule(r):
    """PLAN_X2 v0.1 rule (2026-10-18), superseded 2026-11-01: 0.10 small-effect band"""
    lo, hi = r["ci95"]["b_soc"]; glo = r["ci95"]["gap_eco_minus_soc"][0]
    if lo >= -BAND and hi <= BAND: return "social information erased within party (H-B side)"
    if lo > BAND and glo > 0: return "encoded but down-weighted relative to economic (H-E side)"
    if lo > BAND: return "encoded as strongly as economic (neither H-E nor H-B)"
    return "undetermined"

def check_s4d_baseline(d, model):
    """Frozen baseline: reproduce sealed S4D.json b_ab (economic control) per era and party, and n_rows."""
    ref = json.load(open(dc.OUT / S4D_DIR[model] / "S4D.json", encoding="utf-8"))[model]; k = 0
    for era, e in d.groupby("era"):
        for p in ["Democrat", "Republican"]:
            g = e[e.party == p]; X = g[["z_ab", "z_ec"]].values; b = float(np.linalg.lstsq(X, g.z_y.values, rcond=None)[0][0])
            R = ref[era]["ctrl_econ"][p]; assert abs(b - R["b_ab"]) < 1e-10 and len(g) == R["n_rows"], (model, era, p, b, R["b_ab"]); k += 1
    assert k == 6, k
    return True
