#!/usr/bin/env python
"""Study M X5 pre-run check (PLAN_X5 4): synthetic prompts on the real 2 x (6 x 9) x 2-order grid, 10 personas per party, with known beta_e,
beta_s, label bias, crossed item effects and a layer profile; runs decompose, ratio, pigeonhole bootstrap, verdicts A and B. CPU only."""
import numpy as np, pandas as pd
import mech_decision_common as x5

x5.B = 400

def synth(be, bs, rng, N=12, late_ratio=None, lam=1.5):
    """late_ratio: r at intermediate layers (None = same as final). Margins on layer l = ramp(l) * (2 be x_e + 2 bs' x_s) + lam + noise."""
    ie = {e: rng.normal(0, 0.3) for e in x5.ECON}; is_ = {s: rng.normal(0, 0.3) for s in x5.SOC}; rows = []
    ramp = np.linspace(0.05, 1, N)
    for party in ("Democrat", "Republican"):
        for k in range(10):
            pid = f"{party[0]}{k}"; pe = rng.normal(0, 0.3)
            for e in x5.ECON:
                for s in x5.SOC:
                    for fam in ("party_like", "reversed"):
                        for o in (0, 1):
                            own = 1 if party == "Democrat" else -1
                            xe = own * (1 if o == 0 else -1)                 # label A econ: left in order 0 (pkgL); +1 if own
                            xs = xe if fam == "party_like" else -xe
                            m = np.empty(N)
                            for l in range(N):
                                bsl = bs if (late_ratio is None or l >= N - 2) else late_ratio * (be + ie[e] + pe)
                                m[l] = ramp[l] * (2 * (be + ie[e] + pe) * xe + 2 * (bsl + is_[s]) * xs) + lam + rng.normal(0, 0.5)
                            rows.append(dict(pid=pid, party=party, topic=f"{e}|{s}", family=fam, order=o, **{f"m{l}": m[l] for l in range(N)}))
    return pd.DataFrame(rows), [f"m{l}" for l in range(N)]

rng = np.random.default_rng(3); R = 20
for name, (be, bs, late) in {"down (r 0.5)": (2.0, 1.0, None), "ignored (r 0)": (2.0, 0.0, None), "late suppression (mid r 0.8, final 0.3)": (2.0, 0.6, 0.8)}.items():
    vA, vB, cov = {}, {}, 0
    for i in range(R):
        d, cols = synth(be, bs, rng, late_ratio=late)
        out = []
        for p in ("Democrat", "Republican"):
            dd = d[d.party == p].reset_index(drop=True); u, BE, BS = x5.decompose(dd, cols)
            rf = x5.ratio(BE[:, -1:], BS[:, -1:])[0]; bsr = x5.boot_ratio(u, BE[:, -1:], BS[:, -1:], i)[:, 0]; lo, hi = x5.ci(bsr)
            v = x5.verdict_A(lo, hi); vA[v] = vA.get(v, 0) + 1
            I = x5.layer_set(BE, BS, 3, len(cols)); est = x5.delta_r(BE, BS, None, I)
            bb = x5.boot_ratio(u, BE, BS, 100 + i, fn=lambda a, b, w: x5.delta_r(a, b, w, I)); lo2, hi2 = x5.ci(bb)
            v2 = x5.verdict_B(est, lo2, hi2); vB[v2] = vB.get(v2, 0) + 1
    print(f"truth {name}: A {vA}; B {vB}")
