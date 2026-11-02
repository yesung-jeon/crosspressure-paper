#!/usr/bin/env python
"""G2 descriptive diagnostics (not a test; A14 reports a non-competent model without interpreting it): predicted YEA share by option
order, and accuracy by the classified direction of the gun vote (stricter / looser) and party, beside W1's order shares.
  python 14_gun_diagnose.py qwen   -> out/g2/diagnose_{model}.json
"""
import json, sys
from pathlib import Path
import pandas as pd

V = Path(__file__).resolve().parents[1]; O = V / "out" / "g2"
m = sys.argv[1]
d = pd.read_parquet(O / f"frame_{m}.parquet").merge(pd.read_csv(O / "rollcalls.csv")[["key", "final_dir"]], on="key", validate="many_to_one")
w = pd.read_parquet(V / "out" / "v5" / f"frame_v2_{m}_abortion_economic.parquet")
r = lambda s: round(float(s), 4)
out = dict(model=m,
           gun_pred_yea=dict(yea_first=r(d.pred_yf.mean()), nay_first=r(d.pred_nf.mean()), averaged=r(d.pred_avg.mean()), actual=r(d.actual.mean())),
           gun_two_order_corr=r(d[["share_yf", "share_nf"]].corr().iloc[0, 1]),
           w1_pred_yea=dict(yea_first=r(w.pred_yf.mean()), nay_first=r(w.pred_nf.mean()), averaged=r(w.pred_avg.mean()), actual=r(w.actual.mean())),
           by_direction_party={f"{p}|{k}": dict(n=int(len(g)), actual_yea=r(g.actual.mean()), pred_yea=r(g.pred_avg.mean()),
                                                 pred_yea_yea_first=r(g.pred_yf.mean()), accuracy=r(g.correct_avg.mean()))
                               for (p, k), g in d.groupby(["party", "final_dir"])})
json.dump(out, open(O / f"diagnose_{m}.json", "w"), indent=1); print(json.dumps(out, indent=1))
