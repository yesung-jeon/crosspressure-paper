#!/usr/bin/env python
"""Draw the appendix figures (paper/figures/appendix/*.png and *.pdf). Results are shown as figures rather than tables.

Every plotted number is read from paper/values.json or paper/appendix_values.json (themselves read from package outputs; the by-decade
placement shares enter appendix_values.json as AP_ERA_* keys, cross-verification A23). Nothing is typed.
Colors follow the dataviz reference palette: Qwen = categorical slot 1 (blue), Llama = slot 2 (orange), roll-call benchmarks = neutral
gray. Static figures for print: light surface, thin marks, direct labels where there are few series, a legend otherwise.
Runs in a separate environment with matplotlib (~/venvs/paperfig) so the analysis environment stays as it was.
Usage: ~/venvs/paperfig/bin/python paper/appendix_figures.py"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker

P = Path(__file__).resolve().parent; R = P.parent
OUT = P / "figures" / "appendix"; OUT.mkdir(parents=True, exist_ok=True)
V = json.load(open(P / "values.json", encoding="utf-8")); V.update(json.load(open(P / "appendix_values.json", encoding="utf-8")))

QWEN, LLAMA, BENCH, BENCH2 = "#2a78d6", "#eb6834", "#52514e", "#a3a29c"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
MC = {"Q": QWEN, "L": LLAMA}; MN = {"Q": "Qwen", "L": "Llama"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titlesize": 9, "axes.titleweight": "bold", "axes.titlelocation": "left", "legend.frameon": False,
                     "figure.dpi": 150, "savefig.dpi": 300, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
                     "axes.axisbelow": True})


def num(k):
    return float(V[k]["value"].replace("−", "-").replace(",", ""))


def ci(k):
    lo, hi = V[k]["value"].strip("[]").replace("−", "-").split(",")
    return float(lo), float(hi)


def save(fig, name):
    fig.savefig(OUT / f"{name}.png", bbox_inches="tight", facecolor="white")
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight", facecolor="white", metadata={"CreationDate": None})   # no timestamp: identical bytes on rerun
    plt.close(fig)


def dotci(ax, rows, series, zero=0.0, xlabel=None, dodge=True):
    """Horizontal dot-and-interval plot. rows: labels top to bottom; series: list of (name, color, [key per row or None], marker).
    dodge=False puts every series on the row line (for panels where each row holds one series)."""
    n, m = len(rows), len(series)
    off = [(j - (m - 1) / 2) * 0.22 if dodge else 0.0 for j in range(m)]
    for j, (name, color, keys, marker) in enumerate(series):
        for i, k in enumerate(keys):
            if k is None: continue
            y = n - 1 - i + off[j]
            if k + "_CI" in V:
                lo, hi = ci(k + "_CI"); ax.plot([lo, hi], [y, y], color=color, lw=1.6, solid_capstyle="round")
            ax.plot(num(k), y, marker=marker, color=color, ms=6, mec="white", mew=1.0, ls="none", label=name if i == 0 else None)
    if zero is not None: ax.axvline(zero, color=MUTED, lw=0.8, zorder=0)
    ax.set_yticks(range(n)); ax.set_yticklabels(rows[::-1]); ax.grid(axis="y", visible=False)
    if xlabel: ax.set_xlabel(xlabel)


def legend_top(fig, ax, ncol=3, **kw):
    h, l = ax.get_legend_handles_labels()
    fig.legend(h, l, loc="outside lower center", ncol=ncol, **kw)


# ---- A1: member-Congresses by quadrant
QSHORT = ["Liberal\nboth", "Conserv.\nboth", "Econ. lib.\nsoc. cons.", "Econ. cons.\nsoc. lib."]
Q4 = [("ELSP", "Liberal on both"), ("ERST", "Conservative on both"), ("ELST", "Econ. liberal, soc. conservative"),
      ("ERSP", "Econ. conservative, soc. liberal")]
fig, axs = plt.subplots(1, 2, layout="constrained", figsize=(7.2, 2.4), sharey=True)
for ax, (iss, title) in zip(axs, (("AB", "Abortion"), ("GUN", "Guns"))):
    vals = [num(f"AP_QN_{q}_{iss}") for q, _ in Q4]
    cols = [BENCH2, BENCH2, "#1baf7a", "#1baf7a"]
    ax.barh(range(4)[::-1], vals, color=cols, height=0.62)
    for y, v in zip(range(4)[::-1], vals): ax.text(v, y, f" {v:,.0f}", va="center", color=INK, fontsize=8)
    ax.set_yticks(range(4)[::-1]); ax.set_yticklabels([l for _, l in Q4]); ax.set_title(title); ax.grid(axis="y", visible=False)
    ax.set_xlim(0, max(vals) * 1.22); ax.set_xlabel("Member-Congresses")
save(fig, "A1_quadrants")

# ---- B1: growth of the party gap
fig, axs = plt.subplots(1, 4, layout="constrained", figsize=(7.4, 1.9), sharey=True)
src = [("Qwen", QWEN, "o", "_Q"), ("Llama", LLAMA, "o", "_L"), ("DW-NOMINATE", BENCH, "s", None)]
panels = [("Growth of the gap", "T0_DGAP", "AP_DW_DGAP"), ("Change, Democrats", "T0_CHANGE_D", "AP_DW_CHANGE_D"),
          ("Change, Republicans", "T0_CHANGE_R", "AP_DW_CHANGE_R"), ("Democratic share", "T0_SHARE_D", "T0_SHARE_D_DW")]
for ax, (title, base, dwk) in zip(axs, panels):
    keys = [base + "_Q", base + "_L", dwk]
    for i, ((name, color, mk, _), k) in enumerate(zip(src, keys)):
        y = 2 - i
        if k + "_CI" in V:
            lo, hi = ci(k + "_CI"); ax.plot([lo, hi], [y, y], color=color, lw=1.6)
        ax.plot(num(k), y, marker=mk, color=color, ms=6, mec="white", mew=1, ls="none")
    ax.axvline(0, color=MUTED, lw=0.8, zorder=0); ax.set_title(title, fontsize=8.5); ax.grid(axis="y", visible=False)
axs[0].set_yticks([2, 1, 0]); axs[0].set_yticklabels(["Qwen", "Llama", "DW-NOMINATE"])
save(fig, "B1_gap_growth")

# ---- B2: continuing members, model minus Nokken-Poole
fig, axs = plt.subplots(1, 2, layout="constrained", figsize=(7.0, 1.8), sharey=True, sharex=True)
for ax, (title, sp, pre) in zip(axs, (("Congresses from 1949", "81_118", ""), ("Congresses from 1959", "86_113", "AP_"))):
    rows = ["Democrats", "Republicans"]
    dotci(ax, rows, [(MN[s], MC[s], [f"{pre}N1_DEMOCRAT_{sp}_{s}", f"{pre}N1_REPUBLICAN_{sp}_{s}"], "o") for s in "QL"])
    ax.set_title(title); ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(5))
axs[0].set_xlabel("Movement of continuing members, model minus Nokken-Poole (SD)"); legend_top(fig, axs[0], 2)
save(fig, "B2_continuing")

# ---- B3: by chamber
fig, axs = plt.subplots(1, 3, layout="constrained", figsize=(7.6, 2.0), sharey=True)
dotci(axs[0], ["House", "Senate"], [(MN[s], MC[s], [f"AP_CH_HOUSE_DIFF_{s}", f"AP_CH_SENATE_DIFF_{s}"], "o") for s in "QL"])
axs[0].set_title("Growth of the gap,\nmodel minus DW-NOMINATE", fontsize=8.5)
dotci(axs[1], ["House", "Senate"], [(MN[s], MC[s], [f"AP_CH_HOUSE_SHARE_D_{s}", f"AP_CH_SENATE_SHARE_D_{s}"], "o") for s in "QL"]
      + [("DW-NOMINATE", BENCH, ["AP_CH_HOUSE_SHARE_D_DW", "AP_CH_SENATE_SHARE_D_DW"], "s")], zero=0.5)
axs[1].set_title("Democratic share\nof the growth", fontsize=8.5)
dotci(axs[2], ["House", "Senate"], [(MN[s], MC[s], [f"AP_CH_HOUSE_EARLY_{s}", f"AP_CH_SENATE_EARLY_{s}"], "o") for s in "QL"], zero=1.0)
axs[2].axvline(0, color=GRID, lw=0.8, zorder=0); axs[2].set_title("Early separation as a share\nof DW-NOMINATE's", fontsize=8.5)
legend_top(fig, axs[1], 3)
save(fig, "B3_chamber")

# ---- C1: placement by quadrant, and the two-dimensional DW-NOMINATE benchmark
fig, axs = plt.subplots(1, 3, layout="constrained", figsize=(8.2, 2.6), gridspec_kw={"width_ratios": [2, 2, 1.4]}, sharey=False)
for ax, (iss, title) in zip(axs[:2], (("AB", "Abortion"), ("GUN", "Guns"))):
    x = range(4)
    for j, s in enumerate("QL"):
        ax.bar([i + (j - 0.5) * 0.36 for i in x], [num(f"RECALL_{q}_{iss}_{s}") for q, _ in Q4], width=0.34, color=MC[s],
               label=MN[s])
    ax.set_xticks(list(x)); ax.set_xticklabels(QSHORT, fontsize=7)
    ax.set_ylim(0, 1); ax.set_title(title); ax.grid(axis="x", visible=False)
axs[0].set_ylabel("Share placed in the\nquadrant of their votes")
ax = axs[2]
grp = [("Aligned", "ALIGNED"), ("Cross-\npressured", "CROSS")]
for j, (name, color, fmt) in enumerate([("Qwen", QWEN, "RECALL_{g}_AB_Q"), ("Llama", LLAMA, "RECALL_{g}_AB_L"),
                                        ("DW-NOMINATE 2D", BENCH, "DW2_RECALL_{g}_AB")]):
    ax.bar([i + (j - 1) * 0.26 for i in range(2)], [num(fmt.format(g=g)) for _, g in grp], width=0.25, color=color,
           label=name if j == 2 else None)
ax.set_xticks([0, 1]); ax.set_xticklabels([n for n, _ in grp], fontsize=7.5); ax.set_ylim(0, 1); ax.grid(axis="x", visible=False)
ax.set_title("Abortion, pooled")
h, l = axs[0].get_legend_handles_labels(); h2, l2 = ax.get_legend_handles_labels()
fig.legend(h + h2, l + l2, loc="outside lower center", ncol=3)
save(fig, "C1_placement")

# ---- C2: placement by decade
fig, axs = plt.subplots(1, 2, layout="constrained", figsize=(7.0, 2.3), sharey=True)
for ax, (tag, title) in zip(axs, (("AB", "Abortion"), ("GUN", "Guns"))):
    dec = sorted({int(k.split("_")[3]) for k in V if k.startswith(f"AP_ERA_{tag}_") and k.endswith("_ALIGNED_Q")})
    for s, dx in (("Q", -0.8), ("L", 0.8)):  # small horizontal offset so the two models' points do not hide each other
        xs = [d + dx for d in dec]
        ax.plot(xs, [num(f"AP_ERA_{tag}_{d}_ALIGNED_{s}") for d in dec], color=MC[s], lw=2, marker="o", ms=5, mec="white",
                label=f"{MN[s]}, aligned")
        ax.plot(xs, [num(f"AP_ERA_{tag}_{d}_CROSS_{s}") for d in dec], color=MC[s], lw=2, ls=(0, (3, 2)), marker="o", ms=5,
                mfc="white", label=f"{MN[s]}, cross-pressured")
    ax.set_xticks(dec); ax.set_xticklabels([f"{d}s" for d in dec]); ax.set_ylim(0, 1); ax.set_title(title)
axs[0].set_ylabel("Share placed in the\nquadrant of their votes"); legend_top(fig, axs[0], 4, handlelength=3.5)
save(fig, "C2_by_decade")

# ---- C3: destinations of misplaced members, and the 60 members
fig, axs = plt.subplots(1, 2, layout="constrained", figsize=(7.4, 2.4))
ax = axs[0]
cats = [("ELST", "AB", "Lib.-cons.\nabortion"), ("ERSP", "AB", "Cons.-lib.\nabortion"),
        ("ELST", "GUN", "Lib.-cons.\nguns"), ("ERSP", "GUN", "Cons.-lib.\nguns")]
for j, s in enumerate("QL"):
    ax.bar([i + (j - 0.5) * 0.36 for i in range(4)], [num(f"SAME_ECON_{q}_{iss}_{s}") for q, iss, _ in cats], width=0.34,
           color=MC[s], label=MN[s])
ax.set_xticks(range(4)); ax.set_xticklabels([c for *_, c in cats], fontsize=7); ax.set_ylim(0, 1); ax.grid(axis="x", visible=False)
ax.set_title("Moved to the aligned quadrant\nwith the same economic side", fontsize=8.5)
ax = axs[1]
for j, s in enumerate("QL"):
    ax.bar([i + (j - 0.5) * 0.36 for i in range(4)], [num(f"NAMED_PLACED_{q}_{s}") for q, _ in Q4], width=0.34, color=MC[s])
ax.axhline(num("NAMED_N"), color=MUTED, lw=0.8, ls=(0, (2, 2)))
ax.set_xticks(range(4)); ax.set_xticklabels(QSHORT, fontsize=7)
ax.set_title(f"Selected members placed in\ntheir quadrant (of {num('NAMED_N'):.0f})", fontsize=8.5)
ax.grid(axis="x", visible=False)
legend_top(fig, axs[0], 2)
save(fig, "C3_destinations_members")

# ---- C4: stated profiles
fig, axs = plt.subplots(1, 4, layout="constrained", figsize=(7.8, 1.9), sharey=True)
for ax, (k, title) in zip(axs, (("H3", "Consistency"), ("H4", "Reaches quadrant"), ("H1", "Choice entropy (bits)"),
                                ("H2", "Generation (nats)"))):
    dotci(ax, ["Qwen", "Llama"], [(MN[s], MC[s], [f"{k}_{s}" if s == ss else None for ss in "QL"], "o") for s in "QL"], dodge=False)
    ax.set_ylim(-0.6, 1.6)
    ax.set_title(title, fontsize=8.5)
save(fig, "C4_profiles")

# ---- C5: over-alignment of the two coordinates
fig, ax = plt.subplots(layout="constrained", figsize=(4.6, 1.8))
dotci(ax, ["Abortion", "Guns", "Abortion, cells with a gun scale"], [(MN[s], MC[s], [f"T2_AB_{s}", f"T2_GUN_{s}", f"T2_ABGR_{s}"], "o") for s in "QL"],
      xlabel="Map correlation minus vote correlation")
legend_top(fig, ax, 2)
save(fig, "C5_overalignment")

# ---- C6: policy packages and steering
fig, axs = plt.subplots(1, 2, layout="constrained", figsize=(7.2, 1.9), gridspec_kw={"width_ratios": [1.6, 1]})
dotci(axs[0], ["Democratic personas", "Republican personas", "No persona"],
      [(MN[s], MC[s], [f"BUNDLE_DEMOCRAT_{s}", f"BUNDLE_REPUBLICAN_{s}", f"AP_NOPERSONA_{s}"], "o") for s in "QL"],
      xlabel="Entropy, crossed minus\nparty-like packages (bits)")
dotci(axs[1], ["Steering vs placebo"], [(MN[s], MC[s], [f"AP_STEER_P1_{s}"], "o") for s in "QL"],
      xlabel="Package changes,\npush minus placebo")
axs[1].set_ylim(-0.6, 0.6)
legend_top(fig, axs[0], 2)
save(fig, "C6_packages")

# ---- D1: accuracy and benchmarks
fig, axs = plt.subplots(1, 3, layout="constrained", figsize=(7.6, 2.0), sharey=True, sharex=True)
for ax, (iss, title) in zip(axs, (("AB", "Abortion"), ("ECON", "Economic"), ("GUN", "Guns"))):
    rows = ["Aligned", "Cross-pressured"]
    dotci(ax, rows, [("Qwen", QWEN, [f"ACC_ALIGNED_{iss}_Q", f"ACC_CROSS_{iss}_Q"], "o"),
                     ("Llama", LLAMA, [f"ACC_ALIGNED_{iss}_L", f"ACC_CROSS_{iss}_L"], "o"),
                     ("Party-majority rule", BENCH, [f"PARTY_RULE_ALIGNED_{iss}_Q", f"PARTY_RULE_CROSS_{iss}_Q"], "s"),
                     ("DW-NOMINATE dim. 1", BENCH2, [f"DW1_REF_ALIGNED_{iss}_Q", f"DW1_REF_CROSS_{iss}_Q"], "D")], zero=0.5)
    ax.set_title(title); ax.set_xlim(0.3, 1.0)
axs[1].set_xlabel("Share of votes predicted correctly (vertical line: one half)")
legend_top(fig, axs[0], 4, handlelength=3.5)
save(fig, "D1_accuracy")

# ---- D2: cross-pressured minus aligned accuracy
rows = [("Abortion", "CP_COEF_AB"), ("Abortion: Democrats", "CP_COEF_AB_DEMOCRAT"),
        ("Abortion: Republicans", "CP_COEF_AB_REPUBLICAN"), ("Abortion: leave-one-out", "CP_LOO_AB"),
        ("Abortion: state leans to other party", "D3_AB"), ("Abortion: holding NOMINATE fit", "N2_ACC_AB"),
        ("Economic", "CP_COEF_ECON"), ("Economic: Democrats", "CP_COEF_ECON_DEMOCRAT"),
        ("Economic: Republicans", "CP_COEF_ECON_REPUBLICAN"), ("Economic: leave-one-out", "CP_LOO_ECON"),
        ("Economic: state leans to other party", "D3_ECON"),
        ("Guns, abortion-defined", "CP_COEF_GUN_ABCP"), ("Guns, gun-defined", "CP_COEF_GUN_GUNCP")]
fig, ax = plt.subplots(layout="constrained", figsize=(5.6, 4.0))
dotci(ax, [r for r, _ in rows], [(MN[s], MC[s], [f"{k}_{s}" if f"{k}_{s}" in V else None for _, k in rows], "o") for s in "QL"],
      xlabel="Accuracy, cross-pressured minus aligned,\nwithin party and roll call")
legend_top(fig, ax, 2)
save(fig, "D2_coefficients")

# ---- D3: three members
fig, axs = plt.subplots(1, 2, layout="constrained", figsize=(7.2, 1.9), sharey=True, sharex=True)
for ax, (iss, title) in zip(axs, (("AB", "Abortion roll calls"), ("ECON", "Economic roll calls"))):
    rows = ["Eagleton", "Packwood", "Snowe"]
    dotci(ax, rows, [("Voted against party majority", BENCH, [f"{n.upper()}_{iss}_AGAINST_Q" for n in rows], "s"),
                     ("Qwen accuracy", QWEN, [f"{n.upper()}_{iss}_ACC_Q" for n in rows], "o"),
                     ("Llama accuracy", LLAMA, [f"{n.upper()}_{iss}_ACC_L" for n in rows], "o")], zero=0.5)
    ax.set_title(title); ax.set_xlim(0, 1)
axs[0].set_xlabel("Share of the member's roll calls"); legend_top(fig, axs[0], 3)
save(fig, "D3_members")

# (old Figures E1 and E2 are drawn as body Figure 3 by body_figures.py since 2026-10-25)

# ---- F1: social weight within party, and speech timing
fig, axs = plt.subplots(1, 2, layout="constrained", figsize=(7.2, 1.8))
dotci(axs[0], ["Democrats", "Republicans"], [(MN[s], MC[s], [f"X2_AB_DEMOCRAT_{s}", f"X2_AB_REPUBLICAN_{s}"], "o") for s in "QL"],
      xlabel="Economic minus social coefficient, within party")
dotci(axs[1], ["Speech", "DW-NOMINATE", "Qwen", "Llama"],
      [("", BENCH, ["AP_S1_SPEECH", "AP_S1_DW", None, None], "s"), ("", QWEN, [None, None, "AP_S1_X_Q", None], "o"),
       ("", LLAMA, [None, None, None, "AP_S1_X_L"], "o")], xlabel="Share of gap growth by mid-period", dodge=False)
axs[1].set_ylim(-0.6, 3.6)
legend_top(fig, axs[0], 2)
save(fig, "F1_mechanism_speech")
print(f"appendix figures written to {OUT}")
