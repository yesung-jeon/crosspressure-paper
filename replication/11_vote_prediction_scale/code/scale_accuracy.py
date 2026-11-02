#!/usr/bin/env python
"""Vote-prediction accuracy read from the 9-point scale answers.
CPU only; reads sealed stage 06 and stage 17 outputs; writes only ../out/.
  python scale_accuracy.py --checks   # mapping known answers + synthetic recovery
  python scale_accuracy.py            # joins, baseline gates, estimates -> ../out/results.csv, descriptive.json"""
import argparse, json, sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import norm

H = Path(__file__).resolve().parents[1]; O = H / "out"; O.mkdir(exist_ok=True)
REP = Path(__file__).resolve().parents[2]; V = REP / "10_vote_prediction"; S17 = REP / "16_scale_uncertainty" / "out" / "votes"
sys.path.insert(0, str(V / "code")); sys.path.insert(0, str(REP / "05_directions_and_map" / "code"))
_argv = sys.argv; sys.argv = ["estimate_votes.py"]
import estimate_votes as v5  # noqa: E402  (twoway: the Section 6 estimator)
import map_common as dc  # noqa: E402  (seed_for)
sys.argv = _argv
MODELS = ["qwen", "llama"]; REPS = 1000


def to_s(P, order):
    """P: (n, 9) digit probabilities; order 'asc' (1 = NAY, 9 = YEA) or 'desc'. Returns mass and YEA lean s on 0-1."""
    mass = P.sum(1); Q = P / mass[:, None]; E = (Q * np.arange(1, 10)).sum(1); up = (E - 1) / 8
    return mass, np.where(np.asarray(order) == "asc", up, 1 - up)


def scale_votes(m):
    D = S17 / m; assert (D / "run.json").exists()
    fs = sorted(D.glob("part_*.done"))
    df = pd.concat([pd.read_parquet(f.with_suffix(".parquet")) for f in fs], ignore_index=True)
    assert not df.duplicated(["pid", "order"]).any()
    assert set(df.order.unique()) == {"asc", "desc"}, df.order.unique()                       # both directions,
    assert df.groupby("pid").order.nunique().eq(2).all(), "a pid lacks one scale direction"   # every pid
    mass, s = to_s(df[[f"p{k}" for k in range(1, 10)]].values, df.order.values)
    df = df.assign(mass=mass, s=s)
    w = df.pivot(index="pid", columns="order", values=["s", "mass"])
    w.columns = [f"{a}_{b}" for a, b in w.columns]
    return w.reset_index(), len(df)


def frames(m):
    a = pd.read_parquet(V / "out" / "v5" / f"frame_v2_{m}_abortion_economic.parquet")
    g = pd.read_parquet(V / "out" / "g2" / f"frame_{m}.parquet")
    lab = pd.read_parquet(V / "out" / "v6" / "loo_labels.parquet")
    a = a.merge(lab, on=["key", "icpsr"], how="left", validate="many_to_one")
    cols = ["pid", "key", "icpsr", "party", "issue", "cp", "fe", "actual", "party_yea_share", "party_tie", "format_fail",
            "share_yf", "share_nf", "pred_yf", "pred_avg", "correct_yf", "correct_avg", "party_correct"]
    return a[cols + ["cp_loo"]], g[cols + ["gun_cp_loo"]]


def est(d, y, x="cp"):
    t = v5.twoway(d.assign(y=d[y], cp=d[x]))
    return dict(b=t["b"], se=t["se"], lo95=t["ci95"][0], hi95=t["ci95"][1], p=float(2 * norm.sf(abs(t["b"] / t["se"]))), n=t["n"])


def add_scale(d, w):
    d = d.merge(w, on="pid", how="left", validate="one_to_one")
    d["scale_missing"] = d.s_asc.isna() | d.s_desc.isna()
    d["scale_fail"] = ~d.scale_missing & ((d.mass_asc < 0.5) | (d.mass_desc < 0.5))
    d["s_yea"] = (d.s_asc + d.s_desc) / 2
    for c, s in (("scale", "s_yea"), ("asc", "s_asc"), ("desc", "s_desc")):
        d[f"pred_{c}"] = (d[s] > 0.5).astype(int); d[f"correct_{c}"] = (d[f"pred_{c}"] == d.actual).astype(float)
    d["d_yf"] = d.correct_scale - d.correct_yf; d["d_avg"] = d.correct_scale - d.correct_avg
    return d


def share_toward(g, pred, corr):
    w = g[g[corr] == 0]; return float((w[pred] == w.maj).mean()) if len(w) else np.nan, len(w)


def boot_toward(g, pred, corr, rng):
    """member-cluster bootstrap within party (as 09_error_direction.py within CP x party; here g is one CP group)"""
    g = g.reset_index(drop=True); strata = {}
    for (p, i), idx in g.groupby(["party", "icpsr"]).indices.items(): strata.setdefault(p, []).append(idx)
    out = []
    for _ in range(REPS):
        idx = np.concatenate([np.concatenate([v[j] for j in rng.integers(0, len(v), len(v))]) for v in strata.values()])
        out.append(share_toward(g.iloc[idx], pred, corr)[0])
    return [float(np.nanpercentile(out, 2.5)), float(np.nanpercentile(out, 97.5))]


def majority(d, n_party):
    """M1: party_yea_share (ties out); M2: leave-self-out integer counts (as 09_error_direction.py)"""
    d = d.merge(n_party, on=["key", "party"], how="left", validate="many_to_one"); assert d.n_party.notna().all()
    yo, no = d.yea_party - d.actual, d.n_party - 1
    m1 = d[d.party_yea_share.notna() & (d.party_yea_share != 0.5)].assign(maj=lambda x: (x.party_yea_share > 0.5).astype(int))
    k2 = (no > 0) & (2 * yo != no); m2 = d[k2].assign(maj=(2 * yo > no)[k2].astype(int))
    return {"M1": m1, "M2": m2}


def gates(m, a, g):
    """Section 6 reproduction on the full binary frames (before the scale filter)."""
    E = json.load(open(V / "out" / "v5" / f"estimates_v2_{m}_abortion_economic.json"))
    C = json.load(open(V / "out" / "v5" / f"competence_party_v2_{m}.json"))
    L = json.load(open(V / "out" / "v6" / f"loo_cp_{m}.json"))
    G = json.load(open(V / "out" / "g2" / f"estimates_{m}.json"))
    R = json.load(open(V / "out" / "v6" / f"error_direction_{m}.json"))
    chk = []
    a0 = a[~a.format_fail]
    for i in ("abortion", "economic"):
        s = a0[a0.issue == i]
        chk.append((f"{i} 6.1", v5.twoway(s.assign(y=s.correct_avg))["b"],
                    E["by_issue"][i]["regressions"]["accuracy (6.1 preferred)" if i == "abortion" else "accuracy"]["b"]))
        for p, h in s.groupby("party"):
            chk.append((f"{i} {p}", v5.twoway(h.assign(y=h.correct_avg, fe=h.key))["b"], C[i][p]["cp_coef"]["b"]))
        sl = s[s.cp_loo.notna()]
        chk.append((f"{i} LOO", v5.twoway(sl.assign(cp=sl.cp_loo, y=sl.correct_avg))["b"], L["by_issue"][i]["loo_6_1"]["b"]))
    g0 = g[~g.format_fail]
    chk.append(("guns abortion-CP", v5.twoway(g0.assign(y=g0.correct_avg))["b"], G["regressions_abortion_cp"]["accuracy (6.1)"]["b"]))
    gl = g0[g0.gun_cp_loo.notna()]
    chk.append(("guns gun-CP", v5.twoway(gl.assign(cp=gl.gun_cp_loo, y=gl.correct_avg))["b"], G["gun_cp_loo"]["accuracy"]["b"]))
    out = [dict(model=m, check=c, reproduced=r, sealed=s, abs_diff=abs(r - s)) for c, r, s in chk]
    return out, R


def run():
    mv = pd.read_csv(V / "out" / "v0" / "member_votes.csv.gz", usecols=["congress", "chamber", "rollnumber", "icpsr", "party", "actual"])
    mv["key"] = mv.congress.astype(str) + "|" + mv.chamber + "|" + mv.rollnumber.astype(str)
    n_party = mv.groupby(["key", "party"]).agg(n_party=("actual", "size"), yea_party=("actual", "sum")).reset_index()
    rows, desc, gate_rows = [], {}, []

    def put(m, issue, cp_def, qty, r, sub=None, note=""):
        rows.append(dict(model=m, issue=issue, cp_def=cp_def, quantity=qty, note=note, **r))

    for m in MODELS:
        w, n_cells = scale_votes(m); a, g = frames(m)
        gr, R = gates(m, a, g); gate_rows += gr
        dm = {"scale_cells": n_cells}
        # join gate: key identity
        allpid = set(a.pid) | set(g.pid); sp = set(w.pid)
        dm["join"] = dict(section6_pids=len(allpid), scale_pids=len(sp), missing_in_scale=len(allpid - sp), scale_only=len(sp - allpid),
                          pid_overlap_abortion_economic_vs_guns=len(set(a.pid) & set(g.pid)))
        if dm["join"]["missing_in_scale"] or dm["join"]["scale_only"]:                    # PROTOCOL join gate is a STOP
            raise SystemExit(f"STOP: join gate {m}: {dm['join']}")
        A = add_scale(a[~a.format_fail].copy(), w); Gd = add_scale(g[~g.format_fail].copy(), w)
        for nm, d in (("abortion_economic", A), ("guns", Gd)):
            dm[f"dropped_{nm}"] = dict(binary_format_fail_rows_already_out=int(((a if nm != "guns" else g).format_fail).sum()),
                                       scale_missing=int(d.scale_missing.sum()), scale_fail=int(d.scale_fail.sum()),
                                       exact_ties_s_yea=int((~d.scale_missing & (d.s_yea == 0.5)).sum()))
        A = A[~A.scale_missing & ~A.scale_fail]; Gd = Gd[~Gd.scale_missing & ~Gd.scale_fail]
        sets = [(i, A[A.issue == i], "cp", "vote CP") for i in ("abortion", "economic")]
        sets += [("guns", Gd, "cp", "abortion CP"), ("guns", Gd[Gd.gun_cp_loo.notna()], "gun_cp_loo", "gun CP (LOO)")]
        note = lambda i: "Qwen not competent on guns: not interpreted" if (m == "qwen" and i == "guns") else ""
        for i, d, x, lab in sets:
            for qty in ("correct_scale", "correct_yf", "correct_avg", "d_yf", "d_avg", "correct_asc", "correct_desc"):
                put(m, i, lab, qty, est(d, qty, x), note=note(i))
            by = d.groupby(x)
            dm[f"{i} | {lab}"] = dict(n=by.size().to_dict(), acc_scale=by.correct_scale.mean().round(4).to_dict(),
                                      acc_yf=by.correct_yf.mean().round(4).to_dict(), acc_avg=by.correct_avg.mean().round(4).to_dict(),
                                      pred_yea_scale=by.pred_scale.mean().round(4).to_dict(), pred_yea_avg=by.pred_avg.mean().round(4).to_dict(),
                                      corr_scale_directions=float(np.corrcoef(d.s_asc, d.s_desc)[0, 1]),
                                      corr_binary_orders=float(np.corrcoef(d.share_yf, d.share_nf)[0, 1]),
                                      agree_pred_scale_vs_avg=float((d.pred_scale == d.pred_avg).mean()))
        # Q4 party split, abortion: within party, roll-call FE
        ab = A[A.issue == "abortion"]
        for p, h in ab.groupby("party"):
            h = h.assign(fe=h.key)
            for qty in ("correct_scale", "correct_avg", "d_yf"):
                put(m, "abortion", f"vote CP, {p} only", qty, est(h, qty))
        # Q6 leave-one-out CP, abortion and economic
        for i in ("abortion", "economic"):
            d = A[(A.issue == i) & A.cp_loo.notna()]
            for qty in ("correct_scale", "correct_avg"):
                put(m, i, "vote CP (LOO)", qty, est(d, qty, "cp_loo"))
        # Q5 error direction, abortion, CP members
        ed = {}
        for mdef, e in majority(ab, n_party).items():
            for cp, h in e.groupby("cp"):
                for pred, corr in (("pred_scale", "correct_scale"), ("pred_avg", "correct_avg")):
                    sh, nw = share_toward(h, pred, corr)
                    rng = np.random.default_rng(dc.seed_for("scale_acc", m, mdef, pred, int(cp)) % 2**32)
                    ed[f"{mdef}|cp={cp}|{pred}"] = dict(n_wrong=nw, toward_party=sh, ci95=boot_toward(h, pred, corr, rng))
        ed["sealed_M1_cp1_pred_avg_full_rows"] = R["results"]["M1|abortion|pred_avg"]["cp=1"]["toward_party_among_wrong"]
        dm["error_direction_abortion"] = ed
        desc[m] = dm; print(m, json.dumps(dm["join"]), flush=True)

    G = pd.DataFrame(gate_rows); G.to_csv(O / "baseline_gates.csv", index=False)
    if not (G.abs_diff < 1e-10).all():
        print(G.to_string()); raise SystemExit("STOP: Section 6 baseline not reproduced")
    T = pd.DataFrame(rows); T["p_holm"] = np.nan; T["reading"] = ""
    prim = (T.issue == "abortion") & (T.cp_def == "vote CP") & T.quantity.isin(["correct_scale", "d_yf"])
    for m, h in T[prim].groupby("model"):
        p = h.p.values; o = np.argsort(p); adj = np.empty(len(p)); run_ = 0
        for k, ix in enumerate(o): run_ = max(run_, min(1, (len(p) - k) * p[ix])); adj[ix] = run_
        T.loc[h.index, "p_holm"] = adj
    for ix in T[prim].index:
        r = T.loc[ix]; directional = (r.lo95 > 0 or r.hi95 < 0) and r.p_holm < 0.05
        if r.quantity == "correct_scale":
            T.loc[ix, "reading"] = ("CP less accurate" if r.b < 0 else "CP more accurate") if directional else "no difference detected"
        else:
            T.loc[ix, "reading"] = (("scale gap larger" if r.b < 0 else "scale gap smaller") if directional
                                    else "no difference detected (format does not change the gap)")
    T.to_csv(O / "results.csv", index=False)
    json.dump(desc, open(O / "descriptive.json", "w"), indent=1, default=float)
    show = T[T.quantity.isin(["correct_scale", "correct_yf", "correct_avg", "d_yf"])]
    print(show[["model", "issue", "cp_def", "quantity", "n", "b", "lo95", "hi95", "p_holm", "reading"]].round(4).to_string())


def checks():
    out = {}
    P = np.zeros((3, 9)); P[0, 8] = 1; P[1, 4] = 1; P[2, 0] = 1
    _, sa = to_s(P, ["asc"] * 3); _, sd = to_s(P, ["desc"] * 3)
    out["mapping"] = dict(asc=sa.tolist(), desc=sd.tolist(), ok=bool(np.allclose(sa, [1, .5, 0]) and np.allclose(sd, [0, .5, 1])))
    a, _ = frames("llama"); d = a[(a.issue == "abortion") & ~a.format_fail].copy(); rng = np.random.default_rng(20261101)
    res = {}
    for eff in (-0.10, 0.0):
        d["y"] = (rng.random(len(d)) < 0.6 + eff * d.cp).astype(float); r = est(d, "y")
        res[str(eff)] = dict(b=r["b"], lo95=r["lo95"], hi95=r["hi95"], covered=bool(r["lo95"] <= eff <= r["hi95"]))
    out["synthetic_real_structure"] = res
    out["pass"] = out["mapping"]["ok"] and all(v["covered"] for v in res.values())
    json.dump(out, open(O / "checks.json", "w"), indent=1); print(json.dumps(out, indent=1))
    if not out["pass"]: raise SystemExit("STOP: checks failed")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--checks", action="store_true")
    checks() if ap.parse_args().checks else run()
