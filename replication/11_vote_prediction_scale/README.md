# 11_vote_prediction_scale

Vote predictions read from the nine-point answer scale: accuracy gaps, comparison with the two-answer format on the same prompt, squared error, and the scale task checks. Protocol in `protocol/`.

Used in: Section 6; Appendix D.10, Table D1.

Pipeline steps (4): `scaleacc.checks`, `scaleacc.checks2`, `scaleacc.run`, `scaleacc.s6`.

Run everything through `python run_pipeline.py` from `replication/`; outputs go to `out/` (or `analysis/results*` for the R analyses).
