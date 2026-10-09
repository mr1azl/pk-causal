"""I1 step 0: which conversion actions exist and fire for India, so the baseline
queries name real actions rather than assumed ones."""
import csv, collections
from lib_sa360 import stream, CLEAN, IN_ACCOUNT, chunks

c, rows = stream(IN_ACCOUNT, "SELECT conversion_action.id, conversion_action.name, "
                             "conversion_action.type, conversion_action.status, "
                             "conversion_action.category, conversion_action.primary_for_goal "
                             "FROM conversion_action")
print(f"({c}) {len(rows) if c==200 else rows} conversion actions defined")
defined = {}
if c == 200:
    for r in rows:
        a = r["conversionAction"]
        defined[a.get("name")] = a
        print(f"   {str(a.get('id')):>12}  {str(a.get('status')):<9} {str(a.get('type')):<28} "
              f"{str(a.get('category')):<18} primary={a.get('primaryForGoal')}  {a.get('name')}")

# which actually fire in the window, and at what volume
vol = collections.Counter(); val = collections.Counter(); xdev = collections.Counter()
for d1, d2 in chunks("2026-07-16", "2026-10-07", 31):
    c2, rr = stream(IN_ACCOUNT,
        "SELECT segments.conversion_action_name, metrics.all_conversions, "
        "metrics.all_conversions_value, metrics.cross_device_conversions "
        f"FROM campaign WHERE segments.date BETWEEN '{d1}' AND '{d2}'")
    if c2 != 200:
        print("volume query failed:", c2, rr); break
    for r in rr:
        n = r["segments"]["conversionActionName"]; m = r.get("metrics", {})
        vol[n] += float(m.get("allConversions", 0))
        val[n] += float(m.get("allConversionsValue", 0))
        xdev[n] += float(m.get("crossDeviceConversions", 0))

print(f"\nfiring 2026-07-16 to 2026-10-07:\n")
print(f"{'action':<34} {'all_conv':>12} {'value':>14} {'cross-dev':>11} {'xdev %':>7}")
print("-" * 82)
out = []
for n, v in vol.most_common():
    pct = xdev[n] / v * 100 if v else 0
    print(f"{n:<34} {v:>12,.1f} {val[n]:>14,.0f} {xdev[n]:>11,.1f} {pct:>6.1f}%")
    a = defined.get(n, {})
    out.append({"name": n, "id": a.get("id", ""), "type": a.get("type", ""),
                "category": a.get("category", ""), "status": a.get("status", ""),
                "primary_for_goal": a.get("primaryForGoal", ""),
                "all_conversions": round(v, 2), "all_conversions_value": round(val[n], 2),
                "cross_device": round(xdev[n], 2), "cross_device_pct": round(pct, 2)})

with open(CLEAN / "i1_conversion_actions.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
print("\nwrote i1_conversion_actions.csv")
