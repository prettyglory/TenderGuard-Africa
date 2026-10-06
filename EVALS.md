# TenderGuard Africa - Evaluation Report

## Evaluation Summary

- Total tasks: 10
- Passed: 9
- Failed: 1
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
| EVAL-01 | Run a compliant bid through the complete agent workflow. | PASS | 22.882s | status=AWAITING_HUMAN_REVIEW; priority=STANDARD_REVIEW; final_award_decision=None |
| EVAL-02 | Run a bid with compliance, price, and supplier-data issues. | PASS | 17.484s | status=AWAITING_HUMAN_REVIEW; priority=ATTENTION_REQUIRED; reasons=['Failed mandatory check: Bid was submitted after the tender deadline.', 'Elevated bid price: 17.5% above the median historical award value.', 'Elevated supplier data risk: Inconsistent supplier identifiers in historical records.']; final_award_decision=None |
| EVAL-03 | Inspect tools exposed by the custom Procurement MCP server. | PASS | 1.246s | tools=['check_bid_compliance', 'compare_prices', 'flag_supplier_risk', 'generate_evaluation_report', 'load_tender'] |
| EVAL-04 | Check mandatory compliance for BID-BETA-001. | PASS | 0.002s | failed=['SUBMISSION_DEADLINE', 'TAX_CLEARANCE', 'LOCAL_REGISTRATION'] |
| EVAL-05 | Compare BID-BETA-001 against historical award prices. | PASS | 0.001s | median=40000000.0; deviation=17.5%; risk=ELEVATED |
| EVAL-06 | Review supplier-history inconsistencies for BID-BETA-001. | PASS | 0.001s | risk=ELEVATED; flags=['IDENTIFIER_NAME_INCONSISTENCY'] |
| EVAL-07 | Attempt report generation without a named human approver. | PASS | 0.0s | Blocked: Human approval is required before generating the evaluation report. |
| EVAL-08 | Attempt to read a file outside reports/ through filesystem access. | PASS | 0.0s | Blocked: Borrowed filesystem MCP may only access the reports directory. |
| EVAL-09 | Run the open-weights planner three times on the same task. | PASS | 11.301s | unique_plan_count=1; plans=[['load_tender', 'check_bid_compliance', 'compare_prices', 'flag_supplier_risk'], ['load_tender', 'check_bid_compliance', 'compare_prices', 'flag_supplier_risk'], ['load_tender', 'check_bid_compliance', 'compare_prices', 'flag_supplier_risk']] |
| EVAL-10 | Evaluate an image-only/scanned bid PDF. | FAIL | 0s | Not implemented. The current prototype evaluates structured synthetic bid data and does not include OCR for image-only PDFs. |

## Reliability Notes

The evaluation set includes successful paths, problematic bids, safety gates,
MCP discovery, evidence sourcing, filesystem access control, and repeated
open-model planning. TenderGuard treats supplier-risk findings as data-quality
or review flags, not accusations of fraud or misconduct.

## Known Unfixed Failure

**EVAL-10 - Image-only/scanned PDF extraction: FAIL**

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
