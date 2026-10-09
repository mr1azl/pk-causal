"""R21: pull CA and DE VBB rows so the calibration test has a control group.

Same parser and same privacy handling as r14. PK and India are the markets that
lost booking rate; Canada and Germany are the comparison. If the miscalibration
is identical in markets that did not collapse, it cannot be the cause.
"""
import json, re, sys, hashlib
from lib_gads import RAW, chunks
from lib_sa360 import stream

IATA = re.compile(r"^[a-z]{3}$")
MARKETS = {"CA": "4096344384", "DE": "3218295582"}
D1, D2 = "2026-08-13", "2026-10-05"


def h(x):
    return hashlib.sha256(str(x).encode()).hexdigest()[:20] if x else ""


def parse(oid):
    p = [x.strip().lower() for x in (oid or "").split("-")]
    t = p[0] if p else ""
    o = p[1] if len(p) > 1 and IATA.match(p[1]) else ""
    d = p[2] if len(p) > 2 and IATA.match(p[2]) else ""
    tail = "-".join(p[3:]) if (o and d) else ("-".join(p[2:]) if len(p) > 2 else "")
    return t, o, d, h(tail.split("_")[0] if tail else "")


for lab, acc in MARKETS.items():
    for action, short in [("QR_FlightSearch_VBB", "base"), ("QR_FlightSearch_VBB_ML", "ml")]:
        for a, b in chunks(D1, D2, 7):
            path = RAW / f"r14_{lab}_{short}_{a}_{b}.jsonl"
            if path.exists():
                print(f"   skip {path.name}"); continue
            c, rows = stream(acc,
                "SELECT segments.date, segments.conversion_action_name, "
                "conversion.floodlight_order_id, conversion.conversion_revenue_micros, "
                "conversion.conversion_quantity, campaign.id, campaign.name "
                "FROM conversion "
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
