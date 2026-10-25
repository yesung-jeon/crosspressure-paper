#!/usr/bin/env python
"""D (PROTOCOL_D.md): state presidential lean, state cross-pressure, and the models' maps and W1 votes (Congresses 95-117).
  python state_lean.py --synthetic   # planted state effect recovered by the D2 regression
  python state_lean.py               -> out/d/d.json, lean.csv
"""
import argparse, json, sys
import numpy as np, pandas as pd
import speech_estimators as est
from speech_common import O, KIM, dc

sys.path.insert(0, str(KIM / "09_named_member_entropy" / "code"))
import named_common as nc  # noqa: E402
D = O / "d"; D.mkdir(parents=True, exist_ok=True)
SOUTH = {"AL", "AR", "FL", "GA", "LA", "MS", "NC", "SC", "TN", "TX", "VA"}   # T0's list


def lean_table():
    e = pd.read_csv(KIM / "data" / "elections" / "1976-2024-president.csv")
    e = e[e.party_simplified.isin(["DEMOCRAT", "REPUBLICAN"])]
    s = e.groupby(["year", "state_po", "party_simplified"]).candidatevotes.sum().unstack()
    s["dshare"] = s.DEMOCRAT / (s.DEMOCRAT + s.REPUBLICAN)
    nat = e.groupby(["year", "party_simplified"]).candidatevotes.sum().unstack(); nat = nat.DEMOCRAT / (nat.DEMOCRAT + nat.REPUBLICAN)
    s = s.reset_index(); s["lean"] = s.dshare - s.year.map(nat)
    assert not s.duplicated(["year", "state_po"]).any() and s.groupby("year").size().eq(51).all()
    return s[["year", "state_po", "dshare", "lean"]], nat


def election_for(c):
    y = 1787 + 2 * c; return (y - 1) // 4 * 4


def rows(m, L):
    v = nc.analysis_rows(KIM / "02_ideology_map" / "out" / m / "s3" / "temporal_member_scores.csv")
    n_all = len(v); n_9394 = int((v.congress < 95).sum()); v = v[v.congress >= 95].copy()
    v["election"] = v.congress.map(election_for)
    v = v.merge(L.rename(columns={"year": "election", "state_po": "state"}), on=["election", "state"], how="left", validate="many_to_one")
    hs = pd.read_csv(KIM / "data" / "HSall_members.csv", low_memory=False)[["congress", "chamber", "icpsr", "nokken_poole_dim1", "nokken_poole_dim2"]]
    assert not hs.duplicated(["congress", "chamber", "icpsr"]).any()
    v = v.merge(hs, on=["congress", "chamber", "icpsr"], how="left", validate="one_to_one")
    info = dict(paper_rows=n_all, excluded_93_94=n_9394, rows_95_117=len(v), missing_lean=int(v.lean.isna().sum()),
                missing_np=int(v.nokken_poole_dim1.isna().sum()), missing_np_dim2=int(v.nokken_poole_dim2.isna().sum()),
                missing_np_either=int((v.nokken_poole_dim1.isna() | v.nokken_poole_dim2.isna()).sum()))
    v["cp"] = v.vote_q.isin(["EL-ST", "ER-SP"]).astype(float); v["misplaced"] = (v.map_q != v.vote_q).astype(float)
    v["out_lean"] = np.where(v.party == "Democrat", -v.lean, v.lean); v["ccp"] = (v.out_lean > 0).astype(float)
    z = lambda s: (s - s.mean()) / s.std()
    v["lean_z"], v["out_lean_z"] = z(v.lean), z(v.out_lean)
    v["np1"], v["np2"] = v.nokken_poole_dim1, v.nokken_poole_dim2
    v["fe"] = v.party + "|" + v.congress.astype(str) + "|" + v.chamber; v["south"] = v.state.isin(SOUTH)
    return v, info


s_ = lambda r, x: dict(b=r[x]["b"], ci95=r[x]["ci95"], n=r["_n"])


def analyse(m, v):
    out = {}
    sub = {"pooled": v, "House": v[v.chamber == "House"], "Senate": v[v.chamber == "Senate"]}
    # D1
    out["D1"] = {k: dict(cp_on_out_lean=s_(est.fe_ols(g, "cp", ["out_lean_z"], "fe", "icpsr"), "out_lean_z"),
                         ccp_share_by_cp=g.groupby("cp").ccp.mean().to_dict()) for k, g in sub.items()}
    out["D1"]["south"] = {str(k): s_(est.fe_ols(g, "cp", ["out_lean_z"], "fe", "icpsr"), "out_lean_z") for k, g in v.groupby("south")}
    # overlap of the two definitions in member-Congress rows (Codex 2026-10-23)
    out["D1"]["crosstab_rows"] = {f"cp{int(a)}_ccp{int(b)}": int(n) for (a, b), n in v.groupby(["cp", "ccp"]).size().items()}
    # D2
    d2 = {}
    for k, g in sub.items():
        rx = est.fe_ols(g, "x", ["lean_z", "economic", "np1", "np2"], "fe", "icpsr"); ry = est.fe_ols(g, "y", ["lean_z", "abortion", "np1", "np2"], "fe", "icpsr")
        d2[k] = dict(x=s_(rx, "lean_z"), y=s_(ry, "lean_z"), x_vote_control=s_(rx, "economic"), y_vote_control=s_(ry, "abortion"),
                     ref_economic_on_lean=s_(est.fe_ols(g, "economic", ["lean_z"], "fe", "icpsr"), "lean_z"),
                     ref_abortion_on_lean=s_(est.fe_ols(g, "abortion", ["lean_z"], "fe", "icpsr"), "lean_z"))
    out["D2"] = d2
    # descriptive scale (not registered): map coordinates are in each model's own units; SDs of x and y within FE cells
    wsd = lambda c: float((v[c] - v.groupby("fe")[c].transform("mean")).std())
    out["D2_scale"] = dict(x_within_sd=wsd("x"), y_within_sd=wsd("y"), x_lean_per_within_sd=d2["pooled"]["x"]["b"] / wsd("x"),
                           y_lean_per_within_sd=d2["pooled"]["y"]["b"] / wsd("y"))
    out["reading_RD2_x"] = bool(d2["pooled"]["x"]["ci95"][1] < 0); out["reading_RD2_y"] = bool(d2["pooled"]["y"]["ci95"][1] < 0)
    # D3 map
    out["D3_map"] = {k: dict(misplaced_on_ccp=s_(est.fe_ols(g, "misplaced", ["ccp"], "fe", "icpsr"), "ccp"),
                             recall_by_ccp=(1 - g.groupby("ccp").misplaced.mean()).to_dict()) for k, g in sub.items()}
    # D3 W1
    f = pd.read_parquet(KIM / "06_vote_prediction" / "out" / "v5" / f"frame_v2_{m}_abortion_economic.parquet")
    sets = [(i, g) for i, g in f.groupby("issue")]
    if m == "llama": sets.append(("guns", pd.read_parquet(KIM / "06_vote_prediction" / "out" / "g2" / "frame_llama.parquet")))
    w1 = {}
    for iss, g in sets:
        g = g.copy()
        if "congress" not in g or "chamber" not in g:
            kk = g.key.str.split("|", expand=True); g["congress"] = kk[0].astype(int); g["chamber"] = kk[1]
        n0 = len(g); g = g[g.congress >= 95]
        g = g.merge(v[["congress", "chamber", "icpsr", "ccp"]], on=["congress", "chamber", "icpsr"], how="left", validate="many_to_one")
        miss = int(g.ccp.isna().sum()); g = g.dropna(subset=["ccp"])
        a = v5_tw(g); sen = v5_tw(g[g.chamber == "Senate"]); hou = v5_tw(g[g.chamber == "House"])     # House-only added (PROTOCOL_D: every table by chamber)
        w1[iss] = dict(rows_all=n0, rows_95_117=int(len(g) + miss), missing_ccp=miss, ccp=a, senate_only=sen, house_only=hou,
                       reading_RD3=bool(a["ci95"][1] < 0))
    out["D3_W1"] = w1
    return out


def v5_tw(g):
    r = est.v5.twoway(g.assign(y=g.correct_avg), y="y", x="ccp"); return dict(b=r["b"], ci95=r["ci95"], n=r["n"])


def main():
    L, nat = lean_table(); L.to_csv(D / "lean.csv", index=False)
    res = dict(national_dshare={int(k): float(x) for k, x in nat.items()})
    for m in ["qwen", "llama"]:
        v, info = rows(m, L); res[m] = dict(info=info, **analyse(m, v))
        r = res[m]
        print(m, info, "| D2 x", round(r["D2"]["pooled"]["x"]["b"], 4), [round(z, 4) for z in r["D2"]["pooled"]["x"]["ci95"]],
              "y", round(r["D2"]["pooled"]["y"]["b"], 4), [round(z, 4) for z in r["D2"]["pooled"]["y"]["ci95"]],
              "| W1", {k: (round(x["ccp"]["b"], 4), [round(z, 4) for z in x["ccp"]["ci95"]]) for k, x in r["D3_W1"].items()}, flush=True)
    dc.atomic_json(res, D / "d.json")


def synthetic():
    """planted: map x = votes + state effect -0.3 per lean SD (+ noise); D2 must recover -0.3 and ~0 when no state effect"""
    rng = np.random.default_rng(11); n = 6000
    v = pd.DataFrame(dict(state=rng.integers(0, 50, n), party=rng.choice(["Democrat", "Republican"], n), congress=rng.integers(95, 118, n),
                          chamber="House", icpsr=rng.integers(0, 1500, n)))
    lean = pd.Series(rng.normal(size=50)); v["lean_z"] = v.state.map(lean)
    v["lean_z"] = (v.lean_z - v.lean_z.mean()) / v.lean_z.std()        # standardized over rows as in rows() (Codex 2026-10-23)
    v["economic"] = rng.normal(size=n) - 0.4 * v.lean_z
    v["np1"] = v.economic + rng.normal(0, .3, n); v["np2"] = rng.normal(size=n); v["fe"] = v.party + "|" + v.congress.astype(str)
    out = {}
    for eff in [-0.3, 0.0]:
        v["x"] = v.economic + eff * v.lean_z + rng.normal(0, .5, n)
        out[str(eff)] = est.fe_ols(v, "x", ["lean_z", "economic", "np1", "np2"], "fe", "icpsr")["lean_z"]["b"]
    out["pass"] = bool(abs(out["-0.3"] + 0.3) < 0.03 and abs(out["0.0"]) < 0.03)
    dc.atomic_json(out, D / "synthetic.json"); print(out)
    if not out["pass"]: raise SystemExit("STOP: synthetic failed")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--synthetic", action="store_true"); a = ap.parse_args()
    synthetic() if a.synthetic else main()
