#!/usr/bin/env python
"""Build paper/appendix_values.json: numbers printed only in the appendix that are not headline rows. Each value is read here from a
named package output file (written by the pipeline and covered by validation/SEAL.json) and formatted with the same rules as
values.py. No number is typed in this file. build.py merges these keys with values.json and gives this file to the numeric gate.

Keys start with AP_. Model suffixes: _Q (Qwen), _L (Llama).
Usage: python paper/appendix_values.py   -> paper/appendix_values.json"""
import csv, json
from pathlib import Path

P = Path(__file__).resolve().parent; R = P.parent
MS = {"Q": "qwen", "L": "llama"}
V = {}


def f(x, d=3):
    v = float(x)
    if v == round(v) and abs(v) >= 1: return f"{int(round(v)):,}"
    s = f"{v:.{d}f}"
    return s.replace("-", "−") if s.startswith("-") else s


def J(rel):
    return json.load(open(R / rel, encoding="utf-8"))


def put(key, value, src):
    if key in V: raise KeyError(f"duplicate key {key}")
    V[key] = {"value": value, "source": [src]}


def num(key, x, src, d=3):
    put(key, f(x, d), src)


def interval(key, lohi, src, d=3):
    put(key, f"[{f(lohi[0], d)}, {f(lohi[1], d)}]", src)


# ---- Appendix A: data and measurement
rep = "01_rollcall_scales/out/data/data_report.json"; D = J(rep)
num("AP_RC_VOTEVIEW", D["voteview_rollcalls_80_118"], rep)
num("AP_PAP_MATCH", D["pap_match_rate"], rep)
for iss, k in (("abortion", "AB"), ("economic", "ECON")):
    num(f"AP_RC_{k}", D["issue_rollcalls"][iss]["all"], rep)
    num(f"AP_RC_{k}_CONTESTED", D["issue_rollcalls"][iss]["contested"], rep)
    num(f"AP_SCALES_{k}", D["scales_built"][iss], rep)
g0 = "05_gun_scale/out/g0/report.json"; G = J(g0)
num("AP_GUN_CANDIDATES", G["candidates_contested"], g0)
num("AP_GUN_INCLUDED", G["included"], g0)
num("AP_GUN_AUTHOR", G["label_source"]["author"], g0)
num("AP_GUN_AGREED", G["label_source"]["agreed"], g0)
num("AP_GUN_CELLS", G["cells_built"], g0)
num("AP_GUN_CELLS_PASSED", G["cells_passed"], g0)
num("AP_GUN_CP_SHARE", G["gun_cp_share"], g0)
num("AP_GUN_CORR_AB", G["overlap_with_abortion_cp"]["corr_gun_abortion"], g0)
num("AP_GUN_SAME_LABEL", G["overlap_with_abortion_cp"]["same_label_share"], g0)

ms = "02_ideology_map/out/qwen/s3/temporal_member_scores.csv"
rows = list(csv.DictReader(open(R / ms, encoding="utf-8")))
num("AP_N_MC", len(rows), ms)
num("AP_N_HOUSE", sum(r["chamber"] == "House" for r in rows), ms)
num("AP_N_SENATE", sum(r["chamber"] == "Senate" for r in rows), ms)
num("AP_N_MEMBERS", len({r["icpsr"] for r in rows}), ms)

anc = "02_ideology_map/out/s4/anchors.json"; A = J(anc)
for s, m in MS.items():
    num(f"AP_RECOG_{s}", A[m]["recall"], anc)
    num(f"AP_R_X_DW1_80_{s}", A[m]["r_x_dim1_80"], anc)
    num(f"AP_R_X_DW1_118_{s}", A[m]["r_x_dim1_118"], anc)
    rule = f"02_ideology_map/out/{m}/rule.json"; RU = J(rule)
    num(f"AP_BEST_ECON_{s}", RU["axis_best"]["economic"], rule)
    num(f"AP_BEST_SOC_{s}", RU["axis_best"]["social"], rule)
    for ax, k in (("economic", "ECON"), ("social", "SOC")):
        j1 = f"02_ideology_map/out/{m}/s2/J1_{ax}.json"
        num(f"AP_J1_{k}_{s}", J(j1)["auc"], j1)

for tag, src in (("AB", "02_ideology_map/out/s4/vote_vs_map.json"), ("GUN", "02_ideology_map/out/s4_guns/vote_vs_map.json")):
    VM = J(src)["qwen"]
    num(f"AP_QN_{tag}", VM["n"], src)
    for q, conf in VM["confusion_vote_rows_map_cols"].items():
        num(f"AP_QN_{q.replace('-', '')}_{tag}", sum(conf.values()), src)

# ---- Appendix B: history
con = "10_polarization_history/out/t0/contrasts.json"; C = J(con)
dw = C["qwen"]["main"]["dw1"]
num("AP_DW_DGAP", dw["dgap"], con); interval("AP_DW_DGAP_CI", dw["ci"]["dgap"], con)
num("AP_DW_CHANGE_D", dw["dD"], con); interval("AP_DW_CHANGE_D_CI", dw["ci"]["dD"], con)
num("AP_DW_CHANGE_R", dw["dR"], con); interval("AP_DW_CHANGE_R_CI", dw["ci"]["dR"], con)
sub = "10_polarization_history/out/t0/subgroups.csv"
for r in csv.DictReader(open(R / sub, encoding="utf-8")):
    if r["axis"] == "chamber" and r["pair"] == "x-dw1":
        s = {v: k for k, v in MS.items()}[r["model"]]; ch = r["cell"].upper()
        num(f"AP_CH_{ch}_DIFF_{s}", r["dgap_diff"], sub); interval(f"AP_CH_{ch}_DIFF_{s}_CI", (r["dgap_diff_lo"], r["dgap_diff_hi"]), sub)
        num(f"AP_CH_{ch}_SHARE_D_{s}", r["share_D_model"], sub)
        num(f"AP_CH_{ch}_SHARE_D_DW", r["share_D_dw"], sub) if s == "Q" else None
        num(f"AP_CH_{ch}_EARLY_{s}", r["early_ratio"], sub); interval(f"AP_CH_{ch}_EARLY_{s}_CI", (r["early_ratio_lo"], r["early_ratio_hi"]), sub)
n1 = "11_nominate_benchmarks/out/n1.json"; N1 = J(n1)
for s, m in MS.items():
    for party in ("Democrat", "Republican"):
        x = N1[m]["spans"]["86-113"]["reading"][party]
        num(f"AP_N1_{party.upper()}_86_113_{s}", x["diff"], n1); interval(f"AP_N1_{party.upper()}_86_113_{s}_CI", x["diff_ci"], n1)
num("AP_N1_ROWS", N1["qwen"]["rows"], n1)

# ---- Appendix C: placing members
for tag, src in (("AB", "16_supplementary_checks/members_by_era/members_by_era.json"),
                 ("GUN", "16_supplementary_checks/members_by_era/members_by_era_guns.json")):
    E = J(src)["rows"]
    for s, m in MS.items():
        for dec, x in E[m]["by_decade"].items():
            num(f"AP_ERA_{tag}_{dec}_ALIGNED_{s}", x["recall_aligned"], src)
            num(f"AP_ERA_{tag}_{dec}_CROSS_{s}", x["recall_cross"], src)
            num(f"AP_ERA_{tag}_{dec}_NCROSS", x["n_cross"], src) if s == "Q" else None
for tag, sfx in (("AB", ""), ("GUN", "_guns")):   # noise benchmark (council 2026-10-25 B2): main = independent noise, matched = map x-y correlation
    nb = f"16_supplementary_checks/noise_benchmark/noise_benchmark{sfx}.json"; NB = J(nb)
    for s, m in MS.items():
        for c, k in (("recall_cross", "CROSS"), ("recall_aligned", "ALIGNED"), ("same_econ_share", "DEST")):
            num(f"AP_NOISE_{tag}_{k}_OBS_{s}", NB[m]["observed"][c], nb)
            for v_, vk in (("main", ""), ("matched", "_MATCHED")):
                x = NB[m][v_][c]
                num(f"AP_NOISE_{tag}_{k}{vk}_{s}", x["mean"], nb); interval(f"AP_NOISE_{tag}_{k}{vk}_{s}_CI", (x["lo"], x["hi"]), nb)
    num(f"AP_NOISE_DRAWS", NB["draws"], nb) if tag == "AB" else None
br = "16_supplementary_checks/benchmark/benchmark_recall.json"; B = J(br)
for s, m in MS.items():
    num(f"AP_RECOG_ALIGNED_AB_{s}", B["N2_recognized"][m]["recognition_rate"]["aligned"], br)
    num(f"AP_RECOG_CROSS_AB_{s}", B["N2_recognized"][m]["recognition_rate"]["cross_pressured"], br)
np_ = "16_supplementary_checks/no_persona/no_persona_package_effect.json"; NP = J(np_)
for s, m in MS.items():
    x = NP[m]["interval_2026_10_18"]
    num(f"AP_NOPERSONA_{s}", x["est"], np_); interval(f"AP_NOPERSONA_{s}_CI", x["ci95_pigeonhole"], np_)
for s, m in MS.items():
    bf = f"04_bundled_choices/out/{m}/RESULTS.json"; BU = J(bf)
    num(f"AP_BUNDLE_MASS_{s}", BU["mean_mass"], bf)
    p1 = BU["blockD_flips_party_like_H"]["tests"]["P1_Dp_minus_placebo"]
    num(f"AP_STEER_P1_{s}", p1["est"], bf); interval(f"AP_STEER_P1_{s}_CI", p1["ci95"], bf)

# ---- Appendix D: votes
for s, m in MS.items():
    gf = f"06_vote_prediction/out/g2/estimates_{m}.json"; GE = J(gf)
    num(f"AP_GUN_ORDER_CORR_{s}", GE["corr_two_orders"], gf)
    interval(f"AP_GUN_ACC_ALIGNED_{s}_CI", GE["competence"]["aligned_accuracy_ci95"], gf)
    num(f"AP_GUN_PRED_YEA_{s}", GE["descriptive"]["share_pred_yea"]["0"], gf)
    if s == "Q":
        num("AP_GUN_PRED_RC", GE["rollcalls"], gf)
        num("AP_GUN_PRED_RC_SCALE", GE["gun_cp_loo"]["rollcalls"], gf)
        num("AP_GUN_PRED_RC_OUTSIDE", GE["rollcalls"] - GE["gun_cp_loo"]["rollcalls"], gf + " (rollcalls minus gun_cp_loo.rollcalls)")
    lf = f"06_vote_prediction/out/v6/loo_cp_{m}.json"
    num(f"AP_LOO_CHANGED_{s}", J(lf)["by_issue"]["abortion"]["share_cp_changed"], lf)
    ef = f"06_vote_prediction/out/v6/error_direction_{m}.json"; ED = J(ef)["results"]["M1|abortion|pred_avg"]
    for g, k in (("cp=1", "CP"), ("cp=0", "ALIGNED")):
        num(f"AP_ERRDIR_{k}_AB_{s}", ED[g]["toward_party_among_wrong"], ef)
        interval(f"AP_ERRDIR_{k}_AB_{s}_CI", ED[g]["ci95"]["toward_party_among_wrong"], ef)
num("AP_GUN_ACTUAL_YEA", J("06_vote_prediction/out/g2/estimates_qwen.json")["descriptive"]["share_actual_yea"]["0"],
    "06_vote_prediction/out/g2/estimates_qwen.json")
ac = "06_vote_prediction/out/v1/AUTHOR_CHECK.md"   # descriptions the authors read (abortion and economic), one "## N." section each
num("AP_AUTHOR_READ_AB_ECON", sum(1 for l in open(R / ac, encoding="utf-8") if l.startswith("## ") and l[3:4].isdigit()), ac)
gc = "06_vote_prediction/out/g2/AUTHOR_DESC_CHECK.csv"   # gun descriptions the authors read, one row each
num("AP_AUTHOR_READ_GUN", len(list(csv.DictReader(open(R / gc, encoding="utf-8-sig")))), gc)
dj = "12_speech_and_state/out/d/d.json"; DJ = J(dj)
for s, m in MS.items():
    x = DJ[m]["D3_W1"]["abortion"]["senate_only"]
    num(f"AP_D3_SENATE_{s}", x["b"], dj); interval(f"AP_D3_SENATE_{s}_CI", x["ci95"], dj)
    # D2: map coordinates on state lean, holding the member's own roll-call scale and Nokken-Poole scores constant
    for c, k in (("x", "X"), ("y", "Y")):
        x = DJ[m]["D2"]["pooled"][c]
        num(f"AP_D2_{k}_{s}", x["b"], dj); interval(f"AP_D2_{k}_{s}_CI", x["ci95"], dj)
        num(f"AP_D2_{k}_SD_{s}", DJ[m]["D2_scale"][f"{c}_lean_per_within_sd"], dj)
# D1 (vote-defined labels only, so the same for both models)
x = DJ["qwen"]["D1"]["pooled"]["cp_on_out_lean"]
num("AP_D1_B", x["b"], dj); interval("AP_D1_B_CI", x["ci95"], dj); num("AP_D1_ROWS", x["n"], dj)
ct = DJ["qwen"]["D1"]["crosstab_rows"]
num("AP_D1_CP", ct["cp1_ccp0"] + ct["cp1_ccp1"], dj + " (crosstab cp1_ccp0 + cp1_ccp1)")
num("AP_D1_OVERLAP", ct["cp1_ccp1"], dj)
num("AP_D1_CCP", ct["cp0_ccp1"] + ct["cp1_ccp1"], dj + " (crosstab cp0_ccp1 + cp1_ccp1)")
n2 = "11_nominate_benchmarks/out/n2.json"; N2 = J(n2)
num("AP_GMP_CP", N2["qwen"]["gmp_by_cp"]["cp_coef"]["b"], n2); interval("AP_GMP_CP_CI", N2["qwen"]["gmp_by_cp"]["cp_coef"]["ci95"], n2)

# ---- Appendix E: entropy cells counted in Section 7 that have no values.py key (read from the validated headline table)
hv = "validation/headline_values.csv"
H = {(x["study"], x["model"], x["issue"], x["quantity"]): x for x in csv.DictReader(open(R / hv, encoding="utf-8"))}
for s, m in MS.items():
    for q, k in (("Q2gun", "GUN"), ("Q2ab_same_rows", "GUN_ABDEF")):
        x = H[("named entropy", m, "guns", q)]
        num(f"AP_NAMED_{k}_{s}", x["estimate"], hv); interval(f"AP_NAMED_{k}_{s}_CI", (x["lower95"], x["upper95"]), hv)
import pandas as pd  # only for the named-member rows file
for s, m in MS.items():
    nr = f"09_named_member_entropy/analysis/data/rows_{m}.parquet"
    num(f"AP_NAMED_FAIL_{s}", pd.read_parquet(R / nr, columns=["fail_share"]).fail_share.mean(), nr + " (mean of fail_share)")

# ---- Appendix F: mechanism and speech
x1 = "15_mechanism/out/x1/RESULTS.json"; X1 = J(x1)
x3 = "15_mechanism/out/x3/RESULTS.json"; X3 = J(x3)
x4 = "15_mechanism/out/x4/RESULTS.json"; X4 = J(x4)
x5 = "15_mechanism/out/x5/RESULTS_stageA.json"; X5 = J(x5)
s1 = "12_speech_and_state/out/s1/s1.json"; S1 = J(s1)
s2 = "12_speech_and_state/out/s2/s2.json"; S2 = J(s2)
num("AP_S1_SPEECH", S1["speech"]["share"], s1); interval("AP_S1_SPEECH_CI", S1["speech"]["share_ci"], s1)
num("AP_S1_DW", S1["qwen"]["series"]["dw1"]["share"], s1); interval("AP_S1_DW_CI", S1["qwen"]["series"]["dw1"]["share_ci"], s1)
num("AP_S2_ROWS", S2["qwen"]["with_p"], s2)
for s, m in MS.items():
    p = X1["A_map"][m]["primary"]
    num(f"AP_X1_D_{s}", p["est"]["d"], x1); interval(f"AP_X1_D_{s}_CI", p["ci95"]["d"], x1)
    num(f"AP_X1_ECON_PULL_{s}", p["est"]["econ_pull"], x1); interval(f"AP_X1_ECON_PULL_{s}_CI", p["ci95"]["econ_pull"], x1)
    num(f"AP_X1_PARTY_PULL_{s}", p["est"]["party_pull"], x1); interval(f"AP_X1_PARTY_PULL_{s}_CI", p["ci95"]["party_pull"], x1)
    p = X3["models"][m]["primary"]
    num(f"AP_X3_B_{s}", p["est"]["b"], x3); interval(f"AP_X3_B_{s}_CI", p["ci95"]["b"], x3)
    p = X4["models"][m]["primary"]
    num(f"AP_X4_B_{s}", p["b_per_sd"], x4); interval(f"AP_X4_B_{s}_CI", p["ci95"], x4)
    num("AP_X4_PAIRS", p["n_pairs"], x4) if s == "Q" else None
    p = X5["models"][m]["Democrat"]["primary"]
    num(f"AP_X5_DEMOCRAT_{s}", p["r"], x5); interval(f"AP_X5_DEMOCRAT_{s}_CI", p["ci95"], x5)
    x5s = "15_mechanism/out/x5/SENS_threeway.json"
    for party in ("Democrat", "Republican"):
        p = J(x5s)["stageA"][m][party]
        num(f"AP_X5_3W_{party.upper()}_{s}", p["r"], x5s); interval(f"AP_X5_3W_{party.upper()}_{s}_CI", p["ci95"], x5s)
    num(f"AP_S1_X_{s}", S1[m]["series"]["x"]["share"], s1); interval(f"AP_S1_X_{s}_CI", S1[m]["series"]["x"]["share_ci"], s1)
    b = S2[m]["S2b_cp_rows"]
    num(f"AP_S2B_{s}", b["b"], s2); interval(f"AP_S2B_{s}_CI", b["ci95"], s2)
    c = S2[m]["S2c_toward_party_on_p"]
    num(f"AP_S2C_{s}", c["b"], s2); interval(f"AP_S2C_{s}_CI", c["ci95"], s2)

json.dump(V, open(P / "appendix_values.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(f"appendix_values.json: {len(V)} keys")
