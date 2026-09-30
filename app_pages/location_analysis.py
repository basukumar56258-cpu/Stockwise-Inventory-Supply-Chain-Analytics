from __future__ import annotations

import plotly.express as px
import streamlit as st

from src.analysis import location_summary
from src.ui import format_inr, get_filtered_context


_, snapshots, _ = get_filtered_context()
current_date = snapshots["snapshot_date"].max() if not snapshots.empty else None
current = snapshots.loc[snapshots["snapshot_date"].eq(current_date)].copy() if current_date is not None else snapshots
summary = location_summary(current)

st.title("Location analysis", icon=":material/location_on:")
st.caption("Compare warehouse stock exposure and service risk across regions.")

if summary.empty:
    st.info("No location records match these filters. Widen the filter selection to continue.")
else:
    highest_value = summary.loc[summary["inventory_value"].idxmax()]
    highest_risk = summary.loc[summary["stockout_rate"].idxmax()]
    with st.container(horizontal=True):
        st.metric("Locations", f"{summary['location'].nunique():,}", border=True)
        st.metric("Regions", f"{summary['region'].nunique():,}", border=True)
        st.metric("Largest stock position", format_inr(float(highest_value["inventory_value"])), border=True)
        st.metric("Highest stockout rate", f"{highest_risk['stockout_rate']:.1f}%", border=True)

    left, right = st.columns(2, gap="medium")
    with left:
        with st.container(border=True):
            st.subheader("Inventory value by location")
            fig = px.bar(
                summary.sort_values("inventory_value"),
                x="inventory_value",
                y="location",
                orientation="h",
                color="region",
                labels={"inventory_value": "Stock value (INR)", "location": "Location", "region": "Region"},
            )
            fig.update_layout(height=380, margin=dict(l=8, r=8, t=18, b=8), legend_title_text="Region")
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    with right:
        with st.container(border=True):
            st.subheader("Days of cover by location")
            fig = px.bar(
                summary.sort_values("days_of_cover"),
                x="days_of_cover",
                y="location",
                orientation="h",
                color="days_of_cover",
                color_continuous_scale=["#E9A23B", "#3984D6", "#2AA876"],
                labels={"days_of_cover": "Days of cover", "location": "Location"},
            )
            fig.update_layout(height=380, coloraxis_showscale=False, margin=dict(l=8, r=8, t=18, b=8))
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    st.subheader("Location scorecard")
    display = summary.rename(
        columns={
            "region": "Region",
            "location": "Location",
            "inventory_value": "Inventory value (INR)",
            "units_on_hand": "Units on hand",
            "daily_demand": "Daily demand",
            "days_of_cover": "Days of cover",
            "stockout_rate": "Stockout rate (%)",
        }
    )
    st.dataframe(display.round(1), hide_index=True, width="stretch")
