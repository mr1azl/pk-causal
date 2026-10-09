"""I7a: holdout design.

Design constraint found first, because it changes what a valid holdout is:
every enabled campaign sits on one of 10 shared budgets, and budgets do not line
up with portfolios or with destination groups. If treated campaigns bid higher on
a budget shared with holdout campaigns, the holdout is starved by the treatment
rather than left alone, and the comparison measures budget contention instead of
the strategy. So the holdout has to be budget separated, not only portfolio
separated, and this script reports the crosstab before proposing anything.

Selection: inside each destination group, pick campaigns nearest the group's
spend weighted mean on CPC and booking rate until about 20 percent of the
group's spend is held out, then report how closely the two arms match.
"""
import csv, json, glob, collections, statistics
from lib_sa360 import RAW, CLEAN, in_dest_group, is_non_brand

D1, D2 = "2026-08-13", "2026-10-07"      # last 8 weeks
inv = {r["campaign_id"]: r for r in csv.DictReader(
    open(CLEAN / "i0_campaign_inventory.csv", encoding="utf-8"))}
names = {k: v["name"] for k, v in inv.items()}

A = collections.defaultdict(lambda: collections.Counter())
for p in sorted(glob.glob(str(RAW / "i1_traffic_2026-*.jsonl"))):
    for line in open(p, encoding="utf-8"):
        r = json.loads(line)
        if not (D1 <= r["segments"]["date"] <= D2):
            continue
        cid = r["campaign"]["id"]
        if cid not in inv or inv[cid]["status"] != "ENABLED":
            continue
        m = r.get("metrics", {})
        A[cid]["cost"] += int(m.get("costMicros", 0)) / 1e6
        A[cid]["clicks"] += int(m.get("clicks", 0))
for p in sorted(glob.glob(str(RAW / "i1_conv_2026-*.jsonl"))):
    for line in open(p, encoding="utf-8"):
        r = json.loads(line)
        if not (D1 <= r["segments"]["date"] <= D2):
            continue
        if r["segments"]["conversionActionName"] != "QR_Booking":
            continue
        cid = r["campaign"]["id"]
        if cid in A:
            A[cid]["bk"] += float(r.get("metrics", {}).get("allConversions", 0))

# budget against portfolio crosstab
cross = collections.defaultdict(lambda: collections.Counter())
for cid, r in inv.items():
    if r["status"] != "ENABLED":
        continue
    b = (r["campaign_budget"] or "").rsplit("/", 1)[-1]
    pf = (r["bidding_strategy"] or "").rsplit("/", 1)[-1]
    cross[b][pf] += 1
print("=== budgets against portfolios, enabled campaigns ===")
print(f"{'budget':<16}{'portfolios on it':>18}  campaign split")
print("-" * 70)
for b, a in sorted(cross.items(), key=lambda kv: -sum(kv[1].values())):
    print(f"{b:<16}{len(a):>18}  " + ", ".join(f"{p[-4:]}:{n}" for p, n in a.most_common(5)))
mixed = sum(1 for a in cross.values() if len(a) > 1)
print(f"\n{mixed} of {len(cross)} budgets carry campaigns from more than one portfolio.")

gcross = collections.defaultdict(set)
for cid, r in inv.items():
    if r["status"] == "ENABLED":
        gcross[(r["campaign_budget"] or "").rsplit("/", 1)[-1]].add(in_dest_group(r["name"]))
mixedg = sum(1 for s in gcross.values() if len(s) > 1)
print(f"{mixedg} of {len(gcross)} budgets carry campaigns from more than one destination group.")

cand = []
for cid, a in A.items():
    if a["clicks"] < 200 or a["cost"] < 50:
        continue
    cand.append({"campaign_id": cid, "name": names[cid],
                 "dest_group": in_dest_group(names[cid]),
                 "budget_id": (inv[cid]["campaign_budget"] or "").rsplit("/", 1)[-1],
                 "portfolio_id": (inv[cid]["bidding_strategy"] or "").rsplit("/", 1)[-1],
                 "cost_8w": round(a["cost"], 2), "clicks_8w": int(a["clicks"]),
                 "cpc": round(a["cost"] / a["clicks"], 4),
                 "bookings_8w": round(a["bk"], 1),
                 "bk_per_1k_clicks": round(a["bk"] / a["clicks"] * 1000, 3)})

G = collections.defaultdict(list)
for c in cand:
    G[c["dest_group"]].append(c)

hold = []
print(f"\n=== proposed holdout, about 20 percent of spend per group ===")
print(f"{'group':<26}{'campaigns':>10}{'held out':>10}{'spend held':>12}{'share':>7}")
print("-" * 65)
for g, cs in sorted(G.items(), key=lambda kv: -sum(c["cost_8w"] for c in kv[1])):
    tot = sum(c["cost_8w"] for c in cs)
    if tot <= 0 or len(cs) < 4:
        continue
    mcpc = sum(c["cpc"] * c["cost_8w"] for c in cs) / tot
    mbk = sum(c["bk_per_1k_clicks"] * c["cost_8w"] for c in cs) / tot
    scpc = statistics.pstdev([c["cpc"] for c in cs]) or 1
    sbk = statistics.pstdev([c["bk_per_1k_clicks"] for c in cs]) or 1
    for c in cs:
        c["dist"] = (((c["cpc"] - mcpc) / scpc) ** 2 +
                     ((c["bk_per_1k_clicks"] - mbk) / sbk) ** 2) ** 0.5
    picked, acc = [], 0.0
    for c in sorted(cs, key=lambda x: x["dist"]):
        if acc >= 0.20 * tot:
            break
        picked.append(c); acc += c["cost_8w"]
    for c in picked:
        c["arm"] = "holdout"
    for c in cs:
        c.setdefault("arm", "treated")
    hold += cs
    print(f"{g:<26}{len(cs):>10,d}{len(picked):>10,d}{acc:>12,.0f}{acc/tot*100:>6.0f}%")

print(f"\n=== match quality, holdout against treated, last 8 weeks ===")
print(f"{'group':<26}{'CPC hold':>10}{'CPC trt':>9}{'bk/1k hold':>12}{'bk/1k trt':>11}{'budgets shared':>16}")
print("-" * 86)
qual = []
for g in sorted({c["dest_group"] for c in hold}):
    h = [c for c in hold if c["dest_group"] == g and c["arm"] == "holdout"]
    t = [c for c in hold if c["dest_group"] == g and c["arm"] == "treated"]
    if not h or not t:
        continue
    def wm(rows, key):
        s = sum(r["cost_8w"] for r in rows)
        return sum(r[key] * r["cost_8w"] for r in rows) / s if s else 0
    shared = len({c["budget_id"] for c in h} & {c["budget_id"] for c in t})
    print(f"{g:<26}{wm(h,'cpc'):>10.3f}{wm(t,'cpc'):>9.3f}"
          f"{wm(h,'bk_per_1k_clicks'):>12.2f}{wm(t,'bk_per_1k_clicks'):>11.2f}{shared:>16,d}")
    qual.append({"dest_group": g, "holdout_campaigns": len(h), "treated_campaigns": len(t),
                 "holdout_spend_8w": round(sum(c["cost_8w"] for c in h), 2),
                 "treated_spend_8w": round(sum(c["cost_8w"] for c in t), 2),
                 "holdout_cpc": round(wm(h, "cpc"), 4), "treated_cpc": round(wm(t, "cpc"), 4),
                 "holdout_bk_per_1k": round(wm(h, "bk_per_1k_clicks"), 3),
                 "treated_bk_per_1k": round(wm(t, "bk_per_1k_clicks"), 3),
                 "budgets_shared_between_arms": shared})

with open(CLEAN / "i7_holdout_campaigns.csv", "w", newline="", encoding="utf-8") as fh:
    cols = ["campaign_id", "name", "dest_group", "arm", "budget_id", "portfolio_id",
            "cost_8w", "clicks_8w", "cpc", "bookings_8w", "bk_per_1k_clicks"]
    w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
    w.writeheader(); w.writerows(sorted(hold, key=lambda c: (c["dest_group"], c["arm"])))
with open(CLEAN / "i7_holdout_match_quality.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(qual[0].keys())); w.writeheader(); w.writerows(qual)
print("\nwrote i7_holdout_campaigns.csv and i7_holdout_match_quality.csv")
