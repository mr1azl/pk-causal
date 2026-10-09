"""I4c: the single risk score in i41 was dominated by budget utilisation, which
is a property of the shared budget rather than of the campaign, so every campaign
on the 208 percent budget sorted to the top and rank lost stopped mattering.

Two separate rankings instead, because they are two different failure modes:
  escalation risk  low rank lost means bidding higher wins almost nothing, so a
                   value bidder with no ceiling raises price without buying volume
  budget wall risk high budget lost and a budget already fully used means the
                   extra price immediately costs impression share
Ranked by spend at risk, not by campaign count, so small campaigns do not crowd out
the ones that matter.
"""
import csv, collections
from lib_sa360 import CLEAN

rows = list(csv.DictReader(open(CLEAN / "i4_headroom_by_campaign.csv", encoding="utf-8")))
for r in rows:
    for k in ("cost_4w", "cpc", "rank_lost", "budget_lost", "budget_utilisation_pct", "impr_share"):
        r[k] = float(r[k]) if r[k] not in ("", None) else None

esc = [r for r in rows if r["rank_lost"] is not None and r["cost_4w"] >= 100]
esc.sort(key=lambda r: (r["rank_lost"], -r["cost_4w"]))
print("=== escalation risk: lowest rank lost, 100 USD or more in 4 weeks ===")
print("PK entered its switch at 21.7% rank lost and CPC rose 6.6x; SA at 53% and rose 2.1x\n")
print(f"{'campaign':<44}{'cost 4w':>9}{'CPC':>7}{'rank lost':>11}{'impr share':>12}")
print("-" * 83)
for r in esc[:18]:
    print(f"{r['name'][:42]:<44}{r['cost_4w']:>9,.0f}{r['cpc']:>7.2f}"
          f"{r['rank_lost']:>10.1f}%{r['impr_share']:>11.1f}%")
below_pk = [r for r in esc if r["rank_lost"] < 21.7]
print(f"\n{len(below_pk)} campaigns sit below PK's 21.7 percent starting point, "
      f"{sum(r['cost_4w'] for r in below_pk):,.0f} USD over 4 weeks, "
      f"{sum(r['cost_4w'] for r in below_pk)/sum(r['cost_4w'] for r in esc)*100:.0f}% of the spend here")

wall = [r for r in rows if r["budget_lost"] is not None and r["cost_4w"] >= 100]
for r in wall:
    r["wall"] = r["budget_lost"] / 100 + (r["budget_utilisation_pct"] or 0) / 100
wall.sort(key=lambda r: -r["wall"])
print("\n=== budget wall risk: budget already lost plus budget already used ===")
print(f"{'campaign':<44}{'cost 4w':>9}{'budget lost':>13}{'util':>7}{'score':>7}")
print("-" * 80)
for r in wall[:15]:
    print(f"{r['name'][:42]:<44}{r['cost_4w']:>9,.0f}{r['budget_lost']:>12.1f}%"
          f"{(r['budget_utilisation_pct'] or 0):>6.0f}%{r['wall']:>7.2f}")

with open(CLEAN / "i4_risk_rankings.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["ranking", "rank", "campaign_id", "name", "dest_group", "cost_4w", "cpc",
                "rank_lost", "budget_lost", "budget_utilisation_pct", "score"])
    for i, r in enumerate(esc[:100], 1):
        w.writerow(["escalation", i, r["campaign_id"], r["name"], r["dest_group"],
                    r["cost_4w"], r["cpc"], r["rank_lost"], r["budget_lost"],
                    r["budget_utilisation_pct"], r["rank_lost"]])
    for i, r in enumerate(wall[:100], 1):
        w.writerow(["budget_wall", i, r["campaign_id"], r["name"], r["dest_group"],
                    r["cost_4w"], r["cpc"], r["rank_lost"], r["budget_lost"],
                    r["budget_utilisation_pct"], round(r["wall"], 3)])
print("\nwrote i4_risk_rankings.csv")

G = collections.defaultdict(lambda: collections.Counter())
for r in esc:
    g = G[r["dest_group"]]
    g["cost"] += r["cost_4w"]
    if r["rank_lost"] < 21.7:
        g["at_risk"] += r["cost_4w"]
print("\n=== spend sitting below PK's rank lost starting point, by group ===")
print(f"{'group':<28}{'cost 4w':>10}{'below 21.7%':>13}{'share':>8}")
print("-" * 60)
for g, a in sorted(G.items(), key=lambda kv: -kv[1]["at_risk"]):
    print(f"{g:<28}{a['cost']:>10,.0f}{a['at_risk']:>13,.0f}{a['at_risk']/a['cost']*100:>7.0f}%")
