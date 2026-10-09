"""I4a: shared budgets. Which campaigns share which budget, the amount, and
what share of it each one used over the last 4 weeks."""
import csv, json, collections, glob, sys
from lib_sa360 import stream, CLEAN, RAW, IN_ACCOUNT, in_dest_group, is_non_brand

D1, D2 = "2026-09-10", "2026-10-07"

# campaign_budget exposes only 4 fields in this API: amount_micros, delivery_method,
# period and resource_name. There is no id, name or status, so the budget is keyed
# by the id at the end of its resource name and has no human readable label.
c, rows = stream(IN_ACCOUNT, "SELECT campaign_budget.resource_name, "
                             "campaign_budget.amount_micros, campaign_budget.delivery_method, "
                             "campaign_budget.period FROM campaign_budget")
if c != 200:
    sys.exit(f"campaign_budget failed: {c} {rows}")
B = {}
for r in rows:
    b = r["campaignBudget"]
    bid = (b.get("resourceName") or "").rsplit("/", 1)[-1]
    B[bid] = {"name": bid, "amount": int(b.get("amountMicros", 0)) / 1e6,
              "delivery": b.get("deliveryMethod"), "status": None,
              "period": b.get("period")}
print(f"{len(B):,d} budgets defined")

inv = list(csv.DictReader(open(CLEAN / "i0_campaign_inventory.csv", encoding="utf-8")))
names = {r["campaign_id"]: r["name"] for r in inv}
budget_of = {r["campaign_id"]: (r["campaign_budget"] or "").rsplit("/", 1)[-1] for r in inv}
status_of = {r["campaign_id"]: r["status"] for r in inv}

spend = collections.Counter()
for p in sorted(glob.glob(str(RAW / "i1_traffic_2026-*.jsonl"))):
    for line in open(p, encoding="utf-8"):
        r = json.loads(line)
        if not (D1 <= r["segments"]["date"] <= D2):
            continue
        spend[r["campaign"]["id"]] += int(r.get("metrics", {}).get("costMicros", 0)) / 1e6

days = 28
sh = collections.defaultdict(list)
for cid, bid in budget_of.items():
    if bid and status_of.get(cid) == "ENABLED":
        sh[bid].append(cid)

out = []
for bid, cids in sh.items():
    b = B.get(bid, {})
    amt = b.get("amount", 0)
    tot = sum(spend[c] for c in cids)
    groups = collections.Counter(in_dest_group(names.get(c, "")) for c in cids)
    out.append({"budget_id": bid, "budget_name": b.get("name"),
                "daily_amount": round(amt, 2), "period": b.get("period"),
                "delivery": b.get("delivery"), "status": b.get("status"),
                "enabled_campaigns": len(cids),
                "spend_4w": round(tot, 2),
                "spend_per_day": round(tot / days, 2),
                "utilisation_pct": round(tot / days / amt * 100, 1) if amt else "",
                "dest_groups": "; ".join(f"{g}:{n}" for g, n in groups.most_common())})

out.sort(key=lambda r: -r["spend_4w"])
with open(CLEAN / "i4_shared_budgets.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

print(f"\n{len(out)} budgets carry enabled non-brand campaigns, {D1} to {D2}\n")
print(f"{'budget':<40}{'daily':>9}{'camps':>7}{'spend/day':>11}{'util':>8}  groups")
print("-" * 110)
for r in out[:20]:
    util = (format(r["utilisation_pct"], ".0f") + "%") if r["utilisation_pct"] != "" else "n/a"
    print(f"{str(r['budget_name'])[:38]:<40}{r['daily_amount']:>9,.0f}{r['enabled_campaigns']:>7,d}"
          f"{r['spend_per_day']:>11,.1f}"
          f"{util:>8}"
          f"  {r['dest_groups'][:40]}")
tot_amt = sum(r["daily_amount"] for r in out)
tot_sp = sum(r["spend_per_day"] for r in out)
print(f"\ntotal daily budget {tot_amt:,.0f}, actual spend per day {tot_sp:,.0f}, "
      f"utilisation {tot_sp/tot_amt*100:.1f}%")
shared = [r for r in out if r["enabled_campaigns"] > 1]
print(f"{len(shared)} of {len(out)} budgets are shared by more than one enabled campaign, "
      f"covering {sum(r['enabled_campaigns'] for r in shared):,d} campaigns")
print("\nwrote i4_shared_budgets.csv")
