import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
OCDS_DATA_DIR = PROJECT_ROOT / "data" / "ocds"


def load_tender_record(tender_id: str) -> dict[str, Any]:
    tender_id = tender_id.strip()

    if not tender_id:
        raise ValueError("tender_id cannot be empty")

    for file_path in OCDS_DATA_DIR.glob("*.json"):
        with file_path.open("r", encoding="utf-8") as file:
            record = json.load(file)

        tender = record.get("tender", {})

        if tender.get("id") != tender_id:
            continue

        value = tender.get("value") or {}
        procuring_entity = tender.get("procuringEntity") or {}

        return {
            "ocid": record.get("ocid"),
            "tender_id": tender.get("id"),
            "title": tender.get("title"),
            "description": tender.get("description"),
            "status": tender.get("status"),
            "procurement_method": tender.get("procurementMethod"),
            "amount": value.get("amount"),
            "currency": value.get("currency"),
            "procuring_entity": procuring_entity.get("name"),
            "source_file": str(file_path.relative_to(PROJECT_ROOT)),
        }

    raise FileNotFoundError(f"Tender '{tender_id}' was not found")