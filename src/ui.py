from __future__ import annotations

import pandas as pd
import streamlit as st

from src.analysis import filter_orders, filter_snapshots, inventory_positions
from src.data import load_demo_data


def render_sidebar_filters(snapshots: pd.DataFrame) -> dict[str, object]:
    start = snapshots["snapshot_date"].min().date()
    end = snapshots["snapshot_date"].max().date()
    with st.sidebar:
        st.subheader("Filters")
        selected_dates = st.date_input(
            "Snapshot date range",
            value=(start, end),
            min_value=start,
            max_value=end,
            key="global_snapshot_range",
        )
        if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
            date_start, date_end = selected_dates
        else:
            date_start, date_end = start, end

        regions = sorted(snapshots["region"].unique().tolist())
        categories = sorted(snapshots["category"].unique().tolist())
        suppliers = sorted(snapshots["supplier"].unique().tolist())
        locations = sorted(snapshots["location"].unique().tolist())
        selected_regions = st.multiselect("Region", regions, default=regions, key="global_regions")
        selected_categories = st.multiselect(
            "Category", categories, default=categories, key="global_categories"
        )
        selected_suppliers = st.multiselect(
            "Supplier", suppliers, default=suppliers, key="global_suppliers"
        )
        selected_locations = st.multiselect(
            "Location", locations, default=locations, key="global_locations"
        )

    return {
        "start_date": date_start,
        "end_date": date_end,
        "regions": selected_regions,
        "categories": selected_categories,
        "suppliers": selected_suppliers,
        "locations": selected_locations,
    }


def get_filtered_context() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    products, snapshots, orders = load_demo_data()
    filters = st.session_state.get("inventory_filters")
    if not filters:
        return products, snapshots, orders

    filtered_snapshots = filter_snapshots(snapshots, **filters)
    filtered_orders = filter_orders(
        orders,
        filters["start_date"],
        filters["end_date"],
        filters["regions"],
        filters["suppliers"],
        filters["locations"],
    )
    return products, filtered_snapshots, filtered_orders


def format_inr(value: float) -> str:
    rounded = str(int(round(value)))
    if len(rounded) <= 3:
        return f"₹{rounded}"
    last_three = rounded[-3:]
    remaining = rounded[:-3]
    groups: list[str] = []
    while remaining:
        groups.insert(0, remaining[-2:])
        remaining = remaining[:-2]
    return f"₹{','.join(groups)},{last_three}"


def display_inventory_table(frame: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "sku",
        "product_name",
        "category",
        "region",
        "location",
        "supplier",
        "on_hand",
        "reorder_point",
        "days_of_cover",
        "stock_status",
        "reorder_quantity",
        "reorder_value",
    ]
    visible = frame[[column for column in columns if column in frame]].copy()
    return visible.rename(
        columns={
            "sku": "SKU",
            "product_name": "Product",
            "category": "Category",
            "region": "Region",
            "location": "Location",
            "supplier": "Supplier",
            "on_hand": "Units on hand",
            "reorder_point": "Reorder point",
            "days_of_cover": "Days of cover",
            "stock_status": "Stock status",
            "reorder_quantity": "Suggested order qty",
            "reorder_value": "Suggested order value (INR)",
        }
    )
