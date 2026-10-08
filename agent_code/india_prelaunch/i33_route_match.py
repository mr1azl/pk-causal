"""I3c: does the VBB search value credited to a campaign come from a search for
that campaign's own destination?

This is the PK question that was never measurable there. The order ID carries
the origin and destination the user actually searched, so it can be compared
with the destination named in the campaign. Only the two IATA tokens are used;
the rest of the order ID was discarded at pull time.
"""
import csv, json, glob, collections
from lib_sa360 import RAW, CLEAN, in_dest_group, is_non_brand, dest_code

rows = [json.loads(l) for p in sorted(glob.glob(str(RAW / "i3_vbb_*.jsonl")))
        for l in open(p, encoding="utf-8")]
rows = [r for r in rows if is_non_brand(r["campaign"]) and r["dest"]]

IN_ORIGINS = {"del", "bom", "blr", "maa", "hyd", "ccu", "amd", "cok", "trv", "goi",
              "atq", "nag", "ccj", "pnq", "lko", "ixc", "jai", "vtz", "ixe", "trz",
              "ixm", "bbi", "gau", "vns", "sxr", "ixb", "rpr", "idr", "bho", "pat"}

G = collections.defaultdict(lambda: collections.Counter())
pair = collections.Counter()
for r in rows:
    cd = dest_code(r["campaign"])
    if not cd:
        continue
    g = in_dest_group(r["campaign"])
    a = G[g]; a["n"] += 1; a["val"] += r["rev"]
    if r["dest"].upper() == cd:
        a["match"] += 1; a["match_val"] += r["rev"]
    else:
        a["miss"] += 1; a["miss_val"] += r["rev"]
        pair[(cd, r["dest"].upper())] += 1
    # reverse direction: the searched destination is an Indian city
    if r["dest"] in IN_ORIGINS:
        a["reverse"] += 1; a["reverse_val"] += r["rev"]

out = []
print("=== VBB search value: does it come from the campaign's own destination ===")
print(f"{'group':<28}{'rows':>9}{'on route':>10}{'off route':>11}"
      f"{'value on route':>16}{'reverse dir':>13}")
print("-" * 88)
for g, a in sorted(G.items(), key=lambda kv: -kv[1]["n"]):
    print(f"{g:<28}{a['n']:>9,d}{a['match']/a['n']*100:>9.1f}%{a['miss']/a['n']*100:>10.1f}%"
          f"{a['match_val']/a['val']*100:>15.1f}%{a['reverse']/a['n']*100:>12.1f}%")
    out.append({"dest_group": g, "rows": a["n"],
                "on_route_rows": a["match"], "on_route_pct": round(a["match"]/a["n"]*100, 2),
                "off_route_rows": a["miss"], "off_route_pct": round(a["miss"]/a["n"]*100, 2),
                "value_total": round(a["val"], 2),
                "value_on_route": round(a["match_val"], 2),
                "value_on_route_pct": round(a["match_val"]/a["val"]*100, 2) if a["val"] else "",
                "reverse_direction_rows": a["reverse"],
                "reverse_direction_pct": round(a["reverse"]/a["n"]*100, 2),
                "reverse_direction_value": round(a["reverse_val"], 2)})

with open(CLEAN / "i3_route_match_by_group.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

print(f"\ntop 25 campaign destination -> searched destination mismatches")
print(f"{'campaign dest':<15}{'searched':<12}{'rows':>8}")
print("-" * 35)
for (cd, sd), n in pair.most_common(25):
    print(f"{cd:<15}{sd:<12}{n:>8,d}")
with open(CLEAN / "i3_route_mismatch_pairs.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["campaign_dest", "searched_dest", "rows"])
    for (cd, sd), n in pair.most_common(400):
        w.writerow([cd, sd, n])
print("\nwrote i3_route_match_by_group.csv and i3_route_mismatch_pairs.csv")
