# 02_gun_scale

Finds gun-control roll calls, combines the two model labels and the authors' adjudications (shipped as fixed inputs), builds the gun-control scale for the Congress-chamber cells that pass the scale checks, and computes map recall on guns.

Used in: Appendix A.3, C.1.

Pipeline steps (4): `gunscale.g0_candidates`, `gunscale.g0_labels_claude`, `gunscale.g0_scale`, `gunscale.g1`.

Run everything through `python run_pipeline.py` from `replication/`; outputs go to `out/` (or `analysis/results*` for the R analyses).
