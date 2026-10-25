# W1 uncertainty: are the models less certain about cross-pressured members' votes?

2026-10-22. Author authorized: "1번 rhee에 근거해서 해봐" (item 1 of `kim/review/entropy_2026-10-22/PLAN.md`, answering the coauthors'
2026-10-22 comment to add a light model-internal entropy analysis). Status: confirmatory decision rule fixed here before any entropy
value by cross-pressure is computed; everything else exploratory. Written and sealed (`PROTOCOL_SEAL.json`) before `run.R` is run.
Unchanged: the sealed W1 release (`STUDY_V_votes/RELEASE_2026-10-21b.md`) and its inputs, the manuscript, the replication package.

## Question
In the W1 roll-call task (named member, actual roll call, Junsol Kim's prompt), when the model predicts the vote of a cross-pressured
(CP) member, is its YEA/NAY distribution more uncertain than for an aligned member of the same party on the same roll call?
- Section 2, Table 1 of the manuscript: combination predicts more uncertain answers for CP members; dominance and default predict no
  rise (confident answers, including confident errors). The manuscript tests uncertainty only for stated profiles (Section 5) and
  packages (Section 6), not for named members.
- Informative null: a 90% interval inside +-0.05 bits means the models are about as certain about CP members as about aligned members,
  although they predict them less accurately on abortion (sealed). That reads as confident misprediction.

## Data and sample
- Input: the sealed order-averaged frames `kim/STUDY_V_votes/out/v5/frame_v2_<model>_abortion_economic.parquet` (written by
  `v5_estimate.py --select v2`; sha256 must equal `RELEASE_SEAL_2026-10-21b.json`, asserted in `prepare.py`). One row per member vote,
  main sample: abortion 193 roll calls / 54,086 votes; economic 180 / 48,199; models Qwen, Llama, OLMo.
- Main sample: every row without a format failure (broadest; W1 has 0 format failures). Sensitivities below are named, never
  admission rules.
- Models: Llama and Qwen are interpreted (both passed the A5 competence condition on both issues); OLMo did not and is reported, not
  interpreted (same rule as W1).

## Variables (all from the model's next-token probabilities; no text is judged)
- p_o = P(YEA)/(P(YEA)+P(NAY)) in option order o (YEA-first `share_yf`, NAY-first `share_nf`).
- Binary entropy in bits: H(p) = -p log2 p - (1-p) log2(1-p), with p clipped to [1e-12, 1-1e-12]. Range 0 (certain) to 1 (even).
- **Outcome (main): H = (H(p_yf) + H(p_nf)) / 2**, the model's hesitation averaged over the two orders. The entropy of the averaged
  probability, H((p_yf + p_nf)/2), is not the main outcome: when the two orders lean in opposite directions (position bias; Qwen's
  two-order correlation 0.19 / 0.02), the average sits near 0.5 although the model is confident in each order.
- Sensitivity outcomes: H(p_yf), H(p_nf), H((p_yf + p_nf)/2).
- Regressor: cp (1 = cross-pressured member-Congress row, labels from the roll-call scales, as in W1). No control is measured after
  the vote; party and roll call enter only as fixed effects.

## Specification grid (every cell is reported)
Per model (3) x issue (2):
| tag | outcome | FE | cluster | sample |
|---|---|---|---|---|
| main | H | party x roll call | two-way: member (icpsr) and roll call (key) | all rows |
| yf, nf, havg | H(p_yf), H(p_nf), H(avg p) | party x roll call | two-way | all rows |
| rc_only | H | roll call (party as a regressor) | two-way | all rows |
| cl_member, cl_rollcall | H | party x roll call | one-way member / one-way roll call | all rows |
| dem, rep | H | roll call | two-way | Democrats / Republicans |
| known | H | party x roll call | two-way | members the model names (known = 1) |
| wrong, right (descriptive) | H | party x roll call | two-way | rows the model predicts wrong / right (conditions on the outcome of the accuracy test; description only, no verdict) |
Common-sample note: all FE sets are fit on the same rows except the named subsamples.

## Inference and decision rule (main cell only; Llama and Qwen)
- Two-way cluster-robust variance by member and roll call (Cameron, Gelbach & Miller 2011), the same estimator as W1 §6.1
  (`v5_estimate.twoway`: V = V_member + V_rollcall - V_member x rollcall, each CR1). 95% and 90% intervals with t on min(G) - 1 df.
- Verdict, minimum effect +-0.05 bits (the registered minimum for choice entropy in Section 5, H1, same unit):
  - "more uncertain for CP": 95% interval excludes 0 and estimate >= +0.05;
  - "less uncertain for CP": 95% interval excludes 0 and estimate <= -0.05;
  - "no meaningful difference": 90% interval inside [-0.05, +0.05];
  - otherwise "undetermined" (written as such).
- Holm-adjusted p over the four interpreted main tests (2 models x 2 issues) is reported alongside; the verdict uses the rule above.
- Interpretation fixed now: "more uncertain" -> consistent with combination for named members; "no meaningful difference" or "less
  uncertain" -> confident misprediction, consistent with dominance/default, not combination. Models that differ are reported
  separately, not pooled.

## Verification before reading results
1. **Frozen baseline.** `run.R` first refits the sealed W1 §6.1 accuracy coefficient (outcome `correct_avg`, same FE and two-way
   clustering) for all 6 model x issue cells and must reproduce the sealed coefficient and SE
   (`estimates_v2_<m>_abortion_economic.json`) within 1e-6; it stops otherwise. These values are already public in the release.
2. **Reconstruction.** Every fit's coefficient and two-way clustered variance are rebuilt by matrix algebra from the demeaned design;
   stop above 1e-7.
3. **Synthetic check.** On the real design (Llama abortion rows), an outcome with a planted cp effect of +0.08 bits (plus roll-call
   and member noise) must be recovered with the true value inside the 95% interval; with a planted 0, the 90% interval must lie
   inside +-0.05.
4. `prepare.py` prints only row counts, ranges and missing counts, never entropy by cp.

## Already seen (disclosure)
Everything in `RELEASE_2026-10-21b.md`: accuracy and its cp coefficients, Brier and log-loss cp coefficients (e.g. Llama abortion Brier
+0.048), pooled share of averaged probabilities within 0.05 of 0.5 (not by cp), two-order correlations, OLMo's YEA shares. Not seen by
anyone: any entropy value by cp.

## Prohibitions
Never select specifications, samples or models by significance; never change the outcome definition, minimum effect or rule after
seeing results; report every grid cell and OLMo as is.

## Outputs
`prepare.py` -> `data/w1_uncertainty_input.parquet`; `run.R` (+ `helpers.R`) -> models/, tables/coefficients.csv, coverage.csv,
regression_checks.csv, tables/verdicts.csv, tables/descriptives.csv, regression_verification.json, baseline_check.json,
synthetic_check.json; `ASSESSMENT.md`; `RELEASE.json` via `run_all.py`; snapshot by `protect.py`.
