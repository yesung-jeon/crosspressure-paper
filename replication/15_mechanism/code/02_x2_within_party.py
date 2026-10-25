#!/usr/bin/env python
"""Study M X2 main run (PLAN_X2.md v0.1). Requires PRE_RUN_SEAL_x2.json. CPU only. Writes out/x2/RESULTS.json."""
import json, time
import numpy as np
import mech_within_common as x2

M = x2.xc.M
assert (M / "protocol" / "PRE_RUN_SEAL_x2.json").exists(), "run pre_seal.py --tag x2 first"
O = M / "out" / f"x2{x2.xc.TAG}"; O.mkdir(parents=True, exist_ok=True)
R = {"plan": "PLAN_X2.md v0.1", "run": time.strftime("%Y-%m-%dT%H:%M"), "B": x2.B, "seed": x2.SEED, "band": x2.BAND, "models": {}}
for k, m in enumerate(["qwen", "llama"]):
    d = x2.within_party(m); x2.check_s4d_baseline(d, m); dall = x2.within_party(m, known_only=False)
    out = {"s4d_baseline_reproduced": True}
    for j, p in enumerate(["Democrat", "Republican"]):
        g = d[d.party == p]; s = lambda gg, t: x2.summarize(gg, [x2.SEED, k, j, t])
        out[p] = {"primary": s(g, 0),
                  "S1_all_rows": s(dall[dall.party == p], 1),
                  "S2_by_era": {era: s(e, 2 + i) for i, (era, e) in enumerate(g.groupby("era"))},
                  "S3_house": s(g[g.chamber == "House"], 9)}
    R["models"][m] = out
json.dump(R, open(O / "RESULTS.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
for m, out in R["models"].items():
    for p in ["Democrat", "Republican"]:
        e, c = out[p]["primary"]["est"], out[p]["primary"]["ci95"]
        print(f"{m} {p[:3]}: b_soc {e['b_soc']:+.3f} {np.round(c['b_soc'], 3)} | b_eco {e['b_eco']:+.3f} {np.round(c['b_eco'], 3)} | gap {e['gap_eco_minus_soc']:+.3f} "
              f"{np.round(c['gap_eco_minus_soc'], 3)} | b_cpl {e['b_cpl']:+.3f} {np.round(c['b_cpl'], 3)} | b_x_ab {e['b_x_ab']:+.3f} | n {out[p]['primary']['n_members']} | {out[p]['primary']['verdict']}")
        print("     S1", out[p]["S1_all_rows"]["verdict"], round(out[p]["S1_all_rows"]["est"]["b_soc"], 3), "| S3", out[p]["S3_house"]["verdict"], round(out[p]["S3_house"]["est"]["b_soc"], 3),
              "| S2", {era: (round(v["est"]["b_soc"], 3), round(v["est"]["b_eco"], 3)) for era, v in out[p]["S2_by_era"].items()})
