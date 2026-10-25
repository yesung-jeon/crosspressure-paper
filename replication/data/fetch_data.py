#!/usr/bin/env python
"""Fetch the raw data into replication/data/ and check each file against the exact copy the analyses used (sha256).

Rebuild 2026-10-23 (PLAN v0.2 §4.12): a sha256 mismatch now stops the run. Voteview re-estimates NOMINATE and Nokken-Poole scores for
every Congress at each update, so a newer download is a different input, not just extra 119th-Congress rows. --allow-drift continues
anyway and writes data/DRIFT.json; such a run is not a reproduction. The exact copies are archived for deposit (upload only after the
authors decide); place them in data/ to reproduce exactly.

Files not redistributed here: the Policy Agendas Project roll-call topics (rcv_voteview_v3_4.csv) and the MIT presidential returns
(1976-2024-president.csv): download them yourself (README, "Data"); this script checks their sha256. The Congressional Record text
(Gentzkow, Shapiro and Taddy, Stanford Digital Repository) is downloaded with resumption.

Usage:  python data/fetch_data.py [--allow-drift] [--skip-speech]
"""
import hashlib, json, subprocess, sys, urllib.request
from pathlib import Path

DATA = Path(__file__).resolve().parent
STANFORD = "https://stacks.stanford.edu/file/druid:md374tz9962/"
FILES = {  # name -> (url or None for manual, sha256 of the copy used, local path)
    "HSall_members.csv": ("https://voteview.com/static/data/out/members/HSall_members.csv",
                          "d78f55120b59534e99f30541469325059f953b210f0ddb6ebb54601c9303c0f6", DATA / "HSall_members.csv"),
    "HSall_rollcalls.csv": ("https://voteview.com/static/data/out/rollcalls/HSall_rollcalls.csv",
                            "98fcc6eac8d966557c4f10c3a64aaee321b88b68522bf339ee18da858f5b1988", DATA / "voteview_all" / "HSall_rollcalls.csv"),
    "HSall_votes.csv": ("https://voteview.com/static/data/out/votes/HSall_votes.csv",
                        "84eca8a15b9bfe3b50e37c346b9d9fe1198338c5b4bbfceef1114b27059e226e", DATA / "voteview_all" / "HSall_votes.csv"),
    # Policy Agendas Project, comparativeagendas.net/project/us/datasets (not redistributed)
    "rcv_voteview_v3_4.csv": (None, "f4d95c110d7b55e07720ea050fd10dfbe82fe4d61d1c89c8dae5246c45504ac8", DATA / "agendas" / "rcv_voteview_v3_4.csv"),
    # MIT Election Data and Science Lab, U.S. President 1976-2024, Harvard Dataverse doi:10.7910/DVN/42MVDX (not redistributed)
    "1976-2024-president.csv": (None, "9936410a6dd4ecc8be7fe202c6dff5b5f8fee59d88f35ab542ed12879941dcb7", DATA / "elections" / "1976-2024-president.csv"),
    "hein-bound.zip": (STANFORD + "hein-bound.zip", "391307c149d54f365768ec1f7eac19f46ec391b1b1529bee3c82f9d7999aa240", DATA / "congress_text" / "hein-bound.zip"),
    "hein-daily.zip": (STANFORD + "hein-daily.zip", "0d44564769d826f3c1af40410e9d922d397f8143e2fa039364cbb010b0729c9d", DATA / "congress_text" / "hein-daily.zip"),
}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()


bad, drift = [], {}
for n, (url, ref, dst) in FILES.items():
    if "--skip-speech" in sys.argv and n.startswith("hein-"): continue
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists():
        if url is None:
            print(f"{n}: missing; download it into {dst.parent} (README, 'Data')"); bad.append(n); continue
        print("downloading", url)
        if n.startswith("hein-"):        # large archives: resumable curl
            subprocess.run(["curl", "-sL", "--retry", "5", "-C", "-", "-o", str(dst), url], check=True)
        else:
            urllib.request.urlretrieve(url, dst)
    h = sha(dst)
    if h == ref: print(f"{n}: sha256 matches the copy the analyses used")
    else: print(f"{n}: sha256 DIFFERS ({h})"); bad.append(n); drift[n] = h
if bad:
    if "--allow-drift" in sys.argv and not [n for n in bad if n not in drift]:
        json.dump(drift, open(DATA / "DRIFT.json", "w"), indent=1); print("--allow-drift: continuing; this run is NOT a reproduction (data/DRIFT.json)")
    else:
        sys.exit(f"STOP: inputs missing or different from the copies the analyses used: {bad}")
