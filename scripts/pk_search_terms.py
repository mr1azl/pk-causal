"""PK search terms report (SA360/Google Ads UI export): direction and intent of the queries bought.

Usage: python scripts/pk_search_terms.py "<Search terms report.csv>" [out.parquet]

Monthly granularity, cost and clicks only (the export has no conversions). Classifies each query by
travel direction relative to the campaign's destination, and flags competitor airlines and intent words.
"""
import re
import sys

import numpy as np
import pandas as pd

pd.set_option("display.width", 250)
pd.set_option("display.max_rows", 300)
pd.set_option("display.max_colwidth", 60)

PK = r"pakistan|lahore|karachi|islamabad|multan|peshawar|sialkot|faisalabad|quetta|rawalpindi|lhe|khi|isb|mux|pew|skt|lyp|uet"
UK = (r"uk|u\.k|united kingdom|england|britain|london|manchester|birmingham|edinburgh|glasgow|heathrow|gatwick|stansted|luton|"
      r"leeds|bradford|newcastle|scotland|lhr|lgw|man|bhx|edi|gla|stn|ltn|lba|ncl|dublin|ireland|dub|belfast|bristol|brs")
UK_CODES = {"GB", "IE", "LHR", "LGW", "MAN", "BHX", "EDI", "DUB", "GLA", "LON"}
AIRLINES = (r"pia|pakistan international|emirates|etihad|turkish|saudia|saudi airlines|british airways|\bba\b|virgin|airblue|"
            r"serene|fly ?dubai|air arabia|gulf air|oman air|flynas|air sial|kuwait airways|qatar|qr\b")
MONTHS = ["May 2026", "June 2026", "July 2026", "August 2026", "September 2026", "October 2026"]


def has(pattern: str, text: str) -> bool:
    return re.search(rf"\b(?:{pattern})\b", text) is not None


def direction(q: str) -> str:
    """Return outbound (PK to UK), reverse (UK to PK), uk_to_other, uk_only, pk_only or neither."""
    q = f" {q.lower()} "
    pk, uk = has(PK, q), has(UK, q)
    if not pk and not uk:
        return "neither"
    origin = dest = None
    m = re.search(r"\bfrom\b(.*?)(?:\bto\b(.*))?$", q)
    if m:
        origin, dest = m.group(1), (m.group(2) or q[: m.start()])
    elif " to " in q:
        origin, dest = q.split(" to ", 1)
    elif re.search(r"\b(?:" + PK + r"|" + UK + r")\b\s*[-/ ]\s*\b(?:" + PK + r"|" + UK + r")\b", q):
        # "lahore london flights", "lhe lhr": first place is the origin
        first = re.search(r"\b(?:" + PK + r"|" + UK + r")\b", q)
        origin, dest = q[first.start(): first.end()], q[first.end():]
    if origin is not None:
        o_pk, o_uk, d_pk, d_uk = has(PK, origin), has(UK, origin), has(PK, dest), has(UK, dest)
        if o_uk and d_pk and not o_pk:
            return "reverse (UK to PK)"
        if o_pk and d_uk and not o_uk:
            return "outbound (PK to UK)"
        if o_uk and not d_pk and not d_uk and dest.strip(" flightsticketsairfare") != "":
            return "UK to elsewhere"
    if uk and not pk:
        return "UK only"
    if pk and not uk:
        return "PK only"
    return "outbound (PK to UK)" if q.find(re.search(PK, q).group()) < q.find(re.search(UK, q).group()) else "reverse (UK to PK)"


def load(path: str) -> pd.DataFrame:
    d = pd.read_csv(path, skiprows=2, thousands=",")
    d = d[~d["Search term"].astype(str).str.startswith("Total:") & d.Month.isin(MONTHS)].copy()
    d["Cost"], d["Clicks"] = pd.to_numeric(d.Cost, errors="coerce"), pd.to_numeric(d.Clicks, errors="coerce")
    p = d.Campaign.str.split("|")
    d["dest"] = np.where(p.str.len() == 8, p.str[5], "")
    d["ctype"] = np.where(p.str.len() == 8, p.str[2] + "/" + p.str[3], "generic")
    d["is_uk"] = d.dest.isin(UK_CODES)
    d["gb_country_cut"] = d.Campaign.str.startswith(("Google|PK|Dest|Country|XXX|GB|", "Google|PK|O&D|Country|PK|GB|"))
    q = d["Search term"].astype(str).str.lower()
    d["direction"] = [direction(x) for x in q]
    d["competitor_airline"] = q.str.contains(rf"\b(?:{AIRLINES})", regex=True) & ~q.str.contains(r"\bqatar\b")
    d["qatar_named"] = q.str.contains(r"\bqatar\b")
    d["month"] = pd.Categorical(d.Month, MONTHS, ordered=True)
    return d


def share(d: pd.DataFrame, key: str) -> pd.DataFrame:
    t = d.groupby(["month", key], observed=True).Clicks.sum().unstack(fill_value=0)
    return (t.div(t.sum(axis=1), axis=0) * 100).round(1).assign(total_clicks=t.sum(axis=1))


def main(path: str, out: str | None) -> None:
    d = load(path)
    uk_rest = d[d.is_uk & ~d.gb_country_cut]
    uk_all = d[d.is_uk]
    other = d[~d.is_uk & (d.ctype != "generic")]
    print("== UK+IE campaigns not cut on 20 Aug: click share by query direction (%)"); print(share(uk_rest, "direction").to_string(), "\n")
    print("== UK+IE all campaigns"); print(share(uk_all, "direction").to_string(), "\n")
    print("== UK+IE not cut: competitor airline named in query (% of clicks)"); print(share(uk_rest, "competitor_airline").to_string(), "\n")
    print("== Non-UK destination campaigns: competitor airline named (% of clicks)"); print(share(other, "competitor_airline").to_string(), "\n")
    if out:
        d.to_parquet(out, index=False)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
