def test_project_environment():
    import mcp
    import langgraph
    import pydantic
    import httpx
    import pypdf

    assert mcp is not None
    assert langgraph is not None
    assert pydantic is not None
    assert httpx is not None
    assert pypdf is not None
