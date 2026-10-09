"""R1: what the Google Ads API gives PK that SA360 did not.

Tests each resource the SA360 investigation could not read. Zero fields back
means the resource does not exist; a field list means it does.
"""
import csv, json
from lib_gads import fields, search, ACCOUNTS, CLEAN

RESOURCES = ["change_event", "change_status", "search_term_view", "shared_set",
             "shared_criterion", "campaign_shared_set", "campaign_budget",
             "bidding_strategy", "keyword_view", "ad_group_criterion",
             "campaign_criterion", "campaign", "customer", "ad_group_ad",
             "landing_page_view", "geographic_view", "user_location_view",
             "click_view", "campaign_audience_view", "ad_group_audience_view",
             "detail_placement_view", "search_term_insight", "campaign_search_term_insight"]

print(f"{'resource':<32}{'fields':>8}   verdict")
print("-" * 70)
out = []
for r in RESOURCES:
    rows, err = fields(f"name LIKE '{r}.%'")
    n = len(rows) if rows is not None else -1
    verdict = "ERROR " + str(err)[:40] if n < 0 else ("does NOT exist" if n == 0 else "exists")
    print(f"{r:<32}{n:>8}   {verdict}")
    out.append({"resource": r, "field_count": n, "exists": "yes" if n > 0 else "no"})

with open(CLEAN / "r1_resource_availability.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

print("\n=== change_event fields, the resource SA360 lacks entirely ===")
rows, err = fields("name LIKE 'change_event.%'")
if rows:
    for x in sorted(rows, key=lambda z: z["name"]):
        print(f"   {x['name']:<46} {x.get('dataType','')}")

print("\n=== does PK actually return change_event rows ===")
r, err = search(ACCOUNTS["pk_nonbrand"],
                "SELECT change_event.change_date_time, change_event.change_resource_type, "
                "change_event.resource_change_operation, change_event.user_email "
                "FROM change_event "
                "WHERE change_event.change_date_time >= '2026-08-15' "
                "AND change_event.change_date_time <= '2026-10-07' "
                "LIMIT 10")
print("   ", err or f"{len(r)} rows")
if r:
    for x in r[:5]:
        c = x["changeEvent"]
        print(f"      {c.get('changeDateTime')}  {c.get('changeResourceType'):<22} "
              f"{c.get('resourceChangeOperation')}")
print("\nwrote r1_resource_availability.csv")
