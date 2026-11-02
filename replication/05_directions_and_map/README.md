# 05_directions_and_map

Extracts the economic and social directions from paired instructions, steers and judges at every layer to choose the layer (twice, as a stability gate), projects every member-Congress onto the two directions (the map), compares map quadrants with vote quadrants, places the 60 members selected by their votes, and runs the stated-profile task.

Used in: Sections 3 and 5; Appendix A.4-A.5, C.1-C.5.

Pipeline steps (31; GPU: 16): `map.layercheck`, `map.lc.s1.llama`, `map.lc.s1.qwen`, `map.lc.s2gen.llama`, `map.lc.s2gen.qwen`, `map.lc.s2judge.llama`, `map.lc.s2judge.qwen`, `map.lc.s2rule.llama`, `map.lc.s2rule.qwen`, `map.s1.llama`, `map.s1.qwen`, `map.s2gen.llama`, `map.s2gen.qwen`, `map.s2judge.llama`, `map.s2judge.qwen`, `map.s2rule.llama`, `map.s2rule.qwen`, `map.s3.llama`, `map.s3.qwen`, `map.s4`, `map.s4_guns`, `map.s4b_select`, `map.s4c_positions`, `map.s4c_select`, `map.s4d`, `map.s4d_guns`, `map.s5.llama`, `map.s5.qwen`, `map.s5_analyze`, `map.s5_select`, `map.selection_report`.

Run everything through `python run_pipeline.py` from `replication/`; outputs go to `out/` (or `analysis/results*` for the R analyses).
