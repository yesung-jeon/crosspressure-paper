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
{{RECALL_CROSS_AB_Q}} (Qwen) and {{RECALL_CROSS_AB_L}} (Llama) of cross-pressured member-Congresses (one member in one Congress) in the quadrant of their own
votes, whereas a two-dimensional DW-NOMINATE placement of the same member-Congresses places {{DW2_RECALL_CROSS_AB}}. Most of the members the models misplace are moved into the aligned quadrant that shares their economic position, which for most of them is also their party's. When a cross-pressured profile's positions are stated in the prompt, the models follow it less faithfully. When the models predict the members' votes, they are less accurate on abortion but not on economic votes. As the work on synthetic respondents would lead one to expect, the models flatten differences within each party, and they also flatten the differences between the early parties.

Across tasks, the models are slightly more uncertain about cross-pressured members, most clearly in
Llama, but the added uncertainty is smallest when they predict votes and does not mark the votes they get wrong.

The paper makes two contributions. First, it extends the linear representation of political perspective in language models from one
dimension to two for simulated members of Congress. Earlier work used one dimension (Kim et al., 2025) or separate economic and social directions for the model's own stance (Nadeem et al., 2025), and found that a single direction transfers poorly to simulated votes (Zhang, 2025). We validate every
placement against roll calls and read the representation over time as a reconstructed history. Second, it shows that validation
against an aggregate ordering can hide both a different history of polarization and the members who did not fit that history. Models
used in this way may misdescribe how the parties polarized and hide how varied past Congresses were.

Section 2 reviews the two dimensions and the history of congressional conflict, the members who crossed party lines, and what is
known about language models as simulated political actors. Section 3 describes the data and methods, and Sections 4 to 7 report the history the models reconstruct, the map
and stated profiles, vote prediction, and the models' uncertainty. Section 8 discusses the implications.

## References (introduction only)

Adams, G. D. (1997). Abortion: Evidence of an issue evolution. *American Journal of Political Science, 41*(3), 718–737. https://doi.org/10.2307/2111673

Kim, J., Evans, J., & Schein, A. (2025). Linear representations of political perspective emerge in large language models. In *Proceedings of the Thirteenth International Conference on Learning Representations (ICLR 2025)*. https://openreview.net/forum?id=rwqShzb9li

McCarty, N., Poole, K. T., & Rosenthal, H. (2006). *Polarized America: The dance of ideology and unequal riches*. MIT Press.

Moskowitz, D. J., Rogowski, J. C., & Snyder, J. M., Jr. (2024). Parsing party polarization in Congress. *Quarterly Journal of Political Science, 19*(4), 357–385. https://doi.org/10.1561/100.00022039

Kozlowski, A. C., & Evans, J. (2025). Simulating subjects: The promise and peril of artificial intelligence stand-ins for social agents and interactions. *Sociological Methods & Research, 54*(3), 1017–1073. https://doi.org/10.1177/00491241251337316

Kreutner, M., Lutz, M., & Strohmaier, M. (2026). Persona-driven simulation of voting behavior in the European Parliament with large language models. In *Findings of the Association for Computational Linguistics: EACL 2026* (pp. 490–511). Association for Computational Linguistics. https://doi.org/10.18653/v1/2026.findings-eacl.25

Layman, G. C., & Carsey, T. M. (2002). Party polarization and "conflict extension" in the American electorate. *American Journal of Political Science, 46*(4), 786–802. https://doi.org/10.2307/3088434

Li, H., Gong, R., & Jiang, H. (2025). Political Actor Agent: Simulating legislative system for roll call votes prediction with large language models. *Proceedings of the AAAI Conference on Artificial Intelligence, 39*(1), 388–396. https://doi.org/10.1609/aaai.v39i1.32017

Nadeem, A., Dras, M., & Naseem, U. (2025). Steering towards fairness: Mitigating political bias in LLMs. In *Proceedings of the 8th Workshop on Challenges and Applications of Automated Extraction of Socio-political Events from Texts (CASE 2025)* (pp. 52–61). INCOMA Ltd. https://doi.org/10.26615/978-954-452-099-1-006

Rennard, V., & Xypolopoulos, C. (2026). *Large language models simulate intersectional synthetic identities with a budget of one to two dimensions* (arXiv:2608.23005v1). arXiv. https://doi.org/10.48550/arXiv.2608.23005

Thomsen, D. M. (2014). Ideological moderates won't run: How party fit matters for partisan polarization in Congress. *The Journal of Politics, 76*(3), 786–797. https://doi.org/10.1017/S0022381614000243

Wang, A., Morgenstern, J., & Dickerson, J. P. (2025). Large language models that replace human participants can harmfully misportray and flatten identity groups. *Nature Machine Intelligence, 7*(3), 400–411. https://doi.org/10.1038/s42256-025-00986-z

Wu, P. Y., Nagler, J., Tucker, J. A., & Messing, S. (2023). *Large language models can be used to estimate the latent positions of politicians* (arXiv:2303.12057v4). arXiv. https://doi.org/10.48550/arXiv.2303.12057

Zhang, T. (2025). Probing political ideology in large language models: How latent political representations generalize across tasks. In *Findings of the Association for Computational Linguistics: EMNLP 2025* (pp. 23349–23360). Association for Computational Linguistics. https://doi.org/10.18653/v1/2025.findings-emnlp.1267
