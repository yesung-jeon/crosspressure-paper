#!/usr/bin/env python
"""Study M X4 pre-run check: synthetic F and Y on the 6 x 9 pair grid with crossed item effects; true slope per SD of F = 0.08 or 0.
Runs analyze_x4.fit and its verdict; reports classification and coverage. CPU only."""
import numpy as np, pandas as pd
import analyze_x4 as x4
import mech_decision_common as x5

x4.B = 500
rng = np.random.default_rng(8); R = 60
for b_true in (0.08, 0.0):
    verd, cov = {}, 0
    for r in range(R):
        fe = {e: rng.normal(0, 1) for e in x5.ECON}; fs = {s: rng.normal(0, 1) for s in x5.SOC}
        ye = {e: rng.normal(0, 0.04) for e in x5.ECON}; ys = {s: rng.normal(0, 0.04) for s in x5.SOC}
        rows = []
        for e in x5.ECON:
            for s in x5.SOC:
                F = fe[e] + fs[s] + rng.normal(0, 0.7); rows.append(dict(econ=e, soc=s, F=F, Fraw=F))
        t = pd.DataFrame(rows); z = t.F / t.F.std()
        t["Y"] = 0.15 + b_true * z + t.econ.map(ye) + t.soc.map(ys) + rng.normal(0, 0.05, len(t))
        o = x4.fit(t, r); verd[o["verdict"]] = verd.get(o["verdict"], 0) + 1; cov += o["ci95"][0] <= b_true <= o["ci95"][1]
    print(f"true b {b_true}: verdicts {verd}; coverage {cov / R:.2f}")
