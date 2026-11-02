#!/usr/bin/env python
"""Code check for analyze_named9.py (run before the 1-9 data exist): pointed at the sealed 1-7 named outputs, named9() must reproduce
every named row of the sealed ../out/results.csv (H7 -> H9 column name only). Prints the largest difference; exits 1 on any mismatch."""
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze as A  # noqa: E402
import analyze_named9 as N  # noqa: E402

S = pd.read_csv(A.O / "results.csv"); S = S[S.task == "named"].copy()
S["quantity"] = S.quantity.replace({"H7": "H9", "H7_minus_H": "H9_minus_H"})
rows = []
for m in A.MODELS:
    N.named9(m, rows, task="named", n=7)
T = pd.DataFrame(rows)
k = ["model", "issue", "quantity"]
J = T.merge(S, on=k, suffixes=("", "_s"), validate="one_to_one")
assert len(J) == len(T) == len(S), (len(J), len(T), len(S))
worst = max(float((J[c] - J[c + "_s"]).abs().max()) for c in ["b", "lo95", "hi95", "p", "mean_cp", "mean_aligned"]) + float((J.n != J.n_s).sum())
print("rows", len(J), "largest difference", worst)
sys.exit(0 if worst < 1e-12 else 1)
