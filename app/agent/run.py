import argparse
import asyncio
import json

from app.agent.workflow import procurement_agent


async def run_agent(
    tender_id: str,
    bid_id: str,
) -> None:
    initial_state = {
        "tender_id": tender_id,
        "bid_id": bid_id,
        "status": "STARTED",
    }

    print()
    print("TenderGuard Africa")
    print("===================")
    print(f"Tender: {tender_id}")
    print(f"Bid:    {bid_id}")
    print()

    async for update in procurement_agent.astream(
        initial_state,
        stream_mode="updates",
    ):
        print(
            json.dumps(
                update,
                indent=2,
                default=str,
            )
        )

    print()
    print("Workflow stopped for human review.")


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

    args = parser.parse_args()

    asyncio.run(
        run_agent(
            args.tender,
            args.bid,
        )
    )


if __name__ == "__main__":
    main()