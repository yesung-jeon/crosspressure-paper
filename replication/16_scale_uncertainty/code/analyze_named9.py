#!/usr/bin/env python
"""Named-member questions on the 1-9 scale (protocol/PROTOCOL_named9_2026-11-01.md). Same estimator and definitions as analyze.py
named() for the sealed 1-7 run; only the scale (9 digits, entropy / log2 9) and the input folder (out/named9) differ.
  python analyze_named9.py   -> ../out/results_named9.csv"""
import sys
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze as A  # noqa: E402  (dist, load, fit_row, ER = er_helpers; main() is guarded)


def member_frame(m, task="named9", n=9):
    """Member-Congress rows with the scale quantities. fail_share_x = binary (from rows_<m>), fail_share_y = this scale task."""
    df = A.load(task, m); mass, s, Hn, mid, top = A.dist(df, n)
    df = df.assign(mass=mass, s=s, H9=Hn, Pmid=mid, top=top >= 0.9)
    IT = {i["id"]: i for i in A.items()}
    R = pd.read_parquet(A.REP / f"15_named_member_uncertainty/analysis/data/rows_{m}.parquet")
    ok = df[df.mass >= 0.5].merge(R[["rid", "vote_q"]], on="rid", validate="many_to_one")
    ok["c"] = np.where([A.want_yes(IT[i], q) for i, q in zip(ok["item"], ok.vote_q)], ok.s, 1 - ok.s)
    g = ok.groupby("rid").agg(H9=("H9", "mean"), Pmid=("Pmid", "mean"), top=("top", "mean"), C_scale=("c", "mean"))
    g["fail_share"] = df.groupby("rid").mass.apply(lambda v: float((v < 0.5).mean()))
    d = R.merge(g.reset_index(), on="rid", how="inner", validate="one_to_one")
    d["H9_minus_H"] = d.H9 - d.H; d["Cs_minus_C"] = d.C_scale - d.C_vote
    return d, df


def named9(m, rows, task="named9", n=9):
    # task="named", n=7 is the code check: it must reproduce the sealed results.csv named rows exactly (check_named9.py)
    d, df = member_frame(m, task, n)
    for lab, x, sub in [("abortion (vote CP)", "vote_cp", d), ("abortion (map CP)", "map_crossed", d), ("guns (gun CP)", "gun_cp", d[d.gun_cp.notna()])]:
        for qty in ["H9", "H", "H9_minus_H", "Pmid", "top", "C_scale", "C_vote", "Cs_minus_C"]:
            A.fit_row(rows, m, "named9", lab, qty, A.ER.oneway(sub, qty, x, "fe", "icpsr"), sub, x, qty)
    return dict(rows=len(d), cell_fail_share=float((df.mass < 0.5).mean()), median_mass=float(np.median(df.mass)))


def main():
    rows, info = [], {}
    for m in A.MODELS:
        info[m] = named9(m, rows); print(m, info[m], flush=True)
    T = pd.DataFrame(rows); T["p_holm"] = np.nan
    prim = T.quantity.eq("H9")
    T.loc[prim, "p_holm"] = A.ER.holm(T[prim].copy(), ["model"]).p_holm
    T["reading"] = [("more uncertain" if r.b > 0 else "less uncertain") if r.quantity == "H9" and (r.lo95 > 0 or r.hi95 < 0) and r.p_holm < 0.05
                    else ("no difference detected" if r.quantity == "H9" else "") for r in T.itertuples()]
    T.to_csv(A.O / "results_named9.csv", index=False)
    pd.DataFrame(info).T.to_csv(A.O / "summary_named9.csv")
    print(T[T.quantity == "H9"][["model", "issue", "b", "lo95", "hi95", "p_holm", "reading"]].round(4).to_string())


if __name__ == "__main__":
    main()
