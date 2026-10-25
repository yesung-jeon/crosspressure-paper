#!/usr/bin/env python
"""T2 (PROTOCOL_T2.md): sorting indicators, relative CP share, map vs vote-scale correlation, era recall. Qwen and Llama.
  python 02_sorting.py   -> out/t2/cells.csv, t2.json
"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd

T = Path(__file__).resolve().parents[1]; KIM = T.parent
sys.path.insert(0, str(KIM / "09_named_member_entropy" / "code")); sys.path.insert(0, str(KIM / "02_ideology_map" / "code"))
import map_common as dc  # noqa: E402
import named_common as nc  # noqa: E402
O = T / "out" / "t2"; O.mkdir(parents=True, exist_ok=True)
ERA = lambda c: "93-100" if c <= 100 else ("101-108" if c <= 108 else "109-117")
B = 2000


def corr(a, b): return float(np.corrcoef(a, b)[0, 1]) if len(a) > 2 and np.std(a) > 0 and np.std(b) > 0 else np.nan


def cells(v, sx, sy, party=None):
    rows = []
    for cc, g in v.groupby("cc"):
        if party: g = g[g.party == party]
        if len(g) < 10: continue
        rows.append(dict(cc=cc, congress=int(g.congress.iloc[0]), chamber=g.chamber.iloc[0], n=len(g), era=ERA(int(g.congress.iloc[0])),
                         vote_corr=corr(g[sx], g[sy]), map_corr=corr(g.x, g.y), cp_share=float(g.cp.mean()),
                         party_econ=corr(g[sx], (g.party == "Republican").astype(float)), party_social=corr(g[sy], (g.party == "Republican").astype(float))))
    return pd.DataFrame(rows)


def boot_mean(s, seed):
    s = s.dropna().values; rng = np.random.default_rng(seed)
    b = [s[rng.integers(0, len(s), len(s))].mean() for _ in range(B)]
    return [float(s.mean()), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]


def party_and_era(v, C, sy, tag, m, era, first, last, pre=""):
    """Within-party over-alignment, era quantities and the two readings; one code path for abortion (tag T2) and guns (tag T2g,
    PROTOCOL_GUNSYM Amendment 1). Abortion seeds and keys are those of the first version."""
    out = {}
    for p in ["Democrat", "Republican"]:
        Cp = cells(v, "economic", sy, party=p)
        out[f"{pre}over_alignment_{p}"] = dict(map_corr=boot_mean(Cp.map_corr, 3), vote_corr=boot_mean(Cp.vote_corr, 4),
                                               diff=boot_mean(Cp.map_corr - Cp.vote_corr, dc.seed_for(tag, m, p)))
    out[f"{pre}by_era"] = {}
    for e, g in C.groupby("era"):
        rows_e = v[v.congress.map(era) == e]
        al, cp = rows_e[rows_e.cp == 0], rows_e[rows_e.cp == 1]
        out[f"{pre}by_era"][e] = dict(cells=len(g), vote_corr=boot_mean(g.vote_corr, 5), cp_share=boot_mean(g.cp_share, 6),
                                party_econ=float(g.party_econ.mean()), party_social=float(g.party_social.mean()),
                                recall_aligned=float((al.map_q == al.vote_q).mean()), recall_cp=float((cp.map_q == cp.vote_q).mean()),
                                rows=len(rows_e), share_senate=float((rows_e.chamber == "Senate").mean()), share_rep=float((rows_e.party == "Republican").mean()))
    a, b = out[f"{pre}by_era"][first], out[f"{pre}by_era"][last]
    out[f"{pre}reading_cp_more_common_before_sorting"] = bool(a["cp_share"][1] > b["cp_share"][2] and a["vote_corr"][2] < b["vote_corr"][1])
    return out


GERA = lambda c: "90-100" if c <= 100 else ERA(c)    # gun rows include Congresses 90 and 92 (Amendment 1)
res = {}
gun = pd.read_csv(KIM / "05_gun_scale" / "out" / "g0" / "gun_cp_rows.csv")
for m in ["qwen", "llama"]:
    v = nc.analysis_rows(dc.OUT / m / "s3" / "temporal_member_scores.csv")
    v["cp"] = v.vote_q.isin(["EL-ST", "ER-SP"]).astype(int)
    C = cells(v, "economic", "abortion"); C["model"] = m; C.to_csv(O / f"cells_{m}.csv", index=False)
    out = dict(n_cells=len(C))
    out["over_alignment_all"] = dict(map_corr=boot_mean(C.map_corr, 1), vote_corr=boot_mean(C.vote_corr, 2),
                                     diff=boot_mean(C.map_corr - C.vote_corr, dc.seed_for("T2", m)))
    out.update(party_and_era(v, C, "abortion", "T2", m, ERA, "93-100", "109-117"))
    out["reading_map_aligns_more_than_votes"] = bool(out["over_alignment_all"]["diff"][1] > 0)
    # guns (same quantities on the gun rows; map quadrant by median splits on those rows, vote quadrant = gun quadrant)
    mp = pd.read_csv(dc.OUT / m / "s3" / "temporal_member_scores.csv")[["congress", "chamber", "icpsr", "econ_orth", "social_orth"]]
    gv = gun.merge(mp, on=["congress", "chamber", "icpsr"], validate="one_to_one"); gv["x"], gv["y"] = -gv.econ_orth, -gv.social_orth
    assert len(gv) == len(gun) == 2256, (m, len(gv))       # every registered gun row is on the map (PROTOCOL_T2 Data; Codex round 2)
    gv["cp"] = gv.gun_cp
    hx, hy = (gv[c] > gv.groupby("cc")[c].transform("median") for c in ("x", "y"))
    gv["map_q"] = pd.Series(np.where(hx, "ER-", "EL-"), index=gv.index) + np.where(hy, "ST", "SP"); gv["vote_q"] = gv.gun_q
    G = cells(gv, "economic", "gun_score")
    out["guns_over_alignment"] = dict(n_cells=len(G), map_corr=boot_mean(G.map_corr, 7), vote_corr=boot_mean(G.vote_corr, 8),
                                      diff=boot_mean(G.map_corr - G.vote_corr, dc.seed_for("T2g", m)))
    G["era"] = G.congress.map(GERA); G["model"] = m; G.to_csv(O / f"cells_guns_{m}.csv", index=False)
    out.update(party_and_era(gv, G, "gun_score", "T2g", m, GERA, "90-100", "109-117", pre="guns_"))
    out["guns_reading_map_aligns_more_than_votes"] = bool(out["guns_over_alignment"]["diff"][1] > 0)
    # abortion on the common rows (gun rows with an abortion score; PROTOCOL_GUNSYM Amendment 2): quadrants re-split on these rows
    av = gv.dropna(subset=["abortion"]).copy()
    he, ha, hx, hy = (av[c] > av.groupby("cc")[c].transform("median") for c in ("economic", "abortion", "x", "y"))
    av["vote_q"] = pd.Series(np.where(he, "ER-", "EL-"), index=av.index) + np.where(ha, "ST", "SP")
    av["map_q"] = pd.Series(np.where(hx, "ER-", "EL-"), index=av.index) + np.where(hy, "ST", "SP")
    av["cp"] = av.vote_q.isin(["EL-ST", "ER-SP"]).astype(int)
    A = cells(av, "economic", "abortion"); A["era"] = A.congress.map(GERA)
    out["gunrows_abortion_over_alignment"] = dict(n_rows=len(av), n_cells=len(A), map_corr=boot_mean(A.map_corr, 7), vote_corr=boot_mean(A.vote_corr, 8),
                                                  diff=boot_mean(A.map_corr - A.vote_corr, dc.seed_for("T2ga", m)))
    out.update(party_and_era(av, A, "abortion", "T2ga", m, GERA, "90-100", "109-117", pre="gunrows_abortion_"))
    out["gunrows_abortion_reading_map_aligns_more_than_votes"] = bool(out["gunrows_abortion_over_alignment"]["diff"][1] > 0)
    res[m] = out
    print(m, "map", [round(x, 3) for x in out["over_alignment_all"]["map_corr"]], "vote", [round(x, 3) for x in out["over_alignment_all"]["vote_corr"]],
          "| eras cp", {e: round(x["cp_share"][0], 3) for e, x in out["by_era"].items()}, "vote_corr", {e: round(x["vote_corr"][0], 3) for e, x in out["by_era"].items()}, flush=True)
json.dump(res, open(O / "t2.json", "w"), indent=1)
