#!/usr/bin/env python
"""Study V stage 1 (PLAN v0.2 W1, CPU, no study model): neutral roll-call descriptions for the vote-prediction prompt.

Junsol Kim's template needs, per roll call, a neutral description of the bill or amendment and the specific motion, and what YEA and
NAY mean. A rule-only rewrite of Voteview's text was tried first (2026-10-20) and left outcome clauses, sponsors' names and
content-free entries ("To pass H.R. 5559."), so the descriptions are written by Claude from Voteview's text only (writer), checked by
fixed leak rules here, verified by GPT-4.1-mini (v2_verify.py, a different model family: Kim C7), and spot-checked by the author.
None of the three study models is used.

  python v1_descriptions.py prepare   -> out/v1/batches/batch_<k>.jsonl  (source fields + same-bill context; writer input)
  python v1_descriptions.py merge     -> out/v1/descriptions.csv, summary.json  (writer output + leak checks)
Writer output: out/v1/written/batch_<k>.json, a list of {key, description, yea_means, nay_means, insufficient, note}.
"""
import json, re, sys
from pathlib import Path
import pandas as pd

V = Path(__file__).resolve().parents[1]
KIM = V.parent
O = V / "out" / "v1"; O.mkdir(parents=True, exist_ok=True)
KEY = ["congress", "chamber", "rollnumber"]
N_BATCH = 4
OUTCOME = r"\b(?:PASSED|REJECTED|FAILED|DEFEATED|SUSTAINED|OVERRODE|OVERRIDDEN|TABLED|CARRIED|PREVAILED|APPROVED|ADOPTED BY|AGREED TO BY|MOTION AGREED|WAS AGREED)\b|\b\d{1,3}\s?-\s?\d{1,3}\b"
PARTY = r"\b(?:REPUBLICANS?|DEMOCRATS?|DEMOCRATIC|GOP)\b|\((?:R|D|I)-[A-Z]{2}\)|\b[RD]-[A-Z]{2}\b"
LOADED = r"\b(?:PRO-LIFE|PRO-CHOICE|ANTI-ABORTION|PRO-ABORTION|UNBORN CHILD|BABY|BABIES|KILLING)\b"

def key_of(r): return f"{int(r.congress)}|{r.chamber}|{int(r.rollnumber)}"

def prepare():
    rc = pd.read_csv(V / "out" / "v0" / "rollcalls.csv").fillna("")
    allrc = pd.read_csv(KIM / "data" / "voteview_all" / "HSall_rollcalls.csv", low_memory=False,
                        usecols=KEY + ["bill_number", "vote_question", "vote_desc", "dtl_desc"]).fillna("")
    allrc = allrc[allrc.congress.between(93, 117)]
    ctx = {}
    for (c, ch, b), g in allrc[allrc.bill_number.ne("")].groupby(["congress", "chamber", "bill_number"]):
        texts = [t for t in (g.vote_desc.tolist() + g.dtl_desc.tolist()) if len(str(t)) > 25]
        ctx[(c, ch, b)] = sorted(set(texts), key=len)[:3]       # up to three other descriptions of the same bill
    items = []
    for _, r in rc.sort_values(KEY).iterrows():
        items.append(dict(key=key_of(r), issue=r.issue, motion=r.motion, vote_question=r.vote_question, bill_number=r.bill_number,
                          vote_desc=r.vote_desc, dtl_desc=r.dtl_desc,
                          same_bill_context=[t for t in ctx.get((r.congress, r.chamber, r.bill_number), [])
                                             if t not in (r.vote_desc, r.dtl_desc)]))
    bd = O / "batches"; bd.mkdir(exist_ok=True)
    for k in range(N_BATCH):
        with open(bd / f"batch_{k}.jsonl", "w", encoding="utf-8") as f:
            for it in items[k::N_BATCH]:
                f.write(json.dumps(it, ensure_ascii=False) + "\n")
    print(f"{len(items)} roll calls in {N_BATCH} batches")

def merge():
    items = [json.loads(l) for k in range(N_BATCH) for l in open(O / "batches" / f"batch_{k}.jsonl", encoding="utf-8")]
    written = {}
    for k in range(N_BATCH):
        for w in json.load(open(O / "written" / f"batch_{k}.json", encoding="utf-8")):
            assert w["key"] not in written, f"duplicate key {w['key']}"
            written[w["key"]] = w
    # overrides.json: corrections after the GPT-4.1-mini check (v2_verify.py), each with its reason; applied last and logged
    ov_path = Path(__file__).with_name("overrides.json")
    ov = json.load(open(ov_path, encoding="utf-8")) if ov_path.exists() else {}
    for k, o in ov.items():
        assert k in written, f"override for unknown key {k}"
        written[k] = {**written[k], **{f: o[f] for f in ("description", "yea_means", "nay_means", "insufficient") if f in o},
                      "note": f"OVERRIDE: {o['reason']}"}
    keys = [i["key"] for i in items]
    missing = [k for k in keys if k not in written]; extra = [k for k in written if k not in set(keys)]
    if missing or extra: raise SystemExit(f"STOP: missing {missing[:5]} ({len(missing)}), extra {extra[:5]} ({len(extra)})")
    rows = []
    for it in items:
        w = written[it["key"]]
        full = " ".join([w["description"], w["yea_means"], w["nay_means"]]).upper()
        rows.append(dict(**{k: it[k] for k in ["key", "issue", "motion", "vote_question", "bill_number", "vote_desc", "dtl_desc"]},
                         description=w["description"], yea_means=w["yea_means"], nay_means=w["nay_means"],
                         insufficient=bool(w.get("insufficient", False)), writer_note=w.get("note", ""),
                         leak_outcome=bool(re.search(OUTCOME, full)), leak_party=bool(re.search(PARTY, full)),
                         loaded_term=bool(re.search(LOADED, full)), n_words=len(w["description"].split())))
    d = pd.DataFrame(rows)
    d.to_csv(O / "descriptions.csv", index=False, encoding="utf-8")
    summ = dict(n=len(d), insufficient=int(d.insufficient.sum()), leak_outcome=int(d.leak_outcome.sum()),
                leak_party=int(d.leak_party.sum()), loaded_term=int(d.loaded_term.sum()),
                words_median=float(d.n_words.median()), words_max=int(d.n_words.max()))
    json.dump(summ, open(O / "summary.json", "w"), indent=1)
    print(json.dumps(summ, indent=1))
    flagged = d[d.leak_outcome | d.leak_party | d.loaded_term | d.insufficient]
    for _, x in flagged.iterrows(): print(x.key, "|", x.description[:200])

if __name__ == "__main__":
    {"prepare": prepare, "merge": merge}[sys.argv[1]]()
