"""Fresh review of the PK VBB investigation: every number quoted in docs/analysis/10_FRESH_REVIEW.md.

Usage: python scripts/pk_fresh_review.py            (run from the repo root; reads data/ only, writes nothing)

Sections, in the order they print:
  A  PK non-brand by click date, UK+IE vs the rest, four periods of 2026, with SA360 cost (per day, per dollar)
  B  2025 vs 2026 by click month and segment (seasonality), plus UK excluding the two GB country campaigns
  C  Brand and non-brand together, Aug vs Sep, 2025 and 2026; the same Aug to Sep change in the six markets
  D  The UK effect on each booking measure: Adobe, Floodlight ledger, QR_Booking all_conversions, Google Booking tag
  E  Post-switch bookings against expectation by destination country (the look-elsewhere check)
  F  Rule-based vs ML search value per search and per click against booking value, by group (calibration)
  G  Off-target query share by month on the UK campaigns that were not cut, next to their Adobe booking rate
  H  Searches per click by group and period (SA360)
  I  Adobe non-brand bookings and revenue per SA360 dollar, PK vs SA, CA, MY, by period
  J  Conversion actions that started recording on or after 20 Aug 2026
  K  The 20 Aug cut, rebuilt from SA360 daily cost
  L  Booking lag (booking day minus click day), UK vs the rest

Adobe "clicks" are tracking IDs with at least one flight-search visit, booking or revenue (the pull only returns
rows with a metric), so they are closer to searching visits than to clicks. Bookings are credited to the click day.
UK+IE and long-haul follow scripts/pk_seasonality_adobe.py; the SA360 files carry their own dest_group.
"""
import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pk_seasonality_adobe import load, UK, LONG_HAUL  # noqa: E402

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 60)
pd.set_option("display.max_rows", 400)

ADOBE_PK = "data/adobe/v84_pk_2025-05-01_2026-10-05.parquet"
ADOBE_SIX = "data/adobe/v84_parsed_2026-05-01_2026-10-05.parquet"
R3 = "data/sa360/round3"
EDGES = pd.to_datetime(["2026-06-13", "2026-08-20", "2026-09-02", "2026-09-20", "2026-10-06"])
LABELS = ["13 Jun-19 Aug", "20 Aug-1 Sep", "2-19 Sep", "20 Sep-5 Oct"]
NDAYS = pd.Series([68, 13, 18, 16], index=LABELS)
GB_COUNTRY = {"Google|PK|Dest|Country|XXX|GB|EN|MOD", "Google|PK|O&D|Country|PK|GB|EN|MOD"}
UK_NARROW = {"GB", "IE", "LHR", "LGW", "MAN", "BHX", "EDI", "DUB"}
AIRPORT_COUNTRY = {
    "LHR": "GB", "LGW": "GB", "MAN": "GB", "BHX": "GB", "EDI": "GB", "STN": "GB", "LTN": "GB", "LON": "GB", "GLA": "GB",
    "DUB": "IE", "JFK": "US", "EWR": "US", "IAD": "US", "IAH": "US", "DFW": "US", "ORD": "US", "LAX": "US", "SFO": "US",
    "BOS": "US", "ATL": "US", "MIA": "US", "SEA": "US", "NYC": "US", "CHI": "US", "WAS": "US", "YYZ": "CA", "YUL": "CA",
    "YVR": "CA", "SYD": "AU", "MEL": "AU", "PER": "AU", "BNE": "AU", "ADL": "AU", "AKL": "NZ", "FRA": "DE", "MUC": "DE",
    "BER": "DE", "DUS": "DE", "CDG": "FR", "PAR": "FR", "AMS": "NL", "BCN": "ES", "MAD": "ES", "FCO": "IT", "MXP": "IT",
    "MIL": "IT", "ROM": "IT", "ZRH": "CH", "GVA": "CH", "VIE": "AT", "CPH": "DK", "OSL": "NO", "ARN": "SE", "STO": "SE",
    "HEL": "FI", "BRU": "BE", "LIS": "PT", "ATH": "GR", "WAW": "PL", "PRG": "CZ", "DXB": "AE", "AUH": "AE", "SHJ": "AE",
    "JED": "SA", "RUH": "SA", "DMM": "SA", "MED": "SA", "DOH": "QA", "KUL": "MY", "BKK": "TH", "IST": "TR", "GYD": "AZ",
    "BAK": "AZ", "MCT": "OM", "BAH": "BH", "KWI": "KW", "CAI": "EG", "SIN": "SG", "HKG": "HK", "NRT": "JP", "TYO": "JP",
    "PEK": "CN", "PVG": "CN", "CAN": "CN", "ICN": "KR", "SEL": "KR", "CGK": "ID", "MNL": "PH", "CMB": "LK", "MLE": "MV",
    "NBO": "KE", "JNB": "ZA", "TBS": "GE", "EVN": "AM", "ALA": "KZ", "TAS": "UZ", "HAN": "VN", "SGN": "VN", "DAC": "BD",
    "KTM": "NP",
}


def poisson_le(lam: float, k: int) -> float:
    return sum(math.exp(-lam) * lam ** i / math.factorial(i) for i in range(k + 1)) if lam > 0 else float("nan")


def per_day(t: pd.DataFrame, level: str = "period") -> pd.Series:
    return NDAYS.reindex(t.index.get_level_values(level)).values


def head(title: str) -> None:
    print("\n" + "=" * 100 + f"\n{title}\n" + "=" * 100)


def section_a(nb: pd.DataFrame, tr: pd.DataFrame) -> None:
    head("A. PK non-brand by click date, UK+IE vs the rest, 2026 periods (Adobe bookings and revenue, SA360 cost)")
    first = nb[nb.day == nb.click_day]
    key = ["uk", "period"]
    t = (first.groupby(key, observed=True).agg(adobe_clicks=("v84", "size"))
         .join(nb.groupby(key, observed=True).agg(bookings=("bookings", "sum"), revenue=("revenue", "sum")))
         .join(tr.groupby(key, observed=True).agg(cost=("cost", "sum"), sa_clicks=("clicks", "sum"))))
    t["cost/day"] = (t.cost / per_day(t)).round(0)
    t["bk/day"] = (t.bookings / per_day(t)).round(2)
    t["rev/day"] = (t.revenue / per_day(t)).round(0)
    t["bk per 1k adobe clicks"] = (t.bookings / t.adobe_clicks * 1000).round(2)
    t["bk per $k"] = (t.bookings / t.cost * 1000).round(2)
    t["rev per $"] = (t.revenue / t.cost).round(2)
    t["rev per bk"] = (t.revenue / t.bookings.replace(0, np.nan)).round(0)
    t["cpc"] = (t.cost / t.sa_clicks).round(2)
    for c in ("revenue", "cost"):
        t[c] = t[c].round(0)
    print(t.to_string())
    tot = t.groupby("period", observed=True)[["adobe_clicks", "bookings", "revenue", "cost", "sa_clicks"]].sum()
    tot["cost/day"] = (tot.cost / NDAYS).round(0)
    tot["bk/day"] = (tot.bookings / NDAYS).round(2)
    tot["bk per $k"] = (tot.bookings / tot.cost * 1000).round(2)
    tot["rev per $"] = (tot.revenue / tot.cost).round(2)
    for c in ("revenue", "cost"):
        tot[c] = tot[c].round(0)
    print("\nAll PK non-brand:\n", tot.to_string())


def section_b(d: pd.DataFrame) -> None:
    head("B. 2025 vs 2026 by click month and segment (Adobe)")
    m = d.copy()
    m["month"] = m.click_day.dt.to_period("M")
    first = m[m.day == m.click_day]
    t = (first.groupby(["seg", "month"]).agg(adobe_clicks=("v84", "size"))
         .join(m.groupby(["seg", "month"]).agg(bookings=("bookings", "sum"), revenue=("revenue", "sum"))))
    t["bk per 1k"] = (t.bookings / t.adobe_clicks * 1000).round(2)
    months = [pd.Period(f"{y}-{mm}") for y in (2025, 2026) for mm in ("06", "07", "08", "09", "10")]
    for seg in ["Brand", "NB UK+IE", "NB long-haul", "NB regional", "NB generic/other"]:
        x = t.xs(seg, level="seg").reindex(months)
        print(f"\n{seg}\n", x.round(0).to_string())
    uk = m[(m.seg == "NB UK+IE") & ~m.campaign.isin(GB_COUNTRY)]
    x = (uk.groupby("month").agg(bookings=("bookings", "sum"))
         .join(uk[uk.day == uk.click_day].groupby("month").size().rename("adobe_clicks")))
    x["bk per 1k"] = (x.bookings / x.adobe_clicks * 1000).round(2)
    print("\nNB UK+IE excluding the two GB country campaigns, 2026 by click month\n",
          x.loc[pd.Period("2026-03"):].to_string())
    wk = uk.groupby(uk.click_day.dt.to_period("W-SUN")).agg(bookings=("bookings", "sum"))
    wk["adobe_clicks"] = uk[uk.day == uk.click_day].groupby(uk.click_day.dt.to_period("W-SUN")).size()
    wk = wk[wk.index.start_time >= "2026-06-08"]
    print("\nSame, by click week\n", wk.T.to_string())


def section_c(d: pd.DataFrame, six: pd.DataFrame) -> None:
    head("C. Brand and non-brand together, Aug vs Sep, 2025 and 2026 (Adobe, click month)")
    m = d.copy()
    m["month"] = m.click_day.dt.to_period("M")
    m["bn"] = np.where(m.seg == "Brand", "brand", "non-brand")
    first = m[m.day == m.click_day]
    t = (first.groupby(["bn", "month"]).agg(clicks=("v84", "size"))
         .join(m.groupby(["bn", "month"]).agg(bookings=("bookings", "sum"), revenue=("revenue", "sum"))))
    t["bk per 1k"] = (t.bookings / t.clicks * 1000).round(1)
    t["rev per bk"] = (t.revenue / t.bookings).round(0)
    months = [pd.Period(f"{y}-{mm}") for y in (2025, 2026) for mm in ("07", "08", "09")]
    print(t.loc[(slice(None), months), :].round(0).to_string())
    tot = t.groupby("month")[["bookings", "revenue"]].sum().loc[months]
    for y in (2025, 2026):
        a, s = tot.loc[pd.Period(f"{y}-08")], tot.loc[pd.Period(f"{y}-09")]
        print(f"{y}: total bookings Aug {a.bookings:.0f} -> Sep {s.bookings:.0f} ({s.bookings / a.bookings - 1:+.0%}); "
              f"revenue {a.revenue / 1000:.0f}k -> {s.revenue / 1000:.0f}k ({s.revenue / a.revenue - 1:+.0%})")
    print("\nSix markets, Google paid search, Aug -> Sep 2026 (Adobe, click month):")
    six = six.copy()
    six["month"] = six.click_day.dt.to_period("M")
    fs = six[six.day == six.click_day]
    rows = []
    for (cc, g), x in six.groupby(["cc", "group"]):
        if g == "PMAX":
            continue
        bk = x.groupby("month").bookings.sum()
        cl = fs[(fs.cc == cc) & (fs.group == g)].groupby("month").size()
        a, s = pd.Period("2026-08"), pd.Period("2026-09")
        rows.append({"market": cc, "group": g, "Aug bookings": bk.get(a, 0), "Sep bookings": bk.get(s, 0),
                     "change": f"{bk.get(s, 0) / bk.get(a, 1) - 1:+.0%}", "Aug bk/1k": round(bk.get(a, 0) / cl.get(a, 1) * 1000, 1),
                     "Sep bk/1k": round(bk.get(s, 0) / cl.get(s, 1) * 1000, 1)})
    print(pd.DataFrame(rows).sort_values(["group", "market"]).to_string(index=False))


def section_d(nb: pd.DataFrame, conv: pd.DataFrame, tr: pd.DataFrame) -> None:
    head("D. The UK effect on each booking measure, by period (click date unless stated)")
    key = ["uk", "period"]
    t = tr.groupby(key, observed=True).agg(sa_clicks=("clicks", "sum"))
    nbf = nb[nb.day == nb.click_day]
    t["adobe_clicks"] = nbf.groupby(key, observed=True).size()
    t["Adobe bookings"] = nb.groupby(key, observed=True).bookings.sum()
    for action, name in (("QR_Booking", "QR_Booking all_conv"), ("Booking", "Booking tag (Google)")):
        s = conv[conv.conversion_action == action].groupby(key, observed=True)
        t[name + " click date"] = s.all_conversions.sum().round(1)
        t[name + " conv date"] = s.all_conversions_by_conv_date.sum().round(1)
    led = pd.read_parquet(os.path.join(R3, "b2_booking_ledger.parquet"))
    led["dest"] = led.campaign.str.split("|").str[5].fillna("")
    led["uk"] = np.where(led.dest.isin(UK_NARROW), "UK+IE", "rest")
    for col, name in (("visit_datetime", "ledger rows by visit date"), ("conversion_datetime", "ledger rows by conv date")):
        led["period"] = pd.cut(pd.to_datetime(led[col]), EDGES, right=False, labels=LABELS)
        t[name] = led.groupby(key, observed=True).size()
    t = t.fillna(0)
    print(t.to_string())
    print("(The ledger starts with visits on 2 Aug 2026, so its first period covers 2 to 19 Aug only.)")
    print("\nPer 1,000 SA360 clicks:")
    r = t[["Adobe bookings", "QR_Booking all_conv click date", "Booking tag (Google) click date", "ledger rows by visit date"]]
    print(r.div(t.sa_clicks, axis=0).mul(1000).round(2).to_string())
    uk = t.loc["UK+IE"]
    pre_rate = uk["Adobe bookings"].iloc[:2].sum() / uk.adobe_clicks.iloc[:2].sum()
    for i, lab in enumerate(LABELS[2:], start=2):
        lam = pre_rate * uk.adobe_clicks.iloc[i]
        obs = int(uk["Adobe bookings"].iloc[i])
        print(f"Adobe UK+IE {lab}: {uk.adobe_clicks.iloc[i]:.0f} clicks, expected {lam:.1f} at the 13 Jun-1 Sep rate "
              f"({pre_rate * 1000:.2f} per 1k), observed {obs}, P(<= obs) = {poisson_le(lam, obs):.3f}")
    lam = pre_rate * uk.adobe_clicks.iloc[2:].sum()
    obs = int(uk["Adobe bookings"].iloc[2:].sum())
    print(f"Adobe UK+IE 2 Sep-5 Oct together: expected {lam:.1f}, observed {obs}, P(<= obs) = {poisson_le(lam, obs):.4f}")
    rest = t.loc["rest"]
    rr = rest["Adobe bookings"].iloc[2:].sum() / rest.adobe_clicks.iloc[2:].sum()
    rr_pre = rest["Adobe bookings"].iloc[:2].sum() / rest.adobe_clicks.iloc[:2].sum()
    print(f"Rest: {rr_pre * 1000:.2f} per 1k before, {rr * 1000:.2f} after ({rr / rr_pre - 1:+.0%}); "
          f"if UK+IE had kept its pre-switch ratio to the rest ({pre_rate / rr_pre:.1f}x), expected "
          f"{pre_rate / rr_pre * rr * uk.adobe_clicks.iloc[2:].sum():.1f}, observed {obs}")


def section_e(nb: pd.DataFrame) -> None:
    head("E. Post-switch bookings against expectation by destination country (Adobe, 13 Jun-1 Sep vs 2 Sep-5 Oct)")
    x = nb.copy()
    x["country"] = x.dest.map(lambda c: AIRPORT_COUNTRY.get(c, c if c else "generic"))
    pre = x[(x.click_day >= "2026-06-13") & (x.click_day < "2026-09-02")]
    post = x[x.click_day >= "2026-09-02"]
    fpre, fpost = pre[pre.day == pre.click_day], post[post.day == post.click_day]
    t = pd.DataFrame({"clicks_pre": fpre.groupby("country").size(), "bk_pre": pre.groupby("country").bookings.sum(),
                      "clicks_post": fpost.groupby("country").size(), "bk_post": post.groupby("country").bookings.sum()}).fillna(0)
    t["expected_post"] = (t.bk_pre / t.clicks_pre * t.clicks_post).round(2)
    t["P(<= obs)"] = [round(poisson_le(l, int(o)), 3) for l, o in zip(t.expected_post, t.bk_post)]
    t["P(>= obs)"] = [round(1 - poisson_le(l, int(o) - 1), 3) if o > 0 else float("nan") for l, o in zip(t.expected_post, t.bk_post)]
    print(t[(t.bk_pre + t.bk_post) >= 2].sort_values("bk_pre", ascending=False).to_string())
    print(f"Countries with at least 2 bookings over both windows: {((t.bk_pre + t.bk_post) >= 2).sum()}")


def section_f(conv: pd.DataFrame, tr: pd.DataFrame) -> None:
    head("F. Rule-based vs ML search value against booking value, by destination group (SA360, click date)")
    c = conv[conv.date < "2026-09-02"].copy()
    c["w"] = np.where(c.date < "2026-08-20", "13 Jun-19 Aug", "20 Aug-1 Sep")
    c = c[c.date >= "2026-06-13"]
    t2 = tr[(tr.date >= "2026-06-13") & (tr.date < "2026-09-02")]
    out = pd.DataFrame({"clicks": t2.groupby("dest_group").clicks.sum(), "cost": t2.groupby("dest_group").cost.sum().round(0)})
    for action, name in (("QR_FlightSearch_VBB", "rule"), ("QR_FlightSearch_VBB_ML", "ML"), ("QR_Booking", "booking")):
        s = c[c.conversion_action == action].groupby("dest_group")
        out[name + " n"] = s.all_conversions.sum()
        out[name + " $"] = s.all_conversions_value.sum().round(0)
    out = out.loc[["UK+IE", "long-haul", "regional"]]
    r = pd.DataFrame({
        "clicks": out.clicks, "cost": out.cost,
        "rule $ per search": (out["rule $"] / out["rule n"]).round(1),
        "ML $ per search": (out["ML $"] / out["ML n"]).round(1),
        "rule $ per click": (out["rule $"] / out.clicks).round(1),
        "ML $ per click": (out["ML $"] / out.clicks).round(1),
        "booking $ per click": (out["booking $"] / out.clicks).round(2),
        "rule / booking": (out["rule $"] / out["booking $"]).round(1),
        "ML / booking": (out["ML $"] / out["booking $"]).round(1),
        "ML / rule": (out["ML $"] / out["rule $"]).round(2)})
    print("13 Jun-1 Sep 2026 (before the switch):\n", r.to_string())
    print("\nSame ratios after the switch (2 Sep-5 Oct; QR_Booking is incomplete here, so only rule / ML are meaningful):")
    c = conv[conv.date >= "2026-09-02"]
    t2 = tr[tr.date >= "2026-09-02"]
    out = pd.DataFrame({"clicks": t2.groupby("dest_group").clicks.sum()})
    for action, name in (("QR_FlightSearch_VBB", "rule"), ("QR_FlightSearch_VBB_ML", "ML")):
        s = c[c.conversion_action == action].groupby("dest_group")
        out[name + " n"] = s.all_conversions.sum()
        out[name + " $"] = s.all_conversions_value.sum()
    out = out.loc[["UK+IE", "long-haul", "regional"]]
    print(pd.DataFrame({"rule $ per search": (out["rule $"] / out["rule n"]).round(1),
                        "ML $ per search": (out["ML $"] / out["ML n"]).round(1),
                        "rule $ per click": (out["rule $"] / out.clicks).round(1),
                        "ML $ per click": (out["ML $"] / out.clicks).round(1)}).to_string())


def section_g(nb: pd.DataFrame) -> None:
    head("G. Off-target queries on the UK+IE campaigns not cut on 20 Aug, by month (search terms report), with Adobe booking rate")
    st = pd.read_parquet("data/search_terms/pk_nonbrand_2026-05_2026-10.parquet")
    st["m"] = pd.to_datetime(st.Month, format="%B %Y").dt.to_period("M")
    uk = st[st.is_uk & ~st.gb_country_cut]
    share = uk.groupby(["m", "direction"]).Clicks.sum().unstack().fillna(0)
    tot = share.sum(axis=1)
    share = (share.div(tot, axis=0) * 100).round(1)
    share["off-target (reverse + generic + UK to elsewhere)"] = (
        share.get("reverse (UK to PK)", 0) + share.get("neither", 0) + share.get("UK to elsewhere", 0)).round(1)
    share["search-term clicks"] = tot
    ukr = nb[(nb.uk == "UK+IE") & ~nb.campaign.isin(GB_COUNTRY)].copy()
    ukr["m"] = ukr.click_day.dt.to_period("M")
    ab = ukr.groupby("m").bookings.sum().rename("Adobe bookings").to_frame()
    ab["Adobe clicks"] = ukr[ukr.day == ukr.click_day].groupby("m").size()
    ab["Adobe bk per 1k"] = (ab["Adobe bookings"] / ab["Adobe clicks"] * 1000).round(2)
    print(share.join(ab).to_string())


def section_h(conv: pd.DataFrame, tr: pd.DataFrame) -> None:
    head("H. Searches per click by group and period (SA360: QR_FlightSearch_VBB and Flight Search over clicks)")
    key = ["dest_group", "period"]
    t = tr.groupby(key, observed=True).clicks.sum().to_frame()
    for a in ("QR_FlightSearch_VBB", "Flight Search", "Flight Search (TEST Sept2026)"):
        t[a + " per click"] = (conv[conv.conversion_action == a].groupby(key, observed=True).all_conversions.sum() / t.clicks).round(3)
    print(t.loc[["UK+IE", "long-haul", "regional"]].fillna(0).to_string())


def section_i(six: pd.DataFrame) -> None:
    head("I. Adobe non-brand bookings and revenue per SA360 dollar, by market and period")
    x = six[(six.group == "Non-brand") & six.cc.isin(["PK", "SA", "CA", "MY"])].copy()
    x["period"] = pd.cut(x.click_day, EDGES, right=False, labels=LABELS)
    ab = x.groupby(["cc", "period"], observed=True).agg(bookings=("bookings", "sum"), revenue=("revenue", "sum"))
    cost = {"SA": pd.read_csv("data/sa360/round5_SA/e1_sa_by_period.csv").set_index("period").cost}
    for m in ("CA", "MY", "PK"):
        f = pd.read_csv(f"data/sa360/round6_CA_MY/f_{m}_by_period.csv")
        cost[m] = f[f.dest_group == "ALL"].set_index("period").cost
    t = ab.join(pd.concat(cost, names=["cc", "period"]).rename("cost"))
    t["cost/day"] = (t.cost / per_day(t)).round(0)
    t["bk/day"] = (t.bookings / per_day(t)).round(2)
    t["bk per $k"] = (t.bookings / t.cost * 1000).round(2)
    t["rev per $"] = (t.revenue / t.cost).round(2)
    for c in ("revenue", "cost"):
        t[c] = t[c].round(0)
    print(t.to_string())
    for m in ("PK", "SA", "CA", "MY"):
        y = t.loc[m]
        base, post = y.loc["13 Jun-19 Aug"], y.loc[["2-19 Sep", "20 Sep-5 Oct"]].sum()
        print(f"{m}: 2 Sep-5 Oct vs 13 Jun-19 Aug: bookings per $ {post.bookings / post.cost / (base.bookings / base.cost) - 1:+.0%}, "
              f"revenue per $ {post.revenue / post.cost / (base.revenue / base.cost) - 1:+.0%}, spend per day "
              f"{post.cost / 34 / (base.cost / 68) - 1:+.0%}, on {post.bookings:.0f} post-switch bookings")


def section_j(conv: pd.DataFrame) -> None:
    head("J. Conversion actions in the PK non-brand account that first record on or after 20 Aug 2026")
    t = conv.groupby("conversion_action").agg(first=("date", "min"), last=("date", "max"), conversions=("all_conversions", "sum"),
                                              value=("all_conversions_value", "sum"))
    print(t[t["first"] >= "2026-08-01"].round(0).to_string())


def section_k(tr: pd.DataFrame) -> None:
    head("K. The 20 Aug cut, rebuilt from SA360 daily cost (campaigns at $3+ a day on 10-19 Aug whose 21 Aug-1 Sep cost fell to 40% or less)")
    x = tr.copy()
    x["d"] = pd.to_datetime(x.date)
    a = x[x.d.between("2026-08-10", "2026-08-19")].groupby(["campaign_name", "dest_group"]).cost.sum() / 10
    b = x[x.d.between("2026-08-21", "2026-09-01")].groupby(["campaign_name", "dest_group"]).cost.sum().reindex(a.index, fill_value=0) / 12
    c = x[x.d.between("2026-09-20", "2026-10-05")].groupby(["campaign_name", "dest_group"]).cost.sum().reindex(a.index, fill_value=0) / 16
    t = pd.DataFrame({"10-19 Aug $/day": a, "21 Aug-1 Sep $/day": b, "20 Sep-5 Oct $/day": c})
    t = t[t["10-19 Aug $/day"] >= 3]
    t["cut"] = t["21 Aug-1 Sep $/day"] / t["10-19 Aug $/day"] <= 0.4
    print(t.groupby(["cut", t.index.get_level_values(1)]).agg(campaigns=("cut", "size"), **{k: (k, "sum") for k in t.columns[:3]}).round(0).to_string())
    print("\nLargest cut campaigns:\n", t[t.cut].sort_values("10-19 Aug $/day", ascending=False).head(12).round(1).to_string())
    print("\nAccount daily cost 17 Aug-5 Sep:\n", x.groupby("d").cost.sum().loc["2026-08-17":"2026-09-05"].round(0).to_string())


def section_l(nb: pd.DataFrame) -> None:
    head("L. Booking lag in days (booking day minus click day), share of bookings within n days")
    x = nb[nb.bookings > 0].copy()
    x["lag"] = (x.day - x.click_day).dt.days
    for name, s in (("UK+IE 13 Jun-1 Sep 2026", x[(x.uk == "UK+IE") & (x.click_day >= "2026-06-13") & (x.click_day < "2026-09-02")]),
                    ("rest 13 Jun-1 Sep 2026", x[(x.uk != "UK+IE") & (x.click_day >= "2026-06-13") & (x.click_day < "2026-09-02")]),
                    ("UK+IE Jun-Sep 2025", x[(x.uk == "UK+IE") & (x.click_day >= "2025-06-01") & (x.click_day < "2025-10-01")])):
        w = s.bookings
        print(f"{name}: n={w.sum():.0f}, same day {w[s.lag == 0].sum() / w.sum():.0%}, within 7 days {w[s.lag <= 7].sum() / w.sum():.0%}, "
              f"within 16 days {w[s.lag <= 16].sum() / w.sum():.0%}, max {s.lag.max()} days")


def main() -> None:
    d = load(ADOBE_PK)
    nb = d[d.seg.str.startswith("NB")].copy()
    nb["period"] = pd.cut(nb.click_day, EDGES, right=False, labels=LABELS)
    nb["uk"] = np.where(nb.seg == "NB UK+IE", "UK+IE", "rest")
    conv = pd.read_parquet(os.path.join(R3, "pk_nb_daily_2026.parquet"))
    tr = pd.read_parquet(os.path.join(R3, "pk_nb_traffic_2026.parquet"))
    for x in (conv, tr):
        x["period"] = pd.cut(pd.to_datetime(x.date), EDGES, right=False, labels=LABELS)
        x["uk"] = np.where(x.dest_group == "UK+IE", "UK+IE", "rest")
    six = pd.read_parquet(ADOBE_SIX)
    six = six[six.parsed & (six.engine == "Google") & six.cc.isin(["PK", "SA", "CA", "MY", "DE", "SG"])].copy()
    six["v84"] = six.click_key
    six = six.join(six.groupby("v84").day.min().rename("click_day"), on="v84")

    section_a(nb, tr)
    section_b(d)
    section_c(d, six)
    section_d(nb, conv, tr)
    section_e(nb)
    section_f(conv, tr)
    section_g(nb)
    section_h(conv, tr)
    section_i(six)
    section_j(conv)
    section_k(tr)
    section_l(nb)


if __name__ == "__main__":
    main()
