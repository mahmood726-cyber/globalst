"""Assemble explicitly supplied local snapshots; no live acquisition or fallback data."""
import argparse
import json
import math
import os
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def _reject_nonfinite(value):
    raise ValueError(f"Nonfinite number in snapshot: {value}")


def _check_finite(value):
    if isinstance(value, float) and not math.isfinite(value):
        _reject_nonfinite(value)
    if isinstance(value, dict):
        for item in value.values():
            _check_finite(item)
    elif isinstance(value, list):
        for item in value:
            _check_finite(item)


def _load_snapshot(source_path):
    if source_path is None:
        raise ValueError("An explicit local snapshot is required; live fetching is not implemented")
    with Path(source_path).open(encoding="utf-8") as source:
        records = json.load(source, parse_constant=_reject_nonfinite)
    if not isinstance(records, list) or not records or any(not isinstance(r, dict) for r in records):
        raise ValueError("A snapshot must contain a nonempty JSON list of record objects")
    _check_finite(records)
    return records


def fetch_ct_gov_data(*, source_path=None):
    """Load a caller-supplied registry snapshot; this function does not query CT.gov."""
    return _load_snapshot(source_path)


def fetch_ihme_burden(*, source_path=None):
    """Load a caller-supplied burden snapshot; this function does not query IHME."""
    return _load_snapshot(source_path)


def fetch_world_bank_covariates(*, source_path=None):
    """Load caller-supplied covariates; this function does not query the World Bank."""
    return _load_snapshot(source_path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("rcts", "burden", "covariates", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    data = {
        "rcts": fetch_ct_gov_data(source_path=args.rcts),
        "burden": fetch_ihme_burden(source_path=args.burden),
        "covariates": fetch_world_bank_covariates(source_path=args.covariates),
    }
    encoded = json.dumps(data, indent=4, allow_nan=False)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=args.output.parent, suffix=".tmp", delete=False) as staged:
        staged_path = Path(staged.name)
    try:
        staged_path.write_text(encoded, encoding="utf-8")
        os.replace(staged_path, args.output)
    finally:
        staged_path.unlink(missing_ok=True)
    print(f"Loaded local snapshots into {args.output}; no live sources were queried.")


if __name__ == "__main__":
    main()
