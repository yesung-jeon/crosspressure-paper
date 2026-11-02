#!/usr/bin/env python
"""Analysis of the continuous-scale scoring. Estimators as the paper:
named members = Study N one-way estimator (party x Congress x chamber FE, member CR1; copied in er_helpers.py);
votes = W1 v5.twoway (party x roll-call FE, two-way clustering). Binary comparisons use the sealed values on identical rows.
  python analyze.py --synthetic   # planted effects recovered, null covered (both estimators)
  python analyze.py               # -> ../out/results.csv, ../out/summary.json"""
import argparse, json, sys
from pathlib import Path
import numpy as np, pandas as pd

H = Path(__file__).resolve().parents[1]; O = H / "out"; REP = H.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import er_helpers as ER  # noqa: E402
sys.path.insert(0, str(REP / "15_named_member_uncertainty" / "code"))
from named_common import items, want_yes  # noqa: E402

MODELS = ["qwen", "llama"]
L2 = np.log2


def dist(df, n):
    P = df[[f"p{k}" for k in range(1, n + 1)]].values; mass = P.sum(1); Q = P / mass[:, None]
    E = (Q * np.arange(1, n + 1)).sum(1); Hn = -(np.where(Q > 0, Q * L2(np.clip(Q, 1e-300, None)), 0)).sum(1) / L2(n)
    up = (E - 1) / (n - 1); s = np.where(df.order.values == "asc", up, 1 - up)          # s: 1 = "yes" / "YEA", direction-corrected
    return mass, s, Hn, Q[:, (n - 1) // 2], Q.max(1)


def load(task, m):
    D = O / task / m; fs = sorted(D.glob("part_*.done")); assert (D / "run.json").exists(), f"{task} {m} not finished"
    return pd.concat([pd.read_parquet(f.with_suffix(".parquet")) for f in fs], ignore_index=True)


def fit_row(rows, model, task, issue, qty, r, sub, x, y):
    rows.append(dict(model=model, task=task, issue=issue, quantity=qty, n=int(r["n"]), b=r["b"], lo95=r["lo95"], hi95=r["hi95"],
                     lo90=r["lo90"], hi90=r["hi90"], p=r["p"], mean_cp=float(sub[sub[x] == 1][y].mean()), mean_aligned=float(sub[sub[x] == 0][y].mean())))


def named(m, rows):
    df = load("named", m); mass, s, Hn, mid, top = dist(df, 7)
    df = df.assign(mass=mass, s=s, H7=Hn, Pmid=mid, top=top >= 0.9)
    IT = {i["id"]: i for i in items()}
    R = pd.read_parquet(REP / f"15_named_member_uncertainty/analysis/data/rows_{m}.parquet")
    ok = df[df.mass >= 0.5].merge(R[["rid", "vote_q"]], on="rid", validate="many_to_one")
    ok["c"] = np.where([want_yes(IT[i], q) for i, q in zip(ok["item"], ok.vote_q)], ok.s, 1 - ok.s)
    g = ok.groupby("rid").agg(H7=("H7", "mean"), Pmid=("Pmid", "mean"), top=("top", "mean"), C_scale=("c", "mean"))
    g["fail_share"] = df.groupby("rid").mass.apply(lambda v: float((v < 0.5).mean()))
    d = R.merge(g.reset_index(), on="rid", how="inner", validate="one_to_one")
    d["H7_minus_H"] = d.H7 - d.H; d["Cs_minus_C"] = d.C_scale - d.C_vote
    for lab, x, sub in [("abortion (vote CP)", "vote_cp", d), ("abortion (map CP)", "map_crossed", d), ("guns (gun CP)", "gun_cp", d[d.gun_cp.notna()])]:
        for qty in ["H7", "H", "H7_minus_H", "Pmid", "top", "C_scale", "C_vote", "Cs_minus_C"]:
            fit_row(rows, m, "named", lab, qty, ER.oneway(sub, qty, x, "fe", "icpsr"), sub, x, qty)
    return dict(rows=len(d), cell_fail_share=float((df.mass < 0.5).mean()), median_mass=float(np.median(df.mass)))


def votes(m, rows):
    df = load("votes", m); mass, s, Hn, mid, top = dist(df, 9)
    df = df.assign(mass=mass, s=s, H9=Hn, Pmid=mid, top=top >= 0.9)
    ok = df[df.mass >= 0.5]
    g = ok.groupby("pid").agg(s_yea=("s", "mean"), H9=("H9", "mean"), Pmid=("Pmid", "mean"), top=("top", "mean"), n_dir=("s", "size"))
    g = g[g.n_dir == 2]                                                           # both directions valid
    base = ER.add_plan1(ER.w1_rows(m))                                            # W1U rows, ties dropped, binary P_party and H
    d = base.merge(g.reset_index(), on="pid", how="inner", validate="many_to_one")   # guns appear twice (guns, guns_gcp)
    maj = d.party_yea_share > 0.5
    d["P_party_cont"] = np.where(maj, d.s_yea, 1 - d.s_yea)
    d["Pcont_minus_P"] = d.P_party_cont - d.P_party; d["H9_minus_H"] = d.H9 - d.H
    for iss, sub in d.groupby("issue"):
        for qty in ["P_party_cont", "P_party", "Pcont_minus_P", "act_party", "H9", "H", "H9_minus_H", "Pmid", "top"]:
            fit_row(rows, m, "votes", iss, qty, ER.tw(sub, qty), sub, "cp", qty)
    return dict(rows=len(d), cell_fail_share=float((df.mass < 0.5).mean()), median_mass=float(np.median(df.mass)))


def reading_old(r):
    if r.quantity in ("H7", "H9"):    # Study N rule (fixed before the data; kept for the record)
        if (r.lo95 > 0 or r.hi95 < 0) and abs(r.b) >= 0.05 and r.p_holm < 0.05: return "more uncertain" if r.b > 0 else "less uncertain"
        if r.lo90 >= -0.05 and r.hi90 <= 0.05: return "no meaningful difference"
        return "undetermined"
    return ""


def reading(r):
    if r.quantity in ("H7", "H9"):    # reading rule: any difference with 95% CI excluding 0 and Holm p < 0.05 counts; no size threshold
        p = r.p_holm if pd.notna(r.p_holm) else r.p    # economic placebo rows sit outside the Holm family
        if (r.lo95 > 0 or r.hi95 < 0) and p < 0.05: return "more uncertain" if r.b > 0 else "less uncertain"
        return "no difference detected"
    if r.quantity == "Pcont_minus_P":
        return "moves more than binary" if r.hi95 < 0 else ("moves less than binary" if r.lo95 > 0 else "no difference from binary")
    return ""


def synthetic():
    rng = np.random.default_rng(9); nm, nr = 500, 120
    mem = pd.DataFrame(dict(icpsr=np.arange(nm), party=rng.choice(["Democrat", "Republican"], nm), cp=(rng.random(nm) < .25).astype(int)))
    d = mem.merge(pd.DataFrame(dict(key=np.arange(nr).astype(str))), how="cross").sample(frac=.5, random_state=1)
    d["fe"] = d.party + "|" + d.key; out = {}
    for eff in (0.06, 0.0):
        d["y"] = eff * d.cp + rng.normal(0, .15, len(d))
        t = ER.tw(d, "y"); o = ER.oneway(d, "y", "cp", "fe", "icpsr")
        out[str(eff)] = dict(twoway=[t["lo95"], t["hi95"]], oneway=[o["lo95"], o["hi95"]],
                             ok=bool(t["lo95"] <= eff <= t["hi95"] and o["lo95"] <= eff <= o["hi95"]))
    out["pass"] = all(v["ok"] for k, v in out.items() if k != "pass")
    json.dump(out, open(O / "synthetic.json", "w"), indent=1); print(out)
    if not out["pass"]: raise SystemExit("STOP: synthetic failed")


def main():
    rows, info = [], {}
    for m in MODELS:
        info[m] = dict(named=named(m, rows), votes=votes(m, rows)); print(m, info[m], flush=True)
    R = pd.DataFrame(rows)
    prim = R.quantity.isin(["H7", "H9", "Pcont_minus_P"]) & ~R.issue.isin(["economic"])
    R["p_holm"] = np.nan
    R.loc[prim, "p_holm"] = ER.holm(R[prim].copy(), ["model"]).p_holm
    R["reading"] = [reading(r) for r in R.itertuples()]; R["reading_old_rule"] = [reading_old(r) for r in R.itertuples()]
    for c in ("reading", "reading_old_rule"):
        R.loc[(R.model == "qwen") & R.issue.str.startswith("guns") & (R.task == "votes"), c] += " (Qwen not competent on guns: not interpreted)"
    R.to_csv(O / "results.csv", index=False); json.dump(info, open(O / "summary.json", "w"), indent=1)
    print(R[R.quantity.isin(["H7", "H", "H7_minus_H", "P_party_cont", "P_party", "Pcont_minus_P", "act_party", "H9", "H9_minus_H", "Pmid"])]
          [["model", "task", "issue", "quantity", "b", "lo95", "hi95", "mean_cp", "mean_aligned", "reading"]].round(4).to_string())


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--synthetic", action="store_true"); a = ap.parse_args()
    synthetic() if a.synthetic else main()
