# 6. Predicting Their Votes: Errors Fall on Cross-Pressured Members

Sections 4 and 5 examine the models' internal map. This section asks the models to predict votes. Each model receives a member's name, state, chamber and
year, without the party, together with a neutral description of a roll call, and answers YEA or NAY. Each vote is asked twice, once with
YEA first and once with NAY first, and the two answers are averaged. We compare these predictions with the votes members actually cast on abortion, economic and gun-control
roll calls (Appendix D.1).

**Less accurate for cross-pressured members on abortion.** Both models predict cross-pressured members' abortion votes less accurately
than aligned members' votes: {{ACC_CROSS_AB_Q}} against {{ACC_ALIGNED_AB_Q}} in Qwen, and {{ACC_CROSS_AB_L}} against
{{ACC_ALIGNED_AB_L}} in Llama. Cross-pressured members may vote on different roll calls, or belong to a different party, from aligned
members, so we compare members of the same party voting on the same roll call, with intervals clustered by member and by roll call. The
gap remains: {{CP_COEF_AB_Q}} {{CP_COEF_AB_Q_CI}} in Qwen and {{CP_COEF_AB_L}} {{CP_COEF_AB_L_CI}} in Llama. It also remains when
cross-pressure is defined without the roll call being predicted ({{CP_LOO_AB_Q}} and {{CP_LOO_AB_L}}).

**Not on economic votes.** On economic roll calls, cross-pressured members are predicted at least as accurately as aligned members
({{CP_COEF_ECON_Q}} {{CP_COEF_ECON_Q_CI}} in Qwen and {{CP_COEF_ECON_L}} {{CP_COEF_ECON_L_CI}} in Llama). Qwen's two answer orders barely agree on economic votes (Appendix D.3), so its small advantage there should not be read as better prediction. The deficit appears on abortion votes and not on economic votes. Abortion is also the issue on which the map misplaces these members in Section 5.

**Which members, and which way.** In Llama the abortion gap comes from Republicans ({{CP_COEF_AB_REPUBLICAN_L}}
{{CP_COEF_AB_REPUBLICAN_L_CI}}); for Democrats it is close to zero ({{CP_COEF_AB_DEMOCRAT_L}}). Qwen shows the same pattern more
weakly ({{CP_COEF_AB_REPUBLICAN_Q}} for Republicans, {{CP_COEF_AB_DEMOCRAT_Q}} for Democrats). When the models get a cross-pressured member's abortion vote wrong, the wrong prediction is usually the vote that the member's party majority cast: in a share of {{AP_ERRDIR_CP_AB_Q}} of these errors in Qwen and {{AP_ERRDIR_CP_AB_L}} in Llama.

Olympia Snowe, a Republican from Maine, shows what this looks like for one member. In the House and later in the Senate, she voted
against the majority of her party on {{SNOWE_AB_AGAINST_PCT}} of the {{SNOWE_AB_N_L}} abortion roll calls in our data, and on
{{SNOWE_ECON_AGAINST_PCT}} of the economic ones. Llama predicts {{SNOWE_AB_ACC_L}} of her abortion votes correctly, and
{{SNOWE_AB_WRONG_PARTY_WORDS_L}} of its wrong predictions is the vote her party's majority cast. Two sets of abortion votes show how. In
1997 and 1998 the Senate voted on amendments to repeal the restriction on performing abortions at Department of Defense facilities.
Snowe voted for repeal, against most Republicans; Llama gave her a probability of voting yea of {{SNOWE_DOD1997_YEA_L}} and
{{SNOWE_DOD1998_YEA_L}}, and Qwen gave {{SNOWE_DOD1997_YEA_Q}} on the first. In 2003 she voted against the Partial-Birth Abortion Ban
Act at final passage and again on the conference report, while most Republicans voted for it. Llama predicted a yea vote both times ({{SNOWE_PBA2003_YEA_L}} and {{SNOWE_PBA2003CONF_YEA_L}}). On economic roll calls, Llama
predicts her votes more accurately ({{SNOWE_ECON_ACC_L}}), and only {{SNOWE_ECON_WRONG_PARTY_WORDS_L}} of its errors there follow her
party.

**Guns.** Llama's predictions of gun-control votes repeat the abortion pattern. It predicts {{ACC_CROSS_GUN_L}} of cross-pressured
members' votes correctly, against {{ACC_ALIGNED_GUN_L}} of aligned members' votes. Within party and roll call, the gap is
{{CP_COEF_GUN_GUNCP_L}} {{CP_COEF_GUN_GUNCP_L_CI}} when cross-pressure is defined by gun votes, {{CP_COEF_GUN_ABCP_L}} when it is
defined by abortion votes, and {{CP_COEF_GUN_SAMEROWS_L}} for abortion-defined cross-pressure among the same member-Congresses. Two features differ
from abortion. The gap comes from Democrats ({{CP_COEF_GUN_DEMOCRAT_L}}, against {{CP_COEF_GUN_REPUBLICAN_L}} for Republicans), and the
wrong predictions do not lean toward the member's party. Qwen's gun-vote results are reported in Appendix D.5.

**Other definitions, other benchmarks.** Cross-pressure can also come from a member's state. With state-based cross-pressure, members whose state leans toward the other party are predicted less accurately on abortion ({{D3_AB_Q}} {{D3_AB_Q_CI}} in Qwen, {{D3_AB_L}} {{D3_AB_L_CI}} in Llama) and,
in Llama, on guns ({{D3_GUN_L}} {{D3_GUN_L_CI}}), but not on economic votes ({{D3_ECON_Q}} and {{D3_ECON_L}}). The state is the member's own constituency only for senators, and in the Senate alone the abortion intervals include zero (Appendix D.7). Cross-pressured members' votes are also fitted less well by DW-NOMINATE, which places every member on dimensions estimated from all votes. Holding the NOMINATE fit constant, the abortion gap is {{N2_ACC_AB_L}} {{N2_ACC_AB_L_CI}} in Llama and {{N2_ACC_AB_Q}} {{N2_ACC_AB_Q_CI}} in Qwen. Part of the models' difficulty with these members is therefore shared with DW-NOMINATE (Appendix D.8).

**All in all.** Measured by the votes the models predict, cross-pressured members are again mispredicted, on the issue on which the map misplaces them. The models mispredict cross-pressured members on abortion and, in Llama, on gun control, and they
predict these members' economic votes as well as anyone's. Table 2 collects the estimates.

{{TABLE2}}

## References (Section 6 only)

(No new citations. The vote data are from Voteview; see Section 3.)
