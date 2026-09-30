import pandas as pd

from src.analysis import (
    filter_snapshots,
    inventory_kpis,
    inventory_positions,
    latest_snapshot,
    replenishment_plan,
)
from src.data import load_demo_data


def test_demo_data_has_expected_size_and_columns():
    products, snapshots, orders = load_demo_data(days=12)

    assert len(products) == 36
    assert snapshots["snapshot_date"].nunique() == 12
    assert {"sku", "on_hand", "reorder_point", "target_stock"}.issubset(
        snapshots.columns
    )
    assert {"po_number", "supplier", "status"}.issubset(orders.columns)


def test_latest_snapshot_uses_latest_date():
    _, snapshots, _ = load_demo_data(days=8)

    current = latest_snapshot(snapshots)

    assert current["snapshot_date"].nunique() == 1
    assert current["snapshot_date"].iloc[0] == snapshots["snapshot_date"].max()


def test_stock_status_and_reorder_quantity_are_calculated():
    snapshots = pd.DataFrame(
        {
            "snapshot_date": pd.to_datetime(["2026-09-29"] * 4),
            "sku": ["A", "B", "C", "D"],
            "on_hand": [0, 10, 110, 220],
            "reorder_point": [20, 20, 20, 20],
            "target_stock": [100, 100, 100, 100],
            "unit_cost": [10, 10, 10, 10],
            "inventory_value": [0, 100, 1100, 2200],
            "stockout": [True, False, False, False],
            "daily_demand": [4, 4, 4, 4],
            "unfilled_units": [4, 0, 0, 0],
            "average_daily_demand": [4, 4, 4, 4],
        }
    )

    positions = inventory_positions(snapshots)

    assert positions["stock_status"].tolist() == [
        "Stockout",
        "Reorder now",
        "Healthy",
        "Overstock",
    ]
    assert positions["reorder_quantity"].tolist() == [100, 90, 0, 0]


def test_filter_respects_date_region_and_category():
    _, snapshots, _ = load_demo_data(days=10)
    end_date = snapshots["snapshot_date"].max()

    filtered = filter_snapshots(
        snapshots,
        end_date - pd.Timedelta(days=2),
        end_date,
        ["North"],
        ["Electronics"],
        [],
        [],
    )

    assert filtered["snapshot_date"].nunique() == 3
    assert set(filtered["region"]) == {"North"}
    assert set(filtered["category"]) == {"Electronics"}


def test_kpis_are_finite_and_replenishment_only_includes_risks():
    _, snapshots, orders = load_demo_data(days=14)

    kpis = inventory_kpis(snapshots, orders)
    plan = replenishment_plan(snapshots)

    assert all(pd.notna(value) for value in kpis.values())
    assert 0 <= kpis["stockout_rate"] <= 100
    assert 0 <= kpis["fill_rate"] <= 100
    assert kpis["inventory_turns"] > 0
    assert set(plan["stock_status"]).issubset({"Stockout", "Reorder now"})
