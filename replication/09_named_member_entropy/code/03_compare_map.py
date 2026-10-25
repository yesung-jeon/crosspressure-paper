"""Study N gate R1 (PROTOCOL §3): rerun Study D 06_vote_vs_map.py unchanged on the re-projected map (STUDYD_OUT = out/mapout) and compare its
anchors.json and vote_vs_map.json with the sealed ones at the verdict level (compare_to_sealed.py path A tolerances); digit-level
agreement is recorded. Usage: python 03_compare_map.py --model qwen   -> out/<m>/n1_compare.json (exit 1 if the gate fails)"""
import argparse, json, os, subprocess, sys
import numpy as np, pandas as pd
from named_common import dc, MAPOUT, OUT, Q4, ALIGNED, CROSS

ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True, choices=list(dc.MODELS)); a = ap.parse_args()
sub = "s4"
env = dict(os.environ, STUDYD_OUT=str(MAPOUT), PYTHONIOENCODING="utf-8")
r = subprocess.run([sys.executable, "06_vote_vs_map.py", "--models", a.model, "--out", sub], cwd=dc.CODE, env=env, capture_output=True, text=True)
assert r.returncode == 0, r.stderr[-2000:]
new_a, old_a = (json.load(open(p / sub / "anchors.json"))[a.model] for p in (MAPOUT, dc.OUT))
new_v, old_v = (json.load(open(p / sub / "vote_vs_map.json"))[a.model] for p in (MAPOUT, dc.OUT))
rows = {"A3 r(x, dim1)": ("r_x_dim1_by_congress_mean", None), "A4 r(x, economic)": ("r_x_economic_scale_within_cc", 0),
        "A4 r(y, abortion)": ("r_y_abortion_scale_within_cc", 0), "A6 party gap x": ("party_gap_x_d", None), "A6 party gap y": ("party_gap_y_d", None)}
res = {}
for lab, (k, i) in rows.items():
    n, o = (new_a[k][i] if i is not None else new_a[k]), (old_a[k][i] if i is not None else old_a[k])
    res[lab] = dict(new=n, sealed=o, diff=abs(n - o), pass_=abs(n - o) <= 0.05)
for q in Q4:
    n, o = new_v["recall_by_vote_quadrant"][q], old_v["recall_by_vote_quadrant"][q]
    res[f"A9 recall {q}"] = dict(new=n, sealed=o, diff=abs(n - o), pass_=abs(n - o) <= 0.05)
rec = new_v["recall_by_vote_quadrant"]
pattern = min(rec[q] for q in ALIGNED) > max(rec[q] for q in CROSS) and new_a["party_gap_x_d"] > new_a["party_gap_y_d"]
nm = pd.read_csv(MAPOUT / a.model / "s3" / "temporal_member_scores.csv"); om = pd.read_csv(dc.OUT / a.model / "s3" / "temporal_member_scores.csv")
j = nm.merge(om, on=["congress", "chamber", "icpsr"], suffixes=("_n", "_o"), validate="one_to_one")
digits = {"rows": len(j), "identical_econ_orth": bool((j.econ_orth_n == j.econ_orth_o).all()), "identical_social_orth": bool((j.social_orth_n == j.social_orth_o).all()),
          "max_abs_diff_econ": float((j.econ_orth_n - j.econ_orth_o).abs().max()), "max_abs_diff_social": float((j.social_orth_n - j.social_orth_o).abs().max()),
          "r_econ": float(np.corrcoef(j.econ_orth_n, j.econ_orth_o)[0, 1]), "r_social": float(np.corrcoef(j.social_orth_n, j.social_orth_o)[0, 1]),
          "known_agreement": float((j.known_n.astype(bool) == j.known_o.astype(bool)).mean()),
          "vote_map_confusion_identical": new_v["confusion_vote_rows_map_cols"] == old_v["confusion_vote_rows_map_cols"]}
out = {"model": a.model, "rows": res, "pattern_aligned_gt_cross_and_gap_x_gt_y": bool(pattern), "digits": digits,
       "pass_verdict_level": bool(all(v["pass_"] for v in res.values()) and pattern)}
# Rebuild PLAN v0.2 §5.2: the re-projection runs the same bf16 code at the same batch as Study D s3, so the maps must be identical
out["pass"] = bool(out["pass_verdict_level"] and digits["identical_econ_orth"] and digits["identical_social_orth"]
                   and digits["known_agreement"] == 1.0)
(OUT / a.model).mkdir(parents=True, exist_ok=True); dc.atomic_json(out, OUT / a.model / "n1_compare.json"); print(json.dumps({"pass": out["pass"], "digits": digits}))
sys.exit(0 if out["pass"] else 1)
