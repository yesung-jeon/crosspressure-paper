# 8. Discussion and Conclusion

This paper asked whether language models that speak as members of Congress place them where the roll-call record puts them, over
time and member by member. Two open models, read from their activations, place most aligned members where their votes put them, but
they flatten the political past. Over time, they draw the early postwar parties closer together than the record does and portray an
economic divergence that grows more and, in their coordinates, comes mostly from Democrats. Across members, they misplace most of
those who crossed party lines. On their internal map they move these members to the aligned position on their economic side, as if
the past had the constraint of the present. The models also follow cross-pressured profiles less faithfully when the positions are
stated in the prompt, and they predict these members' abortion votes less accurately. They are slightly more uncertain about these
members, but their uncertainty does not point to the votes they get wrong. In short, the models misplace the members whose positions
were least constrained.

Why the models keep the economic side cannot be settled here. For most cross-pressured members, the aligned quadrant on their economic side is also their party's, and among misplaced members for whom the two differ, the models favor neither (Appendix F.1). One pattern is consistent with these placements. In the postwar Congress, most economic votes tend to line up on the first dimension of roll-call voting (Poole & Rosenthal, 1991). Inside the models, social positions are encoded but carry less weight than economic ones when members of the same party are placed, in all four model-party comparisons, though least for Qwen's Republicans (Appendix F.1). Cross-pressured people may organize their beliefs by
the dominant left–right logic, only more loosely (Boutyline & Vaisey, 2017), and a model that has learned that logic would place such
members in an aligned quadrant. Citizens with these combinations did not resolve them toward the economic side. From 1990, voters who
held them were more likely to identify with the Republican Party, whichever dimension they were conservative on (Baldassarri &
Goldberg, 2014). The models' placements instead follow the economic side, whichever direction that is.

These members are central to the history of polarization. In the roll-call record, the decline of members outside their party's
mainstream, through replacement and conversion, was part of how the parties polarized (Fleisher & Bond, 2004; Thomsen, 2014), and the
replacement of moderate southern Democrats by Republicans was one source of the divergence (McCarty et al., 2006). The two findings of this paper therefore concern the same group of members and the same decades: the models misplace these members and misdraw the history in
which they disappeared. Eagleton, Packwood and Snowe each voted against their party on abortion, the issue on which the models
misplace such members, and members whose states leaned toward the other party are also predicted less accurately on abortion, though not clearly in the Senate alone (Section 6). Cross-pressured members also spoke less partisanly than other members (Appendix F.2), and cooperation across party lines
in the House now rests on very few members (Andris et al., 2015). Citizens who hold the same combinations remain common, about two in
five respondents in one long survey series (Baldassarri & Goldberg, 2014), and a simulated Congress that misplaces such members
cannot show how these combinations were once voiced in roll calls.

The checks most often used do not detect this misplacement. A simulation can agree with the aggregate ordering of members and still
misplace this group, and the models' own uncertainty marks their errors about it poorly (Section 7). Researchers and
practitioners who use language models to stand in for political actors therefore should not rely on aggregate fit or on model confidence alone. The sizes reported here come from two open models of seven and eight billion parameters and may differ for larger models; the test itself, checking a simulation against members' own records, applies to any model. Before simulations are used to study political decisions or to inform them, they need to be tested against members'
own records and, in particular, against the members a single dimension cannot describe (Kozlowski & Evans, 2025; Wang et al., 2025).

The study has three limits. It examines two open models; it reads the history in the models' own coordinates; and it compares that
history with DW-NOMINATE, which is itself one measurement of the past (Section 2.1). Within these limits, the results have one
implication for each field. For research that simulates political actors, agreement with an aggregate benchmark can hide both a
different history and the members who did not fit it. For the study of Congress, these simulations do not reproduce, in their own coordinates, the Republican-led asymmetry of polarization, and they place cross-pressured members far less faithfully than aligned ones; recording those members requires a second dimension.

## References (Section 8 only)

Andris, C., Lee, D., Hamilton, M. J., Martino, M., Gunning, C. E., & Selden, J. A. (2015). The rise of partisanship and super-cooperators in the U.S. House of Representatives. *PLOS ONE, 10*(4), e0123507. https://doi.org/10.1371/journal.pone.0123507

Baldassarri, D., & Goldberg, A. (2014). Neither ideologues nor agnostics: Alternative voters' belief system in an age of partisan politics. *American Journal of Sociology, 120*(1), 45–95. https://doi.org/10.1086/676042

Boutyline, A., & Vaisey, S. (2017). Belief network analysis: A relational approach to understanding the structure of attitudes. *American Journal of Sociology, 122*(5), 1371–1447. https://doi.org/10.1086/691274

Fleisher, R., & Bond, J. R. (2004). The shrinking middle in the US Congress. *British Journal of Political Science, 34*(3), 429–451. https://doi.org/10.1017/S0007123404000122

Kozlowski, A. C., & Evans, J. (2025). Simulating subjects: The promise and peril of artificial intelligence stand-ins for social agents and interactions. *Sociological Methods & Research, 54*(3), 1017–1073. https://doi.org/10.1177/00491241251337316

McCarty, N., Poole, K. T., & Rosenthal, H. (2006). *Polarized America: The dance of ideology and unequal riches*. MIT Press.

Poole, K. T., & Rosenthal, H. (1991). Patterns of congressional voting. *American Journal of Political Science, 35*(1), 228–278. https://doi.org/10.2307/2111445

Thomsen, D. M. (2014). Ideological moderates won't run: How party fit matters for partisan polarization in Congress. *The Journal of Politics, 76*(3), 786–797. https://doi.org/10.1017/S0022381614000243

Wang, A., Morgenstern, J., & Dickerson, J. P. (2025). Large language models that replace human participants can harmfully misportray and flatten identity groups. *Nature Machine Intelligence, 7*(3), 400–411. https://doi.org/10.1038/s42256-025-00986-z
