#!/usr/bin/env python
"""S2 (PROTOCOL_S.md): member speech partisanship p (GST leave-out, own party) vs cross-pressure, map misplacement and W1 error direction.
  python 03_member_speech.py   -> out/s2/s2.json, member_p.csv
"""
import json, sys
import numpy as np, pandas as pd
from speech_common import O, S0, KIM, MAIN, dc, load_matrix
from speech_history import LO
import speech_estimators as est

sys.path.insert(0, str(KIM / "09_named_member_entropy" / "code"))
import named_common as nc  # noqa: E402
S2 = O / "s2"; S2.mkdir(parents=True, exist_ok=True)
MIN_TOKENS = 500


def member_p():
    rows, led = [], {}
    links = {ed: pd.read_csv(S0 / f"link_{ed}.csv", dtype={"speakerid": str}) for ed in ["bound", "daily"]}
    for c in range(93, 115):
        ed = MAIN[c]; X, spk = load_matrix(ed, c); rep = (spk.party == "R").values; _, p = LO(X, rep)()
        t = spk.drop(columns=["chamber"]).assign(p=p, tokens=np.asarray(X.sum(1)).ravel())   # chamber comes from the link (Voteview names)
        lk = links[ed][links[ed].congress == c]
        n_multi = int(lk.multi.sum()); lk = lk[~lk.multi]
        j = t.merge(lk[["speakerid", "icpsr", "chamber_v"]], on="speakerid", how="inner", validate="one_to_one")
        n_low = int((j.tokens < MIN_TOKENS).sum()); j = j[j.tokens >= MIN_TOKENS]
        dup = j.duplicated(["chamber_v", "icpsr"], keep=False); n_dup = int(dup.sum()); j = j[~dup]
        led[c] = dict(edition=ed, speakers=int(len(t)), linked=int(len(j) + n_low + n_dup), dropped_multi_match=n_multi,
                      dropped_low_tokens=n_low, dropped_duplicate_member=n_dup, kept=int(len(j)))
        rows.append(j.assign(congress=c).rename(columns={"chamber_v": "chamber"})[["congress", "chamber", "icpsr", "party", "p", "tokens"]])
    P = pd.concat(rows, ignore_index=True); P["icpsr"] = P.icpsr.astype(int)
    assert not P.duplicated(["congress", "chamber", "icpsr"]).any()
    return P, led


def main():
    P, led = member_p(); P.to_csv(S2 / "member_p.csv", index=False)
    res = dict(ledger=led, ledger_totals={k: sum(x[k] for x in led.values()) for k in ["speakers", "linked", "dropped_multi_match",
                                                                                        "dropped_low_tokens", "dropped_duplicate_member", "kept"]})
    for m in ["qwen", "llama"]:
        v = nc.analysis_rows(KIM / "02_ideology_map" / "out" / m / "s3" / "temporal_member_scores.csv")
        v = v[v.congress <= 114].copy(); n0 = len(v)
        v = v.merge(P[["congress", "chamber", "icpsr", "p", "party"]].rename(columns={"party": "sp_party"}), on=["congress", "chamber", "icpsr"],
                    how="left", validate="one_to_one")
        out = dict(paper_rows_93_114=n0, with_p=int(v.p.notna().sum()))
        v = v.dropna(subset=["p"]).copy()
        out["speech_party_agrees"] = float((v.sp_party == v.party.str[0]).mean())
        v["cp"] = v.vote_q.isin(["EL-ST", "ER-SP"]).astype(float); v["misplaced"] = (v.map_q != v.vote_q).astype(float)
        v["p_z"] = (v.p - v.p.mean()) / v.p.std(); v["fe"] = v.party + "|" + v.congress.astype(str) + "|" + v.chamber
        v["cp_x_p"] = v.cp * v.p_z
        s = lambda r, x: dict(b=r[x]["b"], ci95=r[x]["ci95"], n=r["_n"])
        out["S2a_p_on_cp"] = s(est.fe_ols(v, "p_z", ["cp"], "fe", "icpsr"), "cp")
        out["p_mean_by_cp"] = v.groupby("cp").p.mean().to_dict()
        out["S2b_cp_rows"] = s(est.fe_ols(v[v.cp == 1], "misplaced", ["p_z"], "fe", "icpsr"), "p_z")
        out["S2b_aligned_rows"] = s(est.fe_ols(v[v.cp == 0], "misplaced", ["p_z"], "fe", "icpsr"), "p_z")
        it = est.fe_ols(v, "misplaced", ["cp", "p_z", "cp_x_p"], "fe", "icpsr"); out["S2b_interaction"] = {x: s(it, x) for x in ["cp", "p_z", "cp_x_p"]}
        out["reading_RS2"] = bool(out["S2b_cp_rows"]["ci95"][0] > 0)
        # S2c: W1 abortion, CP members' wrong predictions with a party majority
        f = pd.read_parquet(KIM / "06_vote_prediction" / "out" / "v5" / f"frame_v2_{m}_abortion_economic.parquet")
        f = f[f.issue == "abortion"].copy(); kk = f.key.str.split("|", expand=True); f["congress"] = kk[0].astype(int); f["chamber"] = kk[1]
        f = f.merge(v[["congress", "chamber", "icpsr", "p_z"]], on=["congress", "chamber", "icpsr"], how="inner", validate="many_to_one")
        w = f[(f.cp == 1) & (f.correct_avg == 0) & f.party_yea_share.notna() & (f.party_yea_share != 0.5)].copy()
        w["toward"] = (w.pred_avg == (w.party_yea_share > 0.5).astype(int)).astype(float)
        out["S2c_toward_party_on_p"] = s(est.fe_ols(w, "toward", ["p_z"], "key", "icpsr"), "p_z"); out["S2c_toward_share"] = float(w.toward.mean())
        res[m] = out
        print(m, json.dumps({k: (round(x["b"], 4), [round(z, 4) for z in x["ci95"]]) for k, x in out.items() if isinstance(x, dict) and "b" in x}),
              "| RS2", out["reading_RS2"], flush=True)
    dc.atomic_json(res, S2 / "s2.json")


if __name__ == "__main__":
    main()
