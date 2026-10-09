"""Go table item 1: if a target ROAS is to be set, what does the last 8 weeks
say the starting value should be?

Three candidate denominators, because the answer depends entirely on which value
signal the portfolio reads, and that is the UI question from I1:
  VBB search value / cost      if the portfolio optimises the search value signal
  booking attributed value / cost
  booking ledger revenue / cost   what actually happened
Setting a target against the wrong one is the fastest way to repeat PK.
"""
import csv, json, glob, collections
from lib_sa360 import RAW, CLEAN, in_dest_group, is_non_brand

D1, D2 = "2026-08-13", "2026-10-07"
inv = {r["campaign_id"]: r["name"] for r in csv.DictReader(
    open(CLEAN / "i0_campaign_inventory.csv", encoding="utf-8"))}

cost = collections.Counter()
for p in sorted(glob.glob(str(RAW / "i1_traffic_2026-*.jsonl"))):
    for line in open(p, encoding="utf-8"):
        r = json.loads(line)
        if not (D1 <= r["segments"]["date"] <= D2):
            continue
        nm = inv.get(r["campaign"]["id"])
        if nm is None or not is_non_brand(nm):
            continue
        cost[in_dest_group(nm)] += int(r.get("metrics", {}).get("costMicros", 0)) / 1e6

vbb = collections.Counter(); att = collections.Counter()
for p in sorted(glob.glob(str(RAW / "i1_conv_2026-*.jsonl"))):
    for line in open(p, encoding="utf-8"):
        r = json.loads(line); s = r["segments"]
        if not (D1 <= s["date"] <= D2):
            continue
        nm = inv.get(r["campaign"]["id"])
        if nm is None or not is_non_brand(nm):
            continue
        v = float(r.get("metrics", {}).get("allConversionsValue", 0))
        if s["conversionActionName"] == "QR_FlightSearch_VBB":
            vbb[in_dest_group(nm)] += v
        elif s["conversionActionName"] == "QR_Booking":
            att[in_dest_group(nm)] += v

led = collections.Counter()
for p in sorted(glob.glob(str(RAW / "i2_ledger_*.jsonl"))):
    for line in open(p, encoding="utf-8"):
        c = json.loads(line); nm = c["campaign"].get("name")
        if not is_non_brand(nm):
            continue
        led[in_dest_group(nm)] += int(c["conversion"].get("conversionRevenueMicros", 0)) / 1e6

out = []
print(f"=== realised return on ad spend, {D1} to {D2} ===\n")
print(f"{'group':<26}{'cost':>10}{'VBB value':>12}{'ROAS vbb':>10}"
      f"{'ROAS attrib':>13}{'ROAS ledger':>13}")
print("-" * 84)
for g in sorted(cost, key=lambda k: -cost[k]):
    c = cost[g]
    if c < 100:
        continue
    print(f"{g:<26}{c:>10,.0f}{vbb[g]:>12,.0f}{vbb[g]/c:>10.1f}"
          f"{att[g]/c:>13.1f}{led[g]/c:>13.2f}")
    out.append({"dest_group": g, "cost_8w": round(c, 2),
                "vbb_search_value": round(vbb[g], 2), "roas_on_vbb_search_value": round(vbb[g]/c, 2),
                "booking_attributed_value": round(att[g], 2),
                "roas_on_attributed_bookings": round(att[g]/c, 2),
                "booking_ledger_revenue": round(led[g], 2),
                "roas_on_ledger_revenue": round(led[g]/c, 3)})

C = sum(cost.values()); V = sum(vbb.values()); A = sum(att.values()); L = sum(led.values())
print("-" * 84)
print(f"{'ALL':<26}{C:>10,.0f}{V:>12,.0f}{V/C:>10.1f}{A/C:>13.1f}{L/C:>13.2f}")
out.append({"dest_group": "ALL", "cost_8w": round(C, 2), "vbb_search_value": round(V, 2),
            "roas_on_vbb_search_value": round(V/C, 2),
            "booking_attributed_value": round(A, 2), "roas_on_attributed_bookings": round(A/C, 2),
            "booking_ledger_revenue": round(L, 2), "roas_on_ledger_revenue": round(L/C, 3)})
with open(CLEAN / "i8_target_roas.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

print(f"\nIf the portfolio reads the VBB search value, the account is currently returning "
      f"{V/C:.1f}x on it.")
print(f"A target ROAS set at that level holds spend roughly where it is. Setting it lower, or "
      f"leaving it unset as PK SA CA and MY all did, lets the bidder buy volume at any price.")
print("\nwrote i8_target_roas.csv")
