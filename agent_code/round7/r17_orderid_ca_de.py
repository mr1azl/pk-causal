"""R17: is the {search,sales}-OnD-cookie order ID format the same in Canada and
Germany, or is it a PK and India convention?

Germany is the market the readiness report flagged for an unexplained outage on
30 September, so whether its tag is shaped the same matters beyond curiosity.
Only the first three tokens are read; nothing identifying is printed.
"""
import collections, re
from lib_sa360 import stream

IATA = re.compile(r"^[a-z]{3}$")
MARKETS = [("CA EN", "4096344384"), ("CA FR", "9362154318"),
           ("DE de", "4116587214"), ("DE en", "3218295582"),
           ("PK", "4851538229"), ("IN", "4034062923")]
ACTIONS = ["QR_FlightSearch_VBB", "QR_FlightSearch_VBB_ML", "QR_Booking"]

for lab, acc in MARKETS:
    print(f"\n=== {lab} ({acc}) ===")
    for action in ACTIONS:
        c, rows = stream(acc,
            "SELECT segments.date, segments.conversion_action_name, "
            "conversion.floodlight_order_id, conversion.conversion_revenue_micros "
            "FROM conversion WHERE segments.date BETWEEN '2026-09-22' AND '2026-10-05' "
            f"AND segments.conversion_action_name = '{action}' LIMIT 3000")
        if c != 200:
            print(f"   {action:<24} ERROR {str(rows)[:70]}"); continue
        if not rows:
            print(f"   {action:<24} 0 rows"); continue
        types = collections.Counter(); ond = 0; opaque = 0
        rev = collections.defaultdict(list)
        for r in rows:
            oid = (r["conversion"].get("floodlightOrderId") or "").lower()
            p = [x.strip() for x in oid.split("-")]
            t = p[0] if p else ""
            if len(p) == 1 and len(t) >= 32:
                opaque += 1; t = "(opaque hash)"
            types[t if t in ("search", "sales", "(opaque hash)") else "(other)"] += 1
            if len(p) > 2 and IATA.match(p[1]) and IATA.match(p[2]):
                ond += 1
            rev[types and (t if t in ("search", "sales") else "other")].append(
                int(r["conversion"].get("conversionRevenueMicros", 0)) / 1e6)
        n = len(rows)
        print(f"   {action:<24} {n:>5,d} rows   "
              f"types {dict(types.most_common(3))}   OnD parsed {ond/n*100:>5.1f}%")
        for t in ("search", "sales"):
            v = rev.get(t)
            if v:
                print(f"        {t:<7} n={len(v):>5,d}  mean {sum(v)/len(v):>9.2f}  "
                      f"min {min(v):>8.2f}  max {max(v):>9.2f}")
