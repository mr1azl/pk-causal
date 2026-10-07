"""Checks on the SA360 round 3 pull: seasonality per click, and the Floodlight ledger against Adobe.

Usage: python scripts/pk_sa360_round3_checks.py <round3_dir> <pk_nb.parquet or v84.parquet>

<round3_dir> is the agent's folder (data/clean/pk_nb_daily_YYYY.csv, pk_nb_traffic_YYYY.csv,
data/raw/b2_booking_conversions.jsonl with order IDs already hashed).
"""
import json
import os
import sys

import pandas as pd

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 30)
GROUPS = ["UK+IE", "long-haul", "regional"]


def per_click(r3: str) -> pd.DataFrame:
    rows = []
    for year in ("2025", "2026"):
        conv = pd.read_csv(os.path.join(r3, "data/clean", f"pk_nb_daily_{year}.csv"), parse_dates=["date"])
        traffic = pd.read_csv(os.path.join(r3, "data/clean", f"pk_nb_traffic_{year}.csv"), parse_dates=["date"])
        conv["month"], traffic["month"] = conv.date.dt.month, traffic.date.dt.month
        t = traffic.groupby(["dest_group", "month"]).agg(cost=("cost", "sum"), clicks=("clicks", "sum"))
        for action in ("QR_Booking", "Booking", "Flight Search"):
            t = t.join(conv[conv.conversion_action == action].groupby(["dest_group", "month"]).all_conversions.sum().rename(action))
        t["year"] = year
        rows.append(t.reset_index())
    out = pd.concat(rows)
    out = out[out.dest_group.isin(GROUPS) & out.month.isin([6, 7, 8, 9])]
    out["QR_Booking per 1k clicks"] = out.QR_Booking / out.clicks * 1000
    out["Booking per 1k clicks"] = out.Booking / out.clicks * 1000
    out["Flight Search per click"] = out["Flight Search"] / out.clicks
    return out.round(2).sort_values(["dest_group", "year", "month"])


def ledger_vs_adobe(r3: str, adobe_path: str) -> None:
    raw = [json.loads(line) for line in open(os.path.join(r3, "data/raw/b2_booking_conversions.jsonl"))]
    sa = pd.DataFrame([{"campaign": r["campaign"]["name"],
                        "day": r["conversion"]["conversionDateTime"][:10],
                        "revenue": int(r["conversion"].get("conversionRevenueMicros", 0)) / 1e6} for r in raw])
    sa["day"] = pd.to_datetime(sa.day)
    d = pd.read_parquet(adobe_path)
    if "cc" in d.columns:
        d = d[d.parsed & (d.cc == "PK") & (d.engine == "Google") & (d.group == "Non-brand")]
    ad = d[(d.bookings > 0) & d.day.between(sa.day.min(), sa.day.max())]
    print(f"Floodlight QR_Booking rows: {len(sa)}, revenue {sa.revenue.sum():,.0f}, "
          f"zero-revenue rows {int((sa.revenue <= 0).sum())}, {sa.day.min().date()} to {sa.day.max().date()}")
    print(f"Adobe PK non-brand bookings, same dates: {ad.bookings.sum():.0f}, revenue {ad.revenue.sum():,.0f}")
    key = lambda f: f.day.dt.strftime("%F") + "|" + f.campaign + "|" + f.revenue.round(0).astype(int).astype(str)
    matched = key(sa).isin(set(key(ad)))
    print(f"Floodlight rows with an identical Adobe row (same day, campaign and revenue to $1): {matched.sum()} of {len(sa)}")


def main(r3: str, adobe_path: str) -> None:
    print("== Bookings per click by month, 2025 vs 2026 (all_conversions, attributed)")
    print(per_click(r3).to_string(index=False), "\n")
    print("== Floodlight transaction ledger vs Adobe")
    ledger_vs_adobe(r3, adobe_path)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
