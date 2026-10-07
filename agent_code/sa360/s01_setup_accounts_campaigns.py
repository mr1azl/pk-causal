"""Setup: list MCC accounts, identify the PK account, build the PK non-brand campaign list.

    cd scripts && python3 s01_setup_accounts_campaigns.py

Writes data/raw/s01_customer_clients.jsonl, data/raw/s01_campaigns.jsonl,
data/clean/s01_pk_accounts.csv, data/clean/s01_pk_nonbrand_campaigns.csv
"""
import collections, csv
from lib_sa360 import stream, MCC, RAW, CLEAN, write_jsonl, is_non_brand, dest_code, dest_group

code, rows = stream(MCC, "SELECT customer_client.id, customer_client.descriptive_name, "
                         "customer_client.currency_code, customer_client.time_zone, "
                         "customer_client.manager, customer_client.status FROM customer_client")
assert code == 200, rows
write_jsonl(RAW / "s01_customer_clients.jsonl", rows)
cc = [r["customerClient"] for r in rows]
print(f"accounts under MCC {MCC}: {len(cc)}")

pk = [c for c in cc if "PK" in (c.get("descriptiveName") or "").upper()]
CLEAN.mkdir(parents=True, exist_ok=True)
with (CLEAN / "s01_pk_accounts.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id", "name", "currency", "time_zone", "status", "manager"])
    for c in sorted(pk, key=lambda x: x.get("descriptiveName", "")):
        w.writerow([c.get("id"), c.get("descriptiveName"), c.get("currencyCode"),
                    c.get("timeZone"), c.get("status"), c.get("manager")])
        print(f"   {c.get('id'):>12s}  {c.get('descriptiveName'):<34s} "
              f"{c.get('currencyCode')}  {c.get('timeZone')}  {c.get('status')}")

PK_ID = "4851538229"       # Google-GCCLI-PK-EN, the PK non-brand account
print(f"\nPK account used: {PK_ID}")

# every campaign, including removed, so 2025 history is covered
code, crows = stream(PK_ID, "SELECT campaign.id, campaign.name, campaign.status, "
                            "campaign.start_date, campaign.end_date, "
                            "campaign.advertising_channel_type, campaign.bidding_strategy "
                            "FROM campaign")
assert code == 200, crows
write_jsonl(RAW / "s01_campaigns.jsonl", crows)
camps = [r["campaign"] for r in crows]
print(f"campaigns in account (all statuses): {len(camps):,d}")

nb = [c for c in camps if is_non_brand(c.get("name"))]
exclus = [c for c in camps if not is_non_brand(c.get("name"))]
print(f"PK non-brand (no |Brand|, no Perf_Max or pmax): {len(nb):,d}")
print(f"excluded: {len(exclus):,d}")
raisons = collections.Counter()
for c in exclus:
    low = (c.get("name") or "").lower()
    raisons["|Brand|" if "|brand|" in low else ("Perf_Max/pmax")] += 1
print("   exclusion reasons:", dict(raisons))
print("   channel types among non-brand:",
      dict(collections.Counter(c.get("advertisingChannelType") for c in nb)))
print("   status among non-brand:",
      dict(collections.Counter(c.get("status") for c in nb)))
print("   destination groups:",
      dict(collections.Counter(dest_group(c.get("name")) for c in nb).most_common()))

with (CLEAN / "s01_pk_nonbrand_campaigns.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["campaign_id", "campaign_name", "status", "channel_type",
                "dest_code", "dest_group", "start_date", "end_date", "bidding_strategy"])
    for c in sorted(nb, key=lambda x: x.get("name", "")):
        w.writerow([c.get("id"), c.get("name"), c.get("status"),
                    c.get("advertisingChannelType"), dest_code(c.get("name")),
                    dest_group(c.get("name")), c.get("startDate"), c.get("endDate"),
                    c.get("biddingStrategy", "")])
print(f"\nwrote data/clean/s01_pk_nonbrand_campaigns.csv ({len(nb):,d} rows)")
