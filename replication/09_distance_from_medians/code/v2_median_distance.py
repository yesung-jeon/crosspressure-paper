#!/usr/bin/env python
"""V2 (protocol/PROTOCOL_2026-11-02.md): is the Section 5 placement gap produced by member-Congresses near the medians?
Rows and quadrants as 05_directions_and_map/code/06_vote_vs_map.py l.80-84 (split_hi); gate against benchmark_recall.json. -> ../out/v2.json"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd

H = Path(__file__).resolve().parents[1]; R = H.parent
sys.path.insert(0, str(R / "00_shared")); sys.path.insert(0, str(R / "05_directions_and_map" / "code"))
from splits import split_hi  # noqa: E402
import map_common as dc  # noqa: E402

quad = lambda x, y: pd.Series(np.where(x > 0, "ER-", "EL-"), index=getattr(x, "index", None)) + np.where(y > 0, "ST", "SP")
B = 2000


def rows(m):
    sc = pd.read_csv(dc.ISSUE_SCALES); sc = sc[sc.issue.isin(["economic", "abortion"])]
    w = sc.pivot_table(index=["congress", "chamber", "icpsr"], columns="issue", values="rc_score").reset_index()
    d = pd.read_csv(dc.OUT / m / "s3" / "temporal_member_scores.csv"); assert len(d) == 21288
    d["x"], d["y"] = -d.econ_orth, -d.social_orth; d["cc"] = d.congress.astype(str) + d.chamber
    v = d.merge(w, on=["congress", "chamber", "icpsr"], how="left", validate="one_to_one")
    v = v[(v.congress >= 93) & v.party.isin(["Democrat", "Republican"])].dropna(subset=["economic", "abortion"]).copy()
    for c in ["x", "y", "economic", "abortion"]:
        v[f"hi_{c}"] = split_hi(v[c], v.cc)
    v["vote_q"] = quad(v.hi_economic.astype(int) - 0.5, v.hi_abortion.astype(int) - 0.5)
    v["map_q"] = quad(v.hi_x.astype(int) - 0.5, v.hi_y.astype(int) - 0.5)
    v["cp"] = v.vote_q.isin(["EL-ST", "ER-SP"]); v["hit"] = (v.vote_q == v.map_q).astype(float)
    z = lambda c: (v[c] - v.groupby("cc")[c].transform("median")).abs() / v.groupby("cc")[c].transform(lambda s: s.std(ddof=0))
    v["dist"] = np.minimum(z("economic"), z("abortion"))
    return v.reset_index(drop=True)


def gap_stats(v, mask, rng_seed):
    s = v[mask]; mem = s.icpsr.values; uniq, inv = np.unique(mem, return_inverse=True)
    a, c = ~s.cp.values, s.cp.values; h = s.hit.values
    est = dict(aligned=float(h[a].mean()), cross=float(h[c].mean()), n_aligned=int(a.sum()), n_cross=int(c.sum()))
    est["gap"] = est["aligned"] - est["cross"]
    rng = np.random.default_rng(rng_seed % 2**32); g = []
    for _ in range(B):
        wm = np.bincount(rng.integers(0, len(uniq), len(uniq)), minlength=len(uniq))[inv]
        g.append(np.sum(wm * h * a) / np.sum(wm * a) - np.sum(wm * h * c) / np.sum(wm * c))
    est["gap_ci"] = [float(np.percentile(g, 2.5)), float(np.percentile(g, 97.5))]
    return est


def main():
    out = {"protocol": "09_distance_from_medians/protocol/PROTOCOL_2026-11-02.md"}
    br = json.load(open(R / "08_supplementary_checks" / "benchmark" / "benchmark_recall.json"))["N2_recognized"]
    MS = list(dc.MODELS); V = {m: rows(m) for m in MS}
    cuts = np.quantile(V[MS[0]].dist, [1 / 3, 2 / 3])
    assert np.allclose(np.quantile(V[MS[1]].dist, [1 / 3, 2 / 3]), cuts)   # distances come from roll calls only
    out["tercile_cuts_sd"] = cuts.tolist()
    for m in MS:
        v = V[m]
        g = {"aligned": abs(v[~v.cp].hit.mean() - br[m]["all_rows"]["aligned_pooled"]), "cross": abs(v[v.cp].hit.mean() - br[m]["all_rows"]["cross_pooled"])}
        assert max(g.values()) < 1e-12, (m, g)
        t = np.digitize(v.dist, cuts)                                # 0, 1, 2 = near, middle, far
        res = {"full": gap_stats(v, np.ones(len(v), bool), dc.seed_for("V2", m, "full"))}
        for k, lab in enumerate(["near tercile", "middle tercile", "far tercile"]):
            res[lab] = gap_stats(v, t == k, dc.seed_for("V2", m, lab))
        res["dist >= 0.5 SD"] = gap_stats(v, (v.dist >= 0.5).values, dc.seed_for("V2", m, "0.5"))
        f = res["far tercile"]; ok = (f["gap_ci"][0] > 0) and (f["gap"] >= 0.5 * res["full"]["gap"])
        res["reading"] = ("gap not produced by near-median rows" if ok else
                          "near-median rows account for much of the gap" if f["gap"] < 0.5 * res["full"]["gap"] else "far-tercile gap interval includes zero")
        res["gate_max_abs_diff"] = max(g.values())
        out[m] = res
        print(m, {k: (round(r["aligned"], 3), round(r["cross"], 3), round(r["gap"], 3), [round(c, 3) for c in r["gap_ci"]]) for k, r in res.items() if isinstance(r, dict) and "gap" in r}, res["reading"], flush=True)
    json.dump(out, open(H / "out" / "v2.json", "w"), indent=1)


if __name__ == "__main__":
    main()
