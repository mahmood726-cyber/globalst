"""Local transport fixtures: no fabricated research findings or trial IDs."""
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import ingest_data


@pytest.mark.parametrize("loader", [ingest_data.fetch_ct_gov_data,
                                   ingest_data.fetch_ihme_burden,
                                   ingest_data.fetch_world_bank_covariates])
def test_sources_are_required_instead_of_fabricated(loader, tmp_path, monkeypatch):
    monkeypatch.setattr(ingest_data, "ROOT", tmp_path)
    with pytest.raises(ValueError, match="snapshot"):
        loader()


@pytest.mark.parametrize("payload", [[], {}, [None], [{"value": float("nan")}], [{"value": float("inf")}]])
def test_invalid_snapshot_rejected(tmp_path, payload):
    path = tmp_path / "snapshot.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError):
        ingest_data.fetch_ct_gov_data(source_path=path)


def test_explicit_missing_snapshot_fails(tmp_path):
    with pytest.raises(FileNotFoundError):
        ingest_data.fetch_world_bank_covariates(source_path=tmp_path / "absent.json")


def test_explicit_snapshot_is_loaded_without_fallback(tmp_path):
    path = tmp_path / "snapshot.json"
    records = [{"transport_fixture": "local input"}]
    path.write_text(json.dumps(records), encoding="utf-8")
    for loader in [ingest_data.fetch_ct_gov_data, ingest_data.fetch_ihme_burden,
                   ingest_data.fetch_world_bank_covariates]:
        assert loader(source_path=path) == records


def test_cli_does_not_overwrite_output_on_invalid_input(tmp_path, monkeypatch):
    source = tmp_path / "source.json"
    source.write_text("{}", encoding="utf-8")
    output = tmp_path / "input.json"
    output.write_text("previous valid input", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["ingest_data.py", "--rcts", str(source),
        "--burden", str(source), "--covariates", str(source), "--output", str(output)])
    with pytest.raises(ValueError):
        ingest_data.main()
    assert output.read_text(encoding="utf-8") == "previous valid input"
