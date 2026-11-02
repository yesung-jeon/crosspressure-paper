# 14_vote_uncertainty

Entropy of the two-answer vote predictions, cross-pressured minus aligned members within party and roll call (R, fixest), with a frozen-baseline check, reconstruction of every fit and a synthetic check. Protocol in `protocol/` (its sha256 is checked before fitting).

Used in: Section 7; Appendix E.1-E.2.

Pipeline steps (2): `uncertainty.prepare`, `uncertainty.run`.

Run everything through `python run_pipeline.py` from `replication/`; outputs go to `out/` (or `analysis/results*` for the R analyses).
