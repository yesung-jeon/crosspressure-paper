# 16_scale_uncertainty

Scores the vote and named-member questions on answer scales (1-9; named members also 1-7) and estimates entropy differences with Holm-adjusted p values. Protocols in `protocol/`.

Used in: Sections 6-7; Appendix D.10, E.

Pipeline steps (8; GPU: 4): `scaleH.analyze`, `scaleH.analyze9`, `scaleH.check9`, `scaleH.score.llama`, `scaleH.score.qwen`, `scaleH.score9.llama`, `scaleH.score9.qwen`, `scaleH.synthetic`.

Run everything through `python run_pipeline.py` from `replication/`; outputs go to `out/` (or `analysis/results*` for the R analyses).
