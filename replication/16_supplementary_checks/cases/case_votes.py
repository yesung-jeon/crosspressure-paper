#!/usr/bin/env python
"""Named cases for the manuscript (Sections 5-6): vote-prediction results for individual cross-pressured members, descriptive only.

For each member in CASES and each model: number of main-sample roll calls by issue, accuracy (order-averaged prediction), and the share
of wrong predictions that go with the member's party majority on that roll call. Also writes every abortion roll call for these members
with its date, bill, the neutral description given to the model, the member's vote, the party majority, and each model's YEA share.
Reads out/v5/frame_v2_<model>_abortion_economic.parquet (format failures excluded), out/v0/rollcalls.csv, out/v1/descriptions.csv.
Members were chosen for the text as well-known cross-pressured legislators (author 2026-10-25), not by their prediction results.
Usage: python 16_supplementary_checks/cases/case_votes.py   -> cases/case_votes.json, cases/case_rollcalls.csv"""
import json
from pathlib import Path
import pandas as pd

R = Path(__file__).resolve().parents[2]; V = R / "06_vote_prediction" / "out"; O = Path(__file__).resolve().parent
CASES = {12104: "Thomas Eagleton", 12107: "Robert Packwood", 14661: "Olympia Snowe"}
rc = pd.read_csv(V / "v0" / "rollcalls.csv")
rc["key"] = rc.congress.astype(str) + "|" + rc.chamber + "|" + rc.rollnumber.astype(str)
ds = pd.read_csv(V / "v1" / "descriptions.csv", usecols=["key", "description"])
out, rows = {}, []
for m in ["qwen", "llama"]:
    d = pd.read_parquet(V / "v5" / f"frame_v2_{m}_abortion_economic.parquet")
    d = d[d.icpsr.isin(list(CASES)) & d.main_sample.astype(bool) & ~d.format_fail.astype(bool)].copy()
    d["party_majority_yea"] = (d.party_yea_share > 0.5).astype(int)
    d["wrong_with_party"] = (d.correct_avg == 0) & (d.pred_avg == d.party_majority_yea)
    for i, name in CASES.items():
        for iss, g in d[d.icpsr == i].groupby("issue"):
            wrong = g[g.correct_avg == 0]
            out.setdefault(name, {}).setdefault(m, {})[iss] = dict(
                n=int(len(g)), accuracy=round(float(g.correct_avg.mean()), 4),
                n_wrong=int(len(wrong)), wrong_with_party_share=round(float(wrong.wrong_with_party.mean()), 4) if len(wrong) else None,
                cross_pressured_share=round(float(g.cp.mean()), 4),
                against_party_share=round(float((g.actual != g.party_majority_yea).mean()), 4))
    a = d[d.issue == "abortion"][["icpsr", "key", "actual", "party_majority_yea", "share_avg", "pred_avg", "correct_avg"]].rename(
        columns={"share_avg": f"yea_share_{m}", "pred_avg": f"pred_{m}", "correct_avg": f"correct_{m}"})
    rows.append(a.set_index(["icpsr", "key", "actual", "party_majority_yea"]))
t = pd.concat(rows, axis=1).reset_index()
t["member"] = t.icpsr.map(CASES)
t = t.merge(rc[["key", "date", "chamber", "bill_number", "yea_count", "nay_count"]], on="key", how="left").merge(ds, on="key", how="left")
assert t.description.notna().all() and t.date.notna().all(), "roll call without metadata"
t.sort_values(["member", "date"]).to_csv(O / "case_rollcalls.csv", index=False)
json.dump(out, open(O / "case_votes.json", "w", encoding="utf-8"), indent=1)
print(json.dumps(out, indent=1))
