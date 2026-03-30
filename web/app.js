const metricConfig = [
    ["total_orders", "Total Orders", "Portfolio-wide sales and return transactions under analyst visibility."],
    ["return_orders", "Return Orders", "Transactions requiring RA tracking, receipt validation, and follow-up."],
    ["aged_orders", "Aged Open Orders", "Orders exceeding maintenance thresholds and requiring review."],
    ["missing_ra_cases", "Missing RA Cases", "Return orders lacking authorization and at risk for delay."],
    ["discrepancy_count", "Discrepancies", "Exceptions raised across price, quantity, inquiry, and aging workflows."],
    ["memo_recommendations", "Memo Recommendations", "Debit and credit memo actions inferred from billing variance."],
    ["invalid_compliance_cases", "Invalid Compliance Cases", "Deductions identified as disputable after research."],
    ["invalid_compliance_value", "Invalid Compliance Value", "Total dollar exposure associated with invalid deductions."],
];

function formatValue(key, value) {
    if (key.includes("value")) {
        return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(value);
    }
    return new Intl.NumberFormat("en-US").format(value);
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function badgeClass(value) {
    const normalized = String(value).toLowerCase();
    if (normalized.includes("high") || normalized.includes("invalid") || normalized.includes("missing")) {
        return "badge badge-alert";
    }
    if (normalized.includes("medium") || normalized.includes("pending") || normalized.includes("under review")) {
        return "badge badge-warning";
    }
    if (normalized.includes("closed") || normalized.includes("resolved") || normalized.includes("recovered")) {
        return "badge badge-success";
    }
    return "badge badge-neutral";
}

function renderTable(targetId, rows, columns) {
    const target = document.getElementById(targetId);
    if (!rows.length) {
        target.innerHTML = '<p class="empty-state">No records to display.</p>';
        return;
    }

    const headerHtml = columns.map((column) => `<th>${column.label}</th>`).join("");
    const bodyHtml = rows
        .map((row) => {
            const cells = columns
                .map((column) => {
                    const rawValue = row[column.key] ?? "";
                    if (column.format === "currency") {
                        return `<td>${formatValue("value", rawValue)}</td>`;
                    }
                    if (column.format === "badge") {
                        return `<td><span class="${badgeClass(rawValue)}">${escapeHtml(rawValue)}</span></td>`;
                    }
                    return `<td>${escapeHtml(rawValue)}</td>`;
                })
                .join("");
            return `<tr>${cells}</tr>`;
        })
        .join("");

    target.innerHTML = `
        <div class="table-wrap">
            <table>
                <thead><tr>${headerHtml}</tr></thead>
                <tbody>${bodyHtml}</tbody>
            </table>
        </div>
    `;
}

async function loadDashboard() {
    const response = await fetch("/api/dashboard");
    const payload = await response.json();

    if (!response.ok) {
        document.body.innerHTML = `<main class="error-shell"><h1>Dashboard unavailable</h1><p>${payload.error}</p></main>`;
        return;
    }

    document.getElementById("reportingWeek").textContent = payload.reporting_week;

    const overviewCards = document.getElementById("overviewCards");
    overviewCards.innerHTML = payload.overview
        .map(
            (item) => `
                <article class="statement-card">
                    <p class="statement-value">${escapeHtml(item.value)}</p>
                    <p class="statement-label">${escapeHtml(item.label)}</p>
                    <p class="statement-detail">${escapeHtml(item.detail)}</p>
                </article>
            `
        )
        .join("");

    const metricsGrid = document.getElementById("metricsGrid");
    metricsGrid.innerHTML = metricConfig
        .map(([key, label, detail]) => {
            const value = payload.metrics[key] ?? 0;
            return `
                <article class="metric-card">
                    <p class="metric-label">${label}</p>
                    <p class="metric-value">${formatValue(key, value)}</p>
                    <p class="metric-detail">${detail}</p>
                </article>
            `;
        })
        .join("");

    const priorityStrip = document.getElementById("priorityStrip");
    priorityStrip.innerHTML = payload.priorities
        .map(
            (item) => `
                <article class="priority-card">
                    <p class="priority-label">Priority Focus</p>
                    <div class="priority-headline">
                        <p class="priority-title">${escapeHtml(item.title)}</p>
                        <p class="priority-value">${formatValue("count", item.value)}</p>
                    </div>
                    <p class="priority-detail">${escapeHtml(item.detail)}</p>
                </article>
            `
        )
        .join("");

    renderTable("agedOrdersTable", payload.aged_orders, [
        { key: "order_id", label: "Order ID" },
        { key: "account_name", label: "Account" },
        { key: "order_type", label: "Type", format: "badge" },
        { key: "status", label: "Status", format: "badge" },
        { key: "days_open", label: "Days Open" },
        { key: "memo_action", label: "Memo Action", format: "badge" },
    ]);

    renderTable("raStatusTable", payload.ra_status, [
        { key: "account_name", label: "Account" },
        { key: "return_orders", label: "Return Orders" },
        { key: "ra_present", label: "RA Present" },
        { key: "ra_missing", label: "RA Missing" },
    ]);

    renderTable("discrepanciesTable", payload.discrepancies, [
        { key: "order_id", label: "Order ID" },
        { key: "issue_type", label: "Issue Type" },
        { key: "severity", label: "Severity", format: "badge" },
        { key: "resolution_owner", label: "Owner" },
        { key: "account_name", label: "Account" },
        { key: "status", label: "Status", format: "badge" },
    ]);

    renderTable("complianceTable", payload.compliance, [
        { key: "case_id", label: "Case ID" },
        { key: "order_id", label: "Order ID" },
        { key: "account_name", label: "Account" },
        { key: "deduction_code", label: "Code", format: "badge" },
        { key: "charge_amount", label: "Charge Amount", format: "currency" },
        { key: "dispute_status", label: "Status", format: "badge" },
    ]);
}

loadDashboard().catch((error) => {
    document.body.innerHTML = `<main class="error-shell"><h1>Dashboard error</h1><p>${error.message}</p></main>`;
});