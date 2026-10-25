#!/usr/bin/env python
"""G2 stage 0 (W1 extension to gun votes; PLAN v0.7 step 4): the gun roll calls to predict and their member votes.
Roll calls = G0 included gun votes (05_gun_scale/out/g0/included.csv) in Congresses 93-117 (the paper's rows), motion classified with
the W1 rule (01_select_rollcalls.py motion(), copied verbatim); main sample = content motions. Member votes = members of the paper's 10,444
rows (v0 rows), Voteview cast codes 1-3 YEA / 4-6 NAY, party majority as in v0.
  python 10_gun_rollcalls.py   -> out/g2/rollcalls.csv, member_votes.csv.gz, report.json
"""
import json, re
from pathlib import Path
import numpy as np, pandas as pd

V = Path(__file__).resolve().parents[1]; KIM = V.parent
O = V / "out" / "g2"; O.mkdir(parents=True, exist_ok=True)
KEY = ["congress", "chamber", "rollnumber"]
# --- copied from 01_select_rollcalls.py (motion rule fixed 2026-10-20) ---
src = (V / "code" / "01_select_rollcalls.py").read_text(encoding="utf-8")
ns = {"re": re}
for name in ["PROC_Q", "CONTENT_Q", "CONTENT_D", "PROC_D", "RULE_RES"]:
    m = re.search(rf"^{name} = .*?(?=^\w)", src, flags=re.S | re.M); exec(m.group(0), ns)
exec(re.search(r"^def motion\(row\):.*?(?=^irc\[)", src, flags=re.S | re.M).group(0), ns)
motion = ns["motion"]

inc = pd.read_csv(KIM / "05_gun_scale" / "out" / "g0" / "included.csv")
inc = inc[inc.included].copy()
inc[KEY] = inc.key.str.split("|", expand=True); inc["congress"] = inc.congress.astype(int); inc["rollnumber"] = inc.rollnumber.astype(int)
inc = inc[inc.congress.between(93, 117)]
rc = pd.read_csv(KIM / "data" / "voteview_all" / "HSall_rollcalls.csv", low_memory=False,
                 usecols=KEY + ["date", "bill_number", "vote_question", "vote_desc", "dtl_desc", "yea_count", "nay_count", "vote_result"])
sel = inc.merge(rc, on=KEY, how="left", validate="one_to_one")
sel[["motion", "motion_src"]] = sel.apply(lambda r: pd.Series(motion(r)), axis=1)
sel["issue"] = "guns"; sel["main"] = sel.motion.eq("content")
sel.to_csv(O / "rollcalls.csv", index=False)

rows = pd.read_csv(V / "out" / "v0" / "member_votes.csv.gz", usecols=["congress", "chamber", "icpsr", "name", "state", "party", "known", "vote_q", "cp", "dim1"]) \
    .drop_duplicates(["congress", "chamber", "icpsr"])
want = set(map(tuple, sel[KEY].values)); parts = []
for ch in pd.read_csv(KIM / "data" / "voteview_all" / "HSall_votes.csv", usecols=KEY + ["icpsr", "cast_code"], chunksize=4_000_000,
                      dtype={"congress": "int16", "rollnumber": "int32", "icpsr": "int32", "cast_code": "int8"}):
    ch = ch[ch.congress.between(93, 117)]
    if ch.empty: continue
    k = list(zip(ch.congress, ch.chamber, ch.rollnumber)); parts.append(ch[np.fromiter((x in want for x in k), bool, len(k))])
mv = pd.concat(parts, ignore_index=True)
mv = mv[mv.cast_code.between(1, 6)].copy(); mv["actual"] = mv.cast_code.between(1, 3).astype(int)
mv = mv.merge(rows, on=["congress", "chamber", "icpsr"], how="inner", validate="many_to_one")
mv = mv.merge(sel[KEY + ["main", "motion", "final_dir"]], on=KEY, validate="many_to_one")
pm = mv.groupby(KEY + ["party"]).actual.mean().rename("party_yea_share").reset_index()
mv = mv.merge(pm, on=KEY + ["party"], validate="many_to_one")
mv["party_tie"] = mv.party_yea_share.eq(0.5)
mv["defect"] = np.where(mv.party_tie, np.nan, (mv.actual != (mv.party_yea_share > 0.5).astype(int)).astype(float))
mv.to_csv(O / "member_votes.csv.gz", index=False)
rep = dict(rollcalls=int(len(sel)), by_motion=sel.motion.value_counts().to_dict(), main_rollcalls=int(sel.main.sum()),
           by_chamber=sel[sel.main].chamber.value_counts().to_dict(), member_votes=int(len(mv)), main_member_votes=int(mv.main.sum()),
           cp_share_main=float(mv[mv.main].cp.mean()), prompts_two_orders_main=int(2 * mv.main.sum()))
json.dump(rep, open(O / "report.json", "w"), indent=1); print(rep)
