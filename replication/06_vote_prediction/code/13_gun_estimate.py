#!/usr/bin/env python
"""G2 analysis (PROTOCOL_A14.md): gun votes, Qwen and Llama, W1 code path.
  python 13_gun_estimate.py --gate      # leave-one-out gun CP: rebuild without exclusion reproduces gun_scales.csv and gun_cp exactly
  python 13_gun_estimate.py --model qwen
Outputs: out/g2/frame_{model}.parquet, estimates_{model}.json (grid_{model}.csv: E grid, excluded in the rebuild)
"""
import argparse, json, sys
from pathlib import Path
import numpy as np, pandas as pd

V = Path(__file__).resolve().parents[1]; KIM = V.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(KIM / "08_error_warning" / "code"))      # rebuild: kim/review/entropy_warning_2026-10-22/code
import estimate_votes as v5  # noqa: E402  (twoway, competence, read_parts)
import map_common as dc  # noqa: E402
import error_warning as ew  # noqa: E402  (hb, metrics, boot_diff, calib, grid, interaction)

O = V / "out" / "g2"; G0 = KIM / "05_gun_scale" / "out" / "g0"
KEY = ["congress", "chamber", "rollnumber"]


# ---- gun scale, copied from 05_gun_scale/code/g0_scale.py build() ----
def build(g):
    M = g.pivot_table(index="icpsr", columns="rollnumber", values="r", aggfunc="first")
    M = M[M.notna().sum(1) >= 3]
    if M.shape[1] < 3 or len(M) < 20: return None
    X = M.values; mu = np.nanmean(X, 0); Z = np.where(np.isnan(X), 0.0, X - mu)
    U, S, Vt = np.linalg.svd(Z, full_matrices=False); sc, ld = U[:, 0] * S[0], Vt[0]
    sign = -1.0 if ld.mean() > 0 else 1.0
    return pd.Series(np.round(sign * sc, 10), index=M.index)          # tie rule (author 2026-10-23): as 03_build_gun_scale.py


def gun_votes():
    inc = pd.read_csv(G0 / "included.csv"); inc = inc[inc.included].copy()
    inc[KEY] = inc.key.str.split("|", expand=True); inc["congress"] = inc.congress.astype(int); inc["rollnumber"] = inc.rollnumber.astype(int)
    cells = pd.read_csv(G0 / "cells.csv"); cells = cells[cells.passed]
    inc = inc.merge(cells[["congress", "chamber"]], on=["congress", "chamber"])
    want = set(map(tuple, inc[KEY].values)); parts = []
    for ch in pd.read_csv(KIM / "data" / "voteview_all" / "HSall_votes.csv", usecols=KEY + ["icpsr", "cast_code"], chunksize=4_000_000,
                          dtype={"congress": "int16", "rollnumber": "int32", "icpsr": "int32", "cast_code": "int8"}):
        ch = ch[ch.congress.between(80, 118)]
        if ch.empty: continue
        k = list(zip(ch.congress, ch.chamber, ch.rollnumber)); parts.append(ch[np.fromiter((x in want for x in k), bool, len(k))])
    Vv = pd.concat(parts, ignore_index=True)
    Vv["v"] = np.where(Vv.cast_code.between(1, 3), 1.0, np.where(Vv.cast_code.between(4, 6), 0.0, np.nan))
    Vv = Vv.merge(inc[KEY + ["final_dir"]], on=KEY, validate="m:1")
    Vv["r"] = np.where(Vv.final_dir == "stricter", Vv.v, 1 - Vv.v)
    return Vv


def gun_cp_labels(rows, gs):
    e = rows.economic; s = rows.icpsr.map(gs); ok = s.notna()
    he = e > e[ok].median(); hg = s > s[ok].median()
    cp = ((he & ~hg) | (~he & hg)).astype(float)
    return pd.Series(np.where(ok, cp, np.nan), index=rows.index)


def gate():
    Vv = gun_votes(); R = pd.read_csv(G0 / "gun_cp_rows.csv"); S = pd.read_csv(G0 / "gun_scales.csv")
    mx, mism = 0.0, 0
    for (c, chm), g in Vv.groupby(["congress", "chamber"]):
        gs = build(g); ref = S[(S.congress == c) & (S.chamber == chm)].set_index("icpsr").gun_score
        mx = max(mx, float((gs.reindex(ref.index) - ref).abs().max()))
        r = R[(R.congress == c) & (R.chamber == chm)]
        mism += int((gun_cp_labels(r, gs) != r.gun_cp).sum())
    out = dict(max_abs_diff=mx, cp_mismatch=mism, passed=bool(mx < 1e-9 and mism == 0))
    dc.atomic_json(out, O / "gate_loo.json"); print(out)
    if not out["passed"]: raise SystemExit("STOP: gun LOO gate failed")


def loo_labels():
    Vv = gun_votes(); R = pd.read_csv(G0 / "gun_cp_rows.csv"); lab = []
    keyset = set(pd.read_parquet(O / "prompts.parquet", columns=["key"]).key)
    for (c, chm), g in Vv.groupby(["congress", "chamber"]):
        r = R[(R.congress == c) & (R.chamber == chm)]
        for rn in g.rollnumber.unique():
            k = f"{c}|{chm}|{rn}"
            if k not in keyset: continue
            gs = build(g[g.rollnumber != rn])
            cp = gun_cp_labels(r, gs) if gs is not None else pd.Series(np.nan, index=r.index)
            lab.append(pd.DataFrame(dict(key=k, icpsr=r.icpsr.values, gun_cp_loo=cp.values)))
    return pd.concat(lab, ignore_index=True) if lab else pd.DataFrame(columns=["key", "icpsr", "gun_cp_loo"])


def frame(model):
    P = pd.read_parquet(O / "prompts.parquet")
    A = v5.read_parts(model, "guns"); B = v5.read_parts(model, "swap_guns"); B["pid"] = B.pid.str.replace(r"\|swap$", "|main", regex=True)
    d = P.merge(A[["pid", "p_yea", "p_nay"]], on="pid", validate="one_to_one").merge(B[["pid", "p_yea", "p_nay"]], on="pid", suffixes=("_yf", "_nf"), validate="one_to_one")
    assert len(d) == len(P), (len(d), len(P))
    d["format_fail"] = ((d.p_yea_yf + d.p_nay_yf) < 0.5) | ((d.p_yea_nf + d.p_nay_nf) < 0.5)
    d["share_yf"] = d.p_yea_yf / (d.p_yea_yf + d.p_nay_yf); d["share_nf"] = d.p_yea_nf / (d.p_yea_nf + d.p_nay_nf); d["share_avg"] = (d.share_yf + d.share_nf) / 2
    for s in ["yf", "nf", "avg"]:
        d[f"pred_{s}"] = (d[f"share_{s}"] > 0.5).astype(int); d[f"correct_{s}"] = np.where(d.format_fail, np.nan, (d[f"pred_{s}"] == d.actual).astype(float))
    p = d.share_avg.clip(1e-6, 1 - 1e-6)
    d["brier"] = (d.share_avg - d.actual) ** 2; d["logloss"] = -(d.actual * np.log(p) + (1 - d.actual) * np.log(1 - p))
    d["fe"] = d.party + "|" + d.key
    d["party_correct"] = np.where(d.party_tie, np.nan, (d.actual == (d.party_yea_share > 0.5)).astype(float))
    d["gain_over_party"] = d.correct_avg - d.party_correct
    mv = pd.read_csv(O / "member_votes.csv.gz", usecols=KEY + ["icpsr", "dim1"]); mv["key"] = mv.congress.astype(str) + "|" + mv.chamber + "|" + mv.rollnumber.astype(str)
    d = d.merge(mv[["key", "icpsr", "dim1"]], on=["key", "icpsr"], how="left", validate="one_to_one")
    from sklearn.linear_model import LogisticRegression
    d["dim1_correct"] = np.nan
    for k, g in d[d.dim1.notna()].groupby("key"):
        if g.actual.nunique() < 2: d.loc[g.index, "dim1_correct"] = 1.0; continue
        mdl = LogisticRegression(C=1e6, max_iter=1000).fit(g[["dim1"]].values, g.actual.values)
        d.loc[g.index, "dim1_correct"] = (mdl.predict(g[["dim1"]].values) == g.actual.values).astype(float)
    kn = pd.read_csv(dc.OUT / model / "s3" / "temporal_member_scores.csv", usecols=["congress", "chamber", "icpsr", "known"])
    d = d.drop(columns="known").merge(kn, on=["congress", "chamber", "icpsr"], how="left", validate="many_to_one")
    d["H"] = (ew.hb(d.share_yf) + ew.hb(d.share_nf)) / 2; d["err"] = 1 - d.correct_avg
    rc = pd.read_csv(O / "rollcalls.csv"); t = (rc.vote_desc.fillna("") + " " + rc.vote_question.fillna("") + " " + rc.dtl_desc.fillna("")).str.upper()
    rc["amend"] = t.str.contains("AMEND") & ~t.str.contains("PASS")
    d = d.merge(rc[["key", "amend"]], on="key", validate="many_to_one")
    d["era"] = pd.cut(d.congress, [92, 100, 108, 117], labels=["93-100", "101-108", "109-117"]).astype(str)
    d = d.merge(loo_labels(), on=["key", "icpsr"], how="left", validate="one_to_one")
    return d


def toward_party(g):
    w = g[(g.err == 1) & ~g.party_tie]; maj = (w.party_yea_share > 0.5).astype(int)
    return float((w.pred_avg == maj).mean()) if len(w) else np.nan, len(w)


def run(model):
    d = frame(model); d.to_parquet(O / f"frame_{model}.parquet", index=False)
    # Codex verification 2026-10-22: the first version had an always-true assert here. Format failures are reported and excluded from
    # the warning analysis (error undefined); both models had none.
    n_ff = int(d.format_fail.sum())
    res = dict(model=model, n=len(d), rollcalls=int(d.key.nunique()), format_fail=float(d.format_fail.mean()),
               competence=v5.competence(d), corr_two_orders=float(np.corrcoef(d.share_yf, d.share_nf)[0, 1]))
    by = d.groupby("cp")
    res["descriptive"] = dict(n=by.size().to_dict(), accuracy=by.correct_avg.mean().round(4).to_dict(),
                              accuracy_yf=by.correct_yf.mean().round(4).to_dict(), accuracy_nf=by.correct_nf.mean().round(4).to_dict(),
                              party_rule=by.party_correct.mean().round(4).to_dict(), dim1_reference=by.dim1_correct.mean().round(4).to_dict(),
                              share_pred_yea=by.pred_avg.mean().round(4).to_dict(), share_actual_yea=by.actual.mean().round(4).to_dict(),
                              mean_H=by.H.mean().round(4).to_dict())
    tw = lambda g, y, x="cp": v5.twoway(g.assign(y=g[y], cp=g[x]))
    res["regressions_abortion_cp"] = {"accuracy (6.1)": tw(d, "correct_avg"), "party_rule (6.2a)": tw(d, "party_correct"),
                                      "dim1_reference (6.2b)": tw(d, "dim1_correct"), "gain_over_party (6.2c)": tw(d, "gain_over_party"),
                                      "brier": tw(d, "brier"), "recognized_only": tw(d[d.known.astype(bool)], "correct_avg"),
                                      "yea_first_only": tw(d, "correct_yf"), "nay_first_only": tw(d, "correct_nf"), "entropy H": tw(d, "H")}
    res["by_party_abortion_cp"] = {p: dict(accuracy=v5.twoway(g.assign(y=g.correct_avg)), entropy=v5.twoway(g.assign(y=g.H)))
                                   for p, g in d.groupby("party")}
    gl = d[d.gun_cp_loo.notna()]
    res["gun_cp_loo"] = dict(n=len(gl), rollcalls=int(gl.key.nunique()), cp_share=float(gl.gun_cp_loo.mean()),
                             accuracy=tw(gl, "correct_avg", "gun_cp_loo"), party_rule=tw(gl, "party_correct", "gun_cp_loo"),
                             entropy=tw(gl, "H", "gun_cp_loo"), abortion_cp_same_rows=tw(gl, "correct_avg"))
    res["error_direction"] = {f"cp={c}": dict(zip(["toward_party_share", "n_wrong"], toward_party(g))) for c, g in d.groupby("cp")}
    rng = np.random.default_rng(dc.seed_for("G2W", model) % 2**32)
    dw = d[~d.format_fail].reset_index(drop=True); res["format_fail_rows"] = n_ff
    m1, m0 = ew.metrics(dw[dw.cp == 1]), ew.metrics(dw[dw.cp == 0]); ci = ew.boot_diff(dw, rng)
    res["warning"] = dict(cp=m1, aligned=m0, diff={k: m1[k] - m0[k] for k in ci}, diff_ci95=ci,
                          reading_warns_less_for_cp=bool(ci["auroc_within"][1] < 0 or ci["conf_share_of_wrong"][0] > 0))
    # rebuild (author 2026-10-23): the E subgroup grid (grid_{model}.csv) is excluded; grid() uses no random numbers, so nothing else changes
    dc.atomic_json(res, O / f"estimates_{model}.json")
    r = res["regressions_abortion_cp"]["accuracy (6.1)"]
    print(model, "competent", res["competence"]["competent"], "acc al/cp", res["descriptive"]["accuracy"], "6.1", round(r["b"], 4), [round(x, 4) for x in r["ci95"]],
          "| gun LOO", round(res["gun_cp_loo"]["accuracy"]["b"], 4), "| toward party", res["error_direction"], flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--gate", action="store_true"); ap.add_argument("--model"); a = ap.parse_args()
    gate() if a.gate else run(a.model)
