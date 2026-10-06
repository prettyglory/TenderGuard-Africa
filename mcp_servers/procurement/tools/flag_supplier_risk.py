import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BID_DATA_DIR = PROJECT_ROOT / "data" / "synthetic_bids"
SUPPLIER_HISTORY_FILE = PROJECT_ROOT / "data" / "ocds" / "supplier_history.json"


def _load_bid(bid_id: str) -> tuple[dict[str, Any], Path]:
    for file_path in BID_DATA_DIR.glob("*.json"):
        with file_path.open("r", encoding="utf-8") as file:
            bid = json.load(file)

        if bid.get("bid_id") == bid_id:
            return bid, file_path

    raise FileNotFoundError(f"Bid '{bid_id}' was not found")


def _load_supplier_history() -> list[dict[str, Any]]:
    if not SUPPLIER_HISTORY_FILE.exists():
        raise FileNotFoundError("Supplier history dataset was not found")

    with SUPPLIER_HISTORY_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return data.get("records", [])


def flag_supplier_risk_record(bid_id: str) -> dict[str, Any]:
    """
    Identify supplier-data inconsistencies that require human review.

    This tool does not accuse a supplier of wrongdoing and does not make
    procurement award decisions.
    """

    bid, bid_path = _load_bid(bid_id)

    supplier = bid.get("supplier") or {}
    supplier_name = supplier.get("name")
    supplier_identifier = supplier.get("identifier")

    flags: list[dict[str, Any]] = []
    history = _load_supplier_history()

    bid_source = str(bid_path.relative_to(PROJECT_ROOT))
    history_source = str(
        SUPPLIER_HISTORY_FILE.relative_to(PROJECT_ROOT)
    )

    if not supplier_identifier:
        flags.append(
            {
                "code": "MISSING_SUPPLIER_IDENTIFIER",
                "severity": "HIGH",
                "finding": "Supplier identifier is missing from the bid record.",
                "sources": [bid_source],
            }
        )

    matching_identifier_records = [
        record
        for record in history
        if record.get("supplier_identifier") == supplier_identifier
    ]

    matching_name_records = [
        record
        for record in history
        if record.get("supplier_name") == supplier_name
    ]

    if supplier_identifier and matching_identifier_records:
        names_for_identifier = {
            record.get("supplier_name")
            for record in matching_identifier_records
            if record.get("supplier_name")
        }

        if len(names_for_identifier) > 1:
            flags.append(
                {
                    "code": "IDENTIFIER_NAME_INCONSISTENCY",
                    "severity": "MEDIUM",
                    "finding": (
                        "The same supplier identifier appears under multiple "
                        "supplier names in historical records."
                    ),
                    "sources": [bid_source, history_source],
                    "evidence": {
                        "supplier_identifier": supplier_identifier,
                        "observed_names": sorted(names_for_identifier),
                    },
                }
            )

    if supplier_name and matching_name_records:
        identifiers_for_name = {
            record.get("supplier_identifier")
            for record in matching_name_records
            if record.get("supplier_identifier")
        }

        if len(identifiers_for_name) > 1:
            flags.append(
                {
                    "code": "NAME_IDENTIFIER_INCONSISTENCY",
                    "severity": "MEDIUM",
                    "finding": (
                        "The supplier name appears with multiple identifiers "
                        "in historical records."
                    ),
                    "sources": [bid_source, history_source],
                    "evidence": {
                        "supplier_name": supplier_name,
                        "observed_identifiers": sorted(identifiers_for_name),
                    },
                }
            )

    relevant_history = matching_identifier_records or matching_name_records

    if not relevant_history:
        flags.append(
            {
                "code": "NO_MATCHING_HISTORY",
                "severity": "INFO",
                "finding": (
                    "No matching supplier award history was found in the "
                    "available dataset."
                ),
                "sources": [bid_source, history_source],
            }
        )

    severity_score = {
        "INFO": 0,
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3,
    }

    highest_score = max(
        (severity_score.get(flag["severity"], 0) for flag in flags),
        default=0,
    )

    risk_level = {
        0: "LOW",
        1: "LOW",
        2: "ELEVATED",
        3: "HIGH",
    }[highest_score]

    evidence_records = []

    for record in relevant_history:
        evidence_records.append(
            {
                "ocid": record.get("ocid"),
                "award_id": record.get("award_id"),
                "supplier_identifier": record.get("supplier_identifier"),
                "supplier_name": record.get("supplier_name"),
                "buyer": record.get("buyer"),
                "amount": record.get("amount"),
                "currency": record.get("currency"),
                "source_file": history_source,
            }
        )

    return {
        "bid_id": bid_id,
        "supplier_name": supplier_name,
        "supplier_identifier": supplier_identifier,
        "risk_level": risk_level,
        "flag_count": len(flags),
        "flags": flags,
        "historical_records_checked": len(relevant_history),
        "evidence": evidence_records,
        "source_files": [
            bid_source,
            history_source,
        ],
        "review_note": (
            "Risk flags indicate data inconsistencies only. "
            "They are not findings of fraud, misconduct, or disqualification. "
            "A human procurement officer must review the evidence."
        ),
    }