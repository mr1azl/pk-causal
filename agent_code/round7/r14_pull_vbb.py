"""R14: pull every VBB and VBB_ML conversion row, both types.

The order ID is {search|sales}-OnD-cookieid_session. That means the VBB tag
fires on bookings as well as searches, and the sales rows carry both the OnD and
the real transaction value. QR_Booking's own order ID is a single opaque hash,
so until now booking value could not be attributed to a destination at all.
This can.

Privacy: the cookie and session are personal data. Only tokens 0, 1 and 2 are
read, the OnD tokens are accepted only if they look like IATA codes, and the
tail is hashed immediately so journeys can be joined without storing identity.
The file written holds no identifier, only the hash.
"""
import json, re, sys, hashlib
from lib_gads import RAW, chunks
from lib_sa360 import stream

IATA = re.compile(r"^[a-z]{3}$")
ACTIONS = ["QR_FlightSearch_VBB", "QR_FlightSearch_VBB_ML"]
MARKETS = {"PK": "4851538229", "IN": "4034062923"}
D1, D2 = sys.argv[1], sys.argv[2]


def h(x):
    return hashlib.sha256(str(x).encode()).hexdigest()[:20] if x else ""


def parse(oid):
    """(type, origin, dest, journey_hash). Tail is hashed, never stored raw."""
    p = [x.strip().lower() for x in (oid or "").split("-")]
    t = p[0] if p else ""
    o = p[1] if len(p) > 1 and IATA.match(p[1]) else ""
    d = p[2] if len(p) > 2 and IATA.match(p[2]) else ""
    tail = "-".join(p[3:]) if len(p) > 3 else ""
    # the cookie sits in position 2 when the OND is absent, so hash whatever is
    # left after the recognised structural tokens
    if not d and len(p) > 2:
        tail = "-".join(p[2:])
    return t, o, d, h(tail.split("_")[0] if tail else "")


for lab, acc in MARKETS.items():
    for action in ACTIONS:
        short = "ml" if action.endswith("_ML") else "base"
        for a, b in chunks(D1, D2, 7):
            path = RAW / f"r14_{lab}_{short}_{a}_{b}.jsonl"
            if path.exists():
                print(f"   skip {path.name} ({sum(1 for _ in open(path, encoding='utf-8')):,d})")
                continue
            c, rows = stream(acc,
                "SELECT segments.date, segments.conversion_action_name, "
                "conversion.floodlight_order_id, conversion.conversion_revenue_micros, "
                "conversion.floodlight_original_revenue, conversion.conversion_quantity, "
                "campaign.id, campaign.name FROM conversion "
                f"WHERE segments.date BETWEEN '{a}' AND '{b}' "
                f"AND segments.conversion_action_name = '{action}'")
            if c != 200:
                sys.exit(f"FAILED {lab} {action} {a}..{b}: {rows}")
            with open(path, "w", encoding="utf-8") as fh:
                for r in rows:
                    cv = r["conversion"]
                    t, o, d, j = parse(cv.get("floodlightOrderId"))
                    fh.write(json.dumps({
                        "date": r["segments"]["date"], "market": lab, "model": short,
                        "type": t, "origin": o, "dest": d, "journey": j,
                        "rev": int(cv.get("conversionRevenueMicros", 0)) / 1e6,
                        "qty": cv.get("conversionQuantity"),
                        "campaign": r["campaign"].get("name"),
                    }, separators=(",", ":")) + "\n")
            print(f"   {path.name}: {len(rows):,d}")
print("done")
