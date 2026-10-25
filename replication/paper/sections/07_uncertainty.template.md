# 7. The Models Are Slightly More Uncertain about Cross-Pressured Members

The models' own probabilities also differ for cross-pressured members. We measure the models' uncertainty as the
entropy of their next-token probabilities over the answer options (Appendix E). For a choice between two answers, it ranges from 0 bits, when the
model puts all its probability on one answer, to 1 bit, when it splits its probability evenly. In every task of the paper, we compare
the entropy for cross-pressured members with the entropy for aligned members.

**More uncertain, across tasks.** Across the tasks, the comparisons in which cross-pressured members receive higher entropy outnumber those in which they receive lower entropy.
In Llama, entropy is higher for cross-pressured members in {{ENT_ABOVE_L}} of {{ENT_CELLS}} comparisons and lower in {{ENT_BELOW_L}},
both from choices between two policy packages that each combine an economic and a social position (Appendix C.8). In Qwen, it is higher in {{ENT_ABOVE_Q}} of {{ENT_CELLS}} and lower in none; in the other comparisons the interval includes zero (Figure 3a).

![Figure 3](figures/body/fig3_uncertainty.png)

**Figure 3. Entropy is slightly higher for cross-pressured members in many comparisons, most consistently in Llama, and in Llama it marks errors less well for them.** (a) Cross-pressured minus aligned members in each task (for packages, packages that pair one party's economic position with the other party's social position, minus packages that pair positions one party holds together), with 95% intervals; the tasks are defined in Appendix E. (b) Probability that a randomly drawn wrong prediction has higher entropy than a right one on the same roll call, averaged over roll calls; the vertical line marks one half. Intervals for the difference between the two groups are in Appendix E.4.

**Largest where the member or the profile is in the prompt.** Apart from the choices between policy packages, which compare packages rather than members, the differences are largest when the model speaks as a named member or follows a stated profile. Answering yes-or-no policy questions as a named member, Llama is more uncertain for cross-pressured members by
{{N_Q2_AB_L}} bits {{N_Q2_AB_L_CI}}, and Qwen by {{N_Q2_AB_Q}} {{N_Q2_AB_Q_CI}}. Following a stated profile, Llama's difference is
{{H1_L}} bits {{H1_L_CI}}.

**Small, and smallest in vote prediction.** All of these differences are small next to the 1-bit range, and they are smallest when the
models predict votes. Among members of the same party voting on the same roll call, Llama's entropy is higher for cross-pressured
members by {{W1U_AB_L}} bits {{W1U_AB_L_CI}} on abortion and by {{W1U_GUNCP_L}} {{W1U_GUNCP_L_CI}} on gun control (with cross-pressure defined by gun votes), and Qwen's by
{{W1U_AB_Q}} {{W1U_AB_Q_CI}} on abortion. The pattern is consistent in direction, clearest in Llama, and modest in size. It is
correlational: it shows that the models' probabilities treat these members as harder, not why.

**The uncertainty marks errors less well for cross-pressured members.** For aligned members, Llama's
entropy separates its wrong abortion predictions from its right ones: if one wrong and one right prediction are drawn at random, the
wrong one has the higher entropy with probability {{AUROC_ALIGNED_AB_L}}. For cross-pressured members this probability falls to
{{AUROC_CP_AB_L}}, close to a coin flip (Figure 3b). The same drop appears on gun votes, from {{AUROC_ALIGNED_GUN_L}} to {{AUROC_CP_GUN_L}}, and a
smaller one on economic votes, from {{AUROC_ALIGNED_ECON_L}} to {{AUROC_CP_ECON_L}}. Qwen's entropy separates right from wrong
predictions for neither group (between {{AUROC_CP_ECON_Q}} and {{AUROC_ALIGNED_ECON_Q}} on economic votes and between
{{AUROC_ALIGNED_AB_Q}} and {{AUROC_CP_AB_Q}} on abortion).

**All in all.** The models are slightly more uncertain about cross-pressured members than about aligned ones. The difference is small and clearest in Llama, and it does not tell a user which predictions to doubt. Table 3
brings together the measures of Sections 5 to 7.

{{TABLE3}}
