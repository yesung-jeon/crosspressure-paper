#!/usr/bin/env python
"""Study V stage 5 (CPU): estimates for PROTOCOL §6. One code path for model predictions, reference predictors, the synthetic check
and the minimum detectable effect.

Linear probability model: y ~ cp + party x roll-call fixed effects. Two-way cluster-robust covariance (Cameron, Gelbach & Miller 2011)
by member and roll call: V = V_member + V_rollcall - V_member x rollcall, each piece a CR1 covariance from kim-kit cluster_fit.py, whose
coefficients and covariance are reconstructed by matrix algebra (stops above 1e-6). Fixed effects are absorbed by within-cell demeaning
(Frisch-Waugh-Lovell); the CR1 degrees-of-freedom factor counts the absorbed cells (K = 1 + number of cells), checked against the
dummy-variable fit on a subsample in --synthetic.

  python estimate_votes.py --synthetic           # gate 2: planted effect, recovery and reconstruction
  python estimate_votes.py --mde                 # PROTOCOL 6.5, from the party-rule pseudo-outcome (actual votes only)
  python estimate_votes.py --model qwen --select pilot|main
"""
import argparse, json, sys
from pathlib import Path
import numpy as np, pandas as pd

V = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(V / "code"))                 # rebuild: the package's cluster_fit.py (identical to kim-kit's), not ~/.claude/kim-kit
sys.path.insert(0, str(V.parent / "02_ideology_map" / "code"))
from cluster_fit import cr1_cov, fit_fe  # noqa: E402
import map_common as dc  # noqa: E402

O = V / "out" / "v5"; O.mkdir(parents=True, exist_ok=True)

def within(d, y, x, fe):
    g = d.groupby(fe)
    return d[y] - g[y].transform("mean"), d[x] - g[x].transform("mean")

def twoway(d, y="y", x="cp", fe="fe", c1="icpsr", c2="key"):
    """coefficient on x with FE absorbed; two-way CR1 covariance. Returns dict."""
    d = d[[y, x, fe, c1, c2]].dropna().copy()
    keep = d.groupby(fe)[x].transform("nunique") > 1             # cells without variation in x do not identify the coefficient
    yt, xt = within(d, y, x, fe)
    X = xt.values[:, None]; b = float(np.linalg.lstsq(X, yt.values, rcond=None)[0][0]); u = yt.values - X[:, 0] * b
    N, n_fe = len(d), d[fe].nunique(); K = 1 + n_fe
    def piece(groups):
        V_, G = cr1_cov(X, u, pd.factorize(groups)[0])
        N_, K_ = X.shape                                            # cr1_cov uses K = 1; rescale to K = 1 + cells
        return V_[0, 0] * ((N - K_) / (N - K)), G
    v1, g1 = piece(d[c1].astype(str)); v2, g2 = piece(d[c2].astype(str)); v12, g12 = piece(d[c1].astype(str) + "#" + d[c2].astype(str))
    var = v1 + v2 - v12
    if var <= 0: var = max(v1, v2)                                  # CGM fallback when the combination is not positive
    se = float(np.sqrt(var))
    return dict(b=b, se=se, ci95=[b - 1.96 * se, b + 1.96 * se], ci90=[b - 1.645 * se, b + 1.645 * se],
                ci_bonf3=[b - 2.394 * se, b + 2.394 * se], n=int(N), n_fe=int(n_fe), clusters={c1: int(g1), c2: int(g2)},
                share_in_identifying_cells=round(float(keep.mean()), 4), se_member=float(np.sqrt(v1)), se_rollcall=float(np.sqrt(v2)))

def synthetic():
    """gate 2: planted cp effect -0.10 with member and roll-call random effects; plus a dummy-variable reconstruction on a subsample."""
    rng = np.random.default_rng(dc.seed_for("V-synth") % 2**32)
    nm, nr = 600, 150
    mem = pd.DataFrame(dict(icpsr=np.arange(nm), party=rng.integers(0, 2, nm), cp=(rng.random(nm) < 0.22).astype(int), a=rng.normal(0, .15, nm)))
    rc = pd.DataFrame(dict(key=np.arange(nr), r=rng.normal(0, .15, nr)))
    d = mem.merge(rc, how="cross").sample(frac=0.6, random_state=1)
    p = np.clip(0.8 - 0.10 * d.cp + d.a + d.r + 0.05 * d.party, 0.01, 0.99)
    d["y"] = (rng.random(len(d)) < p).astype(float); d["fe"] = d.party.astype(str) + "|" + d.key.astype(str)
    r = twoway(d)
    # reconstruction: the FWL coefficient equals the dummy-variable coefficient; the member-clustered CR1 SE equals cluster_fit.py's
    sub = d[d.key < 40].copy()
    rs = twoway(sub)
    t = O / "synthetic_fit"; t.mkdir(exist_ok=True); (t / "coefficients.csv").unlink(missing_ok=True)   # fit_fe appends; a rerun starts fresh
    fd = fit_fe(sub.assign(cl=sub.icpsr.astype(str)), "y ~ cp + C(fe)", cluster="cl", name="synthetic_member", out=str(t), key=["cp"])
    b_dv = float(fd.params["cp"]); se_dv = float(fd.bse["cp"])
    out = dict(planted=-0.10, estimate=r, recovered=bool(r["ci95"][0] <= -0.10 <= r["ci95"][1]),
               reconstruction=dict(b_fwl=rs["b"], b_dummies=b_dv, abs_diff=abs(rs["b"] - b_dv),
                                   se_member_fwl=rs["se_member"], se_member_dummies=se_dv, rel_diff=abs(rs["se_member"] - se_dv) / se_dv))
    out["pass"] = bool(out["recovered"] and out["reconstruction"]["abs_diff"] < 1e-8 and out["reconstruction"]["rel_diff"] < 1e-6)
    dc.atomic_json(out, O / "synthetic.json"); print(json.dumps(out, indent=1))
    if not out["pass"]: raise SystemExit("STOP: synthetic gate failed")

def base_frame():
    P = pd.read_parquet(V / "out" / "v3" / "prompts.parquet",
                        columns=["pid", "key", "icpsr", "party", "known", "cp", "issue", "main_sample", "variant", "actual", "party_yea_share", "party_tie", "year"])
    P["fe"] = P.party + "|" + P.key
    P["party_correct"] = np.where(P.party_tie, np.nan, (P.actual == (P.party_yea_share > 0.5)).astype(float))
    return P

def mde():
    P = base_frame(); P = P[(P.variant == "main") & P.main_sample]
    out = {}
    for iss in ["abortion", "economic"]:
        r = twoway(P[P.issue == iss].assign(y=lambda d: d.party_correct))
        out[iss] = dict(party_rule_cp_coefficient=r["b"], se=r["se"], mde_80power_5pct=2.8 * r["se"], n=r["n"], clusters=r["clusters"])
    dc.atomic_json(out, O / "mde.json"); print(json.dumps(out, indent=1))

def dim1_reference(P):
    """PROTOCOL 6.2(b): per roll call, logistic regression of the actual vote on DW-NOMINATE dim 1, fitted on that roll call
    (in-sample ceiling for a single score). Nearly unpenalized (C = 1e6) so separable roll calls are classified perfectly."""
    from sklearn.linear_model import LogisticRegression
    mv = pd.read_csv(V / "out" / "v0" / "member_votes.csv.gz", usecols=["congress", "chamber", "rollnumber", "icpsr", "dim1"])
    mv["key"] = mv.congress.astype(str) + "|" + mv.chamber + "|" + mv.rollnumber.astype(str)
    P = P.merge(mv[["key", "icpsr", "dim1"]], on=["key", "icpsr"], how="left", validate="many_to_one")
    out = pd.Series(np.nan, index=P.index)
    for k, g in P[P.dim1.notna()].groupby("key"):
        if g.actual.nunique() < 2: out[g.index] = 1.0; continue
        m = LogisticRegression(C=1e6, max_iter=1000).fit(g[["dim1"]].values, g.actual.values)
        out[g.index] = (m.predict(g[["dim1"]].values) == g.actual.values).astype(float)
    return out.values

def model_frame(model, selects, known_model=None, variant="main"):
    P = base_frame(); P = P[P.variant == variant]
    parts = [pd.read_parquet(f) for s in selects for f in sorted((V / "out" / "v4" / model / s).glob("part_*.parquet"))]
    R = pd.concat(parts, ignore_index=True)
    assert not R.pid.duplicated().any()
    d = P.merge(R, on="pid", how="inner", validate="one_to_one")
    d["mass"] = d.p_yea + d.p_nay; d["format_fail"] = d.mass < 0.5
    d["share_yea"] = d.p_yea / d.mass; d["pred"] = (d.share_yea > 0.5).astype(int)
    d["correct"] = np.where(d.format_fail, np.nan, (d.pred == d.actual).astype(float))
    d["correct_bound"] = np.where(d.format_fail, 0.0, d.correct)            # 6.4(v): format failures counted as wrong
    d["confidence"] = (d.share_yea - 0.5).abs(); d["brier"] = (d.share_yea - d.actual) ** 2
    maj = (d.party_yea_share > 0.5).astype(int)
    d["pred_defect"] = np.where(d.party_tie | d.format_fail, np.nan, (d.pred != maj).astype(float))
    d["actual_defect"] = np.where(d.party_tie, np.nan, (d.actual != maj).astype(float))
    d["gain_over_party"] = d.correct - d.party_correct
    known = pd.read_csv(dc.OUT / (known_model or model) / "s3" / "temporal_member_scores.csv", usecols=["congress", "chamber", "icpsr", "known"])
    known["k2"] = known.congress.astype(str) + "|" + known.chamber + "|" + known.icpsr.astype(str)
    d["k2"] = d.key.str.rsplit("|", n=1).str[0] + "|" + d.icpsr.astype(str)
    d = d.drop(columns="known").merge(known[["k2", "known"]], on="k2", how="left", validate="many_to_one")
    d["dim1_correct"] = dim1_reference(d)
    return d

def estimate(model, selects, tag):
    d = model_frame(model, selects)
    res = dict(model=model, selects=selects, n=int(len(d)), format_fail=d.groupby(["issue", "cp"]).format_fail.mean().round(4).unstack().to_dict())
    desc = {}
    for iss, g in d[d.main_sample].groupby("issue"):
        by = g.groupby("cp")
        desc[iss] = dict(n=by.size().to_dict(), accuracy=by.correct.mean().round(4).to_dict(),
                         party_rule_accuracy=by.party_correct.mean().round(4).to_dict(),
                         dim1_reference_accuracy=by.dim1_correct.mean().round(4).to_dict(),
                         actual_defection=g.groupby(["cp", "party"]).actual_defect.mean().round(4).unstack().to_dict(),
                         predicted_defection=g.groupby(["cp", "party"]).pred_defect.mean().round(4).unstack().to_dict(),
                         confidence=by.confidence.mean().round(4).to_dict(), brier=by.brier.mean().round(4).to_dict(),
                         share_predicted_yea=by.pred.mean().round(4).to_dict(), share_actual_yea=by.actual.mean().round(4).to_dict())
    res["descriptive"] = desc
    reg = {}
    for iss, g in d[d.main_sample].groupby("issue"):
        reg[iss] = {"model_correct (6.1 preferred)" if iss == "abortion" else "model_correct": twoway(g.assign(y=g.correct)),
                    "party_rule_correct (6.2a)": twoway(g.assign(y=g.party_correct)),
                    "dim1_reference_correct (6.2b)": twoway(g.assign(y=g.dim1_correct)),
                    "gain_over_party (6.2c)": twoway(g.assign(y=g.gain_over_party)),
                    "format_fail_as_wrong (6.4v)": twoway(g.assign(y=g.correct_bound)),
                    "recognized_members_only (6.4iii)": twoway(g[g.known.astype(bool)].assign(y=lambda x: x.correct))}
    res["regressions"] = reg
    if (~d.main_sample).any():
        res["with_sensitivity_rollcalls (6.4iv)"] = {iss: twoway(g.assign(y=g.correct)) for iss, g in d.groupby("issue")}
    dc.atomic_json(res, O / f"estimates_{model}_{tag}.json")
    d.drop(columns=["k2"]).to_parquet(O / f"frame_{model}_{tag}.parquet", index=False)
    print(json.dumps(res, indent=1, default=str))

def variant_compare(model, variant, issues):
    """PROTOCOL 6.4(vi): a prompt variant against the main prompt on the same 25% roll-call sample (same members, same votes)."""
    v = model_frame(model, [variant], variant=variant)
    main_sel = {"abortion": "pilot", "economic": "economic"}
    m = model_frame(model, [main_sel[i] for i in issues])
    m = m[m.key.isin(v.key.unique())]
    v = v[v.issue.isin(issues)]
    j = m[["key", "icpsr", "pred", "share_yea"]].merge(v[["key", "icpsr", "pred", "share_yea"]], on=["key", "icpsr"], suffixes=("_main", "_var"),
                                                      validate="one_to_one")
    res = dict(model=model, variant=variant, n_pairs=int(len(j)), prediction_agreement=round(float((j.pred_main == j.pred_var).mean()), 4),
               corr_share_yea=round(float(np.corrcoef(j.share_yea_main, j.share_yea_var)[0, 1]), 4), by_issue={})
    for iss in issues:
        a, b = m[m.issue == iss], v[v.issue == iss]
        res["by_issue"][iss] = dict(
            main=dict(accuracy=a.groupby("cp").correct.mean().round(4).to_dict(), pred_yea=a.groupby("cp").pred.mean().round(4).to_dict(),
                      cp_coefficient=twoway(a.assign(y=a.correct))),
            variant=dict(accuracy=b.groupby("cp").correct.mean().round(4).to_dict(), pred_yea=b.groupby("cp").pred.mean().round(4).to_dict(),
                         format_fail=round(float(b.format_fail.mean()), 4), cp_coefficient=twoway(b.assign(y=b.correct))),
            actual_yea=a.groupby("cp").actual.mean().round(4).to_dict())
    dc.atomic_json(res, O / f"variant_{model}_{variant}.json"); print(json.dumps(res, indent=1, default=str))

def read_parts(model, select):
    fs = sorted((V / "out" / "v4" / model / select).glob("part_*.parquet"))
    R = pd.concat([pd.read_parquet(f) for f in fs], ignore_index=True)
    assert not R.pid.duplicated().any(); return R

def order_avg_frame(model, issues=("abortion", "economic"), known_model=None):
    """Protocol v2 (A4): YEA-first (main prompt) and NAY-first (swap) probabilities for the same member vote, averaged.
    share_avg = mean of the two YEA shares; prediction = YEA if share_avg > 0.5. Only member votes scored in both orders enter."""
    P = base_frame(); P = P[(P.variant == "main") & P.main_sample & P.issue.isin(issues)]
    first = {"abortion": "pilot", "economic": "economic"}
    A = pd.concat([read_parts(model, first[i]) for i in issues] +
                  ([read_parts(model, "sample_yf")] if (V / "out" / "v4" / model / "sample_yf").exists() else [])).drop_duplicates("pid")
    B = pd.concat([read_parts(model, f"swap_{i}") for i in issues]); B["pid"] = B.pid.str.replace(r"\|swap$", "|main", regex=True)
    if (V / "out" / "v4" / model / "V2").exists():                 # NAY-first votes scored as V2 are not rescored in swap_* (A6)
        b2 = read_parts(model, "V2"); b2["pid"] = b2.pid.str.replace(r"\|V2$", "|main", regex=True)
        B = pd.concat([B, b2[b2.pid.isin(P.pid)]])
    assert not B.pid.duplicated().any()
    d = P.merge(A[["pid", "p_yea", "p_nay"]], on="pid", validate="one_to_one").merge(
        B[["pid", "p_yea", "p_nay"]], on="pid", suffixes=("_yf", "_nf"), validate="one_to_one")
    d["mass_yf"], d["mass_nf"] = d.p_yea_yf + d.p_nay_yf, d.p_yea_nf + d.p_nay_nf
    d["format_fail"] = (d.mass_yf < 0.5) | (d.mass_nf < 0.5)
    d["share_yf"], d["share_nf"] = d.p_yea_yf / d.mass_yf, d.p_yea_nf / d.mass_nf
    d["share_avg"] = (d.share_yf + d.share_nf) / 2
    for s in ["yf", "nf", "avg"]:
        d[f"pred_{s}"] = (d[f"share_{s}"] > 0.5).astype(int)
        d[f"correct_{s}"] = np.where(d.format_fail, np.nan, (d[f"pred_{s}"] == d.actual).astype(float))
    p = d.share_avg.clip(1e-6, 1 - 1e-6)
    d["brier"] = np.where(d.format_fail, np.nan, (d.share_avg - d.actual) ** 2)
    d["logloss"] = np.where(d.format_fail, np.nan, -(d.actual * np.log(p) + (1 - d.actual) * np.log(1 - p)))
    maj = (d.party_yea_share > 0.5).astype(int)
    d["pred_defect"] = np.where(d.party_tie | d.format_fail, np.nan, (d.pred_avg != maj).astype(float))
    d["actual_defect"] = np.where(d.party_tie, np.nan, (d.actual != maj).astype(float))
    d["gain_over_party"] = d.correct_avg - d.party_correct
    known = pd.read_csv(dc.OUT / (known_model or model) / "s3" / "temporal_member_scores.csv", usecols=["congress", "chamber", "icpsr", "known"])
    known["k2"] = known.congress.astype(str) + "|" + known.chamber + "|" + known.icpsr.astype(str)
    d["k2"] = d.key.str.rsplit("|", n=1).str[0] + "|" + d.icpsr.astype(str)
    d = d.drop(columns="known").merge(known[["k2", "known"]], on="k2", how="left", validate="many_to_one").drop(columns="k2")
    d["dim1_correct"] = dim1_reference(d)
    return d

def estimate_avg(model, issues):
    d = order_avg_frame(model, issues)
    res = dict(model=model, protocol="v2 order-averaged (A4)", n=int(len(d)), format_fail=round(float(d.format_fail.mean()), 4), by_issue={})
    for iss, g in d.groupby("issue"):
        t = g.groupby(["key", "party"]).agg(p=("share_avg", "mean"), a=("actual", "mean")).unstack().dropna()
        gp, ga = t["p"]["Democrat"] - t["p"]["Republican"], t["a"]["Democrat"] - t["a"]["Republican"]
        by = g.groupby("cp")
        res["by_issue"][iss] = dict(
            n=by.size().to_dict(),
            accuracy=dict(avg=by.correct_avg.mean().round(4).to_dict(), yea_first=by.correct_yf.mean().round(4).to_dict(),
                          nay_first=by.correct_nf.mean().round(4).to_dict()),
            party_rule_accuracy=by.party_correct.mean().round(4).to_dict(), dim1_reference_accuracy=by.dim1_correct.mean().round(4).to_dict(),
            share_predicted_yea=dict(avg=by.pred_avg.mean().round(4).to_dict(), yea_first=by.pred_yf.mean().round(4).to_dict(),
                                     nay_first=by.pred_nf.mean().round(4).to_dict()),
            share_actual_yea=by.actual.mean().round(4).to_dict(), brier=by.brier.mean().round(4).to_dict(), logloss=by.logloss.mean().round(4).to_dict(),
            share_near_half=round(float(((g.share_avg - 0.5).abs() < 0.05).mean()), 4),
            actual_defection=g.groupby(["cp", "party"]).actual_defect.mean().round(4).unstack().to_dict(),
            predicted_defection=g.groupby(["cp", "party"]).pred_defect.mean().round(4).unstack().to_dict(),
            party_gap=dict(pred=round(float(gp.abs().mean()), 4), actual=round(float(ga.abs().mean()), 4),
                           corr=round(float(np.corrcoef(gp, ga)[0, 1]), 4)),
            regressions={"accuracy (6.1 preferred)" if iss == "abortion" else "accuracy": twoway(g.assign(y=g.correct_avg)),
                         "brier (co-primary, A4)": twoway(g.assign(y=g.brier)), "logloss (A4)": twoway(g.assign(y=g.logloss)),
                         "party_rule (6.2a)": twoway(g.assign(y=g.party_correct)), "dim1_reference (6.2b)": twoway(g.assign(y=g.dim1_correct)),
                         "gain_over_party (6.2c)": twoway(g.assign(y=g.gain_over_party)),
                         "recognized_only (6.4iii)": twoway(g[g.known.astype(bool)].assign(y=lambda x: x.correct_avg)),
                         "yea_first_only (v1 reading)": twoway(g.assign(y=g.correct_yf)), "nay_first_only": twoway(g.assign(y=g.correct_nf))})
    tag = "_".join(issues)
    dc.atomic_json(res, O / f"estimates_v2_{model}_{tag}.json"); d.to_parquet(O / f"frame_v2_{model}_{tag}.parquet", index=False)
    print(json.dumps(res, indent=1, default=str))

def competence(d, share="share_avg", correct="correct_avg", reps=2000):
    """A5 model competence condition (sealed before the sample test and before any Llama/OLMo output):
    (a) aligned members (CP = 0): accuracy above 0.5, 95% roll-call bootstrap interval excluding 0.5;
    (b) direction: across roll calls, the model's Democrat-minus-Republican gap in YEA share correlates positively with the actual gap,
        95% roll-call bootstrap interval excluding 0.
    A model passing both is 'competent'; its CP comparison is interpreted. Otherwise the CP comparison is reported but not interpreted as
    evidence about cross-pressured members ('the model does not perform the task')."""
    rng = np.random.default_rng(dc.seed_for("V-A5") % 2**32)
    al = d[d.cp == 0].groupby("key")[correct].agg(["sum", "count"])
    t = d.groupby(["key", "party"]).agg(p=(share, "mean"), a=("actual", "mean")).unstack().dropna()
    gp, ga = (t["p"]["Democrat"] - t["p"]["Republican"]).values, (t["a"]["Democrat"] - t["a"]["Republican"]).values
    acc_b, cor_b = [], []
    for _ in range(reps):
        i = rng.integers(0, len(al), len(al)); acc_b.append(al["sum"].values[i].sum() / al["count"].values[i].sum())
        k = rng.integers(0, len(gp), len(gp)); cor_b.append(np.corrcoef(gp[k], ga[k])[0, 1])
    acc = float(al["sum"].sum() / al["count"].sum()); cor = float(np.corrcoef(gp, ga)[0, 1])
    a_ci, c_ci = np.percentile(acc_b, [2.5, 97.5]).tolist(), np.nanpercentile(cor_b, [2.5, 97.5]).tolist()
    return dict(aligned_accuracy=acc, aligned_accuracy_ci95=a_ci, party_gap_corr=cor, party_gap_corr_ci95=c_ci,
                pass_a=bool(a_ci[0] > 0.5), pass_b=bool(c_ci[0] > 0), competent=bool(a_ci[0] > 0.5 and c_ci[0] > 0), rollcalls=int(len(al)))

def sample_order_avg(model):
    """A5 sample test: sealed 25% roll-call sample, YEA-first (pilot/economic/sample_yf) and NAY-first (V2), order-averaged."""
    P = base_frame(); P = P[(P.variant == "main") & P.main_sample]
    keys = set(pd.read_csv(V / "out" / "v3" / "variant_rollcalls.csv").key); P = P[P.key.isin(keys)]
    A = pd.concat([read_parts(model, s) for s in ["pilot", "economic", "sample_yf"] if (V / "out" / "v4" / model / s).exists()])
    A = A[A.pid.isin(P.pid)].drop_duplicates("pid")
    B = read_parts(model, "V2"); B["pid"] = B.pid.str.replace(r"\|V2$", "|main", regex=True)
    d = P.merge(A[["pid", "p_yea", "p_nay"]], on="pid", validate="one_to_one").merge(B[["pid", "p_yea", "p_nay"]], on="pid",
                                                                                      suffixes=("_yf", "_nf"), validate="one_to_one")
    assert len(d) == len(P), (len(d), len(P))
    d["format_fail"] = ((d.p_yea_yf + d.p_nay_yf) < 0.5) | ((d.p_yea_nf + d.p_nay_nf) < 0.5)
    d["share_yf"] = d.p_yea_yf / (d.p_yea_yf + d.p_nay_yf); d["share_nf"] = d.p_yea_nf / (d.p_yea_nf + d.p_nay_nf)
    d["share_avg"] = (d.share_yf + d.share_nf) / 2
    for s in ["yf", "nf", "avg"]:
        d[f"pred_{s}"] = (d[f"share_{s}"] > 0.5).astype(int)
        d[f"correct_{s}"] = np.where(d.format_fail, np.nan, (d[f"pred_{s}"] == d.actual).astype(float))
    d["brier"] = (d.share_avg - d.actual) ** 2
    res = dict(model=model, test="A5 sample (25% roll calls, both orders)", n=int(len(d)), format_fail=round(float(d.format_fail.mean()), 4),
               corr_two_orders=round(float(np.corrcoef(d.share_yf, d.share_nf)[0, 1]), 4), by_issue={})
    for iss, g in d.groupby("issue"):
        by = g.groupby("cp")
        res["by_issue"][iss] = dict(
            n=by.size().to_dict(), competence=competence(g),
            accuracy=dict(avg=by.correct_avg.mean().round(4).to_dict(), yea_first=by.correct_yf.mean().round(4).to_dict(),
                          nay_first=by.correct_nf.mean().round(4).to_dict()),
            party_rule_accuracy=by.party_correct.mean().round(4).to_dict(),
            pred_yea=dict(avg=by.pred_avg.mean().round(4).to_dict(), yea_first=by.pred_yf.mean().round(4).to_dict(),
                          nay_first=by.pred_nf.mean().round(4).to_dict()),
            actual_yea=by.actual.mean().round(4).to_dict(), brier=by.brier.mean().round(4).to_dict(),
            share_near_half=round(float(((g.share_avg - 0.5).abs() < 0.05).mean()), 4),
            regressions={"accuracy (6.1)": twoway(g.assign(y=g.correct_avg)), "brier": twoway(g.assign(y=g.brier)),
                         "party_rule": twoway(g.assign(y=g.party_correct))})
    dc.atomic_json(res, O / f"sample_v2_{model}.json"); print(json.dumps(res, indent=1, default=str))

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--synthetic", action="store_true"); ap.add_argument("--mde", action="store_true")
    ap.add_argument("--model"); ap.add_argument("--select"); ap.add_argument("--variant"); ap.add_argument("--issues", nargs="+")
    a = ap.parse_args()
    if a.synthetic: synthetic()
    elif a.mde: mde()
    elif a.variant: variant_compare(a.model, a.variant, a.issues or ["abortion", "economic"])
    elif a.select == "v2": estimate_avg(a.model, tuple(a.issues or ["abortion", "economic"]))
    elif a.select == "sample": sample_order_avg(a.model)
    else:
        sel = {"pilot": ["pilot"], "main": ["pilot", "economic"], "all": ["pilot", "economic", "sensitivity"]}[a.select]
        estimate(a.model, sel, a.select)
