from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st


CATEGORIES = [
    "Electronics",
    "Home & Kitchen",
    "Personal Care",
    "Sports & Outdoors",
    "Office Supplies",
    "Fashion",
]
SUPPLIERS = [
    "Apex Wholesale",
    "BluePeak Supply",
    "Cedar Distribution",
    "Delta Merchants",
    "Evergreen Goods",
    "Northstar Trading",
]
LOCATIONS = [
    ("Delhi Hub", "North"),
    ("Jaipur Hub", "North"),
    ("Mumbai Hub", "West"),
    ("Pune Hub", "West"),
    ("Bengaluru Hub", "South"),
    ("Chennai Hub", "South"),
    ("Kolkata Hub", "East"),
    ("Hyderabad Hub", "Central"),
]
PRODUCT_NAMES = [
    "Wireless mouse", "USB-C charger", "Bluetooth speaker", "Desk lamp",
    "Storage basket", "Insulated bottle", "Cotton bedsheet", "Air fryer",
    "Yoga mat", "Resistance bands", "Notebook set", "Ergonomic chair",
    "Face cleanser", "Hair dryer", "Travel backpack", "LED monitor",
    "Ceramic cookware", "Water filter", "Running shoes", "Power bank",
    "Keyboard", "Bath towel set", "Lunch container", "Smart plug",
    "Yoga block", "Paper ream", "Wireless earbuds", "Floor cushion",
    "Electric kettle", "Camping lantern", "Drawing pencils", "Coffee grinder",
    "Phone stand", "Hand blender", "First aid kit", "Laptop sleeve",
]


@st.cache_data(ttl=3600)
def load_demo_data(days: int = 180) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create a stable, fictional retail inventory and purchase-order dataset."""
    rng = np.random.default_rng(20260930)
    today = pd.Timestamp.today().normalize()
    dates = pd.date_range(end=today, periods=days, freq="D")
    products: list[dict[str, object]] = []

    for index, name in enumerate(PRODUCT_NAMES):
        category = CATEGORIES[index % len(CATEGORIES)]
        supplier = SUPPLIERS[(index * 5 + index // 4) % len(SUPPLIERS)]
        lead_time = int(rng.integers(4, 22))
        average_demand = int(rng.integers(4, 23))
        target_stock = int(max(45, average_demand * lead_time * rng.uniform(1.2, 2.0)))
        products.append(
            {
                "sku": f"SKU-{index + 101:04d}",
                "product_name": name,
                "category": category,
                "supplier": supplier,
                "unit_cost": round(float(rng.uniform(180, 14500)), 2),
                "lead_time_days": lead_time,
                "average_daily_demand": average_demand,
                "reorder_point": max(10, int(target_stock * 0.42)),
                "target_stock": target_stock,
            }
        )

    snapshot_rows: list[dict[str, object]] = []
    for product in products:
        for location, region in LOCATIONS:
            location_factor = float(rng.uniform(0.72, 1.3))
            base_stock = product["target_stock"] * float(rng.uniform(0.7, 1.4))
            for day_index, snapshot_date in enumerate(dates):
                seasonal_factor = 1 + 0.12 * np.sin(2 * np.pi * day_index / 90)
                demand = max(
                    1,
                    int(
                        rng.poisson(
                            product["average_daily_demand"]
                            * location_factor
                            * seasonal_factor
                        )
                    ),
                )
                if rng.random() < 0.035:
                    on_hand = 0
                else:
                    drift = 0.08 * product["target_stock"] * np.sin(
                        2 * np.pi * day_index / 45
                    )
                    stock = base_stock + drift + rng.normal(
                        0, product["target_stock"] * 0.2
                    )
                    if rng.random() < 0.06:
                        stock += product["target_stock"] * rng.uniform(0.5, 1.4)
                    on_hand = max(0, int(stock))

                snapshot_rows.append(
                    {
                        "snapshot_date": snapshot_date,
                        "sku": product["sku"],
                        "product_name": product["product_name"],
                        "category": product["category"],
                        "supplier": product["supplier"],
                        "region": region,
                        "location": location,
                        "unit_cost": product["unit_cost"],
                        "on_hand": on_hand,
                        "daily_demand": demand,
                        "unfilled_units": max(0, demand - on_hand),
                        "inventory_value": round(on_hand * product["unit_cost"], 2),
                        "lead_time_days": product["lead_time_days"],
                        "average_daily_demand": round(
                            product["average_daily_demand"] * location_factor, 2
                        ),
                        "reorder_point": product["reorder_point"],
                        "target_stock": product["target_stock"],
                    }
                )

    snapshots = pd.DataFrame(snapshot_rows)
    snapshots["stockout"] = snapshots["on_hand"].eq(0)
    snapshots["days_of_cover"] = (
        snapshots["on_hand"] / snapshots["average_daily_demand"].clip(lower=1)
    ).round(1)

    purchase_rows: list[dict[str, object]] = []
    for order_number in range(420):
        product = products[int(rng.integers(0, len(products)))]
        location, region = LOCATIONS[int(rng.integers(0, len(LOCATIONS)))]
        order_date = dates[int(rng.integers(0, len(dates))) - 1]
        promised_date = order_date + pd.Timedelta(days=int(product["lead_time_days"]))
        received_date: pd.Timestamp | pd.NaT = pd.NaT
        if promised_date > today:
            status = "In transit"
            if (promised_date - today).days > 10 and rng.random() < 0.08:
                status = "Delayed"
        else:
            delay = int(rng.integers(-3, 9))
            estimated_received = promised_date + pd.Timedelta(days=delay)
            if estimated_received > today:
                status = "Delayed"
            else:
                status = "Received"
                received_date = estimated_received

        quantity = int(rng.integers(40, 420))
        purchase_rows.append(
            {
                "po_number": f"PO-{order_number + 8401:05d}",
                "order_date": order_date,
                "promised_date": promised_date,
                "received_date": received_date,
                "status": status,
                "sku": product["sku"],
                "product_name": product["product_name"],
                "category": product["category"],
                "supplier": product["supplier"],
                "region": region,
                "location": location,
                "ordered_units": quantity,
                "po_value": round(quantity * product["unit_cost"], 2),
                "lead_time_days": product["lead_time_days"],
            }
        )

    orders = pd.DataFrame(purchase_rows)
    return pd.DataFrame(products), snapshots, orders
