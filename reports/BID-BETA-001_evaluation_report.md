# TenderGuard Africa Evaluation Report

## Review Status

DRAFT FOR HUMAN PROCUREMENT COMMITTEE REVIEW

TenderGuard Africa provides decision support only.
It does not award, reject, disqualify, or select a winning bidder.

## Tender

- Tender ID: TG-DEMO-001
- Title: Supply of Computer Equipment
- Procuring Entity: Demo Public Institution
- Tender Source: data\ocds\demo_tender.json

## Bid

- Bid ID: BID-BETA-001
- Supplier: Beta Systems Ltd
- Compliance Status: NON_COMPLIANT

## Compliance Findings

- [FLAG] Bid was submitted after the tender deadline. (Sources: data\ocds\demo_tender.json, data\synthetic_bids\bid_beta.json)
- [PASS] Required document present: Signed Bid Form. (Sources: data\ocds\demo_tender.json, data\synthetic_bids\bid_beta.json)
- [PASS] Required document present: Valid Business License. (Sources: data\ocds\demo_tender.json, data\synthetic_bids\bid_beta.json)
- [FLAG] Required document missing: Valid Tax Clearance Certificate. (Sources: data\ocds\demo_tender.json, data\synthetic_bids\bid_beta.json)
- [FLAG] Eligibility requirement not satisfied: Supplier must be legally registered to operate. (Sources: data\ocds\demo_tender.json, data\synthetic_bids\bid_beta.json)

## Price Analysis

- Submitted Price: 47000000 TZS
- Historical Sample Size: 4
- Historical Median: 40000000.0 TZS
- Deviation from Median: 17.5%
- Price Risk Level: ELEVATED

Finding:

Bid price is 17.5% above the median historical award value.

## Historical Price Evidence

- ocds-demo-history-001 | AWARD-HIST-001 | 38000000 TZS | data\ocds\historical_awards.json
- ocds-demo-history-002 | AWARD-HIST-002 | 40000000 TZS | data\ocds\historical_awards.json
- ocds-demo-history-003 | AWARD-HIST-003 | 41000000 TZS | data\ocds\historical_awards.json
- ocds-demo-history-004 | AWARD-HIST-004 | 40000000 TZS | data\ocds\historical_awards.json

## Supplier Data Review

- Risk Level: ELEVATED
- Historical Records Checked: 2

- [MEDIUM] The same supplier identifier appears under multiple supplier names in historical records. (Sources: data\synthetic_bids\bid_beta.json, data\ocds\supplier_history.json)

Supplier-risk flags represent data inconsistencies only.
They are not findings of fraud or misconduct.

## Human-in-the-Loop Handoff

Report generation approved by: Gloria Mbilinyi - Demo Procurement Reviewer

Generated at: 2026-10-06T11:45:03.057302+00:00

The authorised procurement committee must independently review
the evidence and make the final procurement decision.
