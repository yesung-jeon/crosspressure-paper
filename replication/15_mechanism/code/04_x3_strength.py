#!/usr/bin/env python
"""Study M X3 main run (PLAN_X3.md v0.1). Requires PRE_RUN_SEAL_x3.json. CPU only. Writes out/x3/RESULTS.json and out/x3/strength_<model>.csv."""
import json, time
import numpy as np, pandas as pd
import mech_strength_common as x3

M = x3.xc.M
assert (M / "protocol" / "PRE_RUN_SEAL_x3.json").exists(), "run pre_seal.py --tag x3 first"
O = M / "out" / "x3"; O.mkdir(parents=True, exist_ok=True)
R = {"plan": "PLAN_X3.md v0.1", "run": time.strftime("%Y-%m-%dT%H:%M"), "B": x3.B, "seed": x3.SEED, "models": {}}
NAMES = ["a", "b", "c"]
def fit(r, seed, boot="pigeonhole", cols=("z", "psign")):
    est = x3.ols(r, None, cols); bs = (x3.pigeonhole if boot == "pigeonhole" else x3.persona_boot)(r, seed, cols)
    nm = NAMES[:len(cols) + 1]
    return {"est": {k: float(est[i]) for i, k in enumerate(nm)}, "ci95": {k: x3.ci(bs[:, i]) for i, k in enumerate(nm)}, "n_units": int(len(r)),
            "n_nan_draws": int(np.isnan(bs[:, 0]).sum())}
for k, m in enumerate(["qwen", "llama"]):
    x3.check_baseline(m); r, S = x3.units(m)
    S.rename("strength_logit").reset_index().to_csv(O / f"strength_{m}.csv", index=False)
    P = fit(r, [x3.SEED, k, 0]); P["verdict"] = x3.verdict(len(r), P["ci95"]["b"], P["ci95"]["a"])
    P["sd_delta_s_logit"] = float(r.ds.std()); P["b_per_logit"] = P["est"]["b"] / float(r.ds.std())
    sens = {"S1_clip_0.01": fit(x3.units(m, clip=0.01)[0], [x3.SEED, k, 1]),
            "S2_probability_scale": fit(x3.units(m, scale="prob")[0], [x3.SEED, k, 2]),
            "S3_persona_bootstrap": fit(r, [x3.SEED, k, 3], boot="persona")}
    for j, p in enumerate(["Democrat", "Republican"]):
        sens[f"S4_{p}"] = fit(r[r.party == p], [x3.SEED, k, 4 + j], cols=("z",))
    for s in sens.values():
        if "b" in s["ci95"]: s["verdict"] = x3.verdict(s["n_units"], s["ci95"]["b"], s["ci95"]["a"])
    u = pd.read_csv(x3.L / f"out/{m}/tables/units.csv"); n = u[(u.cond == "NONE") & (u.family == "reversed") & (u.party == "none") & u.decided]
    R["models"][m] = {"baseline_reproduced": True, "primary": P, "sensitivity": sens,
                      "descriptive_no_persona_ELST_share": {"share": float((n.pA_n > 0.5).mean()), "decided_units": int(len(n)), "note": "seen before PLAN_X3; not a decision quantity"}}
json.dump(R, open(O / "RESULTS.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
for m, o in R["models"].items():
    p = o["primary"]; e, c = p["est"], p["ci95"]
    print(f"{m}: n {p['n_units']} | a {e['a']:.3f} {np.round(c['a'], 3)} | b {e['b']:+.3f} {np.round(c['b'], 3)} | c {e['c']:+.3f} {np.round(c['c'], 3)} | {p['verdict']}")
    for s, v in o["sensitivity"].items():
        print(f"   {s}: " + " ".join(f"{kk} {v['est'][kk]:+.3f} {np.round(v['ci95'][kk], 3)}" for kk in v["est"]) + (f" | {v['verdict']}" if "verdict" in v else ""))
