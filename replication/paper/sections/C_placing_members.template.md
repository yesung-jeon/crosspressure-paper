# Appendix C. Placing Members

This appendix reports the placement results of Section 5 in full and describes the task that states positions in the prompt: stated
profiles.

## C.1 Placement by Quadrant

Recall is the share of a quadrant's member-Congresses that the map places in the same quadrant, with the map split at the median of its
Congress and chamber in the same way as the roll-call scales. All Democratic and Republican member-Congresses with both scales are used, whether or not the model recognizes the member (Figure C1).

![Figure C1](figures/appendix/C1_placement.png)

**Figure C1. Both models place aligned member-Congresses in their quadrant far more often than cross-pressured ones; a two-dimensional DW-NOMINATE placement does the reverse.** Share of member-Congresses that the map places in the quadrant of their votes. Right panel: pooled shares on abortion, with the two-dimensional DW-NOMINATE placement for comparison.

**The two-dimensional DW-NOMINATE benchmark.** For the comparison in Section 5, the second dimension of DW-NOMINATE is oriented within
each Congress and chamber so that it correlates positively with the social scale, and both dimensions are split at their medians. This
placement puts cross-pressured member-Congresses in their quadrant more often than aligned ones: {{DW2_RECALL_CROSS_AB}} against
{{DW2_RECALL_ALIGNED_AB}} on abortion, and {{DW2_RECALL_CROSS_GUN}} against {{DW2_RECALL_ALIGNED_GUN}} on guns. Because dimension 2 is oriented by the social scale it is then compared with, we also checked the comparison without that step. On abortion the orientation changes nothing: dimension 2 already points the same way in all {{AP_DW2_CELLS_AB}} Congress-chamber cells. On guns it reverses one of the {{AP_DW2_CELLS_GUN}} cells from 1973 on (two of the {{AP_GUN_CELLS_PASSED}} gun-scale cells of Appendix A.3 are earlier, and the placement comparisons start in 1973); with dimension 2 as published, the shares are {{AP_DW2U_RECALL_CROSS_GUN}} against {{AP_DW2U_RECALL_ALIGNED_GUN}}. On guns, Qwen places {{RECALL_ALIGNED_GUN_Q}} of aligned and {{RECALL_CROSS_GUN_Q}} of cross-pressured member-Congresses in their own quadrant, and Llama places {{RECALL_ALIGNED_GUN_L}} and {{RECALL_CROSS_GUN_L}}; the social coordinate correlates with the gun-control roll-call scale at {{R_Y_GUN_Q}} in Qwen and {{R_Y_GUN_L}} in Llama.

**By decade.** The gap between aligned and cross-pressured members is present in every decade (Figure C2). The share
of aligned member-Congresses placed in their quadrant rises over time in both models, while the share of cross-pressured ones stays
low and falls in the most recent decade on abortion.

![Figure C2](figures/appendix/C2_by_decade.png)

**Figure C2. The gap between aligned and cross-pressured members appears in every decade.** Share of member-Congresses placed in the
quadrant of their votes, by decade of the Congress. Solid lines: aligned; dashed lines: cross-pressured. Few gun-defined
cross-pressured member-Congresses remain in the 2010s.

**The two cross-pressured quadrants.** In Qwen, economically liberal and socially conservative member-Congresses are placed correctly
somewhat more often than economically conservative and socially liberal ones ({{RECALL_ELST_AB_Q}} against {{RECALL_ERSP_AB_Q}} on
abortion); in Llama the two are close ({{RECALL_ELST_AB_L}} and {{RECALL_ERSP_AB_L}}). The two combinations need not look equally
coherent to a model: economic conservatism asks for less state intervention, while social conservatism often asks for more legal
regulation, so whether a combination looks consistent depends on whether positions are organized by left and right or by the reach
of government. The paper does not test this.

## C.2 Recognized Members

Recognition is measured by the party question of Appendix A.5. On abortion, Qwen recognizes a share of {{AP_RECOG_ALIGNED_AB_Q}} of
aligned and {{AP_RECOG_CROSS_AB_Q}} of cross-pressured member-Congresses, and Llama {{AP_RECOG_ALIGNED_AB_L}} and
{{AP_RECOG_CROSS_AB_L}}. Among recognized member-Congresses, the pooled recall is {{RECALL_ALIGNED_AB_RECOG_Q}} for aligned and
{{RECALL_CROSS_AB_RECOG_Q}} for cross-pressured ones in Qwen, and {{RECALL_ALIGNED_AB_RECOG_L}} and {{RECALL_CROSS_AB_RECOG_L}} in Llama.
On guns the figures are {{RECALL_ALIGNED_GUN_RECOG_Q}} and {{RECALL_CROSS_GUN_RECOG_Q}} in Qwen and {{RECALL_ALIGNED_GUN_RECOG_L}} and
{{RECALL_CROSS_GUN_RECOG_L}} in Llama.

## C.3 Where Misplaced Members Go

Among misplaced cross-pressured member-Congresses, Figure C3 (left) gives the share placed in the aligned quadrant with the same economic side:
members who are economically liberal and socially conservative placed as liberal on both dimensions, and members who are economically
conservative and socially liberal placed as conservative on both.

![Figure C3](figures/appendix/C3_destinations_members.png)

**Figure C3. Misplaced cross-pressured members mostly land in the aligned quadrant that shares their economic side, and cross-pressured members are also placed in their own quadrant less often among members selected by their votes.** Left: share of misplaced cross-pressured member-Congresses placed in the aligned quadrant with the same economic side (lib.-cons.: economically liberal and socially conservative; cons.-lib.: the reverse). Right: number of the selected members in each quadrant whom the map places in the quadrant of their votes; the dotted line is the number selected.

## C.4 Members Selected by Their Votes

To show the pattern among individual members, {{NAMED_TOTAL}} members were selected by their votes alone, {{NAMED_N}} from each
quadrant. Eligible members are Democrats and Republicans serving from 1973 on, with both scales and recognized by both models in at least two Congresses. Each
scale is centred on its Congress-chamber median and divided by its standard deviation, and these values are averaged over a member's
Congresses. In each quadrant, ten members are those furthest from both medians and five are drawn at random with a fixed seed. No model
output is used in the selection. A member is placed in the quadrant given by the signs of their average map coordinates, each centred on its Congress-chamber median among the Democratic and Republican member-Congresses the model recognizes.

Figure C3 (right) shows the result.

## C.5 Stated Profiles

**Design.** Each of the four profiles (one for each quadrant) combines one economic and one social position (Appendix A.6). A
profile is given to the model in five ways: in an anonymous member's system prompt (for ten states and three years), in the user turn,
through the paired instructions used to build the directions (in both orders), through four answered example questions, and through a
real member who holds the profile. The model then answers single-issue Yes-or-No items; the probabilities of Yes and No are rescaled to sum to one. Four measures compare cross-pressured with
aligned profiles, with fixed effects for the way the profile was given and intervals from a bootstrap within way and profile:

- consistency: the probability the model gives to the profile's answer on single-issue items;
- quadrant reached: whether the profile's coordinates on the two directions, relative to the no-prompt baseline and the centre of the
  four profiles, lie on the stated side of both directions;
- choice entropy, in bits, on single-issue items;
- generation entropy, in nats, averaged over the first tokens of a free answer.

The model also answers the two-issue items of Table A1, but they do not enter these four measures. Cross-pressured profiles may be less familiar combinations of positions than aligned ones, and the comparison does not hold that familiarity constant. Figure C4 shows the four comparisons.

![Figure C4](figures/appendix/C4_profiles.png)

**Figure C4. Stated cross-pressured profiles are followed less faithfully, and the models are slightly less certain about them.** Cross-pressured minus aligned profiles, with fixed effects for the way the profile is given: consistency with the stated positions, reaching the stated quadrant, choice entropy (bits) and generation entropy (nats). Lines are 95% intervals.

## C.6 Measurement Error

A map measures members' votes with error, and error alone would misplace some members. To see how many, a noise-only map is simulated
on the same member-Congresses. Within each Congress and chamber, the economic and social roll-call scales are standardized, and each is
mixed with random noise so that the simulated coordinates correlate with the scales exactly as closely as the model's coordinates do on
these member-Congresses. In the main version the two noise terms are independent; in a second version they are correlated so that the two
simulated coordinates are also as correlated as the model's. Each version is drawn {{AP_NOISE_DRAWS}} times and split at the medians as
before; intervals cover the middle 95 percent of the draws.

On abortion, the noise-only map places {{AP_NOISE_AB_CROSS_Q}} {{AP_NOISE_AB_CROSS_Q_CI}} of cross-pressured member-Congresses in
their quadrant for Qwen and {{AP_NOISE_AB_CROSS_L}} {{AP_NOISE_AB_CROSS_L_CI}} for Llama, against {{AP_NOISE_AB_CROSS_OBS_Q}} and
{{AP_NOISE_AB_CROSS_OBS_L}} on the models' maps; the correlated version places {{AP_NOISE_AB_CROSS_MATCHED_Q}} and
{{AP_NOISE_AB_CROSS_MATCHED_L}}. The main version places aligned member-Congresses less often than the models do ({{AP_NOISE_AB_ALIGNED_Q}} and
{{AP_NOISE_AB_ALIGNED_L}}, against {{AP_NOISE_AB_ALIGNED_OBS_Q}} and {{AP_NOISE_AB_ALIGNED_OBS_L}}). On guns the pattern is the same:
the noise-only map places {{AP_NOISE_GUN_CROSS_Q}} and {{AP_NOISE_GUN_CROSS_L}} of cross-pressured member-Congresses in their quadrant,
against {{AP_NOISE_GUN_CROSS_OBS_Q}} and {{AP_NOISE_GUN_CROSS_OBS_L}}.

Noise also sends misplaced cross-pressured members toward the aligned quadrant on their economic side, because the social coordinate
tracks its scale less closely than the economic coordinate does. Under noise alone, that share is {{AP_NOISE_AB_DEST_Q}}
{{AP_NOISE_AB_DEST_Q_CI}} in Qwen and {{AP_NOISE_AB_DEST_L}} {{AP_NOISE_AB_DEST_L_CI}} in Llama on abortion, against
{{AP_NOISE_AB_DEST_OBS_Q}} and {{AP_NOISE_AB_DEST_OBS_L}} on the models' maps. On guns it is {{AP_NOISE_GUN_DEST_Q}}
{{AP_NOISE_GUN_DEST_Q_CI}} and {{AP_NOISE_GUN_DEST_L}} {{AP_NOISE_GUN_DEST_L_CI}}, against {{AP_NOISE_GUN_DEST_OBS_Q}} and
{{AP_NOISE_GUN_DEST_OBS_L}}. For Llama, the correlated version cannot
reach Llama's own correlation between the two coordinates (the noise correlation reaches its limit first), so it understates that
correlation. The simulation and its inputs are in the replication package.

## C.7 Distance from the Medians

Cross-pressure is defined by two median splits, so a member just across either median counts as cross-pressured. To check whether such members produce the gap in Section 5, we measure each member-Congress's distance to the nearer of its two cut lines. Within each Congress and chamber, the economic and the abortion roll-call scales are each centred on their median and divided by their standard deviation; the distance is the smaller of the two absolute values. The rows are those of Section 5 (abortion), split into thirds of this distance, with cut points at {{V2_CUT1}} and {{V2_CUT2}} standard deviations, common to both models. Cross-pressured member-Congresses are concentrated near a median: {{V2_NEAR_N_CROSS}} fall in the nearest third, {{V2_MID_N_CROSS}} in the middle third and {{V2_FAR_N_CROSS}} in the furthest third, against {{V2_NEAR_N_ALIGNED}}, {{V2_MID_N_ALIGNED}} and {{V2_FAR_N_ALIGNED}} aligned ones.

The difference between the shares of aligned and cross-pressured member-Congresses placed in their own quadrant is {{V2_NEAR_GAP_Q}} {{V2_NEAR_GAP_Q_CI}} in Qwen and {{V2_NEAR_GAP_L}} {{V2_NEAR_GAP_L_CI}} in Llama in the nearest third, {{V2_MID_GAP_Q}} {{V2_MID_GAP_Q_CI}} and {{V2_MID_GAP_L}} {{V2_MID_GAP_L_CI}} in the middle third, and {{V2_FAR_GAP_Q}} {{V2_FAR_GAP_Q_CI}} and {{V2_FAR_GAP_L}} {{V2_FAR_GAP_L_CI}} in the furthest third. Among all member-Congresses it is {{V2_FULL_GAP_Q}} {{V2_FULL_GAP_Q_CI}} and {{V2_FULL_GAP_L}} {{V2_FULL_GAP_L_CI}}, and among those at least half a standard deviation from both medians {{V2_D05_GAP_Q}} {{V2_D05_GAP_Q_CI}} and {{V2_D05_GAP_L}} {{V2_D05_GAP_L_CI}}. In the furthest third, the models place {{V2_FAR_CROSS_Q}} (Qwen) and {{V2_FAR_CROSS_L}} (Llama) of cross-pressured member-Congresses in their own quadrant, close to their shares among all cross-pressured member-Congresses ({{V2_FULL_CROSS_Q}} and {{V2_FULL_CROSS_L}}), and {{V2_FAR_ALIGNED_Q}} and {{V2_FAR_ALIGNED_L}} of aligned ones. The gap therefore does not come from members near a median. Intervals resample members (2,000 draws). The check was specified in writing before it was run; its code is in the replication package.
