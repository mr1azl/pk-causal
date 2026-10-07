"""Load the raw Adobe v84 daily files into one parsed table.

Usage: python scripts/load_v84.py <raw_dir> <out.parquet>

<raw_dir> holds v84_YYYY-MM-DD.csv files (any depth). Each row is one v84 tracking ID for one day
with flight_search_visits, bookings and revenue. The tracking ID is
account|campaign...|ad_group|keyword|gclid|gclsrc, where the campaign itself contains pipes.
"""
import glob
import os
import re
import sys

import pandas as pd

ACCOUNT_RE = re.compile(r"^([^-]+)-([^-]+)-([A-Za-z]{2})-([A-Za-z]{2})((?:-Brand|-\d+)*)$")


def parse(v84: str) -> dict:
    parts = v84.split("|")
    if len(parts) < 6:
        return {"parsed": False}
    account, campaign = parts[0], "|".join(parts[1:-4])
    ad_group, keyword, gclid, gclsrc = parts[-4:]
    m = ACCOUNT_RE.match(account)
    camp = campaign.lower()
    if "perf_max" in camp or "pmax" in camp:
        group = "PMAX"
    elif "|brand|" in f"|{camp}|" or camp.startswith(("us-brand", "brand")) or "-brand-" in camp:
        group = "Brand"
    else:
        group = "Non-brand"
    return {
        "parsed": True,
        "account": account,
        "engine": m.group(1) if m else account.split("-")[0],
        "cc": m.group(3).upper() if m else None,
        "campaign": campaign,
        "ad_group": ad_group,
        "keyword": keyword,
        "has_gclid": gclid != "",
        "gclsrc": gclsrc,
        "group": group,
    }


def main(raw_dir: str, out: str) -> None:
    frames = []
    for f in sorted(glob.glob(os.path.join(raw_dir, "**", "v84_*.csv"), recursive=True)):
        day = os.path.basename(f)[4:14]
        d = pd.read_csv(f, dtype={"v84": str}, keep_default_na=False)
        d.insert(0, "day", day)
        frames.append(d)
    df = pd.concat(frames, ignore_index=True)
    parsed = pd.DataFrame([parse(v) for v in df["v84"]])
    df = pd.concat([df, parsed], axis=1)
    df["day"] = pd.to_datetime(df["day"])
    df.to_parquet(out, index=False)
    print(f"{len(df):,} rows, {df.day.nunique()} days, {df.day.min().date()} to {df.day.max().date()}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
