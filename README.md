# Language Models Reconstruct a Different History of American Political Polarization

This repository holds the manuscript, its appendix, and the code and data needed to reproduce every number, table and figure in them.

- Manuscript: [`replication/paper/manuscript.md`](replication/paper/manuscript.md)
- Appendix: [`replication/paper/appendix.md`](replication/paper/appendix.md)

Two open models (Qwen2.5-7B-Instruct and Llama-3.1-8B-Instruct) speak as every member of Congress from 1947 to 2024. Each member is
placed on an economic and a social direction taken from the model's activations, and the resulting map is compared with roll-call
records and DW-NOMINATE. The models reconstruct a different history of polarization, and they misplace most cross-pressured members.
The models' vote predictions and their uncertainty are compared in the same way.

## What is here

| Folder | Contents |
|---|---|
| `replication/` | the analysis: one folder per analysis (`00_shared` to `16_supplementary_checks`, each with a short README), the pipeline (`run_pipeline.py`), configuration, environments, validation, and `paper/` (the manuscript build) |
| `congress_map/` | Junsol Kim's direction-extraction and projection scripts (`01_extract_vectors.py`, `03_project_legislators.py`), run unchanged by the package, and the two result files the package compares against |
| `data_generation/trait_data_extract/` | the paired instructions and policy questions used to build the directions |

Analysis-plan records and working notes are not part of this repository. Ten small files in `protocol/` folders remain because the
code checks them before it runs (plan hashes and pre-run records).

## Reproducing the paper

Requirements: Python 3.12, R 4.5.3 (installed with micromamba), and for the full rerun one GPU with enough memory for an 8B model in
bfloat16 (the reference runs used an NVIDIA H200).

```bash
git clone <this repository> && cd <repository>/replication
python -m venv .venv && source .venv/bin/activate
pip install -r environment/requirements-cpu.txt         # or requirements-gpu.txt for the full rerun
micromamba create -n r -f environment/environment-r.yml
export RSCRIPT="micromamba run -n r Rscript"
python data/fetch_data.py                               # raw data, each file checked by sha256 (see Data)
python run_pipeline.py --path B                         # every analysis from the shipped model outputs (CPU, about one hour)
python tools/validate.py                                # every output compared with validation/SEAL.json
```

Build the manuscript and appendix (numbers, tables, figures) from the outputs:

```bash
python -m venv ~/venvs/paperfig && ~/venvs/paperfig/bin/pip install -r environment/requirements-paper.txt
python paper/build.py                                   # writes paper/manuscript.md and paper/appendix.md
```

Full rerun from the models (GPU, several hours; Llama-3.1 needs approved access on Hugging Face):

```bash
python tools/clear_outputs.py --yes                     # remove shipped outputs so every step recomputes
python run_pipeline.py --path A
python tools/validate.py
```

## Data

The raw files are not redistributed. `data/fetch_data.py` downloads what it can and checks every file against the exact copy the
analyses used; a mismatch stops the run.

| File | Source |
|---|---|
| HSall_members, HSall_rollcalls, HSall_votes | Voteview (voteview.com). Voteview re-estimates scores at each update, so a later download can differ from the copy used; the authors can provide the exact copies. |
| rcv_voteview_v3_4.csv | Policy Agendas Project (comparativeagendas.net); download by hand into `replication/data/agendas/` |
| 1976-2024-president.csv | MIT Election Data and Science Lab, doi:10.7910/DVN/42MVDX; download by hand into `replication/data/elections/` |
| hein-bound.zip, hein-daily.zip | Gentzkow, Shapiro and Taddy, Congressional Record (Stanford Digital Repository); downloaded by the script |

Three steps called external language models and are not rerun: labelling gun roll calls, and writing and checking the roll-call
descriptions. Their scripts are in the `code/not_run/` folders and their outputs ship as fixed inputs.

## Licence

Code: `replication/LICENSE`. Data, items, prompts and result files written for this project: CC BY 4.0 (`replication/LICENSE-DATA`).
Raw data keep their original terms. `congress_map/` is Junsol Kim's code.
