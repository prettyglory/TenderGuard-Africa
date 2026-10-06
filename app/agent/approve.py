import argparse
import asyncio
import json

from app.agent.filesystem_mcp import read_report
from app.agent.mcp_client import call_procurement_tool


async def approve_and_generate(
    tender_id: str,
    bid_id: str,
    approved_by: str,
) -> None:
    approved_by = approved_by.strip()

    if not approved_by:
        raise ValueError("A named human approver is required.")

    print()
    print("TenderGuard Africa - Human Approval Gate")
    print("=========================================")
    print(f"Tender:      {tender_id}")
    print(f"Bid:         {bid_id}")
    print(f"Approved by: {approved_by}")
    print()

    result = await call_procurement_tool(
        "generate_evaluation_report",
        {
            "tender_id": tender_id,
            "bid_id": bid_id,
            "approved_by": approved_by,
        },
    )

    print("Own MCP report action completed:")
    print(
        json.dumps(
            result,
            indent=2,
            default=str,
        )
    )

    print()
    print("Reading generated draft through borrowed Filesystem MCP...")
    print()

    report_content = await read_report(
        result["report_path"]
    )

    print(report_content)

    print()
    print("HANDOFF COMPLETE")
    print(
        "TenderGuard has prepared the file. "
        "The procurement committee retains the final decision."
    )


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--tender",
        required=True,
    )

    parser.add_argument(
        "--bid",
        required=True,
    )

    parser.add_argument(
        "--approved-by",
        required=True,
    )

    args = parser.parse_args()

    asyncio.run(
        approve_and_generate(
            args.tender,
            args.bid,
            args.approved_by,
        )
    )


if __name__ == "__main__":
    main()