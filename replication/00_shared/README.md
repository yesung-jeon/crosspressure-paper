# 00_shared

Shared code: the model loader (bf16, pinned revisions, deterministic mode) and constants used by several folders (persona wording read from congress_map/03_project_legislators.py, state names, seeds).

Used in: every model step.

Imported by the analysis steps; it writes no outputs of its own.
