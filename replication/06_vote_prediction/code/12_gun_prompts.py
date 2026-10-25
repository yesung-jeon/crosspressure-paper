#!/usr/bin/env python
"""G2 prompts (A14): the W1 main prompt and its NAY-first swap for every main-sample gun member vote. The prompt functions are taken
verbatim from 02_build_prompts.py (main_prompt and helpers) and 03_build_swap_prompts.py (swap), so the wording is identical to W1.
  python 12_gun_prompts.py   -> out/g2/prompts.parquet, prompts_swap.parquet, summary.json, summary_swap.json
"""
import hashlib, json, re, sys
from pathlib import Path
import pandas as pd

V = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(V.parent / "02_ideology_map" / "code"))
import map_common as dc  # noqa: E402
O = V / "out" / "g2"

ns = {"dc": dc}
src3 = (V / "code" / "02_build_prompts.py").read_text(encoding="utf-8")
exec(re.search(r"^def strip\(t\):.*?(?=^def v1\(r\):)", src3, flags=re.S | re.M).group(0), ns)
src3b = (V / "code" / "03_build_swap_prompts.py").read_text(encoding="utf-8")
exec(re.search(r"^def swap\(t\):.*?(?=^S = M\.copy\(\))", src3b, flags=re.S | re.M).group(0), ns)
main_prompt, swap = ns["main_prompt"], ns["swap"]

rc = pd.read_csv(O / "rollcalls.csv"); rc["year"] = pd.to_datetime(rc.date).dt.year
de = pd.read_csv(O / "descriptions.csv").fillna("")
ver = pd.read_csv(O / "verify.csv"); assert ver["pass"].all() and len(ver) == len(de)
rc = rc[rc["main"]].merge(de[["key", "description", "yea_means", "nay_means", "insufficient"]], on="key", validate="one_to_one")
assert not rc.insufficient.astype(bool).any()
mv = pd.read_csv(O / "member_votes.csv.gz")
mv["key"] = mv.congress.astype(str) + "|" + mv.chamber + "|" + mv.rollnumber.astype(str)
mv = mv[mv["main"]].merge(rc[["key", "year", "description", "yea_means", "nay_means"]], on="key", validate="many_to_one")
mv["issue"] = "guns"; mv["main_sample"] = True; mv["variant"] = "main"
mv["text"] = mv.apply(main_prompt, axis=1)
mv["pid"] = mv.key + "|" + mv.icpsr.astype(str) + "|main"
assert not mv.pid.duplicated().any()
cols = ["pid", "key", "congress", "chamber", "rollnumber", "icpsr", "name", "state", "party", "known", "cp", "vote_q", "issue",
        "motion", "main_sample", "variant", "actual", "party_yea_share", "party_tie", "defect", "year", "text"]
mv[cols].to_parquet(O / "prompts.parquet", index=False)
S = mv[cols].copy(); S["text"] = S.text.map(swap); S["variant"] = "swap"; S["pid"] = S.key + "|" + S.icpsr.astype(str) + "|swap"
S.to_parquet(O / "prompts_swap.parquet", index=False)
for name, T in [("summary.json", mv), ("summary_swap.json", S)]:
    json.dump(dict(rows=len(T), rollcalls=int(T.key.nunique()), text_sha256=hashlib.sha256("".join(T.text).encode()).hexdigest()),
              open(O / name, "w"), indent=1)
print(len(mv), "prompts per order;", mv.key.nunique(), "roll calls"); print(mv.text.iloc[0])
