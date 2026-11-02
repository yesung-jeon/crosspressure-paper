#!/usr/bin/env python
"""Known-answer test for estimate_votes.competence (A5): a party-majority predictor must pass; a predictor whose YEA share is pure noise
around 0.5 must fail. Uses the abortion main-sample votes on the 25% roll-call sample (actual votes only)."""
import sys
from pathlib import Path
import numpy as np, pandas as pd

sys.argv = ["estimate_votes.py"]
sys.path.insert(0, str(Path(__file__).parent))
import estimate_votes as ve  # noqa: E402

P = ve.base_frame(); P = P[(P.variant == "main") & P.main_sample & (P.issue == "abortion") & ~P.party_tie]
P = P[P.key.isin(set(pd.read_csv(ve.V / "out" / "v3" / "variant_rollcalls.csv").key))].copy()
rng = np.random.default_rng(1)
P["share_avg"] = np.where(P.party_yea_share > 0.5, 0.8, 0.2); P["correct_avg"] = ((P.share_avg > .5).astype(int) == P.actual).astype(float)
good = ve.competence(P, reps=300)
P["share_avg"] = 0.5 + rng.normal(0, 0.03, len(P)); P["correct_avg"] = ((P.share_avg > .5).astype(int) == P.actual).astype(float)
bad = ve.competence(P, reps=300)
ok = good["competent"] and not bad["competent"]
print(dict(party_predictor=good, noise_predictor=bad, PASS=bool(ok)))
if not ok: raise SystemExit("STOP: competence known-answer test failed")
