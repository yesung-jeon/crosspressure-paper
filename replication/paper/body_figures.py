#!/usr/bin/env python
"""Draw the body figures (paper/figures/body/fig1_history, fig2_placement, fig3_uncertainty; .png and .pdf). Author 10-19: core
results only, at the visual standard of Junsol Kim's figures (compact lettered panels, labelled members); PLAN rows for Figures 1-3.

Sources. Point estimates and intervals are read from paper/values.json and paper/appendix_values.json. Two inputs are plotted
directly from package outputs because they are series or coordinates, not printed numbers:
  - Figure 1 (a-c): 10_polarization_history/out/t0/trajectories.csv (party means and gap per Congress, in standard deviations of
    each scale, written by party_history.py trajectories()); a guard checks that the plotted series reproduces the printed growth.
  - Figure 2 (a, b): 02_ideology_map/out/s4c/s4c_rows.csv (the 60 vote-selected members: vote quadrant, each model's quadrant and
    average percentile rank of the two coordinates within Congress and chamber, written by 08b_place_by_votes.py).
Nothing is typed. Runs in ~/venvs/paperfig (matplotlib) like appendix_figures.py.
Usage: ~/venvs/paperfig/bin/python paper/body_figures.py"""
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

P = Path(__file__).resolve().parent; R = P.parent
OUT = P / "figures" / "body"; OUT.mkdir(parents=True, exist_ok=True)
V = json.load(open(P / "values.json", encoding="utf-8")); V.update(json.load(open(P / "appendix_values.json", encoding="utf-8")))

QWEN, LLAMA, BENCH, BENCH2, GREEN = "#2a78d6", "#eb6834", "#52514e", "#a3a29c", "#1baf7a"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
MC = {"Q": QWEN, "L": LLAMA}; MN = {"Q": "Qwen", "L": "Llama"}; MK = {"Q": "qwen", "L": "llama"}
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
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"{name}.{ext}", bbox_inches="tight", facecolor="white",
                    metadata={"CreationDate": None} if ext == "pdf" else None)   # no timestamp: identical bytes on rerun
    plt.close(fig)


def dotci(ax, rows, series, zero=None, dodge=0.22):
    n, m = len(rows), len(series)
    for j, (name, color, keys, marker) in enumerate(series):
        for i, k in enumerate(keys):
            if k is None: continue
            y = n - 1 - i + (j - (m - 1) / 2) * dodge
            if k + "_CI" in V:
                lo, hi = ci(k + "_CI"); ax.plot([lo, hi], [y, y], color=color, lw=1.6, solid_capstyle="round")
            ax.plot(num(k), y, marker=marker, color=color, ms=6, mec="white", mew=1.0, ls="none", label=name if i == 0 else None)
    if zero is not None: ax.axvline(zero, color=MUTED, lw=0.8, zorder=0)
    ax.set_yticks(range(n)); ax.set_yticklabels(rows[::-1]); ax.grid(axis="y", visible=False)


year = lambda c: 1789 + 2 * (c - 1)

# ---- Figure 1: the history each model reconstructs -----------------------------------------------------------------------------
T = {}
for r in csv.DictReader(open(R / "10_polarization_history/out/t0/trajectories.csv", encoding="utf-8")):
    T.setdefault((r["model"], r["var"]), []).append((int(r["congress"]), float(r["mean_D"]), float(r["mean_R"]), float(r["gap_s1"])))
EARLY, LATE = range(80, 86), range(113, 119)   # 1947-1958 and 2013-2024 (party_history.py windows)
ser = {"Q": T[("qwen", "x")], "L": T[("llama", "x")], "DW": T[("qwen", "dw1")]}
assert T[("qwen", "dw1")] == T[("llama", "dw1")], "DW-NOMINATE series differ between model files"
w = lambda s, col, rng: sum(r[col] for r in s if r[0] in rng) / len(rng)
for s, key in (("Q", "T0_DGAP_Q"), ("L", "T0_DGAP_L"), ("DW", "AP_DW_DGAP")):
    growth = w(ser[s], 3, LATE) - w(ser[s], 3, EARLY)
    assert abs(growth - num(key)) < 0.001, f"plotted series does not reproduce {key}: {growth:.3f} vs {num(key)}"
style = {"Q": (QWEN, "-", "Qwen"), "L": (LLAMA, "-", "Llama"), "DW": (BENCH, (0, (4, 2)), "DW-NOMINATE")}
fig, axs = plt.subplots(1, 3, layout="constrained", figsize=(7.6, 2.5))
panels = [(3, "a  Party gap", False), (1, "b  Democratic mean", True),
          (2, "c  Republican mean", True)]
for ax, (col, title, rel) in zip(axs, panels):
    for s in ("DW", "Q", "L"):
        color, ls, name = style[s]
        base = w(ser[s], col, EARLY) if rel else 0.0
        ax.plot([year(r[0]) for r in ser[s]], [r[col] - base for r in ser[s]], color=color, ls=ls, lw=1.8, label=name)
    for rng in (EARLY, LATE): ax.axvspan(year(rng[0]), year(rng[-1]) + 2, color=GRID, alpha=0.6, lw=0, zorder=0)
    if rel: ax.axhline(0, color=MUTED, lw=0.8, zorder=0)
    ax.set_title(title, fontsize=8.5); ax.set_xticks([1950, 1970, 1990, 2010])
axs[0].set_ylabel("Standard deviations of each scale")
axs[1].set_ylabel("Change from 1947–1958 (SD)")
h, l = axs[0].get_legend_handles_labels(); fig.legend(h, l, loc="outside lower center", ncol=3, handlelength=3)
save(fig, "fig1_history")

# ---- Figure 2: where the models place members -----------------------------------------------------------------------------------
S = list(csv.DictReader(open(R / "02_ideology_map/out/s4c/s4c_rows.csv", encoding="utf-8")))
assert len(S) == int(num("NAMED_TOTAL")), "selected members file does not match NAMED_TOTAL"
QS = {"EL-SP": ("Liberal on both", BENCH, "o"), "ER-ST": ("Conservative on both", BENCH2, "s"),
      "EL-ST": ("Econ. liberal, soc. conservative", GREEN, "^"), "ER-SP": ("Econ. conservative, soc. liberal", GREEN, "v")}
LABEL = {"Thomas Eagleton": "Eagleton", "Robert Packwood": "Packwood"}
OFF = {("Q", "Eagleton"): (-48, 34), ("Q", "Packwood"): (-40, -30), ("L", "Eagleton"): (28, -30), ("L", "Packwood"): (-8, -34)}
fig = plt.figure(layout="constrained", figsize=(7.6, 3.1))
gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 1.15])
for j, s in enumerate("QL"):
    ax = fig.add_subplot(gs[0, j]); m = MK[s]
    for q, (name, color, mk) in QS.items():
        rows = [r for r in S if r["vote_q"] == q]
        for placed in (True, False):
            pts = [r for r in rows if (r[f"{m}_q"] == q) == placed]
            ax.scatter([float(r[f"{m}_xp"]) for r in pts], [float(r[f"{m}_yp"]) for r in pts], marker=mk, s=30,
                       facecolors=color if placed else "white", edgecolors=color, linewidths=1.2, zorder=3,
                       label=f"{name}" if (placed and j == 0) else None)
    for r in S:
        if r["name"] in LABEL:
            x, y = float(r[f"{m}_xp"]), float(r[f"{m}_yp"])
            ax.annotate(LABEL[r["name"]], (x, y), xytext=OFF[(s, LABEL[r["name"]])], textcoords="offset points", fontsize=7.5,
                        color=INK, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    ax.axvline(0.5, color=MUTED, lw=0.8, zorder=1); ax.axhline(0.5, color=MUTED, lw=0.8, zorder=1)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_aspect("equal"); ax.set_xticks([0, 0.5, 1]); ax.set_yticks([0, 0.5, 1])
    ax.set_title(f"{'ab'[j]}  {MN[s]}'s map", fontsize=8.5)
    ax.set_xlabel("Economic (percentile)")
    if j == 0: ax.set_ylabel("Social (percentile)")
ax = fig.add_subplot(gs[0, 2])
rows = ["Abortion, aligned", "Abortion, cross-pressured", "Guns, aligned", "Guns, cross-pressured"]
dotci(ax, rows, [("Qwen", QWEN, ["RECALL_ALIGNED_AB_Q", "RECALL_CROSS_AB_Q", "RECALL_ALIGNED_GUN_Q", "RECALL_CROSS_GUN_Q"], "o"),
                 ("Llama", LLAMA, ["RECALL_ALIGNED_AB_L", "RECALL_CROSS_AB_L", "RECALL_ALIGNED_GUN_L", "RECALL_CROSS_GUN_L"], "o"),
                 ("DW-NOMINATE, two dimensions", BENCH, ["DW2_RECALL_ALIGNED_AB", "DW2_RECALL_CROSS_AB", "DW2_RECALL_ALIGNED_GUN",
                                                         "DW2_RECALL_CROSS_GUN"], "D")], dodge=0.24)
ax.set_xlim(0, 1); ax.set_xlabel("Share placed in the\nquadrant of their votes"); ax.set_title("c  Placement, all member-Congresses", fontsize=8.5)
h1, l1 = fig.axes[0].get_legend_handles_labels(); h2, l2 = ax.get_legend_handles_labels()
fig.legend(h1 + h2, l1 + l2, loc="outside lower center", ncol=4, fontsize=7.5, handletextpad=0.3, columnspacing=1.0)
save(fig, "fig2_placement")

# ---- Figure 3: uncertainty --------------------------------------------------------------------------------------------------------
fig, axs = plt.subplots(1, 2, layout="constrained", figsize=(7.6, 3.6), gridspec_kw={"width_ratios": [1.5, 1]})
rows = [("Votes, abortion", "W1U_AB"), ("Votes, economic", "W1U_ECON"), ("Votes, guns (abortion-defined)", "W1U_GUN"),
        ("Votes, guns (gun-defined)", "W1U_GUNCP"), ("Named member, abortion", "N_Q2_AB"),
        ("Named member, cross-pressured on the map", "N_Q3_AB"), ("Named member, guns", "AP_NAMED_GUN"),
        ("Named member, guns (abortion-defined)", "AP_NAMED_GUN_ABDEF"), ("Stated profile, choice", "H1"),
        ("Stated profile, generation (nats)", "H2"), ("Packages, Democratic personas", "BUNDLE_DEMOCRAT"),
        ("Packages, Republican personas", "BUNDLE_REPUBLICAN")]
dotci(axs[0], [r for r, _ in rows], [(MN[s], MC[s], [f"{k}_{s}" for _, k in rows], "o") for s in "QL"], zero=0.0)
axs[0].set_xlabel("Entropy, cross-pressured minus aligned\n(bits unless noted)"); axs[0].set_title("a  Entropy differences", fontsize=8.5)
iss = [("Abortion", "AB"), ("Economic", "ECON"), ("Guns", "GUN")]
rows = [f"{n}, {g}" for n, _ in iss for g in ("aligned", "cross-pressured")]
keys = lambda s: [f"AUROC_{g}_{t}_{s}" for _, t in iss for g in ("ALIGNED", "CP")]
dotci(axs[1], rows, [(MN[s], MC[s], keys(s), "o") for s in "QL"], zero=0.5)
axs[1].set_xlim(0.4, 0.8); axs[1].set_xlabel("Probability that a wrong prediction has\nhigher entropy than a right one")
axs[1].set_title("b  Does entropy mark the errors?", fontsize=8.5)
h, l = axs[0].get_legend_handles_labels(); fig.legend(h, l, loc="outside lower center", ncol=2)
save(fig, "fig3_uncertainty")
print(f"body figures written to {OUT}")
