import pytest

from app.agent.mcp_client import (
    call_procurement_tool,
    list_procurement_tools,
)


@pytest.mark.asyncio
async def test_procurement_mcp_exposes_required_tools():
    tools = await list_procurement_tools()

    assert "load_tender" in tools
    assert "check_bid_compliance" in tools
    assert "compare_prices" in tools
    assert "flag_supplier_risk" in tools
    assert "generate_evaluation_report" in tools


@pytest.mark.asyncio
async def test_agent_can_call_mcp_load_tender():
    result = await call_procurement_tool(
        "load_tender",
        {
            "tender_id": "TG-DEMO-001",
        },
    )

    assert result["tender_id"] == "TG-DEMO-001"