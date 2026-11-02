#!/usr/bin/env python
"""Data for body Figures 1 and 3 and Appendix Figure B4.

1. out/gap_benchmark.csv: within-Congress party gap (Republican minus Democratic mean / SD within Congress x chamber, chambers averaged
   with equal weight; party_history.py cell_gap_s2) on matched rows: model social axis vs abortion roll-call scale, model economic axis
   vs economic roll-call scale and DW-NOMINATE dim 1. Used for the dotted benchmark in Figure 1's social panels.
2. out/fig2_quadrant_arrows.csv: per model and vote quadrant, mean percentile position on the roll-call scales and on the map (within
   Congress x chamber, the 06_vote_vs_map.py population: Congress 93+, Democrats and Republicans with both scales; split_hi medians).
   The share kept in the own quadrant must equal the sealed recall_by_vote_quadrant (05_directions_and_map/out/s4/vote_vs_map.json).
3. out/fig2_cp_rows.csv: every cross-pressured member-Congress (vote and map percentiles), for the cloud in Figure 2.
  python figure_data.py"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd

R = Path(__file__).resolve().parents[2]; O = Path(__file__).resolve().parent / "out"; O.mkdir(exist_ok=True); D = R / "05_directions_and_map" / "out"
sys.path.insert(0, str(R / "00_shared")); from splits import split_hi  # noqa: E402  (package tie rule, as 06_vote_vs_map.py)
sc = pd.read_csv(R / "01_rollcall_scales/out/data/issue_scales.csv")
MODELS = ("qwen", "llama")


def gap(d, v):
    """cell_gap_s2 on frame d (congress, chamber, party, v) -> Series by congress"""
    out = {}
    for c, g in d.groupby("congress"):
        gs = []
        for _, h in g.groupby("chamber"):
            if h.party.nunique() < 2: continue
            gs.append((h[h.party == "Republican"][v].mean() - h[h.party == "Democrat"][v].mean()) / h[v].std(ddof=0))
        out[c] = np.mean(gs) if gs else np.nan
    return pd.Series(out)


rows = []
for m in MODELS:
    d = pd.read_csv(D / m / "s3" / "temporal_member_scores.csv")
    d = d[d.party.isin(["Democrat", "Republican"])].assign(x=lambda t: -t.econ_orth, y=lambda t: -t.social_orth)
    for iss, mv in (("abortion", "y"), ("economic", "x")):
        s = sc[sc.issue == iss][["congress", "chamber", "icpsr", "rc_score"]]
        j = d.merge(s, on=["congress", "chamber", "icpsr"], how="inner", validate="one_to_one")
        series = {"model": gap(j, mv), "rollcall": gap(j, "rc_score")}
        if iss == "economic": series["dw1"] = gap(j.dropna(subset=["dim1"]), "dim1")
        T = pd.DataFrame(series); T["n"] = j.groupby("congress").size()
        for c, r in T.iterrows():
            rows.append(dict(llm=m, issue=iss, congress=int(c), year=1789 + 2 * (int(c) - 1), **r.to_dict()))
pd.DataFrame(rows).to_csv(O / "gap_benchmark.csv", index=False)

w = sc.pivot_table(index=["congress", "chamber", "icpsr"], columns="issue", values="rc_score").reset_index()
quad = lambda x, y: pd.Series(np.where(x > 0, "ER-", "EL-"), index=x.index) + np.where(y > 0, "ST", "SP")
sealed = json.load(open(D / "s4" / "vote_vs_map.json", encoding="utf-8"))
arr, pts = [], []
for m in MODELS:
    d = pd.read_csv(D / m / "s3" / "temporal_member_scores.csv"); d["x"], d["y"] = -d.econ_orth, -d.social_orth
    d["cc"] = d.congress.astype(str) + d.chamber
    v = d.merge(w, on=["congress", "chamber", "icpsr"], how="left", validate="one_to_one")
    v = v[(v.congress >= 93) & v.party.isin(["Democrat", "Republican"])].dropna(subset=["economic", "abortion"]).copy()
    for c in ["x", "y", "economic", "abortion"]:
        v[f"hi_{c}"] = split_hi(v[c], v.cc); v[f"{c}_p"] = v.groupby("cc")[c].rank(pct=True)
    v["vote_q"] = quad(v.hi_economic.astype(int) - 0.5, v.hi_abortion.astype(int) - 0.5)
    v["map_q"] = quad(v.hi_x.astype(int) - 0.5, v.hi_y.astype(int) - 0.5)
    for q, g in v.groupby("vote_q"):
        share = float((g.map_q == q).mean()); ref = sealed[m]["recall_by_vote_quadrant"][q]
        assert abs(share - ref) < 1e-12, (m, q, share, ref)                 # guard: same population and split as the sealed result
        arr.append(dict(model=m, vote_q=q, n=len(g), vote_x=g.economic_p.mean(), vote_y=g.abortion_p.mean(), map_x=g.x_p.mean(),
                        map_y=g.y_p.mean(), share_own=share))
    pts.append(v[v.vote_q.isin(["EL-ST", "ER-SP"])][["vote_q", "economic_p", "abortion_p", "x_p", "y_p"]].assign(model=m))
pd.DataFrame(arr).to_csv(O / "fig2_quadrant_arrows.csv", index=False)
pd.concat(pts).round(4).to_csv(O / "fig2_cp_rows.csv", index=False)
print("figure data written to", O)
