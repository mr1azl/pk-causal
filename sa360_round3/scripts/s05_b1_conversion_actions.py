"""B1: full configuration of every PK conversion action whose name contains "Booking",
plus QR_FlightSearch_VBB.

    cd scripts && python3 s05_b1_conversion_actions.py

Writes data/raw/b1_conversion_actions.jsonl, data/clean/b1_booking_actions.csv
"""
import csv, json
from lib_sa360 import stream, fields, RAW, CLEAN, write_jsonl

PK = "4851538229"
code, cat = fields("name LIKE 'conversion_action.%'")
assert code == 200, cat
champs = sorted(f["name"] for f in cat if f.get("selectable"))
print(f"{len(champs)} selectable conversion_action fields, all requested")

code, rows = stream(PK, "SELECT " + ", ".join(champs) + " FROM conversion_action")
assert code == 200, rows
write_jsonl(RAW / "b1_conversion_actions.jsonl", rows)
acts = [r["conversionAction"] for r in rows]
print(f"{len(acts)} conversion actions in the account")

cible = [a for a in acts
         if "booking" in (a.get("name") or "").lower()
         or a.get("name") == "QR_FlightSearch_VBB"]
print(f"{len(cible)} match 'Booking' or QR_FlightSearch_VBB\n")

def g(a, *p):
    v = a
    for k in p:
        if not isinstance(v, dict): return None
        v = v.get(k)
    return v

CLEAN.mkdir(parents=True, exist_ok=True)
with (CLEAN / "b1_booking_actions.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id", "name", "status", "type", "category", "include_in_conversions",
                "include_in_client_account_conversions", "primary_for_goal",
                "attribution_model", "data_driven_status", "click_lookback_days",
                "floodlight_activity_id", "floodlight_activity_tag",
                "floodlight_activity_group_tag", "default_value",
                "always_use_default_value", "default_currency", "owner_customer",
                "creation_time", "app_id"])
    for a in sorted(cible, key=lambda x: (x.get("name", ""), x.get("id", ""))):
        row = [a.get("id"), a.get("name"), a.get("status"), a.get("type"), a.get("category"),
               a.get("includeInConversionsMetric"),
               a.get("includeInClientAccountConversionsMetric"), a.get("primaryForGoal"),
               g(a, "attributionModelSettings", "attributionModel"),
               g(a, "attributionModelSettings", "dataDrivenModelStatus"),
               a.get("clickThroughLookbackWindowDays"),
               g(a, "floodlightSettings", "activityId"),
               g(a, "floodlightSettings", "activityTag"),
               g(a, "floodlightSettings", "activityGroupTag"),
               g(a, "valueSettings", "defaultValue"),
               g(a, "valueSettings", "alwaysUseDefaultValue"),
               g(a, "valueSettings", "defaultCurrencyCode"),
               a.get("ownerCustomer"), a.get("creationTime"), a.get("appId")]
        w.writerow(row)
        print(f"id={a.get('id'):<12s} {a.get('name')[:34]:<34s} {a.get('status'):<8s} "
              f"{str(a.get('type'))[:22]:<22s} cat={str(a.get('category'))[:12]:<12s}")
        print(f"   incl_conv={a.get('includeInConversionsMetric')!s:<5s} "
              f"primary={a.get('primaryForGoal')!s:<5s} "
              f"attrib={str(g(a,'attributionModelSettings','attributionModel'))[:18]:<18s} "
              f"lookback={a.get('clickThroughLookbackWindowDays')}")
        print(f"   floodlight activity={g(a,'floodlightSettings','activityId')} "
              f"tag={g(a,'floodlightSettings','activityTag')} "
              f"group={g(a,'floodlightSettings','activityGroupTag')}")
        print(f"   default_value={g(a,'valueSettings','defaultValue')} "
              f"always={g(a,'valueSettings','alwaysUseDefaultValue')} "
              f"currency={g(a,'valueSettings','defaultCurrencyCode')} "
              f"created={a.get('creationTime')}")
        print()
