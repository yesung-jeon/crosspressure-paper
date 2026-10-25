"""Study N CPU gates before any GPU run (PROTOCOL R1b; R5 item rule).
R1b: named_common.analysis_rows() on the sealed Study D maps must give exactly the sealed vote_vs_map.json (n, confusion) for every model.
Items: 16 single-axis items, want_yes defined for each item and every quadrant.
Usage: python -I 01_check_rows.py   -> out/n0_checks.json"""
import json
import pandas as pd
from named_common import dc, analysis_rows, items, want_yes, Q4, OUT

res = {}
for m in dc.MODELS:                              # rebuild: qwen, llama; compared with this run's own Study D s4 output
    v = analysis_rows(dc.OUT / m / "s3" / "temporal_member_scores.csv")
    sealed = json.load(open(dc.OUT / "s4" / "vote_vs_map.json"))[m]
    ct = pd.crosstab(v.vote_q, v.map_q).reindex(index=Q4, columns=Q4, fill_value=0).to_dict(orient="index")
    same = len(v) == sealed["n"] and all(int(ct[a][b]) == int(sealed["confusion_vote_rows_map_cols"][a][b]) for a in Q4 for b in Q4)
    res[m] = {"n": len(v), "sealed_n": sealed["n"], "confusion_equal": bool(same)}
    assert same, (m, res[m])
its = items()
assert all(want_yes(i, q) is not None for i in its for q in Q4)
res["items"] = {"n": len(its), "econ": sum(i["type"] == "econ_only" for i in its), "soc": sum(i["type"] == "soc_only" for i in its)}
OUT.mkdir(parents=True, exist_ok=True); json.dump(res, open(OUT / "n0_checks.json", "w"), indent=1)
print(json.dumps(res))
