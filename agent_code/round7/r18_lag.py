"""R18: quantify the search to booking lag.

I have cited lag twice as a reason a ratio is understated without ever measuring
it. Two measures, from different clocks:

  A click to conversion   conversion_visit_date_time -> conversion_date_time,
                          available on every row including QR_Booking
  B search to booking     within one hashed journey, the first VBB search row
                          to the VBB sales row. This is the one that matters for
                          the value proxy, because it is the window over which a
                          search value is supposed to predict a booking.

Measure B is right censored: a booking that happens after the pull window is
never seen, so the mean is biased down and the tail is cut. The share still
open at each horizon is reported so the censoring is visible rather than hidden.
"""
import collections, csv, datetime, hashlib, re, statistics, sys
from lib_sa360 import stream
from lib_gads import CLEAN

IATA = re.compile(r"^[a-z]{3}$")
MARKETS = [("PK", "4851538229"), ("IN", "4034062923"),
           ("CA", "4096344384"), ("DE", "3218295582")]
D1, D2 = "2026-08-13", "2026-10-05"


def h(x):
    return hashlib.sha256(str(x).encode()).hexdigest()[:20] if x else ""


def ts(s):
    for f in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime((s or "")[:19], f)
        except Exception:
            pass
    return None


def pct(v, p):
    v = sorted(v)
    return v[min(len(v) - 1, int(len(v) * p / 100))] if v else 0


print("=== A. click to conversion lag, in hours ===")
print(f"{'market':<8}{'action':<26}{'n':>7}{'median':>9}{'mean':>9}{'p90':>8}{'p99':>9}{'max':>9}")
print("-" * 85)
rowsA = []
for lab, acc in MARKETS:
    for action in ["QR_Booking", "QR_FlightSearch_VBB"]:
        c, rows = stream(acc,
            "SELECT segments.conversion_action_name, conversion.conversion_date_time, "
            "conversion.conversion_visit_date_time, conversion.floodlight_order_id "
            f"FROM conversion WHERE segments.date BETWEEN '{D1}' AND '{D2}' "
            f"AND segments.conversion_action_name = '{action}' LIMIT 6000")
        if c != 200 or not rows:
            continue
        lags = []
        for r in rows:
            a = ts(r["conversion"].get("conversionVisitDateTime"))
            b = ts(r["conversion"].get("conversionDateTime"))
            if a and b and b >= a:
                lags.append((b - a).total_seconds() / 3600)
        if len(lags) < 5:
            continue
        print(f"{lab:<8}{action:<26}{len(lags):>7,d}{statistics.median(lags):>9.1f}"
              f"{sum(lags)/len(lags):>9.1f}{pct(lags,90):>8.1f}{pct(lags,99):>9.1f}{max(lags):>9.1f}")
        rowsA.append({"market": lab, "action": action, "n": len(lags),
                      "median_h": round(statistics.median(lags), 2),
                      "mean_h": round(sum(lags) / len(lags), 2),
                      "p90_h": round(pct(lags, 90), 2), "p99_h": round(pct(lags, 99), 2),
                      "max_h": round(max(lags), 2),
                      "same_day_pct": round(sum(1 for x in lags if x < 24) / len(lags) * 100, 1)})

print("\n   share converting within 24 hours of the click:")
for r in rowsA:
    print(f"      {r['market']:<4}{r['action']:<26}{r['same_day_pct']:>6.1f}%")

print("\n=== B. search to booking lag, within one journey, in days ===")
rowsB = []
for lab, acc in MARKETS:
    J = collections.defaultdict(lambda: {"s": [], "b": []})
    for action in ["QR_FlightSearch_VBB"]:
        c, rows = stream(acc,
            "SELECT segments.conversion_action_name, conversion.conversion_date_time, "
            "conversion.floodlight_order_id FROM conversion "
            f"WHERE segments.date BETWEEN '{D1}' AND '{D2}' "
            f"AND segments.conversion_action_name = '{action}'")
        if c != 200:
            print(f"   {lab}: {rows}"); continue
        for r in rows:
            oid = (r["conversion"].get("floodlightOrderId") or "").lower()
            p = [x.strip() for x in oid.split("-")]
            if not p:
                continue
            t = p[0]
            tail = "-".join(p[3:]) if (len(p) > 3 and IATA.match(p[1]) and IATA.match(p[2])) \
                else "-".join(p[2:]) if len(p) > 2 else ""
            j = h(tail.split("_")[0]) if tail else ""
            d = ts(r["conversion"].get("conversionDateTime"))
            if not j or not d:
                continue
            if t == "search":
                J[j]["s"].append(d)
            elif t == "sales":
                J[j]["b"].append(d)
    pairs = []
    for v in J.values():
        if v["b"] and v["s"]:
            first = min(v["s"]); book = min(v["b"])
            if book >= first:
                pairs.append((book - first).total_seconds() / 86400)
    if len(pairs) < 5:
        print(f"   {lab}: only {len(pairs)} linked journeys, too few"); continue
    hz = {f"within_{d}d": round(sum(1 for x in pairs if x <= d) / len(pairs) * 100, 1)
          for d in (0, 1, 3, 7, 14, 30)}
    print(f"\n   --- {lab}: {len(J):,d} journeys, {len(pairs):,d} with a search and a booking ---")
    print(f"      median {statistics.median(pairs):>6.2f} d   mean {sum(pairs)/len(pairs):>6.2f} d   "
          f"p90 {pct(pairs,90):>6.2f} d   max {max(pairs):>6.2f} d")
    print("      cumulative share booked: " + "  ".join(f"{k.replace('within_','')} {v}%"
                                                        for k, v in hz.items()))
    rowsB.append({"market": lab, "journeys": len(J), "linked": len(pairs),
                  "median_days": round(statistics.median(pairs), 3),
                  "mean_days": round(sum(pairs) / len(pairs), 3),
                  "p90_days": round(pct(pairs, 90), 3), "max_days": round(max(pairs), 2), **hz})

if rowsA:
    with open(CLEAN / "r18_click_to_conversion_lag.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rowsA[0].keys())); w.writeheader(); w.writerows(rowsA)
if rowsB:
    with open(CLEAN / "r18_search_to_booking_lag.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rowsB[0].keys())); w.writeheader(); w.writerows(rowsB)
print("\nwrote r18_click_to_conversion_lag.csv and r18_search_to_booking_lag.csv")
