# Appendix B. The History the Models Reconstruct

This appendix defines the history comparisons of Section 4 and reports them in full.

## B.1 The Party Gap and Its Growth

For each Congress, each party's mean is computed within each chamber and the two chambers are averaged with equal weight. Each scale
(a model's economic coordinate, or the first dimension of DW-NOMINATE) is divided by its standard deviation across all Democratic and
Republican member-Congresses from 1947 to 2024, so that the models and DW-NOMINATE are measured in units of their own spread. The growth
of the gap compares a late window (the Congresses of 2013 to 2024) with an early window (1947 to 1958): the change in the Republican
mean minus the change in the Democratic mean. The Democratic share of the growth is the Democratic change divided by the growth in the
gap, with its sign reversed so that a move to the left counts toward the gap; the shares are not forced to lie between zero and one.
Intervals resample members within party, keeping all of a member's Congresses, two thousand times, and differences between a model and DW-NOMINATE use the same draws. Figure B1 shows the results.

![Figure B1](figures/appendix/B1_gap_growth.png)

**Figure B1. The models' party gap grows more than DW-NOMINATE's, mostly through Democrats.** Growth of the gap and the change in each party's mean from 1947–1958 to 2013–2024, in standard deviations of each scale, and the Democratic share of the growth. Lines are 95% intervals from resampling members within party.

## B.2 Early Separation

Early separation is the Republican-minus-Democratic gap divided by the standard deviation within each Congress and chamber, averaged
over the chambers and over the early window. In DW-NOMINATE it is {{T0_EARLY_SEP_DW}} {{T0_EARLY_SEP_DW_CI}}. On the models' economic
direction it is {{T0_EARLY_SEP_MAP_Q}} {{T0_EARLY_SEP_MAP_Q_CI}} in Qwen and {{T0_EARLY_SEP_MAP_L}} {{T0_EARLY_SEP_MAP_L_CI}} in Llama,
so the ratio of model to DW-NOMINATE is {{T0_EARLY_RATIO_Q}} {{T0_EARLY_RATIO_Q_CI}} and {{T0_EARLY_RATIO_L}}
{{T0_EARLY_RATIO_L_CI}}.

## B.3 Continuing Members and Replacement

Section 4 notes that the models' divergence comes mostly from Democrats. A party's mean can move because its continuing members move,
or because new members replace old ones. For each pair of consecutive Congresses, chamber and party, the movement of continuing members
is the change in the mean of the members present in both Congresses, and replacement is the rest of the change; the pieces are summed
over the period. DW-NOMINATE gives each member one score for a whole career, so its continuing members cannot move. The comparison
therefore uses Nokken-Poole scores (Nokken & Poole, 2004), which are estimated for each Congress with the roll-call parameters held
fixed. Both scales are divided by their standard deviations across all Democratic and Republican member-Congresses ({{AP_N1_ROWS}}
member-Congresses with Nokken-Poole scores), and intervals resample members within party one thousand times.

![Figure B2](figures/appendix/B2_continuing.png)

**Figure B2. Continuing Democrats move further left on the models' economic direction than in Nokken-Poole scores.** Sum over consecutive Congresses of the change in the mean of members present in both, model minus Nokken-Poole, in standard deviations. Spans start in 1949 and in 1959. Lines are 95% intervals.

In both models and both spans, continuing Democrats move further left on the models' economic direction than in Nokken-Poole scores (Figure B2).
For Republicans, the difference is smaller and its sign depends on the model and the span. The Democratic side of the models' divergence is therefore also present among members who continued from one Congress to the next, and it does not arise only through replacement.

## B.4 By Chamber

![Figure B3](figures/appendix/B3_chamber.png)

**Figure B3. The pattern holds in both chambers.** Left: growth of the gap, model minus DW-NOMINATE. Middle: Democratic share of the growth (vertical line: one half). Right: early separation as a share of DW-NOMINATE's (vertical line: equal separation). Lines are 95% intervals in the left and right panels; the Democratic shares are point estimates.

The models' gap grows more than DW-NOMINATE's in both chambers (Figure B3), and Democrats account for most of the models' growth in both. The early
parties are closer together than in DW-NOMINATE in both chambers; in the House, Qwen's early parties are not separated at all.
