#!/usr/bin/env python
"""G0 steps 3-4 (PROTOCOL_G0 sections 2-4): final labels (author's judgment wherever given, else the agreed Claude/GPT label), the gun
scale per Congress x chamber with the orientation and pass conditions fixed in the protocol, and the gun CP rows (Qwen map rows).
  python 03_build_gun_scale.py   -> out/g0/included.csv, gun_scales.csv, cells.csv, gun_cp_rows.csv, report.json
"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd

G = Path(__file__).resolve().parents[1]; KIM = G.parent; O = G / "out" / "g0"
sys.path.insert(0, str(KIM / "02_ideology_map" / "code"))
import map_common as dc  # noqa: E402
KEY = ["congress", "chamber", "rollnumber"]

m = pd.read_csv(O / "labels_merged.csv").fillna("")
a = pd.read_csv(O / "AUTHOR_REVIEW.csv", encoding="utf-8-sig").fillna("")
a = a[~a.review.str.startswith("out-of-regex")][["key", "author_gun_control", "author_yea_direction"]]
a["author_gun_control"] = a.author_gun_control.str.strip(); a["author_yea_direction"] = a.author_yea_direction.str.strip()
assert a.author_gun_control.isin(["yes", "no"]).all()
m = m.merge(a, on="key", how="left", validate="1:1")
by_author = m.author_gun_control.ne("") & m.author_gun_control.notna()
m["final_gun"] = np.where(by_author, m.author_gun_control, np.where(m.agree, m.gun_control_claude, ""))
m["final_dir"] = np.where(by_author, np.where(m.author_gun_control == "yes", m.author_yea_direction, ""), np.where(m.agree, m.yea_direction_claude, ""))
assert (m.final_gun != "").all(), "every candidate must have a final label"
m["source"] = np.where(by_author, "author", "agreed")
m["included"] = (m.final_gun == "yes") & m.final_dir.isin(["stricter", "looser"])
m[["key", "final_gun", "final_dir", "source", "included"]].to_csv(O / "included.csv", index=False)
inc = m[m.included].copy()
inc[["congress", "chamber", "rollnumber"]] = inc.key.str.split("|", expand=True); inc["congress"] = inc.congress.astype(int); inc["rollnumber"] = inc.rollnumber.astype(int)

# votes for included roll calls
want = set(map(tuple, inc[KEY].values)); parts = []
for ch in pd.read_csv(KIM / "data" / "voteview_all" / "HSall_votes.csv", usecols=KEY + ["icpsr", "cast_code"], chunksize=4_000_000,
                      dtype={"congress": "int16", "rollnumber": "int32", "icpsr": "int32", "cast_code": "int8"}):
    ch = ch[ch.congress.between(80, 118)]
    if ch.empty: continue
    k = list(zip(ch.congress, ch.chamber, ch.rollnumber)); parts.append(ch[np.fromiter((x in want for x in k), bool, len(k))])
V = pd.concat(parts, ignore_index=True)
V["v"] = np.where(V.cast_code.between(1, 3), 1.0, np.where(V.cast_code.between(4, 6), 0.0, np.nan))
V = V.merge(inc[KEY + ["final_dir"]], on=KEY, validate="m:1")
V["r"] = np.where(V.final_dir == "stricter", V.v, 1 - V.v)          # 1 = toward stricter regulation


def build(g):
    M = g.pivot_table(index="icpsr", columns="rollnumber", values="r", aggfunc="first")
    M = M[M.notna().sum(1) >= 3]
    if M.shape[1] < 3 or len(M) < 20: return None
    X = M.values; mu = np.nanmean(X, 0); Z = np.where(np.isnan(X), 0.0, X - mu)
    U, S, Vt = np.linalg.svd(Z, full_matrices=False); sc, ld = U[:, 0] * S[0], Vt[0]
    sign = -1.0 if ld.mean() > 0 else 1.0                                # higher score = more votes against regulation
    return M, sign * sc, sign * ld, float(S[0] ** 2 / (S ** 2).sum())


cells, scales = [], []
for (c, chm), g in V.groupby(["congress", "chamber"]):
    b = build(g); info = dict(congress=int(c), chamber=chm, n_rollcalls=int(g.rollnumber.nunique()))
    if b is None: cells.append(dict(info, built=False, passed=False, reason="fewer than 3 roll calls or 20 members")); continue
    M, sc, ld, share = b
    agree = float((ld < 0).mean())                                       # recoded pro-regulation votes load negatively
    loo = []
    for rn in M.columns:
        bb = build(g[g.rollnumber != rn])
        if bb is None: loo.append(np.nan); continue
        s2 = pd.Series(bb[1], index=bb[0].index).reindex(M.index)
        ok = s2.notna(); loo.append(float(np.corrcoef(sc[ok.values], s2[ok].values)[0, 1]) if ok.sum() > 10 else np.nan)
    # PROTOCOL: every leave-one-out correlation >= 0.9 (Codex verification 2026-10-22: signed, and an undefined one fails the cell;
    # the first version used abs() and nanmin(), which could hide a sign flip or skip an undefined value)
    loo_all = bool(len(loo) and np.isfinite(loo).all()); loo_min = float(np.min(loo)) if loo_all else np.nan
    passed = bool(agree >= 0.8 and loo_all and loo_min >= 0.9)
    cells.append(dict(info, built=True, n_members=int(len(M)), pc1_share=share, loading_sign_agreement=agree, loo_min_corr=loo_min,
                      loo_corrs=";".join(f"{x:.4f}" for x in loo), passed=passed,
                      reason="" if passed else ("loading agreement < 0.8" if agree < 0.8 else "leave-one-out corr < 0.9 or undefined")))
    if passed: scales.append(pd.DataFrame(dict(congress=int(c), chamber=chm, icpsr=M.index, gun_score=np.round(sc, 10), n_votes=M.notna().sum(1).values)))   # tie rule (author 2026-10-23): 10 decimals
C = pd.DataFrame(cells); C.to_csv(O / "cells.csv", index=False)
S = pd.concat(scales, ignore_index=True) if scales else pd.DataFrame(columns=["congress", "chamber", "icpsr", "gun_score", "n_votes"])
S.to_csv(O / "gun_scales.csv", index=False)

# gun CP rows: Qwen map rows (D/R), economic score from the sealed issue_scales, gun score from passing cells
sc0 = pd.read_csv(dc.ISSUE_SCALES); econ = sc0[sc0.issue == "economic"][["congress", "chamber", "icpsr", "rc_score"]].rename(columns={"rc_score": "economic"})
ab = sc0[sc0.issue == "abortion"][["congress", "chamber", "icpsr", "rc_score"]].rename(columns={"rc_score": "abortion"})
mp = pd.read_csv(dc.OUT / "qwen" / "s3" / "temporal_member_scores.csv")[["congress", "chamber", "icpsr", "party", "state", "known"]]
R = mp[mp.party.isin(["Democrat", "Republican"])].merge(econ, on=["congress", "chamber", "icpsr"], how="left", validate="one_to_one") \
    .merge(S[["congress", "chamber", "icpsr", "gun_score"]], on=["congress", "chamber", "icpsr"], how="left", validate="one_to_one") \
    .merge(ab, on=["congress", "chamber", "icpsr"], how="left", validate="one_to_one")
R = R.dropna(subset=["economic", "gun_score"]).copy(); R["cc"] = R.congress.astype(str) + R.chamber
hi_e = R.economic > R.groupby("cc").economic.transform("median"); hi_g = R.gun_score > R.groupby("cc").gun_score.transform("median")
R["gun_q"] = pd.Series(np.where(hi_e, "ER-", "EL-"), index=R.index) + np.where(hi_g, "ST", "SP"); R["gun_cp"] = R.gun_q.isin(["EL-ST", "ER-SP"]).astype(int)
R.to_csv(O / "gun_cp_rows.csv", index=False)
both = R.dropna(subset=["abortion"]).copy()
hi_a = both.abortion > both.groupby("cc").abortion.transform("median"); hi_e2 = both.economic > both.groupby("cc").economic.transform("median")
both["ab_cp"] = ((hi_e2 & ~hi_a) | (~hi_e2 & hi_a)).astype(int)
rep = dict(candidates_contested=int(len(m)), final={f"{g}/{d}": int(n) for (g, d), n in m.groupby(["final_gun", "final_dir"]).size().items()},
           label_source=m.source.value_counts().to_dict(), included=int(m.included.sum()),
           out_of_regex_misses=["112|House|838"], cells_built=int(C.built.sum()), cells_passed=int(C.passed.sum()),
           cells_failed=C[C.built & ~C.passed][["congress", "chamber", "reason"]].astype(str).values.tolist(),
           gun_cp_rows=int(len(R)), gun_cp_share=float(R.gun_cp.mean()) if len(R) else None,
           overlap_with_abortion_cp=dict(rows_with_both=int(len(both)), same_label_share=float((both.ab_cp == both.gun_cp).mean()) if len(both) else None,
                                         corr_gun_abortion=float(both[["gun_score", "abortion"]].corr().iloc[0, 1]) if len(both) else None),
           corr_gun_economic=float(R[["gun_score", "economic"]].corr().iloc[0, 1]) if len(R) else None,
           descriptive_only=bool(C.passed.sum() < 10))
json.dump(rep, open(O / "report.json", "w"), indent=1, default=str); print(json.dumps(rep, indent=1, default=str))
