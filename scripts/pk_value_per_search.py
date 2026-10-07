"""What the bidder sees: VBB search value per click and per dollar vs booking revenue, by destination group.

Usage: python scripts/pk_value_per_search.py data/sa360_round3
"""
import os
import sys

import pandas as pd

pd.set_option("display.width", 250)
EDGES = pd.to_datetime(["2026-06-13", "2026-08-20", "2026-09-02", "2026-09-20", "2026-10-06"])
LABELS = ["13 Jun-19 Aug", "20 Aug-1 Sep", "2-19 Sep", "20 Sep-5 Oct"]


def main(folder: str) -> None:
    conv = pd.read_parquet(os.path.join(folder, "pk_nb_daily_2026.parquet"))
    traffic = pd.read_parquet(os.path.join(folder, "pk_nb_traffic_2026.parquet"))
    for x in (conv, traffic):
        x["period"] = pd.cut(pd.to_datetime(x.date), EDGES, right=False, labels=LABELS)
    key = ["dest_group", "period"]
    vbb = conv[conv.conversion_action == "QR_FlightSearch_VBB"].groupby(key, observed=True).agg(
        searches=("all_conversions", "sum"), search_value=("all_conversions_value", "sum"))
    bk = conv[conv.conversion_action == "QR_Booking"].groupby(key, observed=True).agg(
        booking_value=("all_conversions_value", "sum"))
    out = traffic.groupby(key, observed=True).agg(clicks=("clicks", "sum"), cost=("cost", "sum")).join(vbb).join(bk)
    out = out[out.index.get_level_values(0).isin(["UK+IE", "long-haul", "regional"])]
    out["searches per click"] = out.searches / out.clicks
    out["value per search"] = out.search_value / out.searches
    out["search value per click"] = out.search_value / out.clicks
    out["search value per $"] = out.search_value / out.cost
    out["booking revenue per click"] = out.booking_value / out.clicks
    print(out.drop(columns=["searches", "search_value", "booking_value"]).round(2).to_string())


if __name__ == "__main__":
    main(sys.argv[1])
