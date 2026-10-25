#!/usr/bin/env python
"""Study M X5 stage B analysis (PLAN_X5 3 + A1): per-layer decision weights from the batch-1 re-run. Only models whose REPRODUCTION.json passes
the A1 criterion are analysed. Delta r = mean r(l) over the eligible layers I - r(final); I fixed on the full sample; item pigeonhole bootstrap.
-> out/x5/RESULTS_stageB.json, out/x5/r_by_layer_<model>.csv. Usage: python 10_x5_stage_b.py"""
import json, sys, time
import numpy as np, pandas as pd
import mech_decision_common as x5
sys.path.insert(0, str(x5.xc.K / "04_bundled_choices" / "code"))
import bundle_common as lc  # noqa: E402  (layer() only; no model load)

M = x5.xc.M; O = M / "out" / "x5"
R = {"plan": "PLAN_X5.md v0.1 + A0 + A1", "stage": "B (per layer, batch-1 re-run)", "run": time.strftime("%Y-%m-%dT%H:%M"), "B": x5.B, "models": {}}
for k, m in enumerate(["qwen", "llama"]):
    od = O / m / "b1"; rep = od / "REPRODUCTION.json"
    if not rep.exists(): R["models"][m] = {"analysed": False, "reason": "reproduction missing"}; continue
    RP = json.load(open(rep))
    if RP["pass"]: status = "A1 (verdict)"
    elif RP.get("pass_A2_pending_author"): status = "A2 (verdict; approved by the author 2026-10-23, written after the FP8 smokes: post hoc)"
    else: R["models"][m] = {"analysed": False, "reason": "reproduction failed (A1 and A2)"}; continue
    d = pd.concat([pd.read_csv(f) for f in sorted(od.glob("part_*.csv.gz"))], ignore_index=True)
    cols = sorted([c for c in d.columns if c.startswith("m") and c[1:].isdigit()]); N = len(cols); Ls = lc.layer(m)
    out = {"analysed": True, "status": status, "n_layers": N, "steer_layer": Ls, "reproduction": RP}; prof = []
    for j, p in enumerate(["Democrat", "Republican"]):
        dd = d[d.party == p].reset_index(drop=True); u, be, bs = x5.decompose(dd, cols)
        I = x5.layer_set(be, bs, Ls, N); r = x5.ratio(be, bs)
        est = float(np.nanmean(r[I]) - r[-1]) if I else np.nan
        bb = x5.boot_ratio(u, be, bs, [x5.SEED, k, j, 9], fn=lambda a, b, w: x5.delta_r(a, b, w, I)) if I else np.full(x5.B, np.nan)
        lo, hi = x5.ci(bb)
        rf = x5.boot_ratio(u, be[:, -1:], bs[:, -1:], [x5.SEED, k, j, 10])[:, 0]
        out[p] = {"layers_I_1based": [l + 1 for l in I], "delta_r": est, "ci95": [float(lo), float(hi)], "verdict": x5.verdict_B(est, lo, hi) if I else "no eligible layers",
                  "r_final": float(r[-1]), "r_final_ci95": [float(x) for x in x5.ci(rf)], "r_mean_I": float(np.nanmean(r[I])) if I else None,
                  "verdict_final_A_rule": x5.verdict_A(*x5.ci(rf))}
        prof.append(pd.DataFrame({"party": p, "layer": np.arange(1, N + 1), "beta_e": be.mean(0), "beta_s": bs.mean(0), "r": r, "in_I": [l in I for l in range(N)]}))
    pd.concat(prof).to_csv(O / f"r_by_layer_{m}.csv", index=False); R["models"][m] = out
json.dump(R, open(O / "RESULTS_stageB.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
for m, o in R["models"].items():
    if not o["analysed"]: print(m, o["reason"]); continue
    for p in ["Democrat", "Republican"]:
        q = o[p]; print(f"[{o['status']}] {m} {p[:3]}: delta r {q['delta_r']:+.3f} {np.round(q['ci95'], 3)} | r_final {q['r_final']:.3f} {np.round(q['r_final_ci95'], 3)} | mean r(I) {q['r_mean_I']} | I {q['layers_I_1based']} | {q['verdict']}")
