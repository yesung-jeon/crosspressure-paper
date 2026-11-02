#!/usr/bin/env python
"""G1 (PROTOCOL_G1.md): map vs economic x gun voting quadrants, Qwen and Llama, with the abortion contrast on the common sample.
  python 05_map_benchmark.py
"""
import sys as _sys; from pathlib import Path as _P; _sys.path.insert(0, str(next(p for p in _P(__file__).resolve().parents if (p / "00_shared").is_dir()) / "00_shared")); from splits import split_hi  # noqa: E402,E702  tie rule 2026-10-30
import json, sys
from pathlib import Path
import numpy as np, pandas as pd

G = Path(__file__).resolve().parents[1]; KIM = G.parent
sys.path.insert(0, str(KIM / "05_directions_and_map" / "code"))
import map_common as dc  # noqa: E402
O = G / "out" / "g1"; O.mkdir(parents=True, exist_ok=True)
Q = ["EL-SP", "EL-ST", "ER-SP", "ER-ST"]; CROSS = ["EL-ST", "ER-SP"]; B = 2000


def quad(hx, hy): return pd.Series(np.where(hx, "ER-", "EL-"), index=hx.index) + np.where(hy, "ST", "SP")


def recall(d, vq):
    r = {q: float((d[d[vq] == q].map_q == q).mean()) if (d[vq] == q).any() else np.nan for q in Q}
    cp = d[vq].isin(CROSS); al = ~cp
    return dict(by_quadrant=r, aligned=float((d[al].map_q == d[al][vq]).mean()), cp=float((d[cp].map_q == d[cp][vq]).mean()),
                n_aligned=int(al.sum()), n_cp=int(cp.sum()))


def baseline(d, vq):
    share = d.map_q.value_counts(normalize=True)
    cp = d[vq].isin(CROSS)
    return dict(aligned=float(d[~cp][vq].map(share).mean()), cp=float(d[cp][vq].map(share).mean()))


def boot(d, vq, seed):
    rng = np.random.default_rng(seed); out = []
    groups = {}                                                          # positions in d (fixed 2026-10-22: were positions within each party subset)
    for (p, i), idx in d.groupby(["party", "icpsr"]).indices.items(): groups.setdefault(p, []).append(idx)
    for _ in range(B):
        idx = np.concatenate([np.concatenate([gl[j] for j in rng.integers(0, len(gl), len(gl))]) for gl in groups.values()])
        r = recall(d.iloc[idx], vq); out.append(r["cp"] - r["aligned"])
    return [float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))]


rows = pd.read_csv(G / "out" / "g0" / "gun_cp_rows.csv")
for m in dc.MODELS:
    mp = pd.read_csv(dc.OUT / m / "s3" / "temporal_member_scores.csv")[["congress", "chamber", "icpsr", "econ_orth", "social_orth"]]
    d = rows.merge(mp, on=["congress", "chamber", "icpsr"], how="left", validate="one_to_one")
    assert d.econ_orth.notna().all()
    d["x"], d["y"] = -d.econ_orth, -d.social_orth
    d["map_q"] = quad(split_hi(d.x, d.cc), split_hi(d.y, d.cc))
    d = d.reset_index(drop=True)
    res = dict(model=m, n_rows=len(d), cells=int(d.cc.nunique()), senate_cells=int(d[d.chamber == "Senate"].cc.nunique()))
    r = recall(d, "gun_q"); r["baseline"] = baseline(d, "gun_q"); r["cp_minus_aligned_ci95"] = boot(d, "gun_q", dc.seed_for("G1", m))
    r["confusion_vote_rows_map_cols"] = pd.crosstab(d.gun_q, d.map_q).to_dict(orient="index")
    res["gun"] = r
    res["reading_map_misses_gun_cp"] = bool(r["cp_minus_aligned_ci95"][1] < 0 and r["cp"] < r["baseline"]["cp"])
    # common sample with abortion: same rows, abortion quadrant (and map quadrant recomputed on these rows)
    c = d.dropna(subset=["abortion"]).copy()
    c["map_q"] = quad(split_hi(c.x, c.cc), split_hi(c.y, c.cc))
    hi_e = split_hi(c.economic, c.cc); hi_g = split_hi(c.gun_score, c.cc)
    c["gun_q2"] = quad(hi_e, hi_g); c["ab_q"] = quad(hi_e, split_hi(c.abortion, c.cc)); c = c.reset_index(drop=True)
    res["common_sample"] = dict(n=len(c), gun=dict(recall(c, "gun_q2"), ci=boot(c, "gun_q2", dc.seed_for("G1c", m)), baseline=baseline(c, "gun_q2")),
                                abortion=dict(recall(c, "ab_q"), ci=boot(c, "ab_q", dc.seed_for("G1a", m)), baseline=baseline(c, "ab_q")))
    # sensitivity: drop rows near either voting-scale median
    z = lambda s: (s - d.groupby("cc")[s.name].transform("median")) / d.groupby("cc")[s.name].transform("std")
    far = (z(d.economic).abs() >= 0.1) & (z(d.gun_score).abs() >= 0.1)
    res["far_from_median"] = dict(recall(d[far], "gun_q"), n=int(far.sum()))
    json.dump(res, open(O / f"g1_{m}.json", "w"), indent=1, default=str)
    print(m, "gun: aligned", round(r["aligned"], 3), "cp", round(r["cp"], 3), "diff ci", [round(x, 3) for x in r["cp_minus_aligned_ci95"]],
          "baseline cp", round(r["baseline"]["cp"], 3), "| common n", len(c), "gun cp", round(res["common_sample"]["gun"]["cp"], 3),
          "abortion cp", round(res["common_sample"]["abortion"]["cp"], 3), "| far cp", round(res["far_from_median"]["cp"], 3), flush=True)
