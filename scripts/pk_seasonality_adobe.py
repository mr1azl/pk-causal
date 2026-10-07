"""PK non-brand on Adobe, 2025 vs 2026: is the September UK drop seasonal?

Usage: python scripts/pk_seasonality_adobe.py <v84 parquet covering both years>

Handles both campaign naming conventions:
  new     Google|PK|Dest|Country|XXX|GB|EN|MOD, Google|PK|O&D|Routes|LHE|LHR|EN|MOD
  legacy  _PK-Country-XXX-GB-EN_phrase, _PK-O&D-LHE-LHR-EN_exact, _PK-D-XXX-LHR-EN_phrase
Brand is decided by the account suffix (-Brand), which also catches legacy brand names.
Bookings and revenue are credited to the click date (first day the tracking ID appears).
"""
import re
import sys

import numpy as np
import pandas as pd

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)
pd.set_option("display.max_rows", 200)

UK = {"GB", "IE", "LHR", "LGW", "MAN", "BHX", "EDI", "DUB", "LON", "GLA", "BHD", "NCL", "ABZ", "ORK", "STN", "LTN"}
LONG_HAUL = set(
    "US CA ATL BOS DFW IAD IAH JFK LAX MIA ORD SEA SFO YUL YYZ YVR EWR NYC CHI WAS "
    "AMS ARN BCN BE BER BRU CDG CPH CY DE DK DUS ES FCO FI FR FRA IT MAD MUC MXP NL NO OSL SE CH ZRH GVA "
    "VIE AT PRG CZ WAW PL ATH GR LIS PT HEL MIL ROM PAR STO "
    "ADL AKL AU BNE MEL NZ PER SYD".split())
LEGACY = re.compile(r"^_?PK-(Country|O&D|D)-([A-Z]{2,3})-([A-Z]{2,3})-[A-Z]{2}_")


def campaign_fields(name: str) -> tuple[str, str]:
    """Return (campaign type, destination code) for either naming convention."""
    p = name.split("|")
    if len(p) == 8:
        kind = {"Dest|Country": "Destination: country", "Dest|City": "Destination: city",
                "O&D|Country": "Route: Pakistan to country", "O&D|Routes": "Route: airport to airport"}
        return kind.get(f"{p[2]}|{p[3]}", "other"), p[5]
    m = LEGACY.match(name)
    if m:
        t, orig, dest = m.groups()
        if t == "Country":
            return "Destination: country", dest
        if t == "D":
            return "Destination: city", dest
        return ("Route: Pakistan to country" if orig == "PK" else "Route: airport to airport"), dest
    return "generic / other", ""


def load(path: str) -> pd.DataFrame:
    d = pd.read_parquet(path)
    if "v84" not in d.columns:
        d["v84"] = d["click_key"]
    d = d[d.parsed & (d.cc == "PK") & (d.engine == "Google")].copy()
    d["is_brand"] = d.account.str.lower().str.endswith("-brand") | (d.group == "Brand")
    d = d.join(d.groupby("v84").day.min().rename("click_day"), on="v84")
    fields = {c: campaign_fields(c) for c in d.campaign.unique()}
    d["ctype"] = d.campaign.map(lambda c: fields[c][0])
    d["dest"] = d.campaign.map(lambda c: fields[c][1])
    d["seg"] = np.select(
        [d.is_brand, d.group == "PMAX", d.dest.isin(UK), d.dest.isin(LONG_HAUL), d.dest == ""],
        ["Brand", "PMAX", "NB UK+IE", "NB long-haul", "NB generic/other"], "NB regional")
    d["naming"] = np.where(d.campaign.str.contains("|", regex=False), "new", "legacy")
    return d


def monthly(d: pd.DataFrame) -> pd.DataFrame:
    first = d[d.day == d.click_day]
    key = [d.click_day.dt.to_period("M").rename("month"), "seg"]
    fkey = [first.click_day.dt.to_period("M").rename("month"), "seg"]
    t = (first.groupby(fkey).agg(clicks=("v84", "size"), search_visits=("flight_search_visits", "sum"))
         .join(d.groupby(key).agg(bookings=("bookings", "sum"), revenue=("revenue", "sum"))))
    t["bk per 1k visits"] = (t.bookings / t.search_visits * 1000).round(2)
    return t.round(0)


def main(path: str) -> None:
    d = load(path)
    nb = d[d.seg.str.startswith("NB")]
    print("Naming convention share of PK non-brand clicks by year:")
    print(nb[nb.day == nb.click_day].groupby([nb.click_day.dt.year, "naming"]).size().unstack().fillna(0).astype(int), "\n")
    t = monthly(d)
    for seg in ["Brand", "NB UK+IE", "NB long-haul", "NB regional", "NB generic/other"]:
        print(f"== {seg}, by click month")
        print(t.xs(seg, level="seg").to_string(), "\n")
    print("== Aug to Sep change, bookings per 1,000 search visits and bookings")
    rows = []
    for seg in ["Brand", "NB UK+IE", "NB long-haul", "NB regional"]:
        x = t.xs(seg, level="seg")
        for y in (2025, 2026):
            a, s = x.loc[pd.Period(f"{y}-08")], x.loc[pd.Period(f"{y}-09")]
            rows.append({"segment": seg, "year": y, "Aug bookings": a.bookings, "Sep bookings": s.bookings,
                         "Aug rate": a["bk per 1k visits"], "Sep rate": s["bk per 1k visits"],
                         "rate change %": round((s["bk per 1k visits"] / a["bk per 1k visits"] - 1) * 100)})
    print(pd.DataFrame(rows).to_string(index=False), "\n")
    uk = d[d.seg == "NB UK+IE"]
    wk = uk.groupby(uk.click_day.dt.to_period("W-SUN")).bookings.sum()
    print("== NB UK+IE bookings by click week, Jul to Oct each year")
    for y in (2025, 2026):
        w = wk[(wk.index.start_time >= f"{y}-07-01") & (wk.index.start_time < f"{y}-10-20")]
        print(y, " ".join(f"{p.start_time:%d%b}:{v:.0f}" for p, v in w.items()))


if __name__ == "__main__":
    main(sys.argv[1])
