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
rerun gives identical output files; the authors confirmed this with a complete rerun of the full path from a fresh copy of the package.
On other hardware, the last digits of some model outputs can differ, and the validation script reports which files differ and how much
the reported values change.

**Steps that are not rerun.** Three steps called external language models: the labelling of gun roll calls (Appendix A.3), and the
writing and checking of roll-call descriptions (Appendix D.1). Their scripts ship with the package, and their outputs ship as fixed
inputs.

**Documentation.** Each analysis folder has a short README that says what it computes and which section or appendix uses it.

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
