# 03_gun_inputs

Writes the issue-scale table with the gun scale in the social slot, so that the map analyses can be rerun on guns with the same scripts (environment variables `ISSUE_SCALES` and `SOCIAL_TAG`).

Used in: Appendix C.1, C.6.

Pipeline steps (1): `gunsym.scales`.

Run everything through `python run_pipeline.py` from `replication/`; outputs go to `out/` (or `analysis/results*` for the R analyses).
