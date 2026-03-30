from __future__ import annotations

import json
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "outputs"
DATABASE_PATH = OUTPUT_DIR / "sales_operations.db"


def fetch_rows(connection: sqlite3.Connection, query: str):
    connection.row_factory = sqlite3.Row
    rows = connection.execute(query).fetchall()
    return [dict(row) for row in rows]


def build_payload():
    if not DATABASE_PATH.exists():
        raise FileNotFoundError("Run src/main.py first to generate outputs/sales_operations.db.")

    with sqlite3.connect(DATABASE_PATH) as conn:
        summary_rows = fetch_rows(
            conn,
            "SELECT metric_name, metric_value, reporting_week FROM weekly_status ORDER BY metric_name",
        )
        metrics = {row["metric_name"]: row["metric_value"] for row in summary_rows}
        reporting_week = summary_rows[0]["reporting_week"] if summary_rows else ""

        aged_orders = fetch_rows(
            conn,
            """
            SELECT order_id, account_name, order_type, status, days_open, memo_action
            FROM orders
            WHERE days_open > 30
              AND status NOT IN ('Closed', 'Resolved')
            ORDER BY days_open DESC, account_name ASC
            LIMIT 12
            """,
        )

        ra_status = fetch_rows(
            conn,
            """
            SELECT account_name,
                   COUNT(*) AS return_orders,
                   SUM(CASE WHEN return_authorization IS NOT NULL THEN 1 ELSE 0 END) AS ra_present,
                   SUM(CASE WHEN return_authorization IS NULL THEN 1 ELSE 0 END) AS ra_missing
            FROM orders
            WHERE order_type = 'Return'
            GROUP BY account_name
            ORDER BY ra_missing DESC, return_orders DESC
            LIMIT 8
            """,
        )

        discrepancies = fetch_rows(
            conn,
            """
            SELECT order_id, issue_type, severity, resolution_owner, account_name, status
            FROM discrepancies
            WHERE status = 'Open'
            ORDER BY CASE severity WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END, account_name ASC
            LIMIT 12
            """,
        )

        compliance = fetch_rows(
            conn,
            """
            SELECT case_id, order_id, account_name, deduction_code, charge_amount, dispute_status
            FROM vendor_compliance
            WHERE finding = 'Invalid'
            ORDER BY charge_amount DESC, account_name ASC
            LIMIT 12
            """,
        )

    total_orders = float(metrics.get("total_orders", 0)) or 1.0
    return_orders = float(metrics.get("return_orders", 0))
    aged_orders_count = float(metrics.get("aged_orders", 0))
    discrepancy_count = float(metrics.get("discrepancy_count", 0))
    invalid_compliance_cases = float(metrics.get("invalid_compliance_cases", 0))

    overview = [
        {
            "label": "Return Mix",
            "value": f"{(return_orders / total_orders) * 100:.1f}%",
            "detail": "Share of total activity represented by return orders.",
        },
        {
            "label": "Aged Order Exposure",
            "value": f"{(aged_orders_count / total_orders) * 100:.1f}%",
            "detail": "Open orders beyond monthly maintenance threshold.",
        },
        {
            "label": "Exception Density",
            "value": f"{(discrepancy_count / total_orders):.2f}",
            "detail": "Average discrepancy records generated per order.",
        },
        {
            "label": "Compliance Dispute Rate",
            "value": f"{(invalid_compliance_cases / total_orders) * 100:.1f}%",
            "detail": "Invalid vendor deductions relative to total order volume.",
        },
    ]

    priorities = [
        {
            "title": "Aged order cleanup",
            "value": int(metrics.get("aged_orders", 0)),
            "detail": "Orders still open past guideline threshold and requiring analyst maintenance.",
        },
        {
            "title": "RA follow-up",
            "value": int(metrics.get("missing_ra_cases", 0)),
            "detail": "Return transactions missing authorization and requiring account communication.",
        },
        {
            "title": "Memo queue",
            "value": int(metrics.get("memo_recommendations", 0)),
            "detail": "Debit and credit memo recommendations awaiting resolution workflow.",
        },
    ]

    payload = {
        "reporting_week": reporting_week,
        "metrics": metrics,
        "overview": overview,
        "priorities": priorities,
        "aged_orders": aged_orders,
        "ra_status": ra_status,
        "discrepancies": discrepancies,
        "compliance": compliance,
    }

    return payload


if __name__ == "__main__":
    out_path = BASE_DIR / "web" / "dashboard.json"
    payload = build_payload()
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote static dashboard to {out_path}")
