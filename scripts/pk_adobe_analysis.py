"""PK non-brand on Adobe v84: periods, click cohorts, UK split.

Usage: python scripts/pk_adobe_analysis.py <v84.parquet>   (built by scripts/load_v84.py)

Bookings and revenue are assigned to the day the tracking ID (one per click, it carries the gclid)
first appears, so a booking made on 10 Sep from a click on 25 Aug counts for 25 Aug.
"""
import sys

import numpy as np
import pandas as pd

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)

EDGES = pd.to_datetime(["2026-05-01", "2026-06-13", "2026-08-20", "2026-09-02", "2026-09-20", "2026-10-06"])
LABELS = ["1 May-12 Jun", "13 Jun-19 Aug", "20 Aug-1 Sep (cut)", "2-19 Sep (switch)", "20 Sep-5 Oct"]
NDAYS = pd.Series(np.diff(EDGES).astype("timedelta64[D]").astype(int), index=LABELS)
UK = {"GB", "LHR", "MAN", "EDI", "LGW", "BHX", "LON", "GLA", "DUB", "IE", "NCL", "LBA", "BHD", "STN", "LTN", "ABZ"}


def main(path: str) -> None:
    d = pd.read_parquet(path)
    d = d[d.parsed]
    d = d.join(d.groupby("v84").day.min().rename("click_day"), on="v84")
    pk = d[(d.cc == "PK") & (d.engine == "Google") & d.group.isin(["Brand", "Non-brand"])].copy()
    parts = pk.campaign.str.split("|")
    new = parts.str.len() == 8
    pk["dest"] = np.where(new, parts.str[5], "legacy")
    pk["family"] = np.where(new, parts.str[2] + "/" + parts.str[3], "legacy")
    pk["seg"] = np.where(pk.group == "Brand", "Brand", np.where(pk.dest.isin(UK), "NB UK+IE", "NB other"))
    pk["period"] = pd.cut(pk.click_day, EDGES, right=False, labels=LABELS)
    first = pk[pk.day == pk.click_day]

    print("1. By click date, per day")
    t = (first.groupby(["period", "seg"], observed=True).agg(clicks=("v84", "size"))
         .join(pk.groupby(["period", "seg"], observed=True).agg(bookings=("bookings", "sum"), revenue=("revenue", "sum")))
         .unstack("seg"))
    print(t.div(NDAYS, axis=0).round(2).to_string(), "\n")

    print("2. Bookings with zero revenue (Adobe)")
    b = pk[pk.bookings > 0]
    print(f"   {b.loc[b.revenue <= 0, 'bookings'].sum():.0f} of {b.bookings.sum():.0f}\n")

    print("3. Bookings by click month")
    print(pk.groupby([pk.click_day.dt.to_period("M"), "seg"]).bookings.sum().unstack("seg").to_string(), "\n")

    print("4. NB UK+IE by campaign family, 13 Jun-1 Sep (81 days) vs 2 Sep-5 Oct (34 days)")
    uk = pk[pk.seg == "NB UK+IE"]
    split = pd.cut(uk.click_day, pd.to_datetime(["2026-06-13", "2026-09-02", "2026-10-06"]), right=False, labels=["pre", "post"])
    uk = uk.assign(split=split)
    for key in ["family", "dest"]:
        cl = uk[uk.day == uk.click_day].groupby([key, "split"], observed=True).size().unstack().div(pd.Series({"pre": 81, "post": 34}))
        bk = uk.groupby([key, "split"], observed=True).bookings.sum().unstack()
        print(pd.concat({"clicks/day": cl.round(1), "bookings": bk}, axis=1).to_string(), "\n")


if __name__ == "__main__":
    main(sys.argv[1])
