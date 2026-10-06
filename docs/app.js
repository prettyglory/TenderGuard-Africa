const bidButtons = document.querySelectorAll(".bid-button");
const runButton = document.getElementById("runButton");
const approveButton = document.getElementById("approveButton");

const workflowSection = document.getElementById("workflowSection");
const resultsSection = document.getElementById("resultsSection");
const reportSection = document.getElementById("reportSection");

const stepsContainer = document.getElementById("steps");

const complianceStatus = document.getElementById("complianceStatus");
const complianceFindings = document.getElementById("complianceFindings");

const priceStatus = document.getElementById("priceStatus");
const priceFindings = document.getElementById("priceFindings");

const supplierStatus = document.getElementById("supplierStatus");
const supplierFindings = document.getElementById("supplierFindings");

const reviewState = document.getElementById("reviewState");
const reviewMessage = document.getElementById("reviewMessage");
const priority = document.getElementById("priority");

const reportContent = document.getElementById("reportContent");

let selectedBid = "beta";

const bids = {
  alpha: {
    name: "Alpha Technologies Ltd",
    bidId: "BID-ALPHA-001",
    price: "TZS 42,000,000",

    compliance: {
      status: "COMPLIANT",
      className: "result-good",
      findings: [
        {
          title: "Submission deadline",
          detail: "Bid submitted before the tender deadline.",
          source: "data/synthetic_bids/bid_alpha.json"
        },
        {
          title: "Mandatory documents",
          detail: "BID_FORM, BUSINESS_LICENSE and TAX_CLEARANCE are present.",
          source: "data/synthetic_bids/bid_alpha.json"
        },
        {
          title: "Eligibility requirement",
          detail: "LOCAL_REGISTRATION requirement is satisfied.",
          source: "data/synthetic_bids/bid_alpha.json"
        }
      ]
    },

    priceAnalysis: {
      status: "NORMAL",
      className: "result-good",
      findings: [
        {
          title: "Submitted price",
          detail: "TZS 42,000,000"
        },
        {
          title: "Historical median",
          detail: "TZS 40,000,000"
        },
        {
          title: "Price observation",
          detail: "Bid price is close to the historical award reference range."
        },
        {
          title: "Source",
          detail: "data/ocds/historical_awards.json"
        }
      ]
    },

    supplierReview: {
      status: "LOW",
      className: "result-good",
      findings: [
        {
          title: "Supplier identifier",
          detail: "SYNTH-ALPHA-001"
        },
        {
          title: "Supplier-history review",
          detail: "No identifier/name inconsistency detected in the synthetic history."
        },
        {
          title: "Source",
          detail: "data/ocds/supplier_history.json"
        }
      ]
    },

    priority: "STANDARD_REVIEW",

    message:
      "The agent found no mandatory compliance failure or elevated supplier/price risk in the synthetic Alpha bid. Human committee review is still required.",

    reportSummary:
      "Alpha Technologies Ltd satisfies the mandatory requirements represented in the synthetic demonstration dataset. The submitted price is within the historical reference range and no supplier identifier/name inconsistency was detected."
  },

  beta: {
    name: "Beta Systems Ltd",
    bidId: "BID-BETA-001",
    price: "TZS 47,000,000",

    compliance: {
      status: "NON_COMPLIANT",
      className: "result-danger",
      findings: [
        {
          title: "Late submission",
          detail: "The bid was submitted after the tender deadline.",
          source: "data/synthetic_bids/bid_beta.json"
        },
        {
          title: "Missing mandatory document",
          detail: "TAX_CLEARANCE is missing from the synthetic bid record.",
          source: "data/synthetic_bids/bid_beta.json"
        },
        {
          title: "Eligibility requirement",
          detail: "LOCAL_REGISTRATION requirement is not satisfied.",
          source: "data/synthetic_bids/bid_beta.json"
        }
      ]
    },

    priceAnalysis: {
      status: "ELEVATED",
      className: "result-warning",
      findings: [
        {
          title: "Submitted price",
          detail: "TZS 47,000,000"
        },
        {
          title: "Historical median",
          detail: "TZS 40,000,000"
        },
        {
          title: "Deviation",
          detail: "+17.5% above the historical median."
        },
        {
          title: "Source",
          detail: "data/ocds/historical_awards.json"
        }
      ]
    },

    supplierReview: {
      status: "ELEVATED",
      className: "result-warning",
      findings: [
        {
          title: "Supplier identifier",
          detail: "SYNTH-BETA-001"
        },
        {
          title: "Identifier/name inconsistency",
          detail:
            "The same synthetic identifier appears under Beta Systems Ltd and Beta Digital Services Ltd."
        },
        {
          title: "Source",
          detail: "data/ocds/supplier_history.json"
        }
      ]
    },

    priority: "ATTENTION_REQUIRED",

    message:
      "The agent identified mandatory compliance failures, an elevated price observation, and a supplier-data inconsistency. These findings require human committee attention.",

    reportSummary:
      "Beta Systems Ltd requires committee attention because the synthetic record contains a late submission, a missing TAX_CLEARANCE document, an unmet LOCAL_REGISTRATION requirement, an elevated price relative to historical awards, and a supplier identifier/name inconsistency."
  }
};

const workflowSteps = [
  {
    title: "Qwen3 planning",
    subtitle: "Open-weights model prepares the evaluation tool sequence."
  },
  {
    title: "load_tender",
    subtitle: "Procurement MCP loads sourced tender evidence."
  },
  {
    title: "check_bid_compliance",
    subtitle: "MCP checks deadline, mandatory documents and eligibility."
  },
  {
    title: "compare_prices",
    subtitle: "MCP compares submitted price with historical award values."
  },
  {
    title: "flag_supplier_risk",
    subtitle: "MCP reviews synthetic supplier-history inconsistencies."
  },
  {
    title: "Qwen3 evidence synthesis",
    subtitle: "Open model synthesizes the collected sourced findings."
  },
  {
    title: "Human review gate",
    subtitle: "Workflow stops at AWAITING_HUMAN_REVIEW."
  }
];

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function resetDemo() {
  workflowSection.classList.add("hidden");
  resultsSection.classList.add("hidden");
  reportSection.classList.add("hidden");

  stepsContainer.innerHTML = "";
  complianceFindings.innerHTML = "";
  priceFindings.innerHTML = "";
  supplierFindings.innerHTML = "";
  reportContent.innerHTML = "";

  runButton.disabled = false;
  runButton.textContent = "Run TenderGuard Evaluation";

  approveButton.disabled = false;
  approveButton.textContent = "Simulate Named Human Approval";
}

bidButtons.forEach((button) => {
  button.addEventListener("click", () => {
    bidButtons.forEach((item) => item.classList.remove("active"));
    button.classList.add("active");

    selectedBid = button.dataset.bid;

    resetDemo();
  });
});

function createStep(step, index) {
  const element = document.createElement("div");

  element.className = "step";

  element.innerHTML = `
    <div class="step-number">${index + 1}</div>

    <div class="step-content">
      <strong>${step.title}</strong>
      <span>${step.subtitle}</span>
    </div>
  `;

  return element;
}

function createFinding(item) {
  const element = document.createElement("div");

  element.className = "finding";

  const source = item.source
    ? `<span>Source: ${item.source}</span>`
    : "";

  element.innerHTML = `
    <strong>${item.title}</strong>
    <span>${item.detail}</span>
    ${source}
  `;

  return element;
}

function populateFindings(container, findings) {
  container.innerHTML = "";

  findings.forEach((finding) => {
    container.appendChild(createFinding(finding));
  });
}

async function runEvaluation() {
  resetDemo();

  runButton.disabled = true;
  runButton.textContent = "Running evaluation...";

  workflowSection.classList.remove("hidden");

  workflowSection.scrollIntoView({
    behavior: "smooth",
    block: "start"
  });

  for (let index = 0; index < workflowSteps.length; index++) {
    const step = createStep(workflowSteps[index], index);

    stepsContainer.appendChild(step);

    await delay(420);

    step.classList.add("completed");
  }

  const bid = bids[selectedBid];

  complianceStatus.textContent = bid.compliance.status;
  complianceStatus.className = bid.compliance.className;

  priceStatus.textContent = bid.priceAnalysis.status;
  priceStatus.className = bid.priceAnalysis.className;

  supplierStatus.textContent = bid.supplierReview.status;
  supplierStatus.className = bid.supplierReview.className;

  populateFindings(
    complianceFindings,
    bid.compliance.findings
  );

  populateFindings(
    priceFindings,
    bid.priceAnalysis.findings
  );

  populateFindings(
    supplierFindings,
    bid.supplierReview.findings
  );

  reviewState.textContent = "AWAITING_HUMAN_REVIEW";

  reviewMessage.textContent = bid.message;

  priority.textContent = bid.priority;

  resultsSection.classList.remove("hidden");

  runButton.disabled = false;
  runButton.textContent = "Run Again";

  await delay(250);

  resultsSection.scrollIntoView({
    behavior: "smooth",
    block: "start"
  });
}

function generateReport() {
  const bid = bids[selectedBid];

  approveButton.disabled = true;
  approveButton.textContent = "Approved by Demo Procurement Reviewer";

  reportContent.innerHTML = `
    <div class="report-block">
      <strong>Tender</strong>
      Supply of Computer Equipment · TG-DEMO-001
    </div>

    <div class="report-block">
      <strong>Bid under review</strong>
      ${bid.name} · ${bid.bidId} · ${bid.price}
    </div>

    <div class="report-block">
      <strong>Compliance classification</strong>
      ${bid.compliance.status}
    </div>

    <div class="report-block">
      <strong>Price classification</strong>
      ${bid.priceAnalysis.status}
    </div>

    <div class="report-block">
      <strong>Supplier review classification</strong>
      ${bid.supplierReview.status}
    </div>

    <div class="report-block">
      <strong>Review priority</strong>
      ${bid.priority}
    </div>

    <div class="report-block">
      <strong>Evidence summary</strong>
      ${bid.reportSummary}
    </div>

    <div class="report-block">
      <strong>Named human approver</strong>
      Demo Procurement Reviewer
    </div>

    <div class="report-block">
      <strong>Final award decision</strong>
      NULL — retained by the authorised human procurement committee.
    </div>

    <div class="report-block">
      <strong>Evidence sources</strong>
      data/ocds/demo_tender.json<br />
      data/ocds/historical_awards.json<br />
      data/ocds/supplier_history.json<br />
      data/synthetic_bids/${selectedBid === "alpha" ? "bid_alpha.json" : "bid_beta.json"}
    </div>
  `;

  reportSection.classList.remove("hidden");

  reportSection.scrollIntoView({
    behavior: "smooth",
    block: "start"
  });
}

runButton.addEventListener("click", runEvaluation);

approveButton.addEventListener("click", generateReport);