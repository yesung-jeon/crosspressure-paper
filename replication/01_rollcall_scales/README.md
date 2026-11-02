# 01_rollcall_scales

Builds the economic and abortion roll-call scales for every Congress and chamber from Voteview votes, with economic roll calls defined by Policy Agendas Project topics (first principal component of the centred vote matrix, oriented so that higher is more conservative). Also links floor-speech speakers to members.

Used in: Section 3; Appendix A.2-A.3.

Pipeline steps (1): `scales.issue_scales`.

Run everything through `python run_pipeline.py` from `replication/`; outputs go to `out/` (or `analysis/results*` for the R analyses).
