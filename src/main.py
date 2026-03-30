from __future__ import annotations

import random
import sqlite3
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "outputs"
SQL_DIR = BASE_DIR / "sql"
RANDOM_SEED = 42
TODAY = date(2026, 3, 29)


@dataclass(frozen=True)
class AccountProfile:
    name: str
    region: str


ACCOUNTS = [
    AccountProfile("Target", "Central"),
    AccountProfile("Walmart", "South"),
    AccountProfile("Costco", "West"),
    AccountProfile("Best Buy", "East"),
    AccountProfile("Home Depot", "South"),
    AccountProfile("Lowe's", "East"),
    AccountProfile("Amazon", "National"),
    AccountProfile("Macy's", "East"),
]

OWNERS = ["Order Management", "Returns Desk", "Sales Ops", "Customer Care"]
SKUS = [
    "HE-1001",
    "HE-1002",
    "HE-1003",
    "HE-1004",
    "HE-1005",
    "HE-1006",
    "HE-1007",
    "HE-1008",
]
RETURN_REASONS = [
    "Damaged in transit",
    "Incorrect item received",
    "Pricing discrepancy",
    "Customer refusal",
    "Late delivery",
    "Over shipment",
]
DEDUCTION_CODES = ["OTIF", "ROUTING", "LABEL", "SHORTAGE", "ASN", "PACKAGING"]


def generate_orders(order_count: int = 540) -> pd.DataFrame:
    random.seed(RANDOM_SEED)
    rows: list[dict[str, object]] = []

    for index in range(1, order_count + 1):
        account = random.choice(ACCOUNTS)
        order_type = "Return" if random.random() < 0.33 else "Sale"
        order_date = TODAY - timedelta(days=random.randint(1, 95))
        status = random.choices(
            ["Open", "Processing", "Pending Review", "Closed", "Resolved"],
            weights=[0.21, 0.24, 0.16, 0.25, 0.14],
            k=1,
        )[0]
        quantity = random.randint(1, 40)
        unit_price = round(random.uniform(55, 750), 2)
        order_value = round(quantity * unit_price, 2)
        price_variance = round(random.uniform(-18, 25), 2) if random.random() < 0.19 else 0.0
        expected_price = unit_price
        billed_price = round(unit_price + price_variance, 2)
        requested_return_qty = quantity if order_type == "Return" else 0
        received_return_qty = 0
        ra_number = None
        discrepancy_reason = None
        memo_action = "None"

        if order_type == "Return":
            received_return_qty = max(0, requested_return_qty - random.randint(0, 4))
            ra_number = f"RA-{10000 + index}" if random.random() < 0.84 else None
            discrepancy_reason = random.choice(RETURN_REASONS) if random.random() < 0.58 else None

        days_open = (TODAY - order_date).days
        inquiry_open = 1 if random.random() < 0.17 else 0
        owner = random.choice(OWNERS)

        if billed_price > expected_price:
            memo_action = "Credit Memo"
        elif billed_price < expected_price:
            memo_action = "Debit Memo"

        rows.append(
            {
                "order_id": f"SO-{index:05d}",
                "account_name": account.name,
                "region": account.region,
                "order_type": order_type,
                "order_date": order_date.isoformat(),
                "status": status,
                "sku": random.choice(SKUS),
                "quantity": quantity,
                "unit_price": unit_price,
                "order_value": order_value,
                "return_authorization": ra_number,
                "requested_return_qty": requested_return_qty,
                "received_return_qty": received_return_qty,
                "price_expected": expected_price,
                "price_billed": billed_price,
                "days_open": days_open,
                "owner": owner,
                "customer_inquiry_open": inquiry_open,
                "discrepancy_reason": discrepancy_reason,
                "memo_action": memo_action,
            }
        )

    return pd.DataFrame(rows)


def build_discrepancies(orders: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, str]] = []

    for record in orders.itertuples(index=False):
        issues: list[tuple[str, str, str, str]] = []

        if record.days_open > 30 and record.status not in {"Closed", "Resolved"}:
            issues.append(("Aged Order", "High", "Order Management", "Monthly maintenance required"))
        if record.order_type == "Return" and not record.return_authorization:
            issues.append(("Missing RA", "High", "Returns Desk", "Customer follow-up needed"))
        if record.order_type == "Return" and record.received_return_qty != record.requested_return_qty:
            issues.append(("Return Quantity Mismatch", "Medium", "Warehouse Support", "Research receiving variance"))
        if round(record.price_billed, 2) != round(record.price_expected, 2):
            issues.append(("Pricing Variance", "Medium", "Sales Ops", "Review debit or credit memo"))
        if record.customer_inquiry_open:
            issues.append(("Open Customer Inquiry", "Low", "Customer Care", "Pending customer update"))

        for issue_type, severity, owner, notes in issues:
            rows.append(
                {
                    "order_id": record.order_id,
                    "issue_type": issue_type,
                    "severity": severity,
                    "resolution_owner": owner,
                    "account_name": record.account_name,
                    "status": "Open" if record.status not in {"Closed", "Resolved"} else "Closed",
                    "notes": notes,
                }
            )

    return pd.DataFrame(rows)


def build_price_adjustments(orders: pd.DataFrame) -> pd.DataFrame:
    adjusted_orders = orders.loc[orders["price_billed"] != orders["price_expected"]].copy()

    if adjusted_orders.empty:
        return pd.DataFrame(
            columns=[
                "order_id",
                "adjustment_type",
                "adjustment_amount",
                "reason",
                "account_name",
                "memo_status",
            ]
        )

    difference = (adjusted_orders["price_billed"] - adjusted_orders["price_expected"]) * adjusted_orders["quantity"]
    adjusted_orders["adjustment_type"] = difference.apply(lambda value: "Credit Memo" if value > 0 else "Debit Memo")
    adjusted_orders["adjustment_amount"] = difference.abs().round(2)
    adjusted_orders["reason"] = "Price mismatch against expected order price"
    adjusted_orders["memo_status"] = adjusted_orders["status"].apply(
        lambda status: "Closed" if status in {"Closed", "Resolved"} else "Pending"
    )

    return adjusted_orders[
        [
            "order_id",
            "adjustment_type",
            "adjustment_amount",
            "reason",
            "account_name",
            "memo_status",
        ]
    ].sort_values(by="adjustment_amount", ascending=False)


def build_vendor_compliance(orders: pd.DataFrame, case_count: int = 90) -> pd.DataFrame:
    random.seed(RANDOM_SEED + 7)
    sample = orders.sample(n=case_count, random_state=RANDOM_SEED + 7).reset_index(drop=True)
    rows: list[dict[str, object]] = []

    for index, record in enumerate(sample.itertuples(index=False), start=1):
        charge_amount = round(random.uniform(45, 650), 2)
        finding = "Invalid" if random.random() < 0.57 else "Valid"
        dispute_status = (
            random.choice(["Submitted", "Under Review", "Recovered"])
            if finding == "Invalid"
            else random.choice(["Accepted", "Preventive Action Logged"])
        )
        rows.append(
            {
                "case_id": f"VC-{index:04d}",
                "order_id": record.order_id,
                "account_name": record.account_name,
                "deduction_code": random.choice(DEDUCTION_CODES),
                "charge_amount": charge_amount,
                "finding": finding,
                "dispute_status": dispute_status,
                "root_cause": random.choice(
                    [
                        "Label issue",
                        "Routing guide mismatch",
                        "Shipment timing dispute",
                        "Retailer system error",
                        "Documentation gap",
                        "Packaging variance",
                    ]
                ),
            }
        )

    return pd.DataFrame(rows)


def build_weekly_status(
    orders: pd.DataFrame,
    discrepancies: pd.DataFrame,
    price_adjustments: pd.DataFrame,
    vendor_compliance: pd.DataFrame,
) -> pd.DataFrame:
    metrics = {
        "total_orders": int(len(orders)),
        "return_orders": int((orders["order_type"] == "Return").sum()),
        "open_orders": int(orders["status"].isin(["Open", "Processing", "Pending Review"]).sum()),
        "aged_orders": int(((orders["days_open"] > 30) & (~orders["status"].isin(["Closed", "Resolved"]))).sum()),
        "missing_ra_cases": int(
            ((orders["order_type"] == "Return") & (orders["return_authorization"].isna())).sum()
        ),
        "open_customer_inquiries": int(orders["customer_inquiry_open"].sum()),
        "discrepancy_count": int(len(discrepancies)),
        "memo_recommendations": int(len(price_adjustments)),
        "total_memo_value": round(float(price_adjustments["adjustment_amount"].sum()), 2),
        "invalid_compliance_cases": int((vendor_compliance["finding"] == "Invalid").sum()),
        "invalid_compliance_value": round(
            float(vendor_compliance.loc[vendor_compliance["finding"] == "Invalid", "charge_amount"].sum()), 2
        ),
    }

    return pd.DataFrame(
        {
            "metric_name": list(metrics.keys()),
            "metric_value": list(metrics.values()),
            "reporting_week": [TODAY.isoformat()] * len(metrics),
        }
    )


def build_ra_status(orders: pd.DataFrame) -> pd.DataFrame:
    returns = orders.loc[orders["order_type"] == "Return"].copy()
    summary = (
        returns.assign(ra_present=returns["return_authorization"].notna().astype(int))
        .groupby("account_name", as_index=False)
        .agg(
            return_orders=("order_id", "count"),
            ra_present=("ra_present", "sum"),
            open_return_orders=("status", lambda status: status.isin(["Open", "Processing", "Pending Review"]).sum()),
        )
    )
    summary["ra_missing"] = summary["return_orders"] - summary["ra_present"]
    return summary.sort_values(by=["ra_missing", "return_orders"], ascending=[False, False])


def build_kpi_summary(weekly_status: pd.DataFrame) -> pd.DataFrame:
    pivot = weekly_status.copy()
    pivot["metric_value"] = pivot["metric_value"].round(2)
    return pivot.rename(columns={"metric_name": "KPI", "metric_value": "Value", "reporting_week": "Reporting Week"})


def initialize_database(
    orders: pd.DataFrame,
    discrepancies: pd.DataFrame,
    price_adjustments: pd.DataFrame,
    vendor_compliance: pd.DataFrame,
    weekly_status: pd.DataFrame,
) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    database_path = OUTPUT_DIR / "sales_operations.db"
    schema_path = SQL_DIR / "schema.sql"

    with sqlite3.connect(database_path) as connection:
        connection.executescript(schema_path.read_text(encoding="utf-8"))
        orders.drop(columns=["region"]).to_sql("orders", connection, if_exists="append", index=False)
        discrepancies.to_sql("discrepancies", connection, if_exists="append", index=False)
        price_adjustments.to_sql("price_adjustments", connection, if_exists="append", index=False)
        vendor_compliance.to_sql("vendor_compliance", connection, if_exists="append", index=False)
        weekly_status.to_sql("weekly_status", connection, if_exists="append", index=False)

    return database_path


def export_outputs(
    orders: pd.DataFrame,
    discrepancies: pd.DataFrame,
    price_adjustments: pd.DataFrame,
    vendor_compliance: pd.DataFrame,
    weekly_status: pd.DataFrame,
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    aged_orders = orders.loc[(orders["days_open"] > 30) & (~orders["status"].isin(["Closed", "Resolved"]))].copy()
    ra_status = build_ra_status(orders)
    kpi_summary = build_kpi_summary(weekly_status)

    orders.to_csv(OUTPUT_DIR / "orders.csv", index=False)
    discrepancies.to_csv(OUTPUT_DIR / "discrepancies.csv", index=False)
    price_adjustments.to_csv(OUTPUT_DIR / "price_adjustments.csv", index=False)
    vendor_compliance.to_csv(OUTPUT_DIR / "vendor_compliance.csv", index=False)
    weekly_status.to_csv(OUTPUT_DIR / "weekly_status_report.csv", index=False)

    workbook_path = OUTPUT_DIR / "sales_return_tracker.xlsx"
    with pd.ExcelWriter(workbook_path, engine="openpyxl") as writer:
        orders.to_excel(writer, sheet_name="Order_Detail", index=False)
        aged_orders.to_excel(writer, sheet_name="Aged_Orders", index=False)
        ra_status.to_excel(writer, sheet_name="RA_Status", index=False)
        discrepancies.to_excel(writer, sheet_name="Discrepancies", index=False)
        price_adjustments.to_excel(writer, sheet_name="Price_Adjustments", index=False)
        vendor_compliance.to_excel(writer, sheet_name="Vendor_Compliance", index=False)
        weekly_status.to_excel(writer, sheet_name="Weekly_Status", index=False)
        kpi_summary.to_excel(writer, sheet_name="KPI_Summary", index=False)


def main() -> None:
    orders = generate_orders()
    discrepancies = build_discrepancies(orders)
    price_adjustments = build_price_adjustments(orders)
    vendor_compliance = build_vendor_compliance(orders)
    weekly_status = build_weekly_status(orders, discrepancies, price_adjustments, vendor_compliance)

    database_path = initialize_database(
        orders=orders,
        discrepancies=discrepancies,
        price_adjustments=price_adjustments,
        vendor_compliance=vendor_compliance,
        weekly_status=weekly_status,
    )
    export_outputs(
        orders=orders,
        discrepancies=discrepancies,
        price_adjustments=price_adjustments,
        vendor_compliance=vendor_compliance,
        weekly_status=weekly_status,
    )

    print("Created project outputs:")
    print(f"- Database: {database_path}")
    print(f"- Excel workbook: {OUTPUT_DIR / 'sales_return_tracker.xlsx'}")
    print(f"- Orders processed: {len(orders)}")
    print(f"- Discrepancies logged: {len(discrepancies)}")
    print(f"- Compliance cases reviewed: {len(vendor_compliance)}")


if __name__ == "__main__":
    main()