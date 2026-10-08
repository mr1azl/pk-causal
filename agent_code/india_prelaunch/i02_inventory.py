"""I0 step 3: campaign inventory for the India non-brand account.

Counts by status, naming convention (pipe vs legacy), spend share on each form
over the last 12 weeks, and destination parse coverage. Also dumps the raw
destination code distribution by spend so the India destination groups can be
defined from what is actually in the account rather than guessed.
"""
import csv, collections, json, sys
from lib_sa360 import stream, chunks, RAW, CLEAN, dest_code, is_non_brand

ACC = "4034062923"        # Google-GCCLI-IN-EN-2, chosen in i01 on spend
D1, D2 = "2026-07-16", "2026-10-07"

c, rows = stream(ACC, "SELECT campaign.id, campaign.name, campaign.status, "
                      "campaign.advertising_channel_type, campaign.bidding_strategy, "
                      "campaign.bidding_strategy_type, campaign.campaign_budget, "
                      "campaign.last_modified_time FROM campaign")
if c != 200:
    sys.exit(f"campaign failed: {c} {rows}")
camps = {r["campaign"]["id"]: r["campaign"] for r in rows}
print(f"{len(camps):,d} campaigns in the account")

nb = {i: x for i, x in camps.items() if is_non_brand(x.get("name"))}
print(f"{len(nb):,d} non-brand ({len(camps)-len(nb):,d} brand or pmax excluded)")
print("  status:", dict(collections.Counter(x.get("status") for x in nb.values()).most_common()))
print("  channel:", dict(collections.Counter(x.get("advertisingChannelType") for x in nb.values()).most_common()))

# spend per campaign over the window
spend = collections.Counter(); clicks = collections.Counter()
for d1, d2 in chunks(D1, D2, 31):
    c, rr = stream(ACC, "SELECT campaign.id, metrics.cost_micros, metrics.clicks "
                        f"FROM campaign WHERE segments.date BETWEEN '{d1}' AND '{d2}'")
    if c != 200:
        sys.exit(f"metrics failed: {c} {rr}")
    for r in rr:
        m = r.get("metrics", {})
        spend[r["campaign"]["id"]] += int(m.get("costMicros", 0)) / 1e6
        clicks[r["campaign"]["id"]] += int(m.get("clicks", 0))

def naming(n):
    return "pipe" if "|" in (n or "") else ("legacy" if (n or "").startswith("_") else "other")

tot = sum(spend[i] for i in nb)
by_form = collections.Counter()
for i, x in nb.items():
    by_form[naming(x.get("name"))] += spend[i]
print(f"\nnon-brand spend {D1} to {D2}: {tot:,.0f} USD")
for f, s in by_form.most_common():
    print(f"  {f:<8} {s:>12,.0f}  {s/tot*100:>5.1f}%")

# destination parse coverage
parsed = sum(s for i, s in ((i, spend[i]) for i in nb) if dest_code(nb[i].get("name")))
print(f"\ndestination parsed on {parsed/tot*100:.1f}% of non-brand spend, "
      f"no code on {(tot-parsed)/tot*100:.1f}%")

by_code = collections.Counter()
for i, x in nb.items():
    by_code[dest_code(x.get("name")) or "(none)"] += spend[i]
print(f"\n{len(by_code)} distinct destination codes. Top 45 by spend:")
for code_, s in by_code.most_common(45):
    print(f"  {code_:<8} {s:>11,.0f}  {s/tot*100:>5.2f}%")

with open(CLEAN / "i0_campaign_inventory.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["campaign_id", "name", "status", "channel", "naming", "dest_code",
                "bidding_strategy_type", "bidding_strategy", "campaign_budget",
                "last_modified_time", "cost_12w", "clicks_12w"])
    for i, x in sorted(nb.items(), key=lambda kv: -spend[kv[0]]):
        w.writerow([i, x.get("name"), x.get("status"), x.get("advertisingChannelType"),
                    naming(x.get("name")), dest_code(x.get("name")),
                    x.get("biddingStrategyType"), x.get("biddingStrategy"),
                    x.get("campaignBudget"), x.get("lastModifiedTime"),
                    round(spend[i], 2), clicks[i]])

with open(CLEAN / "i0_dest_code_spend.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["dest_code", "cost_12w", "share_pct"])
    for code_, s in by_code.most_common():
        w.writerow([code_, round(s, 2), round(s / tot * 100, 3)])
print("\nwrote i0_campaign_inventory.csv and i0_dest_code_spend.csv")
