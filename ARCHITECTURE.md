# TenderGuard Africa - Architecture



## 1. System Purpose



TenderGuard Africa is an agentic AI procurement decision-support system for public tender evaluation.



The system reviews tender and bid evidence, checks mandatory compliance, compares bid prices with historical award data, identifies supplier-data inconsistencies, and prepares an auditable draft evaluation report.



TenderGuard Africa does not award, reject, disqualify, or select a winning bidder. The final procurement decision remains with an authorised human procurement committee.



## 2. High-Level Architecture



```text

Procurement Officer

&#x20;       |

&#x20;       v

TenderGuard CLI / Human Approval Gate

&#x20;       |

&#x20;       v

LangGraph Orchestrator

&#x20;       |

&#x20;       +---------------------------+

&#x20;       |                           |

&#x20;       v                           v

Qwen3 1.7B                    MCP Client

Open-Weights LLM                   |

via Ollama                          |

&#x20;       |                    +------+------+

&#x20;       |                    |             |

&#x20;       v                    v             v

Planning and          Procurement MCP   Filesystem MCP

Evidence Synthesis      Server (Own)     (Borrowed)

&#x20;                           |               |

&#x20;                           v               v

&#x20;                   Procurement Tools     reports/

&#x20;                           |

&#x20;               +-----------+-----------+

&#x20;               |           |           |

&#x20;               v           v           v

&#x20;            Tender     Compliance    Price

&#x20;            Loader       Check       Check

&#x20;                                       |

&#x20;                                       v

&#x20;                               Supplier Risk Check

&#x20;                                       |

&#x20;                                       v

&#x20;                              Human Approval Gate

&#x20;                                       |

&#x20;                                       v

&#x20;                             Draft Evaluation Report

&#x20;                                       |

&#x20;                                       v

&#x20;                             Procurement Committee
3. Agent and Orchestration

TenderGuard Africa uses LangGraph to coordinate the tender-evaluation workflow.

The workflow performs the following steps:

1\. Qwen3 plans the evaluation sequence.

2\. Tender evidence is loaded.

3\. Mandatory bid compliance is checked.

4\. Bid price is compared with historical award data.

5\. Supplier-data inconsistencies are reviewed.

6\. Qwen3 synthesizes the evidence.

7\. The workflow stops at AWAITING\_HUMAN\_REVIEW.

8\. A named human reviewer must approve report generation.

The workflow does not contain an automatic tender-award step.

4\. Open-Weights Model

TenderGuard Africa uses:

\- Model: qwen3:1.7b

\- Runtime: Ollama

\- Deployment: Local machine

The model is used for:

\- workflow planning;

\- evidence synthesis;

\- decision-support summaries.

Pydantic validates the structured output produced by the model.

The model runs locally so the full evaluation task does not depend on a closed cloud model.

5\. Custom MCP Server

TenderGuard Africa includes its own MCP server:

TenderGuard Procurement MCP

Location:

mcp\_servers/procurement/server.py

The LangGraph agent communicates with this server through an MCP client using stdio.

MCP Tools

load\_tender

Loads and normalizes tender information and returns the source of the evidence.

check\_bid\_compliance

Checks:

\- submission deadline;

\- mandatory documents;

\- eligibility requirements.

Each compliance finding includes its source.

compare\_prices

Compares the submitted bid price with historical award values.

It returns:

\- minimum historical value;

\- median historical value;

\- maximum historical value;

\- percentage deviation;

\- risk level;

\- supporting evidence.

flag\_supplier\_risk

Checks supplier-history data for inconsistencies such as the same identifier appearing under different supplier names.

These are review flags only. They are not accusations of fraud or misconduct.

generate\_evaluation\_report

Generates a sourced draft evaluation report.

This action requires a named human approver before the report file is created.

It does not make a tender award decision.

6\. Borrowed MCP Server

TenderGuard Africa also uses:

@modelcontextprotocol/server-filesystem

This MCP server was not developed as part of TenderGuard Africa.

It is used for standardized filesystem operations such as reading and listing generated reports.

Its access is restricted to the:

reports/

directory.

Using an existing filesystem MCP server is preferable to rebuilding generic filesystem capabilities inside the procurement server.

7\. Human-in-the-Loop

The autonomous workflow stops at:

AWAITING\_HUMAN\_REVIEW

A named human reviewer must explicitly approve report generation.

The generated document is marked:

DRAFT\_FOR\_COMMITTEE\_REVIEW

TenderGuard Africa never makes the final procurement decision.

The authorised procurement committee remains responsible for the final decision.

8\. Audit Logging

Custom MCP tool actions are logged.

The audit trail records:

\- timestamp;

\- tool name;

\- inputs;

\- outputs;

\- execution status;

\- human approver where applicable.

This makes the evaluation process traceable and auditable.

9\. Data Sources

The current prototype uses:

data/

├── ocds/

└── synthetic\_bids/



The current development dataset is synthetic.

Tender and historical records use procurement and OCDS-style fields so that the system can safely demonstrate the workflow without using a live tender or personal information.

The project does not claim that the current synthetic records are live Tanzanian procurement records.

Real open OCDS procurement data can be integrated in a future deployment.

10\. Overall Data Flow

Tender and Bid Data

&#x20;       |

&#x20;       v

Qwen3 Planner

&#x20;       |

&#x20;       v

LangGraph

&#x20;       |

&#x20;       v

MCP Client

&#x20;       |

&#x20;       v

TenderGuard Procurement MCP

&#x20;       |

&#x20;       +--> Tender Evidence

&#x20;       +--> Compliance Evidence

&#x20;       +--> Historical Price Evidence

&#x20;       +--> Supplier Data Evidence

&#x20;       |

&#x20;       v

Qwen3 Evidence Synthesis

&#x20;       |

&#x20;       v

AWAITING\_HUMAN\_REVIEW

&#x20;       |

&#x20;       v

Named Human Approval

&#x20;       |

&#x20;       v

generate\_evaluation\_report

&#x20;       |

&#x20;       v

Draft Evaluation Report

&#x20;       |

&#x20;       v

Filesystem MCP

&#x20;       |

&#x20;       v

Human Procurement Committee



11\. Evaluation and Reliability

TenderGuard Africa currently has 10 evaluation tasks.

Results:

\- 9 PASS

\- 1 FAIL

The known unresolved failure is image-only or scanned PDF extraction.

OCR is not implemented in the current prototype.

A future version would add:

\- local OCR;

\- page-level evidence citations;

\- extraction confidence scores;

\- human review for low-confidence extracted fields.

12\. Core Technology Stack

\- Python 3.12

\- MCP Python SDK

\- LangGraph

\- Qwen3 1.7B

\- Ollama

\- Pydantic

\- HTTPX

\- Pytest

\- Filesystem MCP Server

\- Git

\- GitHub

13\. Safety Principle

TenderGuard Africa prepares the procurement evaluation file.
The human procurement committee decides.

