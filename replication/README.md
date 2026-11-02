# Replication package

This package reproduces every number, table and figure in the manuscript and its appendix from raw data and two public open-weight
models:

- Qwen2.5-7B-Instruct
- Llama-3.1-8B-Instruct

Both models run in bf16 at pinned revisions (`config/run.json`). One command runs the whole analysis as a graph of steps, and a
validation script checks every output against the sealed release.

## Quick start (short path, CPU)

```bash
cd replication
python -m venv .venv && source .venv/bin/activate
pip install -r environment/requirements-cpu.txt          # GPU machines: environment/requirements-gpu.txt
micromamba create -n r -f environment/environment-r.yml   # R 4.5.3 with fixest, arrow, data.table
export RSCRIPT="micromamba run -n r Rscript"
python data/fetch_data.py                                # raw data, each file checked by sha256 (see Data)
python run_pipeline.py --path B                          # every analysis from the shipped model outputs
python tools/validate.py                                 # compare every output and every reported value with the seal
```

The short path takes about 75 minutes on 8 CPU cores.

## Full path (GPU)

```bash
huggingface-cli login                                    # Llama-3.1 needs approved access; Llama also judges layer selection
python tools/clear_outputs.py --yes                      # remove the shipped outputs so every step recomputes
python run_pipeline.py --path A                          # both models on one GPU
python tools/validate.py
```

The full path was developed on one NVIDIA H200 (141 GB). Settings for that card are in `config/run.json`; a smaller card needs smaller
batch sizes there, which can change the last digits of model outputs. `python run_pipeline.py --list` prints the step graph, and
`--until <step>` runs only the steps one target needs.

| | Path A: full | Path B: short |
|---|---|---|
| Input | raw data and the two models | raw data and the shipped model outputs (directions, maps, probabilities) |
| Hardware | GPU, bf16 | CPU |
| Steps | 151 (224 with GPU shards) | the CPU steps; GPU steps, and CPU steps inside GPU chains such as layer selection, are skipped |
| Check | `tools/validate.py` | same |

How the runner works:
- `run_pipeline.py` holds one command per step with its declared dependencies. A step starts when its dependencies are done; GPU
  steps share the card under a memory budget; CPU steps share the cores.
- Each step writes `logs/pipeline/<step>.log` and a done marker. A rerun skips steps that are done, so an interrupted run resumes. The
  first failed step stops the run. `logs/pipeline/run_path<A|B>.json` records each step's time, exit code and the configuration.
- `00_shared/loader.py` enforces determinism: deterministic algorithms, fixed workspace configuration, TF32 off, fixed batch sizes and
  seeds. Every random draw uses a seed derived from the name of the analysis. An out-of-memory error stops the run; batch sizes are
  never changed during a run, because batch size can change bf16 outputs.
- Layer gate: path A extracts the directions and selects the steering layer twice (`05_directions_and_map/out_layercheck/`) and stops
  if the two runs differ.

## Building the paper

```bash
python -m venv ~/venvs/paperfig && ~/venvs/paperfig/bin/pip install -r environment/requirements-paper.txt   # figures only
python paper/build.py                                    # PAPER_PYTHON=<interpreter> to use another figure environment
```

`paper/build.py` fills `paper/sections/*.template.md` from `paper/values.json` and `paper/appendix_values.json`, which `paper/values.py`
and `paper/appendix_values.py` read from `validation/headline_values.csv` and from package outputs. It draws the figures, merges the
reference lists and writes `paper/manuscript.md` and `paper/appendix.md`. It stops if a value is missing, and it fails if any number
printed in the text is not found in the generated values (`tools/numeric_gate.py`). Figures are written without timestamps; their
checksums are compared with `paper/figures/FIGURES_SHA256.ref.json`.

## Folder layout (in the order of the paper)

| Folder | What it computes | Used in |
|---|---|---|
| `00_shared/` | model loader (bf16, deterministic), shared constants, the median-split rule | all |
| `01_rollcall_scales/` | economic and abortion roll-call scales from Voteview (Policy Agendas topics) | Section 3, A.3 |
| `02_gun_scale/` | gun-control roll-call scale and map recall on guns | A.3, C.1 |
| `03_gun_inputs/` | the gun scale in the social slot, so the map analyses rerun on guns | C.1, C.6 |
| `04_steering_tools/` | steering helpers (library) | used by 05, 18, 19 |
| `05_directions_and_map/` | economic and social directions, layer selection, the map, recall by vote quadrant, the 60 members selected by their votes, stated profiles | Sections 3 and 5, A.4-A.5, C |
| `06_party_history/` | party gaps over time on the map and in DW-NOMINATE | Section 4, B |
| `07_nominate_benchmarks/` | Nokken-Poole comparison of continuing members; NOMINATE fit | B.3, D.8 |
| `08_supplementary_checks/` | recall benchmarks (two-dimensional DW-NOMINATE, recognized members), members by decade, noise benchmark, vote-prompt checks, answer-order agreement, named cases, figure data, layer check | Sections 5-6, C, D |
| `09_distance_from_medians/` | placement gap by distance from the medians | Section 5, C.7 |
| `10_vote_prediction/` | roll-call selection, descriptions, prompts, vote prediction, accuracy comparisons, leave-one-out labels, guns | Section 6, D |
| `11_vote_prediction_scale/` | vote predictions read from the nine-point scale; scale task checks | Section 6, D.10 |
| `12_speech_and_state/` | floor-speech partisanship; state presidential lean | D.7, F.2 |
| `13_gun_checks/` | gun versions of the speech, state and NOMINATE checks | D.5, D.7, D.8 |
| `14_vote_uncertainty/` | entropy of the two-answer vote predictions (R) | Section 7, E |
| `15_named_member_uncertainty/` | entropy of named-member answers (R) | Section 7, E.3 |
| `16_scale_uncertainty/` | entropy on the answer scales (votes and named members) | Section 7, E |
| `17_error_warning/` | whether entropy separates wrong from right predictions | Section 7, E.4 |
| `18_economic_weight/` | economic and social weight within party; party versus economic side | F.1 |
| `19_bundled_choices/` | bundled-choice battery, input of the no-persona check and F.1 analyses | F.1 |
| `config/` | models, revisions, precision, batch sizes, GPU budget | |
| `data/` | `fetch_data.py` (raw data are downloaded, not shipped) | |
| `environment/` | pinned Python and R environments | |
| `paper/` | section templates, value builders, figure and table scripts, built manuscript and appendix | |
| `tools/` | `validate.py`, `headline_values.py`, `make_manifest.py`, `clear_outputs.py`, `check_selection.py`, `numeric_gate.py` | |
| `validation/` | `SEAL.json` (sha256 of every output), `headline_values.csv`, `PAPER_SEAL.json` | |

Each analysis folder has a `README.md`. Protocols written before the analyses they govern are in `<folder>/protocol/` where the paper
relies on them (Appendix C.7, D.6, D.10, E.2).

The two sibling folders `../congress_map/` (Junsol Kim's direction extraction and member projection, run unchanged) and
`../data_generation/` (instruction and question files) are used by path A.

## Data

`data/fetch_data.py` downloads the raw files and checks each against the exact copy used; a sha256 mismatch stops the run.

| File | Source | Redistributed |
|---|---|---|
| HSall_members, HSall_rollcalls, HSall_votes | Voteview (voteview.com) | no; Voteview re-estimates scores at each update, so a new download differs from the copy used |
| rcv_voteview_v3_4.csv | Policy Agendas Project | no: download from comparativeagendas.net |
| 1976-2024-president.csv | MIT Election Data and Science Lab, doi:10.7910/DVN/42MVDX | no: download from Harvard Dataverse |
| hein-bound.zip, hein-daily.zip | Gentzkow, Shapiro and Taddy, Stanford Digital Repository | no (downloaded with resumption) |

## What is and is not reproduced

- **Reproduced:** every estimate, interval and reading in the manuscript and appendix.
- **Same setup and other setups:** reruns are bit-identical on the same GPU type, driver, CUDA, PyTorch and library versions
  (`environment/`) and the same CPU thread count. `run_pipeline.py` gives each CPU step `cpu_count // cpu_processes` BLAS threads; a
  step run by hand must set `OMP_NUM_THREADS`, `MKL_NUM_THREADS` and `OPENBLAS_NUM_THREADS` to the same value. On other hardware the
  last digits of model outputs can differ; `tools/validate.py` then reports which files differ and how much the reported values change.
- **Not rerun:** three steps called external language models: the labelling of gun roll calls (A.3) and the writing and checking of
  roll-call descriptions (D.1). Their scripts ship in `code/not_run/` folders and their outputs ship as fixed inputs.
- **Verified:** see `VERIFICATION.md`.

## Software

Python 3.12 (`environment/requirements-*.txt`), R 4.5.3 (`environment/environment-r.yml`).

## Licence

Code: `LICENSE`. Data and derived outputs: `LICENSE-DATA`.
