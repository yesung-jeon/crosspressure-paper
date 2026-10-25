# 06_vote_prediction

Selects abortion, economic and gun roll calls, holds their neutral descriptions (code/not_run: written and checked by language models; not rerun, they ship as fixed inputs), builds the prompts, scores every member vote with both models (GPU, both answer orders) and estimates the cross-pressured minus aligned accuracy, the leave-one-out definition and the error direction.

Used in: Section 6; Appendix D.

Run by `run_pipeline.py` (see `../README.md`); its outputs are checked against `validation/SEAL.json` by `tools/validate.py`.
