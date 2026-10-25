#!/usr/bin/env python
"""PROTOCOL.md sections W and L1 (rebuild 2026-10-23: the W1 rows of E, the subgroup grid, are excluded by the author; grid() stays
because g2_estimate imports the module, but it is no longer called here). Qwen and Llama; this run's W1 frames.
  python error_warning.py --synthetic   # AUROC and interaction estimator checks
  python error_warning.py               # full run -> out/w1_warning_<m>.json
"""
import argparse, json, sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import rankdata

R = Path(__file__).resolve().parents[1]; KIM = R.parent        # replication/ (was kim/ two levels up from review/<folder>)
V = KIM / "06_vote_prediction"
sys.path.insert(0, str(V / "code")); sys.path.insert(0, str(KIM / "09_named_member_entropy" / "code"))
import estimate_votes as v5  # noqa: E402  (twoway: W1 estimator; also puts STUDY_D code on the path)
import map_common as dc  # noqa: E402
import named_common as nc  # noqa: E402

MODELS = ["qwen", "llama"]
O = R / "out"; O.mkdir(parents=True, exist_ok=True)
REPS = 1000
SOUTH = {"AL", "AR", "FL", "GA", "LA", "MS", "NC", "SC", "TN", "TX", "VA"}
ALIGNED = ["EL-SP", "ER-ST"]


def hb(p):
    p = np.clip(p, 1e-12, 1 - 1e-12); return -(p * np.log2(p) + (1 - p) * np.log2(1 - p))


def auc(score, pos):
    pos = np.asarray(pos, bool); n1 = pos.sum(); n0 = len(pos) - n1
    if n1 == 0 or n0 == 0: return np.nan, 0
    r = rankdata(score); return (r[pos].sum() - n1 * (n1 + 1) / 2) / (n1 * n0), n1 * n0


def auc_within(g):
    num = den = 0.0
    for _, h in g.groupby("key"):
        a, w = auc(h.H.values, h.err.values)
        if w: num += a * w; den += w
    return num / den if den else np.nan


def metrics(g):
    a, _ = auc(g.H.values, g.err.values)
    wrong = g[g.err == 1]
    return dict(auroc_pooled=a, auroc_within=auc_within(g), conf_err_share_of_conf=float(g[g.H < 0.2].err.mean()) if (g.H < 0.2).any() else np.nan,
                conf_share_of_wrong=float((wrong.H < 0.2).mean()) if len(wrong) else np.nan, n=len(g), n_wrong=len(wrong))


def calib(g):
    c = np.maximum(g.share_avg, 1 - g.share_avg); b = np.minimum(((c - 0.5) / 0.05).astype(int), 9)
    t = pd.DataFrame(dict(b=b, c=c, ok=1 - g.err)).groupby("b").agg(n=("ok", "size"), acc=("ok", "mean"), conf=("c", "mean"))
    ece = float((t.n * (t.acc - t.conf).abs()).sum() / t.n.sum())
    s = g.sort_values("H"); sel = {f"q{q}": float(s.err.iloc[: max(1, int(len(s) * q / 100))].mean()) for q in range(10, 101, 10)}
    return dict(bins=t.reset_index().to_dict("records"), ece=ece, selective_error=sel)


def boot_diff(d, rng):
    """CP - aligned differences of the W metrics; members resampled within party, each member drawn once with all of its rows (CP and
    aligned Congresses together). Codex verification 2026-10-22: the first version resampled within CP x party, which split members
    whose CP status changes across Congresses (744 of 2,146 on abortion) into two independent clusters."""
    strata = {}
    for (p, i), idx in d.groupby(["party", "icpsr"]).indices.items(): strata.setdefault(p, []).append(idx)
    keys = list(strata); out = []
    for _ in range(REPS):
        idx = np.concatenate([np.concatenate([strata[s][j] for j in rng.integers(0, len(strata[s]), len(strata[s]))]) for s in keys])
        b = d.iloc[idx]; m1, m0 = metrics(b[b.cp == 1]), metrics(b[b.cp == 0])
        out.append({k: m1[k] - m0[k] for k in ["auroc_pooled", "auroc_within", "conf_err_share_of_conf", "conf_share_of_wrong"]})
    o = pd.DataFrame(out)
    return {k: [float(np.nanpercentile(o[k], 2.5)), float(np.nanpercentile(o[k], 97.5))] for k in o}


def interaction(d, y, g):
    """FWL: coefficient on cp x g with cp and party x roll-call FE partialled out; two-way clustered (v5.twoway on residuals)"""
    e = d[[y, "cp", "fe", "icpsr", "key"]].copy(); e["x2"] = d.cp * g
    dm = lambda s: s - e.groupby("fe")[s.name].transform("mean")
    yt, x1, x2 = dm(e[y]), dm(e.cp), dm(e.x2)
    r2 = x2 - x1 * (x1 @ x2) / (x1 @ x1); ry = yt - x1 * (x1 @ yt) / (x1 @ x1)
    return v5.twoway(e.assign(ry=ry, r2=r2), y="ry", x="r2")


def frame(m):
    d = pd.read_parquet(V / "out" / "v5" / f"frame_v2_{m}_abortion_economic.parquet")
    if d.format_fail.any():                           # protocol: format failures as in W1 (Codex review round 2: auc() read NaN err as an
        d = d[~d.format_fail].reset_index(drop=True)  # error). Skipped when there are none: the copy alone moves the last float bits
    d["H"] = (hb(d.share_yf) + hb(d.share_nf)) / 2; d["err"] = 1 - d.correct_avg
    mv = pd.read_csv(V / "out" / "v0" / "member_votes.csv.gz", usecols=["congress", "chamber", "rollnumber", "icpsr", "vote_q", "state"])
    mv["key"] = mv.congress.astype(str) + "|" + mv.chamber + "|" + mv.rollnumber.astype(str)
    n0 = len(d); d = d.merge(mv[["key", "icpsr", "vote_q", "state", "congress", "chamber"]], on=["key", "icpsr"], how="left", validate="one_to_one")
    assert len(d) == n0 and d.vote_q.notna().all()
    rc = pd.read_csv(V / "out" / "v0" / "rollcalls.csv")
    rc["key"] = rc.congress.astype(str) + "|" + rc.chamber + "|" + rc.rollnumber.astype(str)
    t = (rc.vote_desc.fillna("") + " " + rc.vote_question.fillna("") + " " + rc.dtl_desc.fillna("")).str.upper()
    rc["amend"] = t.str.contains("AMEND") & ~t.str.contains("PASS")
    d = d.merge(rc[["key", "amend"]], on="key", how="left", validate="many_to_one")
    rows = nc.analysis_rows(dc.OUT / m / "s3" / "temporal_member_scores.csv")
    d = d.merge(rows[["congress", "chamber", "icpsr", "map_q"]], on=["congress", "chamber", "icpsr"], how="left", validate="many_to_one")
    assert len(d) == n0 and d.map_q.notna().all(), d.map_q.isna().sum()
    d["misplaced"] = (d.map_q != d.vote_q).astype(float)
    d["era"] = pd.cut(d.congress, [92, 100, 108, 117], labels=["93-100", "101-108", "109-117"]).astype(str)
    return d


def grid(d, m, iss):
    rows = []
    def add(axis, cell, sub, n_members_min=30):
        n_mem = sub[sub.cp == 1].icpsr.nunique(), sub[sub.cp == 0].icpsr.nunique()
        r = dict(model=m, issue=iss, axis=axis, cell=cell, n=len(sub), n_members_cp=n_mem[0], n_members_aligned=n_mem[1])
        if min(n_mem) >= n_members_min and sub.cp.nunique() == 2:
            t = v5.twoway(sub.assign(y=sub.H)); r.update(b=t["b"], lo95=t["ci95"][0], hi95=t["ci95"][1], lo90=t["ci90"][0], hi90=t["ci90"][1],
                                                       p=float(2 * (1 - __import__("scipy").stats.norm.cdf(abs(t["b"] / t["se"])))))
        rows.append(r)
    for p in ["Democrat", "Republican"]:
        for q in ["EL-ST", "ER-SP"]:
            add("party x CP type", f"{p}|{q}", d[(d.party == p) & d.vote_q.isin(ALIGNED + [q])])
    for c in ["House", "Senate"]: add("chamber", c, d[d.chamber == c])
    for e in ["93-100", "101-108", "109-117"]: add("era", e, d[d.era == e])
    add("recognized", "known", d[d.known.astype(bool)])
    dem = d[d.party == "Democrat"]
    add("South (Democrats)", "South", dem[dem.state.isin(SOUTH)]); add("South (Democrats)", "non-South", dem[~dem.state.isin(SOUTH)])
    add("motion", "amendment", d[d.amend]); add("motion", "other content", d[~d.amend])
    add("correctness (descriptive)", "right", d[d.err == 0]); add("correctness (descriptive)", "wrong", d[d.err == 1])
    g = pd.DataFrame(rows)
    for ax, h in g.groupby("axis"):
        p = h.p.fillna(1.0).values; o = np.argsort(p); adj = np.empty(len(p)); run = 0
        for k, i in enumerate(o): run = max(run, min(1, (len(p) - k) * p[i])); adj[i] = run
        g.loc[h.index, "p_holm"] = adj
    def verdict(r):
        if pd.isna(r.get("b")): return "below minimum size"
        if r.axis.startswith("correctness"): return "descriptive"
        # Holm applied (Codex verification 2026-10-22: p_holm was computed but not used); equivalence uses the 90% interval as before
        if (r.lo95 > 0 or r.hi95 < 0) and abs(r.b) >= 0.05 and r.p_holm < 0.05: return "more uncertain" if r.b > 0 else "less uncertain"
        if r.lo90 >= -0.05 and r.hi90 <= 0.05: return "no meaningful difference"
        return "undetermined"
    g["verdict"] = g.apply(verdict, axis=1)
    return g


def run(m):
    d = frame(m); res = dict(model=m, by_issue={})
    gr = []
    for iss, g in d.groupby("issue"):
        g = g.reset_index(drop=True)
        rng = np.random.default_rng(dc.seed_for("EW", m, iss) % 2**32)
        m1, m0 = metrics(g[g.cp == 1]), metrics(g[g.cp == 0])
        ci = boot_diff(g, rng)
        diff = {k: m1[k] - m0[k] for k in ci}
        rd = dict(cp=m1, aligned=m0, diff=diff, diff_ci95=ci, calib_cp=calib(g[g.cp == 1]), calib_aligned=calib(g[g.cp == 0]))
        rd["reading_warns_less_for_cp"] = bool(ci["auroc_within"][1] < 0 or ci["conf_share_of_wrong"][0] > 0)
        # L1: same-member link
        rd["L1"] = {grp: dict(accuracy=v5.twoway(h.assign(y=h.correct_avg, cp=h.misplaced)), entropy=v5.twoway(h.assign(y=h.H, cp=h.misplaced)),
                              misplaced_share=float(h.misplaced.mean()))
                    for grp, h in [("cp", g[g.cp == 1]), ("aligned", g[g.cp == 0])]}
        # accuracy-entropy contrast for party and era (A8)
        rd["contrast"] = {}
        for ax, gv in [("party=Republican", (g.party == "Republican").astype(float)),
                       ("era=93-100", (g.era == "93-100").astype(float)), ("era=109-117", (g.era == "109-117").astype(float))]:
            rd["contrast"][ax] = dict(accuracy=interaction(g.assign(y=g.correct_avg), "y", gv), entropy=interaction(g.assign(y=g.H), "y", gv))
        res["by_issue"][iss] = rd                                  # rebuild: grid(g, m, iss) not called (E grid excluded; no RNG)
        print(m, iss, "AUROC within cp/aligned", round(m1["auroc_within"], 3), round(m0["auroc_within"], 3), flush=True)
    dc.atomic_json(res, O / f"w1_warning_{m}.json")


def synthetic():
    rng = np.random.default_rng(3); n = 4000
    d = pd.DataFrame(dict(icpsr=rng.integers(0, 400, n), key=rng.integers(0, 40, n).astype(str), party=rng.choice(["Democrat", "Republican"], n)))
    d["cp"] = (d.icpsr % 4 == 0).astype(int); d["fe"] = d.party + "|" + d.key
    d["err"] = (rng.random(n) < 0.3).astype(int)
    d["H"] = np.where(d.cp == 1, rng.random(n), d.err * 0.5 + rng.random(n) * 0.5)    # aligned: H separates errors; CP: noise
    a1, a0 = metrics(d[d.cp == 1])["auroc_within"], metrics(d[d.cp == 0])["auroc_within"]
    g = (d.party == "Republican").astype(float)
    d["y"] = 0.5 - 0.10 * d.cp - 0.15 * d.cp * g + rng.normal(0, .3, n)
    it = interaction(d, "y", g)
    out = dict(auroc_cp=a1, auroc_aligned=a0, interaction=it["b"], interaction_ci=it["ci95"], planted=-0.15)
    out["pass"] = bool(abs(a1 - 0.5) < 0.05 and a0 > 0.7 and it["ci95"][0] < -0.15 < it["ci95"][1])
    dc.atomic_json(out, O / "synthetic.json"); print(out)
    if not out["pass"]: raise SystemExit("STOP: synthetic failed")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--synthetic", action="store_true"); a = ap.parse_args()
    if a.synthetic: synthetic()
    else:
        for m in MODELS: run(m)
