#!/usr/bin/env python
"""G0 step 2c (PROTOCOL_G0 section 2): compare Claude and GPT labels and write the author's review file.
Rows for the author: (a) every disagreement on gun_control or yea_direction; (b) 20 random agreed inclusions; (c) the 40 out-of-regex
audit roll calls. The file shows the roll-call text only (no vote counts beyond what the text itself says, no model output).
  python g0_review.py
"""
import json
from pathlib import Path
import pandas as pd

G = Path(__file__).resolve().parents[1]; O = G / "out" / "g0"
t = pd.read_csv(O / "contested_texts.csv")
c = pd.read_csv(O / "labels_claude.csv").fillna("")
g = pd.read_csv(O / "labels_gpt.csv").fillna("")
assert g.parse_ok.all() and len(g) == len(c) == len(t)
d = t.merge(c, on="key", validate="1:1").merge(g[["key", "gun_control", "yea_direction", "reason"]], on="key", suffixes=("_claude", "_gpt"),
                                                 validate="1:1")
d["agree"] = (d.gun_control_claude == d.gun_control_gpt) & (d.yea_direction_claude == d.yea_direction_gpt)
d["included_if_agreed"] = d.agree & (d.gun_control_claude == "yes") & d.yea_direction_claude.isin(["stricter", "looser"])
dis = d[~d.agree].assign(review="disagreement")
samp = d[d.included_if_agreed].sample(20, random_state=20261022).assign(review="audit of agreed inclusion")
oor = pd.read_csv(O / "audit_out_of_regex.csv").fillna("")
oor["t"] = (oor.vote_question + " || " + oor.vote_desc + " || " + oor.dtl_desc).str.replace(r"\s+", " ", regex=True)
oor = oor[["key", "t"]].assign(review="out-of-regex audit (is this a gun-control vote?)")
cols = ["review", "key", "t", "gun_control_claude", "yea_direction_claude", "gun_control_gpt", "yea_direction_gpt", "reason"]
R = pd.concat([dis[cols], samp[cols], oor.reindex(columns=cols)], ignore_index=True).fillna("")
R["author_gun_control"] = ""; R["author_yea_direction"] = ""; R["author_note"] = ""
R.to_csv(O / "AUTHOR_REVIEW.csv", index=False, encoding="utf-8-sig")
d.to_csv(O / "labels_merged.csv", index=False)
k = pd.crosstab(d.gun_control_claude + "/" + d.yea_direction_claude, d.gun_control_gpt + "/" + d.yea_direction_gpt)
rep = dict(n=len(d), agree=int(d.agree.sum()), agree_share=round(float(d.agree.mean()), 3),
           agree_gun_control=round(float((d.gun_control_claude == d.gun_control_gpt).mean()), 3),
           included_if_agreed=int(d.included_if_agreed.sum()), disagreements=int((~d.agree).sum()),
           author_rows=dict(disagreement=len(dis), audit_included=len(samp), out_of_regex=len(oor)), crosstab=k.to_dict())
json.dump(rep, open(O / "agreement.json", "w"), indent=1)
print({x: y for x, y in rep.items() if x != "crosstab"}); print(k)
