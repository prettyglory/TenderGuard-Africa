from mcp_servers.procurement.tools.check_bid_compliance import (
    check_bid_compliance_record,
)


def test_compliant_bid_passes():
    result = check_bid_compliance_record(
        "TG-DEMO-001",
        "BID-ALPHA-001",
    )

    assert result["status"] == "COMPLIANT"
    assert result["summary"]["failed_checks"] == 0
    assert result["supplier"] == "Alpha Technologies Ltd"

    for check in result["checks"]:
        assert check["sources"]


def test_non_compliant_bid_is_flagged():
    result = check_bid_compliance_record(
        "TG-DEMO-001",
        "BID-BETA-001",
    )

    assert result["status"] == "NON_COMPLIANT"
    assert result["summary"]["failed_checks"] == 3

    failed_criteria = {
        check["criterion"]
        for check in result["checks"]
        if not check["passed"]
    }

    assert "SUBMISSION_DEADLINE" in failed_criteria
    assert "TAX_CLEARANCE" in failed_criteria
    assert "LOCAL_REGISTRATION" in failed_criteria