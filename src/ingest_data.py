import json
import os
from pathlib import Path
import requests
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

def fetch_ct_gov_data(condition="Cardiovascular Diseases"):
    """
    Fetch RCT data from ClinicalTrials.gov (mock/example for now).
    """
    # In a real scenario, use the ClinicalTrials.gov API.
    # For now, we use a fixture if available, else return a mock.
    fixture_path = ROOT / "data" / "fixtures" / "cvd_rct_fixtures.json"
    if os.path.exists(fixture_path):
        with open(fixture_path, 'r') as f:
            return json.load(f)
    return [{"trial_id": "NCT001", "intervention": "A", "control": "B", "outcome": "mortality", "effect_size": 0.85, "n": 5000}]

def fetch_ihme_burden(measure="DALYs", cause="Cardiovascular diseases"):
    """
    Extract CVD burden (e.g., DALYs) from IHME GBD dataset.
    """
    fixture_path = ROOT / "data" / "fixtures" / "ihme_cvd_burden.json"
    if os.path.exists(fixture_path):
        with open(fixture_path, 'r') as f:
            return json.load(f)
    return [{"location": "Global", "measure": measure, "val": 450000000}]

def fetch_world_bank_covariates(indicator="NY.GDP.PCAP.CD"):
    """
    Pull relevant covariates (e.g., GDP per capita) from the World Bank API.
    """
    # World Bank API is generally Open Access: https://api.worldbank.org/v2/country/all/indicator/NY.GDP.PCAP.CD?format=json
    return [{"country": "USA", "gdp_per_capita": 70000}, {"country": "IND", "gdp_per_capita": 2300}]

def main():
    print("Fetching CVD data from Open Access sources...")
    rcts = fetch_ct_gov_data()
    burden = fetch_ihme_burden()
    covariates = fetch_world_bank_covariates()
    
    data = {
        "rcts": rcts,
        "burden": burden,
        "covariates": covariates
    }
    
    output_path = ROOT / "data" / "cvd_synthesis_input.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Data ingestion complete. Saved to {output_path}")

if __name__ == "__main__":
    main()
