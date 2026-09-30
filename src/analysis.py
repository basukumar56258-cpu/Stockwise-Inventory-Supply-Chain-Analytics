from __future__ import annotations

import numpy as np
import pandas as pd


def filter_snapshots(
    snapshots: pd.DataFrame,
    start_date: object,
    end_date: object,
    regions: list[str],
    categories: list[str],
    suppliers: list[str],
    locations: list[str],
) -> pd.DataFrame:
    filtered = snapshots.loc[
        snapshots["snapshot_date"].between(pd.Timestamp(start_date), pd.Timestamp(end_date))
    ]
    if regions:
        filtered = filtered.loc[filtered["region"].isin(regions)]
    if categories:
        filtered = filtered.loc[filtered["category"].isin(categories)]
    if suppliers:
        filtered = filtered.loc[filtered["supplier"].isin(suppliers)]
    if locations:
        filtered = filtered.loc[filtered["location"].isin(locations)]
    return filtered.copy()


def filter_orders(
    orders: pd.DataFrame,
    start_date: object,
    end_date: object,
    regions: list[str],
    suppliers: list[str],
    locations: list[str],
) -> pd.DataFrame:
    filtered = orders.loc[
        orders["order_date"].between(pd.Timestamp(start_date), pd.Timestamp(end_date))
    ]
    if regions:
        filtered = filtered.loc[filtered["region"].isin(regions)]
    if suppliers:
        filtered = filtered.loc[filtered["supplier"].isin(suppliers)]
    if locations:
        filtered = filtered.loc[filtered["location"].isin(locations)]
    return filtered.copy()


def latest_snapshot(snapshots: pd.DataFrame) -> pd.DataFrame:
    if snapshots.empty:
        return snapshots.copy()
    latest_date = snapshots["snapshot_date"].max()
    return snapshots.loc[snapshots["snapshot_date"].eq(latest_date)].copy()


def inventory_positions(snapshots: pd.DataFrame) -> pd.DataFrame:
    current = latest_snapshot(snapshots)
    if current.empty:
        return current

    current["stock_status"] = np.select(
        [
            current["on_hand"].le(0),
            current["on_hand"].le(current["reorder_point"]),
            current["on_hand"].gt(current["target_stock"] * 1.5),
        ],
        ["Stockout", "Reorder now", "Overstock"],
        default="Healthy",
    )
    current["reorder_quantity"] = (current["target_stock"] - current["on_hand"]).clip(
        lower=0
    )
    current["reorder_value"] = current["reorder_quantity"] * current["unit_cost"]
    return current


def inventory_kpis(snapshots: pd.DataFrame, orders: pd.DataFrame) -> dict[str, float]:
    current = latest_snapshot(snapshots)
    if current.empty:
        return {
            "inventory_value": 0.0,
            "stockout_rate": 0.0,
            "inventory_turns": 0.0,
            "days_of_cover": 0.0,
            "fill_rate": 0.0,
            "open_po_value": 0.0,
        }

    valued_demand = snapshots.assign(
        demand_value=snapshots["daily_demand"] * snapshots["unit_cost"]
    )
    daily = valued_demand.groupby("snapshot_date", as_index=False).agg(
        inventory_value=("inventory_value", "sum"),
        demand_value=("demand_value", "sum"),
    )
    average_inventory = float(daily["inventory_value"].mean())
    annualized_demand_value = float(daily["demand_value"].mean()) * 365
    total_demand = float(snapshots["daily_demand"].sum())
    fill_rate = 100 * (1 - float(snapshots["unfilled_units"].sum()) / max(total_demand, 1))
    open_orders = orders.loc[orders["status"].ne("Received")] if not orders.empty else orders

    return {
        "inventory_value": float(current["inventory_value"].sum()),
        "stockout_rate": float(current["stockout"].mean() * 100),
        "inventory_turns": annualized_demand_value / max(average_inventory, 1),
        "days_of_cover": float(
            current["on_hand"].sum() / max(current["average_daily_demand"].sum(), 1)
        ),
        "fill_rate": max(0.0, min(100.0, fill_rate)),
        "open_po_value": float(open_orders["po_value"].sum()) if not open_orders.empty else 0.0,
    }


def monthly_trends(snapshots: pd.DataFrame) -> pd.DataFrame:
    if snapshots.empty:
        return pd.DataFrame(
            columns=["snapshot_date", "inventory_value", "demand_units", "stockout_rate"]
        )
    daily = snapshots.groupby("snapshot_date", as_index=False).agg(
        inventory_value=("inventory_value", "sum"),
        demand_units=("daily_demand", "sum"),
        stockout_rate=("stockout", "mean"),
    )
    monthly = daily.set_index("snapshot_date").resample("MS").agg(
        inventory_value=("inventory_value", "mean"),
        demand_units=("demand_units", "sum"),
        stockout_rate=("stockout_rate", "mean"),
    )
    monthly["stockout_rate"] *= 100
    return monthly.reset_index()


def category_summary(current: pd.DataFrame) -> pd.DataFrame:
    if current.empty:
        return pd.DataFrame()
    return (
        current.groupby("category", as_index=False)
        .agg(
            inventory_value=("inventory_value", "sum"),
            units_on_hand=("on_hand", "sum"),
            daily_demand=("daily_demand", "sum"),
            stockout_rate=("stockout", "mean"),
            sku_count=("sku", "nunique"),
        )
        .assign(stockout_rate=lambda frame: frame["stockout_rate"] * 100)
        .sort_values("inventory_value", ascending=False)
    )


def location_summary(current: pd.DataFrame) -> pd.DataFrame:
    if current.empty:
        return pd.DataFrame()
    return (
        current.groupby(["region", "location"], as_index=False)
        .agg(
            inventory_value=("inventory_value", "sum"),
            units_on_hand=("on_hand", "sum"),
            daily_demand=("average_daily_demand", "sum"),
            stockout_rate=("stockout", "mean"),
        )
        .assign(
            stockout_rate=lambda frame: frame["stockout_rate"] * 100,
            days_of_cover=lambda frame: frame["units_on_hand"]
            / frame["daily_demand"].clip(lower=1),
        )
        .sort_values("inventory_value", ascending=False)
    )


def supplier_summary(orders: pd.DataFrame) -> pd.DataFrame:
    if orders.empty:
        return pd.DataFrame()
    orders = orders.copy()
    orders["open_value"] = orders["po_value"].where(orders["status"].ne("Received"), 0)
    summary = orders.groupby("supplier").agg(
        purchase_orders=("po_number", "nunique"),
        open_value=("open_value", "sum"),
        delayed_orders=("status", lambda values: values.eq("Delayed").sum()),
        received_orders=("status", lambda values: values.eq("Received").sum()),
    )
    received = orders.loc[orders["status"].eq("Received")].copy()
    received["on_time"] = received["received_date"].le(received["promised_date"])
    performance = received.groupby("supplier").agg(
        on_time_orders=("on_time", "sum"),
        avg_lead_time=("lead_time_days", "mean"),
    )
    summary = summary.join(performance)
    summary["on_time_orders"] = summary["on_time_orders"].fillna(0)
    summary["on_time_rate"] = (
        100 * summary["on_time_orders"].fillna(0) / summary["received_orders"].clip(lower=1)
    )
    summary["avg_lead_time"] = summary["avg_lead_time"].fillna(0)
    return summary.reset_index().sort_values("on_time_rate")


def replenishment_plan(snapshots: pd.DataFrame) -> pd.DataFrame:
    positions = inventory_positions(snapshots)
    if positions.empty:
        return positions
    plan = positions.loc[positions["stock_status"].isin(["Stockout", "Reorder now"])].copy()
    return plan.sort_values(["stock_status", "reorder_value"], ascending=[True, False])


def build_recommendations(
    snapshots: pd.DataFrame, orders: pd.DataFrame
) -> list[dict[str, str]]:
    current = inventory_positions(snapshots)
    if current.empty:
        return []

    recommendations: list[dict[str, str]] = []
    stockout_count = int(current["stock_status"].eq("Stockout").sum())
    reorder_count = int(current["stock_status"].eq("Reorder now").sum())
    excess_value = float(
        (current["on_hand"].sub(current["target_stock"] * 1.5).clip(lower=0)
         * current["unit_cost"]).sum()
    )
    if stockout_count or reorder_count:
        recommendations.append(
            {
                "priority": "Urgent" if stockout_count else "High",
                "area": "Replenishment",
                "finding": f"{stockout_count} SKU-location pairs are out of stock and {reorder_count} are below reorder point.",
                "action": "Prioritize the replenishment plan by stockout risk and estimated order value.",
            }
        )
    if excess_value > 0:
        recommendations.append(
            {
                "priority": "Medium",
                "area": "Working capital",
                "finding": f"Estimated excess inventory is worth ₹{excess_value:,.0f}.",
                "action": "Pause replenishment on overstocked items and review transfer or promotion options.",
            }
        )
    suppliers = supplier_summary(orders)
    if not suppliers.empty:
        lowest = suppliers.iloc[0]
        if float(lowest["on_time_rate"]) < 85:
            recommendations.append(
                {
                    "priority": "High",
                    "area": "Supplier performance",
                    "finding": f"{lowest['supplier']} has the lowest on-time rate at {lowest['on_time_rate']:.0f}%.",
                    "action": "Review recent late purchase orders and agree a corrective lead-time plan.",
                }
            )
    if not recommendations:
        recommendations.append(
            {
                "priority": "Monitor",
                "area": "Inventory health",
                "finding": "No critical stock or supplier risk is visible in the selected filters.",
                "action": "Keep monitoring service levels and avoid ordering above target stock.",
            }
        )
    return recommendations
