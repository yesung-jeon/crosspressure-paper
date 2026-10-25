# Verification

## Fresh-copy test of this repository (2026-10-25)

- **Source:** the exact file set a commit of this repository holds (`git ls-files -co --exclude-standard`), copied to a new directory.
- **Raw data:** the exact copies the analyses used; `data/fetch_data.py` checked each file's sha256 before the run (all matched).
- **Environment:** Python 3.12.3 with `environment/requirements-cpu.txt`; R 4.5.3 (`environment/environment-r.yml`, micromamba);
  `RSCRIPT="micromamba run -n r Rscript"`; a new figure environment built from `environment/requirements-paper.txt` (its `pip freeze`
  equal to the file).
- **Path B:** `python run_pipeline.py --path B`: all 196 steps done (GPU steps use the shipped model outputs), 21:44 to 23:10 on an
  NVIDIA H200 VDI with 8 CPU cores. The longest steps were the Congressional Record matrices and the speech history.
- **Validation:** `python tools/validate.py`: 1,616 output files identical to `validation/SEAL.json`, 0 differ, 0 missing, 0 not
  sealed; 482 headline rows, 0 problems. PASS.
- **Manuscript build:** `python paper/build.py`: number check 0 missing for the manuscript and the appendix; abstract 195 words; 34
  figure files identical to `paper/figures/FIGURES_SHA256.ref.json`; `paper/manuscript.md` and `paper/appendix.md` byte-identical to
  the files in this repository.

## Full rerun from the models (Path A)

Path A was last run end to end from a fresh clone of the package these files were taken from (2026-10-24/25, both models, one NVIDIA
H200): every output was bit-identical to the seal. Since then, steps whose results the paper does not report were removed; no kept
step's computation, input or output changed (comments were edited in two scripts). Path A was not rerun for this repository.

## Determinism

On the same hardware and software, reruns give identical output files (deterministic algorithms, fixed batch sizes and seeds; see
`README.md`). On other hardware, the last digits of some model outputs can differ; `tools/validate.py` then lists the files that
differ, and its headline-value check shows whether any reported value changes.
