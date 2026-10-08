"""I3b: share of VBB search values at exactly 0.50 (the fallback) and at 0,
by destination group and by destination, last 4 weeks.

Privacy. The floodlight order ID on these rows has the shape
    search - <origin> - <destination> - <tail>
and when the OND is missing the tail shifts left, so position 2 can hold a GA
client ID beginning "GA1.". Only tokens 0, 1 and 2 are read, token 1 and 2 are
accepted only when they match three lowercase letters, and anything else is
recorded as "(no OND)". The tail is never read, never stored and never printed.
The file written to data/raw/ is already sanitised: it holds no identifier of
any kind, only type, origin, destination, revenue, campaign and date.
"""
import json, re, sys, collections
from lib_sa360 import stream, chunks, RAW, IN_ACCOUNT

D1, D2 = "2026-09-10", "2026-10-07"      # 4 weeks to yesterday
IATA = re.compile(r"^[a-z]{3}$")

Q = ("SELECT segments.date, segments.conversion_action_name, "
     "conversion.floodlight_order_id, conversion.conversion_revenue_micros, "
     "conversion.floodlight_original_revenue, campaign.name FROM conversion "
     "WHERE segments.date BETWEEN '{d1}' AND '{d2}' "
     "AND segments.conversion_action_name = 'QR_FlightSearch_VBB'")


def ond(oid):
    """Return (type, origin, destination) and nothing else. Positions that do
    not look like an IATA code are discarded rather than stored."""
    p = [x.strip().lower() for x in (oid or "").split("-")]
    t = p[0] if p else ""
    o = p[1] if len(p) > 1 and IATA.match(p[1]) else ""
    d = p[2] if len(p) > 2 and IATA.match(p[2]) else ""
    return t, o, d


total = 0
for d1, d2 in chunks(D1, D2, 7):
    path = RAW / f"i3_vbb_{d1}_{d2}.jsonl"
    if path.exists():
        n = sum(1 for _ in open(path, encoding="utf-8"))
        print(f"   skip {path.name} ({n:,d} rows)"); total += n; continue
    c, rows = stream(IN_ACCOUNT, Q.format(d1=d1, d2=d2))
    if c != 200:
        sys.exit(f"FAILED {d1}..{d2}: {c} {rows}")
    with open(path, "w", encoding="utf-8") as fh:
        for r in rows:
            cv = r["conversion"]
            t, o, d = ond(cv.get("floodlightOrderId"))
            fh.write(json.dumps({
                "date": r["segments"]["date"],
                "campaign": r["campaign"].get("name"),
                "type": t, "origin": o, "dest": d,
                "rev": int(cv.get("conversionRevenueMicros", 0)) / 1e6,
                "flrev": int(cv.get("floodlightOriginalRevenue", 0)) / 1e6,
            }, separators=(",", ":")) + "\n")
    print(f"   {path.name}: {len(rows):,d} rows"); total += len(rows)
print(f"VBB search pull complete, {total:,d} rows, {D1} to {D2}")
