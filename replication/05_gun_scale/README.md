# 05_gun_scale

Finds gun-control roll calls, applies the labels (code/not_run: written by two language models and the authors; not rerun, the labels ship as fixed inputs) and builds the gun scale for the Congress-chamber cells that pass its checks.

Used in: Section 3; Appendix A.3.

Run by `run_pipeline.py` (see `../README.md`); its outputs are checked against `validation/SEAL.json` by `tools/validate.py`.
