"""I1c: weekly summary by destination group, both years.

Joins traffic to conversions on date plus campaign id. Share metrics are
impression weighted, and the share of impressions sitting on a clamped value
(exactly 10.0 or 90.0) is reported alongside so a clamped average is never read
as a real one.
"""
import csv, json, collections, datetime, glob, sys
from lib_sa360 import RAW, CLEAN, IN_ACCOUNT, in_dest_group, is_non_brand

names = {}
for r in csv.DictReader(open(CLEAN / "i0_campaign_inventory.csv", encoding="utf-8")):
    names[r["campaign_id"]] = r["name"]

def week(d):
    dt = datetime.date.fromisoformat(d)
    return (dt - datetime.timedelta(days=dt.weekday())).isoformat()   # Monday

SH = [("impr_share", "searchImpressionShare"), ("top_share", "searchTopImpressionShare"),
      ("budget_lost", "searchBudgetLostImpressionShare"),
      ("rank_lost", "searchRankLostImpressionShare")]

def blank():
    d = {"cost": 0.0, "clicks": 0, "impressions": 0}
    for k, _ in SH:
        d[k + "_w"] = 0.0; d[k + "_impr"] = 0; d[k + "_clamped_impr"] = 0
    return d

T = collections.defaultdict(blank)                    # (year, week, group) -> traffic
C = collections.defaultdict(lambda: collections.defaultdict(float))   # key -> action -> metric

for p in sorted(glob.glob(str(RAW / "i1_traffic_*.jsonl"))):
    for line in open(p, encoding="utf-8"):
        r = json.loads(line)
        cid = r["campaign"]["id"]; nm = names.get(cid) or r["campaign"].get("name", "")
        if not is_non_brand(nm):
            continue
        d = r["segments"]["date"]; k = (d[:4], week(d), in_dest_group(nm))
        m = r.get("metrics", {}); imp = int(m.get("impressions", 0))
        t = T[k]
        t["cost"] += int(m.get("costMicros", 0)) / 1e6
        t["clicks"] += int(m.get("clicks", 0)); t["impressions"] += imp
        for key, api in SH:
            if api in m:
                v = float(m[api]) * 100
                t[key + "_w"] += v * imp; t[key + "_impr"] += imp
                if abs(v - 10.0) < 1e-9 or abs(v - 90.0) < 1e-9:
                    t[key + "_clamped_impr"] += imp

for p in sorted(glob.glob(str(RAW / "i1_conv_*.jsonl"))):
    for line in open(p, encoding="utf-8"):
        r = json.loads(line)
        cid = r["campaign"]["id"]; nm = names.get(cid, "")
        if not is_non_brand(nm):
            continue
        d = r["segments"]["date"]; k = (d[:4], week(d), in_dest_group(nm))
        a = r["segments"]["conversionActionName"]; m = r.get("metrics", {})
        C[k][a + "|n"] += float(m.get("allConversions", 0))
        C[k][a + "|v"] += float(m.get("allConversionsValue", 0))
        C[k][a + "|x"] += float(m.get("crossDeviceConversions", 0))

rows = []
for k in sorted(set(T) | set(C)):
    yr, wk, grp = k
    t = T.get(k, blank()); c = C.get(k, {})
    cl = t["clicks"]
    def per1k(a): return round(c.get(a + "|n", 0) / cl * 1000, 3) if cl else ""
    row = {"year": yr, "week": wk, "dest_group": grp,
           "cost": round(t["cost"], 2), "clicks": cl, "impressions": t["impressions"],
           "cpc": round(t["cost"] / cl, 4) if cl else "",
           "qr_booking": round(c.get("QR_Booking|n", 0), 2),
           "qr_booking_value": round(c.get("QR_Booking|v", 0), 2),
           "qr_booking_xdev": round(c.get("QR_Booking|x", 0), 2),
           "qr_booking_xdev_pct": round(c.get("QR_Booking|x", 0) / c["QR_Booking|n"] * 100, 2)
                                   if c.get("QR_Booking|n") else "",
           "qr_booking_per_1k_clicks": per1k("QR_Booking"),
           "booking_webpage": round(c.get("Booking|n", 0), 2),
           "booking_webpage_value": round(c.get("Booking|v", 0), 2),
           "booking_webpage_per_1k_clicks": per1k("Booking"),
           "flight_search": round(c.get("Flight Search|n", 0), 2),
           "flight_search_per_click": round(c.get("Flight Search|n", 0) / cl, 4) if cl else "",
           "qr_flightsearch": round(c.get("QR_FlightSearch|n", 0), 2),
           "vbb_n": round(c.get("QR_FlightSearch_VBB|n", 0), 2),
           "vbb_value": round(c.get("QR_FlightSearch_VBB|v", 0), 2),
           "vbb_ml_n": round(c.get("QR_FlightSearch_VBB_ML|n", 0), 2),
           "vbb_ml_value": round(c.get("QR_FlightSearch_VBB_ML|v", 0), 2)}
    for key, _ in SH:
        imp = t[key + "_impr"]
        row[key] = round(t[key + "_w"] / imp, 2) if imp else ""
        row[key + "_clamped_pct"] = round(t[key + "_clamped_impr"] / imp * 100, 2) if imp else ""
    rows.append(row)

dest = CLEAN / "i1_weekly_by_group.csv"
with open(dest, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(f"wrote {dest.name}, {len(rows):,d} rows")

# compact console view: 2026 totals per group over the window
print("\n=== 2026, 12 weeks to 7 Oct, by destination group ===")
agg = collections.defaultdict(lambda: collections.Counter())
for r in rows:
    if r["year"] != "2026":
        continue
    a = agg[r["dest_group"]]
    for f in ["cost", "clicks", "impressions", "qr_booking", "qr_booking_xdev",
              "booking_webpage", "flight_search", "vbb_n", "vbb_value",
              "vbb_ml_value", "qr_booking_value", "booking_webpage_value"]:
        a[f] += float(r[f] or 0)
hdr = (f"{'group':<28}{'cost':>10}{'clicks':>10}{'CPC':>7}{'QRbk':>8}{'/1k':>7}"
       f"{'xdev%':>7}{'WEBbk':>8}{'/1k':>7}{'FS/clk':>8}{'VBBval/clk':>11}")
print(hdr); print("-" * len(hdr))
for g, a in sorted(agg.items(), key=lambda kv: -kv[1]["cost"]):
    cl = a["clicks"]
    if not cl: continue
    print(f"{g:<28}{a['cost']:>10,.0f}{cl:>10,.0f}{a['cost']/cl:>7.3f}"
          f"{a['qr_booking']:>8,.0f}{a['qr_booking']/cl*1000:>7.2f}"
          f"{(a['qr_booking_xdev']/a['qr_booking']*100 if a['qr_booking'] else 0):>6.1f}%"
          f"{a['booking_webpage']:>8,.0f}{a['booking_webpage']/cl*1000:>7.2f}"
          f"{a['flight_search']/cl:>8.3f}{a['vbb_value']/cl:>11.2f}")
