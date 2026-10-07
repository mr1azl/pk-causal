"""PK brand search terms: did UK (or other) demand move into brand searches after the 2 Sep switch?

Usage: python scripts/pk_brand_search_terms.py "<Search terms report-brand.csv>"

Monthly, cost and clicks only. Tags each brand query by the destination or route it names, using the same
place lists as scripts/pk_search_terms.py.
"""
import re
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from pk_search_terms import MONTHS, PK, UK  # noqa: E402

pd.set_option("display.width", 250)
pd.set_option("display.max_rows", 200)
pd.set_option("display.max_colwidth", 60)

OTHER_LH = (r"usa|united states|america|new york|chicago|houston|toronto|canada|montreal|vancouver|australia|sydney|"
            r"melbourne|perth|europe|germany|frankfurt|paris|france|italy|milan|rome|barcelona|spain|madrid|"
            r"jfk|ord|iah|yyz|syd|mel|per|fra|cdg|mxp|bcn")
REGIONAL = (r"doha|qatar visa|dubai|saudi|jeddah|riyadh|madinah|medina|dammam|kuwait|bahrain|muscat|oman|"
            r"istanbul|turkey|baku|azerbaijan|malaysia|kuala lumpur|bangkok|thailand|indonesia|bali|maldives|"
            r"china|guangzhou|japan|tokyo|uae|abu dhabi|sharjah|jed|ruh|dxb|ist|kul")
SERVICE = (r"baggage|luggage|check ?in|manage|booking reference|pnr|status|cancel|refund|change|contact|"
           r"customer|helpline|number|office|seat|upgrade|privilege|avios|miles|login|app")


def tag(q: str) -> str:
    q = q.lower()
    if re.search(rf"\b(?:{UK})\b", q):
        return "names UK/IE"
    if re.search(rf"\b(?:{OTHER_LH})\b", q):
        return "names other long-haul"
    if re.search(rf"\b(?:{REGIONAL})\b", q):
        return "names regional"
    if re.search(rf"\b(?:{SERVICE})", q):
        return "service / manage booking"
    return "brand, no destination"


def main(path: str) -> None:
    d = pd.read_csv(path, skiprows=2, thousands=",")
    d = d[~d["Search term"].astype(str).str.startswith("Total:") & d.Month.isin(MONTHS)].copy()
    d["Clicks"], d["Cost"] = pd.to_numeric(d.Clicks, errors="coerce"), pd.to_numeric(d.Cost, errors="coerce")
    d["month"] = pd.Categorical(d.Month, MONTHS, ordered=True)
    d["tag"] = [tag(str(x)) for x in d["Search term"]]
    q = d["Search term"].astype(str).str.lower()
    d["mentions_pk_origin"] = q.str.contains(rf"\b(?:{PK})\b")
    t = d.groupby(["month", "tag"], observed=True).Clicks.sum().unstack(fill_value=0)
    print("== Brand clicks by what the query names"); print(t.assign(total=t.sum(axis=1)).to_string(), "\n")
    print("== Share of brand clicks (%)"); print((t.div(t.sum(axis=1), axis=0) * 100).round(1).to_string(), "\n")
    uk = d[d.tag == "names UK/IE"]
    print("== Top brand queries naming UK/IE, Aug vs Sep vs Oct")
    for m in ("August 2026", "September 2026", "October 2026"):
        print(m); print(uk[uk.month == m].groupby("Search term").Clicks.sum().sort_values(ascending=False).head(12).to_string())
    print("\n== Campaigns, clicks by month"); print(d.groupby(["Campaign", "month"], observed=True).Clicks.sum().unstack(fill_value=0).to_string())


if __name__ == "__main__":
    main(sys.argv[1])
