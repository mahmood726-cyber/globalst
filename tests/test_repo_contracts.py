from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OFFLINE_MARKERS = (
    "https://cdn.",
    "https://cdnjs.cloudflare.com",
    "https://cdn.jsdelivr.net",
    "https://unpkg.com",
    "https://fonts.googleapis.com",
    "https://fonts.gstatic.com",
)


def test_release_contract_files_exist():
    assert (PROJECT_ROOT / "docs" / "index.html").exists()
    assert (PROJECT_ROOT / "E156-PROTOCOL.md").exists()


def test_dashboard_is_offline_first():
    html = (PROJECT_ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    assert not any(marker in html for marker in OFFLINE_MARKERS)
    assert "../vendor/chart.umd.min.js" in html
    assert (PROJECT_ROOT / "vendor" / "chart.umd.min.js").exists()


def test_protocol_has_dashboard_reference():
    protocol = (PROJECT_ROOT / "E156-PROTOCOL.md").read_text(encoding="utf-8")
    assert "**Dashboard**:" in protocol
