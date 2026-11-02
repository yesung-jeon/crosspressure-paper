# Writer spec: neutral roll-call descriptions (Study V, 2026-10-20)

Purpose. Each description is shown to a language model that answers as a named member of Congress and predicts that member's YEA or
NAY vote. The description must tell the model what the vote is about and what each side means, and nothing about how the vote ended,
who proposed it, or which party favoured it. Prompt that will use it (Junsol Kim's template):

    You are Senator [FULL NAME], representing [STATE] in the United States Senate in [YEAR].
    Consider the following roll-call vote: [DESCRIPTION]
    A YEA vote would: [YEA_MEANS]. A NAY vote would: [NAY_MEANS].
    How would you vote, based on your policy positions as this senator at that time? Respond with exactly one word: YEA or NAY.

## Input
One JSON object per line: key, issue, motion (content / procedural / unclassified), vote_question, bill_number, vote_desc,
dtl_desc, same_bill_context (other Voteview descriptions of the same bill in the same Congress and chamber).

## Output
A JSON list, one object per input line, same order, with exactly these fields:
- `key`: copied from the input.
- `description`: 1-3 plain English sentences. Name the measure (bill number; the bill's subject or short title when the source gives
  it) and say concretely what the amendment, bill or motion would do. For a procedural motion (table, recommit, previous question,
  cloture, motion to proceed, instruct conferees, decision of the chair) say what the motion does AND what proposal it acts on.
  For conference positions (recede, concur, insist) say which version or provision the motion accepts or keeps.
- `yea_means`: what a YEA vote would do, starting with a verb, no final period (e.g. "adopt the amendment, which prohibits the use
  of these funds for abortions except when the woman's life is endangered").
- `nay_means`: what a NAY vote would do, same form.
- `insufficient`: true only if the source text does not say what the vote is about (e.g. "On the Motion" with no description and no
  usable context). Then write the best neutral description the source allows and explain in `note`.
- `note`: empty, or a short reason for any judgment call.

## Rules
1. Use only the input text. Do not add facts from memory (no sponsor, outcome, date, history, or content that the source does not
   state). same_bill_context may be used only to name the bill's subject.
2. Remove every outcome signal: passed, rejected, agreed to (as an outcome), failed, sustained, adopted by, "(MOTION PASSED)",
   tallies, "3/5 required", "see RC ###", "see note(s)".
3. Remove names of legislators and party or state tags ("the Hyde amendment" -> "an amendment"; "by Smith (R-NJ)" -> delete).
   Program names and law names stay (Medicaid, Title X, Legal Services Corporation).
4. Neutral wording. Replace loaded terms with descriptive ones: "anti-abortion language" -> "language restricting abortion";
   "pro-life", "pro-choice", "unborn child", "baby" -> "fetus", "abortion", or the statutory phrase in quotation marks if the
   source names a bill by it (e.g. the bill's short title "Partial-Birth Abortion Ban Act" may be kept as a title in quotation marks).
   Use "woman" or "pregnant woman" where the source says "mother" only if the meaning is unchanged; keeping "mother" is also
   acceptable when quoting statutory language. Be consistent within a description.
5. Do not say which side is liberal or conservative, or who supports it.
6. Sentence case. Bill numbers as H.R. 1234, S. 123, H.J.Res. 12, H.Res. 12, S.Con.Res. 13.
7. For "TO TABLE X": the YEA side sets X aside (kills it); say what X would have done. For "TO RECOMMIT WITH INSTRUCTIONS": say what
   the instructions would add. For "ORDERING THE PREVIOUS QUESTION" on a rule: YEA ends debate on the rule and blocks an alternative;
   say what alternative the source names, if any.
8. Keep each description under 80 words.
