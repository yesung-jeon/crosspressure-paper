#!/usr/bin/env python
"""N1 (PROTOCOL.md): continuing-member vs replacement decomposition on the models' economic axis and on Nokken-Poole dim1, with a
member-cluster bootstrap; plus the T0 full-range contrast with NP dim1 in place of DW dim1. Two models.
  python nokken_poole.py --synthetic   # decomposition check on a planted panel
  python nokken_poole.py               -> out/n1.json
"""
import argparse, json, sys
from pathlib import Path
import numpy as np, pandas as pd

R = Path(__file__).resolve().parents[1]; KIM = R.parent                   # replication/ (rebuild)
sys.path.insert(0, str(KIM / "02_ideology_map" / "code"))
import map_common as dc  # noqa: E402
O = R / "out"; O.mkdir(parents=True, exist_ok=True)
SPANS = {"81-118": (81, 118), "86-113": (86, 113)}
W0, W1 = range(80, 86), range(113, 119)
B = 1000


def prep(d, v):
    """pairs of consecutive Congresses for the same member, chamber and party, and cell (congress, chamber, party) indices"""
    z = d[["congress", "chamber", "party", "icpsr", v]].rename(columns={v: "z"}).copy()
    nxt = z.assign(congress=z.congress - 1).rename(columns={"z": "z_next"})
    pr = z.merge(nxt, on=["congress", "chamber", "party", "icpsr"])          # member present in c and c+1
    pr["t"] = pr.congress + 1                                                   # transition into Congress t
    return z, pr


def decompose(z, pr, wz, wp, span):
    """within and replacement sums (chambers equal weight per transition) for each party; weights = member bootstrap weights"""
    lo, hi = span; out = {}
    for p in ["Democrat", "Republican"]:
        within = total = 0.0
        for t in range(lo, hi + 1):
            parts = []
            for ch in ["House", "Senate"]:
                a = (z.congress == t - 1) & (z.chamber == ch) & (z.party == p); b = (z.congress == t) & (z.chamber == ch) & (z.party == p)
                if not a.any() or not b.any(): continue
                wa, wb = wz[a.values], wz[b.values]
                if wa.sum() == 0 or wb.sum() == 0: continue
                tot = np.average(z.z[b].values, weights=wb) - np.average(z.z[a].values, weights=wa)
                s = (pr.t == t) & (pr.chamber == ch) & (pr.party == p); ws = wp[s.values]
                wi = np.average(pr.z_next[s].values - pr.z[s].values, weights=ws) if ws.sum() > 0 else 0.0
                parts.append((wi, tot))
            if parts:
                within += np.mean([q[0] for q in parts]); total += np.mean([q[1] for q in parts])
        out[p] = dict(within=within, replacement=total - within, total=total)
    return out


def index(z, pr):
    """cell indices (congress, chamber, party) for rows and (t, chamber, party) for pairs, built once for the bootstrap"""
    mz = {k: i for i, k in enumerate(sorted(set(zip(z.congress, z.chamber, z.party))))}
    mp = {k: i for i, k in enumerate(sorted(set(zip(pr.t, pr.chamber, pr.party))))}
    return dict(mz=mz, mp=mp, cz=np.array([mz[k] for k in zip(z.congress, z.chamber, z.party)]),
                cp=np.array([mp[k] for k in zip(pr.t, pr.chamber, pr.party)]), zv=z.z.values, dv=(pr.z_next - pr.z).values)


def decompose_fast(ix, wz, wp, span):
    """same quantity as decompose() from weighted cell sums (bincount); 2026-10-23: decompose() rebuilt row masks for every cell and
    draw, so N1's 1,000-draw bootstrap had not finished one model after 70 minutes. run_model asserts the two agree."""
    nz, npr = len(ix["mz"]), len(ix["mp"])
    Wz = np.bincount(ix["cz"], wz, nz); Sz = np.bincount(ix["cz"], wz * ix["zv"], nz)
    Wp = np.bincount(ix["cp"], wp, npr); Sp = np.bincount(ix["cp"], wp * ix["dv"], npr)
    lo, hi = span; out = {}
    for p in ["Democrat", "Republican"]:
        within = total = 0.0
        for t in range(lo, hi + 1):
            parts = []
            for ch in ["House", "Senate"]:
                a, b = ix["mz"].get((t - 1, ch, p)), ix["mz"].get((t, ch, p))
                if a is None or b is None or Wz[a] == 0 or Wz[b] == 0: continue
                tot = Sz[b] / Wz[b] - Sz[a] / Wz[a]
                s = ix["mp"].get((t, ch, p)); wi = Sp[s] / Wp[s] if s is not None and Wp[s] > 0 else 0.0
                parts.append((wi, tot))
            if parts:
                within += np.mean([q[0] for q in parts]); total += np.mean([q[1] for q in parts])
        out[p] = dict(within=within, replacement=total - within, total=total)
    return out


def same(o1, o2, tol=1e-9):
    return all(abs(o1[p][k] - o2[p][k]) < tol for p in o1 for k in o1[p])


def run_model(m):
    d = pd.read_csv(dc.OUT / m / "s3" / "temporal_member_scores.csv")
    hs = pd.read_csv(KIM / "data" / "HSall_members.csv", low_memory=False)[["congress", "chamber", "icpsr", "nokken_poole_dim1"]]
    assert not hs.duplicated(["congress", "chamber", "icpsr"]).any()   # assert instead of drop_duplicates (Codex 2026-10-23)
    d = d[d.party.isin(["Democrat", "Republican"])].merge(hs, on=["congress", "chamber", "icpsr"], how="left", validate="one_to_one")
    n_dr = len(d); n_missing = int(d.nokken_poole_dim1.isna().sum()); d = d.dropna(subset=["nokken_poole_dim1"]).reset_index(drop=True)
    d["x"] = -d.econ_orth; d["x"] = d.x / d.x.std(ddof=0); d["np1"] = d.nokken_poole_dim1 / d.nokken_poole_dim1.std(ddof=0)
    res = dict(model=m, dr_rows_before_drop=n_dr, rows=len(d), np_missing_rows=n_missing, bootstrap_draws=B, spans={})
    mem = d.party + "|" + d.icpsr.astype(str); ids, inv = np.unique(mem.values, return_inverse=True)
    party_of = np.array([s.split("|")[0] for s in ids]); groups = {p: np.where(party_of == p)[0] for p in ["Democrat", "Republican"]}
    rng = np.random.default_rng(dc.seed_for("N1", m) % 2**32)
    draws_w = []
    for _ in range(B):
        w = np.zeros(len(ids))
        for p, g in groups.items(): w[g] = np.bincount(rng.integers(0, len(g), len(g)), minlength=len(g))
        draws_w.append(w)
    for var in ["x", "np1"]:
        z, pr = prep(d, var)
        zi = (z.party + "|" + z.icpsr.astype(str)).map({s: i for i, s in enumerate(ids)}).values
        pi = (pr.party + "|" + pr.icpsr.astype(str)).map({s: i for i, s in enumerate(ids)}).values
        for sn, sp in SPANS.items():
            ix = index(z, pr)
            pt = decompose(z, pr, np.ones(len(z)), np.ones(len(pr)), sp)
            chk = [(pt, decompose_fast(ix, np.ones(len(z)), np.ones(len(pr)), sp))] + \
                  [(decompose(z, pr, w[zi], w[pi], sp), decompose_fast(ix, w[zi], w[pi], sp)) for w in draws_w[:3]]
            assert all(same(a, b) for a, b in chk)
            dmax = max(abs(a[p][k] - b[p][k]) for a, b in chk for p in a for k in a[p])
            res["fast_vs_reference_max_abs"] = max(res.get("fast_vs_reference_max_abs", 0.0), float(dmax))
            bs = [decompose_fast(ix, w[zi], w[pi], sp) for w in draws_w]
            res["spans"].setdefault(sn, {})[var] = dict(point=pt, draws={p: [b[p]["within"] for b in bs] for p in pt})
    for sn in SPANS:
        S = res["spans"][sn]; S["reading"] = {}
        for p in ["Democrat", "Republican"]:
            mx, npd = np.array(S["x"]["draws"][p]), np.array(S["np1"]["draws"][p])
            ci = lambda a: [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]
            S["reading"][p] = dict(model_within=S["x"]["point"][p]["within"], model_within_ci=ci(mx), np_within=S["np1"]["point"][p]["within"],
                                   np_within_ci=ci(npd), diff=S["x"]["point"][p]["within"] - S["np1"]["point"][p]["within"], diff_ci=ci(mx - npd))
            r = S["reading"][p]; r["drift_specific_to_model"] = bool(r["model_within_ci"][1] < 0 and r["diff_ci"][1] < 0)
        for v in ["x", "np1"]: del S[v]["draws"]
    for sn in SPANS:                                                            # descriptive (not registered): party gap R - D
        for v in ["x", "np1"]:
            pt = res["spans"][sn][v]["point"]
            res["spans"][sn][v]["gap_R_minus_D"] = {k: pt["Republican"][k] - pt["Democrat"][k] for k in ["within", "replacement", "total"]}
    # T0 full-range contrast with NP dim1 in place of DW dim1: T0's own contrast() (point estimates, W0 80-85 -> W1 113-118). The T0
    # sample (all D/R rows) reproduces T0's sealed x and dw1 values; NP dim1 and the common-sample x/dw1 use the rows with NP scores.
    t0 = load_t0()
    full, _ = t0.load(m); F = t0.Frame(full)
    sdv = lambda e, v: float(e[v].std(ddof=0))
    res["t0_contrast"] = {"t0_sample": {v: t0.contrast(F, full[v].values, np.ones(len(full)), t0.W0, t0.W1, sdv(full, v)) for v in ["x", "dw1"]}}
    cs = full.merge(d[["congress", "chamber", "icpsr", "nokken_poole_dim1"]], on=["congress", "chamber", "icpsr"], how="inner", validate="one_to_one")
    cs["np1"] = cs.nokken_poole_dim1; G = t0.Frame(cs.reset_index(drop=True))
    res["t0_contrast"]["np_sample"] = {v: t0.contrast(G, cs[v].values, np.ones(len(cs)), t0.W0, t0.W1, sdv(cs, v)) for v in ["x", "dw1", "np1"]}
    S = res["t0_contrast"]["np_sample"]
    res["t0_contrast"]["early_ratio"] = {"x/dw1": S["x"]["early_s2"] / S["dw1"]["early_s2"], "x/np1": S["x"]["early_s2"] / S["np1"]["early_s2"]}
    res["t0_contrast"] = json.loads(json.dumps(res["t0_contrast"], default=float))
    return res


def load_t0():
    import importlib.util
    spec = importlib.util.spec_from_file_location("party_history", KIM / "10_polarization_history" / "code" / "party_history.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod


def synthetic():
    """planted panel: members keep their score (no within change) while entry/exit shifts Democrats; then add a common drift to all
    members' scores. Within must be 0 in the first case and equal the drift in the second; total unchanged by construction otherwise."""
    rows = []
    for c in range(80, 100):
        for p, base in [("Democrat", -1.0), ("Republican", 1.0)]:
            for i in range(30):
                mid = (c - 80) // 5 * 100 + i                         # cohorts replaced every 5 Congresses
                shift = -0.05 * ((c - 80) // 5) if p == "Democrat" else 0.0
                rows.append(dict(congress=c, chamber="House", party=p, icpsr=mid + (0 if p == "Democrat" else 10**6), v=base + shift))
    d = pd.DataFrame(rows); z, pr = prep(d, "v")
    o1 = decompose(z, pr, np.ones(len(z)), np.ones(len(pr)), (81, 99))
    d2 = d.assign(v=d.v - 0.01 * (d.congress - 80)); z2, pr2 = prep(d2, "v")
    o2 = decompose(z2, pr2, np.ones(len(z2)), np.ones(len(pr2)), (81, 99))
    out = dict(no_drift=o1, drift=o2, fast_agrees=bool(same(o1, decompose_fast(index(z, pr), np.ones(len(z)), np.ones(len(pr)), (81, 99)))
                                                       and same(o2, decompose_fast(index(z2, pr2), np.ones(len(z2)), np.ones(len(pr2)), (81, 99)))))
    # Expected values: 19 transitions, of which 3 (into 85, 90, 95) replace every member, so they have no continuing members and the
    # common drift of those 3 transitions is counted as replacement: within = 16 x -0.01 = -0.16; Republican replacement -0.03;
    # Democratic replacement -0.15 - 0.03 = -0.18. (The first run expected within -0.19, an error in the expected value, not the code.)
    out["pass"] = bool(out["fast_agrees"] and abs(o1["Democrat"]["within"]) < 1e-12 and abs(o1["Democrat"]["replacement"] + 0.15) < 1e-9
                       and abs(o2["Republican"]["within"] + 0.16) < 1e-9 and abs(o2["Democrat"]["within"] + 0.16) < 1e-9
                       and abs(o2["Republican"]["replacement"] + 0.03) < 1e-9 and abs(o2["Democrat"]["replacement"] + 0.18) < 1e-9)
    dc.atomic_json(out, O / "synthetic_n1.json"); print(out)
    if not out["pass"]: raise SystemExit("STOP: synthetic failed")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--synthetic", action="store_true"); a = ap.parse_args()
    if a.synthetic: synthetic()
    else:
        res = {m: run_model(m) for m in ["qwen", "llama"]}
        dc.atomic_json(res, O / "n1.json")
        for m, r in res.items():
            for sn, S in r["spans"].items():
                print(m, sn, {p: (round(v["model_within"], 3), round(v["np_within"], 3), [round(x, 3) for x in v["diff_ci"]], v["drift_specific_to_model"])
                              for p, v in S["reading"].items()}, flush=True)
            for smp in ["t0_sample", "np_sample"]:
                print(m, "t0 contrast", smp, {k: {kk: round(vv, 3) for kk, vv in v.items()} for k, v in r["t0_contrast"][smp].items()}, flush=True)
            print(m, "early ratio", {k: round(v, 3) for k, v in r["t0_contrast"]["early_ratio"].items()}, flush=True)
