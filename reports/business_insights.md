# Business Insights and Action Framework

All figures shown by the running app come from a deterministic fictional dataset. Use the dashboard to observe the current sample scenario; do not treat the sample outputs as real business findings.

## Decision framework

| Signal | Interpretation | First action | Follow-up measure |
|---|---|---|---|
| Stockout or below reorder point | Availability risk at a specific SKU and warehouse | Validate inbound orders and nearby inventory, then prioritize replenishment | Fill rate and stockout rate |
| Inventory above 1.5x target | Potential excess working capital | Pause new orders and review transfers, returns, or planned promotions | Excess inventory value and days of cover |
| Supplier on-time rate below 85% | Replenishment plan may be exposed to lead-time variability | Review late POs and agree a corrective action with procurement | On-time rate and realized lead time |
| Location has high stockout rate but low days of cover | Allocation may not match local demand | Compare demand and stock positions across nearby warehouses | Location fill rate and transfer lead time |
| Open PO value is concentrated in a few suppliers | Supplier dependency and cash commitment may be concentrated | Review supplier concentration and staged delivery options | Open PO value by supplier |

## Recommended operating cadence

1. Review stockout exceptions daily and confirm receipts before creating new orders.
2. Review replenishment quantities weekly with demand plans, MOQ, case pack, and transfer data.
3. Review supplier delivery scorecards monthly with procurement.
4. Review overstock and inventory-turn trends monthly with merchandising and finance.
5. Reconcile dashboard totals to the source WMS/ERP before using results in a business decision.

## Analyst validation checklist

- Confirm the inventory snapshot timestamp and whether quantities are sellable, reserved, or in transit.
- Confirm cost basis, target stock, reorder point, and promised/received date semantics.
- Check SKU and location uniqueness, missing values, duplicate snapshots, and unit consistency.
- Compare KPI totals with an approved operational report for the same date range.
- Record the owner, expected impact, due date, and success measure for each accepted action.
