from typing import Any

from mcp.server import MCPServer

from mcp_servers.procurement.audit import execute_logged
from mcp_servers.procurement.tools.check_bid_compliance import (
    check_bid_compliance_record,
)
from mcp_servers.procurement.tools.compare_prices import compare_bid_price
from mcp_servers.procurement.tools.generate_evaluation_report import (
    generate_evaluation_report_file,
)
from mcp_servers.procurement.tools.load_tender import load_tender_record


mcp = MCPServer("TenderGuard Procurement MCP")


@mcp.tool()
def load_tender(tender_id: str) -> dict[str, Any]:
    """Load and normalize a tender record with source information."""

    return execute_logged(
        tool_name="load_tender",
        inputs={"tender_id": tender_id},
        action=lambda: load_tender_record(tender_id),
    )


@mcp.tool()
def check_bid_compliance(
    tender_id: str,
    bid_id: str,
) -> dict[str, Any]:
    """Check a bid against mandatory tender requirements with sourced findings."""

    return execute_logged(
        tool_name="check_bid_compliance",
        inputs={
            "tender_id": tender_id,
            "bid_id": bid_id,
        },
        action=lambda: check_bid_compliance_record(
            tender_id,
            bid_id,
        ),
    )


@mcp.tool()
def compare_prices(bid_id: str) -> dict[str, Any]:
    """Compare a bid price with historical awards and return sourced findings."""

    return execute_logged(
        tool_name="compare_prices",
        inputs={"bid_id": bid_id},
        action=lambda: compare_bid_price(bid_id),
    )


@mcp.tool()
def generate_evaluation_report(
    tender_id: str,
    bid_id: str,
    approved_by: str,
) -> dict[str, Any]:
    """
    Generate a sourced evaluation report after named human approval.

    This tool does not award or reject the tender.
    """

    return execute_logged(
        tool_name="generate_evaluation_report",
        inputs={
            "tender_id": tender_id,
            "bid_id": bid_id,
        },
        human_approver=approved_by,
        action=lambda: generate_evaluation_report_file(
            tender_id,
            bid_id,
            approved_by,
        ),
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")