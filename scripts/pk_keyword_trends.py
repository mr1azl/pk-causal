"""How PK non-brand keywords changed over time, May 2025 to Oct 2026 (Adobe, click date).

Usage: python scripts/pk_keyword_trends.py data/adobe/v84_pk_2025-05-01_2026-10-05.parquet
"""
import re
import sys

import numpy as np
import pandas as pd

from pk_seasonality_adobe import load

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)
pd.set_option("display.max_rows", 300)

CABINS = {"Economy", "First", "Business"}
ORIGIN = r"\b(?:pakistan|lahore|karachi|islamabad|multan|peshawar|sialkot|faisalabad|quetta|lhe|khi|isb|mux|pew|skt|uet|lyp)\b"
PRICE = r"\b(?:cheap|cheapest|deal|deals|airfare|airfares|fare|fares|price|prices|offer|offers|ticket price)\b"
SEGS = ["NB UK+IE", "NB long-haul", "NB regional"]
PRE, POST = ("2026-06-13", "2026-09-02"), ("2026-09-02", "2026-10-06")


def prepare(path: str) -> pd.DataFrame:
    d = load(path)
    nb = d[d.seg.isin(SEGS)].copy()
    swap = nb.keyword.isin(CABINS) & ~nb.ad_group.isin(CABINS)
    nb.loc[swap, ["ad_group", "keyword"]] = nb.loc[swap, ["keyword", "ad_group"]].values
    nb["kw"] = nb.keyword.str.lower().str.strip()
    code = np.array([bool(c) and len(c) == 3 and re.search(rf"\b{c.lower()}\b", k) is not None
                     for c, k in zip(nb.dest, nb.kw)])
    nb["origin"] = np.where(nb.kw.str.contains(ORIGIN), "origin named", "no origin")
    nb["dest_form"] = np.select([code, nb.dest.str.len() == 2], ["airport code", "country name"], "city name")
    nb["cabin"] = np.where(nb.kw.str.contains(r"first class|business class") | nb.ad_group.isin(["First", "Business"]),
                           "premium", "economy/none")
    nb["price_word"] = np.where(nb.kw.str.contains(PRICE), "price word", "none")
    nb["month"] = nb.click_day.dt.to_period("M")
    return nb


def monthly_mix(nb: pd.DataFrame, seg: str, key: str) -> pd.DataFrame:
    x = nb[nb.seg == seg]
    f = x[x.day == x.click_day]
    c = f.groupby(["month", key]).size().unstack(fill_value=0)
    b = x.groupby(["month", key]).bookings.sum().unstack(fill_value=0).reindex_like(c).fillna(0)
    return pd.concat({"click share %": (c.div(c.sum(axis=1), axis=0) * 100).round(0),
                      "bk per 1k clicks": (b / c.replace(0, np.nan) * 1000).round(1)}, axis=1)


def breadth(nb: pd.DataFrame) -> pd.DataFrame:
    f = nb[nb.day == nb.click_day]
    rows = []
    for (m, seg), g in f.groupby(["month", "seg"]):
        vc = g.kw.value_counts()
        rows.append({"month": m, "seg": seg, "clicks": len(g), "keywords": len(vc),
                     "top10 share %": round(vc.head(10).sum() / len(g) * 100)})
    return pd.DataFrame(rows).pivot(index="month", columns="seg", values=["clicks", "keywords", "top10 share %"])


def turnover(nb: pd.DataFrame) -> pd.DataFrame:
    """Share of each month's clicks on keywords that had no click in the previous three months."""
    f = nb[nb.day == nb.click_day]
    months = sorted(f.month.unique())
    rows = []
    for i, m in enumerate(months[3:], 3):
        prev = f[f.month.isin(months[i - 3:i])]
        cur = f[f.month == m]
        for seg in SEGS:
            c = cur[cur.seg == seg]
            seen = set(prev[prev.seg == seg].kw)
            rows.append({"month": m, "seg": seg, "new keyword click share %": round((~c.kw.isin(seen)).mean() * 100) if len(c) else np.nan})
    return pd.DataFrame(rows).pivot(index="month", columns="seg", values="new keyword click share %")


def mix_test(nb: pd.DataFrame, seg: str, k: float = 100) -> pd.DataFrame:
    """Price each month's keyword mix at the keyword's 13 Jun-1 Sep 2026 conversion, shrunk to the segment mean."""
    x = nb[nb.seg == seg]
    f = x[x.day == x.click_day]
    base_c = f[f.click_day.between(*PRE, inclusive="left")].groupby("kw").size()
    base_b = x[x.click_day.between(*PRE, inclusive="left")].groupby("kw").bookings.sum().reindex(base_c.index, fill_value=0)
    mean = base_b.sum() / base_c.sum()
    rate = (base_b + k * mean) / (base_c + k)
    rows = []
    for m, g in f[f.click_day >= "2026-05-01"].groupby("month"):
        w = g.kw.value_counts(normalize=True)
        rows.append({"month": m, "mix-implied bk per 1k": round((w * rate.reindex(w.index).fillna(mean)).sum() * 1000, 2),
                     "actual bk per 1k": round(x[x.month == m].bookings.sum() / len(g) * 1000, 2)})
    return pd.DataFrame(rows).set_index("month")


def keyword_table(nb: pd.DataFrame, seg: str, n: int = 20) -> pd.DataFrame:
    x = nb[nb.seg == seg]
    f = x[x.day == x.click_day]
    out = {}
    for name, (a, b), days in (("pre", PRE, 81), ("post", POST, 34)):
        ff, xx = f[f.click_day.between(a, b, inclusive="left")], x[x.click_day.between(a, b, inclusive="left")]
        out[f"clicks/day {name}"] = (ff.groupby("kw").size() / days).round(1)
        out[f"bookings {name}"] = xx.groupby("kw").bookings.sum()
    t = pd.DataFrame(out).fillna(0)
    t["share pre %"] = (t["clicks/day pre"] / t["clicks/day pre"].sum() * 100).round(1)
    t["share post %"] = (t["clicks/day post"] / t["clicks/day post"].sum() * 100).round(1)
    return t.sort_values("clicks/day pre", ascending=False).head(n)


def main(path: str) -> None:
    nb = prepare(path)
    print("== Breadth and concentration, by click month"); print(breadth(nb).to_string(), "\n")
    print("== Share of clicks on keywords with no click in the previous 3 months"); print(turnover(nb).to_string(), "\n")
    for seg in SEGS:
        for key in ("origin", "dest_form", "ctype", "cabin", "price_word"):
            print(f"== {seg}: {key}"); print(monthly_mix(nb, seg, key).to_string(), "\n")
        print(f"== {seg}: keyword mix test (pre-switch conversion per keyword)"); print(mix_test(nb, seg).to_string(), "\n")
        print(f"== {seg}: top keywords, 13 Jun-1 Sep vs 2 Sep-5 Oct 2026"); print(keyword_table(nb, seg).to_string(), "\n")


if __name__ == "__main__":
    main(sys.argv[1])
