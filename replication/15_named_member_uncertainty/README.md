# 15_named_member_uncertainty

Named-member yes/no questions: re-projection of the map, scoring, and entropy and consistency comparisons (R, fixest), on abortion and guns. Protocol in `protocol/`.

Used in: Section 7; Appendix E.2-E.3.

Pipeline steps (16; GPU: 6): `named.R1.llama`, `named.R1.qwen`, `named.R1b`, `named.R2.llama`, `named.R2.qwen`, `named.guns`, `named.map.llama`, `named.map.qwen`, `named.prepare.llama`, `named.prepare.qwen`, `named.prepare_fake.llama`, `named.prepare_fake.qwen`, `named.run`, `named.run_fake`, `named.yesno.llama`, `named.yesno.qwen`.

Run everything through `python run_pipeline.py` from `replication/`; outputs go to `out/` (or `analysis/results*` for the R analyses).
