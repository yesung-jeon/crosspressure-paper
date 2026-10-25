"""Shared definitions for Study S (PROTOCOL_S.md): paths, archive access, vocabulary rule, speaker-member link rule, leave-out partisanship."""
import io, re, sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy import sparse

R = Path(__file__).resolve().parents[1]; KIM = R.parent                   # replication/ (rebuild)
sys.path.insert(0, str(KIM / "01_rollcall_scales" / "code")); sys.path.insert(0, str(KIM / "02_ideology_map" / "code"))
import speech_zipfix as zipfix  # noqa: E402
import map_common as dc  # noqa: E402
O = R / "out"; S0 = O / "s0"
EDITIONS = {"bound": range(80, 112), "daily": range(97, 115)}
MAIN = {**{c: "bound" for c in range(80, 112)}, **{c: "daily" for c in range(112, 115)}}       # GST: bound through 111, daily after
PROC = {"mr speaker", "mr presid", "madam speaker", "madam presid", "unanim consent", "ask unanim", "without object", "quorum call",
        "absenc quorum", "suggest absenc", "point order", "previou question", "reserv balanc", "balanc time", "yield back", "yield minut",
        "yield time", "gentleman yield", "gentlewoman yield", "senat yield", "distinguish gentleman", "distinguish senat",
        "consent request", "clerk call", "clerk will", "the clerk", "the chair"}
MIN_SPEAKERS, MIN_COUNT = 10, 20
_Z = {}


def archive(ed):
    if ed not in _Z: _Z[ed] = zipfix.open_fixed(KIM / "data" / "congress_text" / f"hein-{ed}.zip")
    return _Z[ed]


def member(ed, fname):
    hits = [n for n in archive(ed).namelist() if not n.startswith("__MACOSX") and n.split("/")[-1] == fname]
    if len(hits) != 1: raise SystemExit(f"STOP: expected one {fname} in {ed}, found {hits[:5]}")
    return hits[0]


def read_bar(ed, fname, **kw):
    raw = archive(ed).read(member(ed, fname)).decode("latin-1")
    return pd.read_csv(io.StringIO(raw), sep="|", quoting=3, on_bad_lines="skip", **kw)


def speaker_map(ed, c):
    sm = read_bar(ed, f"{c:03d}_SpeakerMap.txt", dtype=str); sm.columns = [x.strip().lower() for x in sm.columns]
    return sm


def voteview():
    V = pd.read_csv(KIM / "data" / "HSall_members.csv", low_memory=False)
    V = V[V.chamber.isin(["House", "Senate"]) & V.party_code.isin([100, 200])].drop_duplicates(["congress", "icpsr"])
    V["last"] = V.bioname.str.split(",").str[0].str.upper().str.replace(r"[^A-Z]", "", regex=True)
    V["firstn"] = V.bioname.str.split(",").str[1].fillna("").str.strip().str.split().str[0].str.upper().str.replace(r"[^A-Z]", "", regex=True)
    return V


def link(sm, V, c):
    """the rule of 01_rollcall_scales/16_speech_prep.py, line for line (gate L checks identity); returns (links, ledger, multi-match ids)"""
    sm = sm.copy()
    sm["last"] = sm.lastname.str.upper().str.replace(r"[^A-Z]", "", regex=True); sm["firstn"] = sm.firstname.fillna("").str.upper().str.replace(r"[^A-Z]", "", regex=True)
    sm["chamber_v"] = sm.chamber.map({"H": "House", "S": "Senate"})
    spk = sm.drop_duplicates("speakerid")[["speakerid", "last", "firstn", "chamber_v", "state", "party"]]
    vc = V[V.congress == c][["icpsr", "last", "firstn", "chamber", "state_abbrev", "party_code"]]
    cand = spk.merge(vc, left_on=["last", "chamber_v", "state"], right_on=["last", "chamber", "state_abbrev"], how="left", suffixes=("", "_v"))
    n_c = cand.groupby("speakerid").icpsr.nunique(); amb = n_c[n_c > 1].index
    cand.loc[cand.speakerid.isin(amb), "keep"] = cand.firstn.str[:3] == cand.firstn_v.fillna("").str[:3]
    cand.loc[~cand.speakerid.isin(amb), "keep"] = True
    kept = cand[cand.keep.astype(bool) & cand.icpsr.notna()]
    multi = set(kept.groupby("speakerid").icpsr.nunique().loc[lambda s: s > 1].index)        # still more than one member after the rule
    lk = kept.drop_duplicates("speakerid"); lk = lk[~lk.speakerid.duplicated(keep=False)]
    pv = lk.party_code.map({100.0: "D", 200.0: "R"}); agree = float((pv == lk.party).mean()) if len(lk) else np.nan
    led = dict(speakers=int(len(spk)), linked=int(len(lk)), ambiguous=int(len(amb)), multi_after_rule=int(len(multi)), party_agreement=agree,
               voteview_DR_members=int(len(vc)), voteview_members_linked_share=float(vc.icpsr.isin(lk.icpsr).mean()))
    return lk.assign(congress=c)[["congress", "speakerid", "icpsr", "party", "party_code", "chamber_v"]], led, multi


def load_matrix(ed, c, proc=True):
    """CSR speakers x phrases (filtered), speaker table, phrase list; proc=True drops the procedural phrases (main), False keeps them"""
    z = np.load(S0 / f"{ed}_{c:03d}.npz", allow_pickle=False)
    X = sparse.csr_matrix((z["data"], z["indices"], z["indptr"]), shape=tuple(z["shape"]))
    spk = pd.read_csv(S0 / f"{ed}_{c:03d}_speakers.csv", dtype={"speakerid": str, "index": str})
    spk = spk.rename(columns={"index": "speakerid"})              # s0_prep wrote the row order's name as "index" (reset_index of an unnamed Index)
    assert len(spk) == X.shape[0] and spk.speakerid.notna().all()
    if proc: X = X[:, ~z["proc"]]
    return X, spk


def leave_out(X, rep, w=None):
    """GST leave-out partisanship. X CSR counts (speakers x phrases), rep bool (True = R). w speaker weights (bootstrap; default 1).
    Returns (pi, p) with p_i the speaker's mean leave-out probability of its own party; weights multiply speakers in party totals and
    in the party means; the leave-out removes all w_i copies of the speaker (one copy before the 2026-10-23 fix)."""
    n = X.shape[0]; w = np.ones(n) if w is None else w
    m = np.asarray(X.sum(1)).ravel()
    CR = np.asarray(X.T @ (w * rep)).ravel(); CD = np.asarray(X.T @ (w * ~rep)).ravel()
    MR, MD = float(m @ (w * rep)), float(m @ (w * ~rep))
    Xc = X.tocoo(); i, j, v = Xc.row, Xc.col, Xc.data.astype(float)
    r = rep[i]
    own_c = np.where(r, CR[j], CD[j]) - w[i] * v; own_m = np.where(r, MR, MD) - w[i] * m[i]
    oth = np.where(r, CD[j] / MD, CR[j] / MR)
    qown = own_c / np.where(own_m > 0, own_m, np.nan)
    den = qown + oth
    rho = np.where(den > 0, qown / np.where(den > 0, den, 1), 0.5)
    p = np.bincount(i, weights=v / m[i] * rho, minlength=n)
    sel = w > 0
    pi = 0.5 * np.average(p[rep & sel], weights=w[rep & sel]) + 0.5 * np.average(p[~rep & sel], weights=w[~rep & sel])
    return float(pi), p
