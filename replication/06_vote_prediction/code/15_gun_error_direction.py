#!/usr/bin/env python
"""G2 error direction with the A13 rule and intervals (A14), gun votes, both models. The A13 functions shares() and boot() are taken
verbatim from 09_error_direction.py; majority definition M1 (sealed party_yea_share, ties excluded).
  python 15_gun_error_direction.py   -> out/g2/error_direction_{model}.json
"""
import json, re, sys
from pathlib import Path
import numpy as np, pandas as pd

V = Path(__file__).resolve().parents[1]; O = V / "out" / "g2"
sys.path.insert(0, str(V.parent / "02_ideology_map" / "code"))
import map_common as dc  # noqa: E402
src = (Path(__file__).resolve().parent / "09_error_direction.py").read_text(encoding="utf-8")
ns = {"np": np, "pd": pd, "REPS": 1000}
exec(re.search(r"^def shares\(g, pred\):.*?(?=^for m in MODELS:)", src, flags=re.S | re.M).group(0), ns)
shares, boot = ns["shares"], ns["boot"]

for m in ["qwen", "llama"]:
    d = pd.read_parquet(O / f"frame_{m}.parquet")
    e = d[~d.party_tie].copy(); e["maj"] = (e.party_yea_share > 0.5).astype(int); e["defect"] = (e.actual != e.maj).astype(int)
    e["correct_col"] = e.correct_avg
    rng = np.random.default_rng(dc.seed_for("A14-dir", m) % 2**32); res = dict(model=m, rule="A13 M1", cells={})
    for cp, h in e.groupby("cp"):
        res["cells"][f"cp={cp}"] = dict(shares(h, "pred_avg"), ci95=boot(h, "pred_avg", rng))
        for p, hp in h.groupby("party"):
            res["cells"][f"cp={cp}|{p}"] = dict(shares(hp, "pred_avg"), ci95=boot(hp, "pred_avg", rng))
    res["reading_cp_errors_toward_party"] = bool(res["cells"]["cp=1"]["ci95"]["toward_party_among_wrong"][0] > 0.5)
    json.dump(res, open(O / f"error_direction_{m}.json", "w"), indent=1, default=float)
    c = res["cells"]
    print(m, {k: (round(v["toward_party_among_wrong"], 3), [round(x, 3) for x in v["ci95"]["toward_party_among_wrong"]],
                  round(v["defection_caught"], 3)) for k, v in c.items()}, res["reading_cp_errors_toward_party"], flush=True)
