import json
from pathlib import Path
from statistics import median
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BID_DATA_DIR = PROJECT_ROOT / "data" / "synthetic_bids"
HISTORY_FILE = PROJECT_ROOT / "data" / "ocds" / "historical_awards.json"


def _load_bid(bid_id: str) -> tuple[dict[str, Any], Path]:
    for file_path in BID_DATA_DIR.glob("*.json"):
        with file_path.open("r", encoding="utf-8") as file:
            bid = json.load(file)

        if bid.get("bid_id") == bid_id:
            return bid, file_path

    raise FileNotFoundError(f"Bid '{bid_id}' was not found")


def _load_historical_awards() -> list[dict[str, Any]]:
    if not HISTORY_FILE.exists():
        raise FileNotFoundError("Historical award dataset was not found")

    with HISTORY_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return data.get("records", [])


def compare_bid_price(bid_id: str) -> dict[str, Any]:
    """
    Compare a submitted bid price with comparable historical award values.

    This tool provides decision support only. It does not recommend
    awarding or rejecting a tender.
    """

    bid, bid_path = _load_bid(bid_id)

    bid_price = bid.get("price", {}).get("amount")
    bid_currency = bid.get("price", {}).get("currency")

    if bid_price is None:
        raise ValueError(f"Bid '{bid_id}' has no price amount")

    if not bid_currency:
        raise ValueError(f"Bid '{bid_id}' has no price currency")

    records = _load_historical_awards()

    comparable_awards: list[dict[str, Any]] = []

    for record in records:
        award = record.get("award", {})
        value = award.get("value", {})

        amount = value.get("amount")
        currency = value.get("currency")

        if amount is None or currency != bid_currency:
            continue

        comparable_awards.append(
            {
                "ocid": record.get("ocid"),
                "award_id": award.get("id"),
                "supplier": award.get("supplier"),
                "award_date": award.get("date"),
                "amount": amount,
                "currency": currency,
                "source_file": str(
                    HISTORY_FILE.relative_to(PROJECT_ROOT)
                ),
            }
        )

    if not comparable_awards:
        raise ValueError(
            f"No historical awards found in currency '{bid_currency}'"
        )

    historical_values = [
        award["amount"]
        for award in comparable_awards
    ]

    historical_median = median(historical_values)
    historical_min = min(historical_values)
    historical_max = max(historical_values)

    difference = bid_price - historical_median

    if historical_median == 0:
        deviation_percentage = None
    else:
        deviation_percentage = round(
            (difference / historical_median) * 100,
            2,
        )

    if deviation_percentage is None:
        risk_level = "UNKNOWN"
        finding = (
            "Historical median is zero, so percentage deviation "
            "cannot be calculated."
        )
    elif deviation_percentage > 30:
        risk_level = "HIGH"
        finding = (
            f"Bid price is {deviation_percentage}% above the "
            "median historical award value."
        )
    elif deviation_percentage > 15:
        risk_level = "ELEVATED"
        finding = (
            f"Bid price is {deviation_percentage}% above the "
            "median historical award value."
        )
    elif deviation_percentage < -30:
        risk_level = "LOW_PRICE_ANOMALY"
        finding = (
            f"Bid price is {abs(deviation_percentage)}% below the "
            "median historical award value."
        )
    else:
        risk_level = "NORMAL_RANGE"
        finding = (
            f"Bid price is within 15% of the median historical "
            f"award value ({deviation_percentage}% deviation)."
        )

    return {
        "bid_id": bid_id,
        "supplier": bid.get("supplier", {}).get("name"),
        "bid_price": bid_price,
        "currency": bid_currency,
        "historical_statistics": {
            "sample_size": len(historical_values),
            "minimum": historical_min,
            "median": historical_median,
            "maximum": historical_max,
        },
        "difference_from_median": difference,
        "deviation_percentage": deviation_percentage,
        "risk_level": risk_level,
        "finding": finding,
        "sources": {
            "bid": str(bid_path.relative_to(PROJECT_ROOT)),
            "historical_awards": str(
                HISTORY_FILE.relative_to(PROJECT_ROOT)
            ),
        },
        "evidence": comparable_awards,
        "decision_note": (
            "This finding is decision support only. "
            "A human procurement committee makes the final decision."
        ),
    }