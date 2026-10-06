# TenderGuard Africa

Agentic AI procurement decision-support system for auditable public tender evaluation in African institutions.

TenderGuard Africa uses an open-weights model, LangGraph, and Model Context Protocol (MCP) tools to review tender evidence, check mandatory compliance, compare prices with historical procurement data, identify supplier-data inconsistencies, and prepare a sourced evaluation report.

The system does not award tenders. It stops for human procurement committee review.

## Challenge

TenderGuard Africa was built for the Governance track of the African Agentic AI Design Challenge - The Bid Box Challenge.

**Theme:** Digital Economy - Open Contracting

## Problem

Public procurement teams may spend days manually sorting tender records, checking mandatory documents, comparing prices, reviewing supplier information, and preparing evaluation reports.

This process is repetitive, time-consuming, and difficult to audit when evidence is distributed across multiple records.

TenderGuard Africa automates the evidence-preparation workflow while keeping the final procurement decision with an authorised human committee.

## What the Agent Does

The agent:

1. Plans the tender evaluation workflow.
2. Loads tender evidence.
3. Checks mandatory bid compliance.
4. Compares submitted prices with historical award data.
5. Reviews supplier-data inconsistencies.
6. Synthesizes sourced findings.
7. Stops at human review.
8. Generates a draft report only after named human approval.

TenderGuard never automatically awards, rejects, disqualifies, or selects a winning bidder.

## One-Command Demo

### Prerequisites

Install:

- Python 3.12
- Git
- Node.js and npm
- Ollama

The project uses the local open-weights model:

`qwen3:1.7b`

### Run

From the project root:

```powershell
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

The script:

- creates the Python virtual environment if necessary;
- installs dependencies;
- checks Ollama;
- downloads Qwen3 1.7B if necessary;
- runs the TenderGuard evaluation demo.

The workflow should finish at:

`AWAITING_HUMAN_REVIEW`

## Manual Setup

Create the environment:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Download the open-weights model:

```powershell
ollama pull qwen3:1.7b
```

Run the evaluation agent:

```powershell
python -m app.agent.run --tender TG-DEMO-001 --bid BID-BETA-001
```

## Human Approval and Report Generation

After reviewing the agent findings, a named human reviewer can approve generation of the draft evaluation report:

```powershell
python -m app.agent.approve --tender TG-DEMO-001 --bid BID-BETA-001 --approved-by "Demo Procurement Reviewer"
```

The report is written under:

```text
reports/
```

It is marked:

`DRAFT_FOR_COMMITTEE_REVIEW`

Report generation is not an award decision.

## Agent Architecture

TenderGuard uses:

- Qwen3 1.7B as the open-weights reasoning model;
- Ollama for local model inference;
- LangGraph for stateful multi-step orchestration;
- MCP for tool execution;
- Pydantic for structured model outputs;
- Pytest for testing and evaluation.

See `ARCHITECTURE.md` for the complete architecture.

## Custom MCP Server

TenderGuard includes its own MCP server:

`TenderGuard Procurement MCP`

It exposes five tools.

### `load_tender`

Loads and normalizes tender records with source information.

### `check_bid_compliance`

Checks mandatory tender requirements including:

- submission deadline;
- mandatory documents;
- eligibility requirements.

Every finding contains evidence sources.

### `compare_prices`

Compares submitted bid prices with historical award values.

It returns:

- historical minimum;
- median;
- maximum;
- percentage deviation;
- risk classification;
- source evidence.

### `flag_supplier_risk`

Identifies supplier-data inconsistencies.

These flags indicate records that require human review. They are not accusations of fraud or misconduct.

### `generate_evaluation_report`

Writes a sourced draft evaluation report.

This action requires a named human approver and does not make a procurement award decision.

## Borrowed MCP Server

TenderGuard uses:

`@modelcontextprotocol/server-filesystem`

This MCP server was not written as part of TenderGuard Africa.

It provides standardized filesystem operations and access controls. Its TenderGuard integration is restricted to:

`reports/`

This gives the agent reusable filesystem capabilities without rebuilding a generic filesystem MCP server.

## Open-Weights Model

One complete TenderGuard workflow runs locally using:

`qwen3:1.7b`

through Ollama.

The open model performs:

- workflow planning;
- evidence synthesis.

No closed frontier model is required to complete the evaluation workflow.

## Human-in-the-Loop

The autonomous workflow stops at:

`AWAITING_HUMAN_REVIEW`

TenderGuard does not contain an automated tender-award node.

A named human must approve report generation.

The authorised procurement committee retains the final procurement decision.

## Audit Trail

Custom MCP actions are logged with:

- timestamp;
- tool name;
- inputs;
- outputs;
- execution status;
- human approver where applicable.

Runtime audit records are stored under the `reports/` directory.

## Data

The prototype currently uses synthetic procurement records:

```text
data/
├── ocds/
└── synthetic_bids/
```

Tender and historical award records use procurement and OCDS-style fields.

The repository does not claim that these records are live Tanzanian procurement records.

The synthetic dataset is used so the public repository contains no live tender in progress and no personal information.

Real open OCDS releases can be integrated in a future deployment.

## Evaluation

TenderGuard contains 10 documented evaluation tasks.

Current results:

- 9 PASS
- 1 known FAIL

Passing evaluations cover:

- compliant-bid full workflow;
- problematic-bid full workflow;
- MCP tool discovery;
- compliance detection;
- historical price anomaly detection;
- supplier-data inconsistency detection;
- human approval enforcement;
- filesystem sandboxing;
- open-model planner stability.

The intentionally disclosed unresolved failure is:

`Image-only/scanned PDF extraction`

OCR is not implemented in the current prototype.

See `EVALS.md` for the complete evaluation report.

## Tests

Run the automated test suite:

```powershell
pytest -q
```

Run the evaluation suite:

```powershell
python -m evals.run_evals
```

## Project Structure

```text
TenderGuard-Africa/
├── app/
│   └── agent/
│       ├── approve.py
│       ├── filesystem_mcp.py
│       ├── mcp_client.py
│       ├── ollama_client.py
│       ├── run.py
│       ├── state.py
│       └── workflow.py
├── data/
│   ├── ocds/
│   └── synthetic_bids/
├── evals/
│   ├── run_evals.py
│   └── results.json
├── mcp_servers/
│   └── procurement/
│       ├── audit.py
│       ├── server.py
│       └── tools/
├── reports/
├── tests/
├── ARCHITECTURE.md
├── EVALS.md
├── README.md
├── pyproject.toml
└── start.ps1
```

## Technology Stack

- Python 3.12
- MCP Python SDK
- LangGraph
- Qwen3 1.7B
- Ollama
- Pydantic
- HTTPX
- PyPDF
- Pytest
- Node.js
- Filesystem MCP Server
- Git
- GitHub

## Known Limitation

Image-only and scanned PDF bid documents are not currently supported because the prototype does not include OCR.

A future version would add:

- local OCR;
- page-level source citations;
- extraction confidence scores;
- human validation for low-confidence fields.

## Safety and Procurement Principle

**TenderGuard Africa prepares the evaluation file. The human procurement committee decides.**

## License

MIT License