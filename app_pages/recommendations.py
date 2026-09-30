from __future__ import annotations

import pandas as pd
import streamlit as st

from src.analysis import build_recommendations, inventory_kpis, inventory_positions, replenishment_plan
from src.ui import display_inventory_table, format_inr, get_filtered_context


_, snapshots, orders = get_filtered_context()
recommendations = build_recommendations(snapshots, orders)
kpis = inventory_kpis(snapshots, orders)
positions = inventory_positions(snapshots)
plan = replenishment_plan(snapshots)

st.title("Recommendations", icon=":material/lightbulb:")
st.caption("Translate inventory signals into prioritized, measurable business actions.")

if not recommendations:
    st.info("No recommendations can be calculated for the current filters.")
else:
    priority_colors = {"Urgent": "red", "High": "orange", "Medium": "blue", "Monitor": "green"}
    for item in recommendations:
        color = priority_colors.get(item["priority"], "gray")
        with st.container(border=True):
            st.badge(item["priority"], color=color)
            st.markdown(f"**{item['area']}**")
            st.write(item["finding"])
            st.caption("Recommended action: " + item["action"])

left, right = st.columns(2, gap="medium")
with left:
    with st.container(border=True):
        st.subheader("Replenishment exposure")
        st.metric("Suggested order value", format_inr(float(plan["reorder_value"].sum()) if not plan.empty else 0))
        st.metric("SKU-location pairs to review", f"{len(plan):,}")
        if not plan.empty:
            st.dataframe(display_inventory_table(plan.head(8)), hide_index=True, width="stretch")
with right:
    with st.container(border=True):
        st.subheader("Working-capital and service guardrails")
        st.metric("Current fill rate", f"{kpis['fill_rate']:.1f}%")
        st.metric("Current days of cover", f"{kpis['days_of_cover']:.1f} days")
        st.write("Use the replenishment quantity as a starting point. Confirm demand plans, supplier minimums and transfer options before issuing a purchase order.")

with st.expander("How the recommendations are generated"):
    st.markdown(
        "- Stockout and reorder flags are evaluated at the SKU-location level.\n"
        "- Reorder quantity is the gap between target stock and on-hand units.\n"
        "- Overstock is inventory above 1.5 times target stock.\n"
        "- Supplier on-time rate uses received purchase orders only; open orders are excluded from the denominator.\n"
        "- All figures in this starter project use fictional demonstration data."
    )
