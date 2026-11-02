#!/usr/bin/env python
"""Scale competence and scale error warning.
CPU only; reads sealed stage 06, 08, 17 and 22 inputs; writes ../out/scale_checks.json.
  python scale_checks.py            # C1-C3 (C2 for the 1-9 named task only when its scoring has finished)"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd

H = Path(__file__).resolve().parents[1]; O = H / "out"; REP = H.parent
sys.path.insert(0, str(H / "code")); sys.path.insert(0, str(REP / "17_error_warning" / "code"))
sys.path.insert(0, str(REP / "16_scale_uncertainty" / "code"))
_argv = sys.argv; sys.argv = ["scale_accuracy.py"]
import scale_accuracy as SA  # noqa: E402  (frames, add_scale, scale_votes; v5 = estimate_votes; dc = map_common)
import error_warning as EW  # noqa: E402  (frame, metrics, boot_diff, hb)
import analyze_named9 as N9  # noqa: E402  (member_frame)
sys.argv = _argv
v5, dc = SA.v5, SA.dc
L2 = np.log2


def scale_entropy(m):
    """pid -> mean over the two directions of the 9-digit entropy / log2 9 (as 16_scale_uncertainty analyze.dist)."""
    D = SA.S17 / m; fs = sorted(D.glob("part_*.done"))
    df = pd.concat([pd.read_parquet(f.with_suffix(".parquet")) for f in fs], ignore_index=True)
    P = df[[f"p{k}" for k in range(1, 10)]].values; Q = P / P.sum(1)[:, None]
    df["Hs"] = -(np.where(Q > 0, Q * L2(np.clip(Q, 1e-300, None)), 0)).sum(1) / L2(9)
    return df.groupby("pid").Hs.mean()


def stage22_sample(m):
    """The stage 22 sample: format failures dropped, both scale directions present and valid."""
    w, _ = SA.scale_votes(m); a, g = SA.frames(m)
    A = SA.add_scale(a[~a.format_fail].copy(), w); G = SA.add_scale(g[~g.format_fail].copy(), w)
    return A[~A.scale_missing & ~A.scale_fail].copy(), G[~G.scale_missing & ~G.scale_fail].copy()


def member_boot(v, g, seed, reps=2000):
    s = pd.DataFrame(dict(v=v, g=g)).groupby("g").v.agg(["sum", "count"]); rng = np.random.default_rng(seed % 2**32)
    bs = [s["sum"].values[k].sum() / s["count"].values[k].sum() for k in (rng.integers(0, len(s), len(s)) for _ in range(reps))]
    return float(s["sum"].sum() / s["count"].sum()), np.percentile(bs, [2.5, 97.5]).tolist()


def warning(d, m, iss, tag):
    rng = np.random.default_rng(dc.seed_for(tag, m, iss) % 2**32)
    m1, m0 = EW.metrics(d[d.cp == 1]), EW.metrics(d[d.cp == 0]); ci = EW.boot_diff(d, rng)
    return dict(cp=m1, aligned=m0, diff={k: m1[k] - m0[k] for k in ci}, diff_ci95=ci)


out = dict(protocol="PROTOCOL_scale_checks_2026-11-01.md", C1={}, C2={}, C3={}, gate={})
for m in SA.MODELS:
    # code check: the reused functions reproduce the sealed binary AUROC
    f = EW.frame(m); fa = f[f.issue == "abortion"].reset_index(drop=True); sealed = json.load(open(REP / f"17_error_warning/out/w1_warning_{m}.json"))
    dev = max(abs(EW.metrics(fa[fa.cp == c])["auroc_within"] - sealed["by_issue"]["abortion"][k]["auroc_within"]) for c, k in ((1, "cp"), (0, "aligned")))
    out["gate"][m] = dev
    if dev > 1e-12: raise SystemExit(f"STOP: AUROC code check {m} {dev}")
    A, G = stage22_sample(m)
    # C1: A5 competence on the scale answers
    out["C1"][m] = {}
    for iss, d in (("abortion", A[A.issue == "abortion"]), ("economic", A[A.issue == "economic"]), ("guns", G)):
        out["C1"][m][iss] = v5.competence(d.reset_index(drop=True), share="s_yea", correct="correct_scale")
    # C2: Study N competence on the named-member scale answers
    out["C2"][m] = {}
    for task, n in (("named", 7), ("named9", 9)):
        if not (REP / "16_scale_uncertainty" / "out" / task / m / "run.json").exists(): out["C2"][m][task] = "not scored yet"; continue
        d, _ = N9.member_frame(m, task, n); al = d[d.vote_cp == 0]
        est, ci = member_boot(al.C_scale.values, al.icpsr.values, dc.seed_for("N-scale-comp", m, task))
        fail = float(d.fail_share_y.mean())
        out["C2"][m][task] = dict(aligned_C_scale=est, ci95=ci, format_fail=fail, competent=bool(ci[0] > 0.5 and fail < 0.10))
    # C3: scale error warning on the stage 22 abortion sample
    Hs = scale_entropy(m); d = A[A.issue == "abortion"].reset_index(drop=True)
    d["Hs"] = d.pid.map(Hs); assert d.Hs.notna().all()
    out["C3"][m] = dict(n=len(d),
                        scale_entropy_vs_scale_errors=warning(d.assign(H=d.Hs, err=1 - d.correct_scale), m, "abortion", "EW-scale"),
                        scale_entropy_vs_binary_errors=warning(d.assign(H=d.Hs, err=1 - d.correct_avg), m, "abortion", "EW-scale-binerr"))
    c = out["C3"][m]["scale_entropy_vs_scale_errors"]
    print(m, "C1", {i: r["competent"] for i, r in out["C1"][m].items()}, "C2", {t: (r if isinstance(r, str) else r["competent"]) for t, r in out["C2"][m].items()},
          "C3 AUROC within aligned/cp", round(c["aligned"]["auroc_within"], 3), round(c["cp"]["auroc_within"], 3),
          "diff CI", [round(x, 3) for x in c["diff_ci95"]["auroc_within"]], flush=True)
json.dump(out, open(O / "scale_checks.json", "w"), indent=1, default=float)
