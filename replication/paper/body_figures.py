#!/usr/bin/env python
"""Draw the body figures (paper/figures/body/fig1_history, fig2_snapshots, fig3_placement, fig4_votes, fig5_uncertainty; .png and .pdf)
and Appendix Figure B4 (paper/figures/appendix/B4_social_history).

Style: one claim per figure, lettered panels, the key number in the panel title, almost no text inside panels, benchmarks drawn inside
the model panels, axis directions in words; parties #2F6FCF / #D24B2A; cross-pressured types #1b9e77 (econ-liberal, soc-conservative) /
#7b3fa0 (econ-conservative, soc-liberal); aligned grey.

Sources (nothing typed). Values and intervals from paper/values.json and appendix_values.json; series and coordinates from package
outputs:
  - Figure 1 and Figure B4: 06_party_history/out/t0/trajectories.csv (party means per Congress in SD of each scale; a guard checks that
    the series reproduces the printed gap growth); 08_supplementary_checks/figure_data/out/gap_benchmark.csv (abortion roll-call party
    gap); 05_directions_and_map/out/<m>/s3/temporal_member_scores.csv (within-Congress SD for the social benchmark).
  - Figure 2: 05_directions_and_map/out/<m>/s3/temporal_member_scores.csv (member coordinates and DW-NOMINATE dimension 1).
  - Figure 3: 08_supplementary_checks/figure_data/out/fig2_quadrant_arrows.csv and fig2_cp_rows.csv (shares checked there against the
    sealed recall_by_vote_quadrant); panel titles from RECALL_CROSS_AB_*.
Runs in ~/venvs/paperfig (matplotlib) like appendix_figures.py.
Usage: ~/venvs/paperfig/bin/python paper/body_figures.py"""
import csv
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

P = Path(__file__).resolve().parent; R = P.parent
OUT = P / "figures" / "body"; OUT.mkdir(parents=True, exist_ok=True)
FD = R / "08_supplementary_checks" / "figure_data" / "out"
V = json.load(open(P / "values.json", encoding="utf-8")); V.update(json.load(open(P / "appendix_values.json", encoding="utf-8")))

QWEN, LLAMA = "#2a78d6", "#eb6834"                      # models (Figure 4)
DEM, REP = "#2F6FCF", "#D24B2A"                         # parties (Figures 1, 2)
G1, G2, GREY = "#1b9e77", "#7b3fa0", "#b4b3ad"          # cross-pressured types and aligned (Figure 3)
DEMBG, REPBG = "#e3ecf9", "#f9e6e1"
INK, MUTED, GRID = "#1b1b1b", "#6b6a66", "#e7e6e2"
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


def save(fig, name, out=OUT):
    for ext in ("png", "pdf"):
        fig.savefig(out / f"{name}.{ext}", bbox_inches="tight", facecolor="white",
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

# ---- Figure 1: the history each model reconstructs (design C5) --------------------------------------------------------------------
T = {}
for r in csv.DictReader(open(R / "06_party_history/out/t0/trajectories.csv", encoding="utf-8")):
    T.setdefault((r["model"], r["var"]), []).append((int(r["congress"]), float(r["mean_D"]), float(r["mean_R"]), float(r["gap_s1"])))
EARLY, LATE = range(80, 86), range(113, 119)   # 1947-1958 and 2013-2024 (party_history.py windows)
assert T[("qwen", "dw1")] == T[("llama", "dw1")], "DW-NOMINATE series differ between model files"
w = lambda s, col, rng: sum(r[col] for r in s if r[0] in rng) / len(rng)
for s, key in ((T[("qwen", "x")], "T0_DGAP_Q"), (T[("llama", "x")], "T0_DGAP_L"), (T[("qwen", "dw1")], "AP_DW_DGAP")):
    growth = w(s, 3, LATE) - w(s, 3, EARLY)
    assert abs(growth - num(key)) < 0.001, f"plotted series does not reproduce {key}: {growth:.3f} vs {num(key)}"


def series(m, v):
    """party means by year, shifted so that the 1947-1958 midpoint of the two parties is zero (display centring only)"""
    s = np.array(sorted((c, d, r_) for c, d, r_, _ in T[(m, v)])); c, d, r_ = s[:, 0], s[:, 1], s[:, 2]
    mid = np.mean([(a + b) / 2 for cc, a, b in zip(c, d, r_) if cc in EARLY])
    return np.array([year(x) for x in c]), d - mid, r_ - mid


def within_sd_ratio(m):
    """per Congress: mean over chambers of the within-cell SD of the social coordinate, over its pooled SD (the panel's unit)"""
    rows = [r for r in csv.DictReader(open(R / f"05_directions_and_map/out/{m}/s3/temporal_member_scores.csv", encoding="utf-8"))
            if r["party"] in ("Democrat", "Republican")]
    y = -np.array([float(r["social_orth"]) for r in rows]); pooled = y.std()
    c = np.array([int(r["congress"]) for r in rows]); ch = np.array([r["chamber"] for r in rows])
    return {k: np.mean([y[(c == k) & (ch == h)].std() for h in ("House", "Senate") if ((c == k) & (ch == h)).sum() > 1]) / pooled
            for k in np.unique(c)}


GB = list(csv.DictReader(open(FD / "gap_benchmark.csv", encoding="utf-8")))
yw, dw_d, dw_r = series("qwen", "dw1")


def history(v, name, out, figsize):
    """party means per Congress on one direction (v = "x" economic with DW-NOMINATE, "y" social with the abortion roll-call gap) for both
    models; pass 21: the economic panels are Figure 1, the social panels Figure B4"""
    fig, axs = plt.subplots(1, 2, figsize=figsize, sharey=True, layout="constrained")
    for ax, (m, title), lab in zip(axs, [("qwen", "Qwen"), ("llama", "Llama")], "ab"):
        _panel(ax, m, title, v, lab)
    axs[0].invert_yaxis(); axs[0].set_ylabel("Year (each Congress)")
    h = [plt.Line2D([], [], color=MUTED, lw=2.0)] + ([plt.Line2D([], [], color=MUTED, lw=1.1, ls=(0, (3, 2)))] if v == "x" else
                                                    [plt.Line2D([], [], color=MUTED, lw=1.3, ls=(0, (1, 1.4)))])
    lab2 = ("DW-NOMINATE 1st dimension party mean (liberal–conservative; mostly economic)" if v == "x" else
            "Abortion roll calls: party gap only, drawn around the model's party midpoint (positions not comparable)")
    fig.legend(h, ["Party mean on the model's map (SD of each axis)", lab2], loc="outside lower center", ncol=1, fontsize=7)
    save(fig, name, out)


def _panel(ax, m, title, v, lab):
    yr, d, r_ = series(m, v)
    ax.fill_betweenx(yr, d, r_, color="#efeeea", lw=0, zorder=0)
    ax.plot(d, yr, color=DEM, lw=2.0); ax.plot(r_, yr, color=REP, lw=2.0)
    if v == "x":
        ax.plot(dw_d, yw, color=DEM, lw=1.1, ls=(0, (3, 2))); ax.plot(dw_r, yw, color=REP, lw=1.1, ls=(0, (3, 2)))
        sub = f"gap {int(yr[0])} → {int(yr[-1])}: {r_[0] - d[0]:.1f} → {r_[-1] - d[-1]:.1f}\nDW-NOMINATE {dw_r[0] - dw_d[0]:.1f} → {dw_r[-1] - dw_d[-1]:.1f}"
    else:
        # the abortion roll-call scale has no common scale across Congresses: only its within-Congress party gap is drawn, centred on
        # the model's own party midpoint (the location is the model's by construction; the separation is the benchmark)
        ws = within_sd_ratio(m); mid = dict(zip(yr, (d + r_) / 2))
        g = [x for x in GB if x["llm"] == m and x["issue"] == "abortion" and x["rollcall"] not in ("", "nan")]
        by = np.array([int(x["year"]) for x in g]); half = np.array([0.5 * float(x["rollcall"]) * ws[int(x["congress"])] for x in g])
        mm = np.array([mid[y_] for y_ in by])
        ax.plot(mm - half, by, color=DEM, lw=1.3, ls=(0, (1, 1.4))); ax.plot(mm + half, by, color=REP, lw=1.3, ls=(0, (1, 1.4)))
        # audit 11-01b (I1-H, I3-1): print the gaps as drawn (pooled SD of the axis), not the within-Congress gaps of gap_benchmark.csv
        sub = (f"gap {int(yr[0])} → {int(yr[-1])}: {r_[0] - d[0]:.1f} → {r_[-1] - d[-1]:.1f}\n"
               f"roll calls {by[0]} → {by[-1]}: {2 * half[0]:.1f} → {2 * half[-1]:.1f}").replace("-", "−")
    ax.axvline(0, color=MUTED, lw=0.7, zorder=1)
    ax.text(d[-1], yr[-1] + 1, "D", color=DEM, ha="center", va="top", fontsize=8, fontweight="bold")
    ax.text(r_[-1], yr[-1] + 1, "R", color=REP, ha="center", va="top", fontsize=8, fontweight="bold")
    ax.set_title(f"{lab}  {title}, {'economic' if v == 'x' else 'social'}\n\n\n", loc="left", fontsize=8.5)
    t_ = ax.text(0, 1.01, sub, transform=ax.transAxes, fontsize=6.2, color=INK, va="bottom"); t_.set_in_layout(False)
    ax.set_xlim((-2.6, 2.6) if v == "x" else (-3.6, 1.6)); ax.grid(axis="x", visible=False)
    ax.set_xlabel("← left    right →" if v == "x" else "← progressive    traditional →", fontsize=7.5)
history("x", "fig1_history", OUT, (4.6, 5.6))
history("y", "B4_social_history", P / "figures" / "appendix", (4.6, 5.6))

# ---- Figure 2: snapshots of each model's map (
# pass 21:). Members' coordinates from 05_directions_and_map/out/<m>/s3/temporal_member_scores.csv
# (x = -econ_orth, y = -social_orth), each scaled by its pooled SD and shifted so that the 1947-1958 midpoint of the two party means is
# zero (display only); party-mean paths over the earlier Congresses; dashed: DW-NOMINATE dimension 1 party means in the snapshot
# Congress (same scaling). Code moved unchanged from appendix_figures.py.
SNAP = [80, 92, 104, 118]


def _members(m, cols):
    rows = [r for r in csv.DictReader(open(R / f"05_directions_and_map/out/{m}/s3/temporal_member_scores.csv", encoding="utf-8"))
            if r["party"] in ("Democrat", "Republican") and all(r[k] for k in cols)]
    c = np.array([int(r["congress"]) for r in rows]); p = np.array([r["party"] for r in rows]); out = []
    for k, sgn in zip(cols, (-1 if cols[0] == "econ_orth" else 1, -1 if cols[1] == "social_orth" else 1)):
        v = sgn * np.array([float(r[k]) for r in rows]); v = v / v.std(); e = np.isin(c, list(EARLY))
        out.append(v - (v[e & (p == "Democrat")].mean() + v[e & (p == "Republican")].mean()) / 2)
    return c, p, out[0], out[1]


cd, pdw, xdw, _ = _members("qwen", ["dim1", "dim2"])
fig, axs = plt.subplots(2, 4, figsize=(7.4, 4.3), sharex=True, sharey=True, layout="constrained")
for i, (m, title) in enumerate([("qwen", "Qwen"), ("llama", "Llama")]):
    c, p, x, y = _members(m, ["econ_orth", "social_orth"])
    for j, k in enumerate(SNAP):
        ax = axs[i, j]
        for pp, col in (("Democrat", DEM), ("Republican", REP)):
            q = (c == k) & (p == pp); ax.scatter(x[q], y[q], s=3, color=col, alpha=0.3, lw=0)
            t = np.array([(x[(c == kk) & (p == pp)].mean(), y[(c == kk) & (p == pp)].mean()) for kk in range(80, k + 1)])
            ax.plot(t[:, 0], t[:, 1], color=col, lw=1.2); ax.scatter(*t[-1], s=42, color=col, edgecolor="white", lw=1, zorder=5)
            ax.axvline(xdw[(cd == k) & (pdw == pp)].mean(), color=col, lw=1.1, ls=(0, (3, 2)), zorder=4)
        ax.axhline(0, color=MUTED, lw=0.5); ax.axvline(0, color=MUTED, lw=0.5); ax.set_xlim(-3.4, 3.4); ax.set_ylim(-4.2, 3.4)
        ax.set_aspect("equal"); ax.grid(False)
        if i == 0: ax.set_title(f"{year(k)}", loc="center")
        if j == 0: ax.set_ylabel(f"{title}\n← progressive   traditional →", fontsize=8)
for ax in axs[1]: ax.set_xlabel("← left    right →", fontsize=7.5)
h = [plt.Line2D([], [], marker="o", color=MUTED, mec="white", ls="none", ms=7), plt.Line2D([], [], color=MUTED, lw=1.1, ls=(0, (3, 2)))]
fig.legend(h, ["Party mean on the model's map (path = earlier years)", "Party mean in DW-NOMINATE, 1st dimension (liberal–conservative; drawn on the horizontal axis only)"],
           loc="outside lower center", ncol=1, fontsize=7.5)
save(fig, "fig2_snapshots")

# ---- Figure 3: where the models place members (design: placement arrows) ---------------------------------------------------------
A = list(csv.DictReader(open(FD / "fig2_quadrant_arrows.csv", encoding="utf-8")))
PTS = list(csv.DictReader(open(FD / "fig2_cp_rows.csv", encoding="utf-8")))
GC = {"EL-ST": G1, "ER-SP": G2}
plt.rcParams.update({"axes.grid": False})
fig = plt.figure(figsize=(6.4, 3.5), layout="constrained")
gs = fig.add_gridspec(1, 2)
for j, (m, title, s) in enumerate([("qwen", "Qwen", "Q"), ("llama", "Llama", "L")]):
    ax = fig.add_subplot(gs[0, j])
    ax.add_patch(plt.Rectangle((0, 0), 0.5, 0.5, color=DEMBG, lw=0, zorder=0)); ax.add_patch(plt.Rectangle((0.5, 0.5), 0.5, 0.5, color=REPBG, lw=0, zorder=0))
    ax.axvline(0.5, color=MUTED, lw=0.7); ax.axhline(0.5, color=MUTED, lw=0.7)
    for q, col in GC.items():
        pts = [r for r in PTS if r["model"] == m and r["vote_q"] == q]
        ax.scatter([float(r["x_p"]) for r in pts], [float(r["y_p"]) for r in pts], s=2.5, color=col, alpha=0.22, lw=0, zorder=1)
    for x, y, ha, va in [(0.03, 0.97, "left", "top"), (0.97, 0.03, "right", "bottom")]:
        ax.text(x, y, "cross-pressured", ha=ha, va=va, fontsize=6.5, color=MUTED, style="italic", transform=ax.transAxes)
    for r in (r for r in A if r["model"] == m):
        q = r["vote_q"]; x0, y0, x1, y1 = (float(r[k]) for k in ("vote_x", "vote_y", "map_x", "map_y")); col = GC.get(q, GREY); cp = q in GC
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="-|>", color=col, lw=2.4 if cp else 1.2,
                                                                       mutation_scale=12 if cp else 7, shrinkA=4, shrinkB=3), zorder=4)
        ax.scatter([x0], [y0], s=46 if cp else 22, facecolor="white", edgecolor=col, lw=1.6, zorder=5)
        ax.scatter([x1], [y1], s=46 if cp else 22, color=col, edgecolor="white", lw=0.9, zorder=5)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_aspect("equal"); ax.set_xticks([0, 0.5, 1]); ax.set_yticks([0, 0.5, 1])
    ax.tick_params(labelsize=6.5)
    ax.set_title(f"{'ab'[j]}  {title}: cross-pressured kept {round(100 * num(f'RECALL_CROSS_AB_{s}'))}%", fontsize=8)
    ax.set_xlabel("Economic  liberal → conservative", fontsize=7.2)
    if j == 0: ax.set_ylabel("Social  progressive → traditional", fontsize=7.2)
h = [plt.Line2D([], [], marker="o", mfc="white", mec=INK, ls="none", ms=5.5), plt.Line2D([], [], marker="o", color=INK, mec="white", ls="none", ms=5.5),
     plt.Line2D([], [], marker="o", color=G1, ls="none", ms=5), plt.Line2D([], [], marker="o", color=G2, ls="none", ms=5),
     Patch(color=DEMBG), Patch(color=REPBG)]
fig.legend(h, ["votes (group mean)", "model (group mean)", "econ. liberal, soc. conservative", "econ. conservative, soc. liberal",
               "Democratic corner", "Republican corner"], loc="outside lower center", ncol=3, fontsize=6.8, handlelength=1.0, columnspacing=0.9)
save(fig, "fig3_placement")
plt.rcParams.update({"axes.grid": True})

# ---- Figure 4: vote prediction ---
# Cell = cross-pressured minus aligned accuracy within party and roll call (the Section 6 estimator), 95% interval behind it; red = less
# accurate, blue = more, white = 0; cells whose interval includes zero are pale with grey text. Guns, state lean and NOMINATE fit are in
# Appendix D. Draft: 
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
COLS = [("Q", "abortion"), ("Q", "economic"), ("L", "abortion"), ("L", "economic")]
ROWS = [("All cross-pressured", {"abortion": "CP_COEF_AB", "economic": "CP_COEF_ECON"}),
        ("Democrats only", {"abortion": "CP_COEF_AB_DEMOCRAT", "economic": "CP_COEF_ECON_DEMOCRAT"}),
        ("Republicans only", {"abortion": "CP_COEF_AB_REPUBLICAN", "economic": "CP_COEF_ECON_REPUBLICAN"}),
        ("Leave the predicted\nroll call out", {"abortion": "CP_LOO_AB", "economic": "CP_LOO_ECON"})]
cmap = LinearSegmentedColormap.from_list("div", ["#b2182b", "#ef8a62", "#fbe3d6", "#ffffff", "#d6e6f4", "#67a9cf", "#2166ac"])
norm = TwoSlopeNorm(vmin=-0.25, vcenter=0.0, vmax=0.25)
plt.rcParams.update({"axes.grid": False})
fig, ax = plt.subplots(figsize=(5.4, 2.6), layout="constrained")
for i, (lab, keys) in enumerate(ROWS):
    for j, (s, iss) in enumerate(COLS):
        k = f"{keys[iss]}_{s}"; b = num(k); lo, hi = ci(k + "_CI"); sig = lo > 0 or hi < 0
        rgba = list(cmap(norm(b)))
        if not sig: rgba = [1 - 0.35 * (1 - x) for x in rgba[:3]] + [1]
        ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, facecolor=rgba, edgecolor="white", lw=2))
        txt = f"{b:+.2f}".replace("-", "−") if round(b, 2) != 0 else "0.00"
        ax.text(j, i, txt, ha="center", va="center", fontsize=8.5 if sig else 7.5, fontweight="bold" if sig else "normal",
                color=("white" if abs(b) > 0.15 else INK) if sig else "#8d8c86")
ax.set_xlim(-0.5, 3.5); ax.set_ylim(3.5, -0.5)
ax.set_xticks(range(4)); ax.set_xticklabels([iss.capitalize() for _, iss in COLS]); ax.xaxis.tick_top()
ax.set_yticks(range(4)); ax.set_yticklabels([r[0] for r in ROWS])
for sp in ax.spines.values(): sp.set_visible(False)
ax.tick_params(length=0, labelsize=8); ax.axvline(1.5, color="white", lw=6); ax.axhline(2.5, color="white", lw=5)
for x0, x1, name in ((0, 1, "Qwen"), (2, 3, "Llama")):
    ax.annotate("", xy=(x1 + 0.42, -1.05), xytext=(x0 - 0.42, -1.05), annotation_clip=False, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.text((x0 + x1) / 2, -1.2, name, ha="center", va="bottom", fontsize=8.5, fontweight="bold", color=INK, clip_on=False)
cb = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax, shrink=0.75, pad=0.02, ticks=[-0.2, -0.1, 0, 0.1, 0.2])
cb.ax.set_yticklabels(["−0.2", "−0.1", "0", "0.1", "0.2"]); cb.outline.set_visible(False)
cb.set_label("Accuracy gap\n(cross-pressured − aligned)", fontsize=7.5)
ax.set_title("Mispredicted on abortion, not on economic votes", pad=46)
save(fig, "fig4_votes")
plt.rcParams.update({"axes.grid": True})

# ---- Figure 5: uncertainty -----------------------
# a: vote-prediction task; b: the named-member check. Entropy as a share of its maximum (bits for two answers; scale entropy / log2 n,
# stage 17). Draft and dependencies: 
fig, axs = plt.subplots(1, 2, layout="constrained", figsize=(7.6, 2.0), sharex=True)
rows = [("1-9 scale", "SH_VOTE_AB"), ("YEA or NAY", "W1U_AB")]
dotci(axs[0], [r for r, _ in rows], [(MN[s], MC[s], [f"{k}_{s}" for _, k in rows], "o") for s in "QL"], zero=0.0)
axs[0].set_title("a  Votes: higher on the scale in both", fontsize=8.5)
rows = [("1-9 scale", "SH_NAMED_AB"), ("Yes or no", "N_Q2_AB")]
dotci(axs[1], [r for r, _ in rows], [(MN[s], MC[s], [f"{k}_{s}" for _, k in rows], "o") for s in "QL"], zero=0.0)
axs[1].set_title("b  Asked about the member: higher in both", fontsize=8.5)
for ax in axs:
    ax.set_xlabel("Entropy above aligned members, abortion\n(share of the maximum)"); ax.grid(axis="x", visible=True)
    ax.set_ylim(-0.6, 1.6)
axs[0].set_xlim(-0.01, 0.075)
h, l = axs[1].get_legend_handles_labels(); fig.legend(h, l, loc="outside lower center", ncol=2)
save(fig, "fig5_uncertainty")
print(f"body figures written to {OUT}")
