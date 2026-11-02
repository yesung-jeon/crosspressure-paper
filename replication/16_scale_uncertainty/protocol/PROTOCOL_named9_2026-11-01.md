# Named-member questions on the 1-9 scale (amendment, 2026-11-01)

Why: the vote task uses a 1-9 scale and the named-member questions a 1-7 scale, for no recorded reason. The named-member questions are
rescored on the 1-9 scale of the vote task.

Design (fixed before scoring):
- Rows, personas, items, prefill ("Answer: "), digit read-out and forward pass: exactly as the 1-7 named task in code/score_scale.py
  (task "named"). Only the instruction changes:
  asc " Answer with a single number from 1 to 9, where 1 means definitely no and 9 means definitely yes."
  desc " Answer with a single number from 1 to 9, where 1 means definitely yes and 9 means definitely no."
- New task "named9" in score_scale.py (default tasks unchanged); outputs out/named9/<m>/part_*.parquet. Pipeline step
  scaleH.score9.<m> (GPU, batch 1).
- Smoke before the real run (both models, real weights, batch 1 as production): bitwise repeat, digit mass median >= 0.9, format
  failure < 5%, greedy first token a digit >= 95%. Stop if any fails.
- Analysis code/analyze_named9.py: the same estimator and definitions as analyze.py named(): H9 = entropy over 9 digits / log2 9 per
  cell, cells with digit mass < 0.5 dropped, member-Congress mean, one-way FE (party x Congress x chamber), member CR1; rows
  abortion (vote CP), abortion (map CP), guns (gun CP). Holm over the three H9 rows per model; a difference reads as higher or lower
  when its 95% interval excludes 0 and its Holm-adjusted p is below .05.
- The 1-7 outputs (out/named) are not changed.
