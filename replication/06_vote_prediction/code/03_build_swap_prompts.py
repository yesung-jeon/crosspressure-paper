#!/usr/bin/env python
"""Study V stage 3b (protocol v2, amendment A4): the NAY-first prompt for every main-sample member vote, for order averaging.
Built from the sealed main prompt by the V2 rule only: the YEA and NAY lines change places and the answer instruction reads
"NAY or YEA". Checked against the sealed V2 prompts where they exist (25% sample): texts must be identical.
Output: out/v3/prompts_swap.parquet (pid = <key>|<icpsr>|swap), summary_swap.json"""
import hashlib, json
from pathlib import Path
import pandas as pd

V = Path(__file__).resolve().parents[1]
cols = ["pid", "key", "congress", "chamber", "rollnumber", "icpsr", "name", "state", "party", "known", "cp", "vote_q", "issue",
        "motion", "main_sample", "variant", "actual", "party_yea_share", "party_tie", "defect", "year", "text"]
M = pd.read_parquet(V / "out" / "v3" / "prompts.parquet", columns=cols, filters=[("variant", "==", "main"), ("main_sample", "==", True)])
V2 = pd.read_parquet(V / "out" / "v3" / "prompts.parquet", columns=["key", "icpsr", "text"], filters=[("variant", "==", "V2")])

def swap(t):
    lines = t.split("\n")
    iy = [i for i, l in enumerate(lines) if l.startswith("A YEA vote would:")]
    inn = [i for i, l in enumerate(lines) if l.startswith("A NAY vote would:")]
    assert len(iy) == 1 and len(inn) == 1 and inn[0] == iy[0] + 1, t[:200]
    lines[iy[0]], lines[inn[0]] = lines[inn[0]], lines[iy[0]]
    assert lines[-1] == "Respond with exactly one word: YEA or NAY."
    lines[-1] = "Respond with exactly one word: NAY or YEA."
    return "\n".join(lines)

S = M.copy(); S["text"] = S.text.map(swap); S["variant"] = "swap"
S["pid"] = S.key + "|" + S.icpsr.astype(str) + "|swap"
chk = S.merge(V2, on=["key", "icpsr"], suffixes=("", "_v2"))
same = (chk.text == chk.text_v2)
assert same.all(), f"{(~same).sum()} swap prompts differ from sealed V2"
S[cols].to_parquet(V / "out" / "v3" / "prompts_swap.parquet", index=False)
summ = dict(rows=len(S), by_issue=S.issue.value_counts().to_dict(), checked_against_V2=int(len(chk)), identical=int(same.sum()),
            text_sha256=hashlib.sha256("".join(S.text).encode()).hexdigest())
json.dump(summ, open(V / "out" / "v3" / "summary_swap.json", "w"), indent=1); print(json.dumps(summ, indent=1))
