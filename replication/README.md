# replication/

The analysis behind the manuscript and appendix. The repository README (`../README.md`) gives the commands; this file describes how
the package is organized and checked.

## Two paths

| | Path A: full rerun | Path B: analysis only |
|---|---|---|
| Input | raw data and the two models | raw data and the shipped model outputs (directions, maps, probabilities, generations) |
| Hardware | one GPU, bfloat16 | CPU |
| Steps | all steps in `run_pipeline.py` (`python run_pipeline.py --list`) | the CPU analysis steps; GPU steps and the CPU steps inside GPU chains are skipped and their shipped outputs used |
| Check | `tools/validate.py`: every output sha256-equal to `validation/SEAL.json`, and every value in `validation/headline_values.csv` reproduced | same |

`run_pipeline.py` holds the step graph: one command per step with its declared dependencies. A step starts when its dependencies are
done; each step writes `logs/pipeline/<step>.log` and a done marker, so an interrupted run resumes; the first failed step stops the run;
`logs/pipeline/run_path<A|B>.json` records each step's time and exit code with the configuration (`config/run.json`: models, pinned
revisions, precision, batch sizes, GPU memory budget).

## Determinism

`00_shared/loader.py` loads both models in bfloat16 at pinned revisions and enforces deterministic algorithms
(`torch.use_deterministic_algorithms(True)`, `CUBLAS_WORKSPACE_CONFIG=:4096:8`, TF32 off) with fixed batch sizes and seeds; every
random draw uses a seed derived from the name of the analysis. On the same hardware and software a rerun gives identical files. Path A
extracts the directions and chooses the layer twice (`02_ideology_map/out_layercheck/`) and stops if the two runs differ. Batch sizes
are never changed during a run, because batch size can change bfloat16 outputs.

## Layout

```
run_pipeline.py              single entry point (--path A | --path B; --list prints the steps)
config/run.json              models, revisions, precision, batch sizes, GPU budget
00_shared/ ... 16_supplementary_checks/
                             one folder per analysis: code/ (scripts numbered in run order), out/ (outputs), README.md (what it
                             computes and where the paper uses it); code/not_run/ holds the scripts that called external models
data/fetch_data.py           downloads and checks the raw data (not shipped)
environment/                 pinned Python (CPU, GPU, figures) and R environments
tools/                       validate.py, headline_values.py, clear_outputs.py, make_manifest.py, check_selection.py, numeric_gate.py
validation/                  SEAL.json (sha256 of every shipped output), headline_values.csv (every value the paper can draw on)
paper/                       the manuscript build (below)
MANIFEST.json                the files a clean Path A run starts from (code, configuration and frozen inputs) with their sha256
```

## The manuscript build

`paper/build.py` fills `paper/sections/*.template.md` from `paper/values.json` and `paper/appendix_values.json` (both read from the
package outputs by `paper/values.py` and `paper/appendix_values.py`; no number is typed), writes the tables (`paper/tables.py`) and
item lists (`paper/appendix_items.py`), draws the figures (`paper/body_figures.py`, `paper/appendix_figures.py`, in the environment of
`environment/requirements-paper.txt`), merges the reference lists, and writes `paper/manuscript.md` and `paper/appendix.md`. The build
stops if a value is missing or the figure environment is absent, and fails if any number printed in the text is not found in the value
files, the tables or the headline table (`tools/numeric_gate.py`). Figure files are written without timestamps; their checksums are
compared with `paper/figures/FIGURES_SHA256.ref.json`.

## Software

Python 3.12 (`environment/requirements-cpu.txt`, `requirements-gpu.txt`, `requirements-paper.txt`), R 4.5.3
(`environment/environment-r.yml`), CUDA 12.8 for Path A. Reference runs: one NVIDIA H200 (MIG 7g.141gb). Test records:
`VERIFICATION.md`.
