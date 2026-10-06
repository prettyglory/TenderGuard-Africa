from typing import Any

from mcp.server import MCPServer

from mcp_servers.procurement.tools.load_tender import load_tender_record


mcp = MCPServer("TenderGuard Procurement MCP")


@mcp.tool()
def load_tender(tender_id: str) -> dict[str, Any]:
    """Load and normalize a tender record with source information."""
    return load_tender_record(tender_id)


if __name__ == "__main__":
    mcp.run(transport="stdio")
