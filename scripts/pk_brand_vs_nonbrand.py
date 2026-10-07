"""PK brand vs non-brand bookings and revenue by click month, 2025 and 2026 (Adobe).

Usage: python scripts/pk_brand_vs_nonbrand.py data/adobe/v84_pk_2025-05-01_2026-10-05.parquet
"""
import sys

import pandas as pd

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from pk_seasonality_adobe import load  # noqa: E402

pd.set_option("display.width", 250)


def monthly(x: pd.DataFrame) -> pd.DataFrame:
    first = x[x.day == x.click_day]
    month = x.click_day.dt.to_period("M")
    t = pd.DataFrame({"clicks": first.groupby(first.click_day.dt.to_period("M")).size(),
                      "bookings": x.groupby(month).bookings.sum(), "revenue": x.groupby(month).revenue.sum()})
    t["bookings per 1k clicks"] = t.bookings / t.clicks * 1000
    return t


def main(path: str) -> None:
    d = load(path)
    brand, nonbrand = monthly(d[d.seg == "Brand"]), monthly(d[d.seg.str.startswith("NB")])
    total = (brand[["bookings", "revenue"]] + nonbrand[["bookings", "revenue"]])
    for year in (2025, 2026):
        months = [pd.Period(f"{year}-{m}") for m in ("07", "08", "09")]
        print(year)
        print(pd.concat({"brand": brand.loc[months], "non-brand": nonbrand.loc[months], "total": total.loc[months]},
                        axis=1).round(1).to_string(), "\n")


if __name__ == "__main__":
    main(sys.argv[1])
