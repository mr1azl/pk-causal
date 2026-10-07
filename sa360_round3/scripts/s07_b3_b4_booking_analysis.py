"""B3 and B4: what one Floodlight booking is, duplicates, and the destination split.

    cd scripts && python3 s07_b3_b4_booking_analysis.py

Writes data/clean/b3_bookings_daily.csv, data/clean/b4_bookings_by_destgroup.csv
"""
import csv, json, collections, datetime
from lib_sa360 import RAW, CLEAN, dest_group, dest_code

rows = [json.loads(l) for l in (RAW / "b2_booking_conversions.jsonl").read_text(encoding="utf-8").splitlines()]
print(f"{len(rows)} booking conversion rows, 2026-08-01 to 2026-10-05\n")

def f(r):
    c = r["conversion"]
    return {
        "action": r["segments"]["conversionActionName"],
        "date": c.get("conversionDateTime", "")[:10],
        "visit": c.get("conversionVisitDateTime", "")[:10],
        "rev": int(c.get("conversionRevenueMicros", 0) or 0) / 1e6,
        "orig": float(c.get("floodlightOriginalRevenue", 0) or 0),
        "qty": float(c.get("conversionQuantity", 0) or 0),
        "status": c.get("status", ""),
        "attrib": c.get("attributionType", ""),
        "oid": c.get("floodlight_order_id_sha256", ""),
        "camp": r.get("campaign", {}).get("name", ""),
    }
R = [f(r) for r in rows]

print("=== B3a. what one row carries ===")
print(f"{'action':<26s}{'rows':>6s}{'sum qty':>9s}{'revenue':>12s}{'zero rev':>9s}"
      f"{'qty=1':>7s}{'qty>1':>7s}{'qty=0':>7s}")
for a in sorted({x['action'] for x in R}):
    s = [x for x in R if x["action"] == a]
    print(f"{a:<26s}{len(s):>6d}{sum(x['qty'] for x in s):>9,.0f}"
          f"{sum(x['rev'] for x in s):>12,.0f}{sum(1 for x in s if x['rev']==0):>9d}"
          f"{sum(1 for x in s if x['qty']==1):>7d}{sum(1 for x in s if x['qty']>1):>7d}"
          f"{sum(1 for x in s if x['qty']==0):>7d}")

print("\n=== B3b. duplicates on the hashed order ID ===")
par_oid = collections.defaultdict(list)
for x in R:
    if x["oid"]:
        par_oid[x["oid"]].append(x)
dups = {k: v for k, v in par_oid.items() if len(v) > 1}
print(f"   distinct order IDs {len(par_oid):,d}, appearing more than once: {len(dups):,d}")
mixtes = {k: v for k, v in dups.items() if sum(1 for y in v if y['rev'] > 0) == 1}
tous_rev = {k: v for k, v in dups.items() if all(y['rev'] > 0 for y in v)}
print(f"   of those, revenue on only one row: {len(mixtes):,d}")
print(f"   of those, revenue on every row:    {len(tous_rev):,d}")
if dups:
    tailles = collections.Counter(len(v) for v in dups.values())
    print(f"   duplicate group sizes: {dict(sorted(tailles.items()))}")
    paires = collections.Counter(tuple(sorted({y['action'] for y in v})) for v in dups.values())
    print("   action combinations inside a duplicate group:")
    for k, n in paires.most_common():
        print(f"      {n:>4d}  {' + '.join(k)}")

print("\n=== B3c. per day and action ===")
CLEAN.mkdir(parents=True, exist_ok=True)
J = collections.defaultdict(lambda: collections.defaultdict(float))
for x in R:
    k = (x["date"], x["action"])
    J[k]["rows"] += 1; J[k]["qty"] += x["qty"]; J[k]["rev"] += x["rev"]
    if x["rev"] == 0: J[k]["zero"] += 1
with (CLEAN / "b3_bookings_daily.csv").open("w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["date", "conversion_action", "rows", "sum_quantity", "revenue", "rows_zero_revenue"])
    for (d, a) in sorted(J):
        v = J[(d, a)]
        w.writerow([d, a, int(v["rows"]), round(v["qty"], 2), round(v["rev"], 2), int(v["zero"])])
print(f"   wrote b3_bookings_daily.csv, {len(J)} rows")

print("\n=== B4. destination group, before and after 2 Sep ===")
lignes = []
print(f"{'group':<12s}{'period':<12s}{'rows':>6s}{'qty':>8s}{'revenue':>12s}"
      f"{'rev/row':>10s}{'zero rev':>9s}")
for g in ("UK+IE", "long-haul", "regional", "none", "UK+IE (outside brief list)"):
    for lab, lo, hi in (("pre 2 Sep", "2026-08-01", "2026-09-01"),
                        ("from 2 Sep", "2026-09-02", "2026-10-05")):
        s = [x for x in R if dest_group(x["camp"]) == g and lo <= x["date"] <= hi]
        if not s and g in ("none", "UK+IE (outside brief list)"):
            continue
        rev = sum(x["rev"] for x in s)
        print(f"{g:<12s}{lab:<12s}{len(s):>6d}{sum(x['qty'] for x in s):>8,.0f}{rev:>12,.0f}"
              f"{rev/len(s) if s else 0:>10,.0f}{sum(1 for x in s if x['rev']==0):>9d}")
        lignes.append([g, lab, len(s), round(sum(x['qty'] for x in s), 2), round(rev, 2),
                       sum(1 for x in s if x['rev'] == 0)])
with (CLEAN / "b4_bookings_by_destgroup.csv").open("w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["dest_group", "period", "rows", "sum_quantity", "revenue", "rows_zero_revenue"])
    w.writerows(lignes)
print(f"   wrote b4_bookings_by_destgroup.csv")

print("\n=== B3d. status, attribution, revenue integrity ===")
print("   status:", dict(collections.Counter(x["status"] for x in R)))
print("   attribution:", dict(collections.Counter(x["attrib"] for x in R)))
mismatch = [x for x in R if abs(x["rev"] - x["orig"]) > 0.01]
print(f"   rows where reported revenue differs from floodlight original: {len(mismatch)}")
print(f"   rows with revenue 0 but original > 0: {sum(1 for x in R if x['rev']==0 and x['orig']>0)}")
