from mcp_servers.procurement.tools.flag_supplier_risk import (
    flag_supplier_risk_record,
)


def test_alpha_supplier_has_low_risk():
    result = flag_supplier_risk_record("BID-ALPHA-001")

    assert result["supplier_name"] == "Alpha Technologies Ltd"
    assert result["risk_level"] == "LOW"
    assert result["flag_count"] == 0
    assert result["historical_records_checked"] == 2


def test_beta_supplier_identifier_inconsistency_is_flagged():
    result = flag_supplier_risk_record("BID-BETA-001")

    assert result["supplier_name"] == "Beta Systems Ltd"
    assert result["risk_level"] == "ELEVATED"

    codes = {
        flag["code"]
        for flag in result["flags"]
    }

    assert "IDENTIFIER_NAME_INCONSISTENCY" in codes

    for flag in result["flags"]:
        assert flag["sources"]