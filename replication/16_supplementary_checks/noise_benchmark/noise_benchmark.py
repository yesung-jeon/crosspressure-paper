#!/usr/bin/env python
"""Noise benchmark for the map placement (review item, 2026-10-25). Descriptive check
added after the sealed results; no tests. Plan written before computing:

Question. Could the low placement of cross-pressured members, and their move to the aligned quadrant on their economic side, arise only
because the map measures members' votes with error, larger on the social coordinate than on the economic one?

Rows. The same rows as the sealed vote_vs_map comparison and benchmark_recall.py: Democratic and Republican member-Congresses from the
93rd Congress on with both roll-call scales; quadrants split at medians within Congress and chamber. Guns via SOCIAL_TAG/ISSUE_SCALES,
as for the other gun checks.

Simulation. Within each Congress and chamber, standardize the economic and social roll-call scales (z_e, z_s). A noise-only map is
  x* = r_x z_e + sqrt(1 - r_x^2) u,   y* = r_y z_s + sqrt(1 - r_y^2) v,
where r_x and r_y are the observed correlations between each model's coordinates and the scales on these rows (each demeaned within
Congress and chamber), so the simulated map tracks the votes exactly as well as the real map does, and errs only by noise.
  main: u, v independent standard normal;
  matched: u, v correlated so that corr(x*, y*) equals the observed correlation of the two map coordinates on these rows.
Each version is drawn 500 times (seed fixed from this file's name). For each draw: recall of aligned and of cross-pressured rows, and the
share of misplaced cross-pressured rows placed in the aligned quadrant with the same economic side. Reported: mean and 2.5th and 97.5th
percentiles over draws, next to the observed values.

Reading (stated before computing). If the noise-only map places cross-pressured rows about as rarely as the real map, noise alone can
produce the misplacement. If it places them clearly more often, the real map misplaces them beyond what its measurement error implies.
The destination share is read the same way.
Output: 16_supplementary_checks/noise_benchmark/noise_benchmark{TAG}.json
Usage: python 16_supplementary_checks/noise_benchmark/noise_benchmark.py"""
import hashlib, json, os, sys
from pathlib import Path
import numpy as np, pandas as pd

R = Path(__file__).resolve().parents[2]; D = R / "02_ideology_map"; OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(D / "code"))
import map_common as dc  # noqa: E402
TAG = os.environ.get("SOCIAL_TAG", "")
M = ["qwen", "llama"]; Q = ["EL-SP", "ER-ST", "EL-ST", "ER-SP"]; AL, CR = Q[:2], Q[2:]
DRAWS = 500
SEED = int(hashlib.sha256(f"noise_benchmark{TAG}".encode()).hexdigest()[:8], 16)
vm = {k: json.load(open(D / "out" / f"s4{TAG}" / "vote_vs_map.json"))[k] for k in M}
sc = pd.read_csv(dc.ISSUE_SCALES); sc = sc[sc.issue.isin(["economic", "abortion"])]
w = sc.pivot_table(index=["congress", "chamber", "icpsr"], columns="issue", values="rc_score").reset_index()


def quad(hx, hy):
    return np.char.add(np.where(hx, "ER-", "EL-"), np.where(hy, "ST", "SP"))


def rows(key):   # identical to benchmark_recall.py rows()
    m = pd.read_csv(D / "out" / key / "s3" / "temporal_member_scores.csv"); m["x"], m["y"] = -m.econ_orth, -m.social_orth
    m["cc"] = m.congress.astype(str) + m.chamber
    v = m.merge(w, on=["congress", "chamber", "icpsr"], how="left", validate="one_to_one")
    v = v[(v.congress >= 93) & v.party.isin(["Democrat", "Republican"])].dropna(subset=["economic", "abortion"]).copy()
    return v.reset_index(drop=True)


def split(v, a, b):
    g = v.cc.values
    med = lambda s: pd.Series(s).groupby(g).transform("median").values
    return quad(a > med(a), b > med(b))


def stats(vote_q, map_q):
    al, cr = np.isin(vote_q, AL), np.isin(vote_q, CR)
    mis = cr & (map_q != vote_q)
    same_econ = np.where(np.char.startswith(vote_q, "EL-"), "EL-SP", "ER-ST")
    return dict(recall_aligned=float((map_q[al] == vote_q[al]).mean()), recall_cross=float((map_q[cr] == vote_q[cr]).mean()),
                same_econ_share=float((map_q[mis] == same_econ[mis]).mean()) if mis.any() else float("nan"))   # nan: no misplaced rows


def within(v, c):
    g = v.groupby("cc")[c]
    return ((v[c] - g.transform("mean")) / g.transform("std")).values


out = {"note": "descriptive noise benchmark added 2026-10-25 after the sealed results (council B2); no tests", "draws": DRAWS, "seed": SEED}
rng = np.random.default_rng(SEED)
for key in M:
    v = rows(key)
    vote_q = split(v, v.economic.values, v.abortion.values); map_q = split(v, v.x.values, v.y.values)
    obs = stats(vote_q, map_q)
    br = json.load(open(R / "16_supplementary_checks" / "benchmark" / f"benchmark_recall{TAG}.json"))["N2_recognized"][key]["all_rows"]
    assert len(v) == vm[key]["n"] == br["n"], key
    assert abs(obs["recall_cross"] - br["cross_pooled"]) < 1e-12 and abs(obs["recall_aligned"] - br["aligned_pooled"]) < 1e-12, key
    ze, zs, zx, zy = (within(v, c) for c in ("economic", "abortion", "x", "y"))
    exact = stats(vote_q, split(v, ze, zs))   # synthetic check: a map without noise reproduces every quadrant
    assert exact["recall_aligned"] == 1.0 and exact["recall_cross"] == 1.0, exact
    rx, ry, rxy, res = float(np.corrcoef(zx, ze)[0, 1]), float(np.corrcoef(zy, zs)[0, 1]), float(np.corrcoef(zx, zy)[0, 1]), float(np.corrcoef(ze, zs)[0, 1])
    sx, sy = np.sqrt(1 - rx ** 2), np.sqrt(1 - ry ** 2)
    rho = float(np.clip((rxy - rx * ry * res) / (sx * sy), -0.99, 0.99))   # noise correlation that reproduces corr(x, y) of the real map
    out[key] = {"observed": obs, "r_x_economic": rx, "r_y_social": ry, "r_x_y_map": rxy, "r_economic_social": res, "noise_rho_matched": rho,
                "n": int(len(v))}
    for name, r in (("main", 0.0), ("matched", rho)):
        sims = []
        for _ in range(DRAWS):
            u = rng.standard_normal(len(v)); e = r * u + np.sqrt(1 - r ** 2) * rng.standard_normal(len(v))
            sims.append(stats(vote_q, split(v, rx * ze + sx * u, ry * zs + sy * e)))
        S = pd.DataFrame(sims)
        out[key][name] = {c: {"mean": float(S[c].mean()), "lo": float(S[c].quantile(0.025)), "hi": float(S[c].quantile(0.975))} for c in S}
    print(key, TAG or "abortion", {k: round(val, 3) for k, val in obs.items()}, "| main", {c: round(d["mean"], 3) for c, d in out[key]["main"].items()},
          "| matched", {c: round(d["mean"], 3) for c, d in out[key]["matched"].items()}, "| r", round(rx, 3), round(ry, 3), "rho", round(rho, 3))
json.dump(out, open(OUT / f"noise_benchmark{TAG}.json", "w", encoding="utf-8"), indent=1)
