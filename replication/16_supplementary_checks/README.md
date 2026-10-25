# 16_supplementary_checks

Checks reported in the paper: the two-dimensional DW-NOMINATE placement and recognized members (benchmark), placement by decade (members_by_era), the noise-only map (noise_benchmark), the no-persona package effect, the vote prompts (w1), the repeated layer choice (layercheck) and the named senators (cases).

Used in: Sections 3, 5, 6; Appendix C, D.

Run by `run_pipeline.py` (see `../README.md`); its outputs are checked against `validation/SEAL.json` by `tools/validate.py`.
