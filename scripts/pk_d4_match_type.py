"""UK+IE vs the rest by match type, weekly SA360 keyword data (round 4, D4).

Usage: python scripts/pk_d4_match_type.py data/sa360_round4/d4_weekly_keywords.parquet

Note: qr_booking_conversions is all_conversions (attributed, includes cross-device), so levels are
about 3.5x the transaction ledger. Use it for comparisons between groups and periods only.
"""
import sys

import numpy as np
import pandas as pd

pd.set_option("display.width", 250)
pd.set_option("display.max_rows", 200)


def main(path: str) -> None:
    d = pd.read_parquet(path)
    d["week"] = pd.to_datetime(d.week)
    d["period"] = pd.cut(d.week, pd.to_datetime(["2026-06-01", "2026-08-17", "2026-08-31", "2026-09-21", "2026-10-12"]),
                         right=False, labels=["1 Jun-16 Aug", "17-30 Aug", "31 Aug-20 Sep", "21 Sep-5 Oct"])
    d["group"] = np.where(d.segment.str.contains("GB|UK"), "UK+IE", d.segment)
    t = d.groupby(["group", "match_type", "period"], observed=True).agg(
        cost=("cost", "sum"), clicks=("clicks", "sum"), bookings=("qr_booking_conversions", "sum"))
    t["cpc"] = t.cost / t.clicks
    t["bookings per 1k clicks"] = t.bookings / t.clicks * 1000
    t["click share %"] = t.clicks / t.groupby(["group", "period"], observed=True).clicks.transform("sum") * 100
    print(t.round(2).to_string())


if __name__ == "__main__":
    main(sys.argv[1])
