# Appendix D. Predicting Votes

This appendix describes the vote-prediction design of Section 6 and reports its results in full, including the accuracy of both models
against simple benchmarks.

## D.1 Design

**Roll calls.** The abortion roll calls are the contested roll calls of the abortion scale (Appendix A.3) that decide a matter of
substance; procedural motions are set aside. Questions on whether an amendment is germane are kept as votes of substance, because a finding that the amendment is not germane defeats it; three such roll calls enter, two on abortion and one on guns. Within each Congress and chamber, the same number of economic roll calls is drawn at random
with a fixed seed from the economic roll calls of substance. Gun roll calls are the contested gun-regulation roll calls of Appendix A.3 from 1973 on that decide a matter of substance, {{AP_GUN_PRED_RC}} in all. Of these, {{AP_GUN_PRED_RC_OUTSIDE}} come from Congress-chamber cells without a gun scale. They enter the comparisons that define cross-pressure by abortion votes; comparisons that define it by gun votes use the {{AP_GUN_PRED_RC_SCALE}} roll calls from cells with a gun scale. Roll calls whose Voteview text was too thin to describe were left out.

**Descriptions.** For each roll call, a language model (Claude) wrote a neutral description of the measure and of what a YEA and a NAY
vote would do, from Voteview's text only, under written rules: no outcome, no names of members or parties, neutral terms and a short
length. Fixed text rules then flagged outcome words, party cues and loaded terms. A model from another family (GPT-4.1-mini, at
temperature zero) checked each description against the source text, and the flagged descriptions were corrected or adjudicated by the
authors. The authors also read a random sample of descriptions ({{AP_AUTHOR_READ_AB_ECON}} for abortion and economic roll calls and {{AP_AUTHOR_READ_GUN}} for gun roll calls): all of those sampled for abortion and economic roll calls were accepted, and
the two gun descriptions they judged inaccurate were corrected. The checks by the authors follow the advice to review language-model output by hand, because model annotations can contain errors and a model can override its input with its prior knowledge (Lin & Zhang, 2026). The check by a model from a second family is our own addition. The
description and checking scripts called external models and are not rerun by the package; their outputs ship as fixed inputs.

**Prompt and scoring.** The prompt is given in Appendix A.6. It names the member, chamber, state and year but not the party. Each vote
is asked twice, once with YEA first and once with NAY first. In each order, the model's next-token probabilities for YEA and NAY give a
YEA share, and the prediction is YEA when the average of the two shares exceeds one half. A vote counts as a format failure when the
probability on YEA and NAY together is below one half in either order; failures are dropped (none for Qwen, one economic vote for
Llama, none on guns).

**Estimation.** Accuracy (one for a correct prediction, zero otherwise) is regressed on an indicator for cross-pressured members, with
party x roll-call fixed effects, so that cross-pressured members are compared with aligned members of the same party voting
on the same roll call. Standard errors are clustered two ways, by member and by roll call.

## D.2 Full Results

Figure D1 compares the models' accuracy with two roll-call benchmarks (Appendix D.6), and Figure D2 gives every comparison of cross-pressured with aligned members.

![Figure D1](figures/appendix/D1_accuracy.png)

**Figure D1. For aligned members, both models predict abortion and economic votes less accurately than simple roll-call benchmarks.** Share of votes predicted correctly. Squares: the rule that each member votes with their party's majority. Diamonds: each roll call's own DW-NOMINATE cutting line, which is fitted to the votes it predicts. Vertical line: one half. Hollow circles: Qwen's gun votes, not interpreted (Appendix D.5).

![Figure D2](figures/appendix/D2_coefficients.png)

**Figure D2. Cross-pressured members are predicted less accurately on abortion and, in Llama, on guns, but not on economic votes.** Accuracy of cross-pressured minus aligned members, with party x roll-call fixed effects (roll-call fixed effects within party), clustered by member and roll call. Lines are 95% intervals. Hollow circles: Qwen's gun votes, not interpreted (Appendix D.5).

## D.3 Answer Order

The two orders agree closely in Llama and much less in Qwen. Across votes, the correlation between the YEA shares given in the two
orders is {{ORDER_CORR_AB_Q}} (abortion), {{ORDER_CORR_ECON_Q}} (economic) and {{AP_GUN_ORDER_CORR_Q}} (guns) in Qwen, and
{{ORDER_CORR_AB_L}}, {{ORDER_CORR_ECON_L}} and {{AP_GUN_ORDER_CORR_L}} in Llama. Averaging the two orders removes the effect of order on
the prediction, but in Qwen it also means that many averaged shares lie close to one half.

## D.4 The Leave-One-Out Definition

Cross-pressure is defined from the same roll calls that the models predict. In the leave-one-out definition, for each predicted roll
call, both scales of its Congress and chamber are rebuilt without that roll call and the quadrants are recomputed. Rebuilding with
nothing left out reproduces the original scales and labels exactly. Leaving out the predicted roll call changes the label of a share of
{{AP_LOO_CHANGED_Q}} of abortion votes. The estimates are in Figure D2.

## D.5 Guns

Llama predicts {{ACC_ALIGNED_GUN_L}} {{AP_GUN_ACC_ALIGNED_L_CI}} of aligned members' gun votes correctly and {{ACC_CROSS_GUN_L}} of cross-pressured members' votes. Within party and roll call, the gap is {{CP_COEF_GUN_GUNCP_L}} {{CP_COEF_GUN_GUNCP_L_CI}} when cross-pressure is defined by gun votes (leave-one-out), {{CP_COEF_GUN_ABCP_L}} {{CP_COEF_GUN_ABCP_L_CI}} when it is defined by abortion votes, and {{CP_COEF_GUN_SAMEROWS_L}} for abortion-defined cross-pressure among the same member-Congresses. Unlike abortion, the gap comes from Democrats ({{CP_COEF_GUN_DEMOCRAT_L}}, against {{CP_COEF_GUN_REPUBLICAN_L}} for Republicans, abortion-defined). State-based cross-pressure and the NOMINATE benchmark on guns are in D.7 and D.8.

Qwen predicts {{ACC_ALIGNED_GUN_Q}} {{AP_GUN_ACC_ALIGNED_Q_CI}} of aligned members' gun votes correctly, and {{ACC_CROSS_GUN_Q}} of cross-pressured members' votes. Qwen predicts YEA for a share of {{AP_GUN_PRED_YEA_Q}} of aligned
members' gun votes, while the actual share is {{AP_GUN_ACTUAL_YEA}}. Within party and roll call, Qwen's cross-pressured minus aligned
difference is {{CP_COEF_GUN_ABCP_Q}} {{CP_COEF_GUN_ABCP_Q_CI}} with abortion-defined cross-pressure and {{CP_COEF_GUN_GUNCP_Q}}
{{CP_COEF_GUN_GUNCP_Q_CI}} with gun-defined cross-pressure (leave-one-out). Because Qwen's accuracy on aligned members' gun votes is not above one half, Qwen fails the task check of Appendix D.6 on gun votes, and its gun comparisons are reported but not interpreted.

## D.6 How Well the Models Predict Votes

Both models are weak predictors of individual votes. For aligned members, both are less accurate on abortion and economic votes than the rule that
each member votes with their party's majority, and so is Llama on guns (Figure D1). The majority is computed over all of the party's votes on the roll call, the member's own included. Only for cross-pressured members on abortion, where that rule is wrong more
often than right, do the models do better than the rule. The gap between the parties in the models' predicted YEA shares is also far smaller than the actual
gap: on abortion, {{PRED_PARTY_GAP_AB_Q}} in Qwen and {{PRED_PARTY_GAP_AB_L}} in Llama against an actual gap of
{{ACTUAL_PARTY_GAP_AB_Q}}, and on economic votes {{PRED_PARTY_GAP_ECON_Q}} and {{PRED_PARTY_GAP_ECON_L}} against {{ACTUAL_PARTY_GAP_ECON_Q}}.
The comparison in Section 6 is therefore a comparison of accuracy between groups of members within the same party and roll call; it does
not depend on the models being good predictors overall.

The comparison is read only for a model that passes a task check fixed before the results: for aligned members its accuracy is above one half, with a 95% interval from resampling roll calls that excludes one half, and across roll calls the difference between Democrats and Republicans in its predicted YEA share correlates positively with the actual difference, with an interval that excludes zero. Both models pass on abortion and economic votes, and Llama passes on gun votes; Qwen does not (Appendix D.5).

## D.7 State-Based Cross-Pressure

A state's lean is its Democratic share of the two-party presidential vote minus the national share, from the last presidential election
before the Congress begins (MIT Election Data and Science Lab, 2017). A member's state leans toward the other party when it leans
Republican for a Democrat or Democratic for a Republican. Returns begin in 1976, so this definition covers Congresses from 1977 on, and
for House members the state's lean stands in for the district's. Members whose state leans toward the other party are predicted less
accurately on abortion ({{D3_AB_Q}} {{D3_AB_Q_CI}} in Qwen, {{D3_AB_L}} {{D3_AB_L_CI}} in Llama) and, in Llama, on guns ({{D3_GUN_L}}
{{D3_GUN_L_CI}}), but not on economic votes ({{D3_ECON_Q}} {{D3_ECON_Q_CI}} and {{D3_ECON_L}} {{D3_ECON_L_CI}}). Only for senators is the state the
member's own constituency, and in the Senate alone the abortion estimates are {{AP_D3_SENATE_Q}} {{AP_D3_SENATE_Q_CI}} in Qwen and
{{AP_D3_SENATE_L}} {{AP_D3_SENATE_L_CI}} in Llama, with intervals that include zero.

The state-based and vote-based definitions pick out largely different member-Congresses. Of the {{AP_D1_ROWS}} member-Congresses from 1977 on, {{AP_D1_CP}} are cross-pressured by their votes and {{AP_D1_CCP}} by their state, and {{AP_D1_OVERLAP}} are both. Among members of the same party, Congress and chamber, a standard deviation more lean toward the other party raises the probability of being cross-pressured by votes by {{AP_D1_B}} {{AP_D1_B_CI}}. The map itself moves little with state lean once a member's votes are held constant. Holding the member's own roll-call scale and Nokken-Poole scores constant, a standard deviation of more Democratic lean moves the economic coordinate by {{AP_D2_X_Q}} {{AP_D2_X_Q_CI}} in Qwen and {{AP_D2_X_L}} {{AP_D2_X_L_CI}} in Llama, and the social coordinate by {{AP_D2_Y_Q}} {{AP_D2_Y_Q_CI}} and {{AP_D2_Y_L}} {{AP_D2_Y_L_CI}}, in each model's own units. Each shift is less than a tenth of the coordinate's standard deviation within party, Congress and chamber.

## D.8 NOMINATE Fit

The NOMINATE fit is the geometric mean probability that DW-NOMINATE assigns to a member's votes, published by Voteview. Cross-pressured members are fitted less
well: cross-pressured minus aligned members of the same party, Congress and chamber, the geometric mean probability differs by {{AP_GMP_CP}} {{AP_GMP_CP_CI}}. Adding this
fit, standardized, to the model of D.1, the cross-pressured minus aligned gap on abortion is {{N2_ACC_AB_Q}} {{N2_ACC_AB_Q_CI}} in Qwen and
{{N2_ACC_AB_L}} {{N2_ACC_AB_L_CI}} in Llama. On gun votes, with cross-pressure defined by abortion votes, Llama's gap becomes {{N2_ACC_GUN_L}} {{N2_ACC_GUN_L_CI}} with the fit added ({{CP_COEF_GUN_ABCP_L}} without it); Qwen's gun votes are not interpreted (Appendix D.5). Part of the models' difficulty with cross-pressured members is therefore shared with DW-NOMINATE, which also describes these members less well.

## D.9 Individual Members

![Figure D3](figures/appendix/D3_members.png)

**Figure D3. Three well-known cross-pressured senators often voted against their party on abortion.** Squares: share of the member's roll calls on which they voted against their party's majority; roll calls on which the party split evenly are left out. Dots: share predicted correctly. The members were chosen as well-known cases, not by their prediction results; each abortion roll call is listed in the replication package.

Figure D3 shows the three senators named in the text. For Snowe's votes named in Section 6, the models' YEA shares were: on the 1997 and 1998 amendments to repeal the restriction on
abortions at Department of Defense facilities, {{SNOWE_DOD1997_YEA_Q}} and {{SNOWE_DOD1998_YEA_Q}} in Qwen and
{{SNOWE_DOD1997_YEA_L}} and {{SNOWE_DOD1998_YEA_L}} in Llama (she voted yea); on the Partial-Birth Abortion Ban Act at final passage and
on the conference report in 2003, {{SNOWE_PBA2003_YEA_Q}} and {{SNOWE_PBA2003CONF_YEA_Q}} in Qwen and {{SNOWE_PBA2003_YEA_L}} and
{{SNOWE_PBA2003CONF_YEA_L}} in Llama (she voted nay).

## D.10 Answering on a Scale

Section 6 also reports the vote predictions read from a nine-point scale. The prompt is the one of Appendix A.6 with the description that puts YEA first; its last line is replaced by "Answer with a single number from 1 to 9, where 1 means you certainly vote NAY and 9 means you certainly vote YEA", and by the same sentence with YEA and NAY swapped. In each direction the model's probabilities on the nine digits give an expected answer, rescaled to a YEA lean between zero and one; the prediction is YEA when the average of the two leans exceeds one half. No vote had less than half of the probability on the digits. Because the scale is asked only with YEA described first, Section 6 compares it with the two-answer prediction from that same prompt, not with the average over the two orders: the two-answer abortion coefficient with YEA described first is {{SA_YF_AB_Q}} {{SA_YF_AB_Q_CI}} in Qwen and {{SA_YF_AB_L}} {{SA_YF_AB_L_CI}} in Llama, and the scale coefficient minus it is the difference reported in Section 6 (Table D1). The scale answers lean further toward one side than the two-answer predictions. Llama predicts YEA for {{SA_PREDYEA_SCALE_AB_ALIGNED_L}} of aligned members' abortion votes on the scale, against {{SA_PREDYEA_BIN_AB_ALIGNED_L}} with two answers; Qwen predicts YEA less often on the scale ({{SA_PREDYEA_SCALE_AB_ALIGNED_Q}}, against {{SA_PREDYEA_BIN_AB_ALIGNED_Q}}). With a fixed cut at one half, part of the difference in accuracy between the formats comes from this lean. The squared error of the expected answer, the scale's analogue of the Brier score, needs no cut and gives the same pattern: cross-pressured members' abortion votes are predicted worse by {{SA_BRIER_AB_Q}} {{SA_BRIER_AB_Q_CI}} in Qwen and {{SA_BRIER_AB_L}} {{SA_BRIER_AB_L_CI}} in Llama on the scale, against {{SA_BRIER_BIN_AB_Q}} and {{SA_BRIER_BIN_AB_L}} with two answers. Read from the scale, the models pass the same task check as with two answers (Appendix D.6): both models predict more than half of aligned members' abortion and economic votes correctly, and across roll calls the party differences they predict correlate positively with the actual ones; Llama also passes on gun votes, while Qwen's accuracy on aligned members' gun votes is not above one half. Table D1 gives the main estimates of Section 6 and sets each beside its counterpart on the scale, except Qwen's gun votes, which are not interpreted (Appendix D.5).

{{TABLE_D1}}
