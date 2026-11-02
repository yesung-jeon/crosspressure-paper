"""DW-NOMINATE 2-D benchmark without the abortion-based orientation of dimension 2.
Read-only: rebuilds the rows of 08_supplementary_checks/benchmark/benchmark_recall.py (same scales, same split_hi medians), gates the
oriented recall against the sealed benchmark_recall{,_guns}.json, then recomputes recall with dimension 2 as published (no sign change).
Writes 08_supplementary_checks/benchmark/dw2_orientation.json. Pipeline step checks.dw2_orientation."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd

R = Path(__file__).resolve().parents[2]; H = Path(__file__).resolve().parent   # package-relative (sealed 2026-11-01)
sys.path.insert(0, str(R / "00_shared")); from splits import split_hi  # noqa: E402
sys.path.insert(0, str(R / "05_directions_and_map" / "code")); import map_common as dc  # noqa: E402
Q = ["EL-SP", "ER-ST", "EL-ST", "ER-SP"]; AL, CR = Q[:2], Q[2:]
quad = lambda hx, hy: pd.Series(np.where(hx, "ER-", "EL-"), index=hx.index) + np.where(hy, "ST", "SP")


def recall(v, col):
    r = {q: float((v[v.vote_q == q][col] == q).mean()) for q in Q}
    r["aligned_pooled"] = float((v[v.vote_q.isin(AL)][col] == v[v.vote_q.isin(AL)].vote_q).mean())
    r["cross_pooled"] = float((v[v.vote_q.isin(CR)][col] == v[v.vote_q.isin(CR)].vote_q).mean()); r["n"] = int(len(v)); return r


out = {}
for issue, scales, tag in (("abortion", R / "01_rollcall_scales/out/data/issue_scales.csv", ""),
                           ("guns", R / "03_gun_inputs/out/issue_scales_guns.csv", "_guns")):
    sc = pd.read_csv(scales); sc = sc[sc.issue.isin(["economic", "abortion"])]      # the gun file stores the gun scale as "abortion"
    w = sc.pivot_table(index=["congress", "chamber", "icpsr"], columns="issue", values="rc_score").reset_index()
    m = pd.read_csv(R / "05_directions_and_map" / "out" / dc.REF / "s3" / "temporal_member_scores.csv"); m["cc"] = m.congress.astype(str) + m.chamber
    v = m.merge(w, on=["congress", "chamber", "icpsr"], how="left", validate="one_to_one")
    v = v[(v.congress >= 93) & v.party.isin(["Democrat", "Republican"])].dropna(subset=["economic", "abortion"]).copy()
    for c in ["economic", "abortion"]: v[f"hi_{c}"] = split_hi(v[c], v.cc)
    v["vote_q"] = quad(v.hi_economic, v.hi_abortion)
    sign = v.groupby("cc").apply(lambda g: np.sign(np.corrcoef(g.dim2, g.abortion)[0, 1]) or 1.0, include_groups=False)
    res = {}
    for label, d2 in (("oriented (sealed procedure)", v.dim2 * v.cc.map(sign)), ("dimension 2 as published", v.dim2)):
        v["hi_d1"] = split_hi(v.dim1, v.cc); v["hi_d2"] = split_hi(d2, v.cc); v["nom_q"] = quad(v.hi_d1, v.hi_d2)
        res[label] = recall(v, "nom_q")
    sealed = json.load(open(R / f"08_supplementary_checks/benchmark/benchmark_recall{tag}.json"))["N1_dwnominate"]["recall"]
    gate = max(abs(res["oriented (sealed procedure)"][k] - sealed[k]) for k in sealed if k != "n")
    assert gate < 1e-12, (issue, gate)
    flipped = [c for c, s in sign.items() if s < 0]
    out[issue] = dict(cells=int(len(sign)), flipped_cells=flipped,
                      rows_in_flipped_cells=int(v.cc.isin(flipped).sum()), gate_vs_sealed=gate, **res)
    print(issue, "cells", len(sign), "flipped", flipped, "rows there", out[issue]["rows_in_flipped_cells"])
    for label, r in res.items():
        print(f"   {label:28s} aligned {r['aligned_pooled']:.3f}  cross-pressured {r['cross_pooled']:.3f}  n {r['n']}")
json.dump(out, open(H / "dw2_orientation.json", "w"), indent=1)
