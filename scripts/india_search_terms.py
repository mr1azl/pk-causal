"""India search terms (non-brand and brand), May to Oct 2026: query risk profile before a VBB launch.

Usage: python scripts/india_search_terms.py "<non-brand report.csv>" "<brand report.csv>" [out_dir]

India has not switched, so every month is pre-launch. The point is to measure the query traits that hurt PK
after its switch: reverse-direction queries (destination to India), third-country routes, generic queries,
agent and OTA names, competitor airlines, broad-match share, and any overlap with brand.
"""
import re
import sys

import numpy as np
import pandas as pd

pd.set_option("display.width", 250)
pd.set_option("display.max_rows", 300)
pd.set_option("display.max_colwidth", 55)

MONTHS = ["May 2026", "June 2026", "July 2026", "August 2026", "September 2026", "October 2026"]
INDIA = (r"india|indian|delhi|new delhi|mumbai|bombay|bangalore|bengaluru|chennai|madras|hyderabad|kolkata|calcutta|"
         r"kochi|cochin|kerala|ahmedabad|goa|amritsar|trivandrum|thiruvananthapuram|kozhikode|calicut|lucknow|jaipur|"
         r"pune|nagpur|chandigarh|mangalore|mangaluru|kannur|varanasi|patna|srinagar|bhubaneswar|coimbatore|"
         r"vizag|visakhapatnam|madurai|punjab|gujarat|tamil nadu|"
         r"del|bom|blr|maa|hyd|ccu|cok|amd|goi|gox|atq|trv|ccj|lko|jai|pnq|nag|ixc|ixe|cnn|vns|pat|sxr|bbi|cjb")
FILLER = {"flights", "flight", "cheap", "cheapest", "tickets", "ticket", "air", "airfare", "airfares", "book", "booking",
          "best", "direct", "one", "way", "return", "price", "prices", "fare", "fares", "deals", "deal", "low", "cost",
          "airlines", "airline", "online", "today", "tomorrow", "international", "the", "for", "a", "of", "and", "in",
          "time", "duration", "distance", "hours", "how", "many", "much", "is", "first", "business", "class", "economy",
          "round", "trip", "non", "stop", "nonstop", "status", "schedule", "under", "rs", "inr"}
GENERIC = (r"^(?:cheap |cheapest |book(?:ing)? |online |air |international |best |low cost |discount )*"
           r"(?:flights?|tickets?|air tickets?|airlines?|flight booking|ticket booking|book a flight|book flights?|"
           r"airline tickets?|flight tickets?|cheap flights?|air ticket booking|online ticket booking|flights booking|"
           r"international flights?|international tickets?|plane tickets?)(?: booking| online| price| prices| deals)*$")
AGENT_OTA = (r"makemytrip|make my trip|\bmmt\b|goibibo|yatra|cleartrip|easemytrip|ease my trip|ixigo|akbar|ezeego|"
             r"via\.com|paytm|happyeasygo|travelguru|skyscanner|expedia|kayak|booking\.com|trip\.com|kiwi|momondo|"
             r"cheapoair|travel agen|tour|travels\b|agency")
COMPETITORS = (r"air india|indigo|vistara|spicejet|akasa|emirates|etihad|lufthansa|british airways|\bba\b|saudia|"
               r"gulf air|oman air|flydubai|fly dubai|air arabia|singapore airlines|turkish|kuwait airways|"
               r"virgin|klm|air france|swiss|united airlines|american airlines|delta|air canada|qantas")
GROUPS = {
    "UK+IE": "GB LHR LGW EDI MAN BHX IE DUB",
    "North America": "US CA YYZ JFK DFW ORD SFO IAH MIA IAD ATL SEA LAX BOS YUL DTW TPA DEN",
    "Europe": ("DE BER CDG IT FI FCO ZRH FR FRA CH ES NO MT PL BCN AMS MXP PT RO MAD ARN NL GR OSL WAW LIS SE SVO BUD "
               "ATH HU MUC CY OTP CPH PRG HR RS GVA DK AT BE BRU CZ ZAG BEG DUS NCE LCA"),
    "Turkey/Caucasus": "TR IST GE AZ TBS GYD AM EVN",
    "Oceania": "AUS NZ AKL",
    "GCC/Middle East": "DXB AE SA KW RUH AUH DOH QA KWI JED SHJ RSI DMM BAH EG CAI",
    "Africa": "KE TZ ZA JNB CPT ZM LOS NBO DAR NG LUN MPM MZ ABJ JRO CI",
    "South America": "BR GRU CO BOG CCS VE",
}
CODE_GROUP = {c: g for g, codes in GROUPS.items() for c in codes.split()}


def has_india(text: str) -> bool:
    return re.search(rf"\b(?:{INDIA})\b", text) is not None


def meaningful(text: str) -> bool:
    words = [w for w in re.findall(r"[a-z]+", text) if w not in FILLER and w not in {"to", "from"}]
    return bool(words)


def direction(q: str) -> str:
    q = f" {q.lower().strip()} "
    if re.match(GENERIC, q.strip()):
        return "generic"
    india = has_india(q)
    origin = dest = None
    m = re.search(r"\bfrom\b(.*?)(?:\bto\b(.*))?$", q)
    if m:
        origin, dest = m.group(1), (m.group(2) or q[: m.start()])
    elif " to " in q:
        origin, dest = q.split(" to ", 1)
    if origin is not None:
        o_in, d_in = has_india(origin), has_india(dest)
        if o_in and not d_in:
            return "outbound (India to destination)"
        if d_in and not o_in and meaningful(origin):
            return "reverse (destination to India)"
        if not o_in and not d_in and meaningful(origin) and meaningful(dest):
            return "third-country route"
        if o_in and d_in:
            return "within India"
    if india:
        return "India named, no direction"
    return "destination only" if meaningful(q) else "generic"


def load(path: str) -> pd.DataFrame:
    d = pd.read_csv(path, skiprows=2, thousands=",", dtype=str)
    d = d[~d["Search term"].astype(str).str.startswith("Total:") & d.Month.isin(MONTHS)].copy()
    for c in ("Cost", "Clicks"):
        d[c] = pd.to_numeric(d[c].str.replace(",", ""), errors="coerce").fillna(0)
    d["month"] = pd.Categorical(d.Month, MONTHS, ordered=True)
    p = d.Campaign.str.split("|")
    d["dest"] = np.where(p.str.len() == 8, p.str[5], "")
    d["ctype"] = np.where(p.str.len() >= 4, p.str[2] + "/" + p.str[3], "other")
    d["group"] = d.dest.map(CODE_GROUP)
    d.loc[d.group.isna(), "group"] = np.where(d.loc[d.group.isna(), "ctype"].str.startswith("Perf_Max"), "PMAX", "other")
    return d


def shares(d: pd.DataFrame, rows: str, cols: str) -> pd.DataFrame:
    t = d.groupby([rows, cols], observed=True).Clicks.sum().unstack(fill_value=0)
    return (t.div(t.sum(axis=1), axis=0) * 100).round(1).assign(clicks=t.sum(axis=1).astype(int))


def nonbrand(path: str, out_dir: str | None) -> None:
    d = load(path)
    d = d[d.Clicks > 0].copy()
    q = d["Search term"].astype(str).str.lower()
    d["direction"] = [direction(x) for x in q]
    d["agent_ota"] = q.str.contains(AGENT_OTA)
    d["competitor"] = q.str.contains(rf"\b(?:{COMPETITORS})\b")
    d["brand_word"] = q.str.contains(r"\bqatar\b|\bqr\b|qatarairways")
    d["broad"] = d["Match type"].eq("Broad match")
    search = d[d.group != "PMAX"]
    print("== Search campaigns, all months: click share by direction, per destination group (%)")
    print(shares(search, "group", "direction").sort_values("clicks", ascending=False).to_string(), "\n")
    print("== Search campaigns: direction share by month (%)")
    print(shares(search, "month", "direction").to_string(), "\n")
    flags = search.groupby("group").apply(lambda x: pd.Series({
        "clicks": x.Clicks.sum(), "cost": round(x.Cost.sum()),
        "broad %": round(x.loc[x.broad, "Clicks"].sum() / x.Clicks.sum() * 100, 1),
        "agent/OTA %": round(x.loc[x.agent_ota, "Clicks"].sum() / x.Clicks.sum() * 100, 1),
        "competitor %": round(x.loc[x.competitor, "Clicks"].sum() / x.Clicks.sum() * 100, 1),
        "brand word %": round(x.loc[x.brand_word, "Clicks"].sum() / x.Clicks.sum() * 100, 2)}), include_groups=False)
    print("== Search campaigns, all months: match type and query flags by group")
    print(flags.sort_values("clicks", ascending=False).to_string(), "\n")
    off = search.assign(off=search.direction.isin(["reverse (destination to India)", "third-country route", "generic"]))
    camp = off.groupby("Campaign").apply(lambda x: pd.Series({
        "clicks": x.Clicks.sum(), "cost": round(x.Cost.sum()),
        "off-target %": round(x.loc[x.off, "Clicks"].sum() / x.Clicks.sum() * 100, 1),
        "reverse %": round(x.loc[x.direction == "reverse (destination to India)", "Clicks"].sum() / x.Clicks.sum() * 100, 1),
        "generic %": round(x.loc[x.direction == "generic", "Clicks"].sum() / x.Clicks.sum() * 100, 1),
        "broad %": round(x.loc[x.broad, "Clicks"].sum() / x.Clicks.sum() * 100, 1)}), include_groups=False)
    camp = camp[camp.clicks >= 500]
    camp["off-target cost"] = (camp.cost * camp["off-target %"] / 100).round()
    print("== Campaigns with the most off-target spend (reverse + third-country + generic), all months, >=500 clicks")
    print(camp.sort_values("off-target cost", ascending=False).head(25).to_string(), "\n")
    print("== Top reverse-direction queries by clicks, all months")
    print(search[search.direction == "reverse (destination to India)"].groupby(["Search term", "Campaign"]).Clicks.sum()
          .sort_values(ascending=False).head(20).to_string(), "\n")
    print("== Top generic queries by clicks, all months")
    print(search[search.direction == "generic"].groupby(["Search term", "Campaign"]).Clicks.sum()
          .sort_values(ascending=False).head(15).to_string(), "\n")
    off_all = d.assign(off=d.direction.isin(["reverse (destination to India)", "third-country route", "generic"]))
    tot = off_all.groupby("group").apply(lambda x: pd.Series({
        "cost": round(x.Cost.sum()), "off-target cost": round(x.loc[x.off, "Cost"].sum()),
        "reverse cost": round(x.loc[x.direction == "reverse (destination to India)", "Cost"].sum())}), include_groups=False)
    tot.loc["TOTAL"] = tot.sum()
    tot["off-target % of cost"] = (tot["off-target cost"] / tot.cost * 100).round(1)
    print("== Off-target cost by group, May to 7 Oct (reverse + third-country + generic)")
    print(tot.sort_values("cost", ascending=False).to_string(), "\n")
    pm = d[d.group == "PMAX"]
    print("== Performance Max: direction share (%)"); print(shares(pm, "month", "direction").to_string(), "\n")
    if out_dir:
        d.to_parquet(f"{out_dir}/india_search_terms_nonbrand.parquet", index=False, compression="zstd")


def brand(path: str, out_dir: str | None) -> None:
    b = load(path)
    q = b["Search term"].astype(str).str.lower()
    b["has_brand"] = q.str.contains(r"qatar|\bqr\b|katar|qatr|privilege club|avios")
    g = b.groupby(["Campaign", "month"], observed=True).agg(clicks=("Clicks", "sum"), cost=("Cost", "sum"))
    g["cpc"] = (g.cost / g.clicks).round(3)
    print("== Brand campaigns: clicks, cost and CPC by month"); print(g.unstack("Campaign").round(2).to_string(), "\n")
    t = b.groupby(["month", "has_brand"], observed=True).Clicks.sum().unstack(fill_value=0)
    print("== Brand account: clicks on queries without a brand word"); print(t.to_string(), "\n")
    print(b[~b.has_brand].groupby("Search term").Clicks.sum().sort_values(ascending=False).head(15).to_string(), "\n")
    if out_dir:
        b.to_parquet(f"{out_dir}/india_search_terms_brand.parquet", index=False, compression="zstd")


if __name__ == "__main__":
    out = sys.argv[3] if len(sys.argv) > 3 else None
    nonbrand(sys.argv[1], out)
    brand(sys.argv[2], out)
