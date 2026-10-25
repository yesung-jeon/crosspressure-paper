#!/usr/bin/env python
"""W1 order dependence: correlation between the YEA share read in the YEA-first order and in the NAY-first order, over the member votes
of the main sample, per model and issue (the 'two-order correlation' in RELEASE_2026-10-21b, caveat 1). Reads the order-averaged frames
written by estimate_votes.py --select v2 (out/v5/frame_v2_<model>_abortion_economic.parquet); format failures are excluded.
Usage: python 16_supplementary_checks/w1/order_corr.py [--root DIR]   -> 16_supplementary_checks/w1/order_corr.json"""
import json, sys
from pathlib import Path
import pandas as pd

R = Path(__file__).resolve().parents[2]
root = Path(sys.argv[sys.argv.index("--root") + 1]) if "--root" in sys.argv else R / "06_vote_prediction"
out = {}
for m in ["qwen", "llama"]:
    d = pd.read_parquet(root / "out" / "v5" / f"frame_v2_{m}_abortion_economic.parquet", columns=["issue", "share_yf", "share_nf", "format_fail"])
    d = d[~d.format_fail]
    out[m] = {i: round(float(g.share_yf.corr(g.share_nf)), 4) for i, g in d.groupby("issue")}
json.dump(out, open(Path(__file__).with_name("order_corr.json"), "w", encoding="utf-8"), indent=1)
print(json.dumps(out))
