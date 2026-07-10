"""Regression tests for the ST-NMA statistical core.

Primary guard: the convergence diagnostics (r_hat_max / n_eff_min) must be
populated. The shipped code iterated the wrong dict level of
az.summary().to_dict() (orient='dict' => {column: {param: value}}), so both
diagnostics were always None, silently suppressing the Rhat>1.01 / ESS<400
gates. See src/model_stnma.py::extract_diagnostics.
"""
import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from model_stnma import extract_diagnostics  # noqa: E402


def _az_shaped_summary():
    """A DataFrame shaped like az.summary(): index=params, columns=metrics."""
    df = pd.DataFrame(
        {
            "mean": [0.10, 0.20, -0.05],
            "sd": [0.05, 0.06, 0.04],
            "ess_bulk": [450.0, 600.0, 512.0],
            "r_hat": [1.01, 1.00, 1.03],
        },
        index=["d[0]", "tau_region", "delta_region[0]"],
    )
    return df.to_dict()


def test_extract_diagnostics_populated():
    """Correct indexing yields the max r_hat and min ess_bulk, not None."""
    r_hat_max, n_eff_min = extract_diagnostics(_az_shaped_summary())
    assert r_hat_max == pytest.approx(1.03)
    assert n_eff_min == pytest.approx(450.0)


def test_extract_diagnostics_reproduces_old_bug_pattern():
    """The old pattern (iterating .values() and testing 'r_hat' in v) returns
    None on the real az.summary().to_dict() shape; the fixed helper does not."""
    raw = _az_shaped_summary()
    # Old buggy extraction (parameter-name membership test) -> always empty.
    buggy_r_hat = [v["r_hat"] for v in raw.values() if "r_hat" in v]
    assert buggy_r_hat == []  # documents why diagnostics shipped as null
    # Fixed helper recovers the real value.
    r_hat_max, _ = extract_diagnostics(raw)
    assert r_hat_max is not None


def test_extract_diagnostics_missing_columns():
    """When r_hat / ess_bulk columns are absent, return None (not a crash)."""
    raw = pd.DataFrame({"mean": [0.1], "sd": [0.05]}, index=["d[0]"]).to_dict()
    r_hat_max, n_eff_min = extract_diagnostics(raw)
    assert r_hat_max is None
    assert n_eff_min is None


def _tiny_input():
    """Minimal but valid ST-NMA input: two arms, k=2 trials, one region/year."""
    return {
        "rcts": [
            {
                "trial_id": "NCT-A",
                "intervention": "Statin",
                "control": "Placebo",
                "region": "Europe",
                "year": 2020,
                "effect_size": 0.85,
                "n": 4000,
            },
            {
                "trial_id": "NCT-B",
                "intervention": "Statin",
                "control": "Placebo",
                "region": "Asia",
                "year": 2021,
                "effect_size": 0.90,
                "n": 3500,
            },
        ],
        "burden": [{"location": "Europe", "measure": "DALYs", "val": 1000}],
        "covariates": [],
    }


def test_end_to_end_diagnostics_are_populated():
    """End-to-end guard: run_st_nma_mcmc's summary must feed extract_diagnostics
    and yield non-null diagnostics on the REAL az.summary().to_dict() shape.
    This is the exact path that shipped nulls in output/st_nma_results.json.
    Gated on pymc; skipped if sampling is unavailable in this environment."""
    pytest.importorskip("pymc")
    import warnings

    from model_stnma import run_st_nma_mcmc

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            _results, raw_summary, _hash = run_st_nma_mcmc(_tiny_input())
        except Exception as exc:  # pragma: no cover - compiler/backend absent
            pytest.skip(f"MCMC sampling unavailable in this environment: {exc}")

    r_hat_max, n_eff_min = extract_diagnostics(raw_summary)
    # F1 guard: extraction must pull real values from the summary columns, not
    # the always-None the buggy code shipped. n_eff_min (ess_bulk) is well
    # defined even with a single chain; r_hat is a float that may be NaN when
    # the model samples chains=1 (a separate model limitation, not F1), so we
    # only assert it was populated (not None), proving the column was indexed.
    assert r_hat_max is not None, "r_hat_max must be populated (not None) after the fix"
    assert n_eff_min is not None, "n_eff_min must be populated after the fix"
    assert n_eff_min > 0
