"""PK non-brand by destination group, on campaigns the 20 Aug budget cut did not touch.

Usage: python scripts/pk_cut_adjusted.py <v84.parquet> [cut_list.txt]

Without a cut list, campaigns whose clicks fell 60% or more between 10-19 Aug and 21-31 Aug are
treated as cut, plus the two GB country campaigns (their spend fell 88% on 20 Aug, clicks halved).
A cut list file holds one campaign name per line.
"""
import math
import sys

import numpy as np
import pandas as pd

pd.set_option("display.width", 250)

UK = {"GB", "LHR", "MAN", "EDI", "LGW", "BHX", "DUB", "IE"}
LONG_HAUL = set(
    "US CA ATL BOS DFW IAD IAH JFK LAX MIA ORD SEA SFO YUL YYZ "  # North America
    "AMS ARN BCN BE BER BRU CDG CPH CY DE DK DUS ES FCO FI FR FRA IT MAD MUC MXP NL NO OSL SE "  # Europe ex UK/IE
    "ADL AKL AU BNE MEL NZ PER SYD".split())  # Oceania
GB_COUNTRY = {"Google|PK|Dest|Country|XXX|GB|EN|MOD", "Google|PK|O&D|Country|PK|GB|EN|MOD"}
EDGES = pd.to_datetime(["2026-06-13", "2026-08-20", "2026-09-02", "2026-10-06"])
LABELS = ["13 Jun-19 Aug", "20 Aug-1 Sep", "2 Sep-5 Oct"]
NDAYS = pd.Series([68, 13, 34], index=LABELS)


def main(path: str, cut_file: str | None) -> None:
    d = pd.read_parquet(path)
    if "v84" not in d.columns:  # committed data/adobe file: hashed tracking ID instead of the raw one
        d["v84"] = d["click_key"]
    d = d[d.parsed]
    d = d.join(d.groupby("v84").day.min().rename("click_day"), on="v84")
    pk = d[(d.cc == "PK") & (d.engine == "Google") & (d.group == "Non-brand")].copy()
    parts = pk.campaign.str.split("|")
    new = parts.str.len() == 8
    pk["dest"] = np.where(new, parts.str[5], "")
    pk["region"] = np.select([~new, pk.dest.isin(UK), pk.dest.isin(LONG_HAUL)],
                             ["generic (legacy)", "UK+IE", "other long-haul"], "regional")
    first = pk[pk.day == pk.click_day]

    if cut_file:
        cut = set(open(cut_file).read().split("\n")) - {""}
    else:
        a = first[first.day.between("2026-08-10", "2026-08-19")].groupby("campaign").size() / 10
        b = first[first.day.between("2026-08-21", "2026-08-31")].groupby("campaign").size().reindex(a.index, fill_value=0) / 11
        cut = set(a[(b / a - 1 <= -0.6) & (a >= 1)].index) | GB_COUNTRY
    print(f"{len(cut)} campaigns treated as cut")

    pk = pk[~pk.campaign.isin(cut)]
    pk["period"] = pd.cut(pk.click_day, EDGES, right=False, labels=LABELS)
    first = pk[pk.day == pk.click_day]
    tot = (first.groupby(["region", "period"], observed=True)
           .agg(clicks=("v84", "size"), search_visits=("flight_search_visits", "sum"))
           .join(pk.groupby(["region", "period"], observed=True).agg(bookings=("bookings", "sum"), revenue=("revenue", "sum"))))
    out = tot.div(NDAYS, level="period", axis=0).round(2)
    out["booking rate %"] = (tot.bookings / tot.search_visits * 100).round(2)
    out["bookings total"] = tot.bookings
    out["revenue per booking"] = (tot.revenue / tot.bookings).round(0)
    print(out.to_string())
    rev = out.revenue.unstack("period")
    for base in LABELS[:2]:
        loss = (rev[base] - rev[LABELS[2]]).round(0)
        print(f"Revenue lost per day vs {base}: {loss.to_dict()}, net {loss.sum():.0f}")

    uk = tot.loc["UK+IE"]
    rate = uk.bookings.iloc[:2].sum() / uk.search_visits.iloc[:2].sum()
    lam = rate * uk.search_visits.iloc[2]
    obs = int(uk.bookings.iloc[2])
    p = sum(math.exp(-lam) * lam ** k / math.factorial(k) for k in range(obs + 1))
    print(f"UK+IE not cut, after switch: expected {lam:.1f} bookings at the earlier rate, observed {obs}, P(<= observed) = {p:.4f}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
