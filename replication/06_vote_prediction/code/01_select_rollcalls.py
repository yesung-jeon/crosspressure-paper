#!/usr/bin/env python
"""Study V stage 0 (PLAN v0.2 W1, CPU, no model): roll-call universe, member-vote rows, cross-pressure labels, coverage.

No model output is read or produced here; this stage sizes the task and checks identification before the protocol is sealed.
1. Member-Congress rows and voting quadrants exactly as Study D 06_vote_vs_map.py (93rd Congress on, Democrats and Republicans, both scales,
   median splits within Congress x chamber). Checked against the sealed vote_vs_map.json row count.
2. Roll calls = the contested roll calls that built the economic and abortion scales (Study B 01_build_scales.py: minority side >= 10%), in the
   Congress x chamber cells where both scales exist. Motion type from Voteview's vote_question (rule below, recorded per roll call).
3. Economic roll calls: within each cell, a seeded random sample of content roll calls equal in number to that cell's abortion content
   roll calls (all economic content roll calls if fewer).
4. Member votes from HSall_votes (yea = cast 1-3, nay = 4-6, other dropped), joined by key with declared cardinality.
5. Coverage: party x roll-call cells, share with both labels present, clusters.
Outputs: out/v0/rollcalls.csv, member_votes.csv.gz, coverage.json
"""
import json, re, sys
from pathlib import Path
import numpy as np, pandas as pd

V = Path(__file__).resolve().parents[1]
KIM = V.parent
sys.path.insert(0, str(KIM / "02_ideology_map" / "code"))
import map_common as dc  # noqa: E402  (paths and seeds defined once, R14)

O = V / "out" / "v0"; O.mkdir(parents=True, exist_ok=True)
KEY = ["congress", "chamber", "rollnumber"]
DATA = KIM / "01_rollcall_scales" / "out" / "data"
VV = KIM / "data" / "voteview_all"
rep = {}

# ---- 1. rows and voting quadrants (same code path as 06_vote_vs_map.py lines 16-18, 30-33, 79-82) ----
quad = lambda x, y: pd.Series(np.where(x > 0, "ER-", "EL-"), index=getattr(x, "index", None)) + np.where(y > 0, "ST", "SP")
sc = pd.read_csv(dc.ISSUE_SCALES); sc = sc[sc.issue.isin(["economic", "abortion"])]
w = sc.pivot_table(index=["congress", "chamber", "icpsr"], columns="issue", values="rc_score").reset_index()
m = pd.read_csv(dc.OUT / "qwen" / "s3" / "temporal_member_scores.csv")
assert len(m) == 21288, len(m)
m["cc"] = m.congress.astype(str) + m.chamber
j = m.merge(w, on=["congress", "chamber", "icpsr"], how="left", validate="one_to_one")
v = j[(j.congress >= 93) & j.party.isin(["Democrat", "Republican"])].dropna(subset=["economic", "abortion"]).copy()
for c in ["economic", "abortion"]:
    v[f"hi_{c}"] = v[c] > v.groupby("cc")[c].transform("median")
v["vote_q"] = quad(v.hi_economic.astype(int) - 0.5, v.hi_abortion.astype(int) - 0.5)
v["cp"] = v.vote_q.isin(["EL-ST", "ER-SP"]).astype(int)
sealed = json.load(open(dc.OUT / "s4" / "vote_vs_map.json"))["qwen"]["n"]
assert len(v) == sealed, (len(v), sealed)
rep["rows"] = dict(n=int(len(v)), sealed_n=int(sealed), cross_share=round(float(v.cp.mean()), 4),
                   by_quadrant=v.vote_q.value_counts().to_dict())
rows = v[["congress", "chamber", "icpsr", "name", "state", "party", "known", "vote_q", "cp", "dim1"]]

# ---- 2. roll calls ----
irc = pd.read_csv(DATA / "issue_rollcalls.csv")
irc = irc[irc.contested & irc.issue.isin(["economic", "abortion"])]
cells = v[["congress", "chamber"]].drop_duplicates()
irc = irc.merge(cells, on=["congress", "chamber"], how="inner")
dup = irc.duplicated(KEY, keep=False)
rep["rollcalls_in_both_issues"] = int(dup.sum() / 2)          # a roll call both PAP-economic and abortion-matched: kept as abortion
irc = irc.sort_values("issue").drop_duplicates(KEY, keep="first")   # "abortion" sorts before "economic"
rc = pd.read_csv(VV / "HSall_rollcalls.csv", low_memory=False,
                 usecols=KEY + ["date", "bill_number", "vote_question", "vote_desc", "dtl_desc", "yea_count", "nay_count", "vote_result"])
irc = irc.merge(rc, on=KEY, how="left", validate="one_to_one", suffixes=("", "_vv"))
assert irc.yea_count.notna().all()

# Motion type. Procedural = the YEA side cannot be read from a description of the bill's content. Rule fixed before any model run
# (revised once on 2026-10-20 after the first pass matched words inside descriptions, e.g. COMMIT in COMMITTEE; no model output existed).
# Recent roll calls: Voteview's vote_question. Older ones (vote_question empty): the leading phrase of dtl_desc ("TO AMEND ...").
PROC_Q = r"\bTABLE\b|RECOMMIT|PREVIOUS QUESTION|CLOTURE|PROCEED|ADJOURN|INSTRUCT|RECONSIDER|QUORUM|POINT OF ORDER|WAIVE|POSTPONE|\bCOMMIT\b|DISCHARGE|APPEAL|CHAIR|EXHIBITS|\bRULES? OF\b"
CONTENT_Q = r"PASS|AMENDMENT|AGREE|RESOLUTION|CONFERENCE REPORT|VETO|CONCUR|ADOPT|RECEDE|INSIST"
CONTENT_D = ("TO AMEND", "TO AGREE", "TO CONCUR", "TO PASS", "TO ADOPT", "TO MODIFY", "TO RECEDE", "TO INSIST", "TO PERSIST",
             "TO SUSPEND", "TO OVERRIDE", "AN AMENDMENT")
PROC_D = ("TO TABLE", "TO RECOMMIT", "TO CLOSE", "TO RISE", "TO RECONSIDER", "TO RULE", "TO AFFIRM", "TO ORDER", "TO INVOKE",
          "TO ADJOURN", "TO DISCHARGE", "TO INSTRUCT", "TO WAIVE", "TO PROCEED")
RULE_RES = r"PROVIDING FOR (?:THE )?CONSIDERATION"          # special-rule resolutions: procedural even when the question says "agreeing"
def motion(row):
    q = str(row.vote_question or "").upper().strip()
    desc = (str(row.dtl_desc or "") + " " + str(row.vote_desc or "")).upper()
    if re.search(RULE_RES, desc): return "procedural", "rule_resolution"
    if q and q != "NAN":
        if re.search(PROC_Q, q): return "procedural", "vote_question"
        if re.search(CONTENT_Q, q): return "content", "vote_question"
        return "unclassified", "vote_question"
    lead = re.sub(r"^\(+", "", str(row.dtl_desc or "").upper().strip())
    if lead.startswith(PROC_D): return "procedural", "desc"
    if lead.startswith(CONTENT_D): return "content", "desc"
    if re.match(r"THAT THE (?:HOUSE|SENATE) (?:RECEDE|CONCUR|INSIST)|ON A SEPARATE VOTE .*TO AGREE|THE \w+ AMENDMENT", lead):
        return "content", "desc"                            # conference positions on an amendment's content
    return "unclassified", "desc"
irc[["motion", "motion_src"]] = irc.apply(lambda r: pd.Series(motion(r)), axis=1)
rep["motion_by_issue"] = irc.groupby(["issue", "motion"]).size().unstack(fill_value=0).to_dict(orient="index")

ab = irc[irc.issue == "abortion"]
ec = irc[irc.issue == "economic"]
take = []
for (c, ch), g in ab[ab.motion == "content"].groupby(["congress", "chamber"]):
    pool = ec[(ec.congress == c) & (ec.chamber == ch) & (ec.motion == "content")].sort_values("rollnumber")
    k = min(len(g), len(pool))
    if k:
        idx = np.random.default_rng(dc.seed_for("V-v0", c, ch) % 2**32).choice(len(pool), k, replace=False)
        take.append(pool.iloc[np.sort(idx)])
ec_s = pd.concat(take) if take else ec.iloc[:0]
sel = pd.concat([ab, ec_s]).copy()
sel["main"] = sel.motion.eq("content")
sel.sort_values(KEY).to_csv(O / "rollcalls.csv", index=False)
rep["selected"] = sel.groupby(["issue", "motion"]).size().unstack(fill_value=0).to_dict(orient="index")

# ---- 4. member votes (chunked; 700 MB file) ----
want = set(map(tuple, sel[KEY].values))
parts = []
for ch in pd.read_csv(VV / "HSall_votes.csv", usecols=KEY + ["icpsr", "cast_code"], chunksize=4_000_000,
                      dtype={"congress": "int16", "rollnumber": "int32", "icpsr": "int32", "cast_code": "int8"}):
    ch = ch[ch.congress.between(93, 117)]
    if ch.empty: continue
    mk = np.fromiter((x in want for x in zip(ch.congress, ch.chamber, ch.rollnumber)), bool, len(ch))
    parts.append(ch[mk])
votes = pd.concat(parts, ignore_index=True)
votes["actual"] = np.where(votes.cast_code.between(1, 3), 1, np.where(votes.cast_code.between(4, 6), 0, -1))
rep["votes_raw"] = int(len(votes)); rep["votes_not_cast"] = int((votes.actual < 0).sum())
votes = votes[votes.actual >= 0].drop(columns="cast_code")
# Voteview lists some member-roll-call pairs twice (found 2026-10-20 on first run). Identical duplicates are collapsed; pairs whose
# two records disagree are dropped and counted. The Study B scales used the first record (pivot aggfunc="first").
dk = KEY + ["icpsr"]
d2 = votes[votes.duplicated(dk, keep=False)]
conflict = d2.groupby(dk).actual.nunique().gt(1)
rep["duplicate_pairs"] = dict(pairs=int(d2[dk].drop_duplicates().shape[0]), conflicting=int(conflict.sum()))
bad = set(map(tuple, conflict[conflict].reset_index()[dk].values))
votes = votes[~np.fromiter((tuple(x) in bad for x in votes[dk].values), bool, len(votes))].drop_duplicates(dk)
assert not votes.duplicated(dk).any()
mv = votes.merge(rows, on=["congress", "chamber", "icpsr"], how="inner", validate="many_to_one")
mv = mv.merge(sel[KEY + ["issue", "motion", "main"]], on=KEY, how="left", validate="many_to_one")
assert mv.issue.notna().all()
rep["member_votes"] = dict(total=int(len(mv)), main=int(mv.main.sum()),
                           by_issue_main=mv[mv.main].groupby("issue").size().to_dict(),
                           rows_with_any_vote=int(mv[["congress", "chamber", "icpsr"]].drop_duplicates().shape[0]))
# party-majority baseline (from all actual D and R members in the row universe; ties recorded, not broken)
pm = mv.groupby(KEY + ["party"]).actual.mean().rename("party_yea_share").reset_index()
mv = mv.merge(pm, on=KEY + ["party"], how="left", validate="many_to_one")
mv["party_tie"] = mv.party_yea_share.eq(0.5)
mv["defect"] = np.where(mv.party_tie, np.nan, (mv.actual != (mv.party_yea_share > 0.5).astype(int)).astype(float))
mv.to_csv(O / "member_votes.csv.gz", index=False, compression="gzip")

# ---- 5. coverage for the preferred estimate (abortion content votes, party x roll-call FE) ----
cov = {}
for iss in ["abortion", "economic"]:
    d = mv[mv.main & (mv.issue == iss)]
    g = d.groupby(KEY + ["party"]).cp.agg(["min", "max", "size"])
    ident = g[(g["min"] == 0) & (g["max"] == 1)]
    d_id = d.merge(ident.reset_index()[KEY + ["party"]], on=KEY + ["party"], how="inner")
    cov[iss] = dict(member_votes=int(len(d)), rollcalls=int(d[KEY].drop_duplicates().shape[0]),
                    members=int(d.icpsr.nunique()), party_rollcall_cells=int(len(g)), cells_with_both_labels=int(len(ident)),
                    share_votes_in_identifying_cells=round(len(d_id) / max(len(d), 1), 4),
                    cp_share=round(float(d.cp.mean()), 4),
                    actual_defection_rate=dict(aligned=round(float(d[d.cp == 0].defect.mean()), 4),
                                               cross=round(float(d[d.cp == 1].defect.mean()), 4)),
                    party_baseline_accuracy=dict(aligned=round(1 - float(d[d.cp == 0].defect.mean()), 4),
                                                 cross=round(1 - float(d[d.cp == 1].defect.mean()), 4)))
rep["coverage_main"] = cov
json.dump(rep, open(O / "coverage.json", "w"), indent=1, default=str)
print(json.dumps(rep, indent=1, default=str))
