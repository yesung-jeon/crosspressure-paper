# Appendix E. Uncertainty

This appendix defines the uncertainty measures of Section 7 and reports the comparisons behind it.

## E.1 Measures

For a choice between two answers, uncertainty is the binary entropy of the model's next-token probabilities, in bits:
H(p) = −p log2 p − (1 − p) log2(1 − p), where p is the probability of the first answer divided by the probability of both. It is zero
when the model puts all its probability on one answer and one when it splits it evenly. For vote prediction, the entropy is computed
in each answer order and the two entropies are averaged. Averaging the probabilities first would give a misleading picture for Qwen,
whose two orders often disagree: the averaged probability would sit near one half even when each order is confident (Appendix D.3).
For named-member questions, an answer in one order counts as a format failure when the probability on Yes and No together is below one half; such answers are dropped ({{AP_NAMED_FAIL_Q}} of answers in Qwen and {{AP_NAMED_FAIL_L}} in Llama), and each member-Congress's entropy is averaged over the rest. For free answers to stated profiles, the measure is the entropy over the whole vocabulary at each generated token, in nats, averaged
over the first tokens of a greedy answer.

On the scales, the model answers with a number from 1 to 9, asked in both directions, for votes and for policy questions alike. The entropy over the digits is divided by its maximum (log2 9), so it also runs from zero to one; a two-answer entropy in bits is already a share of its maximum. The two tasks keep their own prompts: the vote-scale prompts use the description with YEA first (Appendix D.10), give the persona in the user message and label the ends "certainly vote NAY" and "certainly vote YEA"; the policy questions give the persona as the system prompt (Appendix A.5) and label the ends "definitely no" and "definitely yes". The scale entropy comparisons of votes leave out the few votes on which a member's party split evenly; the two-answer entropy comparisons and the accuracy comparisons of Section 6 keep them.

## E.2 Comparisons and Reading Rule

Section 7 compares cross-pressured with aligned members in the vote-prediction task (abortion; guns below) and, as a check, in the named-member questions (abortion; guns below), each with two answers and on a scale. A difference reads as higher or lower when its 95% interval excludes zero and its Holm-adjusted p is below .05; there is no minimum size. Every difference that Section 7 reads as higher has a Holm-adjusted p far below .05, so the choice of family decides none of these readings. The Holm family is the one fixed in each comparison's protocol: for two-answer votes, both models' abortion and economic comparisons together (the economic comparisons are not reported in this paper); for two-answer named questions, both models' two abortion comparisons; for the vote scale, each model's primary comparisons in the run that scored the vote scale, which also held named-question comparisons from an earlier seven-point version that the paper does not report, and left out economic comparisons; for the named-question scale, each model's three comparisons (abortion by votes, abortion by the map, guns). Intervals for the two-answer entropy comparisons use a t value with degrees of freedom one less than the smaller number of clusters; intervals for the scale comparisons and in Section 6 use the normal critical value. With this many clusters the two differ in the fourth decimal. Section 7 reports a result as holding in both models only when both models show it in the same direction. The same comparison for stated profiles gives {{H1_Q}} {{H1_Q_CI}} bits in Qwen and {{H1_L}} {{H1_L_CI}} in Llama for the choice, and {{H2_Q}} {{H2_Q_CI}} and {{H2_L}} {{H2_L_CI}} nats for free answers.

On gun-control votes, with cross-pressure defined by gun votes, Llama is more uncertain about cross-pressured members on the scale ({{SH_VOTE_GUNCP_L}} {{SH_VOTE_GUNCP_L_CI}}) and with YEA or NAY ({{W1U_GUNCP_L}} {{W1U_GUNCP_L_CI}}); Qwen does not predict gun votes better than chance (Appendix D.5). Asked about the member, both models are more uncertain about members cross-pressured on guns: by {{AP_NAMED_GUN_Q}} and {{AP_NAMED_GUN_L}} with yes or no, and by {{SH_NAMED_GUN_Q}} and {{SH_NAMED_GUN_L}} on the nine-point scale.

## E.3 Named-Member Questions

Each model speaks as a named member (Appendix A.5) and answers single-issue Yes-or-No questions on economic and social policy, in both
answer orders, and the same questions on the nine-point scale (Appendix A.6, E.1). The comparison uses all {{AP_QN_AB}} member-Congresses with an abortion quadrant. Besides cross-pressure defined by
votes, it also compares members whom the map places in a cross-pressured quadrant with the others, and it is repeated on guns.

## E.4 Whether Uncertainty Points to Errors

For each roll call, we compute the probability that a randomly drawn wrong prediction has higher entropy than a randomly drawn right one
(the area under the curve), and average it across roll calls, weighting each roll call by its number of wrong-right pairs. A value of one half means that entropy does not separate wrong from right predictions. Section 7 reports the group values, with YEA or NAY and on the scale. On the scale, entropy and errors both come from the scale answers, on the rows of Appendix D.10. Intervals, from resampling members within party, are computed for the difference between cross-pressured and aligned members: in Llama, {{AUROC_DIFF_AB_L}} {{AUROC_DIFF_AB_L_CI}} on abortion and {{AUROC_DIFF_GUN_L}} {{AUROC_DIFF_GUN_L_CI}} on guns; in Qwen, {{AUROC_DIFF_AB_Q}} {{AUROC_DIFF_AB_Q_CI}} and {{AUROC_DIFF_GUN_Q}} {{AUROC_DIFF_GUN_Q_CI}}. On the abortion scale, the difference is {{SAUROC_DIFF_AB_L}} {{SAUROC_DIFF_AB_L_CI}} in Llama and {{SAUROC_DIFF_AB_Q}} {{SAUROC_DIFF_AB_Q_CI}} in Qwen.

In Llama, entropy separates wrong from right predictions for aligned members, and the separation weakens for cross-pressured members. Qwen's entropy is close to one half for both groups. On gun votes, Llama's probability falls from {{AUROC_ALIGNED_GUN_L}} for aligned to {{AUROC_CP_GUN_L}} for cross-pressured members.