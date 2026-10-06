from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy

from app.agent.mcp_client import call_procurement_tool
from app.agent.ollama_client import (
    plan_procurement_workflow,
    synthesize_procurement_evidence,
)
from app.agent.state import TenderEvaluationState


async def plan_evaluation(
    state: TenderEvaluationState,
) -> dict[str, Any]:
    plan = await plan_procurement_workflow(
        state["tender_id"],
        state["bid_id"],
    )

    return {
        "plan": plan.tool_sequence,
        "plan_rationale": plan.rationale,
        "completed_tools": [],
        "status": "PLANNED_BY_OPEN_MODEL",
    }


def _mark_complete(
    state: TenderEvaluationState,
    tool_name: str,
) -> list[str]:
    return [
        *state.get("completed_tools", []),
        tool_name,
    ]


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
        "completed_tools": _mark_complete(
            state,
            "load_tender",
        ),
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
        "completed_tools": _mark_complete(
            state,
            "check_bid_compliance",
        ),
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
        "completed_tools": _mark_complete(
            state,
            "compare_prices",
        ),
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
        "completed_tools": _mark_complete(
            state,
            "flag_supplier_risk",
        ),
        "status": "SUPPLIER_REVIEWED",
    }


def route_next(
    state: TenderEvaluationState,
) -> str:
    plan = state["plan"]
    completed = state.get("completed_tools", [])

    for tool_name in plan:
        if tool_name not in completed:
            return tool_name

    return "synthesize"


async def synthesize_findings(
    state: TenderEvaluationState,
) -> dict[str, Any]:
    result = await synthesize_procurement_evidence(
        state["compliance"],
        state["price_analysis"],
        state["supplier_risk"],
    )

    return {
        "decision_support": result.model_dump(),
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
    "check_bid_compliance",
    compliance_node,
    retry_policy=retry_policy,
)

builder.add_node(
    "compare_prices",
    price_node,
    retry_policy=retry_policy,
)

builder.add_node(
    "flag_supplier_risk",
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

builder.add_conditional_edges(
    "plan",
    route_next,
    {
        "load_tender": "load_tender",
        "check_bid_compliance": "check_bid_compliance",
        "compare_prices": "compare_prices",
        "flag_supplier_risk": "flag_supplier_risk",
        "synthesize": "synthesize",
    },
)

for node_name in [
    "load_tender",
    "check_bid_compliance",
    "compare_prices",
    "flag_supplier_risk",
]:
    builder.add_conditional_edges(
        node_name,
        route_next,
        {
            "load_tender": "load_tender",
            "check_bid_compliance": "check_bid_compliance",
            "compare_prices": "compare_prices",
            "flag_supplier_risk": "flag_supplier_risk",
            "synthesize": "synthesize",
        },
    )

builder.add_edge(
    "synthesize",
    END,
)

procurement_agent = builder.compile(
    name="TenderGuard Procurement Agent"
)