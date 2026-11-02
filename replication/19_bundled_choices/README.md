# 19_bundled_choices

Bundled-choice battery (calibration, scoring, analysis); its outputs feed the no-persona check and the economic-weight analyses.

Used in: inputs of 08 and 18.

Pipeline steps (6; GPU: 4): `bundles.l0.llama`, `bundles.l0.qwen`, `bundles.l1.llama`, `bundles.l1.qwen`, `bundles.l2.llama`, `bundles.l2.qwen`.

Run everything through `python run_pipeline.py` from `replication/`; outputs go to `out/` (or `analysis/results*` for the R analyses).
