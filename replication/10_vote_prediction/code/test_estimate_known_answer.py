#!/usr/bin/env python
"""Known-answer test for estimate_votes.model_frame/twoway (2026-10-20, before any pilot output is read).
A fake model that predicts each member's party majority must give: model accuracy == party-rule accuracy, the same CP coefficient as the
party rule (to 1e-12), and gain_over_party == 0. Fake predictions are written to out/v4/_fake_party/pilot/ and removed afterwards."""
import shutil, sys
from pathlib import Path
import numpy as np, pandas as pd

sys.argv = ["estimate_votes.py"]
sys.path.insert(0, str(Path(__file__).parent))
import estimate_votes as ve  # noqa: E402

P = ve.base_frame(); P = P[(P.variant == "main") & P.main_sample & (P.issue == "abortion") & ~P.party_tie]
D = ve.V / "out" / "v4" / "_fake_party" / "pilot"; D.mkdir(parents=True, exist_ok=True)
maj = (P.party_yea_share > 0.5).astype(float)
pd.DataFrame(dict(pid=P.pid, p_yea=maj * 0.9 + 0.05, p_nay=(1 - maj) * 0.9 + 0.05, p_yea_any=0.0, p_nay_any=0.0, top1_id=0, top1_p=0.0)) \
    .to_parquet(D / "part_0000.parquet", index=False)
try:
    d = ve.model_frame("_fake_party", ["pilot"], known_model="qwen")
    a = ve.twoway(d.assign(y=d.correct)); b = ve.twoway(d.assign(y=d.party_correct))
    ok = (abs(a["b"] - b["b"]) < 1e-12 and abs(a["se"] - b["se"]) < 1e-12 and float(d.gain_over_party.abs().max()) == 0.0
          and d.format_fail.sum() == 0)
    print(dict(model_b=a["b"], party_b=b["b"], model_se=a["se"], party_se=b["se"], max_gain=float(d.gain_over_party.abs().max()),
               dim1_ref_acc=float(d.dim1_correct.mean()), known_share=float(d.known.mean()), PASS=bool(ok)))
    if not ok: raise SystemExit("STOP: known-answer test failed")
finally:
    shutil.rmtree(D.parent)
