# Study N PROTOCOL: named-member answer entropy, with the paper's map re-projected and linked

2026-10-22. Author decisions: "새로 돌리자 … 기존결과 재현하는 것과 동시에, 교차된 의원들이 엔트로피가 더 높은지", "세 모델 다 해 …
rhee와 kim에 근거해서 qwen먼저", "연결 분석도 넣어서 진행해", "응 진행해 qwen부터 메모리 관리 제발 잘하고". Plan: `PLAN.md` v0.2,
`PLAN_REVIEW.md` (R1-R11). Written and sealed (`PROTOCOL_SEAL.json`) before any GPU output of this study exists. Nothing here changes
after results are seen; any change is a dated amendment that says what had been seen. Same-agent design; not independent validation.

## 1. Data and rows
- Rows: the paper's vote-vs-map rows (10,444 member-Congress rows: 93rd Congress on, Democrats and Republicans, both roll-call scales),
  built by `code/n_common.analysis_rows()`, which reproduces the sealed `vote_vs_map.json` confusion exactly for all three models
  (`out/n0_checks.json`, gate R1b passed 2026-10-22 before any GPU run).
- vote_q: the vote quadrant (median splits of the economic and abortion scales within Congress x chamber); vote_cp = 1 if EL-ST or ER-SP.
- Persona: `dc.kim_persona(name, chamber, state, year)`, the map's persona sentence (Kim step 3, copied verbatim), as the system message.

## 2. Runs (models in this order: Qwen, Llama, OLMo; all three are run whatever Qwen shows)
- [A] `n1_map.py`: Kim's `03_project_legislators.py` unchanged, sealed `vectors.pt` and layer, `--batch 64`, all 21,288 rows ->
  `out/mapout/<m>/s3/temporal_member_scores.csv`.
- [B] `n2_yesno.py`: each analysis row x the 16 single-axis items of Section 5 x two orders (" Answer with Yes or No." /
  " Answer with No or Yes."); full-softmax P(Yes), P(No) of the first answer token; batch 32, length-sorted; parts of 200 rows.
- Memory: RAM >= 5 GB before loading, >= 2 GB between parts (wait otherwise), GPU cap 0.80, OOM halves the batch, resume by row id,
  coverage check; [A] and [B] run as separate processes one after another; detached; logs are not tailed.

## 3. Gates (all must pass before the analysis reads any [B] value by cross-pressure)
- R1b (passed): quadrant rule reproduces the sealed confusion for all models.
- R2 (`n2_yesno.py --r2`): Section 5 I4 (120 named members, "Yes or No"): per-condition C1a and C2 within 0.02 of the sealed values;
  I4 cross-minus-aligned C1a and C2 within 0.02.
- Smoke (`--smoke`): 40 rows complete, Yes/No single tokens, timing recorded.
- R1 (`n1_compare.py`, after [A]): `s4_quadrant.py` rerun on the new map (STUDYD_OUT = out/mapout) must match the sealed `anchors.json`
  and `vote_vs_map.json` at the verdict level (compare_to_sealed.py path A tolerances): A3 r(x, dim1), A4 r(x, economic), r(y, abortion),
  A6 party gaps within 0.05; A9 recall by vote quadrant within 0.05; aligned recall > cross recall and party gap x > y. Digit-level
  agreement is recorded, not required.
- A failed gate stops the study for that model and is reported to the author; no tolerance is changed after a failure.

## 4. Measures (per row; [B] values with mass P(Yes)+P(No) < 0.5 are format failures, counted and excluded)
- p = P(Yes)/(P(Yes)+P(No)); H(p) binary entropy in bits.
- **H (main)**: mean over the 16 items and both orders of H(p) (order-wise entropies averaged; the entropy of the order-averaged
  probability is a sensitivity only, because position bias makes it near 1 when the two orders disagree).
- H_yn: "Yes or No" order only (Section 5 C1a definition). H_econ, H_soc: economic or social items only.
- C_vote: mean probability on the answer that the member's vote quadrant wants (`want_yes`, Section 5 C2 definition, both orders).
- C_map: the same with the new map quadrant as the profile.
- Map measures from [A] (new map; x = -econ_orth, y = -social_orth as s4): map_q (median splits within Congress x chamber);
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
- Secondary: C_vote ~ vote_cp (Section 5 H3 analogue, minimum -0.05).
- Grid (all reported): outcome {H, H_yn, H_econ, H_soc, entropy of the order-averaged p} x FE {party x Congress x chamber; Congress x
  chamber + party} x cluster {member; member + Congress two-way} x sample {all; Democrats; Republicans; party recognized (known); I4
  members excluded}; Q2 and Q3 also on the sealed Study D map.
- 2 x 2 table vote_cp x map_crossed: mean H, n (descriptive).

## 6. Decision rule (Q2 and Q3 main cells; competent models only; minimum +-0.05 bits, the Section 5 H1 minimum)
- 95% interval excludes 0 and estimate >= +0.05: "more uncertain"; excludes 0 and <= -0.05: "less uncertain"; 90% interval inside
  [-0.05, +0.05]: "no meaningful difference"; otherwise "undetermined". Holm-adjusted p over model x {Q2, Q3} reported alongside.
- Secondary (C_vote): estimate <= -0.05 with the 95% interval below 0: "less consistent with own votes"; 90% inside +-0.05: no
  meaningful difference; otherwise undetermined.

## 7. Interpretation (fixed now)
- Q2 no difference + Q3 more uncertain: the model hesitates only for members it represents as crossed; vote-defined cross-pressured
  members are mostly represented as aligned (Section 4), so they get confident answers. The original question of the project
  (conflicting internal directions -> entropy) is supported, and the failure sits at the representation stage.
- Q2 and Q3 no difference: conflicting internal directions do not raise output uncertainty either; same direction as the sealed
  steering results (Studies F, G).
- Q2 more uncertain: combination holds for named members.
- Q3 or Q2 less uncertain: reported as such; no reading fixed beyond the table.
- Models that differ are reported separately; no pooling.
- Observational: no claim that the representation causes the uncertainty.

## 8. Already seen (disclosure)
Section 5 I4 per-mode cross-minus-aligned C1a (Qwen +0.018, Llama +0.023, OLMo +0.003; 120 members); W1 uncertainty
(`review/w1_uncertainty_2026-10-22`); CP1 (exploratory null); Study F/G steering readings; the sealed map. Not seen: any Study N value.
Claude's expectation (stated in PLAN): Q2 no meaningful difference; no expectation for Q3.

## 9. Outputs
`out/n0_checks.json`, `out/<m>/{r2_check.json, yesno_smoke/, yesno/, n1_compare.json}`, `out/mapout/`, `analysis/` (Rhee structure:
prepare.py, helpers.R, run.R, tables/, models/, verification.json, ASSESSMENT.md, RELEASE.json, PROTECTED.json).
