Scripts kept as records and never run by the pipeline (rebuild 2026-10-23):
- g0_labels_gpt.py: GPT-4.1-mini labels through the OpenAI API (needs a key; its outputs labels_gpt.csv and gpt_ledger/ are shipped as frozen inputs).
- g0_review.py: builds the author's blind review sheet and labels_merged.csv; rerunning it would blank the author's judgments in AUTHOR_REVIEW.csv. Both files are shipped as frozen inputs.
- g0_gpt_prompt.txt: the prompt g0_labels_gpt.py used.
