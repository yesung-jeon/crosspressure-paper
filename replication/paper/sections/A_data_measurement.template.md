# Appendix A. Data and Measurement

This appendix gives the details behind Section 3: the terms used in the paper, the data, the roll-call scales, the economic and social
directions, how members are placed on the map, the prompts, and the models.

## A.1 Terms

- **Member-Congress.** One member in one Congress. It is the unit of the map and of most analyses.
- **Economic, abortion and gun-control scales.** A member-Congress's position on roll calls of each kind (A.3). Higher values are more
  conservative. The abortion and gun-control scales are the two social scales; together the three are the roll-call scales.
- **Quadrant.** The combination of a member-Congress's economic and social positions, each split at the median of its Congress and
  chamber: liberal on both dimensions, conservative on both dimensions, economically liberal and socially conservative, or economically
  conservative and socially liberal. Quadrants are named in words throughout.
- **Aligned and cross-pressured members.** Aligned member-Congresses are liberal on both dimensions or conservative on both;
  cross-pressured ones are economically liberal and socially conservative, or the reverse.
- **Economic and social directions.** Two directions in a model's activations, one for economic and one for social policy (A.4).
- **Coordinates and the map.** A member-Congress's economic and social coordinates are the projections of the model's activation on the
  two directions (A.5). The map is the set of all coordinates.
- **Flatten.** The paper uses the word for two patterns: the models draw the early parties closer together than the roll-call record
  does (Section 4), and they place cross-pressured members with aligned members (Section 5).

## A.2 Members and Roll Calls

Members and votes come from Voteview (Lewis et al., 2026) for the House and Senate from 1947 to 2024. A member-Congress enters the map if
the member has a first-dimension DW-NOMINATE score in that Congress. This gives {{AP_N_MC}} member-Congresses ({{AP_N_HOUSE}} in the
House and {{AP_N_SENATE}} in the Senate) of {{AP_N_MEMBERS}} members, identified by their ICPSR codes. Each Voteview roll call is matched
to its Policy Agendas Project topic (Jones et al., 2025). Of the {{AP_RC_VOTEVIEW}} roll calls in these years, a share of
{{AP_PAP_MATCH}} match; the others are left out of the topic-defined economic scale. State presidential returns come from the MIT
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
environment and social welfare: {{AP_RC_ECON}} roll calls, of which {{AP_RC_ECON_CONTESTED}} are contested. Abortion roll calls are
those whose Voteview description, question or detailed description mentions abortion or the unborn: {{AP_RC_AB}} roll calls, {{AP_RC_AB_CONTESTED}}
contested. A roll call is contested when the smaller side holds at least ten percent of the votes.

**Gun-control roll calls.** Gun roll calls were found by a search of Voteview's text for firearms terms, which returned
{{AP_GUN_CANDIDATES}} contested candidates. Each candidate was labelled by two language models from different families and, where they
disagreed or were unsure, by the authors ({{AP_GUN_AUTHOR}} labels by the authors and {{AP_GUN_AGREED}} by agreement of the two
models). The {{AP_GUN_INCLUDED}} roll calls labelled as gun regulation are coded so that higher values mean more votes against
regulation. A Congress and chamber enters the gun scale only if almost all of its roll calls load in the expected direction and the
scale does not depend on any single roll call; {{AP_GUN_CELLS_PASSED}} of {{AP_GUN_CELLS}} Congress-chamber cells do. The labelling
scripts called external models and are not rerun by the package; their labels are shipped as fixed inputs (Appendix G).

**How a scale is built.** Each scale is estimated separately for every Congress, chamber and issue. Votes of yea are coded 1 and votes
of nay 0. Members with fewer than three votes are dropped, and a cell needs at least three roll calls and twenty members. Each roll call is centred on its mean among the members who voted, and missing votes are then set to zero, which fills them with that mean. The scale is the first principal component of this matrix. It is oriented so that higher values are more conservative: by the sign of its correlation with the first dimension of DW-NOMINATE when that correlation is at least three tenths in absolute value; otherwise so that southern Democrats score higher than other Democrats, when each group has at least five members; and otherwise by the sign of the weaker correlation with DW-NOMINATE. The economic scale
exists for {{AP_SCALES_ECON}} Congress-chamber cells, and the abortion scale for {{AP_SCALES_AB}}, from the Congress that began in 1973.

**Quadrants.** Within each Congress and chamber, the economic and the social scale are each split at the median, with ties assigned to the lower half. Quadrants are assigned to Democratic and Republican member-Congresses with both scales (Figure A1).

![Figure A1](figures/appendix/A1_quadrants.png)

**Figure A1. Most member-Congresses are aligned; about one in five is cross-pressured.** Democratic and Republican member-Congresses with both scales, by quadrant of their votes. Gray bars: aligned quadrants; green bars: cross-pressured quadrants.

Abortion-defined and gun-defined cross-pressure agree for a share of {{AP_GUN_SAME_LABEL}} of the member-Congresses that have both social scales, with both definitions split again at the medians of that common set, and the two social scales correlate at {{AP_GUN_CORR_AB}}.

## A.4 Economic and Social Directions

**Instructions and questions.** Following Chen et al. (2025), each direction is built from five pairs of opposing instructions, one side economically left or
socially progressive and the other the reverse, and a set of policy questions. The instruction and question files ship with the replication package. Twenty questions are used to build the directions. Ten further questions are used to choose the layer, and the first five of these are also used to place members.

**Extraction.** For each instruction and question, the model writes five answers by sampling. Answers that are very short or that
refuse are dropped. The model's hidden state is averaged over the tokens of each answer at every layer, and the direction is the
difference between the average for one instruction of a pair and the average for the other. At the chosen layer, the economic and
social directions are made orthogonal to each other by a symmetric rotation, so that neither direction is privileged.

**Choosing the layer.** At every layer, each direction is added to the model's last-position activation at ten strengths, and the
model answers held-out questions. A judge model (Llama-3.1-8B-Instruct) scores how far each answer leans in the intended direction. The judge is one of the two models studied, so for Llama the layer is chosen with Llama judging its own steered answers. The
judge separates the two kinds of extraction answers well: its area under the curve is {{AP_J1_ECON_Q}} and {{AP_J1_SOC_Q}} for Qwen's
economic and social answers, and {{AP_J1_ECON_L}} and {{AP_J1_SOC_L}} for Llama's. For each direction, layers are ranked by the largest
average judge score over strengths, and the chosen layer is the one with the best combined rank across the two directions. The best
single layers are {{AP_BEST_ECON_Q}} (economic) and {{AP_BEST_SOC_Q}} (social) in Qwen and {{AP_BEST_ECON_L}} and {{AP_BEST_SOC_L}} in
Llama; the combined rule chooses layer {{LAYER_Q}} in Qwen and {{LAYER_L}} in Llama. The replication package repeats the extraction,
the steering, the judging and the choice of layer from the start, and it stops unless both runs give the same layer and identical
directions. Both runs give the same layers.

## A.5 Placing Members

As in Kim et al. (2025), each model is given a system prompt that asks it to speak as one member without stating the party; ours also gives the chamber and state: "You are {name}, who serves in the U.S. {House of
Representatives | Senate} representing {state} in {year}. Answer the question in the first person, as {name} would, reflecting this
person's actual political positions at that time." The prompt does not give the party. The user turn is one held-out policy question;
five economic and five social questions are used. The model's activation at the last prompt token, at the chosen layer, is projected
on the two directions. A member's economic coordinate is the average projection over the economic questions minus the same average
with no persona, and likewise for the social coordinate. On the map, the economic coordinate increases to the right and the social
coordinate increases toward the traditional side.

**Correlations in Table 1.** The correlation with the first dimension of DW-NOMINATE is computed in each Congress, with both chambers
together, and averaged across Congresses. It is lower in the earliest Congress than in the latest ({{AP_R_X_DW1_80_Q}} against
{{AP_R_X_DW1_118_Q}} in Qwen, and {{AP_R_X_DW1_80_L}} against {{AP_R_X_DW1_118_L}} in Llama). The correlations with the roll-call scales are computed after subtracting each Congress-chamber mean. These correlations and the party gaps use only the member-Congresses the model recognizes (below). The party gap in Table 1 is the difference between the Republican and the
Democratic mean divided by the standard deviation of all coordinates.

**Recognized members.** To check whether a model knows a member, each model is also asked, "Which political party did {name}, a member
of the U.S. {chamber} from {state} in {year}, belong to? Answer with one word." A member-Congress counts as recognized when the answer names the member's actual party. This shows that the model can name the party, which the state and year may suggest; it does not show that the model knows the member. Qwen recognizes a share of {{AP_RECOG_Q}} of member-Congresses and Llama {{AP_RECOG_L}}. Unless stated otherwise, analyses keep the coordinates of unrecognized members. The exceptions are the correlations and party gaps of Table 1, the selected members of Appendix C.4 and the within-party analysis of Appendix F.1, which use recognized member-Congresses only. Section 5 also reports placement for recognized members only.

## A.6 Prompts

The prompts for each task are reproduced below. Braces mark the parts filled for each member, profile or roll call.

**Member persona (map, Sections 4 and 5).** As in A.5.

**Stated profiles (Section 5).** The anonymous persona states the profile's positions: "This member supports {economic position} and
{social position}." The economic positions are "expanding Social Security, public health insurance and union rights" and "cutting
taxes, reducing government spending and deregulating business"; the social positions are "abortion rights and same-sex marriage" and
"restrictions on abortion and a traditional definition of marriage." The same positions are also given in the user turn, through the
paired instructions of A.4, through four answered example questions, or through a named member who holds them (Appendix C.6). Each
item ends with "Answer with Yes or No."

**Vote prediction (Section 6).** "You are {Senator | Representative} {name}, representing {state} in the United States {Senate | House
of Representatives} in {year}. Consider the following roll-call vote: {description} A YEA vote would: {what a yea vote does}. A NAY vote
would: {what a nay vote does}. How would you vote, based on your policy positions as this {senator | representative} at that time?
Respond with exactly one word: YEA or NAY." In the second order the two meaning lines are swapped and the last line reads "NAY or YEA"
(Appendix D.1).

**Choices between policy packages (Section 7, Appendix C.8).** "You must choose between two policy packages. A) {package} B) {package}
Which do you choose? Answer with A or B only." The positions are listed in Table A2. Here the persona is a Democratic or Republican member of the House from a given state and
year, so the party is given.

**Named-member questions (Section 7).** The member persona of A.5, followed by a single-issue question and "Answer with Yes or No." or
"Answer with No or Yes." The questions are the sixteen single-issue items of Table A1.

**Table A1. Items for stated profiles and named members**

{{ITEMS_PROFILES}}

**Table A2. Positions combined into policy packages**

{{ITEMS_PACKAGES}}

Note. A package joins one economic and one social position with "and". In the party-like version, the liberal economic position is
paired with the progressive social position; in the crossed version, with the traditional one.

## A.7 Models and Computation

The models are Qwen2.5-7B-Instruct and Llama-3.1-8B-Instruct, loaded at fixed revisions that are listed in the replication package, in
bfloat16. Directions are extracted from sampled answers; steering generations and the party question use greedy decoding. Member placement on the map and the coordinates of stated profiles are projections of the hidden state at the last prompt token. Answers to Yes-or-No questions, choices between policy packages and vote predictions are read from the model's next-token probabilities. None of these involves sampling. All computations run in deterministic mode with fixed
batch sizes and seeds, and a rerun on the same hardware and software gives identical outputs (Appendix G).
