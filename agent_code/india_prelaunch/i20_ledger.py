"""I2: the QR_Booking transaction ledger, last 8 weeks.

Field names corrected against searchAds360Fields: the resource exposes
conversion_visit_date_time (not visit_date_time), floodlight_original_revenue
(not ..._micros, and it is still in micros, the PK unit trap), and the action
name comes from segments, not from the conversion resource.

Order IDs, floodlight order IDs, click IDs and merchant IDs are hashed inside
this script before anything is written, so no raw identifier and no GA client
ID reaches data/raw/, data/clean/, the log or the console.
"""
import json, hashlib, sys
from lib_sa360 import stream, chunks, RAW, IN_ACCOUNT

D1, D2 = "2026-08-13", "2026-10-07"      # 8 weeks to yesterday
SENSITIVE = ("advertiserConversionId", "floodlightOrderId", "clickId",
             "id", "merchantId", "criterionId", "visitId", "adId")

def h(x):
    return hashlib.sha256(str(x).encode()).hexdigest()[:24] if x not in (None, "") else ""

Q = ("SELECT segments.date, segments.conversion_action_name, "
     "conversion.id, conversion.conversion_date_time, conversion.conversion_visit_date_time, "
     "conversion.conversion_quantity, conversion.conversion_revenue_micros, "
     "conversion.floodlight_original_revenue, conversion.status, "
     "conversion.attribution_type, conversion.advertiser_conversion_id, "
     "conversion.floodlight_order_id, conversion.criterion_id, "
     "campaign.id, campaign.name "
     "FROM conversion WHERE segments.date BETWEEN '{d1}' AND '{d2}' "
     "AND segments.conversion_action_name = 'QR_Booking'")

total = 0
for d1, d2 in chunks(D1, D2, 31):
    path = RAW / f"i2_ledger_{d1}_{d2}.jsonl"
    if path.exists():
        n = sum(1 for _ in open(path, encoding="utf-8"))
        print(f"   skip {path.name} ({n:,d} rows)"); total += n; continue
    c, rows = stream(IN_ACCOUNT, Q.format(d1=d1, d2=d2))
    if c != 200:
        sys.exit(f"FAILED {d1}..{d2}: {c} {rows}")
    with open(path, "w", encoding="utf-8") as fh:
        for r in rows:
            cv = r.get("conversion", {})
            for k in SENSITIVE:
                if k in cv:
                    cv[k + "_hash"] = h(cv.pop(k))
            # the conversion resource name embeds the raw conversion and visit
            # ids, so it is hashed too rather than written through
            if "resourceName" in cv:
                cv["resourceName_hash"] = h(cv.pop("resourceName"))
            fh.write(json.dumps(r, separators=(",", ":")) + "\n")
    print(f"   {path.name}: {len(rows):,d} rows"); total += len(rows)
print(f"ledger pull complete, {total:,d} rows, {D1} to {D2}")
