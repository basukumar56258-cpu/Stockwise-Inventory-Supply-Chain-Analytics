-- Expected tables: inventory_snapshot, product, purchase_order, supplier, location.
-- Adapt date and column names to the source warehouse before production use.

-- Latest inventory position and exception classification by SKU and location.
WITH latest AS (
    SELECT
        snapshot_date,
        sku,
        location_id,
        on_hand,
        reorder_point,
        target_stock,
        unit_cost,
        ROW_NUMBER() OVER (
            PARTITION BY sku, location_id
            ORDER BY snapshot_date DESC
        ) AS row_num
    FROM inventory_snapshot
)
SELECT
    latest.sku,
    product.product_name,
    location.region,
    location.location_name,
    latest.on_hand,
    latest.reorder_point,
    latest.target_stock,
    latest.on_hand * latest.unit_cost AS inventory_value,
    CASE
        WHEN latest.on_hand = 0 THEN 'Stockout'
        WHEN latest.on_hand <= latest.reorder_point THEN 'Reorder now'
        WHEN latest.on_hand > latest.target_stock * 1.5 THEN 'Overstock'
        ELSE 'Healthy'
    END AS stock_status,
    GREATEST(latest.target_stock - latest.on_hand, 0) AS suggested_order_quantity
FROM latest
JOIN product ON product.sku = latest.sku
JOIN location ON location.location_id = latest.location_id
WHERE latest.row_num = 1;

-- Supplier on-time delivery rate. Open orders are excluded from the denominator.
SELECT
    supplier.supplier_name,
    COUNT(*) AS received_orders,
    SUM(CASE WHEN po.received_date <= po.promised_date THEN 1 ELSE 0 END) AS on_time_orders,
    100.0 * SUM(CASE WHEN po.received_date <= po.promised_date THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0) AS on_time_rate_pct
FROM purchase_order AS po
JOIN supplier ON supplier.supplier_id = po.supplier_id
WHERE po.status = 'Received'
GROUP BY supplier.supplier_name
ORDER BY on_time_rate_pct ASC;

-- Monthly inventory value and stockout rate trend.
SELECT
    DATE_TRUNC('month', snapshot_date) AS snapshot_month,
    AVG(on_hand * unit_cost) AS average_inventory_value,
    100.0 * AVG(CASE WHEN on_hand = 0 THEN 1.0 ELSE 0.0 END) AS stockout_rate_pct
FROM inventory_snapshot
GROUP BY DATE_TRUNC('month', snapshot_date)
ORDER BY snapshot_month;
