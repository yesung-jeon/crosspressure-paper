#!/usr/bin/env python
"""Build paper/values.json: every number the manuscript prints, read by key from validation/headline_values.csv (the validated
headline table) and formatted here. No number is typed in this file or in the section templates. Each value records its source rows.

Keys are UPPER_SNAKE names used as {{KEY}} in paper/sections/*.template.md. Model suffixes: _Q (Qwen), _L (Llama).
Usage: python paper/values.py   -> paper/values.json"""
import csv, json, math
from pathlib import Path

P = Path(__file__).resolve().parent; R = P.parent
H = {(x["study"], x["model"], x["issue"], x["quantity"]): x for x in csv.DictReader(open(R / "validation/headline_values.csv", encoding="utf-8"))}
MS = {"Q": "qwen", "L": "llama"}
V = {}


def row(k):
    if k not in H: raise KeyError(f"headline row missing: {k}")
    return H[k]


def f(x, d=3):
    v = float(x)
    if math.isclose(v, round(v)) and abs(v) >= 1: return f"{int(round(v)):,}"
    s = f"{v:.{d}f}"
    return s.replace("-", "−") if s.startswith("-") else s


def put(key, value, *srcs):
    if key in V: raise KeyError(f"duplicate key {key}")
    V[key] = {"value": value, "source": [" | ".join(s) for s in srcs]}


def est(key, k, d=3):
    put(key, f(row(k)["estimate"], d), k)


def ci(key, k, d=3):
    x = row(k)
    if x["lower95"] == "": raise ValueError(f"no interval for {k}")
    put(key, f"[{f(x['lower95'], d)}, {f(x['upper95'], d)}]", k)


def estci(base, k, d=3):
    est(base, k, d); ci(base + "_CI", k, d)


def verdict(key, k):
    put(key, row(k)["verdict"], k)


def pct(key, k):
    put(key, f"{round(100 * float(row(k)['estimate']))} percent", k)


def pct_range(key, ks):
    xs = sorted(round(100 * float(row(k)["estimate"])) for k in ks)
    put(key, f"{xs[0]} percent" if xs[0] == xs[-1] else f"{xs[0]} to {xs[-1]} percent", *ks)


def frac_words(x):
    """nearest simple fraction in words, for prose ("about a sixth")"""
    names = {(1, 2): "a half", (1, 3): "a third", (1, 4): "a quarter", (1, 5): "a fifth", (1, 6): "a sixth", (2, 3): "two-thirds",
             (3, 4): "three-quarters", (2, 5): "two-fifths", (3, 5): "three-fifths", (4, 5): "four-fifths"}
    (a, b) = min(names, key=lambda k: abs(k[0] / k[1] - x))
    return "about " + names[(a, b)]


# ---- Section 3 / Table 1: the map recovers the aligned structure -------------------------------------------------------------------
for s, m in MS.items():
    est(f"LAYER_{s}", ("map", m, "-", "rule layer"))
    est(f"R_X_DW1_{s}", ("map", m, "-", "A3 r(x, DW-NOMINATE dim1)"))
    est(f"R_X_ECON_{s}", ("map", m, "economic", "A4 r(x, economic scale)"))
    for iss, t in (("abortion", "AB"), ("guns", "GUN")):
        est(f"R_Y_{t}_{s}", ("map", m, iss, "A4 r(y, social scale)"))
    est(f"PARTY_GAP_X_{s}", ("map", m, "-", "A6 party gap x"))
    est(f"PARTY_GAP_Y_{s}", ("map", m, "-", "A6 party gap y (map axis; the same for both social scales)"))
verdict("LAYER_GATE", ("map", "-", "-", "layer stability gate (s1 -> s2rule twice)"))

# ---- Section 4: history (T0) --------------------------------------------------------------------------------------------------------
for s, m in MS.items():
    estci(f"T0_DGAP_{s}", ("history", m, "economic", "T0 change in party gap (x)"))
    estci(f"T0_DGAP_MINUS_DW_{s}", ("history", m, "economic", "T0 model minus DW gap growth"))
    estci(f"T0_SHARE_D_{s}", ("history", m, "economic", "T0 Democratic share of gap growth (x)"))
    estci(f"T0_SHARE_D_MINUS_DW_{s}", ("history", m, "economic", "T0 Democratic share, model minus DW"))
    estci(f"T0_EARLY_RATIO_{s}", ("history", m, "economic", "T0 early-postwar gap, model / DW"))
    verdict(f"T0_EARLY_READING_{s}", ("history", m, "economic", "T0 early-postwar gap, model / DW"))
    estci(f"T0_EARLY_SEP_MAP_{s}", ("history", m, "economic", "T0 early-postwar party separation, map x"))
    put(f"T0_EARLY_FRAC_{s}", frac_words(float(row(("history", m, "economic", "T0 early-postwar gap, model / DW"))["estimate"])),
        ("history", m, "economic", "T0 early-postwar gap, model / DW"))
    verdict(f"T0_READING_A_{s}", ("history", m, "economic", "T0 model minus DW gap growth"))
    verdict(f"T0_READING_B_{s}", ("history", m, "economic", "T0 change in party gap (x)"))
    for p, t in (("Democratic", "D"), ("Republican", "R")):
        estci(f"T0_CHANGE_{t}_{s}", ("history", m, "economic", f"T0 change in {p} mean (x)"))
    for p in ("Democrat", "Republican"):
        estci(f"N1_{p.upper()}_81_118_{s}", ("nominate", m, "economic", f"N1 within-member drift, model - NP, 81-118 {p}"))
        verdict(f"N1_{p.upper()}_81_118_READING_{s}", ("nominate", m, "economic", f"N1 within-member drift, model - NP, 81-118 {p}"))
    estci(f"S1_DIST_{s}", ("speech", m, "-", "S1 model minus DW sorting distance"))
    verdict(f"RS1_{s}", ("speech", m, "-", "S1 model closer to speech (RS1)"))
estci("T0_SHARE_D_DW", ("history", "qwen", "economic", "T0 Democratic share of gap growth, DW dim 1"))
estci("T0_EARLY_SEP_DW", ("history", "qwen", "economic", "T0 early-postwar party separation, DW dim 1"))
for iss, t in (("abortion", "AB"), ("guns", "GUN")):
    for s, m in MS.items():
        for q, dst in (("EL-ST", "EL-SP"), ("ER-SP", "ER-ST")):
            est(f"SAME_ECON_{q.replace('-', '')}_{t}_{s}", ("map", m, iss, f"misplaced {q} rows placed in {dst} (share)"))

# ---- Section 5: cross-pressured members in the map; stated profiles --------------------------------------------------------------
for iss, t in (("abortion", "AB"), ("guns", "GUN")):
    for g, gt in (("aligned_pooled", "ALIGNED"), ("cross_pooled", "CROSS")):
        est(f"DW2_RECALL_{gt}_{t}", ("map", "-", iss, f"two-dimensional DW-NOMINATE recall {g}"))
        for s, m in MS.items():
            est(f"RECALL_{gt}_{t}_{s}", ("map", m, iss, f"map recall {g}"))
            est(f"RECALL_{gt}_{t}_RECOG_{s}", ("map", m, iss, f"map recall {g}, recognized rows"))
    for s, m in MS.items():
        for q in ("EL-SP", "ER-ST", "EL-ST", "ER-SP"):
            est(f"RECALL_{q.replace('-', '')}_{t}_{s}", ("map", m, iss, f"A9 recall {q}"))
ns = [float(row(("map", m, "abortion", f"A12 selected {q} (n)"))["estimate"]) for m in MS.values() for q in ("EL-SP", "ER-ST", "EL-ST", "ER-SP")]
assert len(set(ns)) == 1, "named members per quadrant differ"
put("NAMED_N", f"{int(ns[0])}", *[("map", m, "abortion", f"A12 selected {q} (n)") for m in MS.values() for q in ("EL-SP", "ER-ST", "EL-ST", "ER-SP")])
put("NAMED_TOTAL", f"{int(4 * ns[0])}", ("four quadrants x NAMED_N (the common per-quadrant count of the rows below)",),
    *[("map", m, "abortion", f"A12 selected {q} (n)") for m in MS.values() for q in ("EL-SP", "ER-ST", "EL-ST", "ER-SP")])
for s, m in MS.items():
    estci(f"G1_GAP_{s}", ("gun scale", m, "guns", "G1 map recall CP - aligned"))
    for q in ("EL-SP", "ER-ST", "EL-ST", "ER-SP"):
        est(f"NAMED_PLACED_{q.replace('-', '')}_{s}", ("map", m, "abortion", f"A12 placed {q} (/15)"))
    for src, dst in (("EL-ST", "EL-SP"), ("ER-SP", "ER-ST")):
        est(f"DEST_{src.replace('-', '')}_TO_{dst.replace('-', '')}_{s}", ("map", m, "abortion", f"named cross-pressured members placed {src} -> {dst} (/15)"))
    for h, t in (("H3_C2", "H3"), ("H4_C3hit", "H4"), ("H1_C1a", "H1"), ("H2_C4", "H2")):
        estci(f"{t}_{s}", ("profiles", m, "-", f"S5 {h}"))
        verdict(f"{t}_READING_{s}", ("profiles", m, "-", f"S5 {h}"))
    for iss, t in (("abortion", "AB"), ("guns", "GUN"), ("abortion (gun rows)", "ABGR")):
        estci(f"T2_{t}_{s}", ("history", m, iss, "T2 over-alignment all (map - vote corr)"))
        verdict(f"T2_{t}_ALIGNS_MORE_{s}", ("history", m, iss, "T2 map aligns more than votes"))
        verdict(f"T2_{t}_CP_EARLIER_{s}", ("history", m, iss, "T2 CP more common before sorting"))

# ---- Section 6: roll-call votes (Junsol Kim's design; W1, A12-A14, G2), constituency, NOMINATE ---------------------------------
for s, m in MS.items():
    for iss, t in (("abortion", "AB"), ("economic", "ECON"), ("guns", "GUN")):
        for lab, lt in (("aligned", "ALIGNED"), ("cross-pressured", "CROSS")):
            est(f"ACC_{lt}_{t}_{s}", ("votes", m, iss, f"accuracy {lab}"))
            est(f"PARTY_RULE_{lt}_{t}_{s}", ("votes", m, iss, f"party-majority rule accuracy {lab}"))
            est(f"DW1_REF_{lt}_{t}_{s}", ("votes", m, iss, f"DW dim 1 reference accuracy {lab}"))
        verdict(f"COMPETENT_{t}_{s}", ("votes", m, iss, "A5 competent"))
    for iss, t in (("abortion", "AB"), ("economic", "ECON")):
        estci(f"CP_COEF_{t}_{s}", ("votes", m, iss, "6.1 CP coefficient (party x roll call FE)"))
        estci(f"CP_LOO_{t}_{s}", ("votes", m, iss, "A12 leave-one-out CP 6.1"))
        for p in ("Democrat", "Republican"):
            estci(f"CP_COEF_{t}_{p.upper()}_{s}", ("votes", m, iss, f"CP coefficient {p}"))
        est(f"PRED_PARTY_GAP_{t}_{s}", ("votes", m, iss, "predicted party gap in yea share"))
        est(f"ACTUAL_PARTY_GAP_{t}_{s}", ("votes", m, iss, "actual party gap in yea share"))
        est(f"ORDER_CORR_{t}_{s}", ("votes", m, iss, "yea-first / nay-first prediction correlation"))
    verdict(f"A13_AB_{s}", ("votes", m, "abortion", "A13 CP errors toward party (M1)"))
    estci(f"CP_COEF_GUN_ABCP_{s}", ("votes", m, "guns", "6.1 CP coefficient (abortion-defined CP)"))
    estci(f"CP_COEF_GUN_GUNCP_{s}", ("votes", m, "guns", "6.1 CP coefficient (gun-defined CP, LOO)"))
    estci(f"CP_COEF_GUN_SAMEROWS_{s}", ("votes", m, "guns", "abortion CP on the same rows"))
    verdict(f"GUN_ERRORS_TOWARD_PARTY_{s}", ("votes", m, "guns", "CP errors toward party"))
    for p in ("Democrat", "Republican"):
        estci(f"CP_COEF_GUN_{p.upper()}_{s}", ("votes", m, "guns", f"CP coefficient {p} (abortion-defined CP)"))
    for iss, t in (("abortion", "AB"), ("economic", "ECON")):
        estci(f"D3_{t}_{s}", ("state", m, iss, "D3 vote accuracy ~ constituency CP"))
    estci(f"N2_ACC_AB_{s}", ("nominate", m, "abortion", "N2 vote accuracy ~ CP given GMP"))
    verdict(f"N2_BEYOND_AB_{s}", ("nominate", m, "abortion", "N2 beyond NOMINATE"))
estci("D3_GUN_L", ("state", "llama", "guns", "D3 vote accuracy ~ constituency CP"))
verdict("N2_FITTED_WORSE", ("nominate", "-", "-", "N2 CP fitted worse by NOMINATE"))
verdict("G2_GATE", ("votes", "-", "guns", "G2 leave-one-out gate"))

# ---- named cases (Sections 5-6; 16_supplementary_checks/cases) -------------------------------------------------------------------
for s, m in MS.items():
    for name, t in (("Olympia Snowe", "SNOWE"), ("Thomas Eagleton", "EAGLETON"), ("Robert Packwood", "PACKWOOD")):
        for iss, it in (("abortion", "AB"), ("economic", "ECON")):
            for k, kt in (("n", "N"), ("accuracy", "ACC"), ("wrong_with_party_share", "WRONG_PARTY"), ("against_party_share", "AGAINST")):
                est(f"{t}_{it}_{kt}_{s}", ("cases", m, iss, f"{name}: {k}"))
            x = float(row(("cases", m, iss, f"{name}: wrong_with_party_share"))["estimate"])
            put(f"{t}_{it}_WRONG_PARTY_WORDS_{s}", "every one" if x == 1 else f"{round(100 * x)} percent", ("cases", m, iss, f"{name}: wrong_with_party_share"))
    for key, kt in (("105|Senate|167", "DOD1997"), ("105|Senate|474", "DOD1998"), ("108|Senate|51", "PBA2003"), ("108|Senate|402", "PBA2003CONF")):
        est(f"SNOWE_{kt}_YEA_{s}", ("cases", m, "abortion", f"Olympia Snowe roll call {key}: model YEA share"), d=2)
for name, t in (("Olympia Snowe", "SNOWE"),):
    for iss, it in (("abortion", "AB"), ("economic", "ECON")):
        x = float(row(("cases", "llama", iss, f"{name}: against_party_share"))["estimate"])
        put(f"{t}_{it}_AGAINST_PCT", f"{round(100 * x)} percent", ("cases", "llama", iss, f"{name}: against_party_share"))

# ---- Section 7: uncertainty --------------------------------------------------------------------------------------------------------
ENT = [("profiles", "-", "S5 H1_C1a"), ("profiles", "-", "S5 H2_C4"),
       ("vote uncertainty", "abortion", "CP effect on choice entropy (bits)"), ("vote uncertainty", "economic", "CP effect on choice entropy (bits)"),
       ("vote uncertainty", "guns", "CP effect on choice entropy (bits)"), ("vote uncertainty", "guns_gcp", "CP effect on choice entropy (bits)"),
       ("named entropy", "abortion", "Q2"), ("named entropy", "abortion", "Q3"), ("named entropy", "guns", "Q2gun"),
       ("named entropy", "guns", "Q2ab_same_rows"), ("bundles", "-", "B1_Democrat"), ("bundles", "-", "B2_Republican")]
put("ENT_CELLS", str(len(ENT)), ("count of the entropy cells listed in paper/values.py ENT",))
for s, m in MS.items():
    for iss, t in (("abortion", "AB"), ("economic", "ECON"), ("guns", "GUN"), ("guns_gcp", "GUNCP")):
        estci(f"W1U_{t}_{s}", ("vote uncertainty", m, iss, "CP effect on choice entropy (bits)"))
        verdict(f"W1U_{t}_READING_{s}", ("vote uncertainty", m, iss, "CP effect on choice entropy (bits)"))
    for iss, t in (("abortion", "AB"), ("economic", "ECON"), ("guns", "GUN")):
        for g in ("aligned", "cp"):
            est(f"AUROC_{g.upper()}_{t}_{s}", ("warning", m, iss, f"AUROC within roll call, {g}"))
        estci(f"AUROC_DIFF_{t}_{s}", ("warning", m, iss, "AUROC within roll call, CP - aligned"))
    for q, t in (("Q2", "Q2_AB"), ("Q3", "Q3_AB")):
        estci(f"N_{t}_{s}", ("named entropy", m, "abortion", q))
        verdict(f"N_{t}_READING_{s}", ("named entropy", m, "abortion", q))
    ks = [(st, m, i, q) for st, i, q in ENT]
    above = sum(float(row(k)["lower95"]) > 0 for k in ks); below = sum(float(row(k)["upper95"]) < 0 for k in ks)
    put(f"ENT_ABOVE_{s}", str(above), *ks); put(f"ENT_BELOW_{s}", str(below), *ks)

# ---- Section 8: speech, mechanism, bundles (for the one-sentence pointer) ---------------------------------------------------------
estci("S2A_AB", ("speech", "qwen", "abortion", "S2a partisan speech ~ CP"))
estci("S2A_GUN", ("speech", "qwen", "guns", "S2a partisan speech ~ gun CP"))
for s, m in MS.items():
    for p in ("Democrat", "Republican"):
        estci(f"X2_AB_{p.upper()}_{s}", ("mechanism", m, "abortion", f"X2 within-party gap economic - social, {p}"))
        verdict(f"X2_AB_{p.upper()}_READING_{s}", ("mechanism", m, "abortion", f"X2 within-party gap economic - social, {p}"))
    estci(f"X5A_REPUBLICAN_{s}", ("mechanism", m, "-", "X5 stage A Republican"))
    for p in ("Democrat", "Republican"):
        est(f"B5_ECON_SHARE_{p.upper()}_{s}", ("bundles", m, "-", f"B5 economic share {p}"))
        estci(f"BUNDLE_{p.upper()}_{s}", ("bundles", m, "-", "B1_Democrat" if p == "Democrat" else "B2_Republican"))

if __name__ == "__main__":
    (P / "values.json").write_text(json.dumps(V, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"paper/values.json: {len(V)} keys from {len({s for v in V.values() for s in v['source']})} headline rows")
