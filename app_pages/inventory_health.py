from __future__ import annotations

import plotly.express as px
import streamlit as st

from src.analysis import inventory_positions, replenishment_plan
from src.ui import display_inventory_table, format_inr, get_filtered_context


_, snapshots, _ = get_filtered_context()
positions = inventory_positions(snapshots)
plan = replenishment_plan(snapshots)

st.title("Inventory health", icon=":material/inventory:")
st.caption("Find stockout exposure, replenishment priorities and excess working capital.")

if positions.empty:
    st.info("No inventory rows match these filters. Widen the filter selection to continue.")
else:
    stockouts = int(positions["stock_status"].eq("Stockout").sum())
    reorder_count = int(positions["stock_status"].eq("Reorder now").sum())
    overstock = positions.loc[positions["stock_status"].eq("Overstock")]
    excess_value = float(
        (overstock["on_hand"] - overstock["target_stock"] * 1.5).clip(lower=0).mul(overstock["unit_cost"]).sum()
    )
    with st.container(horizontal=True):
        st.metric("Stockout locations", f"{stockouts:,}", border=True)
        st.metric("Below reorder point", f"{reorder_count:,}", border=True)
        st.metric("Overstock value", format_inr(excess_value), border=True)
        st.metric("SKUs monitored", f"{positions['sku'].nunique():,}", border=True)

    status_counts = (
        positions["stock_status"].value_counts().rename_axis("status").reset_index(name="locations")
    )
    fig = px.bar(
        status_counts,
        x="status",
        y="locations",
        color="status",
        color_discrete_map={
            "Healthy": "#2AA876",
            "Reorder now": "#E9A23B",
            "Stockout": "#D94F4F",
            "Overstock": "#3984D6",
        },
        labels={"status": "Stock status", "locations": "SKU-location pairs"},
    )
    fig.update_layout(height=280, showlegend=False, margin=dict(l=8, r=8, t=18, b=8))
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    st.subheader("Replenishment plan")
    if plan.empty:
        st.success("No replenishment exceptions in this view.")
    else:
        st.dataframe(display_inventory_table(plan), hide_index=True, width="stretch")
        download = plan.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download replenishment plan",
            data=download,
            file_name="replenishment_plan.csv",
            mime="text/csv",
            icon=":material/download:",
        )

    with st.expander("Stock classification rules"):
        st.markdown(
            "- **Stockout:** on-hand quantity is zero.\n"
            "- **Reorder now:** on-hand quantity is at or below the reorder point.\n"
            "- **Overstock:** on-hand quantity is more than 1.5x target stock.\n"
            "- **Healthy:** none of the above."
        )
