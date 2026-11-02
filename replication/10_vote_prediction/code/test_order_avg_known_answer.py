#!/usr/bin/env python
"""Known-answer test for estimate_votes.order_avg_frame (A4, before any NAY-first output exists).
Fake model: YEA-first answer = YEA always (position bias); NAY-first answer = NAY always, each with p 0.9; but both halves tilt by 0.08
toward the party majority. Averaging must cancel the position bias, so the averaged prediction equals the party majority, the CP
coefficient equals the party rule's exactly, and the YEA-first-only prediction is all YEA. Fake files are removed afterwards."""
import shutil, sys
from pathlib import Path
import numpy as np, pandas as pd

sys.argv = ["estimate_votes.py"]
sys.path.insert(0, str(Path(__file__).parent))
import estimate_votes as ve  # noqa: E402

P = ve.base_frame(); P = P[(P.variant == "main") & P.main_sample & (P.issue == "abortion") & ~P.party_tie]
root = ve.V / "out" / "v4" / "_fake_order"
maj = (P.party_yea_share > 0.5).astype(float).values
tilt = np.where(maj == 1, 0.08, -0.08)
def write(sel, p_yea, pid):
    D = root / sel; D.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(dict(pid=pid, p_yea=p_yea, p_nay=1 - p_yea, p_yea_any=0.0, p_nay_any=0.0, top1_id=0, top1_p=0.0)).to_parquet(D / "part_0000.parquet", index=False)
try:
    write("pilot", 0.9 + tilt * 0.5, P.pid.values)                                   # YEA-first: 0.86 or 0.94 -> always YEA
    write("swap_abortion", 0.1 + tilt * 0.5, P.pid.str.replace(r"\|main$", "|swap", regex=True).values)   # NAY-first: 0.06 or 0.14
    d = ve.order_avg_frame("_fake_order", ("abortion",), known_model="qwen")
    a = ve.twoway(d.assign(y=d.correct_avg)); b = ve.twoway(d.assign(y=d.party_correct))
    ok = (len(d) == len(P) and abs(a["b"] - b["b"]) < 1e-12 and float(d.pred_yf.mean()) == 1.0 and float(d.pred_nf.mean()) == 0.0
          and bool((d.pred_avg == (d.party_yea_share > 0.5).astype(int)).all()))
    print(dict(n=len(d), avg_b=a["b"], party_b=b["b"], pred_yea_first=float(d.pred_yf.mean()), pred_nay_first=float(d.pred_nf.mean()), PASS=bool(ok)))
    if not ok: raise SystemExit("STOP: order-average known-answer test failed")
finally:
    shutil.rmtree(root)
