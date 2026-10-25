#!/usr/bin/env python
"""Checks for Study V (W1 roll-call vote prediction) used by the replication scripts (kim/review/w1_pipeline_2026-10-21/PLAN.md + A0).
  content <parquet> ...   print the content hash of each prompt table (rows sorted by pid, every column, written as CSV; independent
                          of the parquet writer's bytes)
  prompts                 path B: the prompt tables rebuilt by 02_build_prompts.py / 03_build_swap_prompts.py must have the sealed content hashes
                          (sealed/06_vote_prediction/out/v3/prompts_content_sha256.json)
  smoke <model> ...       path A smoke: the new out/v4/<model>/smoke.json against the sealed one; at least 19 of 20 greedy generations
                          equal and accuracy within 0.05 (rule fixed before any run, PLAN A0)
Exit status 1 on any failure."""
import hashlib, json, sys
from pathlib import Path
import pandas as pd

R = Path(__file__).resolve().parents[2]; V = R / "06_vote_prediction"; S = R / "06_vote_prediction" / "protocol"   # reference hashes of the sealed FP8 prompt tables
TABLES = ["prompts.parquet", "prompts_swap.parquet"]


# Rebuild 2026-10-23: the prompt tables also carry model- and rule-dependent metadata (known = the Qwen map's party recall; cp, vote_q =
# quadrants under the tie rule). Those change by design with bf16 and the tie rule, so "prompts" now checks every other column (pid, key,
# roll call, member, actual vote, text, ...) against prompts_fixed_sha256.json, made with the same function from the sealed FP8 tables.
MODEL_DEPENDENT = ["known", "cp", "vote_q"]


def content_sha(path, drop=()):
    d = pd.read_parquet(path).drop(columns=list(drop), errors="ignore").sort_values("pid", kind="mergesort").reset_index(drop=True)
    return hashlib.sha256(d.to_csv(index=False, float_format="%.10g", lineterminator="\n").encode("utf-8")).hexdigest()


def main(argv):
    mode = argv[0] if argv else ""
    if mode == "content":
        for p in argv[1:]: print(content_sha(p), p)
        return 0
    if mode == "prompts":
        seal = json.load(open(S / "prompts_fixed_sha256.json", encoding="utf-8"))
        bad = [t for t in TABLES if content_sha(V / "out" / "v3" / t, MODEL_DEPENDENT) != seal[t]]
        print("W1 prompts (columns other than " + ", ".join(MODEL_DEPENDENT) + "): " + ("equal to sealed" if not bad else f"DIFFERENT: {bad}"))
        return 1 if bad else 0
    if mode == "smoke":
        ok = True
        for m in argv[1:]:
            new = json.load(open(V / "out" / "v4" / m / "smoke.json", encoding="utf-8"))
            old = json.load(open(S / "out" / "v4" / m / "smoke.json", encoding="utf-8"))
            same = sum(a == b for a, b in zip(new["generations"], old["generations"]))
            dacc = abs(new["accuracy"] - old["accuracy"])
            pas = same >= 19 and len(new["generations"]) == len(old["generations"]) == 20 and dacc <= 0.05
            print(f"W1 smoke {m}: generations equal {same}/20, accuracy {new['accuracy']:.3f} vs sealed {old['accuracy']:.3f} -> "
                  f"{'PASS' if pas else 'FAIL'}")
            ok &= pas
        return 0 if ok else 1
    print(__doc__); return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
