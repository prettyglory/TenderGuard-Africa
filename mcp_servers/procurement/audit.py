import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


PROJECT_ROOT = Path(__file__).resolve().parents[2]
AUDIT_LOG_FILE = PROJECT_ROOT / "reports" / "audit_log.jsonl"


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_tool_call(
    *,
    tool_name: str,
    inputs: dict[str, Any],
    output: Any,
    status: str,
    human_approver: str | None = None,
) -> None:
    AUDIT_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "timestamp": _timestamp(),
        "tool_name": tool_name,
        "inputs": inputs,
        "output": output,
        "status": status,
        "human_approver": human_approver,
    }

    with AUDIT_LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


def execute_logged(
    *,
    tool_name: str,
    inputs: dict[str, Any],
    action: Callable[[], Any],
    human_approver: str | None = None,
) -> Any:
    try:
        result = action()

        log_tool_call(
            tool_name=tool_name,
            inputs=inputs,
            output=result,
            status="SUCCESS",
            human_approver=human_approver,
        )

        return result

    except Exception as exc:
        log_tool_call(
            tool_name=tool_name,
            inputs=inputs,
            output={
                "error_type": type(exc).__name__,
                "message": str(exc),
            },
            status="FAILED",
            human_approver=human_approver,
        )

        raise