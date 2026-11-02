# Language Models Reconstruct a Different History of American Political Polarization

This repository holds the manuscript, its appendix, and the code needed to reproduce every number, table and figure in them.

- Manuscript: [`replication/paper/manuscript.md`](replication/paper/manuscript.md)
- Appendix: [`replication/paper/appendix.md`](replication/paper/appendix.md)

Two open models (Qwen2.5-7B-Instruct and Llama-3.1-8B-Instruct) speak as every member of Congress from 1947 to 2024. Each member is
placed on an economic and a social direction taken from the model's activations, and the resulting map is compared with roll-call
records and DW-NOMINATE. The models' vote predictions and their uncertainty are compared with the record in the same way.

## What is here

| Folder | Contents |
|---|---|
| `replication/` | the analysis, one folder per analysis in the order of the paper (`00_shared` to `19_bundled_choices`, each with a README), the pipeline (`run_pipeline.py`), configuration, environments, validation, and `paper/` (the manuscript build); see `replication/README.md` |
| `congress_map/` | Junsol Kim's direction-extraction and projection scripts, run unchanged by the full path |
| `data_generation/trait_data_extract/` | the paired instructions and policy questions used to build the directions |

## Reproducing the paper

Requirements: Python 3.12, R 4.5.3 (installed with micromamba), and for the full rerun one GPU with enough memory for an 8B model in
bfloat16 (the reference runs used an NVIDIA H200).

```bash
git clone <this repository> && cd <repository>/replication
python -m venv .venv && source .venv/bin/activate
pip install -r environment/requirements-cpu.txt         # or requirements-gpu.txt for the full rerun
micromamba create -n r -f environment/environment-r.yml
export RSCRIPT="micromamba run -n r Rscript"
python data/fetch_data.py                               # raw data, each file checked by sha256 (see replication/README.md, Data)
python run_pipeline.py --path B                         # every analysis from the shipped model outputs (CPU, about 75 minutes)
python tools/validate.py                                # every output and reported value compared with the seal
python paper/build.py                                   # rebuild the manuscript and appendix (figure environment: replication/README.md)
```

Full rerun from the models (GPU; Llama-3.1 needs approved access on Hugging Face):

```bash
python tools/clear_outputs.py --yes                     # remove shipped outputs so every step recomputes
python run_pipeline.py --path A
python tools/validate.py
```

## Data

The raw files are not redistributed. `replication/data/fetch_data.py` downloads what it can and checks every file against the exact
copy the analyses used; a mismatch stops the run. Voteview re-estimates scores at each update, so a later download can differ from the
copy used; the authors can provide the exact copies. The Policy Agendas Project topics and the MIT presidential returns are downloaded
by hand (sources and folders in `replication/README.md`).

## Licence

Code: `replication/LICENSE`. Data, items, prompts and result files written for this project: CC BY 4.0 (`replication/LICENSE-DATA`).
Raw data keep their original terms. `congress_map/` is Junsol Kim's code.
