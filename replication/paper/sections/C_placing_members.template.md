# Appendix C. Placing Members

This appendix reports the placement results of Section 5 in full and describes the two tasks that state positions in the prompt: stated
profiles and choices between policy packages.

## C.1 Placement by Quadrant

Recall is the share of a quadrant's member-Congresses that the map places in the same quadrant, with the map split at the median of its
Congress and chamber in the same way as the roll-call scales. All Democratic and Republican member-Congresses with both scales are used, whether or not the model recognizes the member (Figure C1).

![Figure C1](figures/appendix/C1_placement.png)

**Figure C1. Both models place aligned member-Congresses in their quadrant far more often than cross-pressured ones; a two-dimensional DW-NOMINATE placement does the reverse.** Share of member-Congresses that the map places in the quadrant of their votes. Right panel: pooled shares on abortion, with the two-dimensional DW-NOMINATE placement for comparison.

**The two-dimensional DW-NOMINATE benchmark.** For the comparison in Section 5, the second dimension of DW-NOMINATE is oriented within
each Congress and chamber so that it correlates positively with the social scale, and both dimensions are split at their medians. This
placement puts cross-pressured member-Congresses in their quadrant more often than aligned ones: {{DW2_RECALL_CROSS_AB}} against
{{DW2_RECALL_ALIGNED_AB}} on abortion, and {{DW2_RECALL_CROSS_GUN}} against {{DW2_RECALL_ALIGNED_GUN}} on guns.

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

**Figure C3. Misplaced cross-pressured members mostly land in the aligned quadrant that shares their economic side, and the pattern holds among members selected by their votes.** Left: share of misplaced cross-pressured member-Congresses placed in the aligned quadrant with the same economic side (lib.-cons.: economically liberal and socially conservative; cons.-lib.: the reverse). Right: number of the selected members in each quadrant whom the map places in the quadrant of their votes; the dotted line is the number selected.

## C.4 Members Selected by Their Votes

To show the pattern among individual members, {{NAMED_TOTAL}} members were selected by their votes alone, {{NAMED_N}} from each
quadrant. Eligible members are Democrats and Republicans serving from 1973 on, with both scales and recognized by both models in at least two Congresses. Each
scale is centred on its Congress-chamber median and divided by its standard deviation, and these values are averaged over a member's
Congresses. In each quadrant, ten members are those furthest from both medians and five are drawn at random with a fixed seed. No model
output is used in the selection. A member is placed in the quadrant given by the signs of their average map coordinates, each centred on its Congress-chamber median among the Democratic and Republican member-Congresses the model recognizes.

Figure C3 (right) shows the result.

## C.5 Two Senators

Eagleton and Packwood, the senators of Section 5, are among the {{NAMED_TOTAL}} members: Eagleton was selected as one of the members
furthest from both medians among those economically liberal and socially conservative, and Packwood was drawn at random among those
economically conservative and socially liberal. Both models place Eagleton as liberal on both dimensions. Qwen places Packwood as
conservative on both, and Llama places him in the quadrant of his votes. The two senators were chosen for the text because
they are well-known cases on opposite sides of the same vote, not because of how the models placed or predicted them. Their predicted
votes are reported in Appendix D.9.

## C.6 Stated Profiles

**Design.** Each of the four profiles (one for each quadrant) combines one economic and one social position (Appendix A.6). A
profile is given to the model in five ways: in an anonymous member's system prompt (for ten states and three years), in the user turn,
through the paired instructions used to build the directions (in both orders), through four answered example questions, and through a
real member who holds the profile. The model then answers single-issue Yes-or-No items; the probabilities of Yes and No are rescaled to sum to one. Four measures compare cross-pressured with
aligned profiles, with fixed effects for the way the profile was given and intervals from a bootstrap within way and profile:

- consistency: the probability the model gives to the profile's answer on single-issue items;
- quadrant reached: whether the profile's coordinates on the two directions, relative to the no-prompt baseline and the centre of the
  four profiles, lies on the stated side of both directions;
- choice entropy, in bits, on single-issue items;
- generation entropy, in nats, averaged over the first tokens of a free answer.

The cross-pressured items in Table A1 may also be less familiar policy questions than the aligned items, and the comparison does not hold item familiarity constant. Figure C4 shows the four comparisons.

![Figure C4](figures/appendix/C4_profiles.png)

**Figure C4. Stated cross-pressured profiles are followed less faithfully.** Cross-pressured minus aligned profiles, with fixed effects for the way the profile is given. Lines are 95% intervals.

## C.7 Llama Places the Two Coordinates Closer Together Than the Votes

In each Congress and chamber with enough member-Congresses, we compare the correlation between a member's economic and social
coordinates on the map with the correlation between the economic and social roll-call scales, and average the difference over cells.
A positive difference means that the map ties the two positions together more closely than the votes do. Intervals resample cells. The coordinates are those after the two directions are made orthogonal (Appendix A.4). The third comparison repeats the abortion comparison in the Congress-chamber cells that have a gun scale.

![Figure C5](figures/appendix/C5_overalignment.png)

**Figure C5. Llama ties members' economic and social coordinates together more closely than their votes; Qwen shows the reverse.** Correlation of the two map coordinates minus correlation of the two roll-call scales, averaged over Congress-chamber cells. Lines are 95% intervals from resampling cells.

Llama ties the two coordinates together more closely than the votes do on both issues. Qwen shows the reverse: its coordinates are tied together less closely than the votes in all three comparisons (Figure C5).

## C.8 Choices Between Policy Packages

**Design.** A policy package joins one economic and one social position, for example a position on the minimum wage and one on abortion.
Six economic and nine social topics give fifty-four combinations (Table A2). Each combination is offered in two versions: a party-like version,
in which each package pairs positions that one party holds together, and a crossed version, in which each package pairs an economic
position of one party with a social position of the other. The model chooses between the two packages, in both orders, as one of ten
Democratic and ten Republican House-member personas whose party is stated (Appendix A.6), or with no persona. The outcome is the entropy
of the final choice in bits. The comparison of crossed with party-like versions uses persona and topic fixed effects, with intervals
clustered by persona.

**Results.** Figure C6 shows the estimates. Qwen finds crossed packages harder than party-like ones: its entropy is higher by {{BUNDLE_DEMOCRAT_Q}}
{{BUNDLE_DEMOCRAT_Q_CI}} as Democrats and {{BUNDLE_REPUBLICAN_Q}} {{BUNDLE_REPUBLICAN_Q_CI}} as Republicans. Llama shows the reverse
({{BUNDLE_DEMOCRAT_L}} {{BUNDLE_DEMOCRAT_L_CI}} and {{BUNDLE_REPUBLICAN_L}} {{BUNDLE_REPUBLICAN_L_CI}}). Llama often answers the package
question with neither letter: its average probability on the two answers is {{AP_BUNDLE_MASS_L}}, against {{AP_BUNDLE_MASS_Q}} for Qwen.
Without a persona, the crossed-minus-party-like difference is {{AP_NOPERSONA_Q}} {{AP_NOPERSONA_Q_CI}} in Qwen and {{AP_NOPERSONA_L}}
{{AP_NOPERSONA_L_CI}} in Llama. When a crossed choice is decided, the model picks the package whose economic position matches the
persona's party in a share of {{B5_ECON_SHARE_DEMOCRAT_Q}} (Democrats) and {{B5_ECON_SHARE_REPUBLICAN_Q}} (Republicans) of the choices
in Qwen, and {{B5_ECON_SHARE_DEMOCRAT_L}} and {{B5_ECON_SHARE_REPUBLICAN_L}} in Llama.

**Steering.** The same task was used to push the model's activation along the economic and social directions at the chosen layer, and
along random directions of the same size as placebos. Pushing along a direction changes the chosen party-like package more often than
the placebos by {{AP_STEER_P1_Q}} {{AP_STEER_P1_Q_CI}} in Qwen and {{AP_STEER_P1_L}} {{AP_STEER_P1_L_CI}} in Llama. In Llama,
pushing toward the package the persona would otherwise reject produced no switches at all, so that contrast cannot be estimated. Other steering contrasts, and their dependence on the layer, are reported in the replication package.

![Figure C6](figures/appendix/C6_packages.png)

**Figure C6. Qwen finds crossed packages harder than party-like ones; Llama does not.** Left: entropy of the package choice, crossed
minus party-like packages, by persona (bits). Right: how much more often a push along a direction changes the chosen party-like
package than a push along random placebo directions. Lines are 95% intervals.

## C.9 Measurement Error

A map measures members' votes with error, and error alone would misplace some members. To see how many, a noise-only map is simulated
on the same member-Congresses. Within each Congress and chamber, the economic and social roll-call scales are standardized, and each is
mixed with random noise so that the simulated coordinates correlate with the scales exactly as closely as the model's coordinates do on
these member-Congresses. In the main version the two noise terms are independent; in a second version they are correlated so that the two
simulated coordinates are also as correlated as the model's. Each version is drawn {{AP_NOISE_DRAWS}} times and split at the medians as
before; intervals cover the middle 95 percent of the draws.

On abortion, the noise-only map places {{AP_NOISE_AB_CROSS_Q}} {{AP_NOISE_AB_CROSS_Q_CI}} of cross-pressured member-Congresses in
their quadrant for Qwen and {{AP_NOISE_AB_CROSS_L}} {{AP_NOISE_AB_CROSS_L_CI}} for Llama, against {{AP_NOISE_AB_CROSS_OBS_Q}} and
{{AP_NOISE_AB_CROSS_OBS_L}} on the models' maps; the correlated version places {{AP_NOISE_AB_CROSS_MATCHED_Q}} and
{{AP_NOISE_AB_CROSS_MATCHED_L}}. It places aligned member-Congresses less often than the models do ({{AP_NOISE_AB_ALIGNED_Q}} and
{{AP_NOISE_AB_ALIGNED_L}}, against {{AP_NOISE_AB_ALIGNED_OBS_Q}} and {{AP_NOISE_AB_ALIGNED_OBS_L}}). On guns the pattern is the same:
the noise-only map places {{AP_NOISE_GUN_CROSS_Q}} and {{AP_NOISE_GUN_CROSS_L}} of cross-pressured member-Congresses in their quadrant,
against {{AP_NOISE_GUN_CROSS_OBS_Q}} and {{AP_NOISE_GUN_CROSS_OBS_L}}.

Noise also sends misplaced cross-pressured members toward the aligned quadrant on their economic side, because the social coordinate
tracks its scale less closely than the economic coordinate does. Under noise alone, that share is {{AP_NOISE_AB_DEST_Q}}
{{AP_NOISE_AB_DEST_Q_CI}} in Qwen and {{AP_NOISE_AB_DEST_L}} {{AP_NOISE_AB_DEST_L_CI}} in Llama on abortion, against
{{AP_NOISE_AB_DEST_OBS_Q}} and {{AP_NOISE_AB_DEST_OBS_L}} on the models' maps. On guns it is {{AP_NOISE_GUN_DEST_Q}}
{{AP_NOISE_GUN_DEST_Q_CI}} and {{AP_NOISE_GUN_DEST_L}} {{AP_NOISE_GUN_DEST_L_CI}}, against {{AP_NOISE_GUN_DEST_OBS_Q}} and
{{AP_NOISE_GUN_DEST_OBS_L}}; for Qwen on guns the models' share lies inside the noise interval. For Llama, the correlated version cannot
reach Llama's own correlation between the two coordinates (the noise correlation reaches its limit first), so it understates that
correlation. The simulation and its inputs are in the replication package (16_supplementary_checks/noise_benchmark).
