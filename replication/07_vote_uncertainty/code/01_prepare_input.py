"""W1 uncertainty (PROTOCOL.md): per-vote binary entropy of the YEA/NAY prediction, from the order-averaged frames of this run's
06_vote_prediction/v5 (rebuild 2026-10-23: the FP8-era sha256 assertion against RELEASE_SEAL_2026-10-21b.json is replaced by recording the
frames' sha256 in data/input_sha256.json). Prints only counts, ranges and missing values (never entropy by cp).
Output: data/w1_uncertainty_input.parquet (one row per model x member vote). Usage: python -I prepare.py"""
import hashlib, json
from pathlib import Path
import numpy as np, pandas as pd

H = Path(__file__).resolve().parents[1]; V = H.parent / "06_vote_prediction"   # H = study folder (this file is in code/)
seal = {}
COLS = ["pid", "key", "icpsr", "party", "issue", "cp", "fe", "known", "format_fail", "share_yf", "share_nf", "share_avg", "correct_avg"]


def hbits(p):
    p = np.clip(np.asarray(p, dtype=float), 1e-12, 1 - 1e-12)
    return -(p * np.log2(p) + (1 - p) * np.log2(1 - p))


out = []
for m in ["qwen", "llama"]:
    rel = f"out/v5/frame_v2_{m}_abortion_economic.parquet"; f = V / rel
    seal[rel] = hashlib.sha256(f.read_bytes()).hexdigest()
    d = pd.read_parquet(f, columns=COLS)
    assert not d.pid.duplicated().any() and len(d) == 102285, (m, len(d))
    assert d.party.isin(["Democrat", "Republican"]).all() and d.cp.isin([0, 1]).all()
    d = d[~d.format_fail].copy()
    d["H"] = (hbits(d.share_yf) + hbits(d.share_nf)) / 2
    d["H_yf"], d["H_nf"], d["H_avg"] = hbits(d.share_yf), hbits(d.share_nf), hbits(d.share_avg)
    d["model"] = m; d["wrong"] = (d.correct_avg == 0).astype(int)
    for c in ["H", "H_yf", "H_nf", "H_avg"]:
        assert d[c].between(0, 1).all() and d[c].notna().all(), (m, c)
    out.append(d)
    print(f"{m}: rows {len(d)} (format failures dropped {102285 - len(d)}); by issue {d.issue.value_counts().to_dict()}; "
          f"H range [{d.H.min():.3f}, {d.H.max():.3f}]; missing known {int(d.known.isna().sum())}")
# Rebuild PROTOCOL_GUNSYM (author 2026-10-24): the same rows for the G2 gun votes, as two cells per model: issue "guns" with the paper's
# abortion CP (as the abortion and economic cells) and issue "guns_gcp" with the gun-defined CP (gun_cp_loo; rows with a gun label).
for m in ["qwen", "llama"]:
    rel = f"out/g2/frame_{m}.parquet"; f = V / rel; seal[rel] = hashlib.sha256(f.read_bytes()).hexdigest()
    g = pd.read_parquet(f, columns=COLS + ["gun_cp_loo"])
    assert not g.pid.duplicated().any() and g.party.isin(["Democrat", "Republican"]).all()
    g = g[~g.format_fail].copy()
    g["H"] = (hbits(g.share_yf) + hbits(g.share_nf)) / 2
    g["H_yf"], g["H_nf"], g["H_avg"] = hbits(g.share_yf), hbits(g.share_nf), hbits(g.share_avg)
    g["model"] = m; g["wrong"] = (g.correct_avg == 0).astype(int)
    a = g.drop(columns=["gun_cp_loo"]).assign(issue="guns")
    b = g[g.gun_cp_loo.notna()].assign(issue="guns_gcp", cp=lambda x: x.gun_cp_loo.astype(int)).drop(columns=["gun_cp_loo"])
    out += [a, b]
    print(f"{m} guns: rows {len(a)} (abortion CP), {len(b)} with a gun-defined CP label")
D = pd.concat(out, ignore_index=True)
D["party_dem"] = (D.party == "Democrat").astype(int)
D["known"] = D.known.fillna(0).astype(int)
(H / "data").mkdir(exist_ok=True)
D.drop(columns=["format_fail", "pid"]).to_parquet(H / "data" / "w1_uncertainty_input.parquet", index=False)
json.dump({"inputs_sha256": seal}, open(H / "data" / "input_sha256.json", "w"), indent=1)
print("written data/w1_uncertainty_input.parquet", len(D), "rows")
