# 08_supplementary_checks

Checks behind Sections 5 and 6: recall benchmarks (two-dimensional DW-NOMINATE, recognized members, dimension-2 orientation), members by decade, the noise-only map, the vote-prompt checks, agreement of the two answer orders, the named cases, data for Figures 1, 3 and B4, and the layer stability check.

Used in: Sections 5-6; Appendix C.1, C.2, C.6, D.3, D.9.

Pipeline steps (13): `checks.benchmark`, `checks.benchmark_guns`, `checks.cases`, `checks.dw2_orientation`, `checks.figure_data`, `checks.members_by_era`, `checks.members_by_era_guns`, `checks.no_persona`, `checks.noise_benchmark`, `checks.noise_benchmark_guns`, `checks.order_corr`, `checks.w1_prompts`, `map.layercheck`.

Run everything through `python run_pipeline.py` from `replication/`; outputs go to `out/` (or `analysis/results*` for the R analyses).
