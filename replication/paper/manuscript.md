# Language Models Reconstruct a Different History of American Political Polarization

# Abstract

Language models increasingly stand in for political actors, and they are judged by their agreement with an aggregate
liberal–conservative ordering. Such models could become instruments for studying political history, but only if they represent the
past as the record describes it. An aggregate ordering cannot show whether they reproduce
how polarization unfolded, or whether they represent cross-pressured members, whose economic and social votes cut across party lines.
We extract economic and social directions from two open models, place every member of Congress from 1947 to 2024 on them, and compare
the resulting map with roll-call records and DW-NOMINATE. The models flatten the political past. They draw the early postwar parties
closer together than the record does and portray a larger economic divergence that, in their coordinates, comes mostly from Democrats.
They also misplace most cross-pressured members: on their internal map they move them toward the aligned position on their economic side, they follow cross-pressured profiles less faithfully when the positions are stated in the prompt, and they predict these members' abortion votes less accurately. Language models that match the aggregate ordering can thus misplace the members whose decline was part of how the parties polarized.

# 1. Introduction

Language models are increasingly used to stand in for political actors. They have been used to place senators on ideological scales
(Wu et al., 2023) and to predict roll-call votes by simulating members as agents (Kreutner et al., 2026; Li et al., 2025). When
they write as individual members, their internal activations track the members' positions on the liberal–conservative dimension
(Kim et al., 2025). These simulations are usually judged by how well they agree with an aggregate ordering of members from liberal to
conservative.

If models hold such representations, they could become instruments for studying political history. A model can be asked to speak as
a member of any Congress, past or present, and its answers can be compared with the record that member left. For members of Congress, this promise rests on
an assumption that has not been tested: that the model represents the past as the record describes it.

However, agreement with an aggregate ordering cannot reveal two things. First, it cannot reveal whether the change over time that a
model reconstructs matches the roll-call record. In that record, congressional polarization since the 1970s has been asymmetric and led by
Republicans (McCarty et al., 2006; Moskowitz et al., 2024). Second, it cannot reveal whether the model represents
cross-pressured members, whose economic and social votes cut across party lines, such as Democrats who opposed abortion rights and
Republicans who supported them. Before the parties sorted on social issues, abortion divided each party internally (Adams, 1997; Layman & Carsey, 2002), and the decline of members who departed from their party's typical positions is
part of how polarization happened (Thomsen, 2014). Work on synthetic respondents gives reason for concern on both counts. Models that
stand in for people tend to flatten the variety within groups (Rennard & Xypolopoulos, 2026; Wang et al., 2025), and a model asked to
speak as a person from the past may draw on text written long afterwards (Kozlowski & Evans, 2025).

This paper asks whether two open language models preserve these distinctions. We extract an economic and a social direction from the
activations of Qwen2.5-7B-Instruct and Llama-3.1-8B-Instruct, prompt each model to speak as every member of Congress from 1947 to
2024 without naming the member's party, and place each member on the two directions. The resulting map answers both questions.
Read across Congresses and compared with DW-NOMINATE, it shows the history of polarization the models reconstruct. Read member by
member and compared with each member's own roll-call record, it shows whether the models place cross-pressured members where their
votes put them. We then examine cross-pressure in two other ways: by stating a cross-pressured profile's positions in the prompt, and by asking the models to predict members' actual votes.

We find that the models flatten the political past on both counts. Over time, they draw the early postwar parties closer together
than the record does, and the economic party gap they reconstruct grows more than the gap in DW-NOMINATE. In the models' coordinates,
most of that growth comes from Democrats moving left, whereas in DW-NOMINATE most of it comes from Republicans moving right.

Across members, the models place most aligned members where their votes put them but misplace most cross-pressured members. On abortion, the maps place only
0.208 (Qwen) and 0.174 (Llama) of cross-pressured member-Congresses (one member in one Congress) in the quadrant of their own
votes, whereas a two-dimensional DW-NOMINATE placement of the same member-Congresses places 0.681. Most of the members the models misplace are moved into the aligned quadrant that shares their economic position, which for most of them is also their party's. When a cross-pressured profile's positions are stated in the prompt, the models follow it less faithfully. When the models predict the members' votes, they are less accurate on abortion but not on economic votes. As the work on synthetic respondents would lead one to expect, the models flatten differences within each party, and they also flatten the differences between the early parties.

The models are also slightly more uncertain about cross-pressured members: in both models when they answer on a scale or are asked about the member, and in Llama when they answer YEA or NAY. The models' probabilities thus carry the uncertainty that studies of voting attach to cross-pressure, but that uncertainty does not flag the votes they get wrong.

The paper makes two contributions. First, it extends the linear representation of political perspective in language models from one
dimension to two for simulated members of Congress. Earlier work used one dimension (Kim et al., 2025) or separate economic and social directions for the model's own stance (Nadeem et al., 2025), and found that a single direction transfers poorly to simulated votes (Zhang, 2025). We validate every
placement against roll calls and read the representation over time as a reconstructed history. Second, it shows that validation
against an aggregate ordering can hide both a different history of polarization and the members who did not fit that history. Models
used in this way may misdescribe how the parties polarized and hide how varied past Congresses were.

Section 2 reviews the two dimensions and the history of congressional conflict, the members who crossed party lines, and what is
known about language models as simulated political actors. Section 3 describes the data and methods, and Sections 4 to 7 report the history the models reconstruct, the map
and stated profiles, vote prediction, and the models' uncertainty. Section 8 discusses the implications.

# 2. Background

Three bodies of research bear on the questions raised in the introduction: work on the dimensions and history of congressional
conflict, work on the members who crossed party lines, and work on language models as simulated political actors.

## 2.1 The Two Dimensions and the History of Polarization

A single liberal–conservative dimension describes most roll-call voting in Congress, and a second dimension captures the conflicts that
divide the parties internally (Poole & Rosenthal, 1991). How much the first dimension appears to capture has itself changed, because polarization can make roll-call voting look more one-dimensional than members' preferences are (Aldrich et al., 2014). Polarization can therefore be read in two ways: as the
distance between the parties, and as *constraint*, the degree to which positions on different issues move together (Baldassarri &
Gelman, 2008). Over recent decades, voters' economic and social positions have become more tightly bound to a single ideological
dimension (Hare, 2022).

That binding happened at different times for different issues. Economic issues have divided the parties since the New Deal, whereas
social issues entered party conflict later (Layman & Carsey, 2002). Abortion is the clearest case. When the Supreme Court decided Roe
v. Wade, the parties' positions on abortion were still unclear (Adams, 1997). State party platforms did not mention it before 1968, the parties' platforms began to separate in 1970 and differed clearly by 1978, and some Democratic state parties opposed abortion rights during that decade
(Gamm et al., 2024).

As social issues joined economic ones, the distance between the parties also grew. At mid-century the parties competed for the
political middle. Since the 1970s they have moved apart (Theriault, 2008), and they have done so asymmetrically, mostly because Republicans moved right (McCarty et al., 2006; Moskowitz et al., 2024) and moderate southern Democrats were replaced by Republicans (McCarty et al., 2006). This account rests largely on DW-NOMINATE, and
the first dimension of DW-NOMINATE may record party as well as ideology, so its picture of polarization is itself one measurement among
others (Caughey & Schickler, 2016). Section 4 compares the history the models reconstruct with this record.

## 2.2 Members Who Crossed Party Lines

Low constraint leaves room for people whose positions point in different directions. The idea of cross-pressure comes from early
studies of voting, and later work links such cross-cutting pressures to ambivalence, more moderate positions and less certainty in
political judgments (Mutz, 2002).

In Congress, members who crossed their party were common for much of the postwar period. Until the early 1980s, each party contained
substantial numbers of members outside its mainstream, and these members disappeared through replacement and conversion (Fleisher &
Bond, 2004). Their decline is part of how the parties polarized (Thomsen, 2014), and cooperation across party lines in the House now
rests on very few members (Andris et al., 2015).

Outside Congress, the same combinations remain common. On a single liberal–conservative scale, people who are liberal on one dimension
and conservative on the other look like moderates (Fowler et al., 2023; Treier & Hillygus, 2009). In the American National Election
Studies of 1984–2004, about two in five respondents were what Baldassarri and Goldberg (2014, p. 45) call "alternatives," who are "morally conservative but economically liberal, or vice versa." Whether such citizens hold a belief system of their own, or the dominant one held more
loosely, is disputed (Boutyline & Vaisey, 2017). Sections 5 and 6 ask how the models place and predict the members of Congress who held
such combinations, and Section 7 whether the models' own probabilities show the uncertainty that this literature attaches to cross-pressure.

## 2.3 Language Models as Simulated Political Actors

A simulated member of Congress has to represent these combinations, and language models have been shown to carry political
information in their internal states. When models write as individual members of Congress, a linear direction in their activations
tracks the members' liberal–conservative positions (Kim et al., 2025). Models also encode when historical figures lived (Gurnee &
Tegmark, 2024). Political ideology appears in more than one partly separate structure (Zhang, 2025), and separate economic and social directions can be found for a model's own stance (Nadeem et al., 2025).

Models that carry this information may still reproduce it unfaithfully. When models simulate people, they reproduce aggregate distributions
(Argyle et al., 2023), but fidelity weakens below the aggregate. Relationships between variables are lost (Bisbee et al., 2024), and
some groups are represented better than others (Santurkar et al., 2023). Strong partisans are predicted better than independents, which Kim and Lee (2026) relate to partisans' more coherent beliefs, in which opinions are highly correlated, and voters who follow their party are predicted better than
those who do not (von der Heyde et al., 2026). Models can represent a group as a monolith (Hu & Collier, 2024) and flatten the variety within groups (Wang et al., 2025), and personas
that combine two identities answer as if they held only one (Rennard & Xypolopoulos, 2026). A model asked to speak as a person from the
past may also draw on text written long afterwards (Kozlowski & Evans, 2025).

A model's own probabilities could, in principle, signal where such simulations fail. Language models' token probabilities can be well calibrated on familiar material (Kadavath et al., 2022). Their estimates of whether they know an answer are less well calibrated on new tasks, and the entropy of their sampled answers is not a reliable sign of what they know (Kadavath et al., 2022). Their answers to survey-style questions also carry systematic biases tied to how the options are presented
(Dominguez-Olmedo et al., 2024). These studies concern simulated respondents and general questions. How models treat past members of
Congress, and whether their uncertainty follows their errors about these members, has not been examined. Section 3 describes how we
measure both.

# 3. Data and Methods

To ask whether a language model places members where their roll-call votes put them, over time and member by member, we need a way to read where the model places a
member, a record to compare it with, and tests that look at cross-pressure from more than one side. This section builds them in that
order.

**Two models.** We study Qwen2.5-7B-Instruct and Llama-3.1-8B-Instruct (Llama Team, 2024; Qwen Team, 2025), hereafter Qwen and Llama.
Our questions concern what happens inside a model, so we use models whose weights are public. The two come from different developers, so a result that holds in both does not rest on one training pipeline. We fix the model versions and run all
computations deterministically, so that every result in the paper can be reproduced exactly on the same hardware and software; the replication package runs every step from the raw data and the public models (Appendix G).

**Economic and social directions.** To place members on two dimensions of conflict, we first need to find those
dimensions inside each model. Following Chen et al. (2025), we prompt each model with pairs of opposing instructions, one pair about
economic policy and one about social policy. The difference between the average activations of the two kinds of answers gives the
model's economic direction and its social direction. We take the directions from the layer at which moving along them most changes
the model's answers: layer 16 in Qwen and layer 15 in Llama. Repeating the whole procedure selects the same layers
(Appendix A.4).

**Placing members: the map.** With the two directions in hand, we place members. For each member in each Congress from 1947 to 2024, a
member-Congress with a DW-NOMINATE score (Appendix A.2), each model is asked to speak as that member. The prompt gives the member's name, chamber, state and year; as in Kim et al. (2025), it does not give the party. Projecting the model's activation onto the two directions gives the member's economic and social coordinates.
Together, these coordinates form the map that Sections 4 and 5 examine (Appendix A.5). The map is the readout under this prompt; it is not a fixed property of the model.

**The roll-call record and cross-pressure.** A map is informative only if it can be checked against what members did. Because economic
and social ideology are distinct dimensions (Feldman & Johnston, 2014), we measure each member's economic and social positions
separately, from roll calls in Voteview (Lewis et al., 2026). The economic scale uses roll calls on the economic topics of the Policy
Agendas Project (Jones et al., 2025). Social positions are measured on abortion, the social issue whose roll calls span the period and
on which the parties were at first internally divided (Adams, 1997; Layman & Carsey, 2002), and, as a second issue reported in the appendices, on gun control (Appendix A.3). Splitting each scale at its median within Congress and chamber places every Democratic and Republican member-Congress with both scales in one of four quadrants.
Cross-pressured members are those whose economic and social scales fall on opposite sides, economically liberal and socially
conservative or the reverse. All others are aligned members. Section 6 adds two definitions that do not depend on the same votes: a
leave-one-out definition, which leaves out the roll call being predicted, and state-based cross-pressure, which holds when the member's state leans toward the other party in presidential elections (MIT Election Data and Science Lab, 2017); for House members, the state stands in for the district.

**Reference scales.** As references, we use the DW-NOMINATE scores that Voteview publishes in one and two dimensions (Lewis et al., 2026), which descend from the NOMINATE scaling of Poole and Rosenthal (1991). We also use Nokken-Poole scores, which estimate each member's position in every
Congress while holding the roll-call parameters fixed (Nokken & Poole, 2004). How well DW-NOMINATE fits a member's votes, the NOMINATE fit, is Voteview's geometric mean probability of those votes.

**Three tests.** A single measurement could mislead, so we examine cross-pressure in three ways. First, following the map Congress by Congress, we compare the party gap on each model's economic direction with the party gap on the first dimension of
DW-NOMINATE, each in standard deviations of its own scale. We then split the change into Democratic and Republican movement, and into
the movement of continuing members and the replacement of members (Section 4). Second, we check whether each member-Congress falls in
the quadrant of its votes, and whether the models follow cross-pressured profiles when the profile's positions are stated in the prompt
instead of a name (Section 5). Third, each model predicts members' votes on abortion and economic roll calls from the
member's name, state, chamber and year and a neutral description of what a YEA and a NAY vote would do (Section 6; gun-control votes in Appendix D.5). The descriptions were
drafted by a language model from Voteview's text, screened by fixed rules for outcome and party cues, checked by a model from another
family (GPT-4.1-mini), and spot-checked by the authors (Appendix D.1). Accuracy is compared among members of the same party voting on the
same roll call, with intervals clustered by member and by roll call.

**The models' own uncertainty.** Finally, we ask whether the models register these members as harder (Section 7). We measure
uncertainty as the entropy of a model's next-token probabilities over the answer options, divided by its maximum so that two-answer and scale formats share one range from 0 to 1. Whether uncertainty points to errors
is measured as the probability that, on the same roll call, a wrong prediction has higher entropy than a right one.

**The map tracks roll-call positions.** Before the tests, we check that the map measures what it should. The models' economic
coordinates track the first dimension of DW-NOMINATE (0.598 in Qwen and 0.836 in Llama, the mean of
correlations computed within each Congress) and the economic scale (0.681 and 0.873, correlated within Congress and
chamber). The party gap is larger on the economic than on the social
direction, and most aligned member-Congresses fall in the quadrant of their own votes (Table 1). The correlations and party gaps use the member-Congresses whose party the model names correctly (Appendix A.5). Because the map tracks roll-call positions for most members, the misplacements reported in the sections that follow are not a general failure of measurement.

**Table 1. The models' directions track members' roll-call positions**

|  | Qwen | Llama |
|---|---|---|
| Selected layer | 16 | 15 |
| r(economic coordinate, DW-NOMINATE dimension 1) | 0.598 | 0.836 |
| r(economic coordinate, economic roll-call scale) | 0.681 | 0.873 |
| r(social coordinate, abortion roll-call scale) | 0.588 | 0.741 |
| Party gap, economic direction (SD) | 1.169 | 1.533 |
| Party gap, social direction (SD) | 0.686 | 1.155 |
| Share of aligned member-Congresses in their own quadrant (abortion) | 0.679 | 0.881 |

Note. The correlation with DW-NOMINATE dimension 1 is the mean of correlations computed within each Congress; the other correlations are computed within Congress and chamber. Correlations and party gaps use the member-Congresses whose party the model names correctly; the shares in own quadrant use all Democratic and Republican member-Congresses with both scales (Appendix A.5). The same layer is chosen when the directions are extracted twice (Appendix A.4).

# 4. The Models Reconstruct a Different History of Polarization

Across Congresses, the map gives the history of polarization that each model reconstructs. Figure 1 shows each party's mean on
each model's economic direction in every Congress, with the first dimension of DW-NOMINATE, the roll-call record against
which this history is usually told, drawn inside each panel; the social direction is in Appendix B.5. Figure 2 shows the members behind these means: each model's map in four Congresses. Each scale is measured in its own standard deviations, and Appendix B gives the definitions and the full results. Measuring each scale in its own standard deviations makes the histories comparable in shape; the early separation below is computed within each Congress and chamber and does not depend on a scale's spread over the whole period.

![Figure 1](figures/body/fig1_history.png)

**Figure 1. On the economic direction, the models' party gap starts smaller and grows more than DW-NOMINATE's, and in their coordinates the growth comes mostly from Democrats.** Each party's mean position on each model's economic direction in every Congress (time runs down), in standard deviations of the axis and centred on the two parties' 1947–1958 midpoint. (a) Qwen, (b) Llama; dashed lines: DW-NOMINATE first-dimension party means, scaled the same way. Above each panel: the party gap as drawn at the start and end of each series, with DW-NOMINATE's. The axes use standard deviations over all Congresses, whereas the early separation in the text is measured within each Congress (Appendix B.2). Intervals for the early and late comparison are in Appendix B; the social direction is in Figure B4.

![Figure 2](figures/body/fig2_snapshots.png)

**Figure 2. On both maps the parties start closer together than in DW-NOMINATE and move apart, Democrats furthest.** Each model's map in 1947, 1971, 1995 and 2023. Points: Democratic and Republican member-Congresses; large circles: party means, with their paths over the earlier Congresses; dashed lines: DW-NOMINATE first-dimension (liberal–conservative) party means in that Congress, drawn on the horizontal axis only. Both coordinates are in standard deviations and centred on the two parties' 1947–1958 midpoint, as in Figure 1, but here every member counts equally, whereas Figure 1 weights the two chambers equally, so the party means differ slightly.

**A larger divergence.** The economic party gap widens in both models, and it widens more than it does in DW-NOMINATE, where the gap
grows from the 1970s on (McCarty et al., 2006; Theriault, 2008). Over the period, the gap on the models' economic direction grows by
2.285 standard deviations in Qwen and 2.187 in Llama. This exceeds the growth in DW-NOMINATE by 1.381
[1.192, 1.557] in Qwen and 1.283 [1.172, 1.381] in Llama.

**Who moves.** In DW-NOMINATE, most of the growth comes from Republicans
moving right (McCarty et al., 2006; Moskowitz et al., 2024). Computed the same way here, Democrats account for a share of
0.357. In the models' coordinates, they account for most of it: 0.679 in Qwen and 0.730 in Llama,
which exceeds the DW-NOMINATE share by 0.322 [0.261, 0.385] and 0.373
[0.320, 0.431]. In both models, Democrats move left (−1.551 and −1.597) and Republicans move right
(0.733 and 0.590). Party means change both because members change their positions and because new members
replace old ones. Following the same members across Congresses from 1949 on separates the two. The part of the Democratic movement that comes from
continuing members goes further left on the models' maps than in the same members' Nokken-Poole scores: the model minus Nokken-Poole difference is −0.600
[−0.741, −0.451] in Qwen and −1.115 [−1.243, −0.985] in Llama. For continuing Republicans, the difference is 0.274 [0.099, 0.434] in Qwen and 0.154 [−0.024, 0.327] in Llama: both are positive, but only Qwen's interval excludes zero. Because each member is prompted with a name, state and year, the models' coordinates may also carry their image of each party in that year; the history in this section is the one those coordinates draw.

**A flatter beginning.** In the early postwar Congresses, the parties in DW-NOMINATE are apart, but far closer than they later become.
Political scientists describe the parties at mid-century as competing for the political middle (McCarty et al., 2006). The models draw
them closer still. Measured within each Congress and chamber, the early separation between the party means is 1.657 standard
deviations in DW-NOMINATE, 0.259 in Qwen and 1.003 in Llama. Qwen's separation is
about a sixth of DW-NOMINATE's (0.156 [0.048, 0.261]), and Llama's is about three-fifths
(0.605 [0.542, 0.664]). The pattern remains among the member-Congresses whose party the model names correctly: their early separation is 0.254 [0.141, 0.364] of DW-NOMINATE's in Qwen and 0.615 [0.550, 0.675] in Llama, and their gap grows more than DW-NOMINATE's by 1.172 [0.975, 1.364] and 1.203 [1.098, 1.308] (Appendix B.2). Naming the party is a weak test of what a model knows about a member, and the models' coordinates track DW-NOMINATE less closely in the earliest Congresses (Appendix A.5).

**All in all.** On both models' maps, the parties begin closer together than in the record and then diverge further,
mostly on the Democratic side. The roll-call record shows a divergence led by Republicans. The models thus flatten the differences between the early parties. The correlations in Table 1 cannot show this, because they are computed within each Congress, and they also cannot show whether each member is placed where their votes put them. In those early decades, each party contained substantial numbers of members outside its mainstream (Fleisher & Bond, 2004), and moderate southern Democrats had not yet been replaced by Republicans (McCarty et al., 2006). Abortion also divided each party internally before the parties sorted on it (Adams, 1997; Layman & Carsey, 2002). Section 5 takes up the second question, member by member, for cross-pressured
members.

# 5. The Models Move Cross-Pressured Members into the Aligned Quadrant That Matches Their Economic Votes

Member by member, the map shows whether each member is placed where their votes put them. For each Democratic and Republican member-Congress with both roll-call scales, we compare the quadrant the map assigns with the quadrant of the member's economic and social roll-call scales. Figure 3 shows the result on abortion for both models; guns and the results by quadrant are in Appendix C.1.

![Figure 3](figures/body/fig3_placement.png)

**Figure 3. Both models place most aligned members in the quadrant of their votes, but few cross-pressured members.** Abortion. Open circles: each vote-quadrant group's mean position by its roll-call scales; filled circles: its mean position on the model's map; arrows join the two (colored: the two cross-pressured groups; grey: the aligned groups). Positions are percentile ranks within Congress and chamber among Democratic and Republican member-Congresses from 1973 on with both scales, so 0.5 is the median line. Faint points: cross-pressured member-Congresses where the model places them. Shaded: each party's aligned corner. Panel titles: share of cross-pressured member-Congresses placed in the quadrant of their votes. The two-dimensional DW-NOMINATE comparison is in the text and Appendix C.1; the 60 members selected by their votes are in Appendix C.4.

**Aligned members land in their own quadrant; cross-pressured members do not.** The maps place most aligned member-Congresses in the quadrant of their
own votes and few cross-pressured ones. On abortion, Qwen places 0.679 of aligned member-Congresses and
0.208 of cross-pressured ones in their own quadrant, and Llama places 0.881 and 0.174. Appendix C.1 gives the same comparison on guns. The gap does not come from members who sit just across a median. Among the third of member-Congresses whose roll-call positions lie furthest from both medians (251 of them cross-pressured), Qwen places 0.768 of aligned and 0.207 of cross-pressured member-Congresses in their own quadrant, and Llama 0.960 and 0.195. The difference, 0.561 [0.480, 0.634] in Qwen and 0.765 [0.684, 0.841] in Llama, is no smaller than among all member-Congresses (0.471 and 0.707; Appendix C.7).

**Two-dimensional DW-NOMINATE places more of them in their own quadrant.** In NOMINATE scaling, the second dimension captures conflicts that divide the parties internally (Poole & Rosenthal, 1991). A two-dimensional DW-NOMINATE placement of the same member-Congresses places
cross-pressured ones in their quadrant more often than aligned ones: 0.681 against 0.546 on
abortion (guns in Appendix C.1).

**Recognition does not explain it.** A model may misplace members it does not know. Restricting the comparison to member-Congresses whose
party the model names correctly leaves the pattern unchanged. On abortion, Qwen places 0.195 of these cross-pressured
member-Congresses in their own quadrant and Llama 0.179, against 0.732 and 0.899 of aligned ones (Appendix C.2).

**Measurement error does not explain it.** A map that tracked members' votes only as closely as the models' maps do, with the rest random noise, would place 0.448 (Qwen) and 0.594 (Llama) of cross-pressured member-Congresses in their own quadrant on abortion, far more than the models' maps place (Appendix C.6). Noise alone would already send many misplaced members toward their economic side on abortion, but fewer than the models do (guns in Appendix C.6).

**Where the misplaced members go.** Most misplaced cross-pressured member-Congresses land in the aligned quadrant that matches their economic
votes. Members who vote liberal on economics are placed as liberal on both dimensions, and members who vote conservative on economics
as conservative on both. On abortion, this is where 0.571 (Qwen) and 0.751 (Llama) of the misplaced
economically liberal, socially conservative member-Congresses go, and 0.574 and 0.740 of the misplaced
economically conservative, socially liberal ones (Appendix C.3). For most of these members, that quadrant is also the aligned quadrant of their own party, so the two cannot be told apart; among misplaced members whose party and economic side point to different aligned quadrants, the models favor neither (Appendix F.1). Cross-pressured members are also placed in their own quadrant less often
among 60 members selected by their votes, 15 from each quadrant. Of the 15 members in each aligned quadrant, Qwen places
10 and 10 in their own quadrant. Of the 15 in each cross-pressured quadrant, it places
5 and 1. For Llama, the numbers are 15 and 15 against
1 and 2.

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
aligned ones. Cross-pressured minus aligned, the probability of answering consistently with the stated profile, among the Yes and No answers, differs by −0.089 [−0.098, −0.081] in Qwen and −0.126 [−0.139, −0.114] in Llama, and the share of conditions in which the profile's coordinates reach the stated quadrant differs by −0.323 [−0.385, −0.265] and −0.308 [−0.350, −0.262] (Appendix C.5).

**All in all.** On the models' internal map, cross-pressured members are misplaced, and mostly in one direction: toward the aligned position on their economic side. With stated profiles, the models follow cross-pressured profiles less faithfully. The models thus flatten the differences within each party. Section 6 asks whether cross-pressured members are also mispredicted when the models predict their actual votes.

# 6. Predicting Their Votes: Errors Fall on Cross-Pressured Members

Sections 4 and 5 examine the models' internal map, and a misplacement on the map need not carry over to what the models answer. This section therefore asks the models to predict votes. Each model receives a member's name, state, chamber and
year, without the party, together with a neutral description of a roll call, and answers YEA or NAY. Each vote is asked twice, once with
YEA first and once with NAY first, and the two answers are averaged. We compare these predictions with the votes members actually cast on abortion and economic
roll calls (Appendix D.1; gun-control votes in Appendix D.5).

**Less accurate for cross-pressured members on abortion.** Both models predict cross-pressured members' abortion votes less accurately
than aligned members' votes: 0.486 against 0.554 in Qwen, and 0.531 against
0.693 in Llama. Cross-pressured members may vote on different roll calls, or belong to a different party, from aligned
members, so we compare members of the same party voting on the same roll call, with intervals clustered by member and by roll call. The
gap remains: −0.048 [−0.079, −0.017] in Qwen and −0.112 [−0.159, −0.065] in Llama (Figure 4). It also remains when
cross-pressure is defined without the roll call being predicted (−0.049 and −0.105; Appendix D.4). Cross-pressured members' abortion votes are hard for any predictor. The first dimension of DW-NOMINATE predicts 0.919 of aligned and 0.374 of cross-pressured members' abortion votes, and the rule that each member votes with the party majority 0.879 and 0.351 (Appendix D.6). The models' gap is smaller than these benchmarks'. The finding is that the models, given the member's name, state and year, do not recover these members' abortion votes.

**Not on economic votes.** On economic roll calls, cross-pressured members are predicted at least as accurately as aligned members
(0.021 [0.002, 0.039] in Qwen and 0.013 [−0.008, 0.033] in Llama). Qwen's two answer orders barely agree on economic votes (Appendix D.3), so its small advantage there should not be read as better prediction. The deficit appears on abortion votes and not on economic votes. Abortion is also the issue on which the map misplaces these members in Section 5.

**Which members, and which way.** In Llama the abortion gap comes from Republicans (−0.247
[−0.334, −0.160]); for Democrats it is close to zero (−0.008). Qwen shows the same pattern more
weakly (−0.099 for Republicans, −0.008 for Democrats).

![Figure 4](figures/body/fig4_votes.png)

**Figure 4. Cross-pressured members are mispredicted on abortion, not on economic votes.** Each cell is the difference in the share of votes predicted correctly between cross-pressured and aligned members of the same party voting on the same roll call (party x roll-call fixed effects; intervals clustered by member and roll call). Red: less accurate; blue: more accurate. Bold cells: the 95% interval excludes zero; pale cells: it includes zero. Rows: all cross-pressured members; each party's cross-pressured members (roll-call fixed effects within the party); cross-pressure defined without the roll call being predicted. Estimates are in Table D1, and those with intervals in Figure D2; guns, state-based cross-pressure and the NOMINATE benchmark are in Appendix D.

Olympia Snowe, a Republican from Maine, shows what this looks like for one member. In the House and later in the Senate, she voted
against the majority of her party on 95 percent of the 64 abortion roll calls in our data, and on
24 percent of the economic ones. Llama predicts 0.484 of her abortion votes correctly. Two sets of abortion votes show its misses. In
1997 and 1998 the Senate voted on amendments to repeal the restriction on performing abortions at Department of Defense facilities.
Snowe voted for repeal, against most Republicans; Llama gave her a probability of voting yea of 0.25 and
0.27, and Qwen gave 0.04 on the first. In 2003 she voted against the Partial-Birth Abortion Ban
Act at final passage and again on the conference report, while most Republicans voted for it. Llama predicted a yea vote both times (0.59 and 0.63). On economic roll calls, Llama
predicts her votes more accurately (0.651).

**Other definitions, other benchmarks.** The abortion deficit also appears when cross-pressure is defined by the member's state rather than by votes (Appendix D.7). Cross-pressured members' votes are fitted less well by DW-NOMINATE as well; holding that fit constant, the abortion deficit remains in both models, although part of the models' difficulty is shared with DW-NOMINATE (Appendix D.8).

**On a nine-point scale.** We also asked each vote on a scale from 1 (certainly NAY) to 9 (certainly YEA), in both directions, and predicted YEA when the expected answer lay above the midpoint (Appendix D.10, Table D1). The directions hold in both models. Cross-pressured members' abortion votes are predicted less accurately (−0.079 [−0.109, −0.050] in Qwen, −0.036 [−0.068, −0.005] in Llama), and their economic votes are not (0.032 and 0.006). The size of the gap depends on the format. Compared with the two-answer format on the same prompt text (YEA described first), the scale gap minus the two-answer gap is −0.082 [−0.120, −0.044] in Qwen and 0.073 [0.020, 0.126] in Llama: on the scale the accuracy deficit of cross-pressured members is larger in Qwen and smaller in Llama. On that prompt, Qwen's two-answer gap is close to zero (0.003 [−0.023, 0.029]); its gap appears when the two answer orders are averaged and on the scale (Appendix D.3, D.10). The split by party does not hold. On the scale, Qwen's gap comes from Democrats (−0.180 [−0.274, −0.086]), and Llama's gap among Republicans is −0.094 [−0.191, 0.003]. Section 7 uses the same scale to measure how uncertain the models are.

**All in all.** Measured by the votes the models predict, cross-pressured members are again mispredicted, on the issue on which the map misplaces them. The models mispredict cross-pressured members on abortion, and they
predict these members' economic votes as well as anyone's. Figure 4 and Table D1 collect the estimates.

# 7. The Models Are Less Certain about Cross-Pressured Members, but Their Doubt Gives No Warning

Studies of voting link cross-pressure to ambivalence and less certainty in political judgments (Section 2.2). This section asks whether the models' own probabilities carry that sign when they predict cross-pressured members' votes, and whether that doubt warns of the predictions they get wrong. The second question matters to anyone who uses the models: if their doubt marked their errors, the mispredicted votes of Section 6 could be caught. We measure uncertainty as the entropy of the model's next-token probabilities over the answers (Appendix E). It is zero when the model puts all its probability on one answer and largest when it spreads its probability evenly. We divide it by that maximum, so it runs from 0 to 1 in both formats of Section 6, the two answers YEA or NAY and the nine-point scale. As in Section 6, we compare cross-pressured with aligned members of the same party voting on the same roll call.

**Slightly more uncertain on the scale.** Answering on the scale, both models are more uncertain about cross-pressured members' abortion votes than about aligned members' votes: by 0.011 [0.005, 0.016] in Qwen and 0.044 [0.032, 0.056] in Llama (Figure 5a). The differences are small next to the range from 0 to 1.

**With YEA or NAY, only in Llama.** With the two answers, Llama is more uncertain about cross-pressured members by 0.032 [0.024, 0.039]. In Qwen the difference, 0.002 [−0.003, 0.006], cannot be told apart from zero. Qwen's two-answer predictions are also unstable: the YEA shares it gives in the two answer orders correlate at only 0.195 on abortion (Appendix D.3). Gun-control votes are in Appendix E.2.

![Figure 5](figures/body/fig5_uncertainty.png)

**Figure 5. Both models are slightly more uncertain about cross-pressured members' votes when they answer on a scale, and more uncertain about these members in every format when asked about the member directly.** Each point is the difference in entropy between cross-pressured and aligned members, with a 95% interval: (a) when the model predicts a member's roll-call vote, among members of the same party voting on the same roll call; (b) when the model answers policy questions as a named member, among members of the same party, Congress and chamber. Entropy is shown as a share of its maximum, so the two-answer formats (YEA or NAY; yes or no) and the scales (1 to 9) share one axis. Abortion; guns are in Appendix E.2. Definitions in Appendix E.

**The same when asked about the member.** The pattern is not tied to the vote task. When the model speaks as a named member and answers policy questions, both models are more uncertain about cross-pressured members in either format (Figure 5b). On abortion, the difference is 0.010 [0.005, 0.016] in Qwen and 0.056 [0.047, 0.064] in Llama with yes or no, and 0.014 [0.009, 0.020] and 0.055 [0.047, 0.064] on the nine-point scale.

**The doubt does not flag the errors.** The uncertainty also does not tell a user which predictions to doubt. With YEA or NAY, for aligned members, Llama's entropy separates its wrong abortion predictions from its right ones: if one wrong and one right prediction are drawn at random, the wrong one has the higher entropy with probability 0.739. For cross-pressured members, neither model's entropy separates them: the probability is 0.472 in Llama and 0.508 in Qwen, close to a coin flip (Qwen's entropy does not separate them for aligned members either; Appendix E.4). The scale answers tell the same story: Llama's scale entropy separates its wrong scale predictions from its right ones with probability 0.679 for aligned members and 0.470 for cross-pressured members, and Qwen's with 0.508 and 0.483. For cross-pressured members, the votes the models get wrong come with no warning from their confidence.

**What this does not show.** The comparison is correlational: it shows that the models' probabilities treat these members as harder, not why. The entropy measures the models' uncertainty about a member, not the member's own ambivalence.

**All in all.** The models' probabilities carry the sign that studies of voting attach to cross-pressure: the models are slightly less certain about these members, in both models on the scale and when asked about the member, and in Llama with YEA or NAY. But the doubt does not show which of their predictions are wrong: for cross-pressured members it separates wrong from right predictions about as well as a coin flip, in either model.

# 8. Discussion and Conclusion

This paper asked whether language models that speak as members of Congress place them where the roll-call record puts them, over
time and member by member. Two open models, read from their activations, place most aligned members where their votes put them, but
they flatten the political past. Over time, they draw the early postwar parties closer together than the record does and portray an
economic divergence that grows more and, in their coordinates, comes mostly from Democrats. Across members, they misplace most
cross-pressured members. On their internal map they move most of the misplaced ones to the aligned position on their economic side, as if
the past had the constraint of the present. The models also follow cross-pressured profiles less faithfully when the positions are
stated in the prompt, and they predict these members' abortion votes less accurately. They are slightly less certain about these
members on the scale and when asked about the member, as studies of cross-pressure would lead one to expect, but their uncertainty does not point to the votes they get wrong. In short, the models misplace the members whose positions
were least constrained.

Why the models keep the economic side cannot be settled here. For most cross-pressured members, the aligned quadrant on their economic side is also their party's, and among misplaced members for whom the two differ, the models favor neither (Appendix F.1). One pattern is consistent with these placements. In the postwar Congress, most economic votes tend to line up on the first dimension of roll-call voting (Poole & Rosenthal, 1991). Inside the models, social positions are encoded but carry less weight than economic ones when members of the same party are placed, in all four model-party comparisons, although for Qwen's Republicans the social coefficient is small (Appendix F.1). Cross-pressured people may organize their beliefs by
the dominant left–right logic, only more loosely (Boutyline & Vaisey, 2017), and a model that has learned that logic would place such
members in an aligned quadrant. Citizens with these combinations did not resolve them toward the economic side. From 1990, voters who
held them were more likely to identify with the Republican Party, whichever dimension they were conservative on (Baldassarri &
Goldberg, 2014). The models' placements instead follow the economic side, whichever direction that is.

These members are central to the history of polarization. In the roll-call record, the decline of members outside their party's
mainstream, through replacement and conversion, was part of how the parties polarized (Fleisher & Bond, 2004; Thomsen, 2014), and the
replacement of moderate southern Democrats by Republicans was one source of the divergence (McCarty et al., 2006). The two findings of this paper are distinct, but they bear on the same history: the models misdraw how the parties polarized, and they misplace the kind of members whose decline was part of it.
Eagleton, Packwood and Snowe each voted against their party on abortion, the issue on which the models
misplace such members, and members whose states leaned toward the other party are also predicted less accurately on abortion, though not clearly in the Senate alone (Appendix D.7). Cross-pressured members also spoke less partisanly than other members (Appendix F.2), and cooperation across party lines
in the House now rests on very few members (Andris et al., 2015). Citizens who hold the same combinations remain common, about two in
five respondents in one long survey series (Baldassarri & Goldberg, 2014), and a simulated Congress that misplaces such members
cannot show how these combinations were once voiced in roll calls.

The checks most often used do not detect this misplacement. A simulation can agree with the aggregate ordering of members and still
misplace this group, and the models' own uncertainty, though slightly higher for this group, gives no warning of the votes they get wrong about it (Section 7). Researchers and
practitioners who use language models to stand in for political actors therefore should not rely on aggregate fit or on model confidence alone. The sizes reported here come from two open models of seven and eight billion parameters and may differ for larger models and for other wordings of the prompts; the test itself, checking a simulation against members' own records, applies to any model. Before simulations are used to study political decisions or to inform them, they need to be tested against members'
own records and, in particular, against the members a single dimension cannot describe (Kozlowski & Evans, 2025; Wang et al., 2025).

The study has three limits. It examines two open models; it reads the history in the models' own coordinates; and it compares that
history with DW-NOMINATE, which is itself one measurement of the past (Section 2.1). Within these limits, the results have one
implication for each field. For research that simulates political actors, agreement with an aggregate benchmark can hide both a
different history and the members who did not fit it. For the study of Congress, these simulations do not reproduce, in their own coordinates, the Republican-led asymmetry of polarization, and they place cross-pressured members far less faithfully than aligned ones; recording those members requires a second dimension.

# References

Adams, G. D. (1997). Abortion: Evidence of an issue evolution. *American Journal of Political Science, 41*(3), 718–737. https://doi.org/10.2307/2111673

Aldrich, J. H., Montgomery, J. M., & Sparks, D. B. (2014). Polarization and ideology: Partisan sources of low dimensionality in scaled roll call analyses. *Political Analysis, 22*(4), 435–456. https://doi.org/10.1093/pan/mpt048

Andris, C., Lee, D., Hamilton, M. J., Martino, M., Gunning, C. E., & Selden, J. A. (2015). The rise of partisanship and super-cooperators in the U.S. House of Representatives. *PLOS ONE, 10*(4), e0123507. https://doi.org/10.1371/journal.pone.0123507

Argyle, L. P., Busby, E. C., Fulda, N., Gubler, J. R., Rytting, C., & Wingate, D. (2023). Out of one, many: Using language models to simulate human samples. *Political Analysis, 31*(3), 337–351. https://doi.org/10.1017/pan.2023.2

Baldassarri, D., & Gelman, A. (2008). Partisans without constraint: Political polarization and trends in American public opinion. *American Journal of Sociology, 114*(2), 408–446. https://doi.org/10.1086/590649

Baldassarri, D., & Goldberg, A. (2014). Neither ideologues nor agnostics: Alternative voters' belief system in an age of partisan politics. *American Journal of Sociology, 120*(1), 45–95. https://doi.org/10.1086/676042

Bisbee, J., Clinton, J. D., Dorff, C., Kenkel, B., & Larson, J. M. (2024). Synthetic replacements for human survey data? The perils of large language models. *Political Analysis, 32*(4), 401–416. https://doi.org/10.1017/pan.2024.5

Boutyline, A., & Vaisey, S. (2017). Belief network analysis: A relational approach to understanding the structure of attitudes. *American Journal of Sociology, 122*(5), 1371–1447. https://doi.org/10.1086/691274

Caughey, D., & Schickler, E. (2016). Substance and change in congressional ideology: NOMINATE and its alternatives. *Studies in American Political Development, 30*(2), 128–146. https://doi.org/10.1017/S0898588X16000092

Chen, R., Arditi, A., Sleight, H., Evans, O., & Lindsey, J. (2025). *Persona vectors: Monitoring and controlling character traits in language models* (arXiv:2507.21509v3). arXiv. https://doi.org/10.48550/arXiv.2507.21509

116 Cong. Rec. 12672–12673 (1970) (introduction of the National Abortion Act, S. 3746, by Sen. Packwood).

129 Cong. Rec. 17346–17347 (1983) (statement of Sen. Eagleton on S.J. Res. 3).

129 Cong. Rec. 17575 (1983) (statement of Sen. Hatch quoting S.J. Res. 3).

Dominguez-Olmedo, R., Hardt, M., & Mendler-Dünner, C. (2024). Questioning the survey responses of large language models. In *Advances in Neural Information Processing Systems 37* (pp. 45850–45878). Curran Associates. https://doi.org/10.52202/079017-1458

Feldman, S., & Johnston, C. (2014). Understanding the determinants of political ideology: Implications of structural complexity. *Political Psychology, 35*(3), 337–358. https://doi.org/10.1111/pops.12055

Fleisher, R., & Bond, J. R. (2004). The shrinking middle in the US Congress. *British Journal of Political Science, 34*(3), 429–451. https://doi.org/10.1017/S0007123404000122

Fowler, A., Hill, S. J., Lewis, J. B., Tausanovitch, C., Vavreck, L., & Warshaw, C. (2023). Moderates. *American Political Science Review, 117*(2), 643–660. https://doi.org/10.1017/S0003055422000818

Gamm, G., Phillips, J. H., Carr, M., & Auslen, M. (2024). The culture war and partisan polarization: State political parties, 1960–2018. *Studies in American Political Development, 38*(2), 117–137. https://doi.org/10.1017/S0898588X2400004X

Gurnee, W., & Tegmark, M. (2024). *Language models represent space and time* (arXiv:2310.02207v3). arXiv. https://doi.org/10.48550/arXiv.2310.02207

Hare, C. (2022). Constrained citizens? Ideological structure and conflict extension in the US electorate, 1980–2016. *British Journal of Political Science, 52*(4), 1602–1621. https://doi.org/10.1017/S000712342100051X

Hu, T., & Collier, N. (2024). Quantifying the persona effect in LLM simulations. In *Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)* (pp. 10289–10307). Association for Computational Linguistics. https://doi.org/10.18653/v1/2024.acl-long.554

Jones, B. D., Baumgartner, F. R., Theriault, S. M., Epp, D. A., Khandekar, S., & Little, D. (2025). *Policy Agendas Project: Codebook* [Codebook]. https://www.comparativeagendas.net/project/us/datasets

Kadavath, S., Conerly, T., Askell, A., Henighan, T., Drain, D., Perez, E., Schiefer, N., Hatfield-Dodds, Z., DasSarma, N., Tran-Johnson, E., Johnston, S., El-Showk, S., Jones, A., Elhage, N., Hume, T., Chen, A., Bai, Y., Bowman, S., Fort, S., … Kaplan, J. (2022). *Language models (mostly) know what they know* (arXiv:2207.05221v4). arXiv. https://doi.org/10.48550/arXiv.2207.05221

Kim, J., Evans, J., & Schein, A. (2025). Linear representations of political perspective emerge in large language models. In *Proceedings of the Thirteenth International Conference on Learning Representations (ICLR 2025)*. https://openreview.net/forum?id=rwqShzb9li

Kim, J., & Lee, B. (2026). *AI-augmented surveys: Leveraging large language models and surveys for opinion prediction* (arXiv:2305.09620v4). arXiv. https://doi.org/10.48550/arXiv.2305.09620

Kozlowski, A. C., & Evans, J. (2025). Simulating subjects: The promise and peril of artificial intelligence stand-ins for social agents and interactions. *Sociological Methods & Research, 54*(3), 1017–1073. https://doi.org/10.1177/00491241251337316

Kreutner, M., Lutz, M., & Strohmaier, M. (2026). Persona-driven simulation of voting behavior in the European Parliament with large language models. In *Findings of the Association for Computational Linguistics: EACL 2026* (pp. 490–511). Association for Computational Linguistics. https://doi.org/10.18653/v1/2026.findings-eacl.25

Layman, G. C., & Carsey, T. M. (2002). Party polarization and "conflict extension" in the American electorate. *American Journal of Political Science, 46*(4), 786–802. https://doi.org/10.2307/3088434

Lewis, J. B., Poole, K., Rosenthal, H., Boche, A., Rudkin, A., & Sonnet, L. (2026). *Voteview: Congressional roll-call votes database* [Data set]. https://voteview.com/

Li, H., Gong, R., & Jiang, H. (2025). Political Actor Agent: Simulating legislative system for roll call votes prediction with large language models. *Proceedings of the AAAI Conference on Artificial Intelligence, 39*(1), 388–396. https://doi.org/10.1609/aaai.v39i1.32017

Llama Team, AI @ Meta. (2024). *The Llama 3 herd of models* (arXiv:2407.21783v3). arXiv. https://doi.org/10.48550/arXiv.2407.21783

Malone, J. (1983, June 27). For senators, no way to duck decision on abortion. *The Christian Science Monitor*. https://www.csmonitor.com/1983/0627/062746.html

McCarty, N., Poole, K. T., & Rosenthal, H. (2006). *Polarized America: The dance of ideology and unequal riches*. MIT Press.

MIT Election Data and Science Lab. (2017). *U.S. President 1976–2024* [Data set]. Harvard Dataverse. https://doi.org/10.7910/DVN/42MVDX

Moskowitz, D. J., Rogowski, J. C., & Snyder, J. M., Jr. (2024). Parsing party polarization in Congress. *Quarterly Journal of Political Science, 19*(4), 357–385. https://doi.org/10.1561/100.00022039

Mutz, D. C. (2002). The consequences of cross-cutting networks for political participation. *American Journal of Political Science, 46*(4), 838–855. https://doi.org/10.2307/3088437

Nadeem, A., Dras, M., & Naseem, U. (2025). Steering towards fairness: Mitigating political bias in LLMs. In *Proceedings of the 8th Workshop on Challenges and Applications of Automated Extraction of Socio-political Events from Texts (CASE 2025)* (pp. 52–61). INCOMA Ltd. https://doi.org/10.26615/978-954-452-099-1-006

Nokken, T. P., & Poole, K. T. (2004). Congressional party defection in American history. *Legislative Studies Quarterly, 29*(4), 545–568. https://doi.org/10.3162/036298004X201294

Poole, K. T., & Rosenthal, H. (1991). Patterns of congressional voting. *American Journal of Political Science, 35*(1), 228–278. https://doi.org/10.2307/2111445

Qwen Team. (2025). *Qwen2.5 technical report* (arXiv:2412.15115v2). arXiv. https://doi.org/10.48550/arXiv.2412.15115

Rennard, V., & Xypolopoulos, C. (2026). *Large language models simulate intersectional synthetic identities with a budget of one to two dimensions* (arXiv:2608.23005v1). arXiv. https://doi.org/10.48550/arXiv.2608.23005

Santurkar, S., Durmus, E., Ladhak, F., Lee, C., Liang, P., & Hashimoto, T. (2023). Whose opinions do language models reflect? In *Proceedings of the 40th International Conference on Machine Learning* (Vol. 202, pp. 29971–30004). PMLR.

Theriault, S. M. (2008). *Party polarization in Congress*. Cambridge University Press. https://doi.org/10.1017/CBO9780511790652

Thomsen, D. M. (2014). Ideological moderates won't run: How party fit matters for partisan polarization in Congress. *The Journal of Politics, 76*(3), 786–797. https://doi.org/10.1017/S0022381614000243

Treier, S., & Hillygus, D. S. (2009). The nature of political ideology in the contemporary electorate. *Public Opinion Quarterly, 73*(4), 679–703. https://doi.org/10.1093/poq/nfp067

von der Heyde, L., Haensch, A.-C., & Wenz, A. (2026). Vox populi, vox AI? Using large language models to estimate German vote choice. *Social Science Computer Review, 44*(3), 549–571. https://doi.org/10.1177/08944393251337014

Wang, A., Morgenstern, J., & Dickerson, J. P. (2025). Large language models that replace human participants can harmfully misportray and flatten identity groups. *Nature Machine Intelligence, 7*(3), 400–411. https://doi.org/10.1038/s42256-025-00986-z

Willamette University Archives and Special Collections. (2017). *Guide to the Robert W. "Bob" Packwood papers, 1957–2018* (WUA104). https://willamette.libraryhost.com/repositories/2/resources/137

Wu, P. Y., Nagler, J., Tucker, J. A., & Messing, S. (2023). *Large language models can be used to estimate the latent positions of politicians* (arXiv:2303.12057v4). arXiv. https://doi.org/10.48550/arXiv.2303.12057

Zhang, T. (2025). Probing political ideology in large language models: How latent political representations generalize across tasks. In *Findings of the Association for Computational Linguistics: EMNLP 2025* (pp. 23349–23360). Association for Computational Linguistics. https://doi.org/10.18653/v1/2025.findings-emnlp.1267
