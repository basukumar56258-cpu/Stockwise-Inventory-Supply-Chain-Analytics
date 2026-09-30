# Stockwise: Retail Inventory & Supply Chain Analytics

A Business Analyst portfolio project that turns inventory snapshots and purchase-order data into replenishment, supplier, and location decisions. The interface follows a compact analytics-dashboard layout with global filters, KPI cards, charts, exception tables, and prioritized actions.

## What it answers

- Which SKU-location pairs are out of stock or below their reorder point?
- How much working capital is tied up in inventory and overstock?
- Which suppliers miss promised delivery dates or hold the most open PO value?
- Which warehouse locations have the highest stockout exposure or lowest days of cover?
- What should the operations team review first?

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`.

## Test

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Pages

- **Overview:** inventory value, stockout rate, inventory turns, days of cover, fill rate, stock status, category and location charts.
- **Inventory health:** SKU-location exceptions and downloadable replenishment plan.
- **Supplier performance:** on-time rate, open commitments, delayed orders, and supplier scorecard.
- **Location analysis:** compare stock value, days of cover, and stockout rate by warehouse.
- **Recommendations:** prioritized actions with the rules and assumptions behind each metric.

## Demo data and assumptions

The app generates a deterministic fictional dataset at runtime: 36 SKUs, six categories, six suppliers, eight warehouse locations across five regions, 180 daily inventory snapshots, and 420 purchase orders. Figures are illustrative and should not be presented as real company performance. Uploading an operational dataset is not yet enabled; replace `load_demo_data()` in `src/data.py` with a validated data source when one is available.

**Stock status:** Stockout = zero units on hand; Reorder now = on-hand at or below reorder point; Overstock = on-hand greater than 1.5 times target stock; otherwise Healthy.

**Fill rate:** one minus unfilled units divided by demand units, aggregated over the selected snapshot period. **On-time delivery:** received POs received on or before their promised date; open POs are excluded from the rate.

## Project structure

```text
app.py
app_pages/
src/
reports/
sql/
tests/
.streamlit/config.toml
requirements.txt
```
