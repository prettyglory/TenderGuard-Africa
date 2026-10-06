import pytest

from app.agent.workflow import procurement_agent


@pytest.mark.asyncio
async def test_alpha_bid_reaches_human_review():
    result = await procurement_agent.ainvoke(
        {
            "tender_id": "TG-DEMO-001",
            "bid_id": "BID-ALPHA-001",
            "status": "STARTED",
        }
    )

    assert result["status"] == "AWAITING_HUMAN_REVIEW"

    assert (
        result["decision_support"]["human_committee_required"]
        is True
    )

    assert (
        result["decision_support"]["final_award_decision"]
        is None
    )

    assert result["compliance"]["status"] == "COMPLIANT"


@pytest.mark.asyncio
async def test_beta_bid_surfaces_attention_without_awarding():
    result = await procurement_agent.ainvoke(
        {
            "tender_id": "TG-DEMO-001",
            "bid_id": "BID-BETA-001",
            "status": "STARTED",
        }
    )

    assert result["status"] == "AWAITING_HUMAN_REVIEW"

    assert (
        result["decision_support"]["review_priority"]
        == "ATTENTION_REQUIRED"
    )

    assert (
        result["decision_support"]["final_award_decision"]
        is None
    )

    assert result["decision_support"]["reasons"]