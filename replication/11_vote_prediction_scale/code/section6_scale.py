#!/usr/bin/env python
"""PROTOCOL.md Amendment A1: the remaining Section 6 / Table 2 / Appendix D quantities with the 9-point scale prediction, beside the
binary value on identical rows. Each producer is first gated against its sealed binary value. Reads sealed outputs only; writes ../out/s6/.
  python section6_scale.py"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scale_accuracy as SA  # noqa: E402  (to_s, scale_votes, add_scale, est, v5, dc, share_toward, boot_toward)
REP, V, v5, dc = SA.REP, SA.V, SA.v5, SA.dc
O = SA.O / "s6"; O.mkdir(exist_ok=True)
sys.path.insert(0, str(REP / "12_speech_and_state" / "code")); sys.path.insert(0, str(REP / "15_named_member_uncertainty" / "code"))
import state_lean as SL  # noqa: E402  (rows, lean_table; main() is guarded)
import named_common as nc  # noqa: E402

GATES, ROWS, DESC = [], [], {}


def gate(m, name, got, sealed, tol=1e-10):
    GATES.append(dict(model=m, check=name, reproduced=float(got), sealed=float(sealed), abs_diff=abs(float(got) - float(sealed)), tol=tol))


def put(m, issue, item, fmt, r):
    ROWS.append(dict(model=m, issue=issue, item=item, format=fmt, b=r["b"], lo95=r["ci95"][0], hi95=r["ci95"][1], n=r["n"]))


def tw(d, y, x="cp"):
    return v5.twoway(d.assign(y=d[y], cp=d[x]))


def party_gap(g, share):
    t = g.groupby(["key", "party"]).agg(p=(share, "mean"), a=("actual", "mean")).unstack().dropna()
    gp, ga = t["p"]["Democrat"] - t["p"]["Republican"], t["a"]["Democrat"] - t["a"]["Republican"]
    return float(gp.abs().mean()), float(ga.abs().mean()), float(np.corrcoef(gp, ga)[0, 1])


def twoway_with_control(g, y, ctrl):
    """as 07_nominate_benchmarks/code/02_gmp_fit.py twoway_with_control + dof_control (re-implemented: that script runs on import)"""
    e = g[[y, "cp", ctrl, "fe", "icpsr", "key"]].dropna().copy()
    dm = lambda s: s - e.groupby("fe")[s.name].transform("mean")
    yt, xt, zt = dm(e[y]), dm(e.cp), dm(e[ctrl])
    ry = yt - zt * (zt @ yt) / (zt @ zt); rx = xt - zt * (zt @ xt) / (zt @ zt)
    r = v5.twoway(e.assign(ry=ry, rx=rx), y="ry", x="rx"); N, n_fe = len(e), e.fe.nunique()
    f = np.sqrt((N - 1 - n_fe) / (N - 2 - n_fe)); se = r["se"] * f
    return dict(b=r["b"], se=se, ci95=[r["b"] - 1.96 * se, r["b"] + 1.96 * se], n=r["n"])


def main():
    hs = pd.read_csv(REP / "data" / "HSall_members.csv", low_memory=False)[
        ["congress", "chamber", "icpsr", "nominate_geo_mean_probability"]]
    L, _ = SL.lean_table()
    D3S = json.load(open(REP / "12_speech_and_state" / "out" / "d" / "d.json"))
    N2S = json.load(open(REP / "07_nominate_benchmarks" / "out" / "n2.json"))
    CS = json.load(open(REP / "08_supplementary_checks" / "cases" / "case_votes.json"))
    for m in SA.MODELS:
        w, _ = SA.scale_votes(m)
        fa = pd.read_parquet(V / "out" / "v5" / f"frame_v2_{m}_abortion_economic.parquet")
        fg = pd.read_parquet(V / "out" / "g2" / f"frame_{m}.parquet")
        E = json.load(open(V / "out" / "v5" / f"estimates_v2_{m}_abortion_economic.json"))
        C = json.load(open(V / "out" / "v5" / f"competence_party_v2_{m}.json"))
        G = json.load(open(V / "out" / "g2" / f"estimates_{m}.json"))
        GE = json.load(open(V / "out" / "g2" / f"error_direction_{m}.json"))
        A = SA.add_scale(fa[~fa.format_fail].copy(), w); Gd = SA.add_scale(fg[~fg.format_fail].copy(), w)
        # PROTOCOL rule: scale format failures are dropped and counted, not asserted away
        DESC.setdefault("_scale_dropped", {})[m] = dict(abortion_economic=int((A.scale_missing | A.scale_fail).sum()),
                                                        guns=int((Gd.scale_missing | Gd.scale_fail).sum()))
        A = A[~(A.scale_missing | A.scale_fail)].copy(); Gd = Gd[~(Gd.scale_missing | Gd.scale_fail)].copy()
        for d in (A, Gd):
            d["brier_scale"] = (d.s_yea - d.actual) ** 2; d["gain_scale"] = d.correct_scale - d.party_correct
        dm = {}
        # --- abortion / economic: A5, Brier, gain over party, party gap
        for i, g in A.groupby("issue"):
            reg = E["by_issue"][i]["regressions"]
            gate(m, f"{i} brier", tw(g, "brier")["b"], reg["brier (co-primary, A4)"]["b"])
            gate(m, f"{i} gain", tw(g, "gain_over_party")["b"], reg["gain_over_party (6.2c)"]["b"])
            pg = party_gap(g, "share_avg"); gate(m, f"{i} party gap pred", round(pg[0], 4), E["by_issue"][i]["party_gap"]["pred"], 1e-9)
            cb = v5.competence(g); gate(m, f"{i} A5 aligned acc", cb["aligned_accuracy"], C[i]["competence"]["aligned_accuracy"])
            # the sealed A5 ran on the frame with binary format failures kept (their YEA share enters the
            # party-gap correlation), so the gate uses that sample; the scale A5 below uses the rows with both formats valid
            cf = v5.competence(fa[fa.issue == i])
            gate(m, f"{i} A5 party-gap corr (producer sample)", cf["party_gap_corr"], C[i]["competence"]["party_gap_corr"])
            cs = v5.competence(g, share="s_yea", correct="correct_scale")
            for y, item in (("brier", "Brier"), ("gain_over_party", "gain over party rule")):
                put(m, i, item, "binary", tw(g, y))
            put(m, i, "Brier", "scale", tw(g, "brier_scale")); put(m, i, "gain over party rule", "scale", tw(g, "gain_scale"))
            ps = party_gap(g, "s_yea")
            dm[i] = dict(A5_binary=cb, A5_scale=cs, party_gap_binary=pg, party_gap_scale=ps,
                         party_rule_acc=g.groupby("cp").party_correct.mean().round(4).to_dict(),
                         dim1_ref_acc=g.groupby("cp").dim1_correct.mean().round(4).to_dict(),
                         brier_mean=dict(binary=g.groupby("cp").brier.mean().round(4).to_dict(),
                                         scale=g.groupby("cp").brier_scale.mean().round(4).to_dict()))
        # --- guns
        gl = Gd[Gd.gun_cp_loo.notna()]
        gate(m, "guns abortion CP same rows", tw(gl, "correct_avg")["b"], G["gun_cp_loo"]["abortion_cp_same_rows"]["b"])
        gate(m, "guns brier", tw(Gd, "brier")["b"], G["regressions_abortion_cp"]["brier"]["b"])
        cbg = v5.competence(Gd); gate(m, "guns A5 aligned acc", cbg["aligned_accuracy"], G["competence"]["aligned_accuracy"])
        gate(m, "guns A5 party-gap corr", cbg["party_gap_corr"], G["competence"]["party_gap_corr"])
        for fmt, y in (("binary", "correct_avg"), ("scale", "correct_scale")):
            put(m, "guns", "abortion CP on gun-LOO rows", fmt, tw(gl, y))
        put(m, "guns", "Brier (abortion CP)", "binary", tw(Gd, "brier")); put(m, "guns", "Brier (abortion CP)", "scale", tw(Gd, "brier_scale"))
        put(m, "guns", "Brier (gun CP)", "binary", tw(gl, "brier", "gun_cp_loo"))
        put(m, "guns", "Brier (gun CP)", "scale", tw(gl, "brier_scale", "gun_cp_loo"))
        for p, h in Gd.groupby("party"):
            gate(m, f"guns {p}", tw(h, "correct_avg")["b"], G["by_party_abortion_cp"][p]["accuracy"]["b"])
            for fmt, y in (("binary", "correct_avg"), ("scale", "correct_scale")):
                put(m, "guns", f"abortion CP, {p} only", fmt, tw(h, y))
        e = Gd[~Gd.party_tie].copy(); e["maj"] = (e.party_yea_share > 0.5).astype(int)
        ed = {}
        for cp, h in e.groupby("cp"):
            for pred, corr in (("pred_avg", "correct_avg"), ("pred_scale", "correct_scale")):
                sh, nw = SA.share_toward(h, pred, corr)
                rng = np.random.default_rng(dc.seed_for("scale_acc_gun", m, pred, int(cp)) % 2**32)
                ed[f"cp={cp}|{pred}"] = dict(n_wrong=nw, toward_party=sh, ci95=SA.boot_toward(h, pred, corr, rng))
        gate(m, "guns error direction cp=1", ed["cp=1|pred_avg"]["toward_party"], GE["cells"]["cp=1"]["toward_party_among_wrong"])
        dm["guns"] = dict(A5_binary=cbg, A5_scale=v5.competence(Gd, share="s_yea", correct="correct_scale"), error_direction=ed,
                          party_gap_binary=party_gap(Gd, "share_avg"), party_gap_scale=party_gap(Gd, "s_yea"))
        # --- state-based CP (D3): state_lean.rows, Congress >= 95
        v, _ = SL.rows(m, L)
        sets = [(i, g) for i, g in A.groupby("issue")] + ([("guns", Gd)] if dc.gun_competent(m) else [])
        for i, g in sets:
            g = g.copy(); kk = g.key.str.split("|", expand=True); g["congress"] = kk[0].astype(int); g["chamber"] = kk[1]
            g = g[g.congress >= 95].merge(v[["congress", "chamber", "icpsr", "ccp"]], on=["congress", "chamber", "icpsr"],
                                          how="left", validate="many_to_one").dropna(subset=["ccp"])
            gate(m, f"D3 {i}", tw(g, "correct_avg", "ccp")["b"], D3S[m]["D3_W1"][i]["ccp"]["b"])
            for sub, k in (("Senate", "senate_only"), ("House", "house_only")):                                # by chamber
                gate(m, f"D3 {i} {sub}", tw(g[g.chamber == sub], "correct_avg", "ccp")["b"], D3S[m]["D3_W1"][i][k]["b"])
            for sub, h in (("all", g), ("Senate", g[g.chamber == "Senate"]), ("House", g[g.chamber == "House"])):
                for fmt, y in (("binary", "correct_avg"), ("scale", "correct_scale")):
                    put(m, i, f"state-based CP ({sub})", fmt, tw(h, y, "ccp"))
        # --- NOMINATE fit control (N2)
        vv = nc.analysis_rows(dc.OUT / m / "s3" / "temporal_member_scores.csv")
        vv = vv.merge(hs, on=["congress", "chamber", "icpsr"], how="left", validate="one_to_one").dropna(subset=["nominate_geo_mean_probability"])
        x = vv.nominate_geo_mean_probability; vv["gmp_z"] = (x - x.mean()) / x.std()
        sets = [(i, g) for i, g in A.groupby("issue")] + ([("guns", Gd)] if dc.gun_competent(m) else [])
        for i, g in sets:
            g = g.copy()
            if "congress" not in g:
                kk = g.key.str.split("|", expand=True); g["congress"] = kk[0].astype(int); g["chamber"] = kk[1]
            g = g.merge(vv[["congress", "chamber", "icpsr", "gmp_z"]], on=["congress", "chamber", "icpsr"], how="left", validate="many_to_one")
            g = g.dropna(subset=["gmp_z", "correct_avg", "dim1_correct"])
            gate(m, f"N2 {i}", twoway_with_control(g, "correct_avg", "gmp_z")["b"], N2S[m]["votes"][i]["cp_given_gmp"]["b"])
            for fmt, y in (("binary", "correct_avg"), ("scale", "correct_scale")):
                put(m, i, "CP given NOMINATE fit", fmt, twoway_with_control(g, y, "gmp_z"))
        # --- named cases
        cases = {12104: "Thomas Eagleton", 12107: "Robert Packwood", 14661: "Olympia Snowe"}
        c = A[A.icpsr.isin(list(cases)) & A.main_sample.astype(bool)].copy()
        c["maj"] = (c.party_yea_share > 0.5).astype(int).where(c.party_yea_share != 0.5, -1)   # ties: no majority (as case_votes.py, 11-02b C7-6)
        cd = {}
        for icp, name in cases.items():
            for i, g in c[c.icpsr == icp].groupby("issue"):
                gate(m, f"case {name} {i} acc", round(float(g.correct_avg.mean()), 4), CS[name][m][i]["accuracy"], 1e-9)
                r = {}
                for fmt, pred, corr in (("binary", "pred_avg", "correct_avg"), ("scale", "pred_scale", "correct_scale")):
                    wr = g[g[corr] == 0]
                    r[fmt] = dict(n=len(g), accuracy=float(g[corr].mean()), n_wrong=len(wr),
                                  wrong_with_party=float((wr[wr.maj >= 0][pred] == wr[wr.maj >= 0].maj).mean()) if (wr.maj >= 0).any() else None)
                cd[f"{name}|{i}"] = r
        sn = c[(c.icpsr == 14661) & c.key.isin(["105|Senate|167", "105|Senate|474", "108|Senate|51", "108|Senate|402"])]
        cd["Snowe four roll calls"] = sn[["key", "actual", "share_avg", "s_yea", "pred_avg", "pred_scale"]].to_dict("records")
        dm["cases"] = cd
        DESC[m] = dm; print(m, "done", flush=True)
    Gt = pd.DataFrame(GATES); Gt.to_csv(O / "gates.csv", index=False)
    bad = Gt[Gt.abs_diff > Gt.tol]
    if len(bad):
        print(bad.to_string()); raise SystemExit("STOP: a sealed binary value was not reproduced")
    pd.DataFrame(ROWS).to_csv(O / "results.csv", index=False)
    json.dump(DESC, open(O / "descriptive.json", "w"), indent=1, default=float)
    print(pd.DataFrame(ROWS).round(4).to_string())


if __name__ == "__main__":
    main()
