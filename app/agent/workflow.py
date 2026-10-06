from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy

from app.agent.mcp_client import call_procurement_tool
from app.agent.state import TenderEvaluationState


async def plan_evaluation(
    state: TenderEvaluationState,
) -> dict[str, Any]:
    """
    Build the controlled evaluation plan.

    The open-weights LLM planner will be added in the next implementation
    stage. For now this establishes the audited orchestration structure.
    """

    return {
        "plan": [
            "Load and normalize tender evidence",
            "Check mandatory bid compliance",
            "Compare bid price with historical awards",
            "Review supplier-data inconsistencies",
            "Synthesize decision-support findings",
            "Stop for human procurement committee review",
        ],
        "status": "PLANNED",
    }


async def load_tender_node(
    state: TenderEvaluationState,
) -> dict[str, Any]:
    result = await call_procurement_tool(
        "load_tender",
        {
            "tender_id": state["tender_id"],
        },
    )

    return {
        "tender": result,
        "status": "TENDER_LOADED",
    }


async def compliance_node(
    state: TenderEvaluationState,
) -> dict[str, Any]:
    result = await call_procurement_tool(
        "check_bid_compliance",
        {
            "tender_id": state["tender_id"],
            "bid_id": state["bid_id"],
        },
    )

    return {
        "compliance": result,
        "status": "COMPLIANCE_CHECKED",
    }


async def price_node(
    state: TenderEvaluationState,
) -> dict[str, Any]:
    result = await call_procurement_tool(
        "compare_prices",
        {
            "bid_id": state["bid_id"],
        },
    )

    return {
        "price_analysis": result,
        "status": "PRICE_CHECKED",
    }


async def supplier_risk_node(
    state: TenderEvaluationState,
) -> dict[str, Any]:
    result = await call_procurement_tool(
        "flag_supplier_risk",
        {
            "bid_id": state["bid_id"],
        },
    )

    return {
        "supplier_risk": result,
        "status": "SUPPLIER_REVIEWED",
    }


async def synthesize_findings(
    state: TenderEvaluationState,
) -> dict[str, Any]:
    """
    Synthesize tool evidence without making an award decision.
    """

    reasons: list[str] = []

    compliance = state["compliance"]
    price_analysis = state["price_analysis"]
    supplier_risk = state["supplier_risk"]

    if compliance.get("status") != "COMPLIANT":
        reasons.append(
            "One or more mandatory compliance checks failed."
        )

    price_risk = price_analysis.get("risk_level")

    if price_risk not in {
        "NORMAL_RANGE",
        None,
    }:
        reasons.append(
            f"Price analysis requires review: {price_risk}."
        )

    supplier_level = supplier_risk.get("risk_level")

    if supplier_level not in {
        "LOW",
        None,
    }:
        reasons.append(
            f"Supplier-data review requires attention: {supplier_level}."
        )

    priority = (
        "ATTENTION_REQUIRED"
        if reasons
        else "STANDARD_REVIEW"
    )

    return {
        "decision_support": {
            "review_priority": priority,
            "reasons": reasons,
            "human_committee_required": True,
            "final_award_decision": None,
            "note": (
                "TenderGuard Africa provides decision support only. "
                "The procurement committee makes the final decision."
            ),
        },
        "status": "AWAITING_HUMAN_REVIEW",
    }


retry_policy = RetryPolicy(
    max_attempts=2,
)

builder = StateGraph(TenderEvaluationState)

builder.add_node(
    "plan",
    plan_evaluation,
)

builder.add_node(
    "load_tender",
    load_tender_node,
    retry_policy=retry_policy,
)

builder.add_node(
    "check_compliance",
    compliance_node,
    retry_policy=retry_policy,
)

builder.add_node(
    "compare_price",
    price_node,
    retry_policy=retry_policy,
)

builder.add_node(
    "supplier_risk",
    supplier_risk_node,
    retry_policy=retry_policy,
)

builder.add_node(
    "synthesize",
    synthesize_findings,
)

builder.add_edge(
    START,
    "plan",
)

builder.add_edge(
    "plan",
    "load_tender",
)

builder.add_edge(
    "load_tender",
    "check_compliance",
)

builder.add_edge(
    "check_compliance",
    "compare_price",
)

builder.add_edge(
    "compare_price",
    "supplier_risk",
)

builder.add_edge(
    "supplier_risk",
    "synthesize",
)

builder.add_edge(
    "synthesize",
    END,
)

procurement_agent = builder.compile(
    name="TenderGuard Procurement Agent"
)