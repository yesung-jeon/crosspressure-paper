#!/usr/bin/env python
"""Study V amendment A12 (CPU): leave-one-roll-call-out CP (PROTOCOL 6.4(ii)), Qwen and Llama only.

For each main-sample roll call k, the abortion and economic scales of k's Congress x chamber are rebuilt without k (code of
01_rollcall_scales/00_data.py step 3, unchanged except for the exclusion), the paper's voting quadrants are recomputed by median splits
within the cell, and the 6.1 specification is re-estimated with cp_loo on the sealed order-averaged frames.
Gate: rebuilding without exclusion reproduces issue_scales.csv (max abs diff < 1e-9) and the v0 cp of all 10,444 rows.

  python 08_leave_one_out_cp.py            # baseline gate, labels, estimates for qwen and llama
"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd

V = Path(__file__).resolve().parents[1]; KIM = V.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(KIM / "00_shared"))
import shared_constants as cm  # noqa: E402  (SOUTH, as in 01_build_scales.py)
import estimate_votes as v5  # noqa: E402  (twoway: the 6.1 estimator)
import map_common as dc  # noqa: E402

MODELS = ["qwen", "llama"]                                           # A12 scope: two models; OLMo rows are not read
KEY = ["congress", "chamber", "rollnumber"]
DATA = KIM / "01_rollcall_scales" / "out" / "data"
O = V / "out" / "v6"; O.mkdir(parents=True, exist_ok=True)

# ---- inputs (as in 01_build_scales.py) ----
irc = pd.read_csv(DATA / "issue_rollcalls.csv")
irc = irc[irc.contested & irc.issue.isin(["economic", "abortion"]) & (irc.congress >= 93)]
want = set(map(tuple, irc[KEY].drop_duplicates().values))
parts = []
for ch in pd.read_csv(KIM / "data" / "voteview_all" / "HSall_votes.csv", usecols=["congress", "chamber", "rollnumber", "icpsr", "cast_code"],
                      chunksize=4_000_000, dtype={"congress": "int16", "rollnumber": "int32", "icpsr": "int32", "cast_code": "int8"}):
    ch = ch[ch.congress.between(93, 118)]
    if ch.empty: continue
    k = list(zip(ch.congress, ch.chamber, ch.rollnumber)); m = np.fromiter((x in want for x in k), bool, len(k))
    parts.append(ch[m])
votes = pd.concat(parts, ignore_index=True)
votes["v"] = np.where(votes.cast_code.between(1, 3), 1.0, np.where(votes.cast_code.between(4, 6), 0.0, np.nan))
votes = votes.merge(irc[KEY + ["issue"]], on=KEY, how="inner", validate="m:m")
mem = pd.read_csv(KIM / "data" / "HSall_members.csv", low_memory=False)
mem = mem[mem.chamber.isin(["House", "Senate"])][["congress", "chamber", "icpsr", "party_code", "state_abbrev", "nominate_dim1"]]
mem = mem.drop_duplicates(["congress", "chamber", "icpsr"])
VG = {k: g for k, g in votes.groupby(["congress", "chamber", "issue"])}


def scale(c, chm, iss, exclude=None):
    """01_build_scales.py step 3 for one cell; `exclude` = rollnumber left out. Returns Series rc_score by icpsr, or None if not built."""
    g = VG.get((c, chm, iss))
    if g is None: return None
    if exclude is not None: g = g[g.rollnumber != exclude]
    M = g.pivot_table(index="icpsr", columns="rollnumber", values="v", aggfunc="first")
    M = M[M.notna().sum(1) >= 3]
    if M.shape[1] < 3 or len(M) < 20: return None
    X = M.values; mu = np.nanmean(X, 0); Z = np.where(np.isnan(X), 0.0, X - mu)
    U, S, Vt = np.linalg.svd(Z, full_matrices=False); sc = U[:, 0] * S[0]
    mm = pd.DataFrame({"icpsr": M.index, "score": sc}).merge(mem[(mem.congress == c) & (mem.chamber == chm)], on="icpsr", how="left", validate="1:1")
    ok = mm.nominate_dim1.notna()
    r1 = np.corrcoef(mm.score[ok], mm.nominate_dim1[ok])[0, 1] if ok.sum() > 10 else np.nan
    dem = mm[mm.party_code == 100]; sdem = dem.state_abbrev.isin(cm.SOUTH)
    if np.isfinite(r1) and abs(r1) >= 0.3: sign = np.sign(r1)
    elif sdem.sum() >= 5 and (~sdem).sum() >= 5: sign = np.sign(dem.score[sdem.values].mean() - dem.score[~sdem.values].mean()) or 1.0
    else: sign = np.sign(r1) if np.isfinite(r1) and r1 != 0 else 1.0
    return pd.Series(np.round(sign * sc, 10), index=M.index)          # tie rule (author 2026-10-23): as 01_build_scales.py


# ---- paper rows (01_select_rollcalls.py step 1) ----
quad = lambda x, y: pd.Series(np.where(x > 0, "ER-", "EL-"), index=x.index) + np.where(y > 0, "ST", "SP")
sc0 = pd.read_csv(dc.ISSUE_SCALES); sc0 = sc0[sc0.issue.isin(["economic", "abortion"])]
w = sc0.pivot_table(index=["congress", "chamber", "icpsr"], columns="issue", values="rc_score").reset_index()
mp = pd.read_csv(dc.OUT / "qwen" / "s3" / "temporal_member_scores.csv")
mp["cc"] = mp.congress.astype(str) + mp.chamber
rows = mp.merge(w, on=["congress", "chamber", "icpsr"], how="left", validate="one_to_one")
rows = rows[(rows.congress >= 93) & rows.party.isin(["Democrat", "Republican"])].dropna(subset=["economic", "abortion"]).copy()
assert len(rows) == 10444, len(rows)


def cp_of(r, econ, abort):
    """median split within the cell on the given scores (aligned to r.icpsr); NaN where a score is missing"""
    e = r.icpsr.map(econ); a = r.icpsr.map(abort); ok = e.notna() & a.notna()
    he = e > e[ok].median(); ha = a > a[ok].median()
    q = quad(he.astype(int) - 0.5, ha.astype(int) - 0.5)
    return pd.Series(np.where(ok, q.isin(["EL-ST", "ER-SP"]).astype(float), np.nan), index=r.index)


# ---- gate: rebuild without exclusion ----
gate = dict(cells=0, max_abs_diff=0.0, cp_mismatch=0)
rows["cp_base"] = np.nan
for (c, chm), r in rows.groupby(["congress", "chamber"]):
    se, sa = scale(c, chm, "economic"), scale(c, chm, "abortion")
    for iss, s in [("economic", se), ("abortion", sa)]:
        ref = sc0[(sc0.congress == c) & (sc0.chamber == chm) & (sc0.issue == iss)].set_index("icpsr").rc_score
        d = (s.reindex(ref.index) - ref).abs()
        assert d.notna().all() and len(s) == len(ref), (c, chm, iss)
        gate["max_abs_diff"] = max(gate["max_abs_diff"], float(d.max())); gate["cells"] += 1
    rows.loc[r.index, "cp_base"] = cp_of(r, se, sa)
quad0 = quad((rows.economic > rows.groupby("cc").economic.transform("median")).astype(int) - 0.5,
             (rows.abortion > rows.groupby("cc").abortion.transform("median")).astype(int) - 0.5)
cp0 = quad0.isin(["EL-ST", "ER-SP"]).astype(float)
gate["cp_mismatch"] = int((rows.cp_base != cp0).sum())
gate["pass"] = bool(gate["max_abs_diff"] < 1e-9 and gate["cp_mismatch"] == 0)
dc.atomic_json(gate, O / "baseline_check.json"); print("gate", gate)
if not gate["pass"]: raise SystemExit("STOP: baseline gate failed")

# ---- leave-one-out labels for every predicted main roll call ----
F = {m: pd.read_parquet(V / "out" / "v5" / f"frame_v2_{m}_abortion_economic.parquet") for m in MODELS}
keys = sorted(set(F["qwen"].key) | set(F["llama"].key))
lab = []
for k in keys:
    c, chm, rn = k.split("|"); c, rn = int(c), int(rn)
    r = rows[(rows.congress == c) & (rows.chamber == chm)]
    se, sa = scale(c, chm, "economic", exclude=rn), scale(c, chm, "abortion", exclude=rn)
    if se is None or sa is None:
        lab.append(pd.DataFrame(dict(key=k, icpsr=r.icpsr.values, cp_loo=np.nan, scale_built=False))); continue
    lab.append(pd.DataFrame(dict(key=k, icpsr=r.icpsr.values, cp_loo=cp_of(r, se, sa).values, scale_built=True)))
lab = pd.concat(lab, ignore_index=True)
assert not lab.duplicated(["key", "icpsr"]).any()
lab.to_parquet(O / "loo_labels.parquet", index=False)

# ---- estimates ----
SEALED = {m: json.load(open(V / "out" / "v5" / f"estimates_v2_{m}_abortion_economic.json")) for m in MODELS}
for m in MODELS:
    d = F[m].merge(lab, on=["key", "icpsr"], how="left", validate="one_to_one")
    res = dict(model=m, amendment="A12", by_issue={})
    for iss, g in d.groupby("issue"):
        sealed_name = "accuracy (6.1 preferred)" if iss == "abortion" else "accuracy"
        rec = v5.twoway(g.assign(y=g.correct_avg))
        s = SEALED[m]["by_issue"][iss]["regressions"][sealed_name]
        gl = g[g.cp_loo.notna()]
        res["by_issue"][iss] = dict(
            n=int(len(g)), n_loo=int(len(gl)), dropped_rows=int(g.cp_loo.isna().sum()),
            cells_not_built=int(g[~g.scale_built.fillna(False).astype(bool)].key.nunique()),
            share_cp_changed=round(float((gl.cp != gl.cp_loo).mean()), 4),
            cp_share=dict(sealed=round(float(g.cp.mean()), 4), loo=round(float(gl.cp_loo.mean()), 4)),
            sealed_6_1=dict(b=s["b"], ci95=s["ci95"]), reproduced_6_1=dict(b=rec["b"], abs_diff=abs(rec["b"] - s["b"])),
            loo_6_1=v5.twoway(gl.assign(cp=gl.cp_loo, y=gl.correct_avg)),
            sealed_cp_on_loo_rows=v5.twoway(gl.assign(y=gl.correct_avg)),
            party_rule_loo=v5.twoway(gl.assign(cp=gl.cp_loo, y=gl.party_correct)))
        assert res["by_issue"][iss]["reproduced_6_1"]["abs_diff"] < 1e-10, (m, iss)
    dc.atomic_json(res, O / f"loo_cp_{m}.json"); print(json.dumps(res, indent=1, default=str))
