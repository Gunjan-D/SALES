-- Open aged sales and return orders beyond global guideline threshold.
SELECT order_id, account_name, order_type, status, days_open, discrepancy_reason
FROM orders
WHERE days_open > 30
  AND status NOT IN ('Closed', 'Resolved')
ORDER BY days_open DESC;

-- Return Authorization tracking by account.
SELECT account_name,
       COUNT(*) AS return_orders,
       SUM(CASE WHEN return_authorization IS NOT NULL THEN 1 ELSE 0 END) AS ra_present,
       SUM(CASE WHEN return_authorization IS NULL THEN 1 ELSE 0 END) AS ra_missing
FROM orders
WHERE order_type = 'Return'
GROUP BY account_name
ORDER BY ra_missing DESC, return_orders DESC;

-- Recommended debit and credit memo totals.
SELECT adjustment_type,
       ROUND(SUM(adjustment_amount), 2) AS total_adjustment,
       COUNT(*) AS order_count
FROM price_adjustments
GROUP BY adjustment_type;

-- Invalid vendor compliance deductions worth disputing.
SELECT case_id, order_id, account_name, deduction_code, charge_amount, dispute_status
FROM vendor_compliance
WHERE finding = 'Invalid'
ORDER BY charge_amount DESC;

-- Weekly exception summary for analyst review.
SELECT metric_name, metric_value, reporting_week
FROM weekly_status
ORDER BY metric_name;