#!/usr/bin/env python
"""T0 (PROTOCOL_T0.md): party trajectories, gap growth and observed party shares in the models' map coordinates vs DW-NOMINATE.
Two models (qwen, llama). Member-cluster bootstrap with member weights (members resampled within party).

  python party_history.py --synthetic     # checks on planted maps
  python party_history.py                 # full run
"""
import argparse, hashlib, json, sys
from pathlib import Path
import numpy as np, pandas as pd

T = Path(__file__).resolve().parents[1]; KIM = T.parent
sys.path.insert(0, str(KIM / "02_ideology_map" / "code"))
import map_common as dc  # noqa: E402

MODELS = ["qwen", "llama"]
O = T / "out" / "t0"; O.mkdir(parents=True, exist_ok=True)
SOUTH = {"AL", "AR", "FL", "GA", "LA", "MS", "NC", "SC", "TN", "TX", "VA"}   # 00_shared/common.py SOUTH
W0, W1 = list(range(80, 86)), list(range(113, 119))
ERAS = {"80-92": list(range(80, 93)), "93-100": list(range(93, 101)), "101-108": list(range(101, 109)), "109-118": list(range(109, 119))}
STARTS = {"80-83": list(range(80, 84)), "80-85": W0, "80-87": list(range(80, 88))}
ENDS = {"113-118": W1, "115-118": list(range(115, 119)), "116-118": list(range(116, 119))}
PAIRS = [("x", "dw1"), ("y", "dw2")]
B = 2000


def load(m):
    d = pd.read_csv(dc.OUT / m / "s3" / "temporal_member_scores.csv")
    hs = pd.read_csv(KIM / "data" / "HSall_members.csv", low_memory=False)[["congress", "chamber", "icpsr", "nominate_dim1", "nominate_dim2"]]
    j = d.merge(hs.drop_duplicates(["congress", "chamber", "icpsr"]), on=["congress", "chamber", "icpsr"], how="left", validate="one_to_one")
    assert float((j.dim1 - j.nominate_dim1).abs().max()) == 0 and float((j.dim2 - j.nominate_dim2).abs().max()) == 0, m
    info = dict(rows=int(len(d)), other_party_rows=int((~d.party.isin(["Democrat", "Republican"])).sum()), dw_missing=int(d.dim1.isna().sum()))
    d = d[d.party.isin(["Democrat", "Republican"])].copy()
    d["x"], d["y"], d["dw1"], d["dw2"] = -d.econ_orth, -d.social_orth, d.dim1, d.dim2
    return d.reset_index(drop=True), info


class Frame:
    """index structures for weighted party means by Congress (chambers equally weighted) and within-cell SDs"""
    def __init__(self, d):
        self.d = d
        self.cong = np.sort(d.congress.unique()); ci = {c: i for i, c in enumerate(self.cong)}
        self.ch = d.chamber.map({"House": 0, "Senate": 1}).values; self.pr = (d.party == "Republican").astype(int).values
        self.ci = d.congress.map(ci).values
        self.cell = (self.ci * 2 + self.ch) * 2 + self.pr                    # congress x chamber x party
        self.cc = self.ci * 2 + self.ch                                       # congress x chamber
        self.nc = len(self.cong)
        mk = d.party + "|" + d.icpsr.astype(str); self.mem, self.mi = np.unique(mk.values, return_inverse=True)
        self.mparty = np.array([s.split("|")[0] for s in self.mem])

    def means(self, v, w):
        """party mean by Congress: cell means, then chambers averaged (equal weight) where present. returns (nc, 2)"""
        n = self.nc * 4
        sw = np.bincount(self.cell, w, n); sx = np.bincount(self.cell, w * v, n)
        cm = np.where(sw > 0, sx / np.where(sw > 0, sw, 1), np.nan).reshape(self.nc, 2, 2)   # congress, chamber, party
        return np.nanmean(cm, axis=1)

    def cell_gap_s2(self, v, w):
        """gap / within-cell SD per Congress x chamber; chambers averaged. returns (nc,)"""
        n = self.nc * 4
        sw = np.bincount(self.cell, w, n); sx = np.bincount(self.cell, w * v, n)
        cm = np.where(sw > 0, sx / np.where(sw > 0, sw, 1), np.nan).reshape(self.nc, 2, 2)
        n2 = self.nc * 2
        cw = np.bincount(self.cc, w, n2); cx = np.bincount(self.cc, w * v, n2); cxx = np.bincount(self.cc, w * v * v, n2)
        mu = cx / np.where(cw > 0, cw, 1); sd = np.sqrt(np.maximum(cxx / np.where(cw > 0, cw, 1) - mu ** 2, 0)).reshape(self.nc, 2)
        g = (cm[:, :, 1] - cm[:, :, 0]) / np.where(sd > 0, sd, np.nan)
        return np.nanmean(g, axis=1)

    def win(self, arr, cs):
        idx = [i for i, c in enumerate(self.cong) if c in cs]
        return np.nanmean(arr[idx], axis=0)


def contrast(F, v, w, s0, s1, sd1):
    pm = F.means(v, w) / sd1
    a, b = F.win(pm, s0), F.win(pm, s1)
    dD, dR = b[0] - a[0], b[1] - a[1]; dg = dR - dD
    return dict(dD=dD, dR=dR, dgap=dg, share_D=-dD / dg if dg != 0 else np.nan, share_R=dR / dg if dg != 0 else np.nan,
                early_s2=float(F.win(F.cell_gap_s2(v, w), s0)))


def stats(F, d, s0, s1, w0=None):
    """point estimates and bootstrap draws for x, y, dw1, dw2 and model - DW differences"""
    w = np.ones(len(d)) if w0 is None else w0
    sd = {v: float(np.sqrt(np.average((d[v] - np.average(d[v], weights=w)) ** 2, weights=w))) for v in ["x", "y", "dw1", "dw2"]}
    pt = {v: contrast(F, d[v].values, w, s0, s1, sd[v]) for v in sd}
    rng = np.random.default_rng(dc.seed_for("T0", len(d), s0[0], s1[-1]) % 2**32)
    draws = {v: [] for v in sd}
    groups = {p: np.where(F.mparty == p)[0] for p in ["Democrat", "Republican"]}
    for _ in range(B):
        mw = np.zeros(len(F.mem))
        for p, ids in groups.items():
            mw[ids] = np.bincount(rng.integers(0, len(ids), len(ids)), minlength=len(ids))
        rw = mw[F.mi] * w
        for v in sd: draws[v].append(contrast(F, d[v].values, rw, s0, s1, sd[v]))
    return pt, {v: pd.DataFrame(draws[v]) for v in sd}


def ci(s):
    s = np.asarray(s, float); s = s[np.isfinite(s)]
    return [float(np.percentile(s, 2.5)), float(np.percentile(s, 97.5))] if len(s) else [np.nan, np.nan]


def pval(s, null=0.0):
    s = np.asarray(s, float); s = s[np.isfinite(s)]
    if not len(s): return np.nan
    return float(min(1.0, 2 * min((s <= null).mean(), (s >= null).mean())))


def summarize(pt, dr):
    out = {}
    for v in pt:
        e = pt[v]; D = dr[v]
        judged = bool(not (ci(D.dgap)[0] <= 0 <= ci(D.dgap)[1]) and abs(e["dgap"]) >= 0.25)
        out[v] = dict({k: float(e[k]) for k in e}, ci={k: ci(D[k]) for k in e}, share_judged=judged,
                      dgap_sign_flip_share=float((np.sign(D.dgap) != np.sign(e["dgap"])).mean()))
    for a, b in PAIRS:
        Da, Db = dr[a], dr[b]
        out[f"{a}-{b}"] = dict(dgap=float(pt[a]["dgap"] - pt[b]["dgap"]), dgap_ci=ci(Da.dgap - Db.dgap), dgap_p=pval(Da.dgap - Db.dgap),
                              share_D=float(pt[a]["share_D"] - pt[b]["share_D"]), share_D_ci=ci(Da.share_D - Db.share_D),
                              share_D_p=pval(Da.share_D - Db.share_D),
                              early_ratio=float(pt[a]["early_s2"] / pt[b]["early_s2"]), early_ratio_ci=ci(Da.early_s2 / Db.early_s2))
        out[f"{a}-{b}"]["reading_a_gap_differs"] = bool(not (out[f"{a}-{b}"]["dgap_ci"][0] <= 0 <= out[f"{a}-{b}"]["dgap_ci"][1]))
        out[f"{a}-{b}"]["reading_c_little_early"] = bool(out[f"{a}-{b}"]["early_ratio"] < 0.5 and out[f"{a}-{b}"]["early_ratio_ci"][1] < 1)
        out[a]["reading_b_D_majority"] = bool(out[a]["share_judged"] and out[a]["ci"]["share_D"][0] > 0.5)
    return out


def trajectories(F, d, m):
    rows = []
    for v in ["x", "y", "dw1", "dw2"]:
        sd = float(d[v].std(ddof=0)); pm = F.means(d[v].values, np.ones(len(d))) / sd; s2 = F.cell_gap_s2(d[v].values, np.ones(len(d)))
        for i, c in enumerate(F.cong):
            rows.append(dict(model=m, var=v, congress=int(c), mean_D=pm[i, 0], mean_R=pm[i, 1], gap_s1=pm[i, 1] - pm[i, 0], gap_s2=s2[i]))
    return rows


SPANS = {"81-118 (all transitions)": range(81, 119), "86-113 (from the end of W0 to the start of W1)": range(86, 114)}


def decomposition(d, m):
    """party-mean change between consecutive Congresses = stayers' change + replacement, per chamber, summed over transitions.
    Weightings: 'equal' = the two chambers weighted equally within a transition; 'obs' = chambers weighted by members in the later
    Congress. Transitions are summed with equal weight in both. Spans: all transitions (80->118) and the transitions between the two
    windows (85->113); the second was added after the Codex verification (2026-10-22), which noted the PROTOCOL asked for W0 -> W1."""
    out = []
    for v in ["x", "y", "dw1", "dw2"]:
        sd = float(d[v].std(ddof=0)); z = d.assign(z=d[v] / sd)
        for p in ["Democrat", "Republican"]:
          for span, rng_c in SPANS.items():
            tot = {"equal": dict(within=0.0, replacement=0.0), "obs": dict(within=0.0, replacement=0.0)}
            for c in rng_c:
                parts = []
                for chm in ["House", "Senate"]:
                    a = z[(z.congress == c - 1) & (z.chamber == chm) & (z.party == p)].set_index("icpsr").z
                    b = z[(z.congress == c) & (z.chamber == chm) & (z.party == p)].set_index("icpsr").z
                    if a.empty or b.empty: continue
                    st = a.index.intersection(b.index)
                    within = float(b[st].mean() - a[st].mean()) if len(st) else 0.0
                    total = float(b.mean() - a.mean())
                    parts.append((within, total - within, len(b)))
                if not parts: continue
                for k, (wi, re, n) in [("equal", (np.mean([q[0] for q in parts]), np.mean([q[1] for q in parts]), 1))]:
                    tot[k]["within"] += wi; tot[k]["replacement"] += re
                nn = sum(q[2] for q in parts)
                tot["obs"]["within"] += sum(q[0] * q[2] for q in parts) / nn; tot["obs"]["replacement"] += sum(q[1] * q[2] for q in parts) / nn
            for k in tot:
                out.append(dict(model=m, var=v, party=p, span=span, weighting=k, within_members=tot[k]["within"],
                                replacement=tot[k]["replacement"], total=tot[k]["within"] + tot[k]["replacement"]))
    return out


def holm(p):
    p = np.asarray(p, float); n = len(p); o = np.argsort(p); adj = np.empty(n); run = 0.0
    for r, i in enumerate(o):
        run = max(run, min(1.0, (n - r) * p[i])); adj[i] = run
    return adj


def subgroups(d, m):
    rows = []
    def add(axis, cell, sub, s0, s1):
        if sub.empty or sub.congress.isin(s0).sum() == 0 or sub.congress.isin(s1).sum() == 0: return
        sub = sub.reset_index(drop=True); F = Frame(sub); pt, dr = stats(F, sub, s0, s1); sm = summarize(pt, dr)
        for a, b in PAIRS:
            r = sm[f"{a}-{b}"]
            rows.append(dict(model=m, axis=axis, cell=cell, pair=f"{a}-{b}", n_rows=len(sub), dgap_model=sm[a]["dgap"], dgap_dw=sm[b]["dgap"],
                             dgap_diff=r["dgap"], dgap_diff_lo=r["dgap_ci"][0], dgap_diff_hi=r["dgap_ci"][1], dgap_diff_p=r["dgap_p"],
                             share_D_model=sm[a]["share_D"], share_D_model_lo=sm[a]["ci"]["share_D"][0], share_D_model_hi=sm[a]["ci"]["share_D"][1],
                             share_judged=sm[a]["share_judged"], share_D_dw=sm[b]["share_D"], share_D_p_vs_half=pval(dr[a].share_D, 0.5),
                             early_ratio=r["early_ratio"], early_ratio_lo=r["early_ratio_ci"][0], early_ratio_hi=r["early_ratio_ci"][1]))
    for e, cs in ERAS.items(): add("era", e, d[d.congress.isin(cs)], cs[:3], cs[-3:])
    for chm in ["House", "Senate"]: add("chamber", chm, d[d.chamber == chm], W0, W1)
    add("region", "South", d[d.state.isin(SOUTH)], W0, W1); add("region", "non-South", d[~d.state.isin(SOUTH)], W0, W1)
    add("known", "known", d[d.known.astype(bool)], W0, W1)
    for sn, s0 in STARTS.items():
        for en, s1 in ENDS.items():
            if (sn, en) != ("80-85", "113-118"): add("window", f"{sn}|{en}", d, s0, s1)
    s = pd.DataFrame(rows)
    for (ax, pair), g in s.groupby(["axis", "pair"]):              # family = quantity x axis
        s.loc[g.index, "dgap_diff_p_holm"] = holm(g.dgap_diff_p.values)
        s.loc[g.index, "share_D_p_holm"] = holm(g.share_D_p_vs_half.fillna(1).values)
    return s


def synthetic():
    rng = np.random.default_rng(1); rows = []
    for c in range(80, 119):
        for chm, n in [("House", 60), ("Senate", 20)]:
            for p in ["Democrat", "Republican"]:
                for i in range(n):
                    base = -0.02 * (c - 80) if p == "Democrat" else 0.0
                    rows.append(dict(congress=c, chamber=chm, party=p, icpsr=(p == "Republican") * 100000 + (chm == "Senate") * 10000 + i, state="OH", known=1,
                                     x=base + rng.normal(0, .1), y=rng.normal(0, .1), dw1=base + rng.normal(0, .1), dw2=rng.normal(0, .1)))
    d = pd.DataFrame(rows); F = Frame(d)
    global B
    b0 = B; B = 200
    pt, dr = stats(F, d, W0, W1)
    d2 = d.copy(); d2["x"] = d2.x + 0.03 * (d2.congress - 80)                # common shift for both parties
    pt2, _ = stats(Frame(d2), d2, W0, W1)
    B = b0
    out = dict(share_D_planted=1.0, share_D=float(pt["x"]["share_D"]), dgap=float(pt["x"]["dgap"]),
               common_shift_share_D=float(pt2["x"]["share_D"]), common_shift_dgap=float(pt2["x"]["dgap"]))
    sd1, sd2 = d.x.std(ddof=0), d2.x.std(ddof=0)
    out["dgap_unchanged_raw_units"] = bool(abs(pt["x"]["dgap"] * sd1 - pt2["x"]["dgap"] * sd2) < 1e-9)
    out["pass"] = bool(abs(out["share_D"] - 1) < 0.05 and out["dgap_unchanged_raw_units"] and abs(out["common_shift_share_D"] - 1) > 0.5)
    dc.atomic_json(out, O / "synthetic.json"); print(out)
    if not out["pass"]: raise SystemExit("STOP: synthetic failed")


def main():
    traj, contrasts, dec, subs = [], {}, [], []
    for m in MODELS:
        d, info = load(m); F = Frame(d)
        traj += trajectories(F, d, m)
        pt, dr = stats(F, d, W0, W1)
        contrasts[m] = dict(info=info, n_dr_rows=int(len(d)), main=summarize(pt, dr))
        dec += decomposition(d, m)
        subs.append(subgroups(d, m))
        print(m, json.dumps(contrasts[m]["main"]["x-dw1"]), flush=True)
    pd.DataFrame(traj).to_csv(O / "trajectories.csv", index=False)
    pd.DataFrame(dec).to_csv(O / "decomposition.csv", index=False)
    pd.concat(subs).to_csv(O / "subgroups.csv", index=False)
    dc.atomic_json(contrasts, O / "contrasts.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--synthetic", action="store_true"); a = ap.parse_args()
    synthetic() if a.synthetic else main()
