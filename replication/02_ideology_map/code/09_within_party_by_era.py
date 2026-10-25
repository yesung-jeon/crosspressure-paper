#!/usr/bin/env python
"""S4d (PLAN addendum A9, exploratory): within-party, within-era sensitivity of the map's social axis to abortion roll-call
deviations, controlling for economic deviations. -> out/s4d/S4D.json, s4d_table.csv"""
import argparse
import numpy as np, pandas as pd
import map_common as dc

ap = argparse.ArgumentParser()   # A12: defaults reproduce the sealed run; OLMo: --models olmo --out s4d_olmo
ap.add_argument("--models", nargs="+", default=["qwen", "llama"], choices=list(dc.MODELS)); ap.add_argument("--out", default="s4d")
a = ap.parse_args(); SEL = a.models
O = dc.OUT / a.out; O.mkdir(parents=True, exist_ok=True)
NB = 1000
sc = pd.read_csv(dc.ISSUE_SCALES); sc = sc[sc.issue.isin(["economic", "abortion"]) & (sc.congress >= 93)]
w = sc.pivot_table(index=["congress", "chamber", "icpsr"], columns="issue", values="rc_score").reset_index().dropna()

def fit(g, ctrl=True):
    X = g[["z_ab", "z_ec"]].values if ctrl else g[["z_ab"]].values
    return float(np.linalg.lstsq(X, g.z_y.values, rcond=None)[0][0])

rows, R = [], {}
for key in SEL:
    m = pd.read_csv(dc.OUT / key / "s3" / "temporal_member_scores.csv"); m["y"] = -m.social_orth
    d = m[m.known.astype(bool) & m.party.isin(["Democrat", "Republican"])].merge(w, on=["congress", "chamber", "icpsr"], validate="one_to_one")
    grp = d.groupby(["congress", "chamber", "party"])
    for src, dst in [("y", "z_y"), ("abortion", "z_ab"), ("economic", "z_ec")]:
        d[dst] = (d[src] - grp[src].transform("mean")) / grp[src].transform("std")
    d = d.dropna(subset=["z_y", "z_ab", "z_ec"])
    d["era"] = pd.cut(d.year, [1972, 1989, 2005, 2024], labels=["1973-89", "1991-2005", "2007-23"]).astype(str)
    R[key] = {}
    for era, e in d.groupby("era"):
        out = {}
        for ctrl in [True, False]:
            est = {p: fit(e[e.party == p], ctrl) for p in ["Democrat", "Republican"]}
            rng = np.random.default_rng(dc.seed_for("D-S4d", key, era, ctrl) % 2**32); bs = {p: [] for p in est}; diff = []
            groups = {p: {i: g for i, g in e[e.party == p].groupby("icpsr")} for p in est}
            for _ in range(NB):
                b = {}
                for p in est:
                    ids = list(groups[p]); pick = rng.choice(len(ids), len(ids))
                    b[p] = fit(pd.concat([groups[p][ids[i]] for i in pick]), ctrl); bs[p].append(b[p])
                diff.append(b["Republican"] - b["Democrat"])
            tag = "ctrl_econ" if ctrl else "no_ctrl"
            out[tag] = {p: {"b_ab": est[p], "ci95": [float(np.percentile(bs[p], 2.5)), float(np.percentile(bs[p], 97.5))],
                            "n_rows": int((e.party == p).sum()), "n_members": int(e[e.party == p].icpsr.nunique())} for p in est}
            out[tag]["diff_R_minus_D"] = {"est": est["Republican"] - est["Democrat"], "ci95": [float(np.percentile(diff, 2.5)), float(np.percentile(diff, 97.5))]}
            if ctrl:
                for p in est:
                    rows.append(dict(model=key, era=era, party=p, b_ab=round(est[p], 3), ci_lo=round(out[tag][p]["ci95"][0], 3),
                                     ci_hi=round(out[tag][p]["ci95"][1], 3), n_members=out[tag][p]["n_members"]))
                rows.append(dict(model=key, era=era, party="R - D", b_ab=round(out[tag]["diff_R_minus_D"]["est"], 3),
                                 ci_lo=round(out[tag]["diff_R_minus_D"]["ci95"][0], 3), ci_hi=round(out[tag]["diff_R_minus_D"]["ci95"][1], 3), n_members=None))
        R[key][era] = out
T = pd.DataFrame(rows); dc.atomic_csv(T, O / "s4d_table.csv"); dc.atomic_json(R, O / "S4D.json")
print(T.to_string(index=False))
for key in R:
    print(key, "no econ control, R-D:", {era: round(v["no_ctrl"]["diff_R_minus_D"]["est"], 3) for era, v in R[key].items()})
