# 00_shared

Shared code: the model loader (bf16 at pinned revisions, deterministic mode, GPU memory cap), shared constants, and the median-split rule used for every quadrant (`splits.py`: members tied at the median go to whichever half keeps the split closer to even).

Used in: every analysis.
