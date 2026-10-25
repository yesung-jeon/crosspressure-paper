#!/usr/bin/env python
"""Study M X1 main run (PLAN.md v0.1). Requires PRE_RUN_SEAL.json. CPU only.
Part A: map rows (three models). Part B1: S5 I4 named members (descriptive). Part B2: S5 I1, I2, I3, I5 (keep-economic share e).
Writes out/x1/RESULTS.json and destination tables."""
import json, time
import numpy as np, pandas as pd
import mech_common as xc

assert (xc.M / "protocol" / "PRE_RUN_SEAL.json").exists(), "run pre_seal.py first"
O = xc.M / "out" / f"x1{xc.TAG}"; O.mkdir(parents=True, exist_ok=True)
R = {"plan": "PLAN.md v0.1", "run": time.strftime("%Y-%m-%dT%H:%M"), "B": xc.B, "seed": xc.SEED,
     "rule": {"H-P": "d >= 0.65 and CI > 0.5", "H-E": "d <= 0.35 and CI < 0.5", "H-U": "CI within [0.40, 0.60]", "min_disc_members": xc.MIN_MEMBERS},
     "A_map": {}, "B1_I4": {}, "B2_no_party_modes": {}}
I4 = pd.read_csv(xc.dc.OUT / "s5" / "i4_members.csv")

for k, m in enumerate(xc.MODELS):
    v = xc.map_rows(m); xc.check_map_baseline(v, m)
    v["cl"] = v.icpsr; L = xc.label(v); xc.destinations(L).to_csv(O / f"destinations_{m}.csv", index=False)
    seed = lambda j: [xc.SEED, k, j]
    A = {"baseline_reproduced": True, "n_rows": int(len(v)), "n_cross_rows": int(len(L)), "miss_rate_cross": float(L.miss.mean()),
         "aligned_share_of_misses": float(L[L.miss].aligned_miss.mean()),
         "primary": xc.summarize(L, seed(0))}
    first = v.sort_values("congress").drop_duplicates("icpsr")
    A["sensitivity"] = {"S1_known_only": xc.summarize(L[L.known.astype(bool)], seed(1)),
                        "S2_first_congress_per_member": xc.summarize(xc.label(first), seed(2)),
                        "S3_house": xc.summarize(L[L.chamber == "House"], seed(3)), "S3_senate": xc.summarize(L[L.chamber == "Senate"], seed(4)),
                        "S4_all_misses_denominator": xc.summarize(L, seed(5), all_miss_den=True)}
    A["by_cell"] = {f"{p}|{q}": {"rows": int(len(g)), "members": int(g.icpsr.nunique()), "miss": float(g.miss.mean()),
                                 "own_share_of_aligned_misses": float(g[g.aligned_miss].own.mean()) if g.aligned_miss.any() else None,
                                 "opposite_cross_share_of_misses": float((g.miss & ~g.aligned_miss).sum() / max(g.miss.sum(), 1))}
                    for (p, q), g in L.groupby(["party", "vote_q"])}
    R["A_map"][m] = A

    # ---- S5 ----
    T = xc.s5_table(m); T.to_csv(O / f"s5_arrivals_{m}.csv", index=False)
    t4 = T[T["mode"] == "I4"].copy()
    t4["icpsr"] = t4.base.str.extract(r"m(\d+)c")[0].astype(int); t4["congress"] = t4.base.str.extract(r"c(\d+)$")[0].astype(int)
    t4 = t4.merge(I4[["congress", "icpsr", "party", "profile"]].rename(columns={"profile": "profile_i4"}), on=["congress", "icpsr"], how="left", validate="many_to_one")
    assert t4.party.notna().all() and (t4.profile == t4.profile_i4).all()
    c4 = t4[t4.profile.isin(xc.CROSS)].copy(); c4["miss"] = c4.arr_q != c4.profile; c4["aligned_miss"] = c4.miss & c4.arr_q.isin(xc.ALIGNED)
    c4["own"] = c4.arr_q == c4.party.map(xc.OWN)
    R["B1_I4"][m] = {f"{p}|{q}": {"n": int(len(g)), "miss": int(g.miss.sum()), "aligned_miss": int(g.aligned_miss.sum()), "own_party_landings": int((g.aligned_miss & g.own).sum()),
                                  "arrivals": g.arr_q.value_counts().to_dict()} for (p, q), g in c4.groupby(["party", "profile"])}
    t2 = T[T["mode"].isin(["I1", "I2", "I3", "I5"]) & T.profile.isin(xc.CROSS)].copy()
    t2["miss"] = t2.arr_q != t2.profile; t2["am"] = t2.miss & t2.arr_q.isin(xc.ALIGNED); t2["keep"] = t2.arr_q == t2.profile.map(xc.KEEP_ECON)
    a = t2[t2.am]; g = a.groupby("base").agg(k=("keep", "sum"), n=("keep", "size"))
    rng = np.random.default_rng([xc.SEED, k, 9]); nb = len(g); bs = np.empty(xc.B)
    for b in range(xc.B):
        w = np.bincount(rng.integers(0, nb, nb), minlength=nb); bs[b] = (w @ g.k.values) / (w @ g.n.values) if (w @ g.n.values) else np.nan
    e = float(a.keep.mean()) if len(a) else np.nan; ci = [float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))]
    R["B2_no_party_modes"][m] = {"n_cross_conditions": int(len(t2)), "misses": int(t2.miss.sum()), "aligned_misses": int(len(a)), "e_keep_economic": e, "ci95": ci,
                                 "n_bases": int(nb), "reading": ("keeps economic (H-E direction)" if ci[0] > 0.5 else "keeps social" if ci[1] < 0.5 else "0.5 not excluded"),
                                 "by_mode": {md: {"aligned_misses": int(len(gg)), "keep_econ": float(gg.keep.mean())} for md, gg in a.groupby("mode")}}

json.dump(R, open(O / "RESULTS.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
for m in xc.MODELS:
    p = R["A_map"][m]["primary"]
    print(f"{m}: d {p['est']['d']:.3f} {np.round(p['ci95']['d'], 3)} | c {p['est']['c']:.3f} | party pull {p['est']['party_pull']:+.3f} {np.round(p['ci95']['party_pull'], 3)}"
          f" | econ pull {p['est']['econ_pull']:+.3f} {np.round(p['ci95']['econ_pull'], 3)} | disc members {p['n_disc_members']} | {p['verdict']}")
    print("   sens:", {s: (round(x["est"]["d"], 3), x["verdict"]) for s, x in R["A_map"][m]["sensitivity"].items()})
    print("   B2 e:", round(R["B2_no_party_modes"][m]["e_keep_economic"], 3), np.round(R["B2_no_party_modes"][m]["ci95"], 3), R["B2_no_party_modes"][m]["aligned_misses"],
          "| B1:", {c: (x["aligned_miss"], x["own_party_landings"]) for c, x in R["B1_I4"][m].items()})
