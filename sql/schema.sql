DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS discrepancies;
DROP TABLE IF EXISTS price_adjustments;
DROP TABLE IF EXISTS vendor_compliance;
DROP TABLE IF EXISTS weekly_status;

CREATE TABLE orders (
    order_id TEXT PRIMARY KEY,
    account_name TEXT NOT NULL,
    order_type TEXT NOT NULL,
    order_date TEXT NOT NULL,
    status TEXT NOT NULL,
    sku TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    order_value REAL NOT NULL,
    return_authorization TEXT,
    requested_return_qty INTEGER,
    received_return_qty INTEGER,
    price_expected REAL,
    price_billed REAL,
    days_open INTEGER NOT NULL,
    owner TEXT NOT NULL,
    customer_inquiry_open INTEGER NOT NULL,
    discrepancy_reason TEXT,
    memo_action TEXT
);

CREATE TABLE discrepancies (
    order_id TEXT NOT NULL,
    issue_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    resolution_owner TEXT NOT NULL,
    account_name TEXT NOT NULL,
    status TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE price_adjustments (
    order_id TEXT NOT NULL,
    adjustment_type TEXT NOT NULL,
    adjustment_amount REAL NOT NULL,
    reason TEXT NOT NULL,
    account_name TEXT NOT NULL,
    memo_status TEXT NOT NULL
);

CREATE TABLE vendor_compliance (
    case_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    account_name TEXT NOT NULL,
    deduction_code TEXT NOT NULL,
    charge_amount REAL NOT NULL,
    finding TEXT NOT NULL,
    dispute_status TEXT NOT NULL,
    root_cause TEXT NOT NULL
);

CREATE TABLE weekly_status (
    metric_name TEXT PRIMARY KEY,
    metric_value REAL NOT NULL,
    reporting_week TEXT NOT NULL
);