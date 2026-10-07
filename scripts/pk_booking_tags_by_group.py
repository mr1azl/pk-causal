"""Booking rate per click on both booking actions, and search value vs booking value, by destination group.

Usage: python scripts/pk_booking_tags_by_group.py data/sa360_round3 data/sa360_round3/c1_campaign_daily_shares.parquet

QR_Booking is the Floodlight transaction tag; Booking is the Google Ads webpage tag (data-driven
attribution). They are independent measurements of the same bookings.
"""
import os
import sys

import pandas as pd

pd.set_option("display.width", 250)


def main(folder: str, traffic_path: str) -> None:
    conv = pd.read_parquet(os.path.join(folder, "pk_nb_daily_2026.parquet"))
    traffic = pd.read_parquet(traffic_path)
    for x in (conv, traffic):
        x["period"] = pd.cut(pd.to_datetime(x.date), pd.to_datetime(["2026-07-01", "2026-09-02", "2026-10-06"]),
                             right=False, labels=["1 Jul-1 Sep", "2 Sep-5 Oct"])
    key = ["dest_group", "period"]
    t = traffic.groupby(key, observed=True).agg(clicks=("clicks", "sum"), cost=("cost", "sum"))
    for action in ("QR_Booking", "Booking", "QR_FlightSearch_VBB"):
        a = conv[conv.conversion_action == action].groupby(key, observed=True)
        t = t.join(a.all_conversions.sum().rename(action)).join(a.all_conversions_value.sum().rename(f"{action}_value"))
    t = t[t.index.get_level_values(0).isin(["UK+IE", "long-haul", "regional"])]
    out = pd.DataFrame({
        "clicks": t.clicks, "cost": t.cost.round(0),
        "QR_Booking per 1k clicks": (t.QR_Booking / t.clicks * 1000).round(2),
        "Booking (Google tag) per 1k clicks": (t.Booking / t.clicks * 1000).round(2),
        "search value per click": (t.QR_FlightSearch_VBB_value / t.clicks).round(2),
        "booking value per click": (t.QR_Booking_value / t.clicks).round(2)})
    out["search value / booking value"] = (out["search value per click"] / out["booking value per click"]).round(1)
    print(out.to_string())


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
