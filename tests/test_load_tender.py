import pytest

from mcp_servers.procurement.tools.load_tender import load_tender_record


def test_load_tender_record():
    result = load_tender_record("TG-DEMO-001")

    assert result["tender_id"] == "TG-DEMO-001"
    assert result["title"] == "Supply of Computer Equipment"
    assert result["amount"] == 45000000
    assert result["currency"] == "TZS"
    assert result["ocid"] == "ocds-demo-tz-001"
    assert result["source_file"] == "data\\ocds\\demo_tender.json"


def test_load_tender_rejects_unknown_tender():
    with pytest.raises(FileNotFoundError):
        load_tender_record("UNKNOWN-TENDER")