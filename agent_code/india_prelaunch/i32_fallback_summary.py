"""I3b summary: fallback and zero share of VBB search values, by group and
by destination, plus how much of total VBB value the fallback rows carry."""
import csv, json, glob, collections
from lib_sa360 import RAW, CLEAN, in_dest_group, is_non_brand, dest_code

rows = [json.loads(l) for p in sorted(glob.glob(str(RAW / "i3_vbb_*.jsonl")))
        for l in open(p, encoding="utf-8")]
rows = [r for r in rows if is_non_brand(r["campaign"])]
print(f"{len(rows):,d} VBB search rows, non-brand, 2026-09-10 to 2026-10-07")

mism = sum(1 for r in rows if abs(r["rev"] - r["flrev"]) > 1e-9)
print(f"  revenue against floodlight_original_revenue: {mism} disagree")
noond = sum(1 for r in rows if not r["dest"])
print(f"  rows with no parsable OND: {noond:,d} ({noond/len(rows)*100:.1f}%)")

def summarise(keyfn, label, keys=None):
    A = collections.defaultdict(lambda: collections.Counter())
    for r in rows:
        k = keyfn(r)
        a = A[k]; a["n"] += 1; a["val"] += r["rev"]
        if abs(r["rev"] - 0.50) < 1e-9:
            a["fb"] += 1; a["fbval"] += r["rev"]
        elif r["rev"] == 0:
            a["zero"] += 1
    out = []
    for k, a in A.items():
        if keys is not None and k not in keys:
            continue
        out.append({label: k, "rows": a["n"], "total_value": round(a["val"], 2),
                    "value_per_row": round(a["val"] / a["n"], 3) if a["n"] else "",
                    "fallback_0_50_rows": a["fb"],
                    "fallback_pct": round(a["fb"] / a["n"] * 100, 2) if a["n"] else "",
                    "zero_rows": a["zero"],
                    "zero_pct": round(a["zero"] / a["n"] * 100, 2) if a["n"] else "",
                    "fallback_share_of_value_pct": round(a["fbval"] / a["val"] * 100, 3)
                                                    if a["val"] else ""})
    return sorted(out, key=lambda r: -r["rows"])

g = summarise(lambda r: in_dest_group(r["campaign"]), "dest_group")
print(f"\n{'group':<28}{'rows':>9}{'val/row':>9}{'fallback':>10}{'zero':>8}{'fb share of value':>19}")
print("-" * 83)
for r in g:
    print(f"{r['dest_group']:<28}{r['rows']:>9,d}{r['value_per_row']:>9.2f}"
          f"{r['fallback_pct']:>9.1f}%{r['zero_pct']:>7.1f}%"
          f"{r['fallback_share_of_value_pct']:>18.2f}%")
with open(CLEAN / "i3_fallback_by_group.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(g[0].keys())); w.writeheader(); w.writerows(g)

# by destination, from the campaign name, which is the destination that was bid on
top = [k for k, _ in collections.Counter(
    dest_code(r["campaign"]) for r in rows).most_common(30) if k]
d = summarise(lambda r: dest_code(r["campaign"]), "dest_code", set(top))
print(f"\n{'top 30 destinations by VBB rows':<31}{'rows':>9}{'val/row':>9}"
      f"{'fallback':>10}{'zero':>8}{'fb share of value':>19}")
print("-" * 86)
for r in sorted(d, key=lambda x: -x["fallback_pct"]):
    print(f"{r['dest_code']:<31}{r['rows']:>9,d}{r['value_per_row']:>9.2f}"
          f"{r['fallback_pct']:>9.1f}%{r['zero_pct']:>7.1f}%"
          f"{r['fallback_share_of_value_pct']:>18.2f}%")
with open(CLEAN / "i3_fallback_by_destination.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(d[0].keys())); w.writeheader(); w.writerows(d)

# does the order ID destination agree with the campaign destination
agree = sum(1 for r in rows if r["dest"] and dest_code(r["campaign"])
            and r["dest"].upper() == dest_code(r["campaign"]))
have = sum(1 for r in rows if r["dest"] and dest_code(r["campaign"]))
print(f"\nsearched destination against campaign destination: "
      f"{agree:,d} of {have:,d} agree ({agree/have*100:.1f}%)")
print("\nwrote i3_fallback_by_group.csv and i3_fallback_by_destination.csv")
