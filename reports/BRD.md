# Business Requirements Document

## Project

**Stockwise: Retail Inventory & Supply Chain Analytics**

## Business problem

Retail operations teams need to balance product availability against working capital. Inventory, demand, and purchase-order signals are often spread across spreadsheets, making it difficult to identify low-stock items, slow-moving excess, and supplier delivery risk in one place.

## Objective

Provide an interactive, decision-oriented view that helps inventory planners prioritize replenishment, investigate supplier delays, and compare warehouse risk.

## Stakeholders

- Inventory planner: prioritizes SKU-location replenishment.
- Procurement analyst: monitors supplier reliability and open purchase orders.
- Warehouse manager: compares availability and stock cover between locations.
- Operations leader: monitors service level and working capital.
- Business analyst: documents KPI definitions, validates data, and translates patterns into actions.

## Scope

### In scope

- Global date, region, category, supplier, and location filters.
- Inventory value, stockout rate, inventory turns, days of cover, and fill-rate KPIs.
- Stock classification and suggested reorder quantity/value.
- Supplier on-time scorecard and delayed/open PO views.
- Warehouse comparison and dynamic business recommendations.
- Downloadable replenishment exception list.

### Out of scope

- Creating or transmitting purchase orders.
- Live ERP/WMS integration, authentication, and role-based access.
- Statistical demand forecasting or automatic safety-stock optimization.
- Real company data; the included dataset is fictional demonstration data.

## Functional requirements

1. Users can filter all views by a snapshot-date range, region, category, supplier, and location.
2. The overview shows the latest selected snapshot alongside trend context from the selected period.
3. Inventory health classifies each SKU-location pair using the documented stock rules.
4. The replenishment plan calculates order quantity as target stock less on-hand, with a floor of zero.
5. Supplier scorecards calculate on-time rate only from received purchase orders.
6. Location analysis compares inventory value, days of cover, and stockout rate.
7. Recommendations state the finding, priority, and proposed operational action.
8. Users can download the filtered replenishment plan as CSV.
9. Empty filter results produce a clear message rather than a runtime error.

## Acceptance criteria

- The demo starts without an external database or data download.
- Global filters affect the visible analyses consistently.
- KPI and stock classification logic is unit-tested.
- Zero denominators and empty result sets are handled safely.
- The UI labels demo data as fictional and exposes calculation assumptions.

## KPI definitions

| KPI | Definition |
|---|---|
| Inventory value | Sum of on-hand units multiplied by unit cost for the latest selected snapshot. |
| Stockout rate | Share of SKU-location rows with zero on-hand units in the latest selected snapshot. |
| Inventory turns | Annualized daily demand value divided by average daily inventory value in the selected period. |
| Days of cover | Latest on-hand units divided by average daily demand. |
| Fill rate | 1 minus unfilled units divided by demand units over the selected period. |
| Supplier on-time rate | Received purchase orders received on or before promised date divided by received purchase orders. |
| Overstock value | Unit cost multiplied by units above 1.5 times target stock. |

## Risks and assumptions

- Synthetic distributions are not calibrated to a specific retailer.
- Reorder quantity does not include supplier minimum order quantity, case-pack size, inbound stock, or transfer availability.
- Inventory turns use demand value as a proxy for cost of goods sold.
- Snapshot stockout is defined as zero on-hand; partial availability is reflected in fill rate.
- Production use requires data-quality checks, access control, and integration with authoritative inventory and PO systems.
