# Appendix F. Why the Economic Side, and Speech

Section 8 asks why the models keep a member's economic position rather than the social one, and notes that cross-pressured members'
floor speech was less partisan. This appendix reports the analyses behind both points. They were added after the main results. They show patterns that fit the discussion, and they do not show what causes the placements.

## F.1 Where the Models Give Social Positions Less Weight

**Do the coordinates carry members' social votes within party?** The two coordinates and the two roll-call scales are standardized within each Congress, chamber and party, among the member-Congresses whose party the model names correctly. Separately for each model and party, these member-Congresses are pooled, the social coordinate is regressed on the abortion and economic scales, and the economic coordinate on the same two scales. The difference between the coefficient of the economic coordinate on the economic scale and that of the social coordinate on the abortion scale (economic minus social) shows how much less the map reflects social votes than economic votes among members of the same party. Intervals resample members.

![Figure F1](figures/appendix/F1_mechanism_speech.png)

**Figure F1. Social votes are reflected in the map but carry less weight than economic votes, and the models' history follows the timing of roll calls rather than of speech.** Left: economic minus social coefficient within party (abortion). Right: share of the growth in the party gap reached by the middle of the period, in speech, in DW-NOMINATE and on the models' economic direction. Lines are 95% intervals.

The social coefficient is positive in each cell, so social votes are reflected in the map. The economic coefficient is larger in all four cells; the difference is smallest for Qwen's Republicans.

**How much weight does the social commitment get when the model decides?** In the policy-package task, comparing the party-like and the
crossed version of each combination separates how much the model's final preference (the margin between the two answers at the last
layer, oriented toward the persona's party) follows the economic position and how much it follows the social one. The ratio of the social to the
economic weight is {{X5A_REPUBLICAN_Q}} {{X5A_REPUBLICAN_Q_CI}} for Qwen's Republican personas and {{X5A_REPUBLICAN_L}}
{{X5A_REPUBLICAN_L_CI}} for Llama's; for Democratic personas it is {{AP_X5_DEMOCRAT_Q}} {{AP_X5_DEMOCRAT_Q_CI}} and {{AP_X5_DEMOCRAT_L}}
{{AP_X5_DEMOCRAT_L_CI}}, so equal weight cannot be ruled out. These intervals resample the economic and the social positions. Resampling the personas as well widens them ({{AP_X5_3W_REPUBLICAN_Q}} {{AP_X5_3W_REPUBLICAN_Q_CI}} and {{AP_X5_3W_REPUBLICAN_L}} {{AP_X5_3W_REPUBLICAN_L_CI}} for Republican personas; {{AP_X5_3W_DEMOCRAT_Q}} {{AP_X5_3W_DEMOCRAT_Q_CI}} and {{AP_X5_3W_DEMOCRAT_L}} {{AP_X5_3W_DEMOCRAT_L_CI}} for Democratic personas) and leaves both statements unchanged.

**Other checks, which do not show an effect.** Three further analyses asked where misplaced members go and what drives the package
choice:

- Among misplaced cross-pressured members whose party and economic side point to different aligned quadrants, the share placed in their
  own party's quadrant is {{AP_X1_D_Q}} {{AP_X1_D_Q_CI}} in Qwen and {{AP_X1_D_L}} {{AP_X1_D_L_CI}} in Llama, close to one half, so
  these members do not show whether the party or the economic side wins. Across all misplaced members, the pull toward the economic side
  is {{AP_X1_ECON_PULL_Q}} {{AP_X1_ECON_PULL_Q_CI}} and {{AP_X1_ECON_PULL_L}} {{AP_X1_ECON_PULL_L_CI}}, and the pull toward the party is
  {{AP_X1_PARTY_PULL_Q}} {{AP_X1_PARTY_PULL_Q_CI}} and {{AP_X1_PARTY_PULL_L}} {{AP_X1_PARTY_PULL_L_CI}}. For most cross-pressured
  members, the party's aligned quadrant and the economic side are the same, so the main results cannot separate the two.
- Whether the stronger single-issue commitment wins the package choice: {{AP_X3_B_Q}} {{AP_X3_B_Q_CI}} in Qwen and {{AP_X3_B_L}}
  {{AP_X3_B_L_CI}} in Llama.
- Whether the package choice is less uncertain for pairs of positions that the model finds more familiar together, measured by the log-probability it gives a social position after an economic one in plain text, across {{AP_X4_PAIRS}} pairs:
  {{AP_X4_B_Q}} {{AP_X4_B_Q_CI}} and {{AP_X4_B_L}} {{AP_X4_B_L_CI}}.

## F.2 Floor Speech

**Data and measure.** Floor speeches come from the Congressional Record as parsed by Gentzkow et al. (2018), from the bound edition and,
for the latest Congresses, the daily edition. Speakers are linked to members, and ambiguous or duplicate links are dropped. Phrases that contain digits, procedural phrases, and phrases used by fewer than ten speakers or fewer than twenty times are removed, and members with fewer than five hundred phrase tokens in a Congress are dropped, leaving
{{AP_S2_ROWS}} member-Congresses from 1973 to 2016. Partisanship is measured by how well a member's phrases predict their party: for each phrase, the probability that it comes from the member's own party is computed with the member's own speech left out, and these probabilities are averaged over the member's phrases. The overall measure weights the two parties equally.

**Cross-pressured members spoke less partisanly.** Among members of the same party, chamber and Congress, cross-pressured members'
speech partisanship is lower by {{S2A_AB}} {{S2A_AB_CI}} standard deviations with abortion-defined cross-pressure and {{S2A_GUN}}
{{S2A_GUN_CI}} with gun-defined cross-pressure (clustered by member).

**Speech partisanship and misplacement.** Among cross-pressured members, we find no clear association between speech partisanship and
misplacement on the map ({{AP_S2B_Q}} {{AP_S2B_Q_CI}} in Qwen, {{AP_S2B_L}} {{AP_S2B_L_CI}} in Llama). More partisan speakers' wrong abortion predictions
lean slightly more toward their party ({{AP_S2C_Q}} {{AP_S2C_Q_CI}} and {{AP_S2C_L}} {{AP_S2C_L_CI}}).

**The models' history is closer to roll calls than to speech.** In speech, the gap between the parties grows late: the share of its growth reached
by the middle of the period is {{AP_S1_SPEECH}} {{AP_S1_SPEECH_CI}}. In DW-NOMINATE it is {{AP_S1_DW}} {{AP_S1_DW_CI}}, and on the
models' economic direction {{AP_S1_X_Q}} {{AP_S1_X_Q_CI}} in Qwen and {{AP_S1_X_L}} {{AP_S1_X_L_CI}} in Llama. The timing of the
models' divergence follows the roll-call record, not the history of partisan speech.
