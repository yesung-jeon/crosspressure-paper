# 5. The Models Move Cross-Pressured Members into the Aligned Quadrant That Matches Their Economic Votes

Member by member, the map shows whether each member is placed where their votes put them. For each Democratic and Republican member-Congress with both roll-call scales, we compare the quadrant the map assigns with the quadrant of the member's economic and social roll-call scales. Figure 2 shows the result for both social issues and both models.

![Figure 2](figures/body/fig2_placement.png)

**Figure 2. Both models place most aligned members in the quadrant of their votes, but few cross-pressured members.** (a, b) The {{NAMED_TOTAL}} members selected by their votes alone, {{NAMED_N}} from each quadrant (Appendix C.4). Marker shape and color give the quadrant of the member's votes; a filled marker means the model places the member in that quadrant, a hollow one that it places the member elsewhere. Positions are the member's average percentile rank within Congress and chamber; the quadrant is set by the average coordinate centred on the median, so a marker on a median line can sit on either side. (c) Share of all Democratic and Republican member-Congresses with both scales that the map places in the quadrant of their votes, with a two-dimensional DW-NOMINATE placement for comparison; results by quadrant are in Appendix C.1.

**Aligned members land in their own quadrant; cross-pressured members do not.** The maps place most aligned member-Congresses in the quadrant of their
own votes and few cross-pressured ones. On abortion, Qwen places {{RECALL_ALIGNED_AB_Q}} of aligned member-Congresses and
{{RECALL_CROSS_AB_Q}} of cross-pressured ones in their own quadrant, and Llama places {{RECALL_ALIGNED_AB_L}} and {{RECALL_CROSS_AB_L}}. On guns, the
corresponding figures are {{RECALL_ALIGNED_GUN_Q}} and {{RECALL_CROSS_GUN_Q}} for Qwen and {{RECALL_ALIGNED_GUN_L}} and
{{RECALL_CROSS_GUN_L}} for Llama.

**Two-dimensional DW-NOMINATE places them correctly.** In NOMINATE scaling, the second dimension captures conflicts that divide the parties internally (Poole & Rosenthal, 1991). A two-dimensional DW-NOMINATE placement of the same member-Congresses places
cross-pressured ones in their quadrant more often than aligned ones: {{DW2_RECALL_CROSS_AB}} against {{DW2_RECALL_ALIGNED_AB}} on
abortion, and {{DW2_RECALL_CROSS_GUN}} against {{DW2_RECALL_ALIGNED_GUN}} on guns.

**Recognition does not explain it.** A model may misplace members it does not know. Restricting the comparison to member-Congresses whose
party the model names correctly leaves the pattern unchanged. On abortion, Qwen places {{RECALL_CROSS_AB_RECOG_Q}} of these cross-pressured
member-Congresses in their own quadrant and Llama {{RECALL_CROSS_AB_RECOG_L}}, against {{RECALL_ALIGNED_AB_RECOG_Q}} and {{RECALL_ALIGNED_AB_RECOG_L}} of aligned ones.

**Measurement error does not explain it.** A map that tracked members' votes only as closely as the models' maps do, with the rest random noise, would place {{AP_NOISE_AB_CROSS_Q}} (Qwen) and {{AP_NOISE_AB_CROSS_L}} (Llama) of cross-pressured member-Congresses in their own quadrant on abortion, far more than the models' maps place (Appendix C.9). Noise alone would already send many misplaced members toward their economic side, but on abortion fewer than the models do.

**Where the misplaced members go.** Most misplaced cross-pressured member-Congresses land in the aligned quadrant that matches their economic
votes. Members who vote liberal on economics are placed as liberal on both dimensions, and members who vote conservative on economics
as conservative on both. On abortion, this is where {{SAME_ECON_ELST_AB_Q}} (Qwen) and {{SAME_ECON_ELST_AB_L}} (Llama) of the misplaced
economically liberal, socially conservative member-Congresses go, and {{SAME_ECON_ERSP_AB_Q}} and {{SAME_ECON_ERSP_AB_L}} of the misplaced
economically conservative, socially liberal ones. For most of these members, that quadrant is also the aligned quadrant of their own party, so the two cannot be told apart; among misplaced members whose party and economic side point to different aligned quadrants, the models favor neither (Appendix F.1). The same pattern
appears among {{NAMED_TOTAL}} members selected by their votes, {{NAMED_N}} from each quadrant. Of the {{NAMED_N}} members in each aligned quadrant, Qwen places
{{NAMED_PLACED_ELSP_Q}} and {{NAMED_PLACED_ERST_Q}} in their own quadrant. Of the {{NAMED_N}} in each cross-pressured quadrant, it places
{{NAMED_PLACED_ELST_Q}} and {{NAMED_PLACED_ERSP_Q}}. For Llama, the numbers are {{NAMED_PLACED_ELSP_L}} and {{NAMED_PLACED_ERST_L}} against
{{NAMED_PLACED_ELST_L}} and {{NAMED_PLACED_ERSP_L}}.

Two senators who stood on opposite sides of the same vote show what this means for individual members. In June 1983 the Senate voted
on a constitutional amendment whose entire text read "A right to abortion is not secured by this Constitution" (129 Cong. Rec.
17575, 1983).
Thomas Eagleton, a Democrat from Missouri, was one of its principal sponsors and called the legal decision in Roe v. Wade "a moral abomination" (129 Cong.
Rec. 17347, 1983). Bob Packwood, a Republican from Oregon who had introduced a National Abortion Act in 1970 (116 Cong. Rec. 12672,
1970), led the opposition (Malone, 1983). On economic legislation their records point the other way. Eagleton's votes place him on
the liberal side of the Senate's economic roll calls. Packwood's place him on the conservative side, though within his own party he
was a moderate, and he later chaired the Finance Committee and helped guide the bipartisan effort to pass the Tax Reform Act of 1986 (Willamette University Archives and Special Collections, 2017). Both models place
Eagleton among members who are liberal on both dimensions, the quadrant that matches his economic votes and not his abortion votes. Qwen does
the same to Packwood and places him among members who are conservative on both; Llama places him where his votes put him.

**Stating their positions does not correct the placement.** The pattern does not depend only on what the models know about particular members. When the
prompt states a profile's economic and social positions directly, both models follow cross-pressured profiles less faithfully than
aligned ones. Cross-pressured minus aligned, the probability of answering consistently with the stated profile, among the Yes and No answers, differs by {{H3_Q}} {{H3_Q_CI}} in Qwen and {{H3_L}} {{H3_L_CI}} in Llama, and the share of conditions in which the profile's coordinates reach the stated quadrant differs by {{H4_Q}} {{H4_Q_CI}} and {{H4_L}} {{H4_L_CI}}. Llama also places members' economic and social coordinates closer together than their votes are; Qwen shows the reverse (Appendix C.7).

**All in all.** On the models' internal map, cross-pressured members are misplaced, and in one direction: toward the aligned position on their economic side. With stated profiles, the models follow cross-pressured profiles less faithfully. The models thus flatten the differences within each party. Section 6 asks whether cross-pressured members are also mispredicted when the models predict their actual votes.

## References (Section 5 only)

Malone, J. (1983, June 27). For senators, no way to duck decision on abortion. *The Christian Science Monitor*. https://www.csmonitor.com/1983/0627/062746.html

Poole, K. T., & Rosenthal, H. (1991). Patterns of congressional voting. *American Journal of Political Science, 35*(1), 228–278. https://doi.org/10.2307/2111445

Willamette University Archives and Special Collections. (2017). *Guide to the Robert W. "Bob" Packwood papers, 1957–2018* (WUA104). https://willamette.libraryhost.com/repositories/2/resources/137

116 Cong. Rec. 12672–12673 (1970) (introduction of the National Abortion Act, S. 3746, by Sen. Packwood).

129 Cong. Rec. 17346–17347 (1983) (statement of Sen. Eagleton on S.J. Res. 3).

129 Cong. Rec. 17575 (1983) (statement of Sen. Hatch quoting S.J. Res. 3).
