from typing import Any, TypedDict


class TenderEvaluationState(TypedDict, total=False):
    tender_id: str
    bid_id: str

    plan: list[str]
    plan_rationale: str
    completed_tools: list[str]

    tender: dict[str, Any]
    compliance: dict[str, Any]
    price_analysis: dict[str, Any]
    supplier_risk: dict[str, Any]

    decision_support: dict[str, Any]

    status: str