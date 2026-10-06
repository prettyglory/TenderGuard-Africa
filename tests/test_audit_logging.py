import json

import mcp_servers.procurement.audit as audit_module


def test_tool_call_is_logged(tmp_path, monkeypatch):
    audit_file = tmp_path / "audit_log.jsonl"

    monkeypatch.setattr(
        audit_module,
        "AUDIT_LOG_FILE",
        audit_file,
    )

    result = audit_module.execute_logged(
        tool_name="test_tool",
        inputs={"value": 10},
        action=lambda: {"result": 20},
        human_approver="Test Officer",
    )

    assert result == {"result": 20}
    assert audit_file.exists()

    record = json.loads(
        audit_file.read_text(encoding="utf-8").strip()
    )

    assert record["tool_name"] == "test_tool"
    assert record["inputs"]["value"] == 10
    assert record["output"]["result"] == 20
    assert record["status"] == "SUCCESS"
    assert record["human_approver"] == "Test Officer"
    assert record["timestamp"]