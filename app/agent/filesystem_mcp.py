from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import TextContent


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = (PROJECT_ROOT / "reports").resolve()


def _server_parameters() -> StdioServerParameters:
    return StdioServerParameters(
        command="cmd",
        args=[
            "/c",
            "npx",
            "-y",
            "@modelcontextprotocol/server-filesystem",
            str(REPORTS_DIR),
        ],
    )


async def list_filesystem_tools() -> list[str]:
    async with stdio_client(_server_parameters()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            response = await session.list_tools()

            return [
                tool.name
                for tool in response.tools
            ]


async def list_allowed_directories() -> str:
    async with stdio_client(_server_parameters()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                "list_allowed_directories",
                arguments={},
            )

            return "\n".join(
                block.text
                for block in result.content
                if isinstance(block, TextContent)
            )


async def list_reports_directory() -> str:
    async with stdio_client(_server_parameters()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                "list_directory",
                arguments={
                    "path": str(REPORTS_DIR),
                },
            )

            return "\n".join(
                block.text
                for block in result.content
                if isinstance(block, TextContent)
            )


async def read_report(report_path: str) -> str:
    requested_path = (PROJECT_ROOT / report_path).resolve()

    if REPORTS_DIR not in requested_path.parents:
        raise PermissionError(
            "Borrowed filesystem MCP may only access the reports directory."
        )

    async with stdio_client(_server_parameters()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                "read_text_file",
                arguments={
                    "path": str(requested_path),
                },
            )

            return "\n".join(
                block.text
                for block in result.content
                if isinstance(block, TextContent)
            )