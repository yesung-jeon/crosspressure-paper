# 6. Predicting Their Votes: Errors Fall on Cross-Pressured Members

Sections 4 and 5 examine the models' internal map, and a misplacement on the map need not carry over to what the models answer. This section therefore asks the models to predict votes. Each model receives a member's name, state, chamber and
year, without the party, together with a neutral description of a roll call, and answers YEA or NAY. Each vote is asked twice, once with
YEA first and once with NAY first, and the two answers are averaged. We compare these predictions with the votes members actually cast on abortion and economic
roll calls (Appendix D.1; gun-control votes in Appendix D.5).

**Less accurate for cross-pressured members on abortion.** Both models predict cross-pressured members' abortion votes less accurately
than aligned members' votes: {{ACC_CROSS_AB_Q}} against {{ACC_ALIGNED_AB_Q}} in Qwen, and {{ACC_CROSS_AB_L}} against
{{ACC_ALIGNED_AB_L}} in Llama. Cross-pressured members may vote on different roll calls, or belong to a different party, from aligned
members, so we compare members of the same party voting on the same roll call, with intervals clustered by member and by roll call. The
gap remains: {{CP_COEF_AB_Q}} {{CP_COEF_AB_Q_CI}} in Qwen and {{CP_COEF_AB_L}} {{CP_COEF_AB_L_CI}} in Llama (Figure 4). It also remains when
cross-pressure is defined without the roll call being predicted ({{CP_LOO_AB_Q}} and {{CP_LOO_AB_L}}; Appendix D.4). Cross-pressured members' abortion votes are hard for any predictor. The first dimension of DW-NOMINATE predicts {{DW1_REF_ALIGNED_AB_Q}} of aligned and {{DW1_REF_CROSS_AB_Q}} of cross-pressured members' abortion votes, and the rule that each member votes with the party majority {{PARTY_RULE_ALIGNED_AB_Q}} and {{PARTY_RULE_CROSS_AB_Q}} (Appendix D.6). The models' gap is smaller than these benchmarks'. The finding is that the models, given the member's name, state and year, do not recover these members' abortion votes.

**Not on economic votes.** On economic roll calls, cross-pressured members are predicted at least as accurately as aligned members
({{CP_COEF_ECON_Q}} {{CP_COEF_ECON_Q_CI}} in Qwen and {{CP_COEF_ECON_L}} {{CP_COEF_ECON_L_CI}} in Llama). Qwen's two answer orders barely agree on economic votes (Appendix D.3), so its small advantage there should not be read as better prediction. The deficit appears on abortion votes and not on economic votes. Abortion is also the issue on which the map misplaces these members in Section 5.

**Which members, and which way.** In Llama the abortion gap comes from Republicans ({{CP_COEF_AB_REPUBLICAN_L}}
{{CP_COEF_AB_REPUBLICAN_L_CI}}); for Democrats it is close to zero ({{CP_COEF_AB_DEMOCRAT_L}}). Qwen shows the same pattern more
weakly ({{CP_COEF_AB_REPUBLICAN_Q}} for Republicans, {{CP_COEF_AB_DEMOCRAT_Q}} for Democrats).

![Figure 4](figures/body/fig4_votes.png)

**Figure 4. Cross-pressured members are mispredicted on abortion, not on economic votes.** Each cell is the difference in the share of votes predicted correctly between cross-pressured and aligned members of the same party voting on the same roll call (party x roll-call fixed effects; intervals clustered by member and roll call). Red: less accurate; blue: more accurate. Bold cells: the 95% interval excludes zero; pale cells: it includes zero. Rows: all cross-pressured members; each party's cross-pressured members (roll-call fixed effects within the party); cross-pressure defined without the roll call being predicted. Estimates are in Table D1, and those with intervals in Figure D2; guns, state-based cross-pressure and the NOMINATE benchmark are in Appendix D.

Olympia Snowe, a Republican from Maine, shows what this looks like for one member. In the House and later in the Senate, she voted
against the majority of her party on {{SNOWE_AB_AGAINST_PCT}} of the {{SNOWE_AB_N_L}} abortion roll calls in our data, and on
{{SNOWE_ECON_AGAINST_PCT}} of the economic ones. Llama predicts {{SNOWE_AB_ACC_L}} of her abortion votes correctly. Two sets of abortion votes show its misses. In
1997 and 1998 the Senate voted on amendments to repeal the restriction on performing abortions at Department of Defense facilities.
Snowe voted for repeal, against most Republicans; Llama gave her a probability of voting yea of {{SNOWE_DOD1997_YEA_L}} and
{{SNOWE_DOD1998_YEA_L}}, and Qwen gave {{SNOWE_DOD1997_YEA_Q}} on the first. In 2003 she voted against the Partial-Birth Abortion Ban
Act at final passage and again on the conference report, while most Republicans voted for it. Llama predicted a yea vote both times ({{SNOWE_PBA2003_YEA_L}} and {{SNOWE_PBA2003CONF_YEA_L}}). On economic roll calls, Llama
predicts her votes more accurately ({{SNOWE_ECON_ACC_L}}).

**Other definitions, other benchmarks.** The abortion deficit also appears when cross-pressure is defined by the member's state rather than by votes (Appendix D.7). Cross-pressured members' votes are fitted less well by DW-NOMINATE as well; holding that fit constant, the abortion deficit remains in both models, although part of the models' difficulty is shared with DW-NOMINATE (Appendix D.8).

**On a nine-point scale.** We also asked each vote on a scale from 1 (certainly NAY) to 9 (certainly YEA), in both directions, and predicted YEA when the expected answer lay above the midpoint (Appendix D.10, Table D1). The directions hold in both models. Cross-pressured members' abortion votes are predicted less accurately ({{SA_GAP_AB_Q}} {{SA_GAP_AB_Q_CI}} in Qwen, {{SA_GAP_AB_L}} {{SA_GAP_AB_L_CI}} in Llama), and their economic votes are not ({{SA_GAP_ECON_Q}} and {{SA_GAP_ECON_L}}). The size of the gap depends on the format. Compared with the two-answer format on the same prompt text (YEA described first), the scale gap minus the two-answer gap is {{SA_DYF_AB_Q}} {{SA_DYF_AB_Q_CI}} in Qwen and {{SA_DYF_AB_L}} {{SA_DYF_AB_L_CI}} in Llama: on the scale the accuracy deficit of cross-pressured members is larger in Qwen and smaller in Llama. On that prompt, Qwen's two-answer gap is close to zero ({{SA_YF_AB_Q}} {{SA_YF_AB_Q_CI}}); its gap appears when the two answer orders are averaged and on the scale (Appendix D.3, D.10). The split by party does not hold. On the scale, Qwen's gap comes from Democrats ({{SA_PARTY_DEM_Q}} {{SA_PARTY_DEM_Q_CI}}), and Llama's gap among Republicans is {{SA_PARTY_REP_L}} {{SA_PARTY_REP_L_CI}}. Section 7 uses the same scale to measure how uncertain the models are.

**All in all.** Measured by the votes the models predict, cross-pressured members are again mispredicted, on the issue on which the map misplaces them. The models mispredict cross-pressured members on abortion, and they
predict these members' economic votes as well as anyone's. Figure 4 and Table D1 collect the estimates.

## References (Section 6 only)

(No new citations. The vote data are from Voteview; see Section 3.)
