#!/usr/bin/env python
"""Study M X1 pre-run check (PLAN 6): synthetic member-Congress rows with a known destination rule (H-P, H-E, H-U), run through the same
label / summarize / verdict functions. Reports classification and bootstrap coverage of the true d. CPU, no real data."""
import numpy as np, pandas as pd
import mech_common as xc

xc.B = 1000   # smaller bootstrap for the check

def synth(kind, rng, n_mem=(140, 63, 256, 538), rows_per=2, p_miss=0.8, strength=0.85):
    cells = [("Democrat", "ER-SP"), ("Republican", "EL-ST"), ("Democrat", "EL-ST"), ("Republican", "ER-SP")]
    rows, cid = [], 0
    for (party, vq), nm in zip(cells, n_mem):
        for _ in range(nm):
            cid += 1; mem_tilt = rng.normal(0, 0.1)   # member-level dependence
            for _ in range(rows_per):
                if rng.random() > p_miss: mq = vq
                else:
                    own, keep = xc.OWN[party], xc.KEEP_ECON[vq]; other = [q for q in xc.ALIGNED if q != own][0]
                    p_own = {"P": strength, "E": (strength if own == keep else 1 - strength), "U": 0.5}[kind]
                    p_own = min(max(p_own + mem_tilt, 0), 1)
                    mq = own if rng.random() < p_own else other
                rows.append(dict(icpsr=cid, party=party, vote_q=vq, map_q=mq))
    v = pd.DataFrame(rows); v["cl"] = v.icpsr; return v

rng = np.random.default_rng(7); R = 60
for kind, true_d in (("P", 0.85), ("E", 0.15), ("U", 0.5)):
    verd, cover = {}, 0
    for r in range(R):
        v = xc.label(synth(kind, rng)); s = xc.summarize(v, seed=r)
        verd[s["verdict"]] = verd.get(s["verdict"], 0) + 1
        lo, hi = s["ci95"]["d"]; cover += lo <= true_d <= hi
    print(f"truth H-{kind} (d={true_d}): verdicts {verd}; coverage of true d {cover / R:.2f}")
# the synthetic truth uses expected d; member tilt makes the realised d noisy around it, so coverage near 0.95 is the target, not exact
