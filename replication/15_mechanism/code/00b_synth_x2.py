#!/usr/bin/env python
"""Study M X2 pre-run check (PLAN_X2 6): synthetic within-party rows with known coefficients (erased, down-weighted, equal), run through the
same summarize / verdict. Reports classification and bootstrap coverage of the true b_soc. CPU, no real data."""
import numpy as np, pandas as pd
import mech_within_common as x2

x2.B = 1000

def synth(kind, rng, n_mem=400, rows=5):
    b_soc, b_cpl, b_eco = {"erased": (0.0, 0.4, 0.7), "down": (0.25, 0.2, 0.7), "equal": (0.6, 0.0, 0.6)}[kind]
    out = []
    for i in range(n_mem):
        ua, ue = rng.normal(0, 0.8, 2)                 # member-level persistence
        for _ in range(rows):
            # first version had ec = 0.3*ab + ... and y noise 0.7 vs x noise 0.6, so "equal" was not equal after standardization (fixed 2026-10-18)
            ab = ua + rng.normal(0, 0.6); ec = (0.3 * ab if kind != "equal" else 0) + ue + rng.normal(0, 0.6)
            y = b_soc * ab + b_cpl * ec + rng.normal(0, 0.6); x = b_eco * ec + rng.normal(0, 0.6)
            out.append((i, ab, ec, y, x))
    d = pd.DataFrame(out, columns=["icpsr", "z_ab", "z_ec", "z_y", "z_x"])
    for c in ["z_ab", "z_ec", "z_y", "z_x"]: d[c] = (d[c] - d[c].mean()) / d[c].std()
    return d, b_soc

rng = np.random.default_rng(11); R = 50
for kind in ("erased", "down", "equal"):
    verd, cover = {}, 0
    for r in range(R):
        d, _ = synth(kind, rng); s = x2.summarize(d, r); verd[s["verdict"]] = verd.get(s["verdict"], 0) + 1
    print(f"truth {kind}: verdicts {verd}")
# coverage is checked against the large-sample coefficient of the standardized data (one big draw), since standardization rescales the truth
for kind in ("erased", "down"):
    big, _ = synth(kind, np.random.default_rng(99), n_mem=20000); truth = x2.coefs(x2.member_moments(big).values.sum(0))[0]; cov = 0
    for r in range(R):
        d, _ = synth(kind, rng); lo, hi = x2.summarize(d, 1000 + r)["ci95"]["b_soc"]; cov += lo <= truth <= hi
    print(f"{kind}: standardized true b_soc {truth:.3f}; coverage {cov / R:.2f}")
