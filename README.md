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

## Pipeline
The project follows the E156 research pipeline rules. See `GEMINI.md` for detailed session instructions and session workflow.

## License
MIT (or as per repository policy).
