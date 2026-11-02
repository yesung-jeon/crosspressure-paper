# 10_vote_prediction

Selects abortion, economic and gun roll calls, builds the neutral descriptions (written and checked by language models before the run; shipped as fixed inputs) and the prompts, scores each member's vote in both answer orders, and estimates accuracy gaps within party and roll call with two-way clustered intervals; leave-one-out labels, error direction, task checks. Protocol and the task-check amendment in `protocol/`.

Used in: Section 6; Appendix D.1-D.6, D.9.

Pipeline steps (31; GPU: 12): `votes.A12_loo_cp`, `votes.A13_error_direction`, `votes.g2_descriptions`, `votes.g2_diagnose.llama`, `votes.g2_diagnose.qwen`, `votes.g2_error_direction`, `votes.g2_estimate.llama`, `votes.g2_estimate.qwen`, `votes.g2_gate`, `votes.g2_prompts`, `votes.g2_rollcalls`, `votes.v0`, `votes.v3`, `votes.v3b`, `votes.v4.llama.economic`, `votes.v4.llama.guns`, `votes.v4.llama.pilot`, `votes.v4.llama.swap_abortion`, `votes.v4.llama.swap_economic`, `votes.v4.llama.swap_guns`, `votes.v4.qwen.economic`, `votes.v4.qwen.guns`, `votes.v4.qwen.pilot`, `votes.v4.qwen.swap_abortion`, `votes.v4.qwen.swap_economic`, `votes.v4.qwen.swap_guns`, `votes.v5.llama`, `votes.v5.qwen`, `votes.v5_synthetic`, `votes.v5c.llama`, `votes.v5c.qwen`.

Run everything through `python run_pipeline.py` from `replication/`; outputs go to `out/` (or `analysis/results*` for the R analyses).
