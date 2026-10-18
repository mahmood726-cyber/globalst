# globalst: Spatio-Temporal Network Meta-Analysis of Cardiovascular Disease

This repository implements a **Spatio-Temporal Network Meta-Analysis (ST-NMA)** to synthesize cardiovascular disease (CVD) evidence from gold-standard clinical trials and large-scale observational datasets.

## Project Scope
- **Data Integration:** Synthesizes RCT data from **ClinicalTrials.gov** with regional burden data from **IHME**, economic indicators from the **World Bank**, and policy data from **WHO**.
- **Statistical Framework:** A Bayesian hierarchical model that borrows strength across spatial (geographic regions) and temporal (years) dimensions to provide context-specific comparative effectiveness estimates.
- **E156 Micro-Paper:** Includes a 7-sentence, 156-word summary of core findings with **TruthCert** proof-carrying numbers.

## Structure
- `src/`: Python/R scripts for the data ingestion and modeling pipeline.
- `data/`: Ingested (Open Access only) data and fixed fixtures for testing.
- `output/`: Model results, estimates, and TruthCert audit logs.
- `tests/`: Automated test suite for data validation and model stability.
- `docs/`: Documentation and the E156 micro-paper draft.

## Setup
Install the pinned dependencies from the repo root:

```
pip install -r requirements.txt
```

`pymc` compiles its model graph through PyTensor and requires a C++ compiler
(`g++` / `gxx`) on `PATH` to run MCMC sampling (with conda:
`conda install -c conda-forge gxx`). The test suite and the diagnostics helpers
run without a compiler; only `run_st_nma_mcmc()` sampling needs one.

Run the tests from the repo root:

```
python -m pytest -q
```

## Pipeline
Ingestion loads explicitly supplied local JSON snapshots. It does not call the
ClinicalTrials.gov, IHME or World Bank APIs, invent fallback records, or silently
select the bundled illustrative fixtures. Each input must be a nonempty list of
record objects with finite numbers; source identity and research validity still
require independent checks before analysis.

```bash
python src/ingest_data.py --rcts registry.json --burden burden.json --covariates covariates.json --output data/cvd_synthesis_input.json
```

The historical `fetch_*` Python helpers now require `source_path=...` instead of
accepting unused search parameters. Missing/invalid inputs leave the existing
output intact. Existing bundled fixtures and saved results are illustrative;
this ingestion repair does not validate their scientific content.

The project follows the E156 research pipeline rules. See `GEMINI.md` for detailed session instructions and session workflow.

## License
MIT (or as per repository policy).
