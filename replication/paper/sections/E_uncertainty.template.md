# Appendix E. Uncertainty

This appendix defines the uncertainty measures of Section 7 and lists every comparison.

## E.1 Measures

For a choice between two answers, uncertainty is the binary entropy of the model's next-token probabilities, in bits:
H(p) = −p log2 p − (1 − p) log2(1 − p), where p is the probability of the first answer divided by the probability of both. It is zero
when the model puts all its probability on one answer and one when it splits it evenly. For vote prediction, the entropy is computed
in each answer order and the two entropies are averaged. Averaging the probabilities first would give a misleading picture for Qwen,
whose two orders often disagree: the averaged probability would sit near one half even when each order is confident (Appendix D.3).
For named-member questions, an answer in one order counts as a format failure when the probability on Yes and No together is below one half; such answers are dropped ({{AP_NAMED_FAIL_Q}} of answers in Qwen and {{AP_NAMED_FAIL_L}} in Llama), and each member-Congress's entropy is averaged over the rest. For free answers to stated profiles, the measure is the entropy over the whole vocabulary at each generated token, in nats, averaged
over the first tokens of a greedy answer.

## E.2 All Comparisons

Section 7 counts twelve comparisons of cross-pressured with aligned members in each model: vote prediction on abortion, economic and
gun-control roll calls (with gun-defined and abortion-defined cross-pressure), named-member questions (on abortion, with members cross-pressured by their votes or placed in a cross-pressured quadrant by the map, and on guns, with gun-defined or abortion-defined cross-pressure), stated profiles (choice and generation entropy) and choices between policy packages. A comparison counts as higher or lower when its interval excludes zero. Figure 3a in the main text shows all of them.

## E.3 Named-Member Questions

Each model speaks as a named member (Appendix A.5) and answers single-issue Yes-or-No questions on economic and social policy, in both
answer orders. The comparison uses all {{AP_QN_AB}} member-Congresses with an abortion quadrant. Besides cross-pressure defined by
votes, it also compares members whom the map places in a cross-pressured quadrant with the others, and it is repeated on guns.

## E.4 Whether Uncertainty Points to Errors

For each roll call, we compute the probability that a randomly drawn wrong prediction has higher entropy than a randomly drawn right one
(the area under the curve), and average it across roll calls, weighting each roll call by its number of wrong-right pairs. A value of one half means that entropy does not separate wrong from right predictions. Figure 3b in the main text shows the point estimates. Intervals, from resampling members within party, are computed for the difference between cross-pressured and aligned members: in Llama, {{AUROC_DIFF_AB_L}} {{AUROC_DIFF_AB_L_CI}} on abortion, {{AUROC_DIFF_ECON_L}} {{AUROC_DIFF_ECON_L_CI}} on economic votes and {{AUROC_DIFF_GUN_L}} {{AUROC_DIFF_GUN_L_CI}} on guns; in Qwen, {{AUROC_DIFF_AB_Q}} {{AUROC_DIFF_AB_Q_CI}}, {{AUROC_DIFF_ECON_Q}} {{AUROC_DIFF_ECON_Q_CI}} and {{AUROC_DIFF_GUN_Q}} {{AUROC_DIFF_GUN_Q_CI}}.

In Llama, entropy separates wrong from right predictions for aligned members on every issue, and the separation weakens for
cross-pressured members. Qwen's entropy is close to one half for both groups.
