# Adjudication of the GPT-4.1-mini description check (2026-10-20)

Checker: `code/v2_verify.py`, gpt-4.1-mini-2025-04-14, temperature 0. Final run: 482 of 524 pass (`summary.json`). Adjudicated by Claude
(same session that directed the writers, so this is not independent); the author spot-checked 20 seeded items and marked all OK.
A row that failed passes only by the written adjudication below (global rule: REVIEW NEEDED passes only after adjudication).

## Real errors found by the checker: 7, fixed in `code/overrides.json` (each with its reason)
94|Senate|595 (bill subject taken from an amendment; now insufficient), 95|House|184 (amendment content added), 96|Senate|308 ("allowing"
vs the source's "restricting"), 96|House|270 ("funding" added), 111|Senate|26 and 117|Senate|350 (regulation and source wording now
quoted; "diagnosed" removed), 95|Senate|337 (NAY claimed an effect the source does not state).
After the fixes, 94|Senate|595, 95|House|184, 96|Senate|308 and 95|Senate|337 pass.

## Remaining flags on sufficient rows: 35, none accepted as errors
- **Quoted official titles or statutory terms ("neutral"), 21:** 109|House|1194, 110|Senate|302, 111|Senate|26, 112|House|1482,
  113|House|248, 114|House|220, 117|Senate|350, 113|House|250, 115|House|548, 116|Senate|485, 110|Senate|523, 114|House|37,
  114|House|222, 115|House|545, 113|House|247, 114|House|38, 115|House|546, 96|House|270 (the checker quotes "anti-abortion
  language" from the source; the written text does not contain it), and 98|House|740, 108|Senate|522, 117|Senate|348 (the writer
  replaced "unborn children" with "fetus" as WRITER_SPEC rule 4 requires; the checker calls either choice non-neutral).
  Policy: a bill's official short title and a regulation's own term are facts about the measure and stay, in quotation marks.
- **"no_outcome" false positives, 7:** 100|House|599, 100|Senate|80, 108|House|1210, 96|Senate|452, 104|House|1042, 114|House|44
  (the checker reads "passage" or "reject" as an outcome, or faults the text for not repeating the source's outcome), and 104|House|307.
- **Context used to name the bill's subject, allowed by WRITER_SPEC rule 1, 4:** 95|Senate|1036, 96|House|630, 95|House|1044,
  96|House|885 (the subject comes from same_bill_context, e.g. "the bill extending the antirecession assistance program").
- **Checker misread the source, 3:** 104|House|307 (NAY keeps the bill's provisions, which is what rejecting the amendment does),
  105|House|1015 (YEA/NAY judged by the recorded outcome), 105|Senate|70 (the substitute's content is in vote_desc).
- **Voteview record with a misattached header, 1:** 104|House|372 (dtl_desc begins with the H.R. 2491 reconciliation header but the
  roll call's bill_number and the amendment text are H.R. 1530, defense authorization, overseas medical facilities; writer followed
  bill_number and the amendment text).

## Insufficient rows that also failed: 7
Excluded from the main analysis by the author's decision (2026-10-20), so not adjudicated further.

## Final counts
524 roll calls; 48 insufficient (main analysis excludes them); main analysis after exclusion: computed in the protocol stage.
