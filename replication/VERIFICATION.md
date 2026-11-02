# Verification

What was checked for this release, how, and what was not checked.

## The short path from a fresh copy (2026-11-02)

- A fresh copy held exactly the files a clone of this repository holds (`git ls-files`, respecting `.gitignore`). The raw data were the
  exact copies the analyses used; `data/fetch_data.py` confirmed each sha256.
- `python run_pipeline.py --path B` ran every CPU step. `python tools/validate.py` then reported:
  - 3,434 of 3,434 sealed output files identical to `validation/SEAL.json`, none missing;
  - 1,094 code, configuration and frozen-input files matching `MANIFEST.json`;
  - the paper value files and tables identical to `validation/PAPER_SEAL.json`;
  - 582 headline rows, 0 problems.
- `python paper/build.py` then rebuilt the manuscript and appendix. The number check found no printed number without a source, and the
  36 figure files matched `paper/figures/FIGURES_SHA256.ref.json`. `paper/manuscript.md`, `paper/appendix.md`, both tables and the figure
  checksums were byte-identical to the versions in this repository.
- The speech matrices (`12_speech_and_state/out/s0/`, not shipped) were deleted and rebuilt from the raw Congressional Record files;
  every sealed output still validated.

## Relation to the authors' working repository

This package was assembled from the authors' working repository, keeping the analyses the paper reports and their inputs. Folders were
renamed in the order of the paper. Every sealed output of the working repository that this package keeps was compared file by file:
all are byte-identical, or differ only in folder names stored as text, in wall-clock run times, in gzip header times, or in descriptive
note strings. The built manuscript, appendix, tables and figures are byte-identical to the working repository's.

## The full path

- The full path (raw data and the two models, GPU) was rerun from a fresh copy of the working package on 2026-10-24, on one NVIDIA H200,
  and reproduced its outputs exactly.
- GPU steps added or changed after that rerun (the answer-scale scoring, the 1-9 named-member scoring, and reruns of the stated-profile
  scoring and its named-member check after a change in the median-split rule) were run once on the same machine; their outputs ship with the package.
- The full path was not rerun for this release.

## Not checked

- An installation on a machine other than the authors' (environment files are pinned in `environment/`).
- The three steps that called external language models (gun-roll-call labels; writing and checking roll-call descriptions) are not
  rerun; their outputs ship as fixed inputs.
