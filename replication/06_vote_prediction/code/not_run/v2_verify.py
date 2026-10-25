#!/usr/bin/env python
"""Study V stage 2: independent check of the written roll-call descriptions by GPT-4.1-mini (a different model family from the writer;
Kim C7). The author approved GPT-4.1-mini for this check on 2026-10-20. Calls are cached and logged (kim-kit llm_ledger.py), temperature 0,
JSON output. The key comes from crosspressure/.env (OPENAI_API_KEY); it is never passed on the command line.

For each roll call the checker sees Voteview's source text and the written description with its YEA/NAY meanings, and answers six
yes/no questions plus a short reason. A row passes only if all six are clean. Failing rows go back to the writer (overrides) and are
re-checked; the check never edits descriptions itself.

  python v2_verify.py            -> out/v2/verify.csv, summary.json; ledger in out/v2/ledger/
  python v2_verify.py --limit 5  -> smoke test on five rows
"""
import argparse, json, sys
from pathlib import Path
import pandas as pd

V = Path(__file__).resolve().parents[1]
REPO = V.parents[1]
sys.path.insert(0, str(Path.home() / ".claude" / "kim-kit" / "scripts"))
from llm_ledger import Ledger  # noqa: E402

MODEL = "gpt-4.1-mini-2025-04-14"          # pinned, same as the project's earlier judge (.env.example)
O = V / "out" / "v2"; O.mkdir(parents=True, exist_ok=True)
CHECKS = ["faithful", "no_added_facts", "no_outcome", "no_actor", "neutral", "yea_nay_correct"]

SYSTEM = ("You audit short descriptions of U.S. congressional roll-call votes written for a research prompt. You compare each "
          "description with the official source text. Answer only from the texts given. Reply with JSON only.")
TEMPLATE = """SOURCE (Voteview record)
vote_question: {vote_question}
bill_number: {bill_number}
vote_desc: {vote_desc}
dtl_desc: {dtl_desc}

WRITTEN
description: {description}
A YEA vote would: {yea_means}
A NAY vote would: {nay_means}

Answer each question true or false:
faithful: the written text describes the same measure and the same motion as the source, without changing what it does.
no_added_facts: the written text adds no fact that is absent from the source (names of the bill or program given in the source are fine).
no_outcome: the written text gives no hint of how the vote ended (passed, rejected, agreed to as an outcome, tallies, "motion failed"). Naming the kind of vote ("final passage", "motion to table", "amendment") is not an outcome.
no_actor: the written text names no legislator, no party, and no sponsor, and does not say which side or party supported it.
neutral: the wording is neutral (no loaded terms such as pro-life, pro-choice, anti-abortion, unborn child, baby).
yea_nay_correct: given the source, a YEA vote really does what "A YEA vote would" says, and NAY the opposite.

Return JSON: {{"faithful": bool, "no_added_facts": bool, "no_outcome": bool, "no_actor": bool, "neutral": bool, "yea_nay_correct": bool, "reason": "one sentence, required if any is false"}}"""

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int); a = ap.parse_args()
    d = pd.read_csv(V / "out" / "v1" / "descriptions.csv").fillna("")
    if a.limit: d = d.head(a.limit)
    L = Ledger(O / "ledger", dotenv=str(REPO / ".env"))
    out = []
    for i, r in d.iterrows():
        msg = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": TEMPLATE.format(**r.to_dict())}]
        txt = L.chat("openai", MODEL, msg, temperature=0, max_tokens=300, response_format={"type": "json_object"})
        try:
            j = json.loads(txt); ok = all(isinstance(j.get(c), bool) for c in CHECKS)
        except json.JSONDecodeError:
            j, ok = {}, False
        row = dict(key=r.key, parse_ok=ok, **{c: j.get(c) for c in CHECKS}, reason=j.get("reason", ""))
        row["pass"] = bool(ok and all(j[c] for c in CHECKS))
        out.append(row)
        if (i + 1) % 50 == 0: print(i + 1, "checked", flush=True)
    v = pd.DataFrame(out)
    v.to_csv(O / ("verify_smoke.csv" if a.limit else "verify.csv"), index=False, encoding="utf-8")
    summ = dict(model=MODEL, n=len(v), parse_failures=int((~v.parse_ok).sum()), passed=int(v["pass"].sum()),
                failed_by_check={c: int((v[c] == False).sum()) for c in CHECKS})  # noqa: E712
    json.dump(summ, open(O / ("summary_smoke.json" if a.limit else "summary.json"), "w"), indent=1)
    print(json.dumps(summ, indent=1))

if __name__ == "__main__":
    main()
