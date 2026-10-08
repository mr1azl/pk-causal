"""I3a: value calibration by destination. The PK UK failure.

Search value per click (QR_FlightSearch_VBB value / clicks) against booking
value per click, measured two ways:
  ledger  = QR_Booking transaction revenue / clicks, the reliable view
  attrib  = QR_Booking all_conversions_value / clicks, the view the bidder sees

A group whose search value runs high relative to its booking value is one the
bidder will overpay for. Flag threshold: ratio above 1.3 times the median ratio.
Window is the 8 weeks the ledger covers so both sides use the same days.
"""
import csv, json, glob, collections, statistics
from lib_sa360 import RAW, CLEAN, in_dest_group, is_non_brand, dest_code

D1, D2 = "2026-08-13", "2026-10-07"
names = {r["campaign_id"]: r["name"]
         for r in csv.DictReader(open(CLEAN / "i0_campaign_inventory.csv", encoding="utf-8"))}


def fmt(v, spec, dash="n/a"):
    """Format a number, or a placeholder when the value is blank."""
    return format(v, spec) if v != "" and v is not None else dash


clicks_g = collections.Counter(); clicks_d = collections.Counter()
cost_g = collections.Counter(); cost_d = collections.Counter()
for p in sorted(glob.glob(str(RAW / "i1_traffic_2026-*.jsonl"))):
    for line in open(p, encoding="utf-8"):
        r = json.loads(line)
        if not (D1 <= r["segments"]["date"] <= D2):
            continue
        nm = names.get(r["campaign"]["id"]) or r["campaign"].get("name", "")
        if not is_non_brand(nm):
            continue
        m = r.get("metrics", {}); cl = int(m.get("clicks", 0))
        co = int(m.get("costMicros", 0)) / 1e6
        clicks_g[in_dest_group(nm)] += cl; clicks_d[dest_code(nm)] += cl
        cost_g[in_dest_group(nm)] += co; cost_d[dest_code(nm)] += co

vbb_g = collections.Counter(); vbb_d = collections.Counter()
att_g = collections.Counter(); att_d = collections.Counter()
for p in sorted(glob.glob(str(RAW / "i1_conv_2026-*.jsonl"))):
    for line in open(p, encoding="utf-8"):
        r = json.loads(line)
        s = r["segments"]
        if not (D1 <= s["date"] <= D2):
            continue
        nm = names.get(r["campaign"]["id"])
        if nm is None or not is_non_brand(nm):
            continue
        v = float(r.get("metrics", {}).get("allConversionsValue", 0))
        if s["conversionActionName"] == "QR_FlightSearch_VBB":
            vbb_g[in_dest_group(nm)] += v; vbb_d[dest_code(nm)] += v
        elif s["conversionActionName"] == "QR_Booking":
            att_g[in_dest_group(nm)] += v; att_d[dest_code(nm)] += v

led_g = collections.Counter(); led_d = collections.Counter()
for p in sorted(glob.glob(str(RAW / "i2_ledger_*.jsonl"))):
    for line in open(p, encoding="utf-8"):
        c = json.loads(line); nm = c["campaign"].get("name")
        if not is_non_brand(nm):
            continue
        rev = int(c["conversion"].get("conversionRevenueMicros", 0)) / 1e6
        led_g[in_dest_group(nm)] += rev; led_d[dest_code(nm)] += rev


def table(keys, clicks, cost, vbb, led, att, label, minclicks=0):
    rows = []
    for k in keys:
        cl = clicks[k]
        if cl <= minclicks:
            continue
        s = vbb[k] / cl
        b_led = led[k] / cl
        b_att = att[k] / cl
        rows.append({label: k, "clicks": cl, "cost": round(cost[k], 2),
                     "search_value_per_click": round(s, 4),
                     "booking_value_per_click_ledger": round(b_led, 4),
                     "booking_value_per_click_attributed": round(b_att, 4),
                     "ratio_ledger": round(s / b_led, 3) if b_led else "",
                     "ratio_attributed": round(s / b_att, 3) if b_att else ""})
    return rows


groups = table(sorted(clicks_g), clicks_g, cost_g, vbb_g, led_g, att_g, "dest_group")
rl = [r["ratio_ledger"] for r in groups if r["ratio_ledger"] != ""]
ra = [r["ratio_attributed"] for r in groups if r["ratio_attributed"] != ""]
med_l, med_a = statistics.median(rl), statistics.median(ra)

for r in groups:
    for which, med in (("ledger", med_l), ("attributed", med_a)):
        v = r["ratio_" + which]
        r["vs_median_" + which] = round(v / med, 3) if v != "" else ""
        r["flag_" + which] = "yes" if v != "" and v > 1.3 * med else "no"
        r["scale_to_median_" + which] = round(med / v, 3) if v else ""

print("=== value calibration by destination group, " + D1 + " to " + D2 + " ===")
print(f"median ratio: ledger {med_l:.2f}, attributed {med_a:.2f}\n")
print(f"{'group':<26}{'clicks':>9}{'srch val/clk':>13}{'bkg/clk led':>12}"
      f"{'ratio':>8}{'x median':>10}{'scale':>7}{'flag':>6}")
print("-" * 91)
for r in sorted(groups, key=lambda x: -(x["ratio_ledger"] or 0)):
    print(f"{r['dest_group']:<26}{r['clicks']:>9,d}{r['search_value_per_click']:>13.2f}"
          f"{r['booking_value_per_click_ledger']:>12.2f}"
          f"{fmt(r['ratio_ledger'], '.2f'):>8}"
          f"{fmt(r['vs_median_ledger'], '.2f', ''):>10}"
          f"{fmt(r['scale_to_median_ledger'], '.2f', ''):>7}"
          f"{r['flag_ledger']:>6}")

with open(CLEAN / "i3_calibration_by_group.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(groups[0].keys())); w.writeheader(); w.writerows(groups)

top = [k for k, _ in clicks_d.most_common(30) if k]
dests = table(top, clicks_d, cost_d, vbb_d, led_d, att_d, "dest_code")
rld = [r["ratio_ledger"] for r in dests if r["ratio_ledger"] != ""]
medd = statistics.median(rld) if rld else 0
for r in dests:
    v = r["ratio_ledger"]
    r["vs_median_ledger"] = round(v / medd, 3) if v != "" and medd else ""
    r["flag_ledger"] = "yes" if v != "" and medd and v > 1.3 * medd else "no"
    r["scale_to_median_ledger"] = round(medd / v, 3) if v else ""
    r["no_bookings_in_window"] = "yes" if r["ratio_ledger"] == "" else "no"

print(f"\n=== top 30 destinations by clicks, median ratio {medd:.2f} ===")
print(f"{'code':<7}{'clicks':>9}{'cost':>10}{'srch/clk':>10}{'bkg/clk':>10}"
      f"{'ratio':>9}{'x med':>8}{'flag':>6}")
print("-" * 69)
for r in sorted(dests, key=lambda x: -(x["ratio_ledger"] if x["ratio_ledger"] != "" else -1)):
    print(f"{r['dest_code']:<7}{r['clicks']:>9,d}{r['cost']:>10,.0f}"
          f"{r['search_value_per_click']:>10.2f}{r['booking_value_per_click_ledger']:>10.2f}"
          f"{fmt(r['ratio_ledger'], '.2f', 'no bkgs'):>9}"
          f"{fmt(r['vs_median_ledger'], '.2f', ''):>8}"
          f"{r['flag_ledger']:>6}")

with open(CLEAN / "i3_calibration_by_destination.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(dests[0].keys())); w.writeheader(); w.writerows(dests)
print("\nwrote i3_calibration_by_group.csv and i3_calibration_by_destination.csv")
