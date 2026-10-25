#!/usr/bin/env python
"""Study M X4 analysis (PLAN_X4.md): pair familiarity gap F vs reversed - party-like entropy Y (no persona: primary; persona: S2).
Item pigeonhole bootstrap. -> out/x4/RESULTS.json. Usage: python analyze_x4.py"""
import json, time
import numpy as np, pandas as pd
from scipy.stats import rankdata
import mech_decision_common as x5

M = x5.xc.M; O = M / "out" / "x4"; B = 10_000; SEED = 20261022
EI = {e: i for i, e in enumerate(x5.ECON)}; SI = {s: i for i, s in enumerate(x5.SOC)}

def fam_gap(D, col):
    w = D.pivot_table(index=["econ", "soc"], columns=["e_side", "s_side"], values=col)
    F = 0.5 * (w[("L", "P")] + w[("R", "T")]) - 0.5 * (w[("L", "T")] + w[("R", "P")]); return F.rename("F").reset_index()

def outcome(model, persona):
    u = pd.read_csv(x5.L / f"out/{model}/tables/units.csv"); u = u[(u.cond == "NONE") & u.family.isin(["party_like", "reversed"])]
    u = u[u.party == "none"] if not persona else u[u.party.isin(["Democrat", "Republican"])]
    w = u.groupby(["topic", "family"]).final_H.mean().unstack("family"); y = (w.reversed - w.party_like).rename("Y").reset_index()
    y[["econ", "soc"]] = y.topic.str.split("|", expand=True); return y[["econ", "soc", "Y"]]

def slope(F, Y, w):
    x = (F - np.average(F, weights=w)); return float(np.sum(w * x * (Y - np.average(Y, weights=w))) / np.sum(w * x * x))

def fit(t, seed, rank=False):
    F = t.F.values.copy(); Y = t.Y.values.copy()
    if rank: F, Y = rankdata(F), rankdata(Y)
    z = F / F.std(); e_i = t.econ.map(EI).values; s_i = t.soc.map(SI).values; rng = np.random.default_rng(seed)
    est = slope(z, Y, np.ones(len(t))); bs = np.empty(B); mf = np.empty(B)
    for b in range(B):
        w = (np.bincount(rng.integers(0, 6, 6), minlength=6)[e_i] * np.bincount(rng.integers(0, 9, 9), minlength=9)[s_i]).astype(float)
        bs[b] = slope(z, Y, w) if np.var(z[w > 0]) > 0 else np.nan; mf[b] = np.average(t.F.values, weights=w)
    lo, hi = np.nanpercentile(bs, [2.5, 97.5])
    v = "familiarity gap predicts reversed-bundle uncertainty" if lo > 0 else ("opposite direction" if hi < 0 else "not shown")
    return {"b_per_sd": est, "ci95": [float(lo), float(hi)], "verdict": v, "mean_F": float(t.F.mean()), "mean_F_ci95": [float(x) for x in np.percentile(mf, [2.5, 97.5])], "n_pairs": int(len(t))}

if __name__ == "__main__":
    R = {"plan": "PLAN_X4.md v0.1", "run": time.strftime("%Y-%m-%dT%H:%M"), "B": B, "seed": SEED, "models": {}}
    for k, m in enumerate(["qwen", "llama"]):
        if not (O / m / "clause_logprob.csv").exists():   # 2026-10-18: the chain was stopped by the system (low memory) before OLMo
            R["models"][m] = {"analysed": False, "reason": "clause scores missing (chain stopped by the system for low memory)"}; continue
        D = pd.read_csv(O / m / "clause_logprob.csv")
        t = fam_gap(D, "lp_sum").merge(outcome(m, False), on=["econ", "soc"], validate="one_to_one"); assert len(t) == 54
        tm = fam_gap(D, "lp_mean").merge(outcome(m, False), on=["econ", "soc"]); tp = fam_gap(D, "lp_sum").merge(outcome(m, True), on=["econ", "soc"])
        R["models"][m] = {"primary": fit(t, [SEED, k, 0]), "S1_token_mean": fit(tm, [SEED, k, 1]), "S2_persona_outcome": fit(tp, [SEED, k, 2]), "S3_spearman": fit(t, [SEED, k, 3], rank=True)}
        t.to_csv(O / f"pairs_{m}.csv", index=False)
    json.dump(R, open(O / "RESULTS.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    for m, o in R["models"].items():
        if o.get("analysed") is False: print(m, o["reason"]); continue
        p = o["primary"]; print(f"{m}: b {p['b_per_sd']:+.3f} {np.round(p['ci95'], 3)} | mean F {p['mean_F']:+.2f} {np.round(p['mean_F_ci95'], 2)} | {p['verdict']}")
        for s in ("S1_token_mean", "S2_persona_outcome", "S3_spearman"): print(f"   {s}: b {o[s]['b_per_sd']:+.3f} {np.round(o[s]['ci95'], 3)} | {o[s]['verdict']}")
