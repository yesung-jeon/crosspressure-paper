# 18_economic_weight

Within-party weight of economic and social votes on the map, and whether misplaced members follow their party or their economic side; synthetic checks for each analysis.

Used in: Section 8; Appendix F.1.

Pipeline steps (18; GPU: 4): `mechanism.X1`, `mechanism.X2`, `mechanism.X3`, `mechanism.X4`, `mechanism.X4_familiarity.llama`, `mechanism.X4_familiarity.qwen`, `mechanism.X5A`, `mechanism.X5B`, `mechanism.X5_layers.llama`, `mechanism.X5_layers.qwen`, `mechanism.X5_reproduce.llama`, `mechanism.X5_reproduce.qwen`, `mechanism.X5_threeway`, `mechanism.synth_check`, `mechanism.synth_check_x2`, `mechanism.synth_check_x3`, `mechanism.synth_check_x4`, `mechanism.synth_check_x5`.

Run everything through `python run_pipeline.py` from `replication/`; outputs go to `out/` (or `analysis/results*` for the R analyses).
