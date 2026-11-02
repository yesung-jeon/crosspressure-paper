# Roll-call vote prediction for aligned and cross-pressured members: protocol

> Note for the replication package: this protocol was written before the first model run, which used FP8 weights and three models.
> The paper reports a rerun in bf16 with Qwen2.5-7B-Instruct and Llama-3.1-8B-Instruct under the same specification. Of the dated
> amendments written during the analysis, A5 (the task check of Appendix D.6) ships as `PROTOCOL_A5.md`. Review-item codes and internal
> file references have been removed; the analysis rules are unchanged.

Date: 2026-10-20. Written before any study-model output exists. Source of the question: Junsol Kim's proposal.
Status: confirmatory for the preferred estimate (§6.1), exploratory otherwise.
Sealed with `PROTOCOL_SEAL.json` before the first model run. Changes after sealing are dated amendments at the end, never edits above.

## 1. Question and claim size
Do three open models, prompted as a named member of Congress, predict that member's actual YEA or NAY less accurately for
cross-pressured members than for aligned members, and does any gap exceed what a party-following predictor would show?
Claim size: descriptive. The gap shows whose behaviour the models fail to reproduce; it is not a causal effect of cross-pressure
(Kim's proposal, §7). The study uses no internal directions and no median split of the map, so it does not depend on the overlap of
the economic and social directions.

## 2. Data
- Rows: the 10,444 Democratic and Republican member-Congress rows of the paper's voting quadrants (Congresses 93-117, both scales);
  cross-pressured (CP = 1) = economically left and socially traditional or economically right and socially progressive, as in
  Section 3 of the paper. Labels come from the scales, never from model output.
- Roll calls: the contested roll calls (minority side >= 10%) that built the abortion and economic scales. Economic roll calls are a
  seeded sample matched in number to abortion content roll calls within each Congress and chamber.
- Main sample: content roll calls whose description is sufficient: 193 abortion and 180 economic roll calls, 102,285 cast member votes
  (abortion 54,086; economic 48,199). Actual vote: Voteview cast codes 1-3 = YEA, 4-6 = NAY; other codes are not rows.
- Sensitivity samples (§6.4): procedural and unclassified roll calls; insufficient descriptions.

## 3. Elicitation
**Main prompt** (Junsol Kim's template; one user message, no system message added; the model's chat template is applied as is):

    You are {Senator|Representative} {NAME}, representing {STATE} in the United States {Senate|House of Representatives} in {YEAR}.
    Consider the following roll-call vote:
    {DESCRIPTION}
    A YEA vote would: {YEA_MEANS}.
    A NAY vote would: {NAY_MEANS}.
    How would you vote, based on your policy positions as this {senator|representative} at that time?
    Respond with exactly one word: YEA or NAY.

NAME = the map's member name, STATE = full state name, YEAR = calendar year of the roll call's date.
Party, the actual vote and the cross-pressure label are never in the prompt. Within a roll call, only the member fields change.

**Variants, on a seeded 25% sample of main roll calls stratified by issue, Congress decade and chamber, all members:**
- V1 expert prediction: "{Senator|Representative} {NAME} represented {STATE} in the United States {chamber} in {YEAR}.
  Consider the following roll-call vote: ... Predict how {NAME} voted. Respond with exactly one word: YEA or NAY."
- V2 order swap: NAY meaning before YEA meaning, and "Respond with exactly one word: NAY or YEA."
- V3 paraphrase: "It is {YEAR}, and you are {NAME}, a member of the United States {chamber} from {STATE}. The chamber is voting on the
  following: ... Voting YEA would {YEA_MEANS}; voting NAY would {NAY_MEANS}. Given your policy positions at the time, how do you vote?
  Answer with one word: YEA or NAY."

**Response reading.** One forward pass; the next-token distribution at the first response position. p_yea and p_nay are the
probabilities of each model's first token of "YEA" and of "NAY" (token IDs fixed per model by the fixture test, §5). Prediction = YEA if
p_yea / (p_yea + p_nay) > 0.5. Format failure = p_yea + p_nay < 0.5: counted and reported by model, issue and CP; never assigned to a
side; excluded from accuracy (the main estimate is also reported with format failures counted as wrong, as a bound). No sampling, so no
temperature; repeated runs are deterministic up to GPU arithmetic (checked on the smoke sample).
In all three tokenizers the first tokens of "YEA" and "NAY" are "Y" and "N" (fixture). The smoke test therefore also generates up to 4
tokens greedily and checks that the answer is the word YEA or NAY and agrees with the first-token reading (20 of 20 in each model).
Prompts are scored one at a time (batch 1): with the FP8 loader, batched scoring differed from single-prompt scoring by up to 0.33 in the
YEA share even without padding, while single-prompt scoring agreed with generation.

## 4. Models
Qwen2.5-7B-Instruct, Llama-3.1-8B-Instruct, OLMo-2-1124-7B-Instruct, FP8 (the map's loader and model IDs). Same models as the
map so the two results can be set side by side. Order: Qwen abortion main (pilot), then Qwen economic,
then Llama, then OLMo, then variants. The pilot is part of the final data; nothing in this protocol changes after seeing it.

## 5. Gates before the first run
1. Fixture: for each model, the chat-templated prompt is decoded back to text and the YEA and NAY first-token IDs differ and decode to
   prefixes of "YEA" and "NAY".
2. Synthetic check of `v5_estimate.py`: data with a planted CP effect (-0.10) and two-way clustered errors recover the effect within
   its interval; the two-way covariance is reconstructed by matrix algebra (fit.py CR1 pieces) to 1e-6.
3. Smoke run: 5 roll calls x 20 members x 3 models; format-failure rate and seconds per prompt recorded; a repeated run on the same
   prompts gives the same predictions.
4. Memory: GPU cap 0.80, OOM halves the batch, RAM guard before loading, resumable parts with done markers, one GPU process.
A gate failure stops the run; the fix and its reason are logged.

## 6. Analysis (per model; `v5_estimate.py`; all cells reported)
Outcome `correct` = 1 if the prediction equals the actual vote.

**6.1 Preferred estimate (one).** Abortion main votes: correct ~ CP + party x roll-call fixed effects (linear probability model), two-way
cluster-robust covariance (Cameron, Gelbach & Miller) by member (icpsr) and roll call, built from CR1 pieces: V = V_member +
V_rollcall - V_member x rollcall. Reported with 95% intervals and, across the three models, Bonferroni 98.3% intervals.
Decision rule: "the model is less accurate for cross-pressured members within party and roll call" if the 95% interval lies below 0.
"No meaningful difference" only if the 90% interval lies within +-0.05 (equivalence band, fixed here).

**6.2 Anchors for interpretation.** The same regression and the raw accuracies for three reference predictors, computed from
actual votes only: (a) party-majority rule (stage 0: abortion 0.878 aligned vs 0.395 cross-pressured); (b) one-dimensional reference:
per roll call, a logistic regression of the actual vote on DW-NOMINATE dimension 1, fitted on that roll call (an in-sample ceiling for a
single score, not a competitor); (c) gain over the party rule: correct_model - correct_party ~ CP + fixed effects, same covariance.
Reading: a model CP gap close to the party rule's gap means the model treats members as their party; a model that beats the party rule
for CP = 1 uses member-specific information.

**6.3 Description.** Raw accuracy by CP (Kim's first comparison), by issue; predicted vs actual defection rate (vote against own party's
majority) by CP and party; confidence |p - 0.5| and Brier score by CP; the same by decade.

**6.4 Sensitivities (named; none admits or drops rows of the main estimate).** (i) Economic main votes, same specification (weak
circularity, R9). (ii) Leave-one-roll-call-out CP: CP recomputed from scales that exclude the predicted roll call. (iii) Members whose
party the model recognized. (iv) Procedural, unclassified and insufficient roll calls added. (v) Format failures
counted as wrong. (vi) Variants V1-V3 on the 25% sample, with the main prompt on the same sample. (vii) Pooled over models (summary
only, B4).

**6.5 Minimum detectable effect.** Computed before the run from the party-rule pseudo-outcome (actual votes only) with the 6.1
specification: MDE = 2.8 x SE (80% power, 5% two-sided).
Computed 2026-10-20 before any model run: abortion 0.088, economic 0.034 (party-rule CP coefficient within party and roll call: abortion
-0.495, economic -0.047). The abortion MDE exceeds the +-0.05 equivalence band, so a "no meaningful difference" conclusion on abortion
votes is not expected to be reachable; an interval that includes 0 will be reported as inconclusive, not as no difference.

## Gate results (2026-10-20, before sealing)
Fixture pass (3 models). Synthetic: planted -0.10 recovered as -0.093 [-0.122, -0.065]; FWL vs dummy-variable coefficient 6e-15, CR1 SE
2e-15. Smoke at batch 1: 0 format failures, identical repeat, 20/20 generation agreement, 0.125 s per prompt.

## 7. Prohibitions
No change of prompt, sample, threshold, specification or model after seeing model output, except as dated amendments that say why and
report both versions. No selection by significance. Contrary results stay in the main text. Same estimand, one code path.

## 8. Outputs
`out/v4/<model>/` predictions (parquet parts, run.json with model revision, token IDs, prompts hash, timing); `out/v5/` estimates,
`verification.json`. Manuscript values only through the paper's fill scripts after sealing.

## Author decisions (filled before running)
| decision | options | what it commits the project to | decided by / date |
|---|---|---|---|
| Scope and order | pilot Qwen abortion, then all | protocol fixed for full scope first | author, 2026-10-20 |
| One-dimensional reference | include | reported as an in-sample ceiling | author, 2026-10-20 |
| Insufficient descriptions | exclude from main, keep as sensitivity | main sample 193 + 180 roll calls | author, 2026-10-20 |
