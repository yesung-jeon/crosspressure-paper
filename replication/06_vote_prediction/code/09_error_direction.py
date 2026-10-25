#!/usr/bin/env python
"""Study V amendment A13 (CPU, descriptive): direction of the errors. Qwen and Llama only.
  python 09_error_direction.py
"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd

V = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(V.parent / "02_ideology_map" / "code"))
import map_common as dc  # noqa: E402

MODELS = ["qwen", "llama"]
O = V / "out" / "v6"; O.mkdir(parents=True, exist_ok=True)
REPS = 1000

mv = pd.read_csv(V / "out" / "v0" / "member_votes.csv.gz", usecols=["congress", "chamber", "rollnumber", "icpsr", "party", "actual"])
mv["key"] = mv.congress.astype(str) + "|" + mv.chamber + "|" + mv.rollnumber.astype(str)
n_party = mv.groupby(["key", "party"]).agg(n_party=("actual", "size"), yea_party=("actual", "sum")).reset_index()
# Codex verification 2026-10-22: M2 must use integer counts. The first version rebuilt the count from the stored float share
# (share x n), so exact leave-self-out ties (2 x yea_others == n - 1) were missed in 150 rows.


def shares(g, pred):
    """quantities 1-3 for one frame subset and one prediction column"""
    wrong = g[g.correct_col == 0]; dfc = g[g.defect == 1]; fol = g[g.defect == 0]
    return dict(n=len(g), n_wrong=len(wrong), toward_party_among_wrong=float((wrong[pred] == wrong.maj).mean()) if len(wrong) else np.nan,
                n_defections=len(dfc), defection_caught=float((dfc[pred] == dfc.actual).mean()) if len(dfc) else np.nan,
                n_follow=len(fol), follow_correct=float((fol[pred] == fol.actual).mean()) if len(fol) else np.nan)


def boot(g, pred, rng):
    """member-cluster bootstrap within CP x party; returns 95% intervals of the three shares"""
    g = g.reset_index(drop=True)
    grp = g.groupby(["cp", "party", "icpsr"]).indices
    strata = {}
    for (c, p, i), idx in grp.items(): strata.setdefault((c, p), []).append(idx)
    keys = list(strata)
    out = {k: [] for k in ["toward_party_among_wrong", "defection_caught", "follow_correct"]}
    for _ in range(REPS):
        idx = np.concatenate([np.concatenate([strata[s][j] for j in rng.integers(0, len(strata[s]), len(strata[s]))]) for s in keys])
        r = shares(g.iloc[idx], pred)
        for k in out: out[k].append(r[k])
    return {k: [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))] for k, v in out.items()}


for m in MODELS:
    d = pd.read_parquet(V / "out" / "v5" / f"frame_v2_{m}_abortion_economic.parquet")
    # rebuild 2026-10-24: the sealed FP8 frames had no format failures, so this asserted none; the bf16 Llama frame has 1 of 102,285.
    # As the W1 main estimates (PROTOCOL 6.4: correct = NaN for format failures), those rows are left out here and counted.
    n_ff = int(d.format_fail.sum()); d = d[~d.format_fail].copy()
    d = d.merge(n_party, on=["key", "party"], how="left", validate="many_to_one")
    assert d.n_party.notna().all()
    yo, no = d.yea_party - d.actual, d.n_party - 1                       # other members of the party on that roll call (integers)
    res = dict(model=m, amendment="A13", results={}, format_fail_rows_excluded=n_ff)
    for maj_def in ["M1", "M2"]:
        if maj_def == "M1":
            keep = d.party_yea_share.notna() & (d.party_yea_share != 0.5); maj = (d.party_yea_share > 0.5)
        else:
            keep = (no > 0) & (2 * yo != no); maj = (2 * yo > no)
        e = d[keep].copy()
        e["maj"] = maj[keep].astype(int); e["defect"] = (e.actual != e.maj).astype(int)
        for iss, g in e.groupby("issue"):
            for pred, corr in [("pred_avg", "correct_avg"), ("pred_yf", "correct_yf"), ("pred_nf", "correct_nf")]:
                gg = g.assign(correct_col=g[corr])
                rng = np.random.default_rng(dc.seed_for("A13", m, iss, maj_def, pred) % 2**32)
                cell = {}
                for cp, h in gg.groupby("cp"):
                    single_ci = maj_def == "M1" and iss == "abortion"            # Codex verification: single-order claims need intervals
                    cell[f"cp={cp}"] = dict(shares(h, pred), ci95=boot(h, pred, rng) if (pred == "pred_avg" or single_ci) else None)
                    for p, hp in h.groupby("party"):
                        cell[f"cp={cp}|{p}"] = dict(shares(hp, pred), ci95=boot(hp, pred, rng) if pred == "pred_avg" else None)
                res["results"][f"{maj_def}|{iss}|{pred}"] = cell
    for k in [x for x in res["results"] if x.endswith("abortion|pred_avg")]:
        c = res["results"][k]["cp=1"]
        res[f"reading_{k.split('|')[0]}_cp_errors_toward_party_abortion"] = bool(c["ci95"]["toward_party_among_wrong"][0] > 0.5)
    for o in ["pred_yf", "pred_nf"]:
        c = res["results"][f"M1|abortion|{o}"]["cp=1"]
        res[f"reading_M1_cp_errors_toward_party_abortion_{o}"] = bool(c["ci95"]["toward_party_among_wrong"][0] > 0.5)
    dc.atomic_json(res, O / f"error_direction_{m}.json")
    print(m, json.dumps({k: {c: round(v["toward_party_among_wrong"], 3) for c, v in res["results"][k].items()}
                         for k in res["results"] if k.endswith("pred_avg")}, indent=0), flush=True)
