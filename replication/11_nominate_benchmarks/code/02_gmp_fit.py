#!/usr/bin/env python
"""N2 (PROTOCOL.md): NOMINATE fit (GMP), cross-pressure, map misplacement and W1 vote errors. Two models (guns: Llama only).
  python 02_gmp_fit.py   -> out/n2.json
"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import norm

R = Path(__file__).resolve().parents[1]; KIM = R.parent                   # replication/ (rebuild)
sys.path.insert(0, str(KIM / "06_vote_prediction" / "code")); sys.path.insert(0, str(KIM / "09_named_member_entropy" / "code"))
sys.path.insert(0, str(KIM / "08_error_warning" / "code"))
import estimate_votes as v5  # noqa: E402  (twoway; puts STUDY_D code on the path)
import map_common as dc  # noqa: E402
import named_common as nc  # noqa: E402
import fe_estimators  # noqa: E402  (rebuild: the grid_other.py preamble, formerly exec'd from kim/review/entropy_warning_2026-10-22/code)
oneway = fe_estimators.oneway                                               # Study N estimator: FE within, member CR1
O = R / "out"; O.mkdir(parents=True, exist_ok=True)

hs = pd.read_csv(KIM / "data" / "HSall_members.csv", low_memory=False)[
    ["congress", "chamber", "icpsr", "nominate_geo_mean_probability", "nominate_number_of_errors", "nominate_number_of_votes"]]
assert not hs.duplicated(["congress", "chamber", "icpsr"]).any()   # assert instead of drop_duplicates (Codex 2026-10-23)
hs["err_rate"] = hs.nominate_number_of_errors / hs.nominate_number_of_votes.replace(0, np.nan)


def twoway_with_control(g, y, ctrl):
    """cp coefficient with party x roll-call FE and one control, two-way clustered (FWL: partial out the demeaned control)"""
    e = g[[y, "cp", ctrl, "fe", "icpsr", "key"]].dropna().copy()
    dm = lambda s: s - e.groupby("fe")[s.name].transform("mean")
    yt, xt, zt = dm(e[y]), dm(e.cp), dm(e[ctrl])
    ry = yt - zt * (zt @ yt) / (zt @ zt); rx = xt - zt * (zt @ xt) / (zt @ zt)
    return dof_control(v5.twoway(e.assign(ry=ry, rx=rx), y="ry", x="rx"), len(e), e.fe.nunique())


def oneway_with_control(d, y, ctrl):
    e = d[[y, "cp", ctrl, "fe", "icpsr"]].dropna().copy()
    dm = lambda s: s - e.groupby("fe")[s.name].transform("mean")
    yt, xt, zt = dm(e[y]), dm(e.cp), dm(e[ctrl])
    e["ry"] = yt - zt * (zt @ yt) / (zt @ zt); e["rx"] = xt - zt * (zt @ xt) / (zt @ zt)
    return dof_control(oneway(e, "ry", "rx", "fe", "icpsr"), len(e), e.fe.nunique())


def dof_control(r, N, n_fe):
    """the shared estimators use K = 1 + cells; with the partialled-out control K = 2 + cells (Codex verification 2026-10-23).
    CR1 variance scales by (N - K1) / (N - K2) in every clustering piece, so the SE scales by its square root."""
    f = np.sqrt((N - 1 - n_fe) / (N - 2 - n_fe)); b, se = r["b"], r["se"] * f; r = dict(r, se=se, dof_factor=float(f))
    for k, z in [("95", 1.96), ("90", 1.645)]:
        if f"lo{k}" in r: r[f"lo{k}"], r[f"hi{k}"] = b - z * se, b + z * se
        if f"ci{k}" in r: r[f"ci{k}"] = [b - z * se, b + z * se]
    if "ci_bonf3" in r: r["ci_bonf3"] = [b - 2.394 * se, b + 2.394 * se]
    for k in ["se_member", "se_rollcall"]:
        if k in r: r[k] = r[k] * f
    if "p" in r: r["p"] = float(2 * norm.sf(abs(b / se)))
    return r


short = lambda r: dict(b=r["b"], ci95=[r["lo95"], r["hi95"]] if "lo95" in r else r["ci95"], n=r.get("n"))
res = {}
for m in ["qwen", "llama"]:
    v = nc.analysis_rows(dc.OUT / m / "s3" / "temporal_member_scores.csv")
    n0 = len(v); v = v.merge(hs, on=["congress", "chamber", "icpsr"], how="left", validate="one_to_one")
    assert len(v) == n0
    out = dict(rows=n0, gmp_missing=int(v.nominate_geo_mean_probability.isna().sum()))
    v = v.dropna(subset=["nominate_geo_mean_probability"]).copy()
    v["cp"] = v.vote_q.isin(["EL-ST", "ER-SP"]).astype(float); v["misplaced"] = (v.map_q != v.vote_q).astype(float)
    v["gmp_z"] = (v.nominate_geo_mean_probability - v.nominate_geo_mean_probability.mean()) / v.nominate_geo_mean_probability.std()
    v["fe"] = v.party + "|" + v.congress.astype(str) + "|" + v.chamber
    # 1. is CP a NOMINATE misfit?
    if m == "qwen":
        out["gmp_by_cp"] = dict(mean=v.groupby("cp").nominate_geo_mean_probability.mean().round(4).to_dict(),
                                cp_coef=short(oneway(v, "nominate_geo_mean_probability", "cp", "fe", "icpsr")),
                                err_rate_cp_coef=short(oneway(v, "err_rate", "cp", "fe", "icpsr")),
                                gmp_by_party_cp=v.groupby(["party", "cp"]).nominate_geo_mean_probability.mean().round(4).to_dict().__repr__())
    # 2. map misplacement
    a = oneway(v, "misplaced", "cp", "fe", "icpsr"); b = oneway_with_control(v, "misplaced", "gmp_z")
    out["misplacement"] = dict(cp=short(a), cp_given_gmp=short(b), remaining_share=b["b"] / a["b"],
                               gmp_within_cp=short(oneway(v[v.cp == 1].assign(cp=v.gmp_z), "misplaced", "cp", "fe", "icpsr")),
                               gmp_within_aligned=short(oneway(v[v.cp == 0].assign(cp=v.gmp_z), "misplaced", "cp", "fe", "icpsr")))
    # 3. W1 votes (and Llama guns)
    f = pd.read_parquet(KIM / "06_vote_prediction" / "out" / "v5" / f"frame_v2_{m}_abortion_economic.parquet")
    kk = f.key.str.split("|", expand=True); f["congress"] = kk[0].astype(int); f["chamber"] = kk[1]
    f = f.merge(v[["congress", "chamber", "icpsr", "gmp_z"]], on=["congress", "chamber", "icpsr"], how="left", validate="many_to_one")
    sets = [(iss, g) for iss, g in f.groupby("issue")]
    if m == "llama":
        gf = pd.read_parquet(KIM / "06_vote_prediction" / "out" / "g2" / "frame_llama.parquet")
        gf = gf.merge(v[["congress", "chamber", "icpsr", "gmp_z"]], on=["congress", "chamber", "icpsr"], how="left", validate="many_to_one")
        sets.append(("guns", gf))
    out["votes"] = {}
    for iss, g in sets:
        g = g.dropna(subset=["gmp_z", "correct_avg", "dim1_correct"]).copy()
        g["gain_dim1"] = g.correct_avg - g.dim1_correct
        a = v5.twoway(g.assign(y=g.correct_avg)); b = twoway_with_control(g, "correct_avg", "gmp_z")
        gd = v5.twoway(g.assign(y=g.gain_dim1)); d1 = v5.twoway(g.assign(y=g.dim1_correct))
        out["votes"][iss] = dict(n=len(g), cp=short(a), cp_given_gmp=short(b), remaining_share=b["b"] / a["b"], dim1_reference=short(d1),
                                 gain_over_dim1=short(gd), reading_beyond_nominate=bool(gd["ci95"][1] < 0))
    res[m] = out
    print(m, json.dumps({k: (v_ if not isinstance(v_, dict) else {kk: (vv if not isinstance(vv, dict) else round(vv.get("b", 0), 4)) for kk, vv in v_.items()})
                         for k, v_ in out.items() if k in ("misplacement",)}), flush=True)
    for iss, x in out["votes"].items():
        print("  ", iss, "cp", round(x["cp"]["b"], 4), "| given gmp", round(x["cp_given_gmp"]["b"], 4), "| dim1 ref", round(x["dim1_reference"]["b"], 4),
              "| gain over dim1", round(x["gain_over_dim1"]["b"], 4), [round(z, 4) for z in x["gain_over_dim1"]["ci95"]], flush=True)
res["reading_cp_fitted_worse"] = bool(res["qwen"]["gmp_by_cp"]["cp_coef"]["ci95"][1] < 0)
json.dump(res, open(O / "n2.json", "w"), indent=1, default=float)
print("GMP by CP", res["qwen"]["gmp_by_cp"]["mean"], res["qwen"]["gmp_by_cp"]["cp_coef"], res["reading_cp_fitted_worse"])
