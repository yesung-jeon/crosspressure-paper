#!/usr/bin/env python
"""Study M X5 stage-B reproduction baseline (PLAN_X5 3): compare re-run final-layer margins and decision layers with Study L's NONE rows.
Criteria: |delta m_final| <= 0.05 for >= 99% of prompts and final-layer sign agreement >= 99.5%. Usage: python 09_x5_reproduce.py --model qwen [--smoke]
Prints and returns the summary; exits non-zero if a criterion fails."""
import argparse, json, sys
import numpy as np, pandas as pd
import mech_decision_common as x5

ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True); ap.add_argument("--smoke", action="store_true")
ap.add_argument("--batch", type=int, default=1)    # A1: batch-1 outputs and the revised criterion (sign >= 99.5%, r >= 0.99); rebuild runs stage B only
a = ap.parse_args()
od = x5.xc.M / "out" / "x5" / a.model / ("b1" if a.batch == 1 else "") / ("smoke" if a.smoke else "")
new = pd.concat([pd.read_csv(f) for f in sorted(od.glob("part_*.csv.gz"))], ignore_index=True)
old = x5.load_L_none(a.model)
m = new.merge(old, on=x5.KEYS, suffixes=("_new", "_L"), validate="one_to_one")
assert len(m) == len(new), (len(m), len(new))
dm = (m.m_final_new - m.m_final_L).abs()
res = {"model": a.model, "smoke": a.smoke, "n": int(len(m)), "share_abs_dm_le_0.05": float((dm <= 0.05).mean()), "max_abs_dm": float(dm.max()),
       "sign_agreement": float((np.sign(m.m_final_new) == np.sign(m.m_final_L)).mean()), "DL_agreement": float((m.DL_new == m.DL_L).mean())}
res["pearson_r"] = float(np.corrcoef(m.m_final_new, m.m_final_L)[0, 1])
big = m.m_final_L.abs() > 3.5
res["sign_agreement_abs_mL_gt_3.5"] = float((np.sign(m.m_final_new[big]) == np.sign(m.m_final_L[big])).mean()); res["n_abs_mL_gt_3.5"] = int(big.sum())
res["pass_A2_pending_author"] = res["sign_agreement_abs_mL_gt_3.5"] >= 0.995 and res["pearson_r"] >= 0.99
if a.batch == 1: res["criterion"] = "A1: sign >= 0.995 and r >= 0.99"; res["pass"] = res["sign_agreement"] >= 0.995 and res["pearson_r"] >= 0.99
else: res["criterion"] = "v0.1: share |dm| <= 0.05 >= 0.99 and sign >= 0.995"; res["pass"] = res["share_abs_dm_le_0.05"] >= 0.99 and res["sign_agreement"] >= 0.995
json.dump(res, open(od / "REPRODUCTION.json", "w"), indent=1); print(json.dumps(res))
sys.exit(0)   # rebuild: a failed reproduction is a registered outcome (that model is not analysed in stage B; 10_x5_stage_b.py), not a pipeline error
