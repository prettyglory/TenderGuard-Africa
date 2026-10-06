import pytest

from app.agent.filesystem_mcp import (
    list_allowed_directories,
    list_filesystem_tools,
    list_reports_directory,
)


@pytest.mark.asyncio
async def test_borrowed_filesystem_mcp_exposes_tools():
    tools = await list_filesystem_tools()

    assert "read_text_file" in tools
    assert "list_directory" in tools
    assert "list_allowed_directories" in tools


@pytest.mark.asyncio
async def test_borrowed_filesystem_mcp_is_scoped_to_reports():
    directories = await list_allowed_directories()

    normalized = directories.replace("\\", "/").lower()

    assert "tenderguard-africa/reports" in normalized


@pytest.mark.asyncio
async def test_borrowed_filesystem_mcp_can_list_reports():
    result = await list_reports_directory()

    assert isinstance(result, str)