# Appendix A. Data and Measurement

This appendix gives the details behind Section 3: the terms used in the paper, the data, the roll-call scales, the economic and social
directions, how members are placed on the map, the prompts, and the models.

## A.1 Terms

- **Member-Congress.** One member in one Congress. It is the unit of the map and of most analyses.
- **Economic, abortion and gun-control scales.** A member-Congress's position on roll calls of each kind (A.3). Higher values are more
  conservative. The abortion and gun-control scales are the two social scales; together the three are the roll-call scales.
- **Quadrant.** The combination of a member-Congress's economic and social positions, each split at the median of its Congress and
  chamber: liberal on both dimensions, conservative on both dimensions, economically liberal and socially conservative, or economically
  conservative and socially liberal. Quadrants are named in words in the text; figure labels abbreviate them.
- **Recall.** The share of a group's member-Congresses that the map places in the quadrant of their votes.
- **Aligned and cross-pressured members.** Aligned member-Congresses are liberal on both dimensions or conservative on both;
  cross-pressured ones are economically liberal and socially conservative, or the reverse.
- **Economic and social directions.** Two directions in a model's activations, one for economic and one for social policy (A.4).
- **Coordinates and the map.** A member-Congress's economic and social coordinates are the projections of the model's activation on the
  two directions (A.5). The map is the set of all coordinates.
- **Flatten.** The paper uses the word for two patterns: the models draw the early parties closer together than the roll-call record
  does (Section 4), and they place cross-pressured members with aligned members (Section 5).

## A.2 Members and Roll Calls

Members and votes come from Voteview (Lewis et al., 2026) for the House and Senate from 1947 to 2024. A member-Congress enters the map if
the member has a first-dimension DW-NOMINATE score in that Congress. This gives 21,288 member-Congresses (17,318 in the
House and 3,970 in the Senate) of 3,637 members, identified by their ICPSR codes. Each Voteview roll call is matched
to its Policy Agendas Project topic (Jones et al., 2025). Of the 60,215 roll calls in these years, a share of
0.982 match; the others are left out of the topic-defined economic scale. State presidential returns come from the MIT
Election Data and Science Lab (2017), and floor speeches from Gentzkow et al. (2018; Appendix F.2). The raw files are downloaded by
the replication package and checked against the exact copies used (Appendix G).

## A.3 Roll-Call Scales and Quadrants

**Why economic and social positions are measured separately.** Economic and social ideology are distinct dimensions with different
roots (Feldman & Johnston, 2014), and many citizens hold liberal positions on one and conservative positions on the other (Treier &
Hillygus, 2009). A single liberal–conservative score cannot show such combinations, so each member's economic and social positions
are measured separately, from their own votes. The paper calls the second dimension social rather than cultural; Layman and Carsey
(2002) use the word cultural for the same issues.

**Why abortion.** Abortion is the social issue best suited to the paper's two questions. Its roll calls run through the whole period
from the 1970s on. The parties' positions on abortion were unclear when the Supreme Court decided Roe v. Wade and became distinct only
over the following two decades (Adams, 1997), and, like other social issues, abortion at first divided each party internally (Layman
& Carsey, 2002). It is therefore an issue on which members could cross their party, and one on which the history the models
reconstruct can be checked.

**Why gun control as a second issue.** To check that the findings do not rest on one issue, gun control is added as a second social
issue. Members' positions on gun control, like their positions on abortion, differ from their liberal–conservative ordering (Wu et al.,
2023). Gun-control roll calls are sparse, however, and most Congresses have none (Wu et al., 2023), so the gun-control scale exists only
for the Congress-chamber cells with enough of them (below).

**Which roll calls.** Economic roll calls are those in the Policy Agendas Project's major topics of macroeconomics, labor, education,
environment and social welfare: 10,817 roll calls, of which 8,815 are contested. Abortion roll calls are
those whose Voteview description, question or detailed description mentions abortion or the unborn: 344 roll calls, 333
contested. A roll call is contested when the smaller side holds at least ten percent of the votes.

**Gun-control roll calls.** Gun roll calls were found by a search of Voteview's text for firearms terms, which returned
234 contested candidates. Each candidate was labelled by two language models from different families and, where they
disagreed or were unsure, by the authors (88 labels by the authors and 146 by agreement of the two
models). The 128 roll calls labelled as gun regulation are coded so that higher values mean more votes against
regulation. A Congress and chamber enters the gun scale only if almost all of its roll calls load in the expected direction and the
scale does not depend on any single roll call; 13 of 20 Congress-chamber cells do. The labelling
scripts called external models and are not rerun by the package; their labels are shipped as fixed inputs (Appendix G).

**How a scale is built.** Each scale is estimated separately for every Congress, chamber and issue. Votes of yea are coded 1 and votes
of nay 0. Members with fewer than three votes are dropped, and a cell needs at least three roll calls and twenty members. Each roll call is centred on its mean among the members who voted, and missing votes are then set to zero, which fills them with that mean. The scale is the first principal component of this matrix. It is oriented so that higher values are more conservative: by the sign of its correlation with the first dimension of DW-NOMINATE when that correlation is at least three tenths in absolute value; otherwise so that southern Democrats score higher than other Democrats, when each group has at least five members; and otherwise by the sign of the weaker correlation with DW-NOMINATE. The economic scale
exists for 78 Congress-chamber cells, and the abortion scale for 40, from the Congress that began in 1973.

**Quadrants.** Within each Congress and chamber, the economic and the social scale are each split at the median, and members tied at the median are assigned to whichever half keeps the split closer to even. In a few chambers most members share the strictest anti-abortion score, and this assignment keeps them on the traditional side. Quadrants are assigned to Democratic and Republican member-Congresses with both scales (Figure A1).

![Figure A1](figures/appendix/A1_quadrants.png)

**Figure A1. Most member-Congresses are aligned; about one in five is cross-pressured.** Democratic and Republican member-Congresses with both scales, by quadrant of their votes. Gray bars: aligned quadrants; green bars: cross-pressured quadrants.

Abortion-defined and gun-defined cross-pressure agree for a share of 0.769 of the member-Congresses that have both social scales, with both definitions split again at the medians of that common set, and the two social scales correlate at 0.650.

## A.4 Economic and Social Directions

**Instructions and questions.** Following Chen et al. (2025), each direction is built from five pairs of opposing instructions, one side economically left or
socially progressive and the other the reverse, and a set of policy questions. The instruction and question files ship with the replication package. Twenty questions are used to build the directions. Ten further questions are used to choose the layer, and the first five of these are also used to place members.

**Extraction.** For each instruction and question, the model writes five answers by sampling. Answers that are very short or that
refuse are dropped. The model's hidden state is averaged over the tokens of each answer at every layer, and the direction is the
difference between the average for one instruction of a pair and the average for the other. At the chosen layer, the economic and
social directions are made orthogonal to each other by a symmetric rotation, so that neither direction is privileged.

**Choosing the layer.** At every layer, each direction is added to the model's last-position activation at ten strengths, and the
model answers held-out questions. A judge model (Llama-3.1-8B-Instruct) scores how far each answer leans in the intended direction. The judge is one of the two models studied, so for Llama the layer is chosen with Llama judging its own steered answers. The
judge separates the two kinds of extraction answers well: its area under the curve is 0.977 and 0.909 for Qwen's
economic and social answers, and 0.971 and 0.975 for Llama's. For each direction, layers are ranked by the largest
average judge score over strengths, and the chosen layer is the one with the best combined rank across the two directions. The best
single layers are 19 (economic) and 16 (social) in Qwen and 16 and 15 in
Llama; the combined rule chooses layer 16 in Qwen and 15 in Llama. The replication package repeats the extraction,
the steering, the judging and the choice of layer from the start, and it stops unless both runs give the same layer and identical
directions. Both runs give the same layers and identical directions.

## A.5 Placing Members

As in Kim et al. (2025), each model is given a system prompt that asks it to speak as one member without stating the party; ours also gives the chamber and state: "You are {name}, who serves in the U.S. {House of
Representatives | Senate} representing {state} in {year}. Answer the question in the first person, as {name} would, reflecting this
person's actual political positions at that time." The prompt does not give the party. The user turn is one held-out policy question;
five economic and five social questions are used. The model's activation at the last prompt token, at the chosen layer, is projected
on the two directions. A member's economic coordinate is the average projection over the economic questions minus the same average
with no persona, and likewise for the social coordinate. On the map, the economic coordinate increases to the right and the social
coordinate increases toward the traditional side.

**Correlations in Table 1.** The correlation with the first dimension of DW-NOMINATE is computed in each Congress, with both chambers
together, and averaged across Congresses. It is lower in the earliest Congress than in the latest (0.315 against
0.792 in Qwen, and 0.511 against 0.963 in Llama). The correlations with the roll-call scales are computed after subtracting each Congress-chamber mean. These correlations and the party gaps use only the member-Congresses the model recognizes (below). The party gap in Table 1 is the difference between the Republican and the
Democratic mean divided by the standard deviation of all coordinates. Section 4 measures the gap in each Congress instead, with the two chambers weighted equally and over all Democratic and Republican member-Congresses (Appendix B.1, B.2).

**Recognized members.** To check whether a model knows a member, each model is also asked, "Which political party did {name}, a member
of the U.S. {chamber} from {state} in {year}, belong to? Answer with one word." A member-Congress counts as recognized when the answer names the member's actual party. This shows that the model can name the party, which the state and year may suggest; it does not show that the model knows the member. Qwen recognizes a share of 0.811 of member-Congresses and Llama 0.921. Unless stated otherwise, analyses keep the coordinates of unrecognized members. The exceptions are the correlations and party gaps of Table 1, the selected members of Appendix C.4 and the within-party analysis of Appendix F.1, which use recognized member-Congresses only. Section 5 also reports, as a check, placement among recognized member-Congresses only.

## A.6 Prompts

The prompts for each task are reproduced below. Braces mark the parts filled for each member, profile or roll call.

**Member persona (map, Sections 4 and 5).** As in A.5.

**Stated profiles (Section 5).** The anonymous persona states the profile's positions: "This member supports {economic position} and
{social position}." The economic positions are "expanding Social Security, public health insurance and union rights" and "cutting
taxes, reducing government spending and deregulating business"; the social positions are "abortion rights and same-sex marriage" and
"restrictions on abortion and a traditional definition of marriage." The same positions are also given in the user turn, through the
paired instructions of A.4, through four answered example questions, or through a named member who holds them (Appendix C.5). Each
item ends with "Answer with Yes or No."

**Vote prediction (Section 6).** "You are {Senator | Representative} {name}, representing {state} in the United States {Senate | House
of Representatives} in {year}. Consider the following roll-call vote: {description} A YEA vote would: {what a yea vote does}. A NAY vote
would: {what a nay vote does}. How would you vote, based on your policy positions as this {senator | representative} at that time?
Respond with exactly one word: YEA or NAY." In the second order the two meaning lines are swapped and the last line reads "NAY or YEA"
(Appendix D.1).

**Named-member questions (Section 7).** The member persona of A.5, followed by a single-issue question and "Answer with Yes or No." or
"Answer with No or Yes." The questions are the sixteen single-issue items of Table A1. On the scale, the question is followed instead by "Answer with a single number from 1 to 9, where 1 means definitely no and 9 means definitely yes." or by the same sentence with the ends swapped (Appendix E.1).

**Table A1. Items for stated profiles and named members**

| Type | Item |
|---|---|
| Economic only | Should the federal minimum wage be raised substantially? |
| Economic only | Should public pension benefits be expanded and funded by higher payroll taxes? |
| Economic only | Should taxes on the wealthiest households be increased to fund public services? |
| Economic only | Should public colleges be tuition-free, paid for by taxpayers? |
| Economic only | Should corporate income taxes be cut to encourage investment? |
| Economic only | Should the postal service be privatized? |
| Economic only | Should unemployment benefits be reduced so that people return to work sooner? |
| Economic only | Should regulations on banks and financial firms be loosened? |
| Social only | Should same-sex marriage be legal? |
| Social only | Should transgender people be allowed to change the gender on their official documents? |
| Social only | Should schools teach that different family structures, including same-sex parents, are equally valid? |
| Social only | Should religion be kept entirely out of public school ceremonies? |
| Social only | Should organized prayer be allowed in public schools? |
| Social only | Should the Ten Commandments be displayed in public courthouses? |
| Social only | Should divorce be made harder to obtain in order to protect marriage? |
| Social only | Should abortion be banned except to save the mother's life? |
| Aligned, liberal on both | Should public health insurance cover contraception at no cost? |
| Aligned, liberal on both | Should the government fund universal childcare so that mothers can work full time? |
| Aligned, liberal on both | Should the government fund shelters and services for homeless LGBT youth? |
| Aligned, liberal on both | Should the law require employers to give same-sex spouses the same benefits as other spouses? |
| Aligned, liberal on both | Should public insurance pay for gender-affirming medical care? |
| Aligned, liberal on both | Should the government fund free family planning clinics, including abortion services? |
| Aligned, liberal on both | Should the government regulate businesses to forbid firing workers for being gay or transgender? |
| Aligned, liberal on both | Should publicly funded daycare be open on equal terms to single parents and same-sex parents? |
| Aligned, conservative on both | Should welfare benefits for unmarried mothers be cut to encourage marriage? |
| Aligned, conservative on both | Should parents receive vouchers to send their children to private religious schools instead of public schools? |
| Aligned, conservative on both | Should private businesses be free to refuse to provide services for same-sex weddings? |
| Aligned, conservative on both | Should employers be allowed to leave contraception out of their health plans for religious reasons? |
| Aligned, conservative on both | Should government funding for family planning programs be eliminated? |
| Aligned, conservative on both | Should private adoption agencies be free to decline to place children with same-sex couples? |
| Aligned, conservative on both | Should taxes be cut for married couples in which one parent stays home with the children? |
| Aligned, conservative on both | Should public funding for broadcasters be ended because of their programs on sexuality and gender? |
| Crossed, economically liberal and socially conservative | Should the government fund religious charities to run welfare programs? |
| Crossed, economically liberal and socially conservative | Should the government pay families a monthly allowance so that one parent can stay home with young children? |
| Crossed, economically liberal and socially conservative | Should the government strictly regulate media companies to limit sexual content? |
| Crossed, economically liberal and socially conservative | Should public funds support pregnancy centers that help women carry their pregnancies to term? |
| Crossed, economically liberal and socially conservative | Should the government ban gambling advertising to protect families? |
| Crossed, economically liberal and socially conservative | Should the law require internet companies to block pornography for all users? |
| Crossed, economically liberal and socially conservative | Should the government give large cash payments to families for each child born, to raise the birth rate? |
| Crossed, economically liberal and socially conservative | Should the government restrict stores from opening on Sundays? |
| Crossed, economically liberal and socially conservative | Should the government fund programs that encourage married couples to stay together? |
| Crossed, economically liberal and socially conservative | Should the law require businesses to give workers Sundays off for rest and worship? |
| Crossed, economically liberal and socially conservative | Should public housing give priority to married couples with children? |
| Crossed, economically liberal and socially conservative | Should the government tax and regulate alcohol more heavily to protect family life? |
| Crossed, economically liberal and socially conservative | Should Social Security give extra pension credits to parents who stay home to raise children? |
| Crossed, economically liberal and socially conservative | Should public funds pay for chaplains and religious counseling in public hospitals? |
| Crossed, economically liberal and socially conservative | Should the government expand child tax credits for married parents only? |
| Crossed, economically liberal and socially conservative | Should the government pay for extended paid leave for mothers so they can stay home with their infants? |
| Crossed, economically conservative and socially liberal | Should marijuana be legal and sold by private businesses with minimal government regulation? |
| Crossed, economically conservative and socially liberal | Should sex work between consenting adults be legal and treated as a private business? |
| Crossed, economically conservative and socially liberal | Should commercial surrogacy contracts be legal without government limits? |
| Crossed, economically conservative and socially liberal | Should the government stop licensing marriage and leave it to private contracts between any consenting adults? |
| Crossed, economically conservative and socially liberal | Should gambling be fully legal and left to the free market? |
| Crossed, economically conservative and socially liberal | Should drug use be decriminalized, with drugs sold by licensed private companies? |
| Crossed, economically conservative and socially liberal | Should pornography between consenting adults be legal and free of government regulation? |
| Crossed, economically conservative and socially liberal | Should companies be free to sell fertility and egg-freezing services without government restrictions? |
| Crossed, economically conservative and socially liberal | Should private clinics be free to provide gender transition care to adults without government restrictions? |
| Crossed, economically conservative and socially liberal | Should businesses be free to sell psychedelic drugs to adults without heavy government regulation? |
| Crossed, economically conservative and socially liberal | Should laws banning alcohol sales on Sundays be repealed so businesses can sell whenever they choose? |
| Crossed, economically conservative and socially liberal | Should the tax code stop favoring married couples and leave family arrangements to individuals? |
| Crossed, economically conservative and socially liberal | Should zoning laws that restrict where adult entertainment businesses can operate be abolished? |
| Crossed, economically conservative and socially liberal | Should fertility clinics be free to offer any service to any adult, including single and same-sex parents, without government limits? |
| Crossed, economically conservative and socially liberal | Should assisted suicide be legal and offered by private clinics without government restrictions? |
| Crossed, economically conservative and socially liberal | Should government rules on explicit content in films and video games be ended, leaving ratings to private industry? |

## A.7 Models and Computation

The models are Qwen2.5-7B-Instruct and Llama-3.1-8B-Instruct, loaded at fixed revisions that are listed in the replication package, in
bfloat16. Directions are extracted from sampled answers; steering generations, the party question and the free answers to stated profiles use greedy decoding. Member placement on the map and the coordinates of stated profiles are projections of the hidden state at the last prompt token. Answers to Yes-or-No questions, vote predictions and answers on the nine-point scales are read from the model's next-token probabilities. Member placement and these probability readouts involve no sampling. All computations run in deterministic mode with fixed
batch sizes and seeds, and a rerun on the same hardware and software gives identical outputs (Appendix G).

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
over the chambers and over the early window. In DW-NOMINATE it is 1.657 [1.613, 1.710]. On the models' economic
direction it is 0.259 [0.080, 0.436] in Qwen and 1.003 [0.889, 1.116] in Llama,
so the ratio of model to DW-NOMINATE is 0.156 [0.048, 0.261] and 0.605
[0.542, 0.664]. Among recognized member-Congresses (Appendix A.5), the ratio is 0.254 [0.141, 0.364] and 0.615 [0.550, 0.675], the models' gap grows more than DW-NOMINATE's by 1.172 [0.975, 1.364] and 1.203 [1.098, 1.308], and Democrats account for a share of 0.696 [0.645, 0.748] and 0.739 [0.710, 0.771] of the models' growth.

## B.3 Continuing Members and Replacement

Section 4 notes that the models' divergence comes mostly from Democrats. A party's mean can move because its continuing members move,
or because new members replace old ones. For each pair of consecutive Congresses, chamber and party, the movement of continuing members
is the change in the mean of the members present in both Congresses, and replacement is the rest of the change; the pieces are summed
over the period. DW-NOMINATE gives each member one score for a whole career, so its continuing members cannot move. The comparison
therefore uses Nokken-Poole scores (Nokken & Poole, 2004), which are estimated for each Congress with the roll-call parameters held
fixed. Both scales are divided by their standard deviations across all Democratic and Republican member-Congresses (21,204
member-Congresses with Nokken-Poole scores), and intervals resample members within party one thousand times.

![Figure B2](figures/appendix/B2_continuing.png)

**Figure B2. Continuing Democrats move further left on the models' economic direction than in Nokken-Poole scores.** Sum over consecutive Congresses of the change in the mean of members present in both, model minus Nokken-Poole, in standard deviations. Spans start in 1949 and in 1959. Lines are 95% intervals.

In both models and both spans, continuing Democrats move further left on the models' economic direction than in Nokken-Poole scores (Figure B2).
For Republicans, the difference is smaller. In the span from 1949, which Section 4 reports, it is 0.274 [0.099, 0.434] in Qwen and 0.154 [−0.024, 0.327] in Llama; in the span from 1959 it is 0.071 [−0.065, 0.200] and −0.099 [−0.237, 0.044], so its sign depends on the model and the span. The Democratic side of the models' divergence is therefore also present among members who continued from one Congress to the next, and it does not arise only through replacement.

## B.4 By Chamber

![Figure B3](figures/appendix/B3_chamber.png)

**Figure B3. The pattern holds in both chambers.** Left: growth of the gap, model minus DW-NOMINATE. Middle: Democratic share of the growth (vertical line: one half). Right: early separation as a share of DW-NOMINATE's (vertical line: equal separation). Lines are 95% intervals in the left and right panels; the Democratic shares are point estimates.

The models' gap grows more than DW-NOMINATE's in both chambers (Figure B3), and, in point estimates, Democrats account for most of the models' growth in both. The early
parties are closer together than in DW-NOMINATE in both chambers; in the House, Qwen's early parties are not separated at all.

## B.5 The Social Direction

Figure B4 draws each model's social coordinate the way Figure 1 draws the economic one. Its benchmark, the abortion roll-call scale, has no common unit across Congresses (Appendix A.3), so only its party gap is drawn: in each Congress, the Republican minus the Democratic mean on the scale, divided by the scale's standard deviation within each chamber and averaged over the chambers, among the member-Congresses that also have a map position. That gap is converted to the panel's unit by the ratio of the social coordinate's standard deviation within the Congress (chambers averaged) to its standard deviation over all Congresses, and it is drawn around the model's own party midpoint. The benchmark's location in Figure B4 is therefore the model's; only its separation carries information.

![Figure B4](figures/appendix/B4_social_history.png)

**Figure B4. On the social direction, both models' party gap grows from near zero, as the party gap in abortion roll calls does from 1973.** Each party's mean position on each model's social direction in every Congress (time runs down), in standard deviations of the axis and centred on the two parties' 1947–1958 midpoint, as in Figure 1. (a) Qwen, (b) Llama; dotted lines: the party gap in abortion roll calls within each Congress, drawn around the model's own party midpoint, because roll-call positions are not comparable across Congresses: only their separation is a benchmark. Above each panel: the party gap as drawn at the start and end of each series, and the drawn roll-call separation from the first Congress with an abortion scale.

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
placement puts cross-pressured member-Congresses in their quadrant more often than aligned ones: 0.681 against
0.546 on abortion, and 0.769 against 0.546 on guns. Because dimension 2 is oriented by the social scale it is then compared with, we also checked the comparison without that step. On abortion the orientation changes nothing: dimension 2 already points the same way in all 40 Congress-chamber cells. On guns it reverses one of the 11 cells from 1973 on (two of the 13 gun-scale cells of Appendix A.3 are earlier, and the placement comparisons start in 1973); with dimension 2 as published, the shares are 0.777 against 0.547. On guns, Qwen places 0.724 of aligned and 0.189 of cross-pressured member-Congresses in their own quadrant, and Llama places 0.913 and 0.136; the social coordinate correlates with the gun-control roll-call scale at 0.603 in Qwen and 0.735 in Llama.

**By decade.** The gap between aligned and cross-pressured members is present in every decade (Figure C2). The share
of aligned member-Congresses placed in their quadrant rises over time in both models, while the share of cross-pressured ones stays
low and falls in the most recent decade on abortion.

![Figure C2](figures/appendix/C2_by_decade.png)

**Figure C2. The gap between aligned and cross-pressured members appears in every decade.** Share of member-Congresses placed in the
quadrant of their votes, by decade of the Congress. Solid lines: aligned; dashed lines: cross-pressured. Few gun-defined
cross-pressured member-Congresses remain in the 2010s.

**The two cross-pressured quadrants.** In Qwen, economically liberal and socially conservative member-Congresses are placed correctly
somewhat more often than economically conservative and socially liberal ones (0.237 against 0.180 on
abortion); in Llama the two are close (0.162 and 0.186). The two combinations need not look equally
coherent to a model: economic conservatism asks for less state intervention, while social conservatism often asks for more legal
regulation, so whether a combination looks consistent depends on whether positions are organized by left and right or by the reach
of government. The paper does not test this.

## C.2 Recognized Members

Recognition is measured by the party question of Appendix A.5. On abortion, Qwen recognizes a share of 0.869 of
aligned and 0.750 of cross-pressured member-Congresses, and Llama 0.940 and
0.908. Among recognized member-Congresses, the pooled recall is 0.732 for aligned and
0.195 for cross-pressured ones in Qwen, and 0.899 and 0.179 in Llama.
On guns the figures are 0.769 and 0.191 in Qwen and 0.924 and
0.135 in Llama.

## C.3 Where Misplaced Members Go

Among misplaced cross-pressured member-Congresses, Figure C3 (left) gives the share placed in the aligned quadrant with the same economic side:
members who are economically liberal and socially conservative placed as liberal on both dimensions, and members who are economically
conservative and socially liberal placed as conservative on both.

![Figure C3](figures/appendix/C3_destinations_members.png)

**Figure C3. Misplaced cross-pressured members mostly land in the aligned quadrant that shares their economic side, and cross-pressured members are also placed in their own quadrant less often among members selected by their votes.** Left: share of misplaced cross-pressured member-Congresses placed in the aligned quadrant with the same economic side (lib.-cons.: economically liberal and socially conservative; cons.-lib.: the reverse). Right: number of the selected members in each quadrant whom the map places in the quadrant of their votes; the dotted line is the number selected.

## C.4 Members Selected by Their Votes

To show the pattern among individual members, 60 members were selected by their votes alone, 15 from each
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
simulated coordinates are also as correlated as the model's. Each version is drawn 500 times and split at the medians as
before; intervals cover the middle 95 percent of the draws.

On abortion, the noise-only map places 0.448 [0.428, 0.470] of cross-pressured member-Congresses in
their quadrant for Qwen and 0.594 [0.574, 0.613] for Llama, against 0.208 and
0.174 on the models' maps; the correlated version places 0.379 and
0.552. The main version places aligned member-Congresses less often than the models do (0.565 and
0.770, against 0.679 and 0.881). On guns the pattern is the same:
the noise-only map places 0.485 and 0.625 of cross-pressured member-Congresses in their quadrant,
against 0.189 and 0.136.

Noise also sends misplaced cross-pressured members toward the aligned quadrant on their economic side, because the social coordinate
tracks its scale less closely than the economic coordinate does. Under noise alone, that share is 0.437
[0.407, 0.463] in Qwen and 0.555 [0.522, 0.584] in Llama on abortion, against
0.572 and 0.746 on the models' maps. On guns it is 0.455
[0.386, 0.523] and 0.560 [0.489, 0.636], against 0.570 and
0.719. For Llama, the correlated version cannot
reach Llama's own correlation between the two coordinates (the noise correlation reaches its limit first), so it understates that
correlation. The simulation and its inputs are in the replication package.

## C.7 Distance from the Medians

Cross-pressure is defined by two median splits, so a member just across either median counts as cross-pressured. To check whether such members produce the gap in Section 5, we measure each member-Congress's distance to the nearer of its two cut lines. Within each Congress and chamber, the economic and the abortion roll-call scales are each centred on their median and divided by their standard deviation; the distance is the smaller of the two absolute values. The rows are those of Section 5 (abortion), split into thirds of this distance, with cut points at 0.29 and 0.69 standard deviations, common to both models. Cross-pressured member-Congresses are concentrated near a median: 1,009 fall in the nearest third, 719 in the middle third and 251 in the furthest third, against 2,469, 2,762 and 3,234 aligned ones.

The difference between the shares of aligned and cross-pressured member-Congresses placed in their own quadrant is 0.441 [0.389, 0.490] in Qwen and 0.635 [0.591, 0.675] in Llama in the nearest third, 0.380 [0.315, 0.445] and 0.676 [0.620, 0.726] in the middle third, and 0.561 [0.480, 0.634] and 0.765 [0.684, 0.841] in the furthest third. Among all member-Congresses it is 0.471 [0.425, 0.515] and 0.707 [0.670, 0.745], and among those at least half a standard deviation from both medians 0.515 [0.447, 0.575] and 0.756 [0.698, 0.813]. In the furthest third, the models place 0.207 (Qwen) and 0.195 (Llama) of cross-pressured member-Congresses in their own quadrant, close to their shares among all cross-pressured member-Congresses (0.208 and 0.174), and 0.768 and 0.960 of aligned ones. The gap therefore does not come from members near a median. Intervals resample members (2,000 draws). The check was specified in writing before it was run; its code is in the replication package.

# Appendix D. Predicting Votes

This appendix describes the vote-prediction design of Section 6 and reports its results in full, including the accuracy of both models
against simple benchmarks.

## D.1 Design

**Roll calls.** The abortion roll calls are the contested roll calls of the abortion scale (Appendix A.3) that decide a matter of
substance; procedural motions are set aside. Questions on whether an amendment is germane are kept as votes of substance, because a finding that the amendment is not germane defeats it; three such roll calls enter, two on abortion and one on guns. Within each Congress and chamber, the same number of economic roll calls is drawn at random
with a fixed seed from the economic roll calls of substance. Gun roll calls are the contested gun-regulation roll calls of Appendix A.3 from 1973 on that decide a matter of substance, 52 in all. Of these, 16 come from Congress-chamber cells without a gun scale. They enter the comparisons that define cross-pressure by abortion votes; comparisons that define it by gun votes use the 36 roll calls from cells with a gun scale. Roll calls whose Voteview text was too thin to describe were left out.

**Descriptions.** For each roll call, a language model (Claude) wrote a neutral description of the measure and of what a YEA and a NAY
vote would do, from Voteview's text only, under written rules: no outcome, no names of members or parties, neutral terms and a short
length. Fixed text rules then flagged outcome words, party cues and loaded terms. A model from another family (GPT-4.1-mini, at
temperature zero) checked each description against the source text, and the flagged descriptions were corrected or adjudicated by the
authors. The authors also read a random sample of descriptions (20 for abortion and economic roll calls and 20 for gun roll calls): all of those sampled for abortion and economic roll calls were accepted, and
the two gun descriptions they judged inaccurate were corrected. The checks by the authors follow the advice to review language-model output by hand, because model annotations can contain errors and a model can override its input with its prior knowledge (Lin & Zhang, 2026). The check by a model from a second family is our own addition. The
description and checking scripts called external models and are not rerun by the package; their outputs ship as fixed inputs.

**Prompt and scoring.** The prompt is given in Appendix A.6. It names the member, chamber, state and year but not the party. Each vote
is asked twice, once with YEA first and once with NAY first. In each order, the model's next-token probabilities for YEA and NAY give a
YEA share, and the prediction is YEA when the average of the two shares exceeds one half. A vote counts as a format failure when the
probability on YEA and NAY together is below one half in either order; failures are dropped (none for Qwen, one economic vote for
Llama, none on guns).

**Estimation.** Accuracy (one for a correct prediction, zero otherwise) is regressed on an indicator for cross-pressured members, with
party x roll-call fixed effects, so that cross-pressured members are compared with aligned members of the same party voting
on the same roll call. Standard errors are clustered two ways, by member and by roll call.

## D.2 Full Results

Figure D1 compares the models' accuracy with two roll-call benchmarks (Appendix D.6), and Figure D2 gives every comparison of cross-pressured with aligned members.

![Figure D1](figures/appendix/D1_accuracy.png)

**Figure D1. For aligned members, both models predict abortion and economic votes less accurately than simple roll-call benchmarks.** Share of votes predicted correctly. Squares: the rule that each member votes with their party's majority. Diamonds: each roll call's own DW-NOMINATE cutting line, which is fitted to the votes it predicts. Vertical line: one half. Hollow circles: Qwen's gun votes, not interpreted (Appendix D.5).

![Figure D2](figures/appendix/D2_coefficients.png)

**Figure D2. Cross-pressured members are predicted less accurately on abortion and, in Llama, on guns, but not on economic votes.** Accuracy of cross-pressured minus aligned members, with party x roll-call fixed effects (roll-call fixed effects within party), clustered by member and roll call. Lines are 95% intervals. Hollow circles: Qwen's gun votes, not interpreted (Appendix D.5).

## D.3 Answer Order

The two orders agree closely in Llama and much less in Qwen. Across votes, the correlation between the YEA shares given in the two
orders is 0.195 (abortion), 0.018 (economic) and 0.212 (guns) in Qwen, and
0.823, 0.776 and 0.853 in Llama. Averaging the two orders removes the effect of order on
the prediction, but in Qwen it also means that many averaged shares lie close to one half.

## D.4 The Leave-One-Out Definition

Cross-pressure is defined from the same roll calls that the models predict. In the leave-one-out definition, for each predicted roll
call, both scales of its Congress and chamber are rebuilt without that roll call and the quadrants are recomputed. Rebuilding with
nothing left out reproduces the original scales and labels exactly. Leaving out the predicted roll call changes the label of a share of
0.011 of abortion votes. The estimates are in Figure D2.

## D.5 Guns

Llama predicts 0.620 [0.545, 0.692] of aligned members' gun votes correctly and 0.494 of cross-pressured members' votes. Within party and roll call, the gap is −0.189 [−0.245, −0.133] when cross-pressure is defined by gun votes (leave-one-out), −0.093 [−0.131, −0.055] when it is defined by abortion votes, and −0.120 for abortion-defined cross-pressure among the same member-Congresses. Unlike abortion, the gap comes from Democrats (−0.165, against 0.005 for Republicans, abortion-defined). State-based cross-pressure and the NOMINATE benchmark on guns are in D.7 and D.8.

Qwen predicts 0.483 [0.435, 0.531] of aligned members' gun votes correctly, and 0.455 of cross-pressured members' votes. Qwen predicts YEA for a share of 0.283 of aligned
members' gun votes, while the actual share is 0.529. Within party and roll call, Qwen's cross-pressured minus aligned
difference is −0.027 [−0.063, 0.010] with abortion-defined cross-pressure and −0.042
[−0.106, 0.022] with gun-defined cross-pressure (leave-one-out). Because Qwen's accuracy on aligned members' gun votes is not above one half, Qwen fails the task check of Appendix D.6 on gun votes, and its gun comparisons are reported but not interpreted.

## D.6 How Well the Models Predict Votes

Both models are weak predictors of individual votes. For aligned members, both are less accurate on abortion and economic votes than the rule that
each member votes with their party's majority, and so is Llama on guns (Figure D1). The majority is computed over all of the party's votes on the roll call, the member's own included. Only for cross-pressured members on abortion, where that rule is wrong more
often than right, do the models do better than the rule. The gap between the parties in the models' predicted YEA shares is also far smaller than the actual
gap: on abortion, 0.059 in Qwen and 0.186 in Llama against an actual gap of
0.513, and on economic votes 0.033 and 0.076 against 0.531.
The comparison in Section 6 is therefore a comparison of accuracy between groups of members within the same party and roll call; it does
not depend on the models being good predictors overall.

The comparison is read only for a model that passes a task check fixed before the results: for aligned members its accuracy is above one half, with a 95% interval from resampling roll calls that excludes one half, and across roll calls the difference between Democrats and Republicans in its predicted YEA share correlates positively with the actual difference, with an interval that excludes zero. Both models pass on abortion and economic votes, and Llama passes on gun votes; Qwen does not (Appendix D.5).

## D.7 State-Based Cross-Pressure

A state's lean is its Democratic share of the two-party presidential vote minus the national share, from the last presidential election
before the Congress begins (MIT Election Data and Science Lab, 2017). A member's state leans toward the other party when it leans
Republican for a Democrat or Democratic for a Republican. Returns begin in 1976, so this definition covers Congresses from 1977 on, and
for House members the state's lean stands in for the district's. Members whose state leans toward the other party are predicted less
accurately on abortion (−0.035 [−0.056, −0.015] in Qwen, −0.054 [−0.075, −0.033] in Llama) and, in Llama, on guns (−0.077
[−0.110, −0.044]), but not on economic votes (−0.002 [−0.019, 0.014] and −0.009 [−0.025, 0.007]). Only for senators is the state the
member's own constituency, and in the Senate alone the abortion estimates are −0.009 [−0.037, 0.018] in Qwen and
−0.032 [−0.066, 0.002] in Llama, with intervals that include zero.

The state-based and vote-based definitions pick out largely different member-Congresses. Of the 9,501 member-Congresses from 1977 on, 1,643 are cross-pressured by their votes and 3,816 by their state, and 824 are both. Among members of the same party, Congress and chamber, a standard deviation more lean toward the other party raises the probability of being cross-pressured by votes by 0.039 [0.027, 0.051]. The map itself moves little with state lean once a member's votes are held constant. Holding the member's own roll-call scale and Nokken-Poole scores constant, a standard deviation of more Democratic lean moves the economic coordinate by −0.015 [−0.028, −0.001] in Qwen and −0.005 [−0.010, 0.001] in Llama, and the social coordinate by −0.017 [−0.031, −0.002] and −0.007 [−0.012, −0.001], in each model's own units. Each shift is less than a tenth of the coordinate's standard deviation within party, Congress and chamber.

## D.8 NOMINATE Fit

The NOMINATE fit is the geometric mean probability that DW-NOMINATE assigns to a member's votes, published by Voteview. Cross-pressured members are fitted less
well: cross-pressured minus aligned members of the same party, Congress and chamber, the geometric mean probability differs by −0.043 [−0.049, −0.038]. Adding this
fit, standardized, to the model of D.1, the cross-pressured minus aligned gap on abortion is −0.032 [−0.060, −0.004] in Qwen and
−0.091 [−0.136, −0.047] in Llama. On gun votes, with cross-pressure defined by abortion votes, Llama's gap becomes −0.051 [−0.082, −0.019] with the fit added (−0.093 without it); Qwen's gun votes are not interpreted (Appendix D.5). Part of the models' difficulty with cross-pressured members is therefore shared with DW-NOMINATE, which also describes these members less well.

## D.9 Individual Members

![Figure D3](figures/appendix/D3_members.png)

**Figure D3. Three well-known cross-pressured senators often voted against their party on abortion.** Squares: share of the member's roll calls on which they voted against their party's majority; roll calls on which the party split evenly are left out. Dots: share predicted correctly. The members were chosen as well-known cases, not by their prediction results; each abortion roll call is listed in the replication package.

Figure D3 shows the three senators named in the text. For Snowe's votes named in Section 6, the models' YEA shares were: on the 1997 and 1998 amendments to repeal the restriction on
abortions at Department of Defense facilities, 0.04 and 0.00 in Qwen and
0.25 and 0.27 in Llama (she voted yea); on the Partial-Birth Abortion Ban Act at final passage and
on the conference report in 2003, 0.50 and 0.50 in Qwen and 0.59 and
0.63 in Llama (she voted nay).

## D.10 Answering on a Scale

Section 6 also reports the vote predictions read from a nine-point scale. The prompt is the one of Appendix A.6 with the description that puts YEA first; its last line is replaced by "Answer with a single number from 1 to 9, where 1 means you certainly vote NAY and 9 means you certainly vote YEA", and by the same sentence with YEA and NAY swapped. In each direction the model's probabilities on the nine digits give an expected answer, rescaled to a YEA lean between zero and one; the prediction is YEA when the average of the two leans exceeds one half. No vote had less than half of the probability on the digits. Because the scale is asked only with YEA described first, Section 6 compares it with the two-answer prediction from that same prompt, not with the average over the two orders: the two-answer abortion coefficient with YEA described first is 0.003 [−0.023, 0.029] in Qwen and −0.109 [−0.156, −0.062] in Llama, and the scale coefficient minus it is the difference reported in Section 6 (Table D1). The scale answers lean further toward one side than the two-answer predictions. Llama predicts YEA for 0.85 of aligned members' abortion votes on the scale, against 0.55 with two answers; Qwen predicts YEA less often on the scale (0.19, against 0.27). With a fixed cut at one half, part of the difference in accuracy between the formats comes from this lean. The squared error of the expected answer, the scale's analogue of the Brier score, needs no cut and gives the same pattern: cross-pressured members' abortion votes are predicted worse by 0.049 [0.027, 0.071] in Qwen and 0.027 [0.010, 0.043] in Llama on the scale, against 0.021 and 0.053 with two answers. Read from the scale, the models pass the same task check as with two answers (Appendix D.6): both models predict more than half of aligned members' abortion and economic votes correctly, and across roll calls the party differences they predict correlate positively with the actual ones; Llama also passes on gun votes, while Qwen's accuracy on aligned members' gun votes is not above one half. Table D1 gives the main estimates of Section 6 and sets each beside its counterpart on the scale, except Qwen's gun votes, which are not interpreted (Appendix D.5).

**Table D1. Vote prediction with two answers and on the nine-point scale: cross-pressured minus aligned members, within party and roll call**

|  | Qwen, YEA or NAY | Qwen, scale | Llama, YEA or NAY | Llama, scale |
|---|---|---|---|---|
| Abortion: accuracy aligned / cross-pressured | 0.554 / 0.486 | 0.528 / 0.435 | 0.693 / 0.531 | 0.634 / 0.554 |
| Abortion: coefficient | −0.048 [−0.079, −0.017] | −0.079 [−0.109, −0.050] | −0.112 [−0.159, −0.065] | −0.036 [−0.068, −0.005] |
| Abortion: coefficient, YEA described first only | 0.003 [−0.023, 0.029] | as above | −0.109 [−0.156, −0.062] | as above |
| Abortion: scale minus YEA-first coefficient | n/a | −0.082 [−0.120, −0.044] | n/a | 0.073 [0.020, 0.126] |
| Abortion: leave-one-out label | −0.049 [−0.081, −0.017] | −0.082 [−0.112, −0.053] | −0.105 [−0.151, −0.059] | −0.033 [−0.065, −0.002] |
| Abortion: Democrats / Republicans | −0.008 / −0.099 | −0.180 / 0.051 | −0.008 / −0.247 | 0.008 / −0.094 |
| Abortion: state-based cross-pressure | −0.035 [−0.056, −0.015] | −0.026 [−0.048, −0.003] | −0.054 [−0.075, −0.033] | −0.028 [−0.046, −0.010] |
| Economic: accuracy aligned / cross-pressured | 0.553 / 0.594 | 0.557 / 0.613 | 0.567 / 0.583 | 0.539 / 0.547 |
| Economic: coefficient | 0.021 [0.002, 0.039] | 0.032 [0.014, 0.051] | 0.013 [−0.008, 0.033] | 0.006 [−0.012, 0.024] |
| Guns: accuracy aligned / cross-pressured | see Appendix D.5 | see Appendix D.5 | 0.620 / 0.494 | 0.633 / 0.522 |
| Guns: coefficient, gun-defined (leave-one-out) | see Appendix D.5 | see Appendix D.5 | −0.189 [−0.245, −0.133] | −0.079 [−0.146, −0.012] |
| Guns: coefficient, abortion-defined | see Appendix D.5 | see Appendix D.5 | −0.093 [−0.131, −0.055] | −0.075 [−0.120, −0.031] |

Note. The YEA or NAY columns are the estimates of Section 6, averaged over the two answer orders (Figure 4 shows the coefficients), except the row with YEA described first only, which uses the scale's prompt; coefficients use party x roll-call fixed effects, clustered by member and roll call, with 95% intervals in brackets. Scale: the prediction is YEA when the average YEA lean of the two directions exceeds one half; same votes and estimator. On the scale Llama predicts YEA far more often than with two answers, so its scale accuracies partly reflect that lean (Appendix D.10).

# Appendix E. Uncertainty

This appendix defines the uncertainty measures of Section 7 and reports the comparisons behind it.

## E.1 Measures

For a choice between two answers, uncertainty is the binary entropy of the model's next-token probabilities, in bits:
H(p) = −p log2 p − (1 − p) log2(1 − p), where p is the probability of the first answer divided by the probability of both. It is zero
when the model puts all its probability on one answer and one when it splits it evenly. For vote prediction, the entropy is computed
in each answer order and the two entropies are averaged. Averaging the probabilities first would give a misleading picture for Qwen,
whose two orders often disagree: the averaged probability would sit near one half even when each order is confident (Appendix D.3).
For named-member questions, an answer in one order counts as a format failure when the probability on Yes and No together is below one half; such answers are dropped (0.020 of answers in Qwen and 0.041 in Llama), and each member-Congress's entropy is averaged over the rest. For free answers to stated profiles, the measure is the entropy over the whole vocabulary at each generated token, in nats, averaged
over the first tokens of a greedy answer.

On the scales, the model answers with a number from 1 to 9, asked in both directions, for votes and for policy questions alike. The entropy over the digits is divided by its maximum (log2 9), so it also runs from zero to one; a two-answer entropy in bits is already a share of its maximum. The two tasks keep their own prompts: the vote-scale prompts use the description with YEA first (Appendix D.10), give the persona in the user message and label the ends "certainly vote NAY" and "certainly vote YEA"; the policy questions give the persona as the system prompt (Appendix A.5) and label the ends "definitely no" and "definitely yes". The scale entropy comparisons of votes leave out the few votes on which a member's party split evenly; the two-answer entropy comparisons and the accuracy comparisons of Section 6 keep them.

## E.2 Comparisons and Reading Rule

Section 7 compares cross-pressured with aligned members in the vote-prediction task (abortion; guns below) and, as a check, in the named-member questions (abortion; guns below), each with two answers and on a scale. A difference reads as higher or lower when its 95% interval excludes zero and its Holm-adjusted p is below .05; there is no minimum size. Every difference that Section 7 reads as higher has a Holm-adjusted p far below .05, so the choice of family decides none of these readings. The Holm family is the one fixed in each comparison's protocol: for two-answer votes, both models' abortion and economic comparisons together (the economic comparisons are not reported in this paper); for two-answer named questions, both models' two abortion comparisons; for the vote scale, each model's primary comparisons in the run that scored the vote scale, which also held named-question comparisons from an earlier seven-point version that the paper does not report, and left out economic comparisons; for the named-question scale, each model's three comparisons (abortion by votes, abortion by the map, guns). Intervals for the two-answer entropy comparisons use a t value with degrees of freedom one less than the smaller number of clusters; intervals for the scale comparisons and in Section 6 use the normal critical value. With this many clusters the two differ in the fourth decimal. Section 7 reports a result as holding in both models only when both models show it in the same direction. The same comparison for stated profiles gives 0.013 [0.006, 0.020] bits in Qwen and 0.061 [0.050, 0.073] in Llama for the choice, and 0.010 [0.001, 0.019] and 0.019 [0.010, 0.028] nats for free answers.

On gun-control votes, with cross-pressure defined by gun votes, Llama is more uncertain about cross-pressured members on the scale (0.067 [0.046, 0.089]) and with YEA or NAY (0.043 [0.025, 0.061]); Qwen does not predict gun votes better than chance (Appendix D.5). Asked about the member, both models are more uncertain about members cross-pressured on guns: by 0.011 and 0.054 with yes or no, and by 0.020 and 0.064 on the nine-point scale.

## E.3 Named-Member Questions

Each model speaks as a named member (Appendix A.5) and answers single-issue Yes-or-No questions on economic and social policy, in both
answer orders, and the same questions on the nine-point scale (Appendix A.6, E.1). The comparison uses all 10,444 member-Congresses with an abortion quadrant. Besides cross-pressure defined by
votes, it also compares members whom the map places in a cross-pressured quadrant with the others, and it is repeated on guns.

## E.4 Whether Uncertainty Points to Errors

For each roll call, we compute the probability that a randomly drawn wrong prediction has higher entropy than a randomly drawn right one
(the area under the curve), and average it across roll calls, weighting each roll call by its number of wrong-right pairs. A value of one half means that entropy does not separate wrong from right predictions. Section 7 reports the group values, with YEA or NAY and on the scale. On the scale, entropy and errors both come from the scale answers, on the rows of Appendix D.10. Intervals, from resampling members within party, are computed for the difference between cross-pressured and aligned members: in Llama, −0.268 [−0.291, −0.244] on abortion and −0.070 [−0.115, −0.021] on guns; in Qwen, 0.032 [0.017, 0.047] and −0.020 [−0.057, 0.014]. On the abortion scale, the difference is −0.209 [−0.232, −0.188] in Llama and −0.025 [−0.043, −0.007] in Qwen.

In Llama, entropy separates wrong from right predictions for aligned members, and the separation weakens for cross-pressured members. Qwen's entropy is close to one half for both groups. On gun votes, Llama's probability falls from 0.664 for aligned to 0.594 for cross-pressured members.

# Appendix F. Why the Economic Side, and Speech

Section 8 asks why the models keep a member's economic position rather than the social one, and notes that cross-pressured members'
floor speech was less partisan. This appendix reports the analyses behind both points. They were added after the main results. They show patterns that fit the discussion, and they do not show what causes the placements.

## F.1 Where the Models Give Social Positions Less Weight

**Do the coordinates carry members' social votes within party?** The two coordinates and the two roll-call scales are standardized within each Congress, chamber and party, among the member-Congresses whose party the model names correctly. Separately for each model and party, these member-Congresses are pooled, the social coordinate is regressed on the abortion and economic scales, and the economic coordinate on the same two scales. The difference between the coefficient of the economic coordinate on the economic scale and that of the social coordinate on the abortion scale (economic minus social) shows how much less the map reflects social votes than economic votes among members of the same party. Intervals resample members. The difference is positive, with an interval that excludes zero, in all four model-party comparisons; for Qwen's Republicans the social coefficient itself is small, its interval reaching below one tenth of a standard deviation.

![Figure F1](figures/appendix/F1_mechanism_speech.png)

**Figure F1. Within party, the map weighs economic votes more than social votes.** Economic minus social coefficient within party (abortion). Lines are 95% intervals.

The social coefficient is positive in each cell, so social votes are reflected in the map. The economic coefficient is larger in all four cells; the difference is smallest for Qwen's Republicans.

**Party or economic side.** Among misplaced cross-pressured members whose party and economic side point to different aligned quadrants, the share placed in their
own party's quadrant is 0.522 [0.424, 0.615] in Qwen and 0.495 [0.407, 0.582] in Llama, close to one half, so
these members do not show whether the party or the economic side wins. Across all misplaced members, the pull toward the economic side
is 0.102 [0.049, 0.157] and 0.176 [0.130, 0.224], and the pull toward the party is
0.124 [0.067, 0.179] and 0.171 [0.123, 0.218]. For most cross-pressured
members, the party's aligned quadrant and the economic side are the same, so the main results cannot separate the two.

## F.2 Floor Speech

**Data and measure.** Floor speeches come from the Congressional Record as parsed by Gentzkow et al. (2018), from the bound edition and,
for the latest Congresses, the daily edition. Speakers are linked to members, and ambiguous or duplicate links are dropped. Phrases that contain digits, procedural phrases, and phrases used by fewer than ten speakers or fewer than twenty times are removed, and members with fewer than five hundred phrase tokens in a Congress are dropped, leaving
9,559 member-Congresses from 1973 to 2016. Partisanship is measured by how well a member's phrases predict their party: for each phrase, the probability that it comes from the member's own party is computed with the member's own speech left out, and these probabilities are averaged over the member's phrases. The overall measure weights the two parties equally.

**Cross-pressured members spoke less partisanly.** Among members of the same party, chamber and Congress, cross-pressured members'
speech partisanship is lower by −0.237 [−0.292, −0.181] standard deviations with abortion-defined cross-pressure and −0.416
[−0.522, −0.310] with gun-defined cross-pressure (clustered by member).

**Speech partisanship and misplacement.** Among cross-pressured members, we find no clear association between speech partisanship and
misplacement on the map (0.010 [−0.026, 0.045] in Qwen, −0.008 [−0.046, 0.031] in Llama).

# Appendix G. Reproduction

Every number in the paper and this appendix can be reproduced with the replication package.

**What the package contains.** One script runs the whole analysis as a graph of steps, each with its declared inputs, and stops at the
first failed step. The package has two paths. The full path reruns everything from the raw data and the two models on one GPU, which
takes several hours. The short path reruns every analysis from the model outputs that ship with the package, on a CPU. A validation
script then compares every output file with a reference copy by its checksum, and every number printed in the paper with the table of
reported values. The manuscript itself is built from that table: each number in the text, the tables and this appendix is filled in from
the package's outputs, and a check stops the build if a printed number has no source.

**Data.** The raw files (Voteview, the Policy Agendas Project, the MIT Election Data and Science Lab, and the Congressional Record files
of Gentzkow et al., 2018) are not redistributed. A script downloads them and checks each against the exact copy used; a mismatch stops
the run.

**Models and determinism.** Both models are loaded at fixed revisions in bfloat16. Deterministic algorithms are enforced, batch sizes
and seeds are fixed, and every random draw uses a seed derived from the name of the analysis. On the same hardware and software, a
rerun gives identical output files. The authors reran the full path from a fresh copy of the package once during the analysis; GPU steps added or changed after that rerun were run once, and their outputs ship with the package. The short path was rerun from a fresh copy of the released package and reproduces every output file and every number in the paper.
On other hardware, the last digits of some model outputs can differ, and the validation script reports which files differ and how much
the reported values change.

**Steps that are not rerun.** Three steps called external language models: the labelling of gun roll calls (Appendix A.3), and the
writing and checking of roll-call descriptions (Appendix D.1). Their scripts ship with the package, and their outputs ship as fixed
inputs.

**Documentation.** The package README lists the analysis folders in the order of the paper, and each folder has a short README that says what it computes and which section or appendix uses it.

## References (Appendix)

Adams, G. D. (1997). Abortion: Evidence of an issue evolution. *American Journal of Political Science, 41*(3), 718–737. https://doi.org/10.2307/2111673

Chen, R., Arditi, A., Sleight, H., Evans, O., & Lindsey, J. (2025). *Persona vectors: Monitoring and controlling character traits in language models* (arXiv:2507.21509v3). arXiv. https://doi.org/10.48550/arXiv.2507.21509

Feldman, S., & Johnston, C. (2014). Understanding the determinants of political ideology: Implications of structural complexity. *Political Psychology, 35*(3), 337–358. https://doi.org/10.1111/pops.12055

Gentzkow, M., Shapiro, J. M., & Taddy, M. (2018). *Congressional Record for the 43rd-114th Congresses: Parsed speeches and phrase counts* [Data set]. Stanford Libraries. https://data.stanford.edu/congress_text

Jones, B. D., Baumgartner, F. R., Theriault, S. M., Epp, D. A., Khandekar, S., & Little, D. (2025). *Policy Agendas Project: Codebook* [Codebook]. https://www.comparativeagendas.net/project/us/datasets

Kim, J., Evans, J., & Schein, A. (2025). Linear representations of political perspective emerge in large language models. In *Proceedings of the Thirteenth International Conference on Learning Representations (ICLR 2025)*. https://openreview.net/forum?id=rwqShzb9li

Layman, G. C., & Carsey, T. M. (2002). Party polarization and "conflict extension" in the American electorate. *American Journal of Political Science, 46*(4), 786–802. https://doi.org/10.2307/3088434

Lewis, J. B., Poole, K., Rosenthal, H., Boche, A., Rudkin, A., & Sonnet, L. (2026). *Voteview: Congressional roll-call votes database* [Data set]. https://voteview.com/

Lin, H., & Zhang, Y. (2026). Navigating the risks of using large language models for text annotation in social science research. *Social Science Computer Review, 44*(3), 403–427. https://doi.org/10.1177/08944393251366243

MIT Election Data and Science Lab. (2017). *U.S. President 1976–2024* [Data set]. Harvard Dataverse. https://doi.org/10.7910/DVN/42MVDX

Nokken, T. P., & Poole, K. T. (2004). Congressional party defection in American history. *Legislative Studies Quarterly, 29*(4), 545–568. https://doi.org/10.3162/036298004X201294

Treier, S., & Hillygus, D. S. (2009). The nature of political ideology in the contemporary electorate. *Public Opinion Quarterly, 73*(4), 679–703. https://doi.org/10.1093/poq/nfp067

Wu, P. Y., Nagler, J., Tucker, J. A., & Messing, S. (2023). *Large language models can be used to estimate the latent positions of politicians* (arXiv:2303.12057v4). arXiv. https://doi.org/10.48550/arXiv.2303.12057
