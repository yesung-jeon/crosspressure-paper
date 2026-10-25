#!/usr/bin/env python
"""Descriptive follow-up for Section 7 (added 2026-10-19 at the author's request, after the sealed results; descriptive only, no tests,
no new model runs). Reads the shipped maps (02_ideology_map/out/<model>/s3), the issue scales and the vote-based selection.
1. Who the 60 vote-selected legislators are and where each model places them (same computation as 08b_place_by_votes.py; the placed counts are
   asserted equal to the sealed S4C.json for every model).
2. Where misplaced cross-pressured legislators land, by party.
3. Member-Congress rows from the 93rd Congress on (as 06_vote_vs_map.py vote_vs_map): party x voting quadrant of cross-pressured rows, and by
   decade (1973-79 ... 2011-2021) the share of cross-pressured rows and recall of aligned and cross-pressured rows (overall recall asserted equal to the sealed
   vote_vs_map.json).
Output: 16_supplementary_checks/members_by_era/members_by_era.json and members_table.csv. Usage: python 16_supplementary_checks/members_by_era/members_by_era.py"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd

R = Path(__file__).resolve().parents[2]; D = R / "02_ideology_map"; S = D / "out"; OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(D / "code"))
import map_common as dc  # noqa: E402
M = ["qwen", "llama"]; Q = ["EL-SP", "ER-ST", "EL-ST", "ER-SP"]; CROSS = ["EL-ST", "ER-SP"]
J = lambda p: json.load(open(p, encoding="utf-8"))
s4c = {"qwen": J(S / "s4c" / "S4C.json")["qwen"], "llama": J(S / "s4c" / "S4C.json")["llama"]}
import os
TAG = os.environ.get("SOCIAL_TAG", "")   # rebuild PROTOCOL_GUNSYM: "_guns" = rows part with the gun scale; the 60-legislator part is
                                          # abortion/economic-specific (fixed coded selection) and is skipped for guns
vm = {k: J(S / f"s4{TAG}" / "vote_vs_map.json")[k] for k in M}
quad = lambda hx, hy: pd.Series(np.where(hx, "ER-", "EL-"), index=hx.index) + np.where(hy, "ST", "SP")

JR = dc.s4_selection_rows(); sel = pd.read_csv(D / "out" / "s4c" / "selection.csv")
sc = pd.read_csv(dc.ISSUE_SCALES); sc = sc[sc.issue.isin(["economic", "abortion"])]
w = sc.pivot_table(index=["congress", "chamber", "icpsr"], columns="issue", values="rc_score").reset_index()
out = {"note": "descriptive follow-up added 2026-10-19 after the sealed results; no tests", "members": {}, "rows": {}}
for key in M:
    m = pd.read_csv(D / "out" / key / "s3" / "temporal_member_scores.csv"); m["x"], m["y"] = -m.econ_orth, -m.social_orth
    m["cc"] = m.congress.astype(str) + m.chamber
    # (1) legislators selected by votes: as 08b_place_by_votes.py
    k = m[m.party.isin(["Democrat", "Republican"]) & m.known.astype(bool)].copy()
    for c in ["x", "y"]:
        k[f"{c}m"] = k[c] - k.groupby("cc")[c].transform("median")
    if not TAG:
        pos = k.merge(JR, on=["congress", "chamber", "icpsr"]).groupby("icpsr")[["xm", "ym"]].mean()
        q = quad(pos.xm > 0, pos.ym > 0)
        sel[key] = sel.icpsr.map(q)
        placed = {v: int((sel[sel.vote_q == v][key] == v).sum()) for v in Q}
        assert placed == {v: s4c[key][v]["placed"] for v in Q}, (key, placed)
    # (3) rows: as 06_vote_vs_map.py vote_vs_map
    v = m.merge(w, on=["congress", "chamber", "icpsr"], how="left", validate="one_to_one")
    v = v[(v.congress >= 93) & v.party.isin(["Democrat", "Republican"])].dropna(subset=["economic", "abortion"]).copy()
    for c in ["x", "y", "economic", "abortion"]:
        v[f"hi_{c}"] = v[c] > v.groupby("cc")[c].transform("median")
    v["vote_q"] = quad(v.hi_economic, v.hi_abortion); v["map_q"] = quad(v.hi_x, v.hi_y); v["cross"] = v.vote_q.isin(CROSS)
    assert len(v) == vm[key]["n"] and all(abs((v[v.vote_q == c].map_q == c).mean() - vm[key]["recall_by_vote_quadrant"][c]) < 1e-12 for c in Q)
    v["decade"] = np.minimum(v.year // 10 * 10, 2010)   # rows need both scales, so the last observed Congress is the 117th (2021, 98 rows), grouped with 2011-2019
    dec = {}
    for d_, g in v.groupby("decade"):
        dec[str(int(d_))] = {"rows": int(len(g)), "cross_share": float(g.cross.mean()),
                             "recall_aligned": float((g[~g.cross].map_q == g[~g.cross].vote_q).mean()),
                             "recall_cross": float((g[g.cross].map_q == g[g.cross].vote_q).mean()) if g.cross.any() else None,
                             "n_cross": int(g.cross.sum())}
    out["rows"][key] = {"by_decade": dec,
                        "cross_rows_party_by_quadrant": {c: v[v.vote_q == c].party.value_counts().to_dict() for c in CROSS}}
if TAG:
    out["members"] = "not applicable: the 60 legislators were selected and coded on the abortion/economic scales (PROTOCOL_GUNSYM)"
    json.dump(out, open(OUT / f"members_by_era{TAG}.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("written (rows part only)", TAG); sys.exit(0)
sel["n_placed"] = sum((sel[k] == sel.vote_q).astype(int) for k in M)
cr = sel[sel.vote_q.isin(CROSS)]; al = sel[~sel.vote_q.isin(CROSS)]
out["members"] = {
    "cross_placed_by_k_models": {str(i): int((cr.n_placed == i).sum()) for i in range(4)},
    "aligned_placed_by_k_models": {str(i): int((al.n_placed == i).sum()) for i in range(4)},
    "cross_party_by_quadrant": {c: cr[cr.vote_q == c].party.value_counts().to_dict() for c in CROSS},
    "cross_first_decade": {str(int(d)): int(n) for d, n in (cr["first"] // 10 * 10).value_counts().sort_index().items()},
    "misplaced_destination": {key: {c: cr[(cr.vote_q == c) & cr[key].notna() & (cr[key] != c)][key].value_counts().to_dict() for c in CROSS} for key in M},
    "no_position": {key: int(sel[key].isna().sum()) for key in M},
    "senators_cross": [{"name": r["name"], "party": r.party, "state": r.state, "first": int(r["first"]), "last": int(r["last"]), "vote_q": r.vote_q,
                        **{key: (None if pd.isna(r[key]) else bool(r[key] == r.vote_q)) for key in M}}
                       for _, r in cr[cr.chamber.str.contains("Senate")].sort_values(["vote_q", "first"]).iterrows()],
}
tab = sel[["name", "party", "chamber", "state", "first", "last", "vote_q", "how", "depth"] + M + ["n_placed"]].sort_values(["vote_q", "how", "depth"], ascending=[True, True, False])
tab.to_csv(OUT / "members_table.csv", index=False)
json.dump(out, open(OUT / "members_by_era.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("written; cross placed by k models", out["members"]["cross_placed_by_k_models"], "aligned", out["members"]["aligned_placed_by_k_models"])
