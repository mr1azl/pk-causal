"""I0 step 4: spend share per India destination group, and a hard check that
nothing material falls into 'unclassified'. Writes i0_group_spend.csv."""
import csv, collections
from lib_sa360 import CLEAN, in_dest_group, in_dest_region, dest_code

rows = list(csv.DictReader(open(CLEAN / "i0_campaign_inventory.csv", encoding="utf-8")))
tot = sum(float(r["cost_12w"] or 0) for r in rows)

g = collections.Counter(); reg = collections.Counter()
gc = collections.Counter(); unk = collections.Counter()
live = collections.Counter()
for r in rows:
    cost = float(r["cost_12w"] or 0)
    gr = in_dest_group(r["name"]); rg = in_dest_region(r["name"])
    g[gr] += cost; reg[rg] += cost; gc[gr] += 1
    if r["status"] == "ENABLED":
        live[gr] += 1
    if rg == "unclassified":
        unk[dest_code(r["name"])] += cost

print(f"non-brand spend 12 weeks: {tot:,.0f} USD\n")
print(f"{'group':<30} {'cost':>11} {'share':>7} {'campaigns':>10} {'enabled':>8}")
print("-" * 70)
for k, v in g.most_common():
    print(f"{k:<30} {v:>11,.0f} {v/tot*100:>6.2f}% {gc[k]:>10,d} {live[k]:>8,d}")

print(f"\n{'region (finer)':<30} {'cost':>11} {'share':>7}")
print("-" * 50)
for k, v in reg.most_common():
    print(f"{k:<30} {v:>11,.0f} {v/tot*100:>6.2f}%")

print(f"\nunclassified codes: {len(unk)}, {sum(unk.values()):,.0f} USD "
      f"({sum(unk.values())/tot*100:.3f}% of spend)")
for c, v in unk.most_common(25):
    print(f"   {c:<6} {v:>9,.0f}")

with open(CLEAN / "i0_group_spend.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["dest_group", "cost_12w", "share_pct", "campaigns", "enabled"])
    for k, v in g.most_common():
        w.writerow([k, round(v, 2), round(v / tot * 100, 3), gc[k], live[k]])
with open(CLEAN / "i0_region_spend.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["dest_region", "cost_12w", "share_pct"])
    for k, v in reg.most_common():
        w.writerow([k, round(v, 2), round(v / tot * 100, 3)])
print("\nwrote i0_group_spend.csv and i0_region_spend.csv")
