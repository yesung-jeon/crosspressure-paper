#!/usr/bin/env python
"""G2 (A14): GPT-4.1-mini check of the gun descriptions with the W1 checker unchanged (prompt, model, six checks imported from
v2_verify.py). Same ledger class; key from crosspressure/.env, never printed.
  python g2_verify.py   -> out/g2/verify.csv, verify_summary.json
"""
import json, sys
from pathlib import Path
import pandas as pd

V = Path(__file__).resolve().parents[1]; REPO = V.parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import v2_verify as w  # noqa: E402  (SYSTEM, TEMPLATE, CHECKS, MODEL, Ledger)

O = V / "out" / "g2"
d = pd.read_csv(O / "descriptions.csv").fillna("")
L = w.Ledger(O / "verify_ledger", dotenv=str(REPO / ".env"))
out = []
for _, r in d.iterrows():
    msg = [{"role": "system", "content": w.SYSTEM}, {"role": "user", "content": w.TEMPLATE.format(**r.to_dict())}]
    txt = L.chat("openai", w.MODEL, msg, temperature=0, max_tokens=300, response_format={"type": "json_object"})
    try:
        j = json.loads(txt); ok = all(isinstance(j.get(c), bool) for c in w.CHECKS)
    except json.JSONDecodeError:
        j, ok = {}, False
    row = dict(key=r.key, parse_ok=ok, **{c: j.get(c) for c in w.CHECKS}, reason=j.get("reason", ""))
    row["pass"] = bool(ok and all(j[c] for c in w.CHECKS)); out.append(row)
v = pd.DataFrame(out); v.to_csv(O / "verify.csv", index=False, encoding="utf-8")
summ = dict(model=w.MODEL, n=len(v), passed=int(v["pass"].sum()), failed_by_check={c: int((v[c] == False).sum()) for c in w.CHECKS})  # noqa: E712
json.dump(summ, open(O / "verify_summary.json", "w"), indent=1); print(summ)
for _, r in v[~v["pass"]].iterrows(): print(r.key, "|", r.reason)
