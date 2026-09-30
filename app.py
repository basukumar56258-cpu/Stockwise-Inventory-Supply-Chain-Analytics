from __future__ import annotations

import streamlit as st

from src.data import load_demo_data
from src.ui import render_sidebar_filters


st.set_page_config(
    page_title="Stockwise | Inventory control tower",
    page_icon=":material/inventory_2:",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.markdown("## :material/inventory_2: Stockwise")
st.sidebar.caption("Retail inventory & supply chain analytics")

pages = st.navigation(
    {
        "Workspace": [
            st.Page(
                "app_pages/overview.py",
                title="Overview",
                icon=":material/dashboard:",
                default=True,
            ),
            st.Page(
                "app_pages/inventory_health.py",
                title="Inventory health",
                icon=":material/inventory:",
            ),
        ],
        "Operations": [
            st.Page(
                "app_pages/supplier_performance.py",
                title="Supplier performance",
                icon=":material/local_shipping:",
            ),
            st.Page(
                "app_pages/location_analysis.py",
                title="Location analysis",
                icon=":material/location_on:",
            ),
        ],
        "Decision support": [
            st.Page(
                "app_pages/recommendations.py",
                title="Recommendations",
                icon=":material/lightbulb:",
            ),
        ],
    },
    position="sidebar",
)

_, all_snapshots, _ = load_demo_data()
st.session_state["inventory_filters"] = render_sidebar_filters(all_snapshots)

with st.sidebar:
    st.caption("DEMO DATA · 36 SKUs · 8 locations · 180 days")
    st.caption("Built with Python, Streamlit, Pandas and Plotly")

pages.run()
