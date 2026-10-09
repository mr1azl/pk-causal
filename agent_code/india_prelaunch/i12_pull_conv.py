"""I1b: daily campaign conversions by conversion action, for the actions that
matter to a VBB launch. Separate query from traffic because segmenting by
conversion_action_name forbids cost and clicks in the same SELECT
(PROHIBITED_SEGMENT_WITH_METRIC_IN_SELECT_OR_WHERE_CLAUSE, learned in PK).
Joined to traffic on date plus campaign id downstream.
"""
import json, sys
from lib_sa360 import stream, chunks, RAW, IN_ACCOUNT

D1, D2 = sys.argv[1], sys.argv[2]
ACTIONS = ["QR_Booking", "Booking", "QR_FlightSearch", "QR_FlightSearch_VBB",
           "QR_FlightSearch_VBB_ML", "Flight Search", "Flight Search (TEST Sept2026)"]
IN_LIST = ", ".join("'" + a.replace("'", "\\'") + "'" for a in ACTIONS)

Q = ("SELECT segments.date, segments.conversion_action_name, campaign.id, "
     "metrics.all_conversions, metrics.all_conversions_value, "
     "metrics.cross_device_conversions "
     "FROM campaign WHERE segments.date BETWEEN '{d1}' AND '{d2}' "
     f"AND segments.conversion_action_name IN ({IN_LIST})")

for d1, d2 in chunks(D1, D2, 31):
    path = RAW / f"i1_conv_{d1}_{d2}.jsonl"
    if path.exists():
        print(f"   skip {path.name} ({sum(1 for _ in open(path, encoding='utf-8')):,d} rows)")
        continue
    c, rows = stream(IN_ACCOUNT, Q.format(d1=d1, d2=d2))
    if c != 200:
        sys.exit(f"FAILED {d1}..{d2}: {c} {rows}")
    with open(path, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, separators=(",", ":")) + "\n")
    print(f"   {path.name}: {len(rows):,d} rows")
print("conversion pull complete")
