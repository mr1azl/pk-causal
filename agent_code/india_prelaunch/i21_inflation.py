"""I2b: ledger structure, and the all_conversions over ledger inflation ratio
with cross-device share, by destination group. Flags any group above 3x.

Scope correction made after the first run: the ledger query carries no
non-brand filter, so it included `Google|IN|Perf_Max|Generic|XXX|XXX|EN`, while
the campaign inventory excludes Performance Max by construction. That put 103
ledger rows in "other" and their attributed twins in "none". Performance Max is
now excluded from the group table and reported on its own line, because it is
not part of the search portfolios a VBB launch would move.
"""
import csv, json, glob, collections
from lib_sa360 import RAW, CLEAN, in_dest_group, is_non_brand

D1, D2 = "2026-08-13", "2026-10-07"
PMAX = "perf_max"

led_all = [json.loads(l) for p in sorted(glob.glob(str(RAW / "i2_ledger_*.jsonl")))
           for l in open(p, encoding="utf-8")]
led = [c for c in led_all if is_non_brand(c["campaign"].get("name"))]
pmax = [c for c in led_all if PMAX in (c["campaign"].get("name") or "").lower()]
print(f"ledger rows {len(led_all):,d} total, {len(led):,d} search non-brand, "
      f"{len(pmax):,d} Performance Max, {D1} to {D2}")

q = collections.Counter(c["conversion"].get("conversionQuantity") for c in led_all)
st = collections.Counter(c["conversion"].get("status") for c in led_all)
at = collections.Counter(c["conversion"].get("attributionType") for c in led_all)
print(f"  conversion_quantity: {dict(q)}")
print(f"  status: {dict(st)}   attribution: {dict(at)}")
mism = sum(1 for c in led_all
           if int(c["conversion"].get("conversionRevenueMicros", 0))
           != int(c["conversion"].get("floodlightOriginalRevenue", 0)))
print(f"  revenue against floodlight_original_revenue: {mism} of {len(led_all)} disagree "
      f"(both in micros, the PK unit trap)")
dupes = [k for k, n in collections.Counter(
    c["conversion"].get("floodlightOrderId_hash") for c in led_all).items() if n > 1 and k]
print(f"  duplicate hashed order IDs: {len(dupes)}")

G = collections.defaultdict(lambda: {"rows": 0, "rev": 0.0, "zero": 0})
for c in led:
    g = in_dest_group(c["campaign"].get("name"))
    rev = int(c["conversion"].get("conversionRevenueMicros", 0)) / 1e6
    G[g]["rows"] += 1; G[g]["rev"] += rev
    if rev == 0:
        G[g]["zero"] += 1

names = {r["campaign_id"]: r["name"]
         for r in csv.DictReader(open(CLEAN / "i0_campaign_inventory.csv", encoding="utf-8"))}
A = collections.defaultdict(lambda: collections.Counter())
pmax_a = collections.Counter()
for p in sorted(glob.glob(str(RAW / "i1_conv_2026-*.jsonl"))):
    for line in open(p, encoding="utf-8"):
        r = json.loads(line)
        if r["segments"]["conversionActionName"] != "QR_Booking":
            continue
        if not (D1 <= r["segments"]["date"] <= D2):
            continue
        m = r.get("metrics", {})
        nm = names.get(r["campaign"]["id"])
        if nm is None:                      # not in the non-brand inventory: Performance Max
            pmax_a["all"] += float(m.get("allConversions", 0))
            pmax_a["xdev"] += float(m.get("crossDeviceConversions", 0))
            pmax_a["val"] += float(m.get("allConversionsValue", 0))
            continue
        g = in_dest_group(nm)
        A[g]["all"] += float(m.get("allConversions", 0))
        A[g]["xdev"] += float(m.get("crossDeviceConversions", 0))
        A[g]["val"] += float(m.get("allConversionsValue", 0))

out = []
print(f"\n{'group':<28}{'ledger':>8}{'all_conv':>10}{'ratio':>8}{'xdev %':>8}"
      f"{'same-dev/ledger':>17}{'zero rev':>9}{'flag':>6}")
print("-" * 95)
rows_sorted = sorted(set(G) | set(A), key=lambda k: -A[k]["all"])
for g in rows_sorted:
    rows = G[g]["rows"]; all_ = A[g]["all"]; x = A[g]["xdev"]
    if not rows and not all_:
        continue
    ratio = all_ / rows if rows else None
    same = (all_ - x) / rows if rows else None
    xp = x / all_ * 100 if all_ else 0
    flag = "FLAG" if ratio and ratio > 3 else ""
    print(f"{g:<28}{rows:>8,d}{all_:>10,.0f}"
          f"{(f'{ratio:.2f}' if ratio else 'n/a'):>8}{xp:>7.1f}%"
          f"{(f'{same:.2f}' if same else 'n/a'):>17}{G[g]['zero']:>9,d}{flag:>6}")
    out.append({"dest_group": g, "ledger_rows": rows,
                "ledger_revenue": round(G[g]["rev"], 2), "zero_revenue_rows": G[g]["zero"],
                "zero_revenue_pct": round(G[g]["zero"] / rows * 100, 2) if rows else "",
                "all_conversions": round(all_, 1), "all_conversions_value": round(A[g]["val"], 2),
                "cross_device": round(x, 1), "cross_device_pct": round(xp, 2),
                "all_over_ledger": round(ratio, 3) if ratio else "",
                "same_device_over_ledger": round(same, 3) if same else "",
                "flag_above_3x": "yes" if ratio and ratio > 3 else "no"})

pr = len(pmax)
pratio = pmax_a["all"] / pr if pr else None
print(f"{'Performance Max (separate)':<28}{pr:>8,d}{pmax_a['all']:>10,.0f}"
      f"{(f'{pratio:.2f}' if pratio else 'n/a'):>8}"
      f"{(pmax_a['xdev']/pmax_a['all']*100 if pmax_a['all'] else 0):>7.1f}%")
out.append({"dest_group": "Performance Max (not a search portfolio)", "ledger_rows": pr,
            "ledger_revenue": round(sum(int(c["conversion"].get("conversionRevenueMicros", 0))/1e6
                                        for c in pmax), 2),
            "zero_revenue_rows": sum(1 for c in pmax
                                     if int(c["conversion"].get("conversionRevenueMicros", 0)) == 0),
            "zero_revenue_pct": "", "all_conversions": round(pmax_a["all"], 1),
            "all_conversions_value": round(pmax_a["val"], 2),
            "cross_device": round(pmax_a["xdev"], 1),
            "cross_device_pct": round(pmax_a["xdev"]/pmax_a["all"]*100, 2) if pmax_a["all"] else "",
            "all_over_ledger": round(pratio, 3) if pratio else "",
            "same_device_over_ledger": round((pmax_a["all"]-pmax_a["xdev"])/pr, 3) if pr else "",
            "flag_above_3x": "yes" if pratio and pratio > 3 else "no"})

with open(CLEAN / "i2_inflation_by_group.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

tr = len(led); ta = sum(A[g]["all"] for g in A); tx = sum(A[g]["xdev"] for g in A)
print(f"\nsearch non-brand: ledger {tr:,d}, all_conversions {ta:,.0f}, ratio {ta/tr:.2f}, "
      f"same-device over ledger {(ta-tx)/tr:.2f}")
print(f"ledger revenue {sum(G[g]['rev'] for g in G):,.0f} USD, "
      f"attributed value {sum(A[g]['val'] for g in A):,.0f} USD, "
      f"ratio {sum(A[g]['val'] for g in A)/sum(G[g]['rev'] for g in G):.2f}")
print(f"Performance Max holds {pr} of {len(led_all)} ledger rows "
      f"({pr/len(led_all)*100:.0f}% of all India bookings)")
print("\nwrote i2_inflation_by_group.csv")
