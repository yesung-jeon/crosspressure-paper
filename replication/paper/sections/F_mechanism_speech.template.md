# Appendix F. Why the Economic Side, and Speech

Section 8 asks why the models keep a member's economic position rather than the social one, and notes that cross-pressured members'
floor speech was less partisan. This appendix reports the analyses behind both points. They were added after the main results. They show patterns that fit the discussion, and they do not show what causes the placements.

## F.1 Where the Models Give Social Positions Less Weight

**Do the coordinates carry members' social votes within party?** The two coordinates and the two roll-call scales are standardized within each Congress, chamber and party, among the member-Congresses whose party the model names correctly. Separately for each model and party, these member-Congresses are pooled, the social coordinate is regressed on the abortion and economic scales, and the economic coordinate on the same two scales. The difference between the coefficient of the economic coordinate on the economic scale and that of the social coordinate on the abortion scale (economic minus social) shows how much less the map reflects social votes than economic votes among members of the same party. Intervals resample members. The difference is positive, with an interval that excludes zero, in all four model-party comparisons; for Qwen's Republicans the social coefficient itself is small, its interval reaching below one tenth of a standard deviation.

![Figure F1](figures/appendix/F1_mechanism_speech.png)

**Figure F1. Within party, the map weighs economic votes more than social votes.** Economic minus social coefficient within party (abortion). Lines are 95% intervals.

The social coefficient is positive in each cell, so social votes are reflected in the map. The economic coefficient is larger in all four cells; the difference is smallest for Qwen's Republicans.

**Party or economic side.** Among misplaced cross-pressured members whose party and economic side point to different aligned quadrants, the share placed in their
own party's quadrant is {{AP_X1_D_Q}} {{AP_X1_D_Q_CI}} in Qwen and {{AP_X1_D_L}} {{AP_X1_D_L_CI}} in Llama, close to one half, so
these members do not show whether the party or the economic side wins. Across all misplaced members, the pull toward the economic side
is {{AP_X1_ECON_PULL_Q}} {{AP_X1_ECON_PULL_Q_CI}} and {{AP_X1_ECON_PULL_L}} {{AP_X1_ECON_PULL_L_CI}}, and the pull toward the party is
{{AP_X1_PARTY_PULL_Q}} {{AP_X1_PARTY_PULL_Q_CI}} and {{AP_X1_PARTY_PULL_L}} {{AP_X1_PARTY_PULL_L_CI}}. For most cross-pressured
members, the party's aligned quadrant and the economic side are the same, so the main results cannot separate the two.

## F.2 Floor Speech

**Data and measure.** Floor speeches come from the Congressional Record as parsed by Gentzkow et al. (2018), from the bound edition and,
for the latest Congresses, the daily edition. Speakers are linked to members, and ambiguous or duplicate links are dropped. Phrases that contain digits, procedural phrases, and phrases used by fewer than ten speakers or fewer than twenty times are removed, and members with fewer than five hundred phrase tokens in a Congress are dropped, leaving
{{AP_S2_ROWS}} member-Congresses from 1973 to 2016. Partisanship is measured by how well a member's phrases predict their party: for each phrase, the probability that it comes from the member's own party is computed with the member's own speech left out, and these probabilities are averaged over the member's phrases. The overall measure weights the two parties equally.

**Cross-pressured members spoke less partisanly.** Among members of the same party, chamber and Congress, cross-pressured members'
speech partisanship is lower by {{S2A_AB}} {{S2A_AB_CI}} standard deviations with abortion-defined cross-pressure and {{S2A_GUN}}
{{S2A_GUN_CI}} with gun-defined cross-pressure (clustered by member).

**Speech partisanship and misplacement.** Among cross-pressured members, we find no clear association between speech partisanship and
misplacement on the map ({{AP_S2B_Q}} {{AP_S2B_Q_CI}} in Qwen, {{AP_S2B_L}} {{AP_S2B_L_CI}} in Llama).
