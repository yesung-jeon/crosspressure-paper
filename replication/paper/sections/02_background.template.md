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
such combinations.

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

## References (Section 2 only)

Adams, G. D. (1997). Abortion: Evidence of an issue evolution. *American Journal of Political Science, 41*(3), 718–737. https://doi.org/10.2307/2111673

Aldrich, J. H., Montgomery, J. M., & Sparks, D. B. (2014). Polarization and ideology: Partisan sources of low dimensionality in scaled roll call analyses. *Political Analysis, 22*(4), 435–456. https://doi.org/10.1093/pan/mpt048

Andris, C., Lee, D., Hamilton, M. J., Martino, M., Gunning, C. E., & Selden, J. A. (2015). The rise of partisanship and super-cooperators in the U.S. House of Representatives. *PLOS ONE, 10*(4), e0123507. https://doi.org/10.1371/journal.pone.0123507

Argyle, L. P., Busby, E. C., Fulda, N., Gubler, J. R., Rytting, C., & Wingate, D. (2023). Out of one, many: Using language models to simulate human samples. *Political Analysis, 31*(3), 337–351. https://doi.org/10.1017/pan.2023.2

Baldassarri, D., & Gelman, A. (2008). Partisans without constraint: Political polarization and trends in American public opinion. *American Journal of Sociology, 114*(2), 408–446. https://doi.org/10.1086/590649

Baldassarri, D., & Goldberg, A. (2014). Neither ideologues nor agnostics: Alternative voters' belief system in an age of partisan politics. *American Journal of Sociology, 120*(1), 45–95. https://doi.org/10.1086/676042

Bisbee, J., Clinton, J. D., Dorff, C., Kenkel, B., & Larson, J. M. (2024). Synthetic replacements for human survey data? The perils of large language models. *Political Analysis, 32*(4), 401–416. https://doi.org/10.1017/pan.2024.5

Boutyline, A., & Vaisey, S. (2017). Belief network analysis: A relational approach to understanding the structure of attitudes. *American Journal of Sociology, 122*(5), 1371–1447. https://doi.org/10.1086/691274

Caughey, D., & Schickler, E. (2016). Substance and change in congressional ideology: NOMINATE and its alternatives. *Studies in American Political Development, 30*(2), 128–146. https://doi.org/10.1017/S0898588X16000092

Dominguez-Olmedo, R., Hardt, M., & Mendler-Dünner, C. (2024). Questioning the survey responses of large language models. In *Advances in Neural Information Processing Systems 37* (pp. 45850–45878). Curran Associates. https://doi.org/10.52202/079017-1458

Fleisher, R., & Bond, J. R. (2004). The shrinking middle in the US Congress. *British Journal of Political Science, 34*(3), 429–451. https://doi.org/10.1017/S0007123404000122

Fowler, A., Hill, S. J., Lewis, J. B., Tausanovitch, C., Vavreck, L., & Warshaw, C. (2023). Moderates. *American Political Science Review, 117*(2), 643–660. https://doi.org/10.1017/S0003055422000818

Gamm, G., Phillips, J. H., Carr, M., & Auslen, M. (2024). The culture war and partisan polarization: State political parties, 1960–2018. *Studies in American Political Development, 38*(2), 117–137. https://doi.org/10.1017/S0898588X2400004X

Gurnee, W., & Tegmark, M. (2024). *Language models represent space and time* (arXiv:2310.02207v3). arXiv. https://doi.org/10.48550/arXiv.2310.02207

Hare, C. (2022). Constrained citizens? Ideological structure and conflict extension in the US electorate, 1980–2016. *British Journal of Political Science, 52*(4), 1602–1621. https://doi.org/10.1017/S000712342100051X

Hu, T., & Collier, N. (2024). Quantifying the persona effect in LLM simulations. In *Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)* (pp. 10289–10307). Association for Computational Linguistics. https://doi.org/10.18653/v1/2024.acl-long.554

Kadavath, S., Conerly, T., Askell, A., Henighan, T., Drain, D., Perez, E., Schiefer, N., Hatfield-Dodds, Z., DasSarma, N., Tran-Johnson, E., Johnston, S., El-Showk, S., Jones, A., Elhage, N., Hume, T., Chen, A., Bai, Y., Bowman, S., Fort, S., … Kaplan, J. (2022). *Language models (mostly) know what they know* (arXiv:2207.05221v4). arXiv. https://doi.org/10.48550/arXiv.2207.05221

Kim, J., Evans, J., & Schein, A. (2025). Linear representations of political perspective emerge in large language models. In *Proceedings of the Thirteenth International Conference on Learning Representations (ICLR 2025)*. https://openreview.net/forum?id=rwqShzb9li

Kim, J., & Lee, B. (2026). *AI-augmented surveys: Leveraging large language models and surveys for opinion prediction* (arXiv:2305.09620v4). arXiv. https://doi.org/10.48550/arXiv.2305.09620

Kozlowski, A. C., & Evans, J. (2025). Simulating subjects: The promise and peril of artificial intelligence stand-ins for social agents and interactions. *Sociological Methods & Research, 54*(3), 1017–1073. https://doi.org/10.1177/00491241251337316

Layman, G. C., & Carsey, T. M. (2002). Party polarization and "conflict extension" in the American electorate. *American Journal of Political Science, 46*(4), 786–802. https://doi.org/10.2307/3088434

McCarty, N., Poole, K. T., & Rosenthal, H. (2006). *Polarized America: The dance of ideology and unequal riches*. MIT Press.

Moskowitz, D. J., Rogowski, J. C., & Snyder, J. M., Jr. (2024). Parsing party polarization in Congress. *Quarterly Journal of Political Science, 19*(4), 357–385. https://doi.org/10.1561/100.00022039

Mutz, D. C. (2002). The consequences of cross-cutting networks for political participation. *American Journal of Political Science, 46*(4), 838–855. https://doi.org/10.2307/3088437

Nadeem, A., Dras, M., & Naseem, U. (2025). Steering towards fairness: Mitigating political bias in LLMs. In *Proceedings of the 8th Workshop on Challenges and Applications of Automated Extraction of Socio-political Events from Texts (CASE 2025)* (pp. 52–61). INCOMA Ltd. https://doi.org/10.26615/978-954-452-099-1-006

Poole, K. T., & Rosenthal, H. (1991). Patterns of congressional voting. *American Journal of Political Science, 35*(1), 228–278. https://doi.org/10.2307/2111445

Rennard, V., & Xypolopoulos, C. (2026). *Large language models simulate intersectional synthetic identities with a budget of one to two dimensions* (arXiv:2608.23005v1). arXiv. https://doi.org/10.48550/arXiv.2608.23005

Santurkar, S., Durmus, E., Ladhak, F., Lee, C., Liang, P., & Hashimoto, T. (2023). Whose opinions do language models reflect? In *Proceedings of the 40th International Conference on Machine Learning* (Vol. 202, pp. 29971–30004). PMLR.

Theriault, S. M. (2008). *Party polarization in Congress*. Cambridge University Press. https://doi.org/10.1017/CBO9780511790652

Thomsen, D. M. (2014). Ideological moderates won't run: How party fit matters for partisan polarization in Congress. *The Journal of Politics, 76*(3), 786–797. https://doi.org/10.1017/S0022381614000243

Treier, S., & Hillygus, D. S. (2009). The nature of political ideology in the contemporary electorate. *Public Opinion Quarterly, 73*(4), 679–703. https://doi.org/10.1093/poq/nfp067

von der Heyde, L., Haensch, A.-C., & Wenz, A. (2026). Vox populi, vox AI? Using large language models to estimate German vote choice. *Social Science Computer Review, 44*(3), 549–571. https://doi.org/10.1177/08944393251337014

Wang, A., Morgenstern, J., & Dickerson, J. P. (2025). Large language models that replace human participants can harmfully misportray and flatten identity groups. *Nature Machine Intelligence, 7*(3), 400–411. https://doi.org/10.1038/s42256-025-00986-z

Zhang, T. (2025). Probing political ideology in large language models: How latent political representations generalize across tasks. In *Findings of the Association for Computational Linguistics: EMNLP 2025* (pp. 23349–23360). Association for Computational Linguistics. https://doi.org/10.18653/v1/2025.findings-emnlp.1267
