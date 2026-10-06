from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mcp_servers.procurement.tools.check_bid_compliance import (
    check_bid_compliance_record,
)
from mcp_servers.procurement.tools.compare_prices import compare_bid_price
from mcp_servers.procurement.tools.flag_supplier_risk import (
    flag_supplier_risk_record,
)
from mcp_servers.procurement.tools.load_tender import load_tender_record


PROJECT_ROOT = Path(__file__).resolve().parents[3]
REPORTS_DIR = PROJECT_ROOT / "reports"


def _report_path_for_output(report_path: Path) -> str:
    try:
        return str(report_path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(report_path)


def generate_evaluation_report_file(
    tender_id: str,
    bid_id: str,
    approved_by: str,
) -> dict[str, Any]:
    """
    Generate a sourced draft evaluation report for committee review.

    Human approval is required before the file is written.
    This function never awards or rejects a tender.
    """

    approved_by = approved_by.strip()

    if not approved_by:
        raise PermissionError(
            "Human approval is required before generating the evaluation report."
        )

    tender = load_tender_record(tender_id)
    compliance = check_bid_compliance_record(tender_id, bid_id)
    price_analysis = compare_bid_price(bid_id)
    supplier_risk = flag_supplier_risk_record(bid_id)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    safe_bid_id = "".join(
        character
        for character in bid_id
        if character.isalnum() or character in {"-", "_"}
    )

    report_path = REPORTS_DIR / f"{safe_bid_id}_evaluation_report.md"
    generated_at = datetime.now(timezone.utc).isoformat()

    compliance_lines = []

    for check in compliance["checks"]:
        mark = "PASS" if check["passed"] else "FLAG"

        compliance_lines.append(
            f"- [{mark}] {check['finding']} "
            f"(Sources: {', '.join(check['sources'])})"
        )

    price_evidence_lines = []

    for award in price_analysis["evidence"]:
        price_evidence_lines.append(
            "- "
            f"{award['ocid']} | "
            f"{award['award_id']} | "
            f"{award['amount']} {award['currency']} | "
            f"{award['source_file']}"
        )

    supplier_flag_lines = []

    if supplier_risk["flags"]:
        for flag in supplier_risk["flags"]:
            supplier_flag_lines.append(
                "- "
                f"[{flag['severity']}] "
                f"{flag['finding']} "
                f"(Sources: {', '.join(flag['sources'])})"
            )
    else:
        supplier_flag_lines.append(
            "- No supplier-data inconsistency flags were identified "
            "in the available dataset."
        )

    report = f"""# TenderGuard Africa Evaluation Report

## Review Status

DRAFT FOR HUMAN PROCUREMENT COMMITTEE REVIEW

TenderGuard Africa provides decision support only.
It does not award, reject, disqualify, or select a winning bidder.

## Tender

- Tender ID: {tender_id}
- Title: {tender.get('title')}
- Procuring Entity: {tender.get('procuring_entity')}
- Tender Source: {tender.get('source_file')}

## Bid

- Bid ID: {bid_id}
- Supplier: {compliance.get('supplier')}
- Compliance Status: {compliance.get('status')}

## Compliance Findings

{chr(10).join(compliance_lines)}

## Price Analysis

- Submitted Price: {price_analysis.get('bid_price')} {price_analysis.get('currency')}
- Historical Sample Size: {price_analysis['historical_statistics']['sample_size']}
- Historical Median: {price_analysis['historical_statistics']['median']} {price_analysis.get('currency')}
- Deviation from Median: {price_analysis.get('deviation_percentage')}%
- Price Risk Level: {price_analysis.get('risk_level')}

Finding:

{price_analysis.get('finding')}

## Historical Price Evidence

{chr(10).join(price_evidence_lines)}

## Supplier Data Review

- Risk Level: {supplier_risk.get('risk_level')}
- Historical Records Checked: {supplier_risk.get('historical_records_checked')}

{chr(10).join(supplier_flag_lines)}

Supplier-risk flags represent data inconsistencies only.
They are not findings of fraud or misconduct.

## Human-in-the-Loop Handoff

Report generation approved by: {approved_by}

Generated at: {generated_at}

The authorised procurement committee must independently review
the evidence and make the final procurement decision.
"""

    report_path.write_text(report, encoding="utf-8")

    return {
        "tender_id": tender_id,
        "bid_id": bid_id,
        "report_path": _report_path_for_output(report_path),
        "report_status": "DRAFT_FOR_COMMITTEE_REVIEW",
        "approved_by": approved_by,
        "generated_at": generated_at,
        "final_decision_made": False,
    }