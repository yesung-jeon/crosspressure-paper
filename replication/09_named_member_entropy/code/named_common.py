"""Study N shared definitions (PLAN.md v0.2, PLAN_REVIEW). Paths, analysis rows, quadrant rule, items, want_yes, binary entropy.
Rules copied from sealed Study D scripts that cannot be imported (they run on import); each copy names its source and is checked against
the sealed outputs (PROTOCOL R1b, R2)."""
import gc, json, os, sys, time
from pathlib import Path
import numpy as np, pandas as pd

N = Path(__file__).resolve().parents[1]; KIM = N.parent
sys.path.insert(0, str(KIM / "02_ideology_map" / "code"))
import map_common as dc  # noqa: E402

OUT = N / "out"
MAPOUT = OUT / "mapout"                       # STUDYD_OUT for the re-projected map: mapout/<m>/{rule.json, s3/}, mapout/s4*/
RAM_LOAD_GB, RAM_PART_GB = 5.0, 2.0           # global long-run rule (Study V A1 values): before loading / between parts
PART_ROWS = 200                               # member-Congress rows per part (200 x 16 items x 2 orders = 6,400 prompts)
FMT = {"yn": " Answer with Yes or No.", "ny": " Answer with No or Yes."}
Q4 = ["EL-SP", "ER-ST", "EL-ST", "ER-SP"]; ALIGNED, CROSS = ["EL-SP", "ER-ST"], ["EL-ST", "ER-SP"]


def quad(x, y):
    """06_vote_vs_map.py line 14"""
    return pd.Series(np.where(x > 0, "ER-", "EL-"), index=getattr(x, "index", None)) + np.where(y > 0, "ST", "SP")


def analysis_rows(map_csv):
    """06_vote_vs_map.py lines 16-18, 30-33, 79-82: the paper's vote-vs-map rows (93rd Congress on, Democrats and Republicans, both scales)
    with vote and map quadrants (median splits within Congress x chamber) and median-origin standardized map coordinates (line 56, 62)."""
    sc = pd.read_csv(dc.ISSUE_SCALES); sc = sc[sc.issue.isin(["economic", "abortion"])]
    w = sc.pivot_table(index=["congress", "chamber", "icpsr"], columns="issue", values="rc_score").reset_index()
    m = pd.read_csv(map_csv)
    m["cc"] = m.congress.astype(str) + m.chamber
    m["x"], m["y"] = -m.econ_orth, -m.social_orth            # 06_vote_vs_map.py line 29 (orientation: x right, y traditional)
    j = m.merge(w, on=["congress", "chamber", "icpsr"], how="left", validate="one_to_one")
    v = j[(j.congress >= 93) & j.party.isin(["Democrat", "Republican"])].dropna(subset=["economic", "abortion"]).copy()
    for c in ["x", "y", "economic", "abortion"]:
        v[f"hi_{c}"] = v[c] > v.groupby("cc")[c].transform("median")
    v["vote_q"] = quad(v.hi_economic.astype(int) - 0.5, v.hi_abortion.astype(int) - 0.5)
    v["map_q"] = quad(v.hi_x.astype(int) - 0.5, v.hi_y.astype(int) - 0.5)
    v["xm"] = v.x - v.groupby("cc").x.transform("median"); v["ym"] = v.y - v.groupby("cc").y.transform("median")
    v["zx"] = v.xm / v.groupby("cc").xm.transform("std"); v["zy"] = v.ym / v.groupby("cc").ym.transform("std")
    v["rid"] = v.congress.astype(str) + "|" + v.chamber + "|" + v.icpsr.astype(str)
    assert not v.rid.duplicated().any()
    return v.reset_index(drop=True)


def items():
    """the 16 single-axis items of Section 5 (11_stated_profiles.py line 21-22)"""
    it = json.load(open(dc.CP_ITEMS, encoding="utf-8"))["items"]
    s = [i for i in it if i["type"] in ("econ_only", "soc_only")]
    assert len(s) == 16
    return s


def want_yes(it, prof):
    """11_stated_profiles.py lines 28-33: desired answer of a single-axis item for a quadrant profile"""
    E, S = prof[1], prof[4]
    e = None if it["econ_yes"] == 0 else ((it["econ_yes"] == 1) == (E == "L"))
    s = None if it["soc_yes"] == 0 else ((it["soc_yes"] == 1) == (S == "P"))
    return e if e is not None else s


def hbits(p):
    p = np.clip(np.asarray(p, dtype=float), 1e-12, 1 - 1e-12)
    return -(p * np.log2(p) + (1 - p) * np.log2(1 - p))


def wait_ram(need):
    t0 = time.time()
    while dc.free_ram_gb() < need:
        if time.time() - t0 > 3 * 3600: raise SystemExit(f"RAM guard: < {need} GB free for 3 h")
        dc.log(f"RAM guard: {dc.free_ram_gb():.1f} GB free (< {need}), waiting 60 s"); gc.collect(); time.sleep(60)
