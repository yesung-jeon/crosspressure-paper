# Continuous answer scales for the entropy analysis: protocol (2026-10-29)

> Note for the replication package: written before any output of this analysis, for the bf16 run of Qwen2.5-7B-Instruct and
> Llama-3.1-8B-Instruct that the paper reports. The reading rule the paper uses (Appendix E.2) later dropped the minimum size of 0.05
> below: a difference reads as higher or lower when its 95% interval excludes zero and its Holm-adjusted p is below .05. The named-member
> part (A) was later rescored on the 1-9 scale (`PROTOCOL_named9_2026-11-01.md`). Internal file references have been removed.

## Request
- The coauthors asked whether the two-option entropy compresses the models' uncertainty and suggested looking at it continuously.
- The current entropy already uses the continuous next-token probability over the two options. What can compress it is the two-option
  format. This protocol changes the format and keeps everything else the same.

## Design (one change: the answer format)
**A. Named members (Appendix E.3).**
- Rows and prompts:
  - the same 10,444 member-Congresses, persona system prompt and 16 single-axis items;
  - the Yes/No instruction is replaced by a 7-point scale, in two directions (as yn/ny):
    - "asc": " Answer with a single number from 1 to 7, where 1 means definitely no and 7 means definitely yes."
    - "desc": " Answer with a single number from 1 to 7, where 1 means definitely yes and 7 means definitely no."
  - 334,208 prompts per model.
- Read-out: the full-softmax probability of the digit tokens "1".."7" at the first answer position, the same forward path as the
  yes/no scoring.
- Format failure: digit mass below 0.5. Failed cells are dropped.
- Per cell: q_k = p_k / Σp; s = the expected answer rescaled to 0-1 with 1 = "yes" (direction-corrected);
  H7 = −Σ q_k log2 q_k / log2 7 (0-1); P_mid = q_4.
- Per member-Congress, means over items and directions: H7; P_mid; C_scale = mean of s where want_yes else 1 − s (vote quadrant;
  continuous analogue of C_vote).

**B. Votes (Section 6).**
- Rows and prompts:
  - the main vote prompts for abortion and economic roll calls (102,285) and the gun prompts (11,934), YEA-first text;
  - the last line "Respond with exactly one word: YEA or NAY." is replaced by a 9-point scale, in two directions:
    - "asc": "Answer with a single number from 1 to 9, where 1 means you certainly vote NAY and 9 means you certainly vote YEA."
    - "desc": the same with YEA and NAY swapped.
  - 228,438 prompts per model.
- Read-out: digits "1".."9", the same path as the vote scoring.
- Per cell: s_yea = expected answer rescaled to 0-1, YEA-corrected; H9 normalised by log2 9; P_mid = q_5.
- Per vote, means over the two directions: P_party_cont = s_yea toward the party majority; H9; P_mid.

## Estimation (same estimators as the paper; rows as the paper)
- **A:** outcome ~ vote_cp | party x Congress x chamber fixed effects, clustered by member; also map-defined cross-pressure, and
  gun-defined cross-pressure on the rows with a gun label.
- **B:** outcome ~ cp | party x roll-call fixed effects, two-way clustering by member and roll call. Issues: abortion, economic, guns
  (abortion CP), guns_gcp (gun CP). Rows as the vote-uncertainty analysis: party ties dropped for P_party, format failures dropped.

## Questions and readings (fixed before any output)
1. **Primary A:** is the scale entropy H7 higher for cross-pressured members?
   - "more uncertain" if the 95% interval excludes 0, |b| ≥ 0.05 and Holm p < 0.05; "no meaningful difference" if the 90% interval
     lies within ±0.05; otherwise "undetermined". H7 is on 0-1 like the binary entropy, so the ±0.05 band is the same.
2. **Primary B:** does the continuous party-line expectation move for cross-pressured members?
   - CP coefficient on P_party_cont, compared with the binary value on the same rows and with the actual difference in party loyalty.
   - "Moves more than binary" if the 95% interval of (scale − binary) excludes 0 in the negative direction, from the same estimator
     applied to the per-row difference.
3. **Collapse check (descriptive):** on identical rows, the CP coefficient on H7 or H9 against the binary-entropy coefficient
   (difference, with interval); the share of cells whose top category holds ≥ 0.9 of the mass, CP vs aligned.
4. **Secondary:** P_mid (mass on the middle answer) and C_scale (consistency with the member's vote quadrant), CP vs aligned.
- Holm family: per model, the primary rows (A: Q2, Q3, gun; B: four issues).
- Qwen gun rows are reported but not interpreted (Qwen fails the task check on gun votes).
- Expectation stated in advance: the continuous answer will not follow cross-pressured members' defections much more than the binary
  one, but it may put more mass in the middle. Either outcome is reported.

## GPU run
- bf16 at the pinned revisions, batch 1 (each row's result is independent of the others).
- Parts of 2,000 prompts with done markers, resumable; --shard i/n; GPU memory cap per process; an out-of-memory error stops the run.
- Smoke at production settings (batch 1) on both models, 100 prompts per task, run twice: bitwise repeat; median digit mass ≥ 0.9 and
  format failures < 5%; greedy 3-token generation starts with a digit in ≥ 95% of prompts; timing and peak memory recorded.

## Outputs
`out/{named,votes}/<m>/part_*.parquet`, then the analysis results.
