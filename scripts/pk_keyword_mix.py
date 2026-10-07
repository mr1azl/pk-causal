"""PK non-brand keyword mix and campaign type, by click date.

Usage: python scripts/pk_keyword_mix.py <v84.parquet>   (built by scripts/load_v84.py)
"""
import re
import sys

import numpy as np
import pandas as pd

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)
pd.set_option("display.max_rows", 200)

EDGES = pd.to_datetime(["2026-06-13", "2026-08-20", "2026-09-02", "2026-09-20", "2026-10-06"])
LABELS = ["13 Jun-19 Aug", "20 Aug-1 Sep cut", "2-19 Sep switch", "20 Sep-5 Oct"]
NDAYS = pd.Series(np.diff(EDGES).astype("timedelta64[D]").astype(int), index=LABELS)
UK = {"GB", "LHR", "MAN", "EDI", "LGW", "BHX", "DUB", "IE"}
CABINS = {"Economy", "First", "Business"}
ORIGIN_CITY = r"\b(?:lahore|karachi|islamabad|multan|peshawar|sialkot|faisalabad)\b"
ORIGIN_CODE = r"\b(?:lhe|khi|isb|mux|pew|skt|lyp)\b"
PRICE = r"\b(?:cheap|cheapest|deal|deals|airfare|airfares|fare|fares|price|prices|offer|offers)\b"


def load(path: str) -> pd.DataFrame:
    d = pd.read_parquet(path)
    if "v84" not in d.columns:  # committed data/adobe file: hashed tracking ID instead of the raw one
        d["v84"] = d["click_key"]
    d = d[d.parsed]
    d = d.join(d.groupby("v84").day.min().rename("click_day"), on="v84")
    pk = d[(d.cc == "PK") & (d.engine == "Google") & (d.group == "Non-brand")].copy()
    # A few IDs carry keyword and ad group in swapped order.
    swap = pk.keyword.isin(CABINS) & ~pk.ad_group.isin(CABINS)
    pk.loc[swap, ["ad_group", "keyword"]] = pk.loc[swap, ["keyword", "ad_group"]].values
    p = pk.campaign.str.split("|")
    new = p.str.len() == 8
    pk["dest"] = np.where(new, p.str[5], "")
    pk["campaign_type"] = np.select(
        [new & (p.str[2] == "O&D") & (p.str[3] == "Routes"),
         new & (p.str[2] == "O&D") & (p.str[3] == "Country"),
         new & (p.str[2] == "Dest") & (p.str[3] == "City"),
         new & (p.str[2] == "Dest") & (p.str[3] == "Country")],
        ["Route: airport to airport", "Route: Pakistan to country", "Destination: city", "Destination: country"],
        "Generic (legacy)")
    pk["match"] = np.where(new, p.str[7], "Exact")
    kw = pk.keyword.str.lower()
    code_hit = np.array([bool(c) and re.search(rf"\b{c.lower()}\b", k) is not None for c, k in zip(pk.dest, kw)])
    pk["kw_origin"] = np.select(
        [kw.str.contains(r"\bpakistan\b"), kw.str.contains(ORIGIN_CITY), kw.str.contains(ORIGIN_CODE)],
        ["origin: Pakistan", "origin: city name", "origin: airport code"], "no origin")
    pk["kw_dest"] = np.select(
        [pk.campaign_type == "Generic (legacy)", code_hit, pk.dest.str.len() == 2],
        ["no destination", "dest: airport code", "dest: country name"], "dest: city name")
    pk["kw_cabin"] = np.where(kw.str.contains(r"first class|business class") | pk.ad_group.isin(["First", "Business"]),
                              "premium cabin", "economy / none")
    pk["kw_price"] = np.where(kw.str.contains(PRICE), "price word", "no price word")
    pk["region"] = np.where(pk.dest.isin(UK), "UK+IE", "other")
    pk["period"] = pd.cut(pk.click_day, EDGES, right=False, labels=LABELS)
    return pk[pk.period.notna()]


def table(pk: pd.DataFrame, key) -> pd.DataFrame:
    first = pk[pk.day == pk.click_day]
    clicks = first.groupby([*key, "period"], observed=True).size().unstack("period")
    bk = pk.groupby([*key, "period"], observed=True).bookings.sum().unstack("period")
    rev = pk.groupby([*key, "period"], observed=True).revenue.sum().unstack("period")
    share = (clicks / clicks.sum() * 100).round(1)
    per_day = clicks.div(NDAYS).round(1)
    conv = (bk / clicks * 1000).round(1)
    return pd.concat({"clicks/day": per_day, "click share %": share, "bookings": bk.fillna(0).astype(int),
                      "bk per 1k clicks": conv, "revenue/day": rev.div(NDAYS).round(0)}, axis=1)


def mix_test(pk: pd.DataFrame, key: str, k: float = 200) -> pd.DataFrame:
    """Price each period's click mix at the 13 Jun-1 Sep conversion of each key (shrunk to the mean)."""
    first = pk[pk.day == pk.click_day]
    base = pk.period.isin(LABELS[:2])
    cl = first[first.period.isin(LABELS[:2])].groupby(key).size()
    bk = pk[base].groupby(key).bookings.sum().reindex(cl.index, fill_value=0)
    rv = pk[base].groupby(key).revenue.sum().reindex(cl.index, fill_value=0)
    cr, rpc = bk.sum() / cl.sum(), rv.sum() / cl.sum()
    cr_k, rpc_k = (bk + k * cr) / (cl + k), (rv + k * rpc) / (cl + k)
    rows = []
    for per, g in first.groupby("period", observed=True):
        m = g.groupby(key).size()
        m = m / m.sum()
        allp = pk[pk.period == per]
        rows.append({"period": per,
                     "mix-implied bk per 1k": (m * cr_k.reindex(m.index).fillna(cr)).sum() * 1000,
                     "actual bk per 1k": allp.bookings.sum() / len(g) * 1000,
                     "mix-implied rev per click": (m * rpc_k.reindex(m.index).fillna(rpc)).sum(),
                     "actual rev per click": allp.revenue.sum() / len(g)})
    return pd.DataFrame(rows).set_index("period").round(2)


def main(path: str) -> None:
    pk = load(path)
    for key in (["campaign_type"], ["campaign_type", "region"], ["match"], ["kw_origin"], ["kw_dest"],
                ["kw_cabin"], ["kw_price"]):
        print(f"== {' x '.join(key)}")
        print(table(pk, key).to_string(), "\n")
    print("== Mix test by keyword (each period's keyword mix at pre-switch conversion per keyword)")
    print(mix_test(pk, "keyword").to_string(), "\n")
    print("== Mix test by campaign")
    print(mix_test(pk, "campaign").to_string(), "\n")
    first = pk[pk.day == pk.click_day]
    top = first.groupby(["keyword", "period"], observed=True).size().unstack("period").fillna(0)
    share = (top / top.sum() * 100).round(1)
    print("== Top keywords by click share, before vs after")
    order = share[LABELS[0]].sort_values(ascending=False).index[:20]
    print(share.loc[order].to_string(), "\n")
    print("== Keywords that gained most share after the switch (20 Sep-5 Oct vs 13 Jun-19 Aug)")
    gain = (share[LABELS[3]] - share[LABELS[0]]).sort_values(ascending=False)
    print(share.loc[gain.index[:15]].to_string(), "\n")
    print("== Distinct keywords with a click per day")
    print(first.groupby("period", observed=True).apply(lambda g: g.groupby("day").keyword.nunique().mean()).round(1))


if __name__ == "__main__":
    main(sys.argv[1])
