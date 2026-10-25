# 3. Data and Methods

To ask whether a language model places members where their roll-call votes put them, over time and member by member, we need a way to read where the model places a
member, a record to compare it with, and tests that look at cross-pressure from more than one side. This section builds them in that
order.

**Two models.** We study Qwen2.5-7B-Instruct and Llama-3.1-8B-Instruct (Llama Team, 2024; Qwen Team, 2025), hereafter Qwen and Llama.
Our questions concern what happens inside a model, so we use models whose weights are public. We fix the model versions and run all
computations deterministically, so that every result in the paper can be reproduced exactly.

**Economic and social directions.** To place members on two dimensions of conflict, we first need to find those
dimensions inside each model. Following Chen et al. (2025), we prompt each model with pairs of opposing instructions, one pair about
economic policy and one about social policy. The difference between the average activations of the two kinds of answers gives the
model's economic direction and its social direction. We take the directions from the layer at which moving along them most changes
the model's answers: layer {{LAYER_Q}} in Qwen and layer {{LAYER_L}} in Llama. Repeating the whole procedure selects the same layers
(Appendix A.4).

**Placing members: the map.** With the two directions in hand, we place members. For each member in each Congress from 1947 to 2024, a
member-Congress, each model is asked to speak as that member. The prompt gives the member's name, chamber, state and year; as in Kim et al. (2025), it does not give the party. Projecting the model's activation onto the two directions gives the member's economic and social coordinates.
Together, these coordinates form the map that Sections 4 and 5 examine (Appendix A.5).

**The roll-call record and cross-pressure.** A map is informative only if it can be checked against what members did. Because economic
and social ideology are distinct dimensions (Feldman & Johnston, 2014), we measure each member's economic and social positions
separately, from roll calls in Voteview (Lewis et al., 2026). The economic scale uses roll calls on the economic topics of the Policy
Agendas Project (Jones et al., 2025). Social positions are measured on abortion, the social issue whose roll calls span the period and
on which the parties were at first internally divided (Adams, 1997; Layman & Carsey, 2002), and, as a second issue, on gun control (Appendix A.3). Splitting each scale at its median within Congress and chamber places every Democratic and Republican member-Congress with both scales in one of four quadrants.
Cross-pressured members are those whose economic and social scales fall on opposite sides, economically liberal and socially
conservative or the reverse. All others are aligned members. Section 6 adds two definitions that do not depend on the same votes: a
leave-one-out definition, which leaves out the roll call being predicted, and state-based cross-pressure, which holds when the member's state leans toward the other party in presidential elections (MIT Election Data and Science Lab, 2017); for House members, the state stands in for the district.

**Reference scales.** As references, we use the DW-NOMINATE scores that Voteview publishes in one and two dimensions (Lewis et al., 2026), which descend from the NOMINATE scaling of Poole and Rosenthal (1991). We also use Nokken-Poole scores, which estimate each member's position in every
Congress while holding the roll-call parameters fixed (Nokken & Poole, 2004). How well DW-NOMINATE fits a member's votes, the NOMINATE fit, is Voteview's geometric mean probability of those votes.

**Three tests.** A single measurement could mislead, so we examine cross-pressure in three ways. First, following the map Congress by Congress, we compare the party gap on each model's economic direction with the party gap on the first dimension of
DW-NOMINATE, each in standard deviations of its own scale. We then split the change into Democratic and Republican movement, and into
the movement of continuing members and the replacement of members (Section 4). Second, we check whether each member-Congress falls in
the quadrant of its votes, and whether the models follow cross-pressured profiles when the profile's positions are stated in the prompt
instead of a name (Section 5). Third, each model predicts members' votes on abortion, economic and gun-control roll calls from the
member's name, state, chamber and year and a neutral description of what a YEA and a NAY vote would do (Section 6). The descriptions were
drafted by a language model from Voteview's text, screened by fixed rules for outcome and party cues, checked by a model from another
family (GPT-4.1-mini), and spot-checked by the authors (Appendix D.1). Accuracy is compared among members of the same party voting on the
same roll call, with intervals clustered by member and by roll call.

**The models' own uncertainty.** Finally, we ask whether the models register these members as harder (Section 7). We measure
uncertainty as the entropy, in bits, of a model's next-token probabilities over the answer options. Whether uncertainty points to errors
is measured as the probability that, on the same roll call, a wrong prediction has higher entropy than a right one.

**The map tracks roll-call positions.** Before the tests, we check that the map measures what it should. The models' economic
coordinates track the first dimension of DW-NOMINATE ({{R_X_DW1_Q}} in Qwen and {{R_X_DW1_L}} in Llama, the mean of
correlations computed within each Congress) and the economic scale ({{R_X_ECON_Q}} and {{R_X_ECON_L}}, correlated within Congress and
chamber). The party gap is larger on the economic than on the social
direction, and most aligned member-Congresses fall in the quadrant of their own votes (Table 1). The correlations and party gaps use the member-Congresses whose party the model names correctly (Appendix A.5). Because the map tracks roll-call positions for most members, the misplacements reported in the sections that follow are not a general failure of measurement.

{{TABLE1}}

## References (Section 3 only)

Adams, G. D. (1997). Abortion: Evidence of an issue evolution. *American Journal of Political Science, 41*(3), 718–737. https://doi.org/10.2307/2111673

Chen, R., Arditi, A., Sleight, H., Evans, O., & Lindsey, J. (2025). *Persona vectors: Monitoring and controlling character traits in language models* (arXiv:2507.21509v3). arXiv. https://doi.org/10.48550/arXiv.2507.21509

Feldman, S., & Johnston, C. (2014). Understanding the determinants of political ideology: Implications of structural complexity. *Political Psychology, 35*(3), 337–358. https://doi.org/10.1111/pops.12055

Jones, B. D., Baumgartner, F. R., Theriault, S. M., Epp, D. A., Khandekar, S., & Little, D. (2025). *Policy Agendas Project: Codebook* [Codebook]. https://www.comparativeagendas.net/project/us/datasets

Kim, J., Evans, J., & Schein, A. (2025). Linear representations of political perspective emerge in large language models. In *Proceedings of the Thirteenth International Conference on Learning Representations (ICLR 2025)*. https://openreview.net/forum?id=rwqShzb9li

Layman, G. C., & Carsey, T. M. (2002). Party polarization and "conflict extension" in the American electorate. *American Journal of Political Science, 46*(4), 786–802. https://doi.org/10.2307/3088434

Lewis, J. B., Poole, K., Rosenthal, H., Boche, A., Rudkin, A., & Sonnet, L. (2026). *Voteview: Congressional roll-call votes database* [Data set]. https://voteview.com/

Llama Team, AI @ Meta. (2024). *The Llama 3 herd of models* (arXiv:2407.21783v3). arXiv. https://doi.org/10.48550/arXiv.2407.21783

MIT Election Data and Science Lab. (2017). *U.S. President 1976–2024* [Data set]. Harvard Dataverse. https://doi.org/10.7910/DVN/42MVDX

Nokken, T. P., & Poole, K. T. (2004). Congressional party defection in American history. *Legislative Studies Quarterly, 29*(4), 545–568. https://doi.org/10.3162/036298004X201294

Poole, K. T., & Rosenthal, H. (1991). Patterns of congressional voting. *American Journal of Political Science, 35*(1), 228–278. https://doi.org/10.2307/2111445

Qwen Team. (2025). *Qwen2.5 technical report* (arXiv:2412.15115v2). arXiv. https://doi.org/10.48550/arXiv.2412.15115
