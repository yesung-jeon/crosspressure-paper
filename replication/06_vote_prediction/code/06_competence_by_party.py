#!/usr/bin/env python
"""Full main sample, order-averaged (A7/A10): A5 competence condition and the within-party cross-pressure comparison (roll-call fixed
effects, two-way clustered as §6.1), per issue. Written as a script on 2026-10-21; it must reproduce the Llama file made on 2026-10-21
(out/v5/competence_party_v2_llama.json) exactly before it is used for another model.
Usage: python 06_competence_by_party.py qwen   ->  out/v5/competence_party_v2_<model>.json"""
import json, sys
from pathlib import Path

model = sys.argv[1]
sys.path.insert(0, str(Path(__file__).parent)); sys.argv = ["estimate_votes.py"]
import estimate_votes as ve  # noqa: E402

d = ve.order_avg_frame(model, ("abortion", "economic"))
out = {}
for iss, g in d.groupby("issue"):
    o = {"competence": ve.competence(g)}
    for party, h in g.groupby("party"):
        o[party] = {"acc": h.groupby("cp").correct_avg.mean().round(4).to_dict(),
                    "cp_coef": ve.twoway(h.assign(y=h.correct_avg, fe=h.key))}
    out[iss] = o
p = ve.V / "out" / "v5" / f"competence_party_v2_{model}.json"
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(p)
