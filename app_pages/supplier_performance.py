from __future__ import annotations

import plotly.express as px
import pandas as pd
import streamlit as st

from src.analysis import supplier_summary
from src.ui import format_inr, get_filtered_context


_, _, orders = get_filtered_context()
summary = supplier_summary(orders)

st.title("Supplier performance", icon=":material/local_shipping:")
st.caption("Compare delivery reliability, open commitments and lead-time performance.")

if summary.empty:
    st.info("No purchase orders match these filters. Widen the filter selection to continue.")
else:
    delayed_count = int(orders["status"].eq("Delayed").sum())
    open_value = float(orders.loc[orders["status"].ne("Received"), "po_value"].sum())
    overall_on_time = float(
        orders.loc[orders["status"].eq("Received"), "received_date"].le(
            orders.loc[orders["status"].eq("Received"), "promised_date"]
        ).mean()
        * 100
    ) if orders["status"].eq("Received").any() else 0.0

    with st.container(horizontal=True):
        st.metric("Suppliers", f"{summary['supplier'].nunique():,}", border=True)
        st.metric("On-time delivery", f"{overall_on_time:.1f}%", border=True)
        st.metric("Delayed orders", f"{delayed_count:,}", border=True)
        st.metric("Open PO value", format_inr(open_value), border=True)

    left, right = st.columns([1.35, 1], gap="medium")
    with left:
        with st.container(border=True):
            st.subheader("On-time rate by supplier")
            fig = px.bar(
                summary.sort_values("on_time_rate"),
                x="on_time_rate",
                y="supplier",
                orientation="h",
                color="on_time_rate",
                color_continuous_scale=["#D94F4F", "#E9A23B", "#2AA876"],
                range_color=(0, 100),
                labels={"on_time_rate": "On-time delivery (%)", "supplier": "Supplier"},
            )
            fig.update_layout(height=350, coloraxis_showscale=False, margin=dict(l=8, r=8, t=18, b=8))
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    with right:
        with st.container(border=True):
            st.subheader("Purchase order status")
            status_counts = orders["status"].value_counts().rename_axis("status").reset_index(name="orders")
            fig = px.pie(
                status_counts,
                names="status",
                values="orders",
                hole=0.6,
                color="status",
                color_discrete_map={
                    "Received": "#2AA876",
                    "In transit": "#3984D6",
                    "Delayed": "#D94F4F",
                },
            )
            fig.update_layout(height=350, margin=dict(l=8, r=8, t=18, b=8), legend_title_text="")
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    st.subheader("Supplier scorecard")
    display = summary.rename(
        columns={
            "supplier": "Supplier",
            "purchase_orders": "Purchase orders",
            "on_time_rate": "On-time rate (%)",
            "avg_lead_time": "Avg lead time (days)",
            "delayed_orders": "Delayed orders",
            "open_value": "Open value (INR)",
        }
    )
    keep = [
        "Supplier",
        "Purchase orders",
        "On-time rate (%)",
        "Avg lead time (days)",
        "Delayed orders",
        "Open value (INR)",
    ]
    st.dataframe(display[keep].round(1), hide_index=True, width="stretch")

    st.subheader("Delayed purchase orders")
    delayed = orders.loc[orders["status"].eq("Delayed")].copy()
    if delayed.empty:
        st.success("No delayed purchase orders in this view.")
    else:
        delayed["overdue_days"] = (pd.Timestamp.today().normalize() - delayed["promised_date"]).dt.days.clip(lower=0)
        columns = ["po_number", "supplier", "product_name", "location", "promised_date", "overdue_days", "po_value"]
        st.dataframe(
            delayed[columns].sort_values("overdue_days", ascending=False).rename(
                columns={
                    "po_number": "PO number",
                    "supplier": "Supplier",
                    "product_name": "Product",
                    "location": "Location",
                    "promised_date": "Promised date",
                    "overdue_days": "Overdue days",
                    "po_value": "PO value (INR)",
                }
            ),
            hide_index=True,
            width="stretch",
        )
