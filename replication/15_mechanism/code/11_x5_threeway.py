#!/usr/bin/env python
"""Study M X5, post hoc sensitivity (written after stage-A results were seen; labelled post hoc in ASSESSMENT_X5): the stage-A and stage-B
intervals resampled items only. The X6 synthetic check (PLAN_X6 A0) showed that item-only resampling ignores persona-level variation, so this
recomputes both with the three-way bootstrap (personas x economic items x social items). Verdict rules unchanged; the pre-registered primary
intervals stay the reported verdicts. -> out/x5/SENS_threeway.json"""
import json, sys
import numpy as np, pandas as pd
import mech_decision_common as x5
sys.path.insert(0, str(x5.xc.K / "04_bundled_choices" / "code"))
import bundle_common as lc  # noqa: E402
M = x5.xc.M; O = M / "out" / "x5"; R = {"note": "post hoc; three-way bootstrap", "B": x5.B, "stageA": {}, "stageB": {}}
for k, m in enumerate(["qwen", "llama"]):
    d = x5.load_L_none(m); R["stageA"][m] = {}
    for j, p in enumerate(["Democrat", "Republican"]):
        u, be, bs = x5.decompose(d[d.party == p].reset_index(drop=True), ["m_final"])
        lo, hi = x5.ci(x5.boot_ratio(u, be, bs, [x5.SEED, 70 + k, j], kind="three_way")[:, 0])
        R["stageA"][m][p] = {"r": float(x5.ratio(be, bs)[0]), "ci95": [float(lo), float(hi)], "verdict": x5.verdict_A(lo, hi)}
    files = sorted((O / m / "b1").glob("part_*.csv.gz"))
    if len(files) == 4:
        db = pd.concat([pd.read_csv(f) for f in files], ignore_index=True); cols = sorted([c for c in db.columns if c.startswith("m") and c[1:].isdigit()]); R["stageB"][m] = {}
        for j, p in enumerate(["Democrat", "Republican"]):
            u, be, bs = x5.decompose(db[db.party == p].reset_index(drop=True), cols); I = x5.layer_set(be, bs, lc.layer(m), len(cols))
            est = x5.delta_r(be, bs, None, I); lo, hi = x5.ci(x5.boot_ratio(u, be, bs, [x5.SEED, 80 + k, j], kind="three_way", fn=lambda a, b, w: x5.delta_r(a, b, w, I)))
            R["stageB"][m][p] = {"delta_r": float(est), "ci95": [float(lo), float(hi)], "verdict": x5.verdict_B(est, lo, hi)}
json.dump(R, open(O / "SENS_threeway.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
for s in ("stageA", "stageB"):
    for m, o in R[s].items():
        for p, q in o.items(): print(s, m, p[:3], {k: (np.round(v, 3).tolist() if isinstance(v, (list, float)) else v) for k, v in q.items()})
