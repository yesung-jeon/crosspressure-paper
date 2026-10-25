#!/usr/bin/env python
"""Study M X3 pre-run check (PLAN_X3 6): synthetic decided units on the real 6 x 9 item grid with known a, b, c, run through the same OLS,
pigeonhole bootstrap and verdict. Item-level strengths carry crossed item effects, so the pigeonhole interval is the relevant one. CPU only."""
import numpy as np, pandas as pd
import mech_strength_common as x3

x3.B = 500

def synth(a, b, c, rng, per_cell=5):
    se = {e: rng.normal(0, 1) for e in x3.ECON}; ss = {s: rng.normal(0, 1) for s in x3.SOC}   # item strengths (crossed)
    ie = {e: rng.normal(0, 0.08) for e in x3.ECON}; is_ = {s: rng.normal(0, 0.08) for s in x3.SOC}   # item effects on y beyond strength
    rows = []
    for party, ps in (("Democrat", 1.0), ("Republican", -1.0)):
        for e in x3.ECON:
            for s in x3.SOC:
                ds = se[e] - ss[s] + rng.normal(0, 0.3)
                for k in range(per_cell):
                    p = np.clip(a + b * ds / 1.4 + c * ps + ie[e] + is_[s], 0, 1)
                    rows.append(dict(pid=f"{party[0]}{k}", party=party, e=e, s=s, ds=ds, psign=ps, y=float(rng.random() < p)))
    r = pd.DataFrame(rows); r["z"] = r.ds / r.ds.std(); return r

rng = np.random.default_rng(5); R = 40
for name, (a, b, c) in {"strength": (0.5, 0.15, 0.0), "econ": (0.7, 0.0, 0.0), "lean": (0.5, 0.0, 0.15)}.items():
    vb, va, cov_a, cov_c = {}, {}, 0, 0
    for i in range(R):
        r = synth(a, b, c, rng); est = x3.ols(r); bs = x3.pigeonhole(r, i)
        v = x3.verdict(len(r), x3.ci(bs[:, 1]), x3.ci(bs[:, 0])); vb[v["b"]] = vb.get(v["b"], 0) + 1; va[v["a"]] = va.get(v["a"], 0) + 1
        lo, hi = x3.ci(bs[:, 0]); cov_a += lo <= a <= hi; lo, hi = x3.ci(bs[:, 2]); cov_c += lo <= c <= hi
    print(f"truth {name} (a={a}, b={b}, c={c}): b verdicts {vb}; a verdicts {va}; coverage a {cov_a / R:.2f}, c {cov_c / R:.2f}")
