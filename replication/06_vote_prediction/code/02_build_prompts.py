#!/usr/bin/env python
"""Study V stage 3 (CPU): prompt table for every member vote (PROTOCOL §3). Builds the main prompt for all member votes on the
selected roll calls (main + sensitivity roll calls) and variants V1-V3 for a seeded 25% roll-call sample of the main roll calls.
The table holds user-message text only; each model's chat template is applied in 04_score_votes.py.
Output: out/v3/prompts.parquet (one row per member vote x variant), variant_rollcalls.csv, summary.json"""
import hashlib, json, sys
from pathlib import Path
import numpy as np, pandas as pd

V = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(V.parent / "02_ideology_map" / "code"))
import map_common as dc  # noqa: E402

O = V / "out" / "v3"; O.mkdir(parents=True, exist_ok=True)
KEY = ["congress", "chamber", "rollnumber"]
mv = pd.read_csv(V / "out" / "v0" / "member_votes.csv.gz")
rc = pd.read_csv(V / "out" / "v0" / "rollcalls.csv")
de = pd.read_csv(V / "out" / "v1" / "descriptions.csv").fillna("")
for d in (mv, rc):
    d["key"] = d.congress.astype(str) + "|" + d.chamber + "|" + d.rollnumber.astype(str)
rc = rc.merge(de[["key", "description", "yea_means", "nay_means", "insufficient"]], on="key", how="left", validate="one_to_one")
assert rc.description.ne("").all() and rc.description.notna().all()
rc["year"] = pd.to_datetime(rc.date).dt.year
rc["main_sample"] = rc.main & ~rc.insufficient.astype(bool)
mv = mv.merge(rc[["key", "year", "description", "yea_means", "nay_means", "main_sample"]], on="key", how="left", validate="many_to_one")
assert mv.description.notna().all()

def strip(t): return str(t).strip().rstrip(".")
def title(ch): return "Senator" if ch == "Senate" else "Representative"
def body(ch): return "Senate" if ch == "Senate" else "House of Representatives"
def role(ch): return "senator" if ch == "Senate" else "representative"

def main_prompt(r):
    return (f"You are {title(r.chamber)} {r['name']}, representing {dc.STATES[r.state]} in the United States {body(r.chamber)} in {r.year}.\n"
            f"Consider the following roll-call vote:\n{r.description}\n"
            f"A YEA vote would: {strip(r.yea_means)}.\nA NAY vote would: {strip(r.nay_means)}.\n"
            f"How would you vote, based on your policy positions as this {role(r.chamber)} at that time?\n"
            f"Respond with exactly one word: YEA or NAY.")

def v1(r):
    return (f"{title(r.chamber)} {r['name']} represented {dc.STATES[r.state]} in the United States {body(r.chamber)} in {r.year}.\n"
            f"Consider the following roll-call vote:\n{r.description}\n"
            f"A YEA vote would: {strip(r.yea_means)}.\nA NAY vote would: {strip(r.nay_means)}.\n"
            f"Predict how {r['name']} voted.\nRespond with exactly one word: YEA or NAY.")

def v2(r):
    return (f"You are {title(r.chamber)} {r['name']}, representing {dc.STATES[r.state]} in the United States {body(r.chamber)} in {r.year}.\n"
            f"Consider the following roll-call vote:\n{r.description}\n"
            f"A NAY vote would: {strip(r.nay_means)}.\nA YEA vote would: {strip(r.yea_means)}.\n"
            f"How would you vote, based on your policy positions as this {role(r.chamber)} at that time?\n"
            f"Respond with exactly one word: NAY or YEA.")

def v3(r):
    return (f"It is {r.year}, and you are {r['name']}, a member of the United States {body(r.chamber)} from {dc.STATES[r.state]}. "
            f"The chamber is voting on the following:\n{r.description}\n"
            f"Voting YEA would {strip(r.yea_means)}; voting NAY would {strip(r.nay_means)}.\n"
            f"Given your policy positions at the time, how do you vote? Answer with one word: YEA or NAY.")

# variant roll-call sample: 25% of main roll calls, stratified by issue x decade x chamber, seeded
m = rc[rc.main_sample].copy(); m["decade"] = (m.year // 10) * 10
pick = []
for s, g in m.groupby(["issue", "decade", "chamber"]):
    k = int(round(0.25 * len(g)))
    if k:
        pick += g.sample(k, random_state=dc.seed_for("V-variants", *s) % 2**32).key.tolist()
pd.Series(sorted(pick), name="key").to_csv(O / "variant_rollcalls.csv", index=False)

parts = [mv.assign(variant="main", text=mv.apply(main_prompt, axis=1))]
sub = mv[mv.key.isin(pick)]
for name, f in [("V1", v1), ("V2", v2), ("V3", v3)]:
    parts.append(sub.assign(variant=name, text=sub.apply(f, axis=1)))
P = pd.concat(parts, ignore_index=True)
P["pid"] = P.key + "|" + P.icpsr.astype(str) + "|" + P.variant
assert not P.pid.duplicated().any()
cols = ["pid", "key", "congress", "chamber", "rollnumber", "icpsr", "name", "state", "party", "known", "cp", "vote_q", "issue",
        "motion", "main_sample", "variant", "actual", "party_yea_share", "party_tie", "defect", "year", "text"]
P[cols].to_parquet(O / "prompts.parquet", index=False)
summ = dict(rows=len(P), by_variant=P.variant.value_counts().to_dict(),
            main_sample_main_prompt=int((P.main_sample & P.variant.eq("main")).sum()),
            variant_rollcalls=len(pick), text_sha256=hashlib.sha256("".join(P.text).encode()).hexdigest())
json.dump(summ, open(O / "summary.json", "w"), indent=1)
print(json.dumps(summ, indent=1))
print("--- example ---\n" + P[P.variant.eq("main")].text.iloc[0])
