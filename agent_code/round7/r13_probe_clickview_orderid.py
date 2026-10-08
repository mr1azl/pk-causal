"""R13 probe: two questions.

1 Does click_view carry anything useful? It holds a gclid, which is personal
  data, so the test is whether the non-identifying columns justify using it at
  all. Nothing identifying is printed.
2 The VBB Floodlight order ID is said to be {search,sales}-OnD-cookieid_session.
  If both a search row and a sales row exist under the same cookie, the search
  value and the booking value can be joined at journey level, which is exactly
  what the calibration question needs. Only the type and OND tokens are read;
  the cookie is hashed immediately and never printed or written.
"""
import collections, hashlib, re
from lib_gads import search as gsearch, fields, ACCOUNTS
from lib_sa360 import stream

print("=== 1. click_view: does it exist and what does it carry ===")
f, err = fields("name LIKE 'click_view.%'")
print(f"   {len(f) if f else err} fields")
for x in sorted(f or [], key=lambda z: z["name"]):
    print(f"      {x['name']:<44} {x.get('dataType','')}")

print("\n   can it be queried, and over what window")
for d1 in ["2026-06-13", "2026-07-10", "2026-09-01", "2026-09-20", "2026-10-01"]:
    r, e = gsearch(ACCOUNTS["pk_nonbrand"],
        "SELECT click_view.gclid, campaign.name, segments.date "
        f"FROM click_view WHERE segments.date = '{d1}' LIMIT 5")
    print(f"      {d1}: {e[:90] if e else f'{len(r)} rows'}")

print("\n=== 2. VBB order ID structure, SA360 conversion resource ===")
for acc, lab in [("4851538229", "PK"), ("4034062923", "IN")]:
    for action in ["QR_FlightSearch_VBB", "QR_FlightSearch_VBB_ML", "QR_Booking"]:
        c, rows = stream(acc,
            "SELECT segments.conversion_action_name, conversion.floodlight_order_id, "
            "conversion.conversion_revenue_micros, campaign.name FROM conversion "
            "WHERE segments.date BETWEEN '2026-09-29' AND '2026-10-05' "
            f"AND segments.conversion_action_name = '{action}' LIMIT 4000")
        if c != 200:
            print(f"   {lab} {action}: {rows}"); continue
        types = collections.Counter()
        ntok = collections.Counter()
        rev_by_type = collections.defaultdict(list)
        for r in rows:
            oid = r["conversion"].get("floodlightOrderId") or ""
            p = [x.strip().lower() for x in oid.split("-")]
            t = p[0] if p else "(empty)"
            types[t] += 1; ntok[len(p)] += 1
            rev_by_type[t].append(int(r["conversion"].get("conversionRevenueMicros", 0)) / 1e6)
        print(f"\n   {lab} {action}: {len(rows):,d} rows")
        print(f"      first token: {dict(types.most_common(6))}")
        print(f"      token counts: {dict(ntok.most_common(5))}")
        for t, v in rev_by_type.items():
            if not v: continue
            print(f"      type '{t}': n={len(v):,d} mean rev {sum(v)/len(v):>9.2f} "
                  f"min {min(v):.2f} max {max(v):.2f}")
