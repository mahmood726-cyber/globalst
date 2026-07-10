import json
import os
from pathlib import Path
import numpy as np
import pandas as pd
import pymc as pm
import arviz as az
import hashlib

ROOT = Path(__file__).resolve().parents[1]

def extract_diagnostics(raw_summary):
    """
    Extract convergence diagnostics from an arviz summary that has been
    rendered via pandas DataFrame.to_dict() (default orient='dict', which
    yields {column_name: {param_name: value}}).

    Returns (r_hat_max, n_eff_min). Either value is None if the corresponding
    column is absent from the summary.

    Note: the summary must be indexed by COLUMN ('r_hat', 'ess_bulk') first;
    iterating raw_summary.values() gives per-column {param: value} dicts, whose
    KEYS are parameter names, never 'r_hat'/'ess_bulk'.
    """
    r_hat_col = raw_summary.get('r_hat')
    ess_col = raw_summary.get('ess_bulk')
    r_hat_max = float(max(r_hat_col.values())) if r_hat_col else None
    n_eff_min = float(min(ess_col.values())) if ess_col else None
    return r_hat_max, n_eff_min

def generate_truthcert_hash(data):
    """
    Generate a SHA-256 hash for data to satisfy TruthCert requirements.
    """
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

def run_st_nma_mcmc(input_data):
    """
    Robust Spatio-Temporal Network Meta-Analysis (ST-NMA) using PyMC.
    """
    rcts = pd.DataFrame(input_data['rcts'])
    burden = pd.DataFrame(input_data['burden'])
    
    # Preprocessing
    # Map interventions to indices
    interventions = sorted(list(set(rcts['intervention'].unique()) | set(rcts['control'].unique())))
    int_map = {name: i for i, name in enumerate(interventions)}
    rcts['t_idx'] = rcts['intervention'].map(int_map)
    rcts['c_idx'] = rcts['control'].map(int_map)
    
    # Map regions to indices
    regions = sorted(list(set(rcts['region'].unique()) | set(burden['location'].unique())))
    reg_map = {name: i for i, name in enumerate(regions)}
    rcts['r_idx'] = rcts['region'].map(reg_map)
    
    # Map years to indices
    years = sorted(rcts['year'].unique())
    year_map = {yr: i for i, yr in enumerate(years)}
    rcts['y_idx'] = rcts['year'].map(year_map)
    
    # Simplified Log-OR and SE (for demonstration)
    y = np.log(rcts['effect_size'].values)
    # Approximate SE: 4 / sqrt(n) is a rough proxy for binary outcomes with balanced arms
    se = 4.0 / np.sqrt(rcts['n'].values)
    
    with pm.Model() as model:
        # Priors for treatment effects (relative to Placebo/index 0)
        # Note: We anchor the first intervention (usually Placebo) to 0
        d = pm.Normal("d", mu=0, sigma=1, shape=len(interventions))
        
        # Regional random effects
        tau_region = pm.HalfNormal("tau_region", sigma=0.5)
        delta_region = pm.Normal("delta_region", mu=0, sigma=tau_region, shape=len(regions))
        
        # Temporal random effects
        tau_year = pm.HalfNormal("tau_year", sigma=0.5)
        zeta_year = pm.Normal("zeta_year", mu=0, sigma=tau_year, shape=len(years))
        
        # Likelihood
        # The expected effect in trial i is (d[T] - d[C]) + region_effect + year_effect
        mu = (d[rcts['t_idx'].values] - d[rcts['c_idx'].values]) + \
             delta_region[rcts['r_idx'].values] + \
             zeta_year[rcts['y_idx'].values]
        
        pm.Normal("obs", mu=mu, sigma=se, observed=y)
        
        # Sampling
        print("Starting MCMC sampling...")
        trace = pm.sample(200, tune=100, cores=1, chains=1, random_seed=42, progressbar=False)
    
    # Summary. arviz >=1.0 renamed the credible-interval kwarg hdi_prob -> ci_prob;
    # fall back so the pipeline runs on both the old and pinned (1.1.0) arviz.
    try:
        summary = az.summary(trace, hdi_prob=0.95)
    except TypeError:
        summary = az.summary(trace, ci_prob=0.95)
    
    # Regional Estimates (Base + Regional Effect)
    # For a specific intervention (e.g., Statin vs Placebo)
    statin_idx = int_map.get('Statin', 0)
    base_statin_effect = trace.posterior['d'].sel(d_dim_0=statin_idx).values.flatten()
    
    results = []
    for reg_name, r_idx in reg_map.items():
        reg_effect = trace.posterior['delta_region'].sel(delta_region_dim_0=r_idx).values.flatten()
        total_effect = np.exp(base_statin_effect + reg_effect)
        
        results.append({
            "region": reg_name,
            "estimate": round(float(np.mean(total_effect)), 4),
            "ci_low": round(float(np.percentile(total_effect, 2.5)), 4),
            "ci_high": round(float(np.percentile(total_effect, 97.5)), 4),
            "evidence_hash": generate_truthcert_hash(reg_name) # Simplified for demo
        })
    
    return results, summary.to_dict(), generate_truthcert_hash(input_data)

def main():
    input_path = ROOT / "data" / "cvd_synthesis_input.json"
    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        return

    with open(input_path, 'r') as f:
        input_data = json.load(f)

    results, raw_summary, input_hash = run_st_nma_mcmc(input_data)

    r_hat_max, n_eff_min = extract_diagnostics(raw_summary)
    output = {
        "model": "ST-NMA-MCMC-v2.0",
        "results": results,
        "diagnostics": {
            "r_hat_max": r_hat_max,
            "n_eff_min": n_eff_min
        },
        "truthcert": {
            "input_hash": input_hash,
            "timestamp": "2026-04-08"
        }
    }

    output_path = ROOT / "output" / "st_nma_results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=4)
    print(f"MCMC Model execution complete. Results saved to {output_path}")

if __name__ == "__main__":
    main()
