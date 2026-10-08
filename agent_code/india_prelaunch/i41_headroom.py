"""I4b: bid headroom per campaign and per group, last 4 weeks.

The PK and SA comparison says the CPC rise on switching is largest where rank
lost impression share is already low: PK entered at 21.7 percent rank lost and
its CPC rose 6.6 times, SA entered at 53 percent and rose 2.1 times. Low rank
lost means bidding higher wins almost nothing extra, so the bidder escalates
price without buying volume and the spend lands on the budget wall instead.

Risk score, deliberately simple so it can be argued with:
    risk = (1 - rank_lost/100) * (budget_lost/100 + utilisation)
High when there is little to win on rank and little room to pay for it.
"""
import csv, json, glob, collections
from lib_sa360 import RAW, CLEAN, in_dest_group, is_non_brand

D1, D2 = "2026-09-10", "2026-10-07"
DAYS = 28
inv = list(csv.DictReader(open(CLEAN / "i0_campaign_inventory.csv", encoding="utf-8")))
names = {r["campaign_id"]: r["name"] for r in inv}
status = {r["campaign_id"]: r["status"] for r in inv}
budget_of = {r["campaign_id"]: (r["campaign_budget"] or "").rsplit("/", 1)[-1] for r in inv}
bud = {r["budget_id"]: r for r in csv.DictReader(open(CLEAN / "i4_shared_budgets.csv",
                                                      encoding="utf-8"))}

SH = [("impr_share", "searchImpressionShare"), ("top_share", "searchTopImpressionShare"),
      ("budget_lost", "searchBudgetLostImpressionShare"),
      ("rank_lost", "searchRankLostImpressionShare")]
A = collections.defaultdict(lambda: collections.Counter())
for p in sorted(glob.glob(str(RAW / "i1_traffic_2026-*.jsonl"))):
    for line in open(p, encoding="utf-8"):
        r = json.loads(line)
        if not (D1 <= r["segments"]["date"] <= D2):
            continue
        cid = r["campaign"]["id"]
        if status.get(cid) != "ENABLED" or not is_non_brand(names.get(cid, "")):
            continue
        m = r.get("metrics", {}); imp = int(m.get("impressions", 0))
        a = A[cid]
        a["cost"] += int(m.get("costMicros", 0)) / 1e6
        a["clicks"] += int(m.get("clicks", 0)); a["impr"] += imp
        for k, api in SH:
            if api in m:
                a[k] += float(m[api]) * 100 * imp; a[k + "_i"] += imp

rows = []
for cid, a in A.items():
    if a["clicks"] < 100:
        continue
    f = lambda k: a[k] / a[k + "_i"] if a[k + "_i"] else None
    rl, bl = f("rank_lost"), f("budget_lost")
    b = bud.get(budget_of.get(cid, ""), {})
    util = float(b.get("utilisation_pct") or 0) / 100
    risk = (1 - (rl or 0) / 100) * ((bl or 0) / 100 + util) if rl is not None else None
    rows.append({"campaign_id": cid, "name": names.get(cid), "dest_group": in_dest_group(names.get(cid, "")),
                 "cost_4w": round(a["cost"], 2), "clicks_4w": a["clicks"],
                 "cpc": round(a["cost"] / a["clicks"], 4),
                 "impr_share": round(f("impr_share"), 2) if f("impr_share") is not None else "",
                 "rank_lost": round(rl, 2) if rl is not None else "",
                 "budget_lost": round(bl, 2) if bl is not None else "",
                 "budget_id": budget_of.get(cid, ""),
                 "budget_daily": b.get("daily_amount", ""),
                 "budget_utilisation_pct": b.get("utilisation_pct", ""),
                 "cpc_spike_risk": round(risk, 3) if risk is not None else ""})

rows.sort(key=lambda r: -(r["cpc_spike_risk"] or 0))
with open(CLEAN / "i4_headroom_by_campaign.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

print(f"{len(rows):,d} enabled non-brand campaigns with 100+ clicks, {D1} to {D2}\n")
print("=== 20 campaigns most at risk of a CPC spike ===")
print(f"{'campaign':<44}{'cost':>8}{'CPC':>7}{'rank lost':>11}{'budget lost':>12}{'util':>7}{'risk':>7}")
print("-" * 96)
for r in rows[:20]:
    print(f"{r['name'][:42]:<44}{r['cost_4w']:>8,.0f}{r['cpc']:>7.2f}"
          f"{r['rank_lost']:>10.1f}%{r['budget_lost']:>11.1f}%"
          f"{float(r['budget_utilisation_pct'] or 0):>6.0f}%{r['cpc_spike_risk']:>7.2f}")

G = collections.defaultdict(lambda: collections.Counter())
for r in rows:
    g = G[r["dest_group"]]
    g["cost"] += r["cost_4w"]; g["n"] += 1
    g["rl"] += (r["rank_lost"] or 0) * r["cost_4w"]; g["bl"] += (r["budget_lost"] or 0) * r["cost_4w"]
    g["risk"] += (r["cpc_spike_risk"] or 0) * r["cost_4w"]
print(f"\n=== by group, cost weighted ===")
print(f"{'group':<28}{'campaigns':>11}{'cost 4w':>10}{'rank lost':>11}{'budget lost':>13}{'risk':>7}")
print("-" * 80)
grp = []
for g, a in sorted(G.items(), key=lambda kv: -kv[1]["risk"] / max(kv[1]["cost"], 1)):
    print(f"{g:<28}{a['n']:>11,d}{a['cost']:>10,.0f}{a['rl']/a['cost']:>10.1f}%"
          f"{a['bl']/a['cost']:>12.1f}%{a['risk']/a['cost']:>7.2f}")
    grp.append({"dest_group": g, "campaigns": a["n"], "cost_4w": round(a["cost"], 2),
                "rank_lost_cost_weighted": round(a["rl"] / a["cost"], 2),
                "budget_lost_cost_weighted": round(a["bl"] / a["cost"], 2),
                "cpc_spike_risk_cost_weighted": round(a["risk"] / a["cost"], 3)})
with open(CLEAN / "i4_headroom_by_group.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(grp[0].keys())); w.writeheader(); w.writerows(grp)
print("\nwrote i4_headroom_by_campaign.csv and i4_headroom_by_group.csv")
