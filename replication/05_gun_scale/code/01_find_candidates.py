#!/usr/bin/env python
"""G0 step 1 (PROTOCOL_G0.md section 1): gun roll-call candidates and the out-of-regex audit sample. No votes are read.
  python 01_find_candidates.py
"""
import json
from pathlib import Path
import numpy as np, pandas as pd

G = Path(__file__).resolve().parents[1]; KIM = G.parent
O = G / "out" / "g0"; O.mkdir(parents=True, exist_ok=True)
KEY = ["congress", "chamber", "rollnumber"]
RX = r"FIREARM|HANDGUN|\bGUNS?\b|ASSAULT WEAPON|AMMUNITION|BRADY|SECOND AMENDMENT|\bRIFLES?\b|PISTOL|CONCEALED CARRY|GUN SHOW"

rc = pd.read_csv(KIM / "data" / "voteview_all" / "HSall_rollcalls.csv", low_memory=False,
                 usecols=KEY + ["date", "bill_number", "yea_count", "nay_count", "vote_result", "vote_desc", "vote_question", "dtl_desc"])
rc = rc[rc.congress.between(80, 118) & rc.chamber.isin(["House", "Senate"])].copy()
rc["text"] = (rc.vote_desc.fillna("") + " " + rc.vote_question.fillna("") + " " + rc.dtl_desc.fillna("")).str.upper().str.strip()
rc["minority"] = np.minimum(rc.yea_count, rc.nay_count) / (rc.yea_count + rc.nay_count).replace(0, np.nan)
rc["contested"] = rc.minority >= 0.10
rc["key"] = rc.congress.astype(str) + "|" + rc.chamber + "|" + rc.rollnumber.astype(str)
hit = rc.text.str.contains(RX, regex=True)
cand = rc[hit].copy()
cand[["key"] + KEY + ["date", "bill_number", "vote_question", "vote_desc", "dtl_desc", "contested", "minority"]].to_csv(O / "candidates.csv", index=False)

# out-of-regex audit sample: contested, 1990-2018, PAP major topic 12, not matched
# PAP topics through the paper's ledger (01_build_scales.py step 1 maps PAP chamber codes 1/2 to House/Senate; a direct join matches ~5%)
pap = pd.read_csv(KIM / "01_rollcall_scales" / "out" / "data" / "pap_ledger.csv")
pap = pap[pap.status.eq("ok")].rename(columns={"major": "majortopic"})[KEY + ["majortopic"]].drop_duplicates(KEY)
x = rc[~hit & rc.contested].merge(pap, on=KEY, how="left", validate="one_to_one")
x["year"] = pd.to_datetime(x.date, errors="coerce").dt.year
pool = x[(x.majortopic == 12) & x.year.between(1990, 2018)]
aud = pool.sample(min(40, len(pool)), random_state=20261022)
aud[["key", "date", "bill_number", "vote_question", "vote_desc", "dtl_desc"]].to_csv(O / "audit_out_of_regex.csv", index=False)

rep = dict(regex=RX, candidates=int(len(cand)), contested=int(cand.contested.sum()), pap_major12_pool=int(len(pool)),
           pap_merge_rate=float(x.majortopic.notna().mean()), audit_sample=int(len(aud)),
           contested_by_congress_chamber=cand[cand.contested].groupby(["congress", "chamber"]).size().unstack(fill_value=0).to_dict())
json.dump(rep, open(O / "candidates_report.json", "w"), indent=1, default=str)
print({k: v for k, v in rep.items() if k != "contested_by_congress_chamber"})
