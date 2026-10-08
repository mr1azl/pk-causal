"""I5c: match type mix, broad match share of clicks, and the reverse direction
negative check.

Capability note found while running: `shared_set`, `shared_criterion` and
`campaign_shared_set` do not exist in this API, zero fields each, so shared
negative lists cannot be read here. Anything below is campaign and ad group
level only, and a shared list could in principle cover some of the gaps found.
"""
import csv, json, collections, re
from lib_sa360 import RAW, CLEAN, in_dest_group, is_non_brand, dest_code

inv = list(csv.DictReader(open(CLEAN / "i0_campaign_inventory.csv", encoding="utf-8")))
names = {r["campaign_id"]: r["name"] for r in inv}
cost4 = {}
for r in csv.DictReader(open(CLEAN / "i4_headroom_by_campaign.csv", encoding="utf-8")):
    cost4[r["campaign_id"]] = float(r["cost_4w"])

kw = [json.loads(l) for l in open(RAW / "i5_keywords.jsonl", encoding="utf-8")]
kw = [k for k in kw if is_non_brand(k["campaign"].get("name"))]
print(f"{len(kw):,d} enabled keywords in enabled non-brand campaigns")

mt = collections.Counter(k["adGroupCriterion"]["keyword"].get("matchType") for k in kw)
print("  match types:", dict(mt.most_common()))
st = collections.Counter(k["adGroupCriterion"].get("status") for k in kw)
print("  criterion status:", dict(st.most_common()))

# match type by destination group, weighted by the campaign's 4 week spend
G = collections.defaultdict(lambda: collections.Counter())
for k in kw:
    nm = k["campaign"].get("name"); cid = k["campaign"]["id"]
    g = in_dest_group(nm); m = k["adGroupCriterion"]["keyword"].get("matchType")
    G[g][m] += 1
    G[g]["_n"] += 1
print(f"\n{'group':<28}{'keywords':>10}  match type mix")
print("-" * 78)
rows = []
for g, a in sorted(G.items(), key=lambda kv: -kv[1]["_n"]):
    mix = "; ".join(f"{m} {a[m]/a['_n']*100:.0f}%"
                    for m in sorted(a, key=lambda x: -a[x]) if m != "_n")
    print(f"{g:<28}{a['_n']:>10,d}  {mix}")
    rows.append({"dest_group": g, "keywords": a["_n"],
                 **{f"pct_{m}": round(a[m] / a["_n"] * 100, 2) for m in a if m != "_n"}})
with open(CLEAN / "i5_match_type_by_group.csv", "w", newline="", encoding="utf-8") as fh:
    cols = sorted({c for r in rows for c in r})
    w = csv.DictWriter(fh, fieldnames=["dest_group", "keywords"] +
                       [c for c in cols if c.startswith("pct_")])
    w.writeheader()
    for r in rows:
        w.writerow(r)

# campaign name match-type token, which is what the structure actually uses
tok = collections.Counter()
tok_cost = collections.Counter()
for r in inv:
    if r["status"] != "ENABLED":
        continue
    p = (r["name"] or "").split("|")
    t = p[7] if len(p) > 7 else "(none)"
    tok[t] += 1; tok_cost[t] += float(r["cost_12w"] or 0)
print(f"\ncampaign name match token, enabled campaigns:")
for t, n in tok.most_common():
    print(f"   {t:<8} {n:>5,d} campaigns   {tok_cost[t]:>11,.0f} USD 12w")

# negatives
neg = [json.loads(l) for l in open(RAW / "i5_neg_campaign.jsonl", encoding="utf-8")]
neg = [n for n in neg if is_non_brand(n["campaign"].get("name"))]
print(f"\n{len(neg):,d} campaign level negatives on enabled non-brand campaigns, "
      f"0 ad group level negatives, shared lists not readable")
bycamp = collections.defaultdict(list)
for n in neg:
    t = (n["campaignCriterion"].get("keyword") or {}).get("text", "")
    bycamp[n["campaign"]["id"]].append(t.lower())
print(f"  they sit on {len(bycamp):,d} distinct campaigns")
kinds = collections.Counter()
for ts in bycamp.values():
    for t in ts:
        if re.search(r"\bqr\s?\d", t) or re.search(r"\bflight\s+qr", t):
            kinds["flight number"] += 1
        elif t.startswith("to ") or " to " in t:
            kinds["directional phrase"] += 1
        else:
            kinds["other"] += 1
print("  what they are:", dict(kinds.most_common()))

# reverse direction check
IN_CITIES = ["india", "delhi", "mumbai", "bangalore", "bengaluru", "chennai", "hyderabad",
             "kolkata", "ahmedabad", "kochi", "cochin", "trivandrum", "thiruvananthapuram",
             "goa", "amritsar", "nagpur", "calicut", "kozhikode", "pune", "lucknow",
             "chandigarh", "jaipur", "new delhi", "bombay", "madras"]
REV = re.compile("|".join(r"to\s+" + re.escape(c) for c in IN_CITIES))

out = []
for r in inv:
    if r["status"] != "ENABLED" or not dest_code(r["name"]):
        continue
    if in_dest_group(r["name"]) == "India (reverse direction)":
        continue
    ts = bycamp.get(r["campaign_id"], [])
    has = any(REV.search(t) for t in ts)
    out.append({"campaign_id": r["campaign_id"], "name": r["name"],
                "dest_group": in_dest_group(r["name"]), "dest_code": dest_code(r["name"]),
                "cost_12w": float(r["cost_12w"] or 0), "cost_4w": cost4.get(r["campaign_id"], 0),
                "negatives_on_campaign": len(ts),
                "has_reverse_direction_negative": "yes" if has else "no"})

miss = [r for r in out if r["has_reverse_direction_negative"] == "no"]
print(f"\n=== reverse direction negatives ===")
print(f"{len(out):,d} enabled destination campaigns outside India")
print(f"{len(miss):,d} have no reverse direction negative "
      f"({len(miss)/len(out)*100:.1f}%), carrying {sum(r['cost_12w'] for r in miss):,.0f} USD "
      f"of the {sum(r['cost_12w'] for r in out):,.0f} USD measured here")
nonone = [r for r in out if r["negatives_on_campaign"] == 0]
print(f"{len(nonone):,d} have no campaign level negative of any kind")

miss.sort(key=lambda r: -r["cost_12w"])
print(f"\ntop 20 by spend with no reverse direction negative:")
print(f"{'campaign':<46}{'group':<22}{'cost 12w':>10}{'negs':>6}")
print("-" * 86)
for r in miss[:20]:
    print(f"{r['name'][:44]:<46}{r['dest_group'][:20]:<22}{r['cost_12w']:>10,.0f}"
          f"{r['negatives_on_campaign']:>6,d}")

with open(CLEAN / "i5_reverse_direction_check.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader()
    w.writerows(sorted(out, key=lambda r: -r["cost_12w"]))
print("\nwrote i5_match_type_by_group.csv and i5_reverse_direction_check.csv")
