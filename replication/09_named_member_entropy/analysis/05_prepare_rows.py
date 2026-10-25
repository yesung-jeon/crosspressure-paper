"""Study N analysis input (PROTOCOL §4): one row per analysis row (member-Congress) per model, from the [B] parts and the [A] map.
Prints counts and format-failure shares only (never a value by cross-pressure).
Usage: python prepare.py --model qwen [--fake]   (--fake: random probabilities on the real rows, to test the analysis code; written
to data_fake/)  ->  data/rows_<m>.parquet"""
import argparse, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
from named_common import dc, OUT, MAPOUT, analysis_rows, items, want_yes, hbits, CROSS  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True); ap.add_argument("--fake", action="store_true"); a = ap.parse_args()
H = Path(__file__).resolve().parent; m = a.model
IT = {i["id"]: i for i in items()}
sealed_map = dc.OUT / m / "s3" / "temporal_member_scores.csv"
new_map = MAPOUT / m / "s3" / "temporal_member_scores.csv"
V = analysis_rows(sealed_map if a.fake else new_map)                      # vote_q, map_q (new map), zx, zy, known, party, cc
S = analysis_rows(sealed_map)[["rid", "map_q", "zx", "zy"]].rename(columns=lambda c: c if c == "rid" else c + "_sealed")
assert set(V.rid) == set(S.rid) and (V.set_index("rid").vote_q == analysis_rows(sealed_map).set_index("rid").vote_q).all()

if a.fake:   # random answers on the real design (code test only)
    rng = np.random.default_rng(7)
    B = pd.DataFrame([(r, i, o) for r in V.rid for i in IT for o in ("yn", "ny")], columns=["rid", "item", "order"])
    B["p_yes"] = rng.beta(0.6, 0.6, len(B)) * 0.98; B["p_no"] = 0.98 - B.p_yes
else:
    fs = sorted((OUT / m / "yesno").glob("part_*.done"))
    B = pd.concat([pd.read_parquet(f.with_suffix(".parquet"), columns=["rid", "item", "order", "p_yes", "p_no"]) for f in fs], ignore_index=True)
assert len(B) == len(V) * 32 and not (B.rid + B["item"] + B.order).duplicated().any()
B["mass"] = B.p_yes + B.p_no; B["fail"] = B.mass < 0.5
B["p"] = B.p_yes / B.mass; B["Hc"] = hbits(B.p)
B = B.merge(V[["rid", "vote_q", "map_q"]], on="rid", validate="many_to_one")
wy = {(i, q): want_yes(IT[i], q) for i in IT for q in ["EL-SP", "ER-ST", "EL-ST", "ER-SP"]}
B["c_vote"] = np.where([wy[(i, q)] for i, q in zip(B["item"], B.vote_q)], B.p, 1 - B.p)
B["c_map"] = np.where([wy[(i, q)] for i, q in zip(B["item"], B.map_q)], B.p, 1 - B.p)
B["axis"] = B["item"].map(lambda i: IT[i]["type"])
ok = B[~B.fail]
agg = ok.groupby("rid").agg(H=("Hc", "mean"), C_vote=("c_vote", "mean"), C_map=("c_map", "mean"))
agg["H_yn"] = ok[ok.order == "yn"].groupby("rid").Hc.mean()
agg["H_econ"] = ok[ok.axis == "econ_only"].groupby("rid").Hc.mean(); agg["H_soc"] = ok[ok.axis == "soc_only"].groupby("rid").Hc.mean()
pv = ok.pivot_table(index=["rid", "item"], columns="order", values="p").dropna()      # entropy of the order-averaged p (sensitivity)
agg["H_avgp"] = pd.Series(hbits((pv.yn + pv.ny) / 2), index=pv.index).groupby("rid").mean()
agg["fail_share"] = B.groupby("rid").fail.mean()
D = V.merge(agg.reset_index(), on="rid", validate="one_to_one").merge(S, on="rid", validate="one_to_one")
i4 = pd.read_csv(dc.OUT / "s5" / "i4_members.csv")
D["i4"] = (D.congress.astype(str) + "|" + D.icpsr.astype(str)).isin(i4.congress.astype(str) + "|" + i4.icpsr.astype(str)).astype(int)
D["vote_cp"] = D.vote_q.isin(CROSS).astype(int)
for suf in ("", "_sealed"):
    D[f"map_crossed{suf}"] = D[f"map_q{suf}"].isin(CROSS).astype(int)
    D[f"depth{suf}"] = np.minimum(D[f"zx{suf}"].abs(), D[f"zy{suf}"].abs()); D[f"conflict{suf}"] = D[f"depth{suf}"] * D[f"map_crossed{suf}"]
    D[f"abs_zx{suf}"], D[f"abs_zy{suf}"] = D[f"zx{suf}"].abs(), D[f"zy{suf}"].abs(); D[f"zxzy{suf}"] = D[f"zx{suf}"] * D[f"zy{suf}"]
for q in CROSS:
    D[f"vote_{q.replace('-', '')}"] = (D.vote_q == q).astype(int); D[f"map_{q.replace('-', '')}"] = (D.map_q == q).astype(int)
# Rebuild PROTOCOL_GUNSYM (author 2026-10-24): the gun-defined vote quadrant (G0 gun_cp_rows: economic x gun median splits) on the rows that
# have a gun label, and the consistency of the answers with that quadrant (C_gun, same want_yes rule as C_vote). No rescoring.
gun = pd.read_csv(dc.KIM / "05_gun_scale" / "out" / "g0" / "gun_cp_rows.csv")[["congress", "chamber", "icpsr", "gun_q", "gun_cp"]]
D = D.merge(gun, on=["congress", "chamber", "icpsr"], how="left", validate="one_to_one")
bg = ok.merge(D[["rid", "gun_q"]].dropna(), on="rid", validate="many_to_one")
bg["c_gun"] = np.where([wy[(i, q)] for i, q in zip(bg["item"], bg.gun_q)], bg.p, 1 - bg.p)
D = D.merge(bg.groupby("rid").c_gun.mean().rename("C_gun").reset_index(), on="rid", how="left", validate="one_to_one")
D["party_dem"] = (D.party == "Democrat").astype(int); D["known"] = D.known.fillna(False).astype(bool).astype(int)
D["fe"] = D.party + "|" + D.cc; D["model"] = m
assert D[["H", "H_yn", "H_econ", "H_soc", "C_vote", "C_map"]].notna().all().all(), "a row lost every cell to format failures"
keep = ["model", "rid", "icpsr", "congress", "chamber", "cc", "party", "party_dem", "fe", "known", "i4", "vote_q", "vote_cp", "vote_ELST",
        "vote_ERSP", "map_q", "map_crossed", "map_ELST", "map_ERSP", "zx", "zy", "abs_zx", "abs_zy", "zxzy", "depth", "conflict",
        "map_crossed_sealed", "depth_sealed", "conflict_sealed", "H", "H_yn", "H_econ", "H_soc", "H_avgp", "C_vote", "C_map", "fail_share",
        "gun_q", "gun_cp", "C_gun"]
od = H / ("data_fake" if a.fake else "data"); od.mkdir(exist_ok=True)
D[keep].to_parquet(od / f"rows_{m}.parquet", index=False)
print(f"{m}{' (fake)' if a.fake else ''}: rows {len(D)}; item-order cells {len(B)}; format failures {B.fail.mean():.4f}; "
      f"rows with any failure {(D.fail_share > 0).mean():.4f}")
