import pytest

import mcp_servers.procurement.tools.generate_evaluation_report as report_module


def test_report_requires_human_approval():
    with pytest.raises(PermissionError):
        report_module.generate_evaluation_report_file(
            "TG-DEMO-001",
            "BID-ALPHA-001",
            "",
        )


def test_report_is_generated_after_human_approval(tmp_path, monkeypatch):
    monkeypatch.setattr(
        report_module,
        "REPORTS_DIR",
        tmp_path,
    )

    result = report_module.generate_evaluation_report_file(
        "TG-DEMO-001",
        "BID-ALPHA-001",
        "Demo Procurement Officer",
    )

    assert result["report_status"] == "DRAFT_FOR_COMMITTEE_REVIEW"
    assert result["approved_by"] == "Demo Procurement Officer"
    assert result["final_decision_made"] is False

    report_file = tmp_path / "BID-ALPHA-001_evaluation_report.md"

    assert report_file.exists()

    content = report_file.read_text(encoding="utf-8")

    assert "DRAFT FOR HUMAN PROCUREMENT COMMITTEE REVIEW" in content
    assert "TenderGuard Africa provides decision support only" in content
    assert "Demo Procurement Officer" in content