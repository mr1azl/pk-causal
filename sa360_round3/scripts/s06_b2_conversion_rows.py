"""B2: conversion level rows for the PK booking actions, 2026-08-01 to 2026-10-05.

The Floodlight order ID is hashed with SHA-256 inside this script before anything is written
to disk, including data/raw/. Only the hash and a short prefix of it ever exist in a file, so
no handed back artefact can carry an order ID or a GA client ID.

    cd scripts && python3 s06_b2_conversion_rows.py

Writes data/raw/b2_booking_conversions.jsonl (order ID already hashed)
"""
import hashlib, json
from lib_sa360 import stream, chunks, RAW, is_non_brand

PK = "4851538229"
D1, D2 = "2026-08-01", "2026-10-05"
ACTIONS = {"QR_Booking", "Booking", "Android App Booking", "iOS App Booking",
           "QR_DiscoverQatar_Booking", "Retrieve Booking", "DONOTUSE_BOOKINGS"}

Q = ("SELECT conversion.id, segments.conversion_action_name, conversion.conversion_date_time, "
     "conversion.conversion_visit_date_time, conversion.conversion_revenue_micros, "
     "conversion.floodlight_original_revenue, conversion.conversion_quantity, "
     "conversion.status, conversion.attribution_type, conversion.floodlight_order_id, "
     "conversion.advertiser_conversion_id, campaign.id, campaign.name "
     "FROM conversion WHERE segments.date BETWEEN '{a}' AND '{b}'")

def h(x):
    return hashlib.sha256(str(x).encode("utf-8")).hexdigest() if x not in (None, "") else ""

f = RAW / "b2_booking_conversions.jsonl"
total = garde = 0
with f.open("w", encoding="utf-8") as out:
    for a, b in chunks(D1, D2, 31):
        code, rows = stream(PK, Q.format(a=a, b=b))
        if code != 200:
            print(f"   {a}..{b}: HTTP {code} -> {str(rows)[:160]}")
            continue
        total += len(rows)
        n = 0
        for r in rows:
            act = r.get("segments", {}).get("conversionActionName")
            if act not in ACTIONS:
                continue
            if not is_non_brand(r.get("campaign", {}).get("name")):
                continue
            c = r["conversion"]
            # hash before writing, and drop the plaintext identifiers entirely
            c["floodlight_order_id_sha256"] = h(c.pop("floodlightOrderId", None))
            c["advertiser_conversion_id_sha256"] = h(c.pop("advertiserConversionId", None))
            out.write(json.dumps(r, ensure_ascii=False) + "\n")
            n += 1
        garde += n
        print(f"   {a}..{b}: {len(rows):,d} conversion rows, {n:,d} booking rows kept")
print(f"\ntotal conversion rows scanned {total:,d}, booking rows written {garde:,d}")
print("order IDs are SHA-256 hashed in every file, including data/raw/")
