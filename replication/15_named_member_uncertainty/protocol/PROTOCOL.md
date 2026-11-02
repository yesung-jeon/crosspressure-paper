# Named-member answer entropy, with the paper's map re-projected and linked: protocol

> Note for the replication package: this protocol was written on 2026-10-22, before any GPU output of this analysis existed, for the
> first model run (FP8 weights, three models). The paper reports a rerun in bf16 with Qwen2.5-7B-Instruct and Llama-3.1-8B-Instruct
> under the same specification. The reading rule the paper uses (Appendix E.2) later replaced the minimum effect of 0.05 bits below: a
> difference reads as higher or lower when its 95% interval excludes zero and its Holm-adjusted p is below .05, with no minimum size.
> Internal file references have been removed; the specification is unchanged.

2026-10-22. Written and sealed before any GPU output of this analysis exists. Nothing here changes after results are seen; any change
is a dated amendment that says what had been seen.

## 1. Data and rows
- Rows: the paper's vote-vs-map rows (10,444 member-Congress rows: 93rd Congress on, Democrats and Republicans, both roll-call scales),
  built by `code/n_common.analysis_rows()`, which reproduces the stored vote-by-map confusion exactly for every model (gate R1b).
- vote_q: the vote quadrant (median splits of the economic and abortion scales within Congress x chamber); vote_cp = 1 if EL-ST or ER-SP.
- Persona: the map's persona sentence (name, chamber, state, year), as the system message.

## 2. Runs (models in a fixed order; all models are run whatever the first shows)
- [A] Map re-projection: Junsol Kim's `03_project_legislators.py` unchanged, the stored directions and layer, all 21,288 rows.
- [B] Yes/no scoring: each analysis row x the 16 single-axis items of Table A1 x two orders (" Answer with Yes or No." /
  " Answer with No or Yes."); full-softmax P(Yes), P(No) of the first answer token.
- Memory: RAM checks before loading and between parts, GPU memory cap, resume by row id, coverage check; [A] and [B] run as separate
  processes one after another.

## 3. Gates (all must pass before the analysis reads any [B] value by cross-pressure)
- R1b: quadrant rule reproduces the stored confusion for all models.
- R2: stated-profile check (120 named members, "Yes or No"): per-condition consistency and choice entropy within 0.02 of the stored
  values; cross-minus-aligned differences within 0.02.
- Smoke: 40 rows complete, Yes/No single tokens, timing recorded.
- R1 (after [A]): the placement analysis rerun on the re-projected map must match the stored anchors and recall at the verdict level:
  r(x, dim1), r(x, economic), r(y, abortion) and party gaps within 0.05; recall by vote quadrant within 0.05; aligned recall > cross
  recall and party gap x > y. Digit-level agreement is recorded, not required.
- A failed gate stops the analysis for that model and is reported; no tolerance is changed after a failure.

## 4. Measures (per row; [B] values with mass P(Yes)+P(No) < 0.5 are format failures, counted and excluded)
- p = P(Yes)/(P(Yes)+P(No)); H(p) binary entropy in bits.
- **H (main)**: mean over the 16 items and both orders of H(p) (order-wise entropies averaged; the entropy of the order-averaged
  probability is a sensitivity only, because position bias makes it near 1 when the two orders disagree).
- H_yn: "Yes or No" order only. H_econ, H_soc: economic or social items only.
- C_vote: mean probability on the answer that the member's vote quadrant wants (both orders).
- C_map: the same with the new map quadrant as the profile.
- Map measures from [A] (x = -econ_orth, y = -social_orth): map_q (median splits within Congress x chamber);
  map_crossed = map_q in {EL-ST, ER-SP}; zx, zy = median-centred coordinates divided by their SD within Congress x chamber;
  depth = min(|zx|, |zy|); conflict = depth x map_crossed.
- Competence (per model; computed on aligned vote-quadrant rows only, before any comparison by cross-pressure):
  (a) mean C_vote above 0.5 with the 95% member-cluster bootstrap interval (2,000 draws, seeded) excluding 0.5; (b) format failures
  below 10% of item-order cells. A model failing either is reported, not interpreted.

## 5. Estimation (R, fixest; every fit's coefficients and variance reconstructed by matrix algebra, stop above 1e-7)
- Main FE: party x Congress x chamber. Main cluster: member (icpsr), CR1. t intervals on G - 1 df.
- Q2: H ~ vote_cp. Q3: H ~ map_crossed. Joint: H ~ vote_cp + map_crossed. Continuous: H ~ conflict + depth; H ~ |zx| + |zy| + zx:zy.
- Q4 (descriptive): among vote_cp rows with map_q != vote_q, mean of C_map - C_vote with a member-cluster bootstrap 95% interval.
- Q5 (descriptive): EL-ST vs aligned and ER-SP vs aligned (indicators for each crossed quadrant), vote-based and map-based.
- Secondary: C_vote ~ vote_cp (minimum -0.05).
- Grid (all reported): outcome {H, H_yn, H_econ, H_soc, entropy of the order-averaged p} x FE {party x Congress x chamber; Congress x
  chamber + party} x cluster {member; member + Congress two-way} x sample {all; Democrats; Republicans; party recognized (known); the
  120 stated-profile members excluded}; Q2 and Q3 also on the stored map.
- 2 x 2 table vote_cp x map_crossed: mean H, n (descriptive).

## 6. Decision rule (Q2 and Q3 main cells; competent models only; minimum +-0.05 bits)
- 95% interval excludes 0 and estimate >= +0.05: "more uncertain"; excludes 0 and <= -0.05: "less uncertain"; 90% interval inside
  [-0.05, +0.05]: "no meaningful difference"; otherwise "undetermined". Holm-adjusted p over model x {Q2, Q3} reported alongside.
- Secondary (C_vote): estimate <= -0.05 with the 95% interval below 0: "less consistent with own votes"; 90% inside +-0.05: no
  meaningful difference; otherwise undetermined.
- Models that differ are reported separately; no pooling. Observational: no claim that the representation causes the uncertainty.

## 7. Already seen (disclosure)
Stated-profile cross-minus-aligned choice entropy for the 120 named members; the vote-uncertainty results; the stored map. Not seen:
any value of this analysis.

## 8. Outputs
`out/n0_checks.json`, `out/<m>/{r2_check.json, yesno_smoke/, yesno/, n1_compare.json}`, `out/mapout/`, `analysis/` (prepare script,
helpers.R, fitting script, tables/, models/, verification files).
