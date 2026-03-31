# Sales Order & Return Reconciliation Tracker

**Live dashboard → [https://gunjan-d.github.io/SALES/](https://gunjan-d.github.io/SALES/)**

> Local Sales Order & Return Reconciliation Tracker — generates simulated orders, flags discrepancies, recommends memos, and serves an interactive dashboard.

This resume-ready business analyst portfolio project simulates sales and return operations to demonstrate reconciliation workflows, exception detection, memo recommendations, RA tracking, and vendor compliance dispute logging. It produces CSV/Excel exports and a local web dashboard for stakeholder reporting and operational review.

This project is a resume-ready business analyst portfolio piece designed for roles focused on sales order management, returns processing, reconciliation, vendor compliance, and customer support.

It simulates the day-to-day workflow of a Sales/Return Order Analyst by generating realistic order activity, identifying discrepancies, calculating debit and credit memo adjustments, tracking Return Authorization (RA) status, flagging aged orders, and logging vendor compliance disputes.

## Role Alignment

This project is built to mirror the responsibilities in a Business Analyst 1 (Sales/Return Order Analyst) role:

- Enter and update sales and return orders
- Maintain aged orders against compliance guidelines
- Track Return Authorization status by account
- Research and resolve order discrepancies
- Process debit and credit memo adjustments
- Dispute invalid vendor compliance deductions
- Report valid compliance issues for future mitigation
- Produce customer-facing and stakeholder-facing status reporting

## Tech Stack

- Python
- SQL (SQLite)
- Excel output generation with multi-sheet reporting
- Pandas for reconciliation and reporting workflows
- OpenPyXL for workbook creation

## Deliverables

Running the project creates the following outputs in `outputs/`:

- `sales_operations.db`: SQLite database with staged order and compliance tables
- `sales_return_tracker.xlsx`: Excel workbook with operational dashboards and trackers
- `orders.csv`: simulated order and return transactions
- `discrepancies.csv`: identified order exceptions and status
- `price_adjustments.csv`: debit and credit memo recommendations
- `vendor_compliance.csv`: vendor charge research log with dispute status
- `weekly_status_report.csv`: stakeholder reporting summary

## Workbook Sheets

- `Order_Detail`
- `Aged_Orders`
- `RA_Status`
- `Discrepancies`
- `Price_Adjustments`
- `Vendor_Compliance`
- `Weekly_Status`
- `KPI_Summary`

## How To Run

1. Install dependencies:

```powershell
pip install -r requirements.txt
```

2. Run the project:

```powershell
python src/main.py
```

3. Review the generated files inside `outputs/`.

4. Launch the localhost dashboard:

```powershell
python src/dashboard_server.py
```

5. Open `http://127.0.0.1:8000` in your browser.

## Public Hosting (GitHub Pages)

This project can be published as a static site on GitHub Pages. I included a static dashboard snapshot at `web/dashboard.json` which the frontend will use when the dynamic API is not available. To publish the site:

- Ensure `web/dashboard.json` exists by running:

```powershell
python src/build_static_dashboard.py
```

- Push the `main` branch to GitHub and enable GitHub Pages in the repository settings using the `gh-pages` branch or the `main` branch with `/ (root)` as the source. The site will be available at:

https://gunjan-d.github.io/SALES/

Keep this link visible in the README so visitors can open the public demo.

## SQL Assets

The `sql/` folder includes:

- `schema.sql`: database schema used by the project
- `analysis_queries.sql`: sample analyst queries for reconciliation and compliance reporting

## Local Dashboard

The localhost dashboard presents the project as an analyst operations console with:

- KPI summary cards
- Aged open order monitoring
- Return Authorization status by account
- Open discrepancy queue
- Vendor compliance dispute tracking

It reads directly from the generated SQLite database in `outputs/`.

## Resume Bullets

You can use or adapt these bullets for your resume:

- Built an end-to-end Sales Order & Return Reconciliation Tracker that simulated 500+ transactions across order entry, return processing, aged order review, and RA status management using Python, SQL, and Excel.
- Automated discrepancy detection and debit/credit memo recommendations by reconciling order, return, pricing, and authorization records, reducing manual review effort through rules-based exception handling.
- Designed a vendor compliance dispute log and weekly operational dashboard that tracked invalid chargebacks, valid compliance violations, and account-level return activity for stakeholder reporting.

//////////////////////////////////////////////////////////

## Project Structure

```text
Sales/
|-- README.md
|-- requirements.txt
|-- resume_support.md
|-- sql/
|   |-- schema.sql
|   |-- analysis_queries.sql
|-- src/
|   |-- main.py
|-- outputs/
```
