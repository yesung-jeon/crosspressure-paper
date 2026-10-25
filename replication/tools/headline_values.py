#!/usr/bin/env python
"""Headline values: the estimates, intervals and verdicts that the manuscript and appendix report, read from the run's own outputs.

One row per (study, model, issue, quantity). The same rows feed the validation (tools/validate.py compares them with the sealed table
validation/headline_values.csv), the FP8 vs bf16 sensitivity report and the README result tables. Rows come from the ASSESSMENT files
of the original sealed studies (rebuild P5, 2026-10-24); the rows are fixed here, not chosen after looking at results. Social-issue
rows exist for abortion and guns wherever the gun version of the analysis exists (PROTOCOL_GUNSYM); cells that do not exist are listed
in NOT_APPLICABLE. A missing file or key is an error, never a silent skip.

Usage: python tools/headline_values.py [--root DIR] [--layout new|old] [--out FILE]
  --layout old reads a tree in the folder layout used before the 2026-10-24 rename (STUDY_* folders, post/), e.g. the FP8 runs."""
import argparse, csv, json, math, sys
from pathlib import Path

R0 = Path(__file__).resolve().parents[1]
OLD = {"01_rollcall_scales": "STUDY_B_polarization", "02_ideology_map": "STUDY_D_quadrant", "04_bundled_choices": "STUDY_L_battery",
       "05_gun_scale": "STUDY_G_guns", "06_vote_prediction": "STUDY_V_votes", "07_vote_uncertainty": "STUDY_W1U_uncertainty",
       "08_error_warning": "STUDY_EW_warning", "09_named_member_entropy": "STUDY_N_named_entropy", "10_polarization_history": "STUDY_T_history",
       "11_nominate_benchmarks": "STUDY_NOM_nominate", "12_speech_and_state": "STUDY_SD_speech_district", "13_coverage_fill": "STUDY_GF_gapfill",
       "14_gun_symmetry": "STUDY_SYM_guns", "15_mechanism": "STUDY_M_mechanism", "16_supplementary_checks": "post"}
M = ["qwen", "llama"]
Q4 = ["EL-SP", "ER-ST", "EL-ST", "ER-SP"]
EST = ("est", "b", "estimate", "delta_r", "b_per_sd", "b_ab", "d", "r")
CI = ("ci95", "ci", "d_ci", "ci95_pigeonhole")
VERD = ("supported", "verdict", "competent")
NOT_APPLICABLE = [
    "guns: A12 placement of 60 named legislators (the 60-person coding exists for abortion only; PROTOCOL_GUNSYM)",
    "guns: S5 stated-profile hypotheses H1-H4 and Study L bundles (persona batteries, no issue scale)",
    "guns: T0 party history (economic-axis history)",
    "qwen guns: NOMINATE N2 votes and state-lean D3 (Qwen is not competent on gun votes, G2 A5); W1U, G2, GF cells are reported but marked not interpreted",
    "guns: error warning lives in 06_vote_prediction/out/g2 (warning block), not in 08_error_warning",
]
ROWS = []


def row(study, model, issue, qty, f, path, est=None, ci=None, verdict=None):
    ROWS.append(dict(study=study, model=model, issue=issue, quantity=qty, file=f, path=list(path), est=est, ci=ci, verdict=verdict))


def csvrow(study, model, issue, qty, f, filt, est="estimate", lo="lower95", hi="upper95", verdict="verdict"):
    ROWS.append(dict(study=study, model=model, issue=issue, quantity=qty, file=f, csv=filt, est=est, lo=lo, hi=hi, verdict=verdict))


# ---- 02 ideology map (sections 3-5) -----------------------------------------------------------------------------------------------
D = "02_ideology_map/out"
for m in M:
    row("map", m, "-", "rule layer", f"{D}/{m}/rule.json", ["common_layer"])
    a = f"{D}/s4/anchors.json"
    row("map", m, "-", "A3 r(x, DW-NOMINATE dim1)", a, [m, "r_x_dim1_by_congress_mean"])
    row("map", m, "economic", "A4 r(x, economic scale)", a, [m, "r_x_economic_scale_within_cc", 0])
    row("map", m, "-", "A6 party gap x", a, [m, "party_gap_x_d"])
    row("map", m, "-", "A6 party gap y (map axis; the same for both social scales)", a, [m, "party_gap_y_d"])
    for iss, s4 in (("abortion", "s4"), ("guns", "s4_guns")):
        row("map", m, iss, "A4 r(y, social scale)", f"{D}/{s4}/anchors.json", [m, "r_y_abortion_scale_within_cc", 0])
        for q in Q4: row("map", m, iss, f"A9 recall {q}", f"{D}/{s4}/vote_vs_map.json", [m, "recall_by_vote_quadrant", q])
        for era in ("1973-89", "1991-2005", "2007-23"):
            row("map", m, iss, f"S4d R-D within-party social slope {era}", f"{D}/{s4.replace('s4', 's4d')}/S4D.json",
                [m, era, "ctrl_econ", "diff_R_minus_D"])
    for q in Q4: row("map", m, "abortion", f"A12 placed {q} (/15)", f"{D}/s4c/S4C.json", [m, q, "placed"])
    for q in Q4: row("map", m, "abortion", f"A12 selected {q} (n)", f"{D}/s4c/S4C.json", [m, q, "n"])   # added 2026-10-25 (Section 5 prose)
    for h in ("H1_C1a", "H2_C4", "H3_C2", "H4_C3hit"): row("profiles", m, "-", f"S5 {h}", f"{D}/s5/S5_RESULTS.json", [m, "hyp", h])
row("map", "-", "-", "layer stability gate (s1 -> s2rule twice)", "16_supplementary_checks/layercheck/layer_check.json", ["pass"])
# added 2026-10-25 (Section 5): share of misplaced cross-pressured rows that land in the aligned quadrant with the same economic side
# (EL-ST -> EL-SP, ER-SP -> ER-ST), from the vote-by-map confusion matrix; descriptive
SAME_ECON = {"EL-ST": "EL-SP", "ER-SP": "ER-ST"}
for iss, s4 in (("abortion", "s4"), ("guns", "s4_guns")):
    for m in M:
        for q, dst in SAME_ECON.items():
            row("map", m, iss, f"misplaced {q} rows placed in {dst} (share)", f"02_ideology_map/out/{s4}/vote_vs_map.json",
                [m, "confusion_vote_rows_map_cols", q],
                est=(lambda q, dst: (lambda r: r[dst] / (sum(r.values()) - r[q])))(q, dst))
# added 2026-10-25 for the manuscript (PLAN_REVIEW must-fix 4): descriptive benchmark values the text cites (no tests)
for iss, bf in (("abortion", "benchmark_recall.json"), ("guns", "benchmark_recall_guns.json")):
    B = f"16_supplementary_checks/benchmark/{bf}"
    for g in ("aligned_pooled", "cross_pooled"):
        row("map", "-", iss, f"two-dimensional DW-NOMINATE recall {g}", B, ["N1_dwnominate", "recall", g])
        for m in M:
            row("map", m, iss, f"map recall {g}", B, ["N2_recognized", m, "all_rows", g])
            row("map", m, iss, f"map recall {g}, recognized rows", B, ["N2_recognized", m, "recognized_rows", g])
for m in M:
    for src, dst in (("EL-ST", "EL-SP"), ("EL-ST", "ER-SP"), ("EL-ST", "ER-ST"), ("ER-SP", "ER-ST"), ("ER-SP", "EL-SP"), ("ER-SP", "EL-ST")):
        row("map", m, "abortion", f"named cross-pressured members placed {src} -> {dst} (/15)", "16_supplementary_checks/members_by_era/members_by_era.json",
            ["members", "misplaced_destination", m, src], est=(lambda s, d: (lambda node: node.get(d, 0)))(src, dst))

# ---- 04 bundled choices (section 5) -------------------------------------------------------------------------------------------------
for m in M:
    L = f"04_bundled_choices/out/{m}/RESULTS.json"
    for t in ("P1_Dp_minus_placebo", "P2_Dp_minus_Dm", "P4_Dp_minus_Sm"): row("bundles", m, "-", f"D {t}", L, ["blockD_flips_party_like_H", "tests", t])
    for t in ("B1_Democrat", "B2_Republican", "B3_Republican_minus_Democrat_conflict_effect"):
        row("bundles", m, "-", t, L, ["blockB_natural_cross_pressure", "tests", t])
    for p in ("Democrat", "Republican"):
        row("bundles", m, "-", f"B5 economic share {p}", L, ["blockB_natural_cross_pressure", "tests", "economic_dominance_share_by_party", p])
    for t in ("C1_entropy_toward_loser_minus_toward_winner|H", "C2_switch_toward_loser_minus_toward_winner|H"):
        row("bundles", m, "-", t, L, ["blockC_displacement", "tests", t])
    row("bundles", m, "-", "no-persona reversed - party-like (two-way item bootstrap)", "16_supplementary_checks/no_persona/no_persona_package_effect.json",
        [m, "interval_2026_10_18"])

# ---- 06 vote prediction (section 6, W1; A12-A14; guns = G2) -------------------------------------------------------------------------
V = "06_vote_prediction/out"
for m in M:
    for i in ("abortion", "economic"):
        E = f"{V}/v5/estimates_v2_{m}_abortion_economic.json"; C = f"{V}/v5/competence_party_v2_{m}.json"
        row("votes", m, i, "accuracy aligned", E, ["by_issue", i, "accuracy", "avg", "0"])
        row("votes", m, i, "accuracy cross-pressured", E, ["by_issue", i, "accuracy", "avg", "1"])
        row("votes", m, i, "6.1 CP coefficient (party x roll call FE)", E, ["by_issue", i, "regressions", "accuracy (6.1 preferred)" if i == "abortion" else "accuracy"])
        row("votes", m, i, "A5 competent", C, [i, "competence", "competent"])
        for p in ("Democrat", "Republican"):
            row("votes", m, i, f"CP coefficient {p}", C, [i, p, "cp_coef"])
        row("votes", m, i, "A12 leave-one-out CP 6.1", f"{V}/v6/loo_cp_{m}.json", ["by_issue", i, "loo_6_1"])
    row("votes", m, "abortion", "A13 CP errors toward party (M1)", f"{V}/v6/error_direction_{m}.json", ["reading_M1_cp_errors_toward_party_abortion"])
    G2 = f"{V}/g2/estimates_{m}.json"
    row("votes", m, "guns", "A5 competent", G2, ["competence", "competent"])
    row("votes", m, "guns", "6.1 CP coefficient (abortion-defined CP)", G2, ["regressions_abortion_cp", "accuracy (6.1)"])
    row("votes", m, "guns", "6.1 CP coefficient (gun-defined CP, LOO)", G2, ["gun_cp_loo", "accuracy"])
    row("votes", m, "guns", "abortion CP on the same rows", G2, ["gun_cp_loo", "abortion_cp_same_rows"])
    row("votes", m, "guns", "CP errors toward party", f"{V}/g2/error_direction_{m}.json", ["reading_cp_errors_toward_party"])
    # added 2026-10-25 for the manuscript (P1): reference accuracies, gun descriptives and party splits the vote section cites
    for i in ("abortion", "economic"):
        E = f"{V}/v5/estimates_v2_{m}_abortion_economic.json"
        for g, lab in (("0", "aligned"), ("1", "cross-pressured")):
            row("votes", m, i, f"party-majority rule accuracy {lab}", E, ["by_issue", i, "party_rule_accuracy", g])
            row("votes", m, i, f"DW dim 1 reference accuracy {lab}", E, ["by_issue", i, "dim1_reference_accuracy", g])
        row("votes", m, i, "predicted party gap in yea share", E, ["by_issue", i, "party_gap", "pred"])
        row("votes", m, i, "actual party gap in yea share", E, ["by_issue", i, "party_gap", "actual"])
        row("votes", m, i, "yea-first / nay-first prediction correlation", "16_supplementary_checks/w1/order_corr.json", [m, i])
    for g, lab in (("0", "aligned"), ("1", "cross-pressured")):
        row("votes", m, "guns", f"accuracy {lab}", G2, ["descriptive", "accuracy", g])
        row("votes", m, "guns", f"party-majority rule accuracy {lab}", G2, ["descriptive", "party_rule", g])
        row("votes", m, "guns", f"DW dim 1 reference accuracy {lab}", G2, ["descriptive", "dim1_reference", g])
    for p in ("Democrat", "Republican"):
        row("votes", m, "guns", f"CP coefficient {p} (abortion-defined CP)", G2, ["by_party_abortion_cp", p, "accuracy"])
    row("warning", m, "guns", "AUROC within roll call, CP - aligned", G2, ["warning"], est=["diff", "auroc_within"], ci=["diff_ci95", "auroc_within"],
        verdict=["reading_warns_less_for_cp"])
row("votes", "-", "guns", "G2 leave-one-out gate", f"{V}/g2/gate_loo.json", ["passed"])
# added 2026-10-25 (Sections 5-6): named cases, descriptive (16_supplementary_checks/cases)
CASEJ = "16_supplementary_checks/cases/case_votes.json"; CASEC = "16_supplementary_checks/cases/case_rollcalls.csv"
for name in ("Thomas Eagleton", "Robert Packwood", "Olympia Snowe"):
    for m in M:
        for i in ("abortion", "economic"):
            for k in ("n", "accuracy", "wrong_with_party_share", "against_party_share"):
                row("cases", m, i, f"{name}: {k}", CASEJ, [name, m, i, k])
for key in ("105|Senate|167", "105|Senate|474", "108|Senate|51", "108|Senate|402"):
    for m in M:
        csvrow("cases", m, "abortion", f"Olympia Snowe roll call {key}: model YEA share", CASEC, {"member": "Olympia Snowe", "key": key},
               est=f"yea_share_{m}", lo="none", hi="none", verdict="none")
    csvrow("cases", "-", "abortion", f"Olympia Snowe roll call {key}: her vote (1 = yea)", CASEC, {"member": "Olympia Snowe", "key": key},
           est="actual", lo="none", hi="none", verdict="none")

# ---- 07 vote uncertainty (W1U) ------------------------------------------------------------------------------------------------------
for m in M:
    for i in ("abortion", "economic", "guns", "guns_gcp"):
        csvrow("vote uncertainty", m, i, "CP effect on choice entropy (bits)", "07_vote_uncertainty/tables/verdicts.csv", {"model": m, "issue": i})

# ---- 08 error warning ---------------------------------------------------------------------------------------------------------------
for m in M:
    for i in ("abortion", "economic"):
        W = f"08_error_warning/out/w1_warning_{m}.json"
        row("warning", m, i, "AUROC within roll call, CP - aligned", W, ["by_issue", i], est=["diff", "auroc_within"],
            ci=["diff_ci95", "auroc_within"], verdict=["reading_warns_less_for_cp"])
        row("warning", m, i, "confident-wrong share, CP - aligned", W, ["by_issue", i], est=["diff", "conf_err_share_of_conf"],
            ci=["diff_ci95", "conf_err_share_of_conf"])
        # added 2026-10-25 (PLAN_REVIEW must-fix 4): the group AUROCs behind the difference
        for g in ("aligned", "cp"):
            row("warning", m, i, f"AUROC within roll call, {g}", W, ["by_issue", i, g, "auroc_within"])
    for g in ("aligned", "cp"):
        row("warning", m, "guns", f"AUROC within roll call, {g}", f"06_vote_prediction/out/g2/estimates_{m}.json", ["warning", g, "auroc_within"])

# ---- 09 named-member entropy (Study N) ----------------------------------------------------------------------------------------------
N = "09_named_member_entropy/analysis"
for m in M:
    csvrow("named entropy", m, "-", "competence (aligned C_vote)", f"{N}/results/tables/competence.csv", {"model": m}, est="aligned_C_vote", lo="lo",
           hi="hi", verdict="competent")
    for s in ("Q2", "Q3"): csvrow("named entropy", m, "abortion", f"{s}", f"{N}/results/tables/verdicts.csv", {"model": m, "spec": s})
    csvrow("named entropy", m, "abortion", "secondary C_vote ~ vote_cp", f"{N}/results/tables/verdicts_secondary.csv", {"model": m})
    for s in ("Q2gun", "Q2ab_same_rows"): csvrow("named entropy", m, "guns", s, f"{N}/results_guns/tables/verdicts.csv", {"model": m, "spec": s})
    for s in ("sec_Cgun", "sec_Cvote_same_rows"):
        csvrow("named entropy", m, "guns", s, f"{N}/results_guns/tables/verdicts_secondary.csv", {"model": m, "spec": s})

# ---- 10 polarization history (T0, T2) -----------------------------------------------------------------------------------------------
T = "10_polarization_history/out"
for m in M:
    row("history", m, "economic", "T0 change in party gap (x)", f"{T}/t0/contrasts.json", [m, "main", "x"], est=["dgap"], ci=["ci", "dgap"],
        verdict=["reading_b_D_majority"])
    row("history", m, "economic", "T0 Democratic share of gap growth (x)", f"{T}/t0/contrasts.json", [m, "main", "x"], est=["share_D"],
        ci=["ci", "share_D"])
    row("history", m, "economic", "T0 model minus DW gap growth", f"{T}/t0/contrasts.json", [m, "main", "x-dw1"], est=["dgap"], ci=["dgap_ci"],
        verdict=["reading_a_gap_differs"])
    # added 2026-10-25 for the manuscript (author decision K2: Junsol's history contrasts); values already in the sealed contrasts.json
    row("history", m, "economic", "T0 Democratic share of gap growth, DW dim 1", f"{T}/t0/contrasts.json", [m, "main", "dw1"], est=["share_D"],
        ci=["ci", "share_D"])
    row("history", m, "economic", "T0 Democratic share, model minus DW", f"{T}/t0/contrasts.json", [m, "main", "x-dw1"], est=["share_D"],
        ci=["share_D_ci"])
    row("history", m, "economic", "T0 early-postwar gap, model / DW", f"{T}/t0/contrasts.json", [m, "main", "x-dw1"], est=["early_ratio"],
        ci=["early_ratio_ci"], verdict=["reading_c_little_early"])
    # added 2026-10-25 (Section 4): early-postwar party separation itself, within-Congress SD units (S2), map x and DW dim 1
    for v, lab in (("x", "map x"), ("dw1", "DW dim 1")):
        row("history", m, "economic", f"T0 early-postwar party separation, {lab}", f"{T}/t0/contrasts.json", [m, "main", v], est=["early_s2"],
            ci=["ci", "early_s2"])
    for k, p in (("dD", "Democratic"), ("dR", "Republican")):
        row("history", m, "economic", f"T0 change in {p} mean (x)", f"{T}/t0/contrasts.json", [m, "main", "x"], est=[k], ci=["ci", k])
        row("history", m, "economic", f"T0 change in {p} mean (DW dim 1)", f"{T}/t0/contrasts.json", [m, "main", "dw1"], est=[k], ci=["ci", k])
    for k in ("all", "Democrat", "Republican"):
        row("history", m, "abortion", f"T2 over-alignment {k} (map - vote corr)", f"{T}/t2/t2.json", [m, f"over_alignment_{k}", "diff"])
    row("history", m, "abortion", "T2 map aligns more than votes", f"{T}/t2/t2.json", [m, "reading_map_aligns_more_than_votes"])
    row("history", m, "abortion", "T2 CP more common before sorting", f"{T}/t2/t2.json", [m, "reading_cp_more_common_before_sorting"])
    for k in ("all", "Democrat", "Republican"):      # guns: PROTOCOL_GUNSYM Amendment 1 (2026-10-24)
        row("history", m, "guns", f"T2 over-alignment {k} (map - vote corr)", f"{T}/t2/t2.json",
            [m, "guns_over_alignment" if k == "all" else f"guns_over_alignment_{k}", "diff"])
    row("history", m, "guns", "T2 map aligns more than votes", f"{T}/t2/t2.json", [m, "guns_reading_map_aligns_more_than_votes"])
    row("history", m, "guns", "T2 CP more common before sorting", f"{T}/t2/t2.json", [m, "guns_reading_cp_more_common_before_sorting"])
    for k in ("all", "Democrat", "Republican"):      # abortion on the gun rows (common rows; PROTOCOL_GUNSYM Amendment 2)
        row("history", m, "abortion (gun rows)", f"T2 over-alignment {k} (map - vote corr)", f"{T}/t2/t2.json",
            [m, "gunrows_abortion_over_alignment" if k == "all" else f"gunrows_abortion_over_alignment_{k}", "diff"])
    row("history", m, "abortion (gun rows)", "T2 map aligns more than votes", f"{T}/t2/t2.json", [m, "gunrows_abortion_reading_map_aligns_more_than_votes"])
    row("history", m, "abortion (gun rows)", "T2 CP more common before sorting", f"{T}/t2/t2.json", [m, "gunrows_abortion_reading_cp_more_common_before_sorting"])

# ---- 11 NOMINATE benchmarks ---------------------------------------------------------------------------------------------------------
for m in M:
    for span in ("81-118", "86-113"):
        for p in ("Democrat", "Republican"):
            row("nominate", m, "economic", f"N1 within-member drift, model - NP, {span} {p}", "11_nominate_benchmarks/out/n1.json",
                [m, "spans", span, "reading", p], est=["diff"], ci=["diff_ci"], verdict=["drift_specific_to_model"])
    row("nominate", m, "-", "N2 misplacement ~ CP given GMP", "11_nominate_benchmarks/out/n2.json", [m, "misplacement", "cp_given_gmp"])
    for i in ("abortion", "economic") + (("guns",) if m == "llama" else ()):
        row("nominate", m, i, "N2 vote accuracy ~ CP given GMP", "11_nominate_benchmarks/out/n2.json", [m, "votes", i, "cp_given_gmp"])
        row("nominate", m, i, "N2 beyond NOMINATE", "11_nominate_benchmarks/out/n2.json", [m, "votes", i, "reading_beyond_nominate"])
row("nominate", "-", "-", "N2 CP fitted worse by NOMINATE", "11_nominate_benchmarks/out/n2.json", ["reading_cp_fitted_worse"])

# ---- 12 speech and state ------------------------------------------------------------------------------------------------------------
S = "12_speech_and_state/out"
row("speech", "-", "-", "S1 speech-side gate", f"{S}/s1/s1.json", ["gate_GS1", "pass"])
for m in M:
    row("speech", m, "-", "S1 model minus DW sorting distance", f"{S}/s1/s1.json", [m, "comparison", "dw1"], verdict=None)
    row("speech", m, "-", "S1 model closer to speech (RS1)", f"{S}/s1/s1.json", [m, "reading_RS1"])
    row("speech", m, "abortion", "S2b CP x partisan speech", f"{S}/s2/s2.json", [m, "S2b_interaction", "cp_x_p"])
    row("speech", m, "abortion", "S2 reading (RS2)", f"{S}/s2/s2.json", [m, "reading_RS2"])
    # added 2026-10-25 for the manuscript: S2a is a votes-and-speech quantity (the same for both models)
    row("speech", m, "abortion", "S2a partisan speech ~ CP", f"{S}/s2/s2.json", [m, "S2a_p_on_cp"])
    row("speech", m, "guns", "S2a partisan speech ~ gun CP", "13_coverage_fill/out/gf.json", ["G2_gun_cp", m, "S2", "S2a_gun", "gun_cp"])
    for ax in ("x", "y"):
        row("state", m, "-", f"D2 map {ax} ~ state lean (pooled)", f"{S}/d/d.json", [m, "D2", "pooled", ax])
        row("state", m, "-", f"D2 reading {ax}", f"{S}/d/d.json", [m, f"reading_RD2_{ax}"])
    for i in ("abortion", "economic") + (("guns",) if m == "llama" else ()):
        row("state", m, i, "D3 vote accuracy ~ constituency CP", f"{S}/d/d.json", [m, "D3_W1", i, "ccp"], verdict=None)
        row("state", m, i, "D3 reading", f"{S}/d/d.json", [m, "D3_W1", i, "reading_RD3"])

# ---- 13 coverage fill (gun versions of S2, D, N2; L1 for guns) ----------------------------------------------------------------------
GF = "13_coverage_fill/out/gf.json"
for m in M:
    for i in ("abortion", "economic", "guns", "guns_gun_cp_loo"):
        row("coverage fill", m, i.replace("guns_gun_cp_loo", "guns (gun CP)"), "G1 S2c errors toward party ~ partisan speech", GF, ["G1_S2c", m, i])
    row("coverage fill", m, "guns", "G1 interpreted", GF, ["G1_S2c", m, "guns_interpreted"])
    row("coverage fill", m, "guns", "G2 S2b gun CP x partisan speech", GF, ["G2_gun_cp", m, "S2", "S2b_gun_interaction", "gcp_x_p"])
    row("coverage fill", m, "guns", "G2 RS2 gun reading", GF, ["G2_gun_cp", m, "S2", "reading_RS2_gun"])
    row("coverage fill", m, "guns", "G2 N2 CP fitted worse (gun)", GF, ["G2_gun_cp", m, "N2", "reading_cp_fitted_worse_gun"])
    for d in ("abortion_cp_def", "gun_cp_def"):
        row("coverage fill", m, "guns", f"G4 L1 accuracy, CP ({d})", GF, ["G4_L1_guns", m, d, "cp", "accuracy"])
    row("coverage fill", m, "guns", "G4 interpreted", GF, ["G4_L1_guns", m, "interpreted"])

# ---- 05 gun scale (G0, G1) ----------------------------------------------------------------------------------------------------------
row("gun scale", "-", "guns", "G0 gun CP share", "05_gun_scale/out/g0/report.json", ["gun_cp_share"])
row("gun scale", "-", "guns", "G0 cells passed", "05_gun_scale/out/g0/report.json", ["cells_passed"])
for m in M:
    row("gun scale", m, "guns", "G1 map recall CP - aligned", f"05_gun_scale/out/g1/g1_{m}.json", ["gun"], est=lambda g: g["cp"] - g["aligned"],
        ci=["cp_minus_aligned_ci95"])
    row("gun scale", m, "guns", "G1 map recall aligned", f"05_gun_scale/out/g1/g1_{m}.json", ["gun", "aligned"])
    row("gun scale", m, "guns", "G1 map recall CP", f"05_gun_scale/out/g1/g1_{m}.json", ["gun", "cp"])
    row("gun scale", m, "guns", "G1 map misses gun CP", f"05_gun_scale/out/g1/g1_{m}.json", ["reading_map_misses_gun_cp"])

# ---- 15 mechanism (Study M) ---------------------------------------------------------------------------------------------------------
X = "15_mechanism/out"
for m in M:
    for iss, x1, x2 in (("abortion", "x1", "x2"), ("guns", "x1_guns", "x2_guns")):
        row("mechanism", m, iss, "X1 primary d (party pull - economic pull)", f"{X}/{x1}/RESULTS.json", ["A_map", m, "primary"], est=["est", "d"],
            ci=["ci95", "d"], verdict=["verdict"])
        for p in ("Democrat", "Republican"):
            row("mechanism", m, iss, f"X2 within-party gap economic - social, {p}", f"{X}/{x2}/RESULTS.json", ["models", m, p, "primary"],
                est=["est", "gap_eco_minus_soc"], ci=["ci95", "gap_eco_minus_soc"], verdict=["verdict"])
    row("mechanism", m, "-", "X3 b (social strength beyond economic)", f"{X}/x3/RESULTS.json", ["models", m, "primary"], est=["est", "b"],
        ci=["ci95", "b"], verdict=["verdict", "b"])
    row("mechanism", m, "-", "X4 familiarity slope per SD", f"{X}/x4/RESULTS.json", ["models", m, "primary"])
    for p in ("Democrat", "Republican"):
        row("mechanism", m, "-", f"X5 stage A {p}", f"{X}/x5/RESULTS_stageA.json", ["models", m, p, "primary"])
        row("mechanism", m, "-", f"X5 stage B late suppression {p}", f"{X}/x5/RESULTS_stageB.json", ["models", m, p])


# -------------------------------------------------------------------------------------------------------------------------------------
def at(node, path):
    for k in path:
        node = node[k] if not isinstance(node, list) else node[int(k)]
    return node


def first(d, keys):
    for k in keys:
        if isinstance(d, dict) and k in d: return d[k]
    return None


def num(x):
    if x is None or isinstance(x, bool): return None
    try:
        v = float(x); return None if math.isnan(v) else v
    except (TypeError, ValueError): return None


def norm(node, r):
    est = (r["est"](node) if callable(r["est"]) else at(node, r["est"])) if r.get("est") else None
    ci = at(node, r["ci"]) if r.get("ci") else None
    ver = at(node, r["verdict"]) if r.get("verdict") else None
    if r.get("est") is None and r.get("ci") is None:
        if isinstance(node, (bool, str)): ver = node
        elif isinstance(node, (int, float)): est = node
        elif isinstance(node, list) and len(node) == 3 and all(isinstance(v, (int, float)) for v in node): est, ci = node[0], node[1:]
        elif isinstance(node, dict):
            est, ci = first(node, EST), first(node, CI)
            if ver is None: ver = first(node, VERD)
    elif r.get("verdict") is None and isinstance(node, dict) and r.get("est") is None:
        ver = first(node, VERD)
    lo, hi = (ci[0], ci[1]) if isinstance(ci, (list, tuple)) and len(ci) == 2 else (None, None)
    return num(est), num(lo), num(hi), ver


def path_of(root, layout, rel):
    top, rest = rel.split("/", 1)
    return root / (OLD.get(top, top) if layout == "old" else top) / rest


def values(root=R0, layout="new"):
    out, cache = [], {}
    for r in ROWS:
        p = path_of(root, layout, r["file"])
        if "csv" in r:
            if p not in cache: cache[p] = list(csv.DictReader(open(p, encoding="utf-8")))
            hit = [x for x in cache[p] if all(x.get(k) == v for k, v in r["csv"].items())]
            if len(hit) != 1: raise KeyError(f"{r['file']} {r['csv']}: {len(hit)} rows")
            h = hit[0]; est, lo, hi, ver = num(h.get(r["est"])), num(h.get(r["lo"])), num(h.get(r["hi"])), h.get(r["verdict"])
        else:
            if p not in cache: cache[p] = json.load(open(p, encoding="utf-8"))
            est, lo, hi, ver = norm(at(cache[p], r["path"]), r)
        out.append(dict(study=r["study"], model=r["model"], issue=r["issue"], quantity=r["quantity"], estimate=est, lower95=lo, upper95=hi,
                        verdict="" if ver is None else str(ver), source=r["file"] + ("" if "csv" in r else " " + json.dumps(r["path"]))))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--root", default=str(R0)); ap.add_argument("--layout", choices=["new", "old"], default="new")
    ap.add_argument("--out", default=None); a = ap.parse_args()
    rows = values(Path(a.root), a.layout)
    f = open(a.out, "w", newline="", encoding="utf-8") if a.out else sys.stdout
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader()
    for x in rows: w.writerow({k: (repr(v) if isinstance(v, float) else v) for k, v in x.items()})
    print(f"{len(rows)} rows", file=sys.stderr)
