from typing import Any

from mcp.server import MCPServer

from mcp_servers.procurement.tools.check_bid_compliance import (
    check_bid_compliance_record,
)
from mcp_servers.procurement.tools.load_tender import load_tender_record


mcp = MCPServer("TenderGuard Procurement MCP")


@mcp.tool()
def load_tender(tender_id: str) -> dict[str, Any]:
    """Load and normalize a tender record with source information."""
    return load_tender_record(tender_id)


@mcp.tool()
def check_bid_compliance(
    tender_id: str,
    bid_id: str,
) -> dict[str, Any]:
    """Check a bid against mandatory tender requirements with sourced findings."""
    return check_bid_compliance_record(tender_id, bid_id)


if __name__ == "__main__":
    mcp.run(transport="stdio")