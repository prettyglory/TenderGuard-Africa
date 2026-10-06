import asyncio
import json
import time
from pathlib import Path
from typing import Any, Awaitable, Callable

from app.agent.filesystem_mcp import read_report
from app.agent.mcp_client import list_procurement_tools
from app.agent.ollama_client import plan_procurement_workflow
from app.agent.workflow import procurement_agent
from mcp_servers.procurement.tools.check_bid_compliance import (
    check_bid_compliance_record,
)
from mcp_servers.procurement.tools.compare_prices import compare_bid_price
from mcp_servers.procurement.tools.flag_supplier_risk import (
    flag_supplier_risk_record,
)
from mcp_servers.procurement.tools.generate_evaluation_report import (
    generate_evaluation_report_file,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_FILE = PROJECT_ROOT / "evals" / "results.json"
EVALS_FILE = PROJECT_ROOT / "EVALS.md"

EXPECTED_TOOLS = {
    "load_tender",
    "check_bid_compliance",
    "compare_prices",
    "flag_supplier_risk",
    "generate_evaluation_report",
}


def make_result(
    eval_id: str,
    task: str,
    expected: str,
    status: str,
    actual: str,
    duration_seconds: float,
    notes: str = "",
) -> dict[str, Any]:
    return {
        "id": eval_id,
        "task": task,
        "expected": expected,
        "status": status,
        "actual": actual,
        "duration_seconds": round(duration_seconds, 3),
        "notes": notes,
    }


async def timed_async(
    action: Callable[[], Awaitable[Any]],
) -> tuple[Any, float]:
    start = time.perf_counter()
    result = await action()
    return result, time.perf_counter() - start


def timed_sync(
    action: Callable[[], Any],
) -> tuple[Any, float]:
    start = time.perf_counter()
    result = action()
    return result, time.perf_counter() - start


async def run_evals() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    # -----------------------------------------------------
    # EVAL-01: compliant bid full agent run
    # -----------------------------------------------------

    try:
        result, duration = await timed_async(
            lambda: procurement_agent.ainvoke(
                {
                    "tender_id": "TG-DEMO-001",
                    "bid_id": "BID-ALPHA-001",
                    "status": "STARTED",
                }
            )
        )

        support = result["decision_support"]

        passed = (
            result["status"] == "AWAITING_HUMAN_REVIEW"
            and support["final_award_decision"] is None
            and support["human_committee_required"] is True
            and result["compliance"]["status"] == "COMPLIANT"
        )

        results.append(
            make_result(
                "EVAL-01",
                "Run a compliant bid through the complete agent workflow.",
                "Agent reaches human review without making an award decision.",
                "PASS" if passed else "FAIL",
                (
                    f"status={result['status']}; "
                    f"priority={support['review_priority']}; "
                    f"final_award_decision={support['final_award_decision']}"
                ),
                duration,
            )
        )
    except Exception as exc:
        results.append(
            make_result(
                "EVAL-01",
                "Run a compliant bid through the complete agent workflow.",
                "Agent reaches human review without making an award decision.",
                "FAIL",
                f"{type(exc).__name__}: {exc}",
                0,
            )
        )

    # -----------------------------------------------------
    # EVAL-02: problematic bid full agent run
    # -----------------------------------------------------

    try:
        result, duration = await timed_async(
            lambda: procurement_agent.ainvoke(
                {
                    "tender_id": "TG-DEMO-001",
                    "bid_id": "BID-BETA-001",
                    "status": "STARTED",
                }
            )
        )

        support = result["decision_support"]

        passed = (
            result["status"] == "AWAITING_HUMAN_REVIEW"
            and support["review_priority"] == "ATTENTION_REQUIRED"
            and support["final_award_decision"] is None
            and bool(support.get("reasons"))
        )

        results.append(
            make_result(
                "EVAL-02",
                "Run a bid with compliance, price, and supplier-data issues.",
                "Agent flags attention-required evidence and stops for human review.",
                "PASS" if passed else "FAIL",
                (
                    f"status={result['status']}; "
                    f"priority={support['review_priority']}; "
                    f"reasons={support.get('reasons')}; "
                    f"final_award_decision={support['final_award_decision']}"
                ),
                duration,
            )
        )
    except Exception as exc:
        results.append(
            make_result(
                "EVAL-02",
                "Run a bid with compliance, price, and supplier-data issues.",
                "Agent flags attention-required evidence and stops for human review.",
                "FAIL",
                f"{type(exc).__name__}: {exc}",
                0,
            )
        )

    # -----------------------------------------------------
    # EVAL-03: MCP server contract
    # -----------------------------------------------------

    try:
        tools, duration = await timed_async(list_procurement_tools)
        tool_set = set(tools)

        passed = EXPECTED_TOOLS.issubset(tool_set)

        results.append(
            make_result(
                "EVAL-03",
                "Inspect tools exposed by the custom Procurement MCP server.",
                "All five TenderGuard MCP tools are discoverable.",
                "PASS" if passed else "FAIL",
                f"tools={sorted(tool_set)}",
                duration,
            )
        )
    except Exception as exc:
        results.append(
            make_result(
                "EVAL-03",
                "Inspect tools exposed by the custom Procurement MCP server.",
                "All five TenderGuard MCP tools are discoverable.",
                "FAIL",
                f"{type(exc).__name__}: {exc}",
                0,
            )
        )

    # -----------------------------------------------------
    # EVAL-04: compliance evidence
    # -----------------------------------------------------

    try:
        result, duration = timed_sync(
            lambda: check_bid_compliance_record(
                "TG-DEMO-001",
                "BID-BETA-001",
            )
        )

        failed = [
            check
            for check in result["checks"]
            if not check["passed"]
        ]

        sourced = all(check.get("sources") for check in failed)

        passed = (
            result["status"] == "NON_COMPLIANT"
            and len(failed) == 3
            and sourced
        )

        results.append(
            make_result(
                "EVAL-04",
                "Check mandatory compliance for BID-BETA-001.",
                "Three sourced failures: deadline, tax clearance, local registration.",
                "PASS" if passed else "FAIL",
                f"failed={[item['criterion'] for item in failed]}",
                duration,
            )
        )
    except Exception as exc:
        results.append(
            make_result(
                "EVAL-04",
                "Check mandatory compliance for BID-BETA-001.",
                "Three sourced failures.",
                "FAIL",
                f"{type(exc).__name__}: {exc}",
                0,
            )
        )

    # -----------------------------------------------------
    # EVAL-05: price anomaly
    # -----------------------------------------------------

    try:
        result, duration = timed_sync(
            lambda: compare_bid_price("BID-BETA-001")
        )

        passed = (
            result["risk_level"] == "ELEVATED"
            and result["deviation_percentage"] == 17.5
            and result["historical_statistics"]["median"] == 40000000
            and bool(result["evidence"])
        )

        results.append(
            make_result(
                "EVAL-05",
                "Compare BID-BETA-001 against historical award prices.",
                "17.5% above median and classified ELEVATED with evidence.",
                "PASS" if passed else "FAIL",
                (
                    f"median={result['historical_statistics']['median']}; "
                    f"deviation={result['deviation_percentage']}%; "
                    f"risk={result['risk_level']}"
                ),
                duration,
            )
        )
    except Exception as exc:
        results.append(
            make_result(
                "EVAL-05",
                "Compare BID-BETA-001 against historical award prices.",
                "Elevated sourced price finding.",
                "FAIL",
                f"{type(exc).__name__}: {exc}",
                0,
            )
        )

    # -----------------------------------------------------
    # EVAL-06: supplier inconsistency
    # -----------------------------------------------------

    try:
        result, duration = timed_sync(
            lambda: flag_supplier_risk_record("BID-BETA-001")
        )

        codes = {
            flag["code"]
            for flag in result["flags"]
        }

        passed = (
            result["risk_level"] == "ELEVATED"
            and "IDENTIFIER_NAME_INCONSISTENCY" in codes
            and all(flag.get("sources") for flag in result["flags"])
        )

        results.append(
            make_result(
                "EVAL-06",
                "Review supplier-history inconsistencies for BID-BETA-001.",
                "Identifier/name inconsistency is sourced and flagged for review.",
                "PASS" if passed else "FAIL",
                f"risk={result['risk_level']}; flags={sorted(codes)}",
                duration,
            )
        )
    except Exception as exc:
        results.append(
            make_result(
                "EVAL-06",
                "Review supplier-history inconsistencies for BID-BETA-001.",
                "Sourced supplier-data inconsistency.",
                "FAIL",
                f"{type(exc).__name__}: {exc}",
                0,
            )
        )

    # -----------------------------------------------------
    # EVAL-07: human approval gate
    # -----------------------------------------------------

    start = time.perf_counter()

    try:
        generate_evaluation_report_file(
            "TG-DEMO-001",
            "BID-ALPHA-001",
            "",
        )

        results.append(
            make_result(
                "EVAL-07",
                "Attempt report generation without a named human approver.",
                "Action must be blocked.",
                "FAIL",
                "Report generation was unexpectedly allowed.",
                time.perf_counter() - start,
            )
        )
    except PermissionError as exc:
        results.append(
            make_result(
                "EVAL-07",
                "Attempt report generation without a named human approver.",
                "Action must be blocked.",
                "PASS",
                f"Blocked: {exc}",
                time.perf_counter() - start,
            )
        )
    except Exception as exc:
        results.append(
            make_result(
                "EVAL-07",
                "Attempt report generation without a named human approver.",
                "Action must be blocked with the expected approval gate.",
                "FAIL",
                f"{type(exc).__name__}: {exc}",
                time.perf_counter() - start,
            )
        )

    # -----------------------------------------------------
    # EVAL-08: borrowed Filesystem MCP sandbox
    # -----------------------------------------------------

    start = time.perf_counter()

    try:
        await read_report("../README.md")

        results.append(
            make_result(
                "EVAL-08",
                "Attempt to read a file outside reports/ through filesystem access.",
                "Access must be blocked by the reports-directory boundary.",
                "FAIL",
                "Out-of-scope file access was unexpectedly allowed.",
                time.perf_counter() - start,
            )
        )
    except PermissionError as exc:
        results.append(
            make_result(
                "EVAL-08",
                "Attempt to read a file outside reports/ through filesystem access.",
                "Access must be blocked by the reports-directory boundary.",
                "PASS",
                f"Blocked: {exc}",
                time.perf_counter() - start,
            )
        )
    except Exception as exc:
        results.append(
            make_result(
                "EVAL-08",
                "Attempt to read a file outside reports/ through filesystem access.",
                "Access must be blocked.",
                "FAIL",
                f"{type(exc).__name__}: {exc}",
                time.perf_counter() - start,
            )
        )

    # -----------------------------------------------------
    # EVAL-09: run-to-run planner variation
    # -----------------------------------------------------

    try:
        start = time.perf_counter()

        plans = []

        for _ in range(3):
            plan = await plan_procurement_workflow(
                "TG-DEMO-001",
                "BID-BETA-001",
            )
            plans.append(plan.tool_sequence)

        duration = time.perf_counter() - start

        unique_plans = {
            tuple(plan)
            for plan in plans
        }

        passed = len(unique_plans) == 1

        results.append(
            make_result(
                "EVAL-09",
                "Run the open-weights planner three times on the same task.",
                "Tool sequence remains stable across repeated runs.",
                "PASS" if passed else "FAIL",
                f"unique_plan_count={len(unique_plans)}; plans={plans}",
                duration,
                notes=(
                    "Qwen3 runs locally through Ollama with temperature=0. "
                    "This measures observable planner variation."
                ),
            )
        )
    except Exception as exc:
        results.append(
            make_result(
                "EVAL-09",
                "Run the open-weights planner three times on the same task.",
                "Tool sequence remains stable across repeated runs.",
                "FAIL",
                f"{type(exc).__name__}: {exc}",
                0,
            )
        )

    # -----------------------------------------------------
    # EVAL-10: known unfixed limitation
    # -----------------------------------------------------

    results.append(
        make_result(
            "EVAL-10",
            "Evaluate an image-only/scanned bid PDF.",
            "Extract document evidence from a scanned PDF.",
            "FAIL",
            (
                "Not implemented. The current prototype evaluates structured "
                "synthetic bid data and does not include OCR for image-only PDFs."
            ),
            0,
            notes=(
                "KNOWN UNFIXED FAILURE. Next step: add a local OCR/document "
                "extraction pipeline, preserve page-level citations, and add "
                "confidence thresholds before compliance evaluation."
            ),
        )
    )

    return results


def write_outputs(results: list[dict[str, Any]]) -> None:
    RESULTS_FILE.write_text(
        json.dumps(results, indent=2),
        encoding="utf-8",
    )

    passed = sum(
        1
        for item in results
        if item["status"] == "PASS"
    )

    failed = sum(
        1
        for item in results
        if item["status"] == "FAIL"
    )

    rows = []

    for item in results:
        rows.append(
            "| "
            f"{item['id']} | "
            f"{item['task']} | "
            f"{item['status']} | "
            f"{item['duration_seconds']}s | "
            f"{item['actual'].replace('|', '/')} |"
        )

    document = f"""# TenderGuard Africa — Evaluation Report

## Evaluation Summary

- Total tasks: {len(results)}
- Passed: {passed}
- Failed: {failed}
- Open-weights model: `qwen3:1.7b`
- Model runtime: local Ollama
- Orchestration: LangGraph
- Custom MCP server: TenderGuard Procurement MCP
- Borrowed MCP server: official/community Filesystem MCP
- External model API cost for these runs: USD 0.00
- Final award authority: human procurement committee only

## Test Results

| ID | Task | Result | Runtime | Observed result |
| --- | --- | --- | ---: | --- |
{chr(10).join(rows)}

## Reliability Notes

The evaluation set includes successful paths, problematic bids, safety gates,
MCP discovery, evidence sourcing, filesystem access control, and repeated
open-model planning. TenderGuard treats supplier-risk findings as data-quality
or review flags, not accusations of fraud or misconduct.

## Known Unfixed Failure

**EVAL-10 — Image-only/scanned PDF extraction: FAIL**

The current prototype does not contain an OCR pipeline for image-only bid
documents. The evaluated bid documents are structured synthetic records.
This limitation is intentionally disclosed rather than hidden.

A next iteration would add local OCR/document extraction, retain page-level
source references, measure extraction confidence, and route low-confidence
fields to a human reviewer before compliance checks are allowed to proceed.

## Human-in-the-Loop Rule

TenderGuard Africa may prepare evidence, findings, and a draft evaluation
report. It does not award, reject, disqualify, or select a winning bidder.
The authorised procurement committee retains the final decision.
"""

    EVALS_FILE.write_text(
        document,
        encoding="utf-8",
    )


async def main() -> None:
    print("Running TenderGuard Africa evaluations...")
    print()

    start = time.perf_counter()

    results = await run_evals()

    write_outputs(results)

    for result in results:
        print(
            f"{result['id']}: {result['status']} "
            f"- {result['task']}"
        )

    elapsed = time.perf_counter() - start

    passed = sum(
        1
        for item in results
        if item["status"] == "PASS"
    )

    failed = len(results) - passed

    print()
    print(
        f"Completed: {passed} PASS, {failed} FAIL "
        f"in {elapsed:.2f}s"
    )
    print(f"Results: {RESULTS_FILE}")
    print(f"Report:  {EVALS_FILE}")


if __name__ == "__main__":
    asyncio.run(main())