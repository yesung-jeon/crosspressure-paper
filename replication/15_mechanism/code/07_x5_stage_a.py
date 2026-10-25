#!/usr/bin/env python
"""Study M X5 stage A (PLAN_X5 2), CPU: decision weights from Study L's sealed final-layer margins (NONE). Requires PRE_RUN_SEAL_x5.json.
-> out/x5/RESULTS_stageA.json"""
import json, time
import numpy as np
import mech_decision_common as x5

M = x5.xc.M
assert (M / "protocol" / "PRE_RUN_SEAL_x5.json").exists(), "run pre_seal.py --tag x5 first"
O = M / "out" / "x5"; O.mkdir(parents=True, exist_ok=True)
R = {"plan": "PLAN_X5.md v0.1 + A0", "stage": "A (final layer, sealed Study L m_final)", "run": time.strftime("%Y-%m-%dT%H:%M"), "B": x5.B, "seed": x5.SEED, "models": {}}
def summ(u, be, bs, seed, kind="pigeonhole"):
    r = float(x5.ratio(be, bs)[0]); b = x5.boot_ratio(u, be, bs, seed, kind)[:, 0]; lo, hi = x5.ci(b)
    return {"r": r, "ci95": [float(lo), float(hi)], "beta_e": float(be.mean()), "beta_s": float(bs.mean()), "n_units": int(len(u)), "verdict": x5.verdict_A(lo, hi)}
for k, m in enumerate(["qwen", "llama"]):
    d = x5.load_L_none(m); out = {}
    for j, p in enumerate(["Democrat", "Republican"]):
        dd = d[d.party == p].reset_index(drop=True); u, be, bs = x5.decompose(dd, ["m_final"])
        dc = dd.assign(m_final=dd.m_final.clip(-10, 10)); uc, bec, bsc = x5.decompose(dc, ["m_final"])
        o = {"primary": summ(u, be, bs, [x5.SEED, k, j, 0]), "S1_clip10": summ(uc, bec, bsc, [x5.SEED, k, j, 1]),
             "S2_persona_bootstrap": summ(u, be, bs, [x5.SEED, k, j, 2], "persona")}
        # S3 per order: beta from one order only (label bias not cancelled; descriptive)
        for oo in (0, 1):
            t = dd[dd.order == oo].copy(); t["m_final"] = t.m_final * x5.sgn(t)
            g = t.groupby(["pid", "topic", "family"]).m_final.mean().unstack("family")
            o[f"S3_order{oo}"] = {"r": float(((g.party_like - g.reversed) / 4).mean() / ((g.party_like + g.reversed) / 4).mean())}
        # S4 label bias lambda = mean over orders of raw m (oriented sum cancels); describe its size relative to beta_e
        lam = dd.groupby(["pid", "topic", "family"]).m_final.mean()
        o["S4_label_bias_mean"] = float(lam.mean()); o["S4_label_bias_sd"] = float(lam.std())
        out[p] = o
    R["models"][m] = out
json.dump(R, open(O / "RESULTS_stageA.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
for m, o in R["models"].items():
    for p in ["Democrat", "Republican"]:
        q = o[p]["primary"]
        print(f"{m} {p[:3]}: r {q['r']:.3f} {np.round(q['ci95'], 3)} (beta_e {q['beta_e']:.2f}, beta_s {q['beta_s']:.2f}, n {q['n_units']}) | {q['verdict']}")
        print(f"    S1 {o[p]['S1_clip10']['r']:.3f} {np.round(o[p]['S1_clip10']['ci95'], 3)} | S2 {np.round(o[p]['S2_persona_bootstrap']['ci95'], 3)} | S3 {o[p]['S3_order0']['r']:.3f} / {o[p]['S3_order1']['r']:.3f} | lambda {o[p]['S4_label_bias_mean']:+.2f} (sd {o[p]['S4_label_bias_sd']:.2f})")
