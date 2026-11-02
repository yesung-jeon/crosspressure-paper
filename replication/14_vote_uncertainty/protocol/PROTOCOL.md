# Vote uncertainty: are the models less certain about cross-pressured members' votes?

> Note for the replication package: this protocol was written on 2026-10-22, before any entropy value by cross-pressure was computed,
> for the first model run (FP8 weights, three models). The paper reports a rerun in bf16 with Qwen2.5-7B-Instruct and
> Llama-3.1-8B-Instruct under the same specification. The reading rule the paper uses (Appendix E.2) later replaced the minimum effect of
> 0.05 bits below: a difference reads as higher or lower when its 95% interval excludes zero and its Holm-adjusted p is below .05, with
> no minimum size. Internal file references have been removed; the specification is unchanged.

2026-10-22. Status: confirmatory decision rule fixed here before any entropy value by cross-pressure is computed; everything else
exploratory. Written and sealed (`PROTOCOL_SEAL.json`) before `02_fit_entropy.R` is run.

## Question
In the roll-call task (named member, actual roll call, Junsol Kim's prompt), when the model predicts the vote of a cross-pressured
(CP) member, is its YEA/NAY distribution more uncertain than for an aligned member of the same party on the same roll call?
- Informative null: a 90% interval inside +-0.05 bits means the models are about as certain about CP members as about aligned members,
  although they predict them less accurately on abortion. That reads as confident misprediction.

## Data and sample
- Input: the order-averaged vote-prediction frames of `10_vote_prediction` (one row per member vote; main sample: abortion 193 roll
  calls / 54,086 votes; economic 180 / 48,199).
- Main sample: every row without a format failure (broadest). Sensitivities below are named, never admission rules.
- Models: a model is interpreted only if it passed the A5 competence condition on both issues; otherwise it is reported, not
  interpreted.

## Variables (all from the model's next-token probabilities; no text is judged)
- p_o = P(YEA)/(P(YEA)+P(NAY)) in option order o (YEA-first `share_yf`, NAY-first `share_nf`).
- Binary entropy in bits: H(p) = -p log2 p - (1-p) log2(1-p), with p clipped to [1e-12, 1-1e-12]. Range 0 (certain) to 1 (even).
- **Outcome (main): H = (H(p_yf) + H(p_nf)) / 2**, the model's hesitation averaged over the two orders. The entropy of the averaged
  probability, H((p_yf + p_nf)/2), is not the main outcome: when the two orders lean in opposite directions (position bias), the average
  sits near 0.5 although the model is confident in each order.
- Sensitivity outcomes: H(p_yf), H(p_nf), H((p_yf + p_nf)/2).
- Regressor: cp (1 = cross-pressured member-Congress row, labels from the roll-call scales). No control is measured after the vote;
  party and roll call enter only as fixed effects.

## Specification grid (every cell is reported)
Per model x issue:
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

## Inference and decision rule (main cell only; interpreted models)
- Two-way cluster-robust variance by member and roll call (Cameron, Gelbach & Miller 2011), the same estimator as the vote-accuracy
  comparison (V = V_member + V_rollcall - V_member x rollcall, each CR1). 95% and 90% intervals with t on min(G) - 1 df.
- Verdict, minimum effect +-0.05 bits (the minimum registered for choice entropy with stated profiles, same unit):
  - "more uncertain for CP": 95% interval excludes 0 and estimate >= +0.05;
  - "less uncertain for CP": 95% interval excludes 0 and estimate <= -0.05;
  - "no meaningful difference": 90% interval inside [-0.05, +0.05];
  - otherwise "undetermined" (written as such).
- Holm-adjusted p over the four interpreted main tests (2 models x 2 issues) is reported alongside.
- Models that differ are reported separately, not pooled.

## Verification before reading results
1. **Frozen baseline.** The fitting script first refits the vote-accuracy coefficient (outcome `correct_avg`, same FE and two-way
   clustering) for every model x issue cell and must reproduce the stored coefficient and SE within 1e-6; it stops otherwise.
2. **Reconstruction.** Every fit's coefficient and two-way clustered variance are rebuilt by matrix algebra from the demeaned design;
   stop above 1e-7.
3. **Synthetic check.** On the real design (Llama abortion rows), an outcome with a planted cp effect of +0.08 bits (plus roll-call
   and member noise) must be recovered with the true value inside the 95% interval; with a planted 0, the 90% interval must lie
   inside +-0.05.
4. The input script prints only row counts, ranges and missing counts, never entropy by cp.

## Already seen (disclosure)
Accuracy and its cp coefficients, Brier and log-loss cp coefficients, the pooled share of averaged probabilities within 0.05 of 0.5
(not by cp), two-order correlations. Not seen by anyone: any entropy value by cp.

## Prohibitions
Never select specifications, samples or models by significance; never change the outcome definition, minimum effect or rule after
seeing results; report every grid cell.

## Outputs
`code/01_prepare_input.py` -> the input frame; `code/02_fit_entropy.R` (+ `helpers.R`) -> models/, tables/coefficients.csv,
coverage.csv, regression_checks.csv, tables/verdicts.csv, tables/descriptives.csv, regression_verification.json, baseline_check.json,
synthetic_check.json.
