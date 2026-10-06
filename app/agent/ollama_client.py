from typing import Any

import httpx
from pydantic import BaseModel, Field


OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "qwen3:1.7b"


class EvaluationPlan(BaseModel):
    tool_sequence: list[str] = Field(
        description="Ordered list of procurement MCP tools to execute."
    )
    rationale: str


class EvidenceSummary(BaseModel):
    review_priority: str
    summary: str
    key_findings: list[str]
    human_committee_required: bool = True
    final_award_decision: None = None


async def _chat_structured(
    *,
    system_prompt: str,
    user_prompt: str,
    schema: dict[str, Any],
) -> dict[str, Any]:
    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "think": False,
        "format": schema,
        "options": {
            "temperature": 0
        },
        "messages": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            OLLAMA_URL,
            json=payload,
        )
        response.raise_for_status()

        data = response.json()
        content = data["message"]["content"]

    return content


async def plan_procurement_workflow(
    tender_id: str,
    bid_id: str,
) -> EvaluationPlan:
    allowed_tools = [
        "load_tender",
        "check_bid_compliance",
        "compare_prices",
        "flag_supplier_risk",
    ]

    system_prompt = """
You are TenderGuard Africa's procurement workflow planner.

You provide decision support only.

You must never award, reject, disqualify, or select a winning supplier.

Plan an evidence-first tender evaluation using only the allowed MCP tools.

The final workflow must stop for human committee review.
"""

    user_prompt = f"""
Tender ID: {tender_id}
Bid ID: {bid_id}

Allowed MCP tools:
{allowed_tools}

Return the safest logical tool order.

The workflow must:
1. establish tender context,
2. check mandatory compliance,
3. compare price evidence,
4. inspect supplier-data inconsistencies,
5. stop before any award decision.

Return JSON only.
"""

    raw = await _chat_structured(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        schema=EvaluationPlan.model_json_schema(),
    )

    plan = EvaluationPlan.model_validate_json(raw)

    invalid_tools = [
        tool
        for tool in plan.tool_sequence
        if tool not in allowed_tools
    ]

    if invalid_tools:
        raise ValueError(
            f"Open model planned unsupported tools: {invalid_tools}"
        )

    required = set(allowed_tools)

    if set(plan.tool_sequence) != required:
        raise ValueError(
            "Open model plan must contain each required evaluation tool exactly once."
        )

    if len(plan.tool_sequence) != len(required):
        raise ValueError(
            "Open model plan contains duplicate evaluation tools."
        )

    return plan


async def synthesize_procurement_evidence(
    compliance: dict[str, Any],
    price_analysis: dict[str, Any],
    supplier_risk: dict[str, Any],
) -> EvidenceSummary:
    system_prompt = """
You are TenderGuard Africa's evidence synthesis model.

Use only the evidence supplied to you.

Never invent missing facts.
Never accuse a supplier of fraud or misconduct.
Never make an award, rejection, or disqualification decision.

Your output is decision support for a human procurement committee.
"""

    user_prompt = f"""
COMPLIANCE EVIDENCE:
{compliance}

PRICE EVIDENCE:
{price_analysis}

SUPPLIER DATA EVIDENCE:
{supplier_risk}

Summarize the evidence.

review_priority must be either:
- STANDARD_REVIEW
- ATTENTION_REQUIRED

Use ATTENTION_REQUIRED when any evidence contains failed mandatory checks,
an elevated/high price flag, or elevated/high supplier-data risk.

The final award decision must remain null.

Return JSON only.
"""

    raw = await _chat_structured(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        schema=EvidenceSummary.model_json_schema(),
    )

    result = EvidenceSummary.model_validate_json(raw)

    result.human_committee_required = True
    result.final_award_decision = None

    return result