import json
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
TENDER_DATA_DIR = PROJECT_ROOT / "data" / "ocds"
BID_DATA_DIR = PROJECT_ROOT / "data" / "synthetic_bids"


def _load_tender(tender_id: str) -> tuple[dict[str, Any], Path]:
    for file_path in TENDER_DATA_DIR.glob("*.json"):
        with file_path.open("r", encoding="utf-8") as file:
            record = json.load(file)

        tender = record.get("tender", {})

        if tender.get("id") == tender_id:
            return tender, file_path

    raise FileNotFoundError(f"Tender '{tender_id}' was not found")


def _load_bid(bid_id: str) -> tuple[dict[str, Any], Path]:
    for file_path in BID_DATA_DIR.glob("*.json"):
        with file_path.open("r", encoding="utf-8") as file:
            bid = json.load(file)

        if bid.get("bid_id") == bid_id:
            return bid, file_path

    raise FileNotFoundError(f"Bid '{bid_id}' was not found")


def check_bid_compliance_record(
    tender_id: str,
    bid_id: str,
) -> dict[str, Any]:
    """Check a synthetic bid against mandatory tender compliance requirements."""

    tender, tender_path = _load_tender(tender_id)
    bid, bid_path = _load_bid(bid_id)

    if bid.get("tender_id") != tender_id:
        raise ValueError(
            f"Bid '{bid_id}' does not belong to tender '{tender_id}'"
        )

    tender_source = str(tender_path.relative_to(PROJECT_ROOT))
    bid_source = str(bid_path.relative_to(PROJECT_ROOT))

    sources = [tender_source, bid_source]

    checks: list[dict[str, Any]] = []

    deadline_raw = tender.get("submissionDeadline")
    submitted_raw = bid.get("submitted_at")

    if deadline_raw and submitted_raw:
        deadline = datetime.fromisoformat(deadline_raw)
        submitted_at = datetime.fromisoformat(submitted_raw)

        passed = submitted_at <= deadline

        checks.append(
            {
                "criterion": "SUBMISSION_DEADLINE",
                "passed": passed,
                "finding": (
                    "Bid was submitted before or at the deadline."
                    if passed
                    else "Bid was submitted after the tender deadline."
                ),
                "sources": sources,
            }
        )

    submitted_documents = {
        document.get("code")
        for document in bid.get("documents", [])
        if document.get("code")
    }

    for requirement in tender.get("requiredDocuments", []):
        code = requirement.get("code")
        name = requirement.get("name")

        passed = code in submitted_documents

        checks.append(
            {
                "criterion": code,
                "passed": passed,
                "finding": (
                    f"Required document present: {name}."
                    if passed
                    else f"Required document missing: {name}."
                ),
                "sources": sources,
            }
        )

    declarations = bid.get("declarations", {})

    for requirement in tender.get("eligibilityRequirements", []):
        code = requirement.get("code")
        description = requirement.get("description")

        passed = declarations.get(code) is True

        checks.append(
            {
                "criterion": code,
                "passed": passed,
                "finding": (
                    f"Eligibility requirement satisfied: {description}"
                    if passed
                    else f"Eligibility requirement not satisfied: {description}"
                ),
                "sources": sources,
            }
        )

    failed_checks = [check for check in checks if not check["passed"]]
    passed_checks = [check for check in checks if check["passed"]]

    return {
        "tender_id": tender_id,
        "bid_id": bid_id,
        "supplier": bid.get("supplier", {}).get("name"),
        "status": "COMPLIANT" if not failed_checks else "NON_COMPLIANT",
        "summary": {
            "total_checks": len(checks),
            "passed_checks": len(passed_checks),
            "failed_checks": len(failed_checks),
        },
        "checks": checks,
        "source_files": sources,
    }