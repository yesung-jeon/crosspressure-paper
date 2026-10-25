#!/usr/bin/env python
"""A12 selection report (rebuild PLAN v0.2 §4.8; author decision 2026-10-23: the 60-legislator sample is a fixed input).
The A12 text codes (out/s4b and out/s4c coding_codes.csv) are fixed data keyed to the original selections, which stay in out/s4b and
out/s4c. 07a_reselect_deepest.py and 07b_reselect_by_votes.py rerun the selection rule on this run's maps into out/s4b_reselect and out/s4c_reselect; this
script reports whether the rule picks the same members and which fixed members this run's models no longer recognize. It never stops
the run. -> 02_ideology_map/out/selection_report.json"""
import json
from pathlib import Path
import pandas as pd
R = Path(__file__).resolve().parents[1]; D = R / "02_ideology_map" / "out"
rep = {}
for s in ("s4b", "s4c"):
    fixed = pd.read_csv(D / s / "selection.csv"); new = pd.read_csv(D / f"{s}_reselect" / "selection.csv")
    a, b = set(fixed.icpsr), set(new.icpsr)
    rep[s] = {"fixed_n": len(a), "reselected_n": len(b), "same_members": a == b, "only_fixed": sorted(a - b), "only_reselected": sorted(b - a)}
fx = pd.concat([pd.read_csv(D / s / "selection.csv") for s in ("s4b", "s4c")])[["icpsr", "name", "first", "last"]].drop_duplicates("icpsr")
for m in ("qwen", "llama"):           # share of each fixed member's map rows (first..last) that this run's model recognizes (party recalled)
    sc = pd.read_csv(D / m / "s3" / "temporal_member_scores.csv", usecols=["year", "icpsr", "known"])
    j = fx.merge(sc, on="icpsr", how="left"); j = j[j.year.between(j["first"], j["last"])]
    share = j.groupby(["icpsr", "name"]).known.apply(lambda s: float(s.astype(bool).mean())).reset_index()
    share = fx[["icpsr", "name"]].merge(share, on=["icpsr", "name"], how="left").fillna({"known": 0.0}) \
        .sort_values(["icpsr", "name"]).reset_index(drop=True)   # a fixed member with no map row counts as never recognized (Codex round 3)
    rep[f"{m}_fixed_members_recognized_share"] = {"n_members": int(len(share)), "never_recognized": share[share.known == 0][["icpsr", "name"]].values.tolist(),
                                                 "mean_share": float(share.known.mean())}
json.dump(rep, open(D / "selection_report.json", "w"), indent=1, default=int)
print(json.dumps({s: rep[s]["same_members"] for s in ("s4b", "s4c")}))
