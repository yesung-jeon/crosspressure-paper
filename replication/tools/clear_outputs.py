#!/usr/bin/env python
"""Remove the shipped outputs before a full Path A rerun, so every step recomputes instead of resuming from shipped part files.

Removes every file listed in validation/SEAL.json, the regenerated-only files (*.rds, *_input.csv.gz, 12 S0 matrices), the pipeline
logs and done markers. Frozen inputs (MANIFEST.json "frozen") and code
are never touched; restore the shipped outputs with `git checkout -- .`. Path B needs the shipped outputs, so do not run this before Path B.
Usage: python tools/clear_outputs.py --yes"""
import json, shutil, sys
from pathlib import Path

R = Path(__file__).resolve().parents[1]
if "--yes" not in sys.argv: sys.exit(__doc__)
seal = json.load(open(R / "validation" / "SEAL.json", encoding="utf-8"))["files"]
listed = set(json.load(open(R / "MANIFEST.json", encoding="utf-8"))["files"])   # code and frozen inputs
clash = sorted(set(seal) & listed)
assert not clash, f"sealed outputs that are MANIFEST files (code or frozen inputs): {clash[:5]}"
n = 0
for rel in seal:
    p = R / rel
    if p.is_file(): p.unlink(); n += 1
# regenerated-only files that are never shipped or sealed (fixest objects, model input copies, speech matrices): a step that resumes
# from existing files (12 S0 skips finished .npz) must not find a previous run's copies (Codex round 3)
regen = [p for s in sorted(R.glob("[01][0-9]_*")) for pat in ("*.rds", "*_input.csv.gz") for p in s.rglob(pat)]
regen += [p for p in (R / "12_speech_and_state" / "out" / "s0").rglob("*") if p.is_file()]
clash = sorted(p.relative_to(R).as_posix() for p in regen if p.relative_to(R).as_posix() in listed)
assert not clash, f"regenerated-only files that are MANIFEST files: {clash[:5]}"
for p in regen: p.unlink()
shutil.rmtree(R / "logs" / "pipeline", ignore_errors=True)
print(f"removed {n} shipped output files, {len(regen)} regenerated-only files and logs/pipeline; run: python run_pipeline.py --path A")
