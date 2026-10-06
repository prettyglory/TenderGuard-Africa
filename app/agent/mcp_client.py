import json
import sys
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import TextContent


async def call_procurement_tool(
    tool_name: str,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """
    Call the TenderGuard Procurement MCP server over stdio.

    The agent does not import procurement tool functions directly.
    Every tool execution crosses the MCP client/server boundary.
    """

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "mcp_servers.procurement.server",
        ],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                tool_name,
                arguments=arguments,
            )

            if result.is_error:
                messages = [
                    block.text
                    for block in result.content
                    if isinstance(block, TextContent)
                ]

                raise RuntimeError(
                    "; ".join(messages)
                    or f"MCP tool '{tool_name}' failed"
                )

            if result.structured_content is not None:
                return dict(result.structured_content)

            text_blocks = [
                block.text
                for block in result.content
                if isinstance(block, TextContent)
            ]

            if not text_blocks:
                return {}

            text = "\n".join(text_blocks)

            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                return {"text": text}

            if isinstance(parsed, dict):
                return parsed

            return {"result": parsed}


async def list_procurement_tools() -> list[str]:
    """Return tool names exposed by the procurement MCP server."""

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "mcp_servers.procurement.server",
        ],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            response = await session.list_tools()

            return [
                tool.name
                for tool in response.tools
            ]