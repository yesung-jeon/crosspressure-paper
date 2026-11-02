## Amendment A5 (2026-10-20): model competence condition, and a Qwen sample test before any full rerun

**Decisions (2026-10-20).** Seal a competence condition before more model output is read; stop the full Qwen v2 chain (economic
YEA-first stopped at 11 of 25 parts; no NAY-first output existed) and first run a sample test of Qwen in both orders.

**Competence condition** (`estimate_votes.competence`). For each model and issue, on order-averaged predictions:
(a) aligned members' accuracy above 0.5, with the 95% roll-call bootstrap interval (2,000 draws, seeded) excluding 0.5; and
(b) the model's Democrat-minus-Republican gap in YEA share, across roll calls, correlates positively with the actual gap, 95% roll-call
bootstrap interval excluding 0.
A model passing both is competent and its cross-pressure comparison (§6.1) is interpreted. A model failing either is reported as not
performing the task: its §6.1 coefficient is still reported, but not read as evidence about cross-pressured members.
Disclosure: the Qwen diagnostic sample (2,000 votes, order-averaged) had already been seen when this condition was written (aligned
accuracy 0.578; party-gap correlation 0.40). No Llama or OLMo vote-prediction output beyond the 20-prompt smoke test had been seen.
Known-answer test: a party-majority predictor passes, a noise predictor fails.

**Sample test.** The sealed 25% roll-call sample (94 roll calls, 25,972 votes; abortion 13,615, economic 12,357), in both orders.
