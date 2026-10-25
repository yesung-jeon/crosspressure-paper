"""Study M X1 (PLAN.md): shared definitions. Where do missed cross-pressured legislators go?"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd

M = Path(__file__).resolve().parents[1]; K = M.parent; D = K / "02_ideology_map"
sys.path.insert(0, str(D / "code"))
import map_common as dc  # noqa: E402

MODELS = ["qwen", "llama"]
import os
TAG = os.environ.get("SOCIAL_TAG", "")   # rebuild PROTOCOL_GUNSYM: "_guns" = gun scale as the social side (ISSUE_SCALES env)
S4_DIR = {"qwen": f"s4{TAG}", "llama": f"s4{TAG}"}
S5_DIR = {"qwen": "s5", "llama": "s5"}
Q4 = ["EL-SP", "EL-ST", "ER-SP", "ER-ST"]; CROSS = ["EL-ST", "ER-SP"]; ALIGNED = ["EL-SP", "ER-ST"]
OWN = {"Democrat": "EL-SP", "Republican": "ER-ST"}
KEEP_ECON = {"EL-ST": "EL-SP", "ER-SP": "ER-ST"}           # aligned quadrant sharing the economic half
DISCORDANT = {("Democrat", "ER-SP"), ("Republican", "EL-ST")}  # own party = keep social: H-P and H-E disagree
CONCORDANT = {("Democrat", "EL-ST"), ("Republican", "ER-SP")}  # own party = keep economic: H-P and H-E agree
B = 10_000; SEED = 20261018
EQ = (0.40, 0.60); HI, LO = 0.65, 0.35; MIN_MEMBERS = 20

def quad(xhi, yhi):
    return np.where(xhi, "ER-", "EL-").astype(object) + np.where(yhi, "ST", "SP")

def map_rows(model):
    """Vote and map quadrants per member-Congress row, exactly as 02_ideology_map/code/06_vote_vs_map.py (93rd on, D/R, both scales)."""
    sc = pd.read_csv(dc.ISSUE_SCALES); sc = sc[sc.issue.isin(["economic", "abortion"])]
    w = sc.pivot_table(index=["congress", "chamber", "icpsr"], columns="issue", values="rc_score").reset_index()
    m = pd.read_csv(dc.OUT / model / "s3" / "temporal_member_scores.csv")
    assert len(m) == 21288, len(m)
    m["x"], m["y"] = -m.econ_orth, -m.social_orth; m["cc"] = m.congress.astype(str) + m.chamber
    j = m.merge(w, on=["congress", "chamber", "icpsr"], how="left", validate="one_to_one")
    v = j[(j.congress >= 93) & j.party.isin(["Democrat", "Republican"])].dropna(subset=["economic", "abortion"]).copy()
    for c in ["x", "y", "economic", "abortion"]:
        v[f"hi_{c}"] = v[c] > v.groupby("cc")[c].transform("median")
    v["vote_q"] = quad(v.hi_economic.values, v.hi_abortion.values); v["map_q"] = quad(v.hi_x.values, v.hi_y.values)
    return v[["congress", "chamber", "icpsr", "party", "known", "vote_q", "map_q"]].reset_index(drop=True)

def check_map_baseline(v, model):
    """Frozen baseline: reproduce the sealed vote_vs_map.json confusion matrix and recall exactly."""
    ref = json.load(open(dc.OUT / S4_DIR[model] / "vote_vs_map.json", encoding="utf-8"))[model]
    ct = pd.crosstab(v.vote_q, v.map_q).reindex(index=Q4, columns=Q4, fill_value=0)
    assert ref["n"] == len(v), (model, ref["n"], len(v))
    for q in Q4:
        for r in Q4: assert int(ref["confusion_vote_rows_map_cols"][q][r]) == int(ct.loc[q, r]), (model, q, r)
        assert abs(ref["recall_by_vote_quadrant"][q] - float((v[v.vote_q == q].map_q == q).mean())) < 1e-12
    return True

def label(v):
    """Adds cell type and destination flags for cross rows."""
    v = v[v.vote_q.isin(CROSS)].copy()
    v["cell"] = [("disc" if (p, q) in DISCORDANT else "conc") for p, q in zip(v.party, v.vote_q)]
    v["miss"] = v.map_q != v.vote_q
    v["aligned_miss"] = v.miss & v.map_q.isin(ALIGNED)
    v["own"] = v.map_q == v.party.map(OWN)
    v["keep_econ"] = v.map_q == v.vote_q.map(KEEP_ECON)
    return v

def member_counts(v, all_miss_den=False):
    """Per cluster: own-party landings and denominators in discordant and concordant cells."""
    den = v.miss if all_miss_den else v.aligned_miss
    g = pd.DataFrame({"cl": v.cl, "disc_own": (v.cell == "disc") & den & v.own, "disc_n": (v.cell == "disc") & den,
                      "conc_own": (v.cell == "conc") & den & v.own, "conc_n": (v.cell == "conc") & den}).groupby("cl").sum()
    return g

def stats_from(g, w=None):
    s = g.mul(w, axis=0).sum() if w is not None else g.sum()
    d = s.disc_own / s.disc_n if s.disc_n else np.nan; c = s.conc_own / s.conc_n if s.conc_n else np.nan
    return {"d": d, "c": c, "party_pull": (c + d) / 2 - 0.5, "econ_pull": (c - d) / 2}

def boot_stats(g, seed):
    rng = np.random.default_rng(seed); n = len(g); A = g.values.astype(float); out = np.empty((B, 4))
    for b in range(B):
        w = np.bincount(rng.integers(0, n, n), minlength=n).astype(float); s = w @ A
        d = s[0] / s[1] if s[1] else np.nan; c = s[2] / s[3] if s[3] else np.nan
        out[b] = (d, c, (c + d) / 2 - 0.5, (c - d) / 2)
    return out

def summarize(v, seed, all_miss_den=False):
    g = member_counts(v, all_miss_den); est = stats_from(g); bs = boot_stats(g, seed)
    ci = {k: [float(np.nanpercentile(bs[:, i], 2.5)), float(np.nanpercentile(bs[:, i], 97.5))] for i, k in enumerate(["d", "c", "party_pull", "econ_pull"])}
    disc_members = int(v[(v.cell == "disc")].cl.nunique())
    return {"est": {k: float(x) for k, x in est.items()}, "ci95": ci, "n_disc_rows_den": int(g.disc_n.sum()), "n_conc_rows_den": int(g.conc_n.sum()),
            "n_disc_members": disc_members, "n_clusters": int(len(g)), "verdict": verdict(est["d"], ci["d"], disc_members)}

def verdict(d, ci, n_members):
    if n_members < MIN_MEMBERS: return "not judged (discordant members < 20)"
    lo, hi = ci
    if d >= HI and lo > 0.5: return "H-P supported over H-E"
    if d <= LO and hi < 0.5: return "H-E supported over H-P"
    if lo >= EQ[0] and hi <= EQ[1]: return "consistent with H-U (equivalence range)"
    return "undetermined"

def destinations(v):
    t = v.groupby(["party", "vote_q", "map_q"]).size().rename("rows").reset_index()
    return t

# ---- S5 profiles ----
def s5_table(model):
    T = pd.read_csv(dc.OUT / S5_DIR[model] / f"s5_conditions_{model}.csv")
    cx = T.groupby("mode").x.transform("mean"); cy = T.groupby("mode").y.transform("mean")
    T["arr_q"] = quad((T.x - cx).values > 0, (T.y - cy).values > 0)
    hit = ((((T.x - cx) > 0) == T.profile.str.startswith("ER")) & (((T.y - cy) > 0) == T.profile.str.endswith("ST"))).astype(float)
    assert np.array_equal(hit.values, T.hit.values), model     # frozen baseline: sealed hit column reproduces
    return T
