#!/usr/bin/env python
"""Gap fill (PLAN.md + PLAN_REVIEW.md, sealed in PROTOCOL_SEAL.json): extensions of sealed analyses to the missing issues and definitions.
  G1 S2c error direction on economic and gun votes      G2 gun-defined CP for S2a/S2b, D1/D3 map, N2(1)/(2)
  G3 social axis (y) history: S1-y and N1-y              G4 L1 (map misplacement vs vote errors) on gun votes
Each part first reproduces the sealed original with the same code (gate; STOP if not equal), then runs the extension.
  python 01_fill_gaps.py --synthetic     # planted gun-CP effect on the real gun rows; growth-share denominator rule
  python 01_fill_gaps.py                 -> out/gf.json
"""
import argparse, importlib.util, json, sys
from pathlib import Path
import numpy as np, pandas as pd

R = Path(__file__).resolve().parents[1]; KIM = R.parent                   # replication/ (rebuild)
SD, NOM, EW = KIM / "12_speech_and_state", KIM / "11_nominate_benchmarks", KIM / "08_error_warning"   # rebuild: kim/review/<dated folders>
for p in [SD / "code", KIM / "09_named_member_entropy" / "code", KIM / "06_vote_prediction" / "code"]: sys.path.insert(0, str(p))
import speech_estimators as est  # noqa: E402  (FE OLS, member CR1, K = regressors + FE cells; also loads estimate_votes)
import named_common as nc  # noqa: E402
import map_common as dc  # noqa: E402
v5 = est.v5
O = R / "out"; O.mkdir(parents=True, exist_ok=True)
CROSS = ["EL-ST", "ER-SP"]; MODELS = ["qwen", "llama"]; MIN_CP_MEMBERS = 30
HS = pd.read_csv(KIM / "data" / "HSall_members.csv", low_memory=False)
assert not HS.duplicated(["congress", "chamber", "icpsr"]).any()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def close(a, b, tol=1e-9):
    """nested numeric equality for the gates"""
    if isinstance(a, dict): return all(close(a[k], b[k], tol) for k in a)
    if isinstance(a, (list, tuple)): return len(a) == len(b) and all(close(x, y, tol) for x, y in zip(a, b))
    return abs(float(a) - float(b)) < tol


def gate(name, ok):
    if not ok: raise SystemExit(f"STOP: gate {name} failed")
    return True


def fe(d, y, xs, cpcol=None):
    """est.fe_ols with party x Congress x chamber FE and member clusters; adds CP-member count and the small-sample flag"""
    r = est.fe_ols(d, y, xs, "fe", "icpsr")
    out = {x: dict(b=r[x]["b"], ci95=r[x]["ci95"]) for x in ([xs] if isinstance(xs, str) else xs)}
    out.update(n=r["_n"], members=r["_clusters"], fe_cells=r["_fe_cells"])
    if cpcol is not None:
        e = d[[y, *([xs] if isinstance(xs, str) else xs), "fe", "icpsr"]].dropna().index
        k = int(d.loc[e][d.loc[e, cpcol] == 1].icpsr.nunique()); out["cp_members"] = k; out["too_few_cp_members"] = k < MIN_CP_MEMBERS
    return out


def sk(s):
    """series -> dict with string keys (JSON)"""
    return {str(k): float(x) for k, x in s.items()}


def paper(m):
    v = nc.analysis_rows(dc.OUT / m / "s3" / "temporal_member_scores.csv")
    v["cp"] = v.vote_q.isin(CROSS).astype(float); v["misplaced"] = (v.map_q != v.vote_q).astype(float)
    v["fe"] = v.party + "|" + v.congress.astype(str) + "|" + v.chamber
    return v


def s2_rows(m):
    """S2 sample exactly as 03_member_speech.py: paper rows <= 114 with speech partisanship; p_z over this sample"""
    P = pd.read_csv(SD / "out" / "s2" / "member_p.csv")
    v = paper(m); v = v[v.congress <= 114].merge(P[["congress", "chamber", "icpsr", "p", "party"]].rename(columns={"party": "sp_party"}),
                                                 on=["congress", "chamber", "icpsr"], how="left", validate="one_to_one")
    v = v.dropna(subset=["p"]).copy(); v["p_z"] = (v.p - v.p.mean()) / v.p.std()
    return v, dict(mean=float(v.p.mean()), sd=float(v.p.std()))


def gun_rows(m):
    """gun-defined rows of G0 with G1's map quadrant (median split within the gun rows' Congress x chamber cell, as 05_map_benchmark.py;
    quad() is copied from there because 05_map_benchmark.py runs on import; the gate checks G1's sealed recall)"""
    quad = lambda hx, hy: pd.Series(np.where(hx, "ER-", "EL-"), index=hx.index) + np.where(hy, "ST", "SP")
    g = pd.read_csv(KIM / "05_gun_scale" / "out" / "g0" / "gun_cp_rows.csv")
    mp = pd.read_csv(dc.OUT / m / "s3" / "temporal_member_scores.csv")[["congress", "chamber", "icpsr", "econ_orth", "social_orth"]]
    d = g.merge(mp, on=["congress", "chamber", "icpsr"], how="left", validate="one_to_one")
    assert d.econ_orth.notna().all() and d.social_orth.notna().all() and d.gun_q.notna().all()     # both coordinates (Codex 2026-10-23)
    d["x"], d["y"] = -d.econ_orth, -d.social_orth
    d["map_q_gun"] = quad(d.x > d.groupby("cc").x.transform("median"), d.y > d.groupby("cc").y.transform("median"))
    assert (d.gun_cp == d.gun_q.isin(CROSS).astype(int)).all()
    d["misplaced_gun"] = (d.map_q_gun != d.gun_q).astype(float); d["fe"] = d.party + "|" + d.congress.astype(str) + "|" + d.chamber
    return d


def with_paper(d, v, cols):
    """attach the original (abortion-quadrant) definition from the paper rows; rows not in the paper sample get NaN"""
    return d.merge(v[["congress", "chamber", "icpsr", *cols]], on=["congress", "chamber", "icpsr"], how="left", validate="one_to_one")


# ---------------------------------------------------------------- G1: S2c on economic and gun votes
def s2c(f, v, cpcol):
    n_frame = len(f); n_le114 = int((f.congress <= 114).sum())
    f = f.merge(v[["congress", "chamber", "icpsr", "p_z"]], on=["congress", "chamber", "icpsr"], how="inner", validate="many_to_one")
    w = f[(f[cpcol] == 1) & (f.correct_avg == 0) & f.party_yea_share.notna() & (f.party_yea_share != 0.5)].copy()
    w["toward"] = (w.pred_avg == (w.party_yea_share > 0.5).astype(int)).astype(float)
    r = est.fe_ols(w, "toward", ["p_z"], "key", "icpsr")
    return dict(b=r["p_z"]["b"], ci95=r["p_z"]["ci95"], n=r["_n"], members=r["_clusters"], toward_share=float(w.toward.mean()),
                ledger=dict(frame_votes=n_frame, votes_congress_le_114=n_le114, votes_with_p=len(f), cp_wrong_with_majority=len(w)))


def part1():
    out = {}
    for m in MODELS:
        v, _ = s2_rows(m); sealed = json.loads((SD / "out" / "s2" / "s2.json").read_text())[m]
        f = pd.read_parquet(KIM / "06_vote_prediction" / "out" / "v5" / f"frame_v2_{m}_abortion_economic.parquet")
        kk = f.key.str.split("|", expand=True); f["congress"] = kk[0].astype(int); f["chamber"] = kk[1]
        ab = s2c(f[f.issue == "abortion"], v, "cp")
        gate(f"G1-{m}", close(dict(b=sealed["S2c_toward_party_on_p"]["b"], ci95=sealed["S2c_toward_party_on_p"]["ci95"]),
                              dict(b=ab["b"], ci95=ab["ci95"])) and abs(ab["toward_share"] - sealed["S2c_toward_share"]) < 1e-12)
        g = pd.read_parquet(KIM / "06_vote_prediction" / "out" / "g2" / f"frame_{m}.parquet")
        out[m] = dict(gate="abortion S2c reproduced", abortion=ab, economic=s2c(f[f.issue == "economic"], v, "cp"),
                      guns=s2c(g, v, "cp"), guns_gun_cp_loo=s2c(g, v, "gun_cp_loo"), guns_interpreted=(m == "llama"))
        print("G1", m, {k: (round(x["b"], 4), [round(z, 4) for z in x["ci95"]], x["n"]) for k, x in out[m].items() if isinstance(x, dict)}, flush=True)
    return out


# ---------------------------------------------------------------- G2: gun-defined CP for S2, D, N2
def part2():
    state_lean = load("state_lean", SD / "code" / "state_lean.py")
    L, _ = state_lean.lean_table(); out = {}
    hs = HS[["congress", "chamber", "icpsr", "nominate_geo_mean_probability"]]
    for m in MODELS:
        o = {}; G = gun_rows(m); v = paper(m)
        g1 = json.loads((KIM / "05_gun_scale" / "out" / "g1" / f"g1_{m}.json").read_text())["gun"]
        rec = {k: float(1 - G[G.gun_cp == c].misplaced_gun.mean()) for k, c in [("aligned", 0), ("cp", 1)]}
        gate(f"G2-G1recall-{m}", close(dict(aligned=g1["aligned"], cp=g1["cp"]), rec, 1e-12))
        o["rows"] = dict(gun_rows=len(G), cells=int(G.cc.nunique()), senate_cells=int(G[G.chamber == "Senate"].cc.nunique()),
                         gun_cp_rows=int(G.gun_cp.sum()))
        # S2 (93-114)
        s2v, _ = s2_rows(m)
        sealed = json.loads((SD / "out" / "s2" / "s2.json").read_text())[m]
        # gate: S2a and S2b (CP rows) points and intervals as sealed (extended after the Codex verification)
        a = est.fe_ols(s2v, "p_z", ["cp"], "fe", "icpsr")["cp"]; s2v["misplaced"] = (s2v.map_q != s2v.vote_q).astype(float)
        b_ = est.fe_ols(s2v[s2v.cp == 1], "misplaced", ["p_z"], "fe", "icpsr")["p_z"]
        gate(f"G2-S2-{m}", close([sealed["S2a_p_on_cp"]["b"], *sealed["S2a_p_on_cp"]["ci95"], sealed["S2b_cp_rows"]["b"], *sealed["S2b_cp_rows"]["ci95"]],
                                 [a["b"], *a["ci95"], b_["b"], *b_["ci95"]]))
        G9 = G[G.congress.between(93, 114)]; S = with_paper(G9, s2v, ["p_z", "cp", "misplaced"])
        led = dict(gun_rows_93_114=len(G9), in_paper_rows_with_p=int(S.p_z.notna().sum()),
                   in_paper_rows=int(with_paper(G9, v, ["cp"]).cp.notna().sum()))
        S = S.dropna(subset=["p_z"]).copy(); S["gcp_x_p"] = S.gun_cp * S.p_z; S["cp_x_p"] = S.cp * S.p_z
        o["S2"] = dict(n_rows=len(S), ledger=led,
                       S2a_gun=fe(S, "p_z", ["gun_cp"], "gun_cp"), S2a_orig_same_rows=fe(S, "p_z", ["cp"], "cp"),
                       S2b_gun_cp_rows=fe(S[S.gun_cp == 1], "misplaced_gun", ["p_z"], "gun_cp"),
                       S2b_gun_aligned_rows=fe(S[S.gun_cp == 0], "misplaced_gun", ["p_z"]),
                       S2b_gun_interaction=fe(S, "misplaced_gun", ["gun_cp", "p_z", "gcp_x_p"], "gun_cp"),
                       S2b_orig_cp_rows_same_rows=fe(S[S.cp == 1], "misplaced", ["p_z"], "cp"),
                       S2b_orig_interaction_same_rows=fe(S, "misplaced", ["cp", "p_z", "cp_x_p"], "cp"))
        o["S2"]["reading_RS2_gun"] = bool(o["S2"]["S2b_gun_cp_rows"]["p_z"]["ci95"][0] > 0)
        # D (95-117): standardization and lean exactly as state_lean.rows
        dv, _ = state_lean.rows(m, L); dsd = json.loads((SD / "out" / "d" / "d.json").read_text())[m]
        chk = est.fe_ols(dv, "cp", ["out_lean_z"], "fe", "icpsr")["out_lean_z"]
        chk2 = est.fe_ols(dv, "misplaced", ["ccp"], "fe", "icpsr")["ccp"]
        gate(f"G2-D-{m}", close([dsd["D1"]["pooled"]["cp_on_out_lean"]["b"], *dsd["D1"]["pooled"]["cp_on_out_lean"]["ci95"],
                                 dsd["D3_map"]["pooled"]["misplaced_on_ccp"]["b"], *dsd["D3_map"]["pooled"]["misplaced_on_ccp"]["ci95"]],
                                [chk["b"], *chk["ci95"], chk2["b"], *chk2["ci95"]]))
        mu, sd = dv.out_lean.mean(), dv.out_lean.std()
        D = G[G.congress >= 95].copy(); D["election"] = D.congress.map(state_lean.election_for)
        D = D.merge(L.rename(columns={"year": "election", "state_po": "state"})[["election", "state", "lean"]], on=["election", "state"],
                    how="left", validate="many_to_one")
        miss = int(D.lean.isna().sum()); D = D.dropna(subset=["lean"]).copy()
        D["out_lean"] = np.where(D.party == "Democrat", -D.lean, D.lean); D["out_lean_z"] = (D.out_lean - mu) / sd; D["ccp"] = (D.out_lean > 0).astype(float)
        D = with_paper(D, dv.rename(columns={"misplaced": "misplaced_p", "cp": "cp_p"}), ["cp_p", "misplaced_p"])
        Dc = D[D.cp_p.notna()]                                   # rows with both definitions (Codex 2026-10-23: common-sample comparison)
        o["D"] = dict(n_rows=len(D), n_common=len(Dc), missing_lean=miss,
                      D1_gun=fe(D, "gun_cp", ["out_lean_z"]), D1_gun_common=fe(Dc, "gun_cp", ["out_lean_z"]),
                      D1_orig_same_rows=fe(D, "cp_p", ["out_lean_z"]),
                      D1_gun_ccp_share_by_gun_cp=D.groupby("gun_cp").ccp.mean().pipe(sk),
                      D3_map_gun=fe(D, "misplaced_gun", ["ccp"]), D3_map_gun_common=fe(Dc, "misplaced_gun", ["ccp"]),
                      D3_map_orig_same_rows=fe(D, "misplaced_p", ["ccp"]),
                      D3_gun_recall_by_ccp=(1 - D.groupby("ccp").misplaced_gun.mean()).pipe(sk))
        # N2: GMP standardized over the N2 sample (paper rows with GMP)
        nv = v.merge(hs, on=["congress", "chamber", "icpsr"], how="left", validate="one_to_one").dropna(subset=["nominate_geo_mean_probability"]).copy()
        gmu, gsd = nv.nominate_geo_mean_probability.mean(), nv.nominate_geo_mean_probability.std()
        nv["gmp_z"] = (nv.nominate_geo_mean_probability - gmu) / gsd
        n2 = json.loads((NOM / "out" / "n2.json").read_text())
        c1 = est.fe_ols(nv, "misplaced", ["cp"], "fe", "icpsr")["cp"]; c2 = est.fe_ols(nv, "misplaced", ["cp", "gmp_z"], "fe", "icpsr")["cp"]
        ok = close([n2[m]["misplacement"]["cp"]["b"], *n2[m]["misplacement"]["cp"]["ci95"], n2[m]["misplacement"]["cp_given_gmp"]["b"],
                    *n2[m]["misplacement"]["cp_given_gmp"]["ci95"]], [c1["b"], *c1["ci95"], c2["b"], *c2["ci95"]])
        if m == "qwen":
            c0 = est.fe_ols(nv, "nominate_geo_mean_probability", ["cp"], "fe", "icpsr")["cp"]
            ok = ok and close([n2["qwen"]["gmp_by_cp"]["cp_coef"]["b"], *n2["qwen"]["gmp_by_cp"]["cp_coef"]["ci95"]], [c0["b"], *c0["ci95"]])
        gate(f"G2-N2-{m}", ok)
        N = G.merge(hs, on=["congress", "chamber", "icpsr"], how="left", validate="one_to_one")
        nmiss = int(N.nominate_geo_mean_probability.isna().sum()); N = N.dropna(subset=["nominate_geo_mean_probability"]).copy()
        N["gmp_z"] = (N.nominate_geo_mean_probability - gmu) / gsd; N = with_paper(N, v, ["cp", "misplaced"])
        a1 = fe(N, "misplaced_gun", ["gun_cp"], "gun_cp"); a2 = fe(N, "misplaced_gun", ["gun_cp", "gmp_z"], "gun_cp")
        b1 = fe(N, "misplaced", ["cp"], "cp"); b2 = fe(N, "misplaced", ["cp", "gmp_z"], "cp")
        Nc = N[N.cp.notna()]
        c1g = fe(Nc, "misplaced_gun", ["gun_cp"], "gun_cp"); c2g = fe(Nc, "misplaced_gun", ["gun_cp", "gmp_z"], "gun_cp")
        o["N2"] = dict(n_rows=len(N), n_common=len(Nc), missing_gmp=nmiss,
                       gmp_on_gun_cp=fe(N, "nominate_geo_mean_probability", ["gun_cp"], "gun_cp"),
                       gmp_on_gun_cp_common=fe(Nc, "nominate_geo_mean_probability", ["gun_cp"], "gun_cp"),
                       misplaced_gun_common=c1g, misplaced_gun_given_gmp_common=c2g, remaining_share_gun_common=c2g["gun_cp"]["b"] / c1g["gun_cp"]["b"],
                       gmp_on_orig_cp_same_rows=fe(N, "nominate_geo_mean_probability", ["cp"], "cp"),
                       gmp_mean_by_gun_cp=N.groupby("gun_cp").nominate_geo_mean_probability.mean().pipe(sk),
                       misplaced_gun_on_gun_cp=a1, misplaced_gun_given_gmp=a2, remaining_share_gun=a2["gun_cp"]["b"] / a1["gun_cp"]["b"],
                       misplaced_orig_same_rows=b1, misplaced_orig_given_gmp_same_rows=b2, remaining_share_orig=b2["cp"]["b"] / b1["cp"]["b"])
        o["N2"]["reading_cp_fitted_worse_gun"] = bool(o["N2"]["gmp_on_gun_cp"]["gun_cp"]["ci95"][1] < 0)
        out[m] = o
        print("G2", m, "S2a gun", round(o["S2"]["S2a_gun"]["gun_cp"]["b"], 4), "| S2b gun CP rows", round(o["S2"]["S2b_gun_cp_rows"]["p_z"]["b"], 4),
              o["S2"]["S2b_gun_cp_rows"]["p_z"]["ci95"], "| D1 gun", round(o["D"]["D1_gun"]["out_lean_z"]["b"], 4), "| D3 gun",
              round(o["D"]["D3_map_gun"]["ccp"]["b"], 4), "| GMP gun", round(o["N2"]["gmp_on_gun_cp"]["gun_cp"]["b"], 4), flush=True)
    return out


# ---------------------------------------------------------------- G3: social-axis history (S1-y, N1-y)
def part3():
    s1 = load("speech_history", SD / "code" / "speech_history.py"); t0 = s1.load_t0()
    sealed = json.loads((SD / "out" / "s1" / "s1.json").read_text())
    ser = pd.read_csv(SD / "out" / "s1" / "series.csv"); sp = ser.pi.values; boot = np.load(SD / "out" / "s1" / "boot_speech.npy")
    gate("G3-speech", abs(s1.share(sp) - sealed["speech"]["share"]) < 1e-12)
    C = s1.CONG; a = lambda s, cs: s[..., [C.index(c) for c in cs]].mean(-1)
    out = dict(S1y={}, N1y={})
    for m in MODELS:
        # series exactly as speech_history.rollcall_model_series, plus y, dw2, np2 under the same member draws
        d, _ = t0.load(m)
        hs = HS[["congress", "chamber", "icpsr", "nokken_poole_dim1", "nokken_poole_dim2"]]
        d = d.merge(hs, on=["congress", "chamber", "icpsr"], how="left", validate="one_to_one")
        assert (d.nokken_poole_dim1.isna() == d.nokken_poole_dim2.isna()).all()           # PLAN_REVIEW 3
        d = d.dropna(subset=["nokken_poole_dim1"]).reset_index(drop=True); d["np1"], d["np2"] = d.nokken_poole_dim1, d.nokken_poole_dim2
        F = t0.Frame(d); cong = list(F.cong); idx = [cong.index(c) for c in C]
        gap = lambda var, w: (lambda pm: pm[:, 1] - pm[:, 0])(F.means(d[var].values, w))[idx]
        V = ["x", "dw1", "np1", "y", "dw2", "np2"]; pt = {k: gap(k, np.ones(len(d))) for k in V}
        rng = np.random.default_rng(dc.seed_for("S1-members", m) % 2**32); groups = {p: np.where(F.mparty == p)[0] for p in ["Democrat", "Republican"]}
        dr = {k: np.empty((s1.B, len(C))) for k in V}
        for b in range(s1.B):
            mw = np.zeros(len(F.mem))
            for p, ids in groups.items(): mw[ids] = np.bincount(rng.integers(0, len(ids), len(ids)), minlength=len(ids))
            rw = mw[F.mi]
            for k in V: dr[k][b] = gap(k, rw)
        # gate: x, dw1, np1 shares, intervals and comparisons equal the sealed S1
        S = {k: dict(share=float(s1.share(pt[k])), share_ci=s1.ci(s1.share(dr[k])), t50=s1.t50(pt[k])) for k in V}
        cmp = lambda mv, ref: dict(d=float(abs(s1.share(pt[mv]) - s1.share(sp)) - abs(s1.share(pt[mv]) - s1.share(pt[ref]))),
                                   d_ci=s1.ci(np.abs(s1.share(dr[mv]) - s1.share(boot)) - np.abs(s1.share(dr[mv]) - s1.share(dr[ref]))))
        gs = sealed[m]
        gate(f"G3-S1-{m}", all(close([gs["series"][k]["share"], *gs["series"][k]["share_ci"]], [S[k]["share"], *S[k]["share_ci"]], 1e-12)
                               for k in ["x", "dw1", "np1"]) and all(close([gs["comparison"][r]["d"], *gs["comparison"][r]["d_ci"]],
                                                                          [cmp("x", r)["d"], *cmp("x", r)["d_ci"]], 1e-12) for r in ["dw1", "np1"]))
        change = {k: dict(point=float(a(pt[k], s1.W1) - a(pt[k], s1.W0)), ci=s1.ci(a(dr[k], s1.W1) - a(dr[k], s1.W0))) for k in ["y", "dw2", "np2"]}
        interp = {k: not (change[k]["ci"][0] <= 0 <= change[k]["ci"][1]) for k in change}
        fd = lambda q: np.diff(q)
        out["S1y"][m] = dict(series={k: S[k] for k in ["y", "dw2", "np2"]}, change_W0_W1=change, share_interpretable=interp,
                             comparison={r: dict(cmp("y", r), closer_to_speech=bool(cmp("y", r)["d_ci"][1] < 0)) for r in ["dw2", "np2"]},
                             first_diff_corr={f"y~{b}": float(np.corrcoef(fd(pt["y"]), fd(q))[0, 1]) for b, q in [("speech", sp), ("dw2", pt["dw2"]), ("np2", pt["np2"])]},
                             gap_series={k: [float(z) for z in pt[k]] for k in ["y", "dw2", "np2"]}, label="descriptive (dim2 is not the abortion axis)")
        print("G3 S1y", m, {k: round(S[k]["share"], 3) for k in ["y", "dw2", "np2"]}, interp, flush=True)
    # N1-y: n1's decomposition functions and draws; gate on the sealed x / np1 readings
    n1 = load("nokken_poole", NOM / "code" / "nokken_poole.py"); n1s = json.loads((NOM / "out" / "n1.json").read_text())
    for m in MODELS:
        d = pd.read_csv(dc.OUT / m / "s3" / "temporal_member_scores.csv")
        hs = HS[["congress", "chamber", "icpsr", "nokken_poole_dim1", "nokken_poole_dim2"]]
        d = d[d.party.isin(["Democrat", "Republican"])].merge(hs, on=["congress", "chamber", "icpsr"], how="left", validate="one_to_one")
        d = d.dropna(subset=["nokken_poole_dim1"]).reset_index(drop=True); assert d.nokken_poole_dim2.notna().all()
        d["x"] = -d.econ_orth; d["x"] = d.x / d.x.std(ddof=0); d["np1"] = d.nokken_poole_dim1 / d.nokken_poole_dim1.std(ddof=0)
        d["y"] = -d.social_orth; d["y"] = d.y / d.y.std(ddof=0); d["np2"] = d.nokken_poole_dim2 / d.nokken_poole_dim2.std(ddof=0)
        mem = d.party + "|" + d.icpsr.astype(str); ids = np.unique(mem.values)
        party_of = np.array([s.split("|")[0] for s in ids]); groups = {p: np.where(party_of == p)[0] for p in ["Democrat", "Republican"]}
        rng = np.random.default_rng(dc.seed_for("N1", m) % 2**32); draws_w = []
        for _ in range(n1.B):
            w = np.zeros(len(ids))
            for p, g in groups.items(): w[g] = np.bincount(rng.integers(0, len(g), len(g)), minlength=len(g))
            draws_w.append(w)
        pos = {s: i for i, s in enumerate(ids)}; res = {}
        for var in ["x", "np1", "y", "np2"]:
            z, pr = n1.prep(d, var); zi = (z.party + "|" + z.icpsr.astype(str)).map(pos).values; pi = (pr.party + "|" + pr.icpsr.astype(str)).map(pos).values
            ix = n1.index(z, pr)
            for sn, spn in n1.SPANS.items():
                pt = n1.decompose_fast(ix, np.ones(len(z)), np.ones(len(pr)), spn)
                assert n1.same(pt, n1.decompose(z, pr, np.ones(len(z)), np.ones(len(pr)), spn))
                bs = [n1.decompose_fast(ix, w[zi], w[pi], spn) for w in draws_w]
                res.setdefault(sn, {})[var] = dict(point=pt, draws={p: np.array([b[p]["within"] for b in bs]) for p in pt})
        ci = lambda q: [float(np.percentile(q, 2.5)), float(np.percentile(q, 97.5))]
        rd = lambda S, mv, rv, p: dict(model_within=S[mv]["point"][p]["within"], model_within_ci=ci(S[mv]["draws"][p]), np_within=S[rv]["point"][p]["within"],
                                       np_within_ci=ci(S[rv]["draws"][p]), diff=S[mv]["point"][p]["within"] - S[rv]["point"][p]["within"],
                                       diff_ci=ci(S[mv]["draws"][p] - S[rv]["draws"][p]))
        ok = all(close({k: n1s[m]["spans"][sn]["reading"][p][k] for k in ["model_within", "model_within_ci", "np_within", "np_within_ci", "diff", "diff_ci"]},
                       rd(res[sn], "x", "np1", p), 1e-12) for sn in n1.SPANS for p in ["Democrat", "Republican"])
        gate(f"G3-N1-{m}", ok)
        o = {}
        for sn in n1.SPANS:
            o[sn] = {}
            for p in ["Democrat", "Republican"]:
                r = rd(res[sn], "y", "np2", p); r["drift_specific_to_model"] = bool(r["model_within_ci"][1] < 0 and r["diff_ci"][1] < 0)
                r["model_total"] = res[sn]["y"]["point"][p]["total"]; r["np_total"] = res[sn]["np2"]["point"][p]["total"]
                r["model_replacement"] = res[sn]["y"]["point"][p]["replacement"]; r["np_replacement"] = res[sn]["np2"]["point"][p]["replacement"]
                o[sn][p] = r
        out["N1y"][m] = dict(o, label="descriptive application of the N1 rule (NP dim2 is not the abortion axis)")
        print("G3 N1y", m, {sn: {p[0]: (round(o[sn][p]["model_within"], 3), round(o[sn][p]["np_within"], 3)) for p in o[sn]} for sn in o}, flush=True)
    return out


# ---------------------------------------------------------------- G4: L1 on gun votes
def part4():
    ww = load("error_warning", EW / "code" / "error_warning.py"); out = {}
    for m in MODELS:
        sealed = json.loads((EW / "out" / f"w1_warning_{m}.json").read_text())["by_issue"]
        d = ww.frame(m)
        l1 = lambda h, mis: dict(accuracy=v5.twoway(h.assign(y=h.correct_avg, cp=h[mis])), entropy=v5.twoway(h.assign(y=h.H, cp=h[mis])),
                                 misplaced_share=float(h[mis].mean()), members=int(h.icpsr.nunique()))
        for iss, g in d.groupby("issue"):
            g = g.reset_index(drop=True)
            for grp, h in [("cp", g[g.cp == 1]), ("aligned", g[g.cp == 0])]:
                r = l1(h, "misplaced"); s = sealed[iss]["L1"][grp]
                gate(f"G4-{m}-{iss}-{grp}", close([s["accuracy"]["b"], *s["accuracy"]["ci95"], s["entropy"]["b"], *s["entropy"]["ci95"]],
                                                  [r["accuracy"]["b"], *r["accuracy"]["ci95"], r["entropy"]["b"], *r["entropy"]["ci95"]], 1e-12))
        f = pd.read_parquet(KIM / "06_vote_prediction" / "out" / "g2" / f"frame_{m}.parquet")
        H = (ww.hb(f.share_yf) + ww.hb(f.share_nf)) / 2; assert np.allclose(H, f.H, atol=1e-12)
        rows = paper(m); n0 = len(f)
        f = f.merge(rows[["congress", "chamber", "icpsr", "map_q"]], on=["congress", "chamber", "icpsr"], how="left", validate="many_to_one")
        assert len(f) == n0 and f.map_q.notna().all(); f["misplaced"] = (f.map_q != f.vote_q).astype(float)
        G = gun_rows(m)[["congress", "chamber", "icpsr", "misplaced_gun"]]
        f = f.merge(G, on=["congress", "chamber", "icpsr"], how="left", validate="many_to_one")
        fg = f[f.gun_cp_loo.notna() & f.misplaced_gun.notna()]
        out[m] = dict(interpreted=(m == "llama"), n=len(f),
                      abortion_cp_def={grp: l1(h, "misplaced") for grp, h in [("cp", f[f.cp == 1]), ("aligned", f[f.cp == 0])]},
                      gun_cp_def={grp: l1(h, "misplaced_gun") for grp, h in [("cp", fg[fg.gun_cp_loo == 1]), ("aligned", fg[fg.gun_cp_loo == 0])]},
                      n_gun_cp_def=len(fg))
        print("G4", m, {k: {g: (round(x["accuracy"]["b"], 4), [round(z, 4) for z in x["accuracy"]["ci95"]]) for g, x in out[m][k].items()}
                        for k in ["abortion_cp_def", "gun_cp_def"]}, flush=True)
    return out


def synthetic():
    """(a) planted gun-CP effect through fe() on the real gun rows; (b) growth share and the denominator rule"""
    rng = np.random.default_rng(23); G = gun_rows("qwen"); res = {}
    for eff in [-0.1, 0.0]:
        G["yy"] = eff * G.gun_cp + G.groupby("fe").congress.transform(lambda s: rng.normal(0, .2)) + rng.normal(0, .3, len(G))
        res[str(eff)] = fe(G, "yy", ["gun_cp"])["gun_cp"]["b"]
    s1 = load("speech_history", SD / "code" / "speech_history.py"); C = s1.CONG
    lin = np.array([0.0 if c <= 85 else (c - 85) / 29 for c in C])                 # steady rise from 85 to 114: share = mean(93-102 rise)
    expect = np.mean([(c - 85) / 29 for c in s1.MID]) / np.mean([(c - 85) / 29 for c in s1.W1])
    res["share_linear"] = float(s1.share(lin)); res["share_expected"] = float(expect)
    flat = rng.normal(0, 0.05, (200, len(C)))                                         # no change: the W1-W0 interval must include 0
    a = lambda s, cs: s[..., [C.index(c) for c in cs]].mean(-1); ch = s1.ci(a(flat, s1.W1) - a(flat, s1.W0))
    res["flat_change_ci"] = ch
    res["pass"] = bool(abs(res["-0.1"] + 0.1) < 0.03 and abs(res["0.0"]) < 0.03 and abs(res["share_linear"] - expect) < 1e-12 and ch[0] <= 0 <= ch[1])
    dc.atomic_json(res, O / "synthetic.json"); print(res)
    if not res["pass"]: raise SystemExit("STOP: synthetic failed")


def main():
    res = dict(G1_S2c=part1(), G2_gun_cp=part2(), G3_social_axis=part3(), G4_L1_guns=part4())
    dc.atomic_json(json.loads(json.dumps(res, default=lambda z: float(z) if np.isscalar(z) else str(z))), O / "gf.json")
    print("GF DONE", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--synthetic", action="store_true"); a = ap.parse_args()
    synthetic() if a.synthetic else main()
