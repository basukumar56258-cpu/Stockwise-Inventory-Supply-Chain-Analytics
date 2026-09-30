from __future__ import annotations

import plotly.express as px
import streamlit as st

from src.analysis import (
    category_summary,
    inventory_kpis,
    inventory_positions,
    latest_snapshot,
    location_summary,
    monthly_trends,
)
from src.ui import display_inventory_table, format_inr, get_filtered_context


_, snapshots, orders = get_filtered_context()
current = inventory_positions(snapshots)
kpis = inventory_kpis(snapshots, orders)

st.title("Inventory control tower", icon=":material/dashboard:")
st.caption("A decision-ready view of stock availability, working capital and supply risk.")

with st.container(horizontal=True):
    st.metric("Inventory value", format_inr(kpis["inventory_value"]), border=True)
    st.metric("Stockout rate", f"{kpis['stockout_rate']:.1f}%", border=True)
    st.metric("Inventory turns", f"{kpis['inventory_turns']:.1f}x", border=True)
    st.metric("Days of cover", f"{kpis['days_of_cover']:.0f} days", border=True)
    st.metric("Fill rate", f"{kpis['fill_rate']:.1f}%", border=True)

trend = monthly_trends(snapshots)
if current.empty:
    st.info("No inventory rows match these filters. Widen the filter selection to continue.")
else:
    left, right = st.columns([1.55, 1], gap="medium")
    with left:
        with st.container(border=True):
            st.subheader("Inventory value trend")
            fig = px.line(
                trend,
                x="snapshot_date",
                y="inventory_value",
                markers=True,
                labels={"snapshot_date": "Month", "inventory_value": "Average stock value (INR)"},
            )
            fig.update_traces(line_color="#2478C3", line_width=3)
            fig.update_layout(height=300, margin=dict(l=8, r=8, t=18, b=8), showlegend=False)
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    with right:
        with st.container(border=True):
            st.subheader("Current stock position")
            status_counts = (
                current["stock_status"].value_counts().rename_axis("status").reset_index(name="items")
            )
            fig = px.pie(
                status_counts,
                names="status",
                values="items",
                hole=0.62,
                color="status",
                color_discrete_map={
                    "Healthy": "#2AA876",
                    "Reorder now": "#E9A23B",
                    "Stockout": "#D94F4F",
                    "Overstock": "#3984D6",
                },
            )
            fig.update_layout(height=300, margin=dict(l=8, r=8, t=18, b=8), legend_title_text="")
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    categories = category_summary(current)
    locations = location_summary(current)
    left, right = st.columns(2, gap="medium")
    with left:
        with st.container(border=True):
            st.subheader("Stock value by category")
            fig = px.bar(
                categories.sort_values("inventory_value"),
                x="inventory_value",
                y="category",
                orientation="h",
                color="category",
                labels={"inventory_value": "Stock value (INR)", "category": "Category"},
            )
            fig.update_layout(height=320, showlegend=False, margin=dict(l=8, r=8, t=18, b=8))
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    with right:
        with st.container(border=True):
            st.subheader("Stockout rate by location")
            fig = px.bar(
                locations.sort_values("stockout_rate"),
                x="stockout_rate",
                y="location",
                orientation="h",
                color="stockout_rate",
                color_continuous_scale=["#69BF98", "#F0BC56", "#D94F4F"],
                labels={"stockout_rate": "Stockout rate (%)", "location": "Location"},
            )
            fig.update_layout(height=320, coloraxis_showscale=False, margin=dict(l=8, r=8, t=18, b=8))
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    st.subheader("Items needing attention")
    risks = current.loc[current["stock_status"].isin(["Stockout", "Reorder now"])].copy()
    risks = risks.sort_values(["stock_status", "reorder_value"], ascending=[True, False]).head(10)
    if risks.empty:
        st.success("No stockout or reorder-point exceptions in this view.")
    else:
        st.dataframe(display_inventory_table(risks), hide_index=True, width="stretch")

st.caption("Fictional demo data · Snapshot date: " + str(latest_snapshot(snapshots)["snapshot_date"].max().date()) if not snapshots.empty else "Fictional demo data")
