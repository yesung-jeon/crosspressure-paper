#!/usr/bin/env python
"""Seal Study V outputs as they stand: SHA256 of protocols, seals, code, estimate files, description seal, and a manifest of every
model-output part (per folder: file count, vote count, and a hash over the sorted per-file hashes). Prose and later analyses read
these files; they are not refitted. Usage: python seal_release.py 2026-10-21  ->  RELEASE_SEAL_<date>.json"""
import hashlib, json, sys
from pathlib import Path

import pandas as pd

V = Path(__file__).resolve().parents[1]
tag = sys.argv[1]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


files = sorted([*V.glob("PROTOCOL*.md"), *V.glob("PROTOCOL_SEAL*.json"), *V.glob("*.md"), *(V / "code").glob("*.py"),
                *(V / "code").glob("*.ps1"), *(V / "code").glob("*.md"), *(V / "code").glob("*.json"),
                *(V / "out" / "v5").glob("*.json"), *(V / "out" / "v5").glob("*.parquet"),
                *(V / "out" / "v1").glob("DESCRIPTIONS_SEAL.json"), *(V / "out" / "v3").glob("*.csv"), *(V / "out" / "v3").glob("*.parquet")])
out = {"tag": tag, "files": {str(p.relative_to(V)).replace("\\", "/"): sha(p) for p in dict.fromkeys(files)}, "parts": {}}
for d in sorted((V / "out" / "v4").glob("*/*/")):
    ps = sorted(d.glob("part_*.parquet"))
    if not ps:
        continue
    hs = [sha(p) for p in ps]
    out["parts"][str(d.relative_to(V)).replace("\\", "/")] = {
        "files": len(ps), "done": len(list(d.glob("part_*.done"))),
        "votes": int(sum(len(pd.read_parquet(p, columns=["pid"])) for p in ps)),
        "complete_run_json": (d / "run.json").exists(), "sha256_of_part_hashes": hashlib.sha256("".join(hs).encode()).hexdigest()}
dst = V / f"RELEASE_SEAL_{tag}.json"
dst.write_text(json.dumps(out, indent=1), encoding="utf-8")
print(dst.name, len(out["files"]), "files,", len(out["parts"]), "part folders")
for k, v in out["parts"].items():
    print(f"  {k}: {v['files']} parts, {v['done']} done, {v['votes']} votes, complete={v['complete_run_json']}")
