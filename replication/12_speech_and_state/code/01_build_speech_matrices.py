#!/usr/bin/env python
"""S0 (PROTOCOL_S.md): per edition and Congress, filtered speaker x phrase count matrices (R/D speakers) and speaker-member links.
Resumable (one npz per Congress = done marker); RAM guard before each Congress.
  python 01_build_speech_matrices.py            -> out/s0/{edition}_{NNN}.npz, _speakers.csv, _phrases.txt; link_{edition}.csv; ledger_s0.json
  python 01_build_speech_matrices.py --gate     -> gate L: links equal the sealed 01_rollcall_scales/out/speech/link_*.csv on their Congresses
"""
import argparse, json, time
import numpy as np, pandas as pd
import psutil
from speech_common import S0, EDITIONS, PROC, MIN_SPEAKERS, MIN_COUNT, KIM, read_bar, speaker_map, voteview, link
S0.mkdir(parents=True, exist_ok=True)


def matrix(ed, c, sm):
    sp = sm.drop_duplicates("speakerid")[["speakerid", "party", "chamber", "state", "lastname", "firstname"]]
    sp = sp[sp.party.isin(["R", "D"])]
    b = read_bar(ed, f"byspeaker_2gram_{c:03d}.txt", dtype={"speakerid": str, "phrase": str, "count": "int64"})
    n_raw = len(b)
    b = b[b.speakerid.isin(sp.speakerid) & b.phrase.notna() & ~b.phrase.str.contains(r"\d", regex=True)]
    st = b.groupby("phrase").agg(n_spk=("speakerid", "nunique"), tot=("count", "sum"))
    keep = st[(st.n_spk >= MIN_SPEAKERS) & (st.tot >= MIN_COUNT)].index
    b = b[b.phrase.isin(keep)]
    spk = pd.Index(sorted(b.speakerid.unique())); ph = pd.Index(sorted(keep))
    from scipy import sparse
    X = sparse.csr_matrix((b["count"].values, (spk.get_indexer(b.speakerid), ph.get_indexer(b.phrase))), shape=(len(spk), len(ph)))
    X.sum_duplicates()
    assert (spk.get_indexer(b.speakerid) >= 0).all() and (ph.get_indexer(b.phrase) >= 0).all()
    proc = np.array([p in PROC for p in ph])
    np.savez_compressed(S0 / f"{ed}_{c:03d}.npz", data=X.data, indices=X.indices, indptr=X.indptr, shape=np.array(X.shape), proc=proc)
    sp.set_index("speakerid").loc[spk].rename_axis("speakerid").reset_index().to_csv(S0 / f"{ed}_{c:03d}_speakers.csv", index=False)
    (S0 / f"{ed}_{c:03d}_phrases.txt").write_text("\n".join(ph), encoding="utf-8")
    return dict(rows_raw=int(n_raw), speakers=int(len(spk)), phrases=int(len(ph)), procedural_in_vocab=int(proc.sum()), nnz=int(X.nnz),
                tokens=int(X.sum()))


def main():
    V = voteview(); led_p = S0 / "ledger_s0.json"
    led = json.loads(led_p.read_text()) if led_p.exists() else {}
    for ed, cs in EDITIONS.items():
        links = []
        for c in cs:
            k = f"{ed}_{c:03d}"; sm = speaker_map(ed, c)
            lk, ll, multi = link(sm, V, c); links.append(lk.assign(multi=lk.speakerid.isin(multi)))
            if (S0 / f"{k}.npz").exists() and k in led: continue
            free = psutil.virtual_memory().available / 2**30
            if free < 3: raise SystemExit(f"STOP: only {free:.1f} GB free before {k}")
            t = time.time(); led[k] = dict(matrix(ed, c, sm), link=ll, seconds=round(time.time() - t, 1))
            led_p.write_text(json.dumps(led, indent=1)); print(k, led[k], flush=True)
        pd.concat(links, ignore_index=True).to_csv(S0 / f"link_{ed}.csv", index=False)
    print("S0 DONE", flush=True)


def gate():
    out = {}
    for ed in ["daily", "bound"]:
        old = pd.read_csv(KIM / "01_rollcall_scales" / "out" / "speech" / f"link_{ed}.csv", dtype={"speakerid": str})
        new = pd.read_csv(S0 / f"link_{ed}.csv", dtype={"speakerid": str})
        new = new[new.congress.isin(old.congress.unique())]
        cols = ["congress", "speakerid", "icpsr", "party", "party_code"]
        norm = lambda d: d[cols].astype({"congress": int, "icpsr": int, "party_code": int, "party": str}).sort_values(cols).reset_index(drop=True)
        a, b = norm(old), norm(new)
        out[ed] = dict(congresses=sorted(int(x) for x in old.congress.unique()), rows_old=len(a), rows_new=len(b),
                       identical=bool(len(a) == len(b) and (a.astype(str).values == b.astype(str).values).all()))
    led = json.loads((S0 / "ledger_s0.json").read_text())
    agree = [v["link"]["party_agreement"] for v in led.values()]
    out["mean_party_agreement"] = float(np.nanmean(agree)); out["min_party_agreement"] = float(np.nanmin(agree))
    out["pass"] = bool(all(out[e]["identical"] for e in ["daily", "bound"]) and out["mean_party_agreement"] >= 0.98)
    (S0 / "gate_L.json").write_text(json.dumps(out, indent=1))
    print(out)
    if not out["pass"]: raise SystemExit("STOP: gate L failed")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--gate", action="store_true"); a = ap.parse_args()
    gate() if a.gate else main()
