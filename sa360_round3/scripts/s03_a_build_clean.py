"""A: build the clean per-year tables and check what conversion actions exist in each year.

    cd scripts && python3 s03_a_build_clean.py

Writes data/clean/pk_nb_daily_<year>.csv            date x campaign x conversion action
       data/clean/pk_nb_traffic_<year>.csv          date x campaign, cost clicks impressions
"""
import csv, json, collections
from lib_sa360 import RAW, CLEAN, is_non_brand, dest_code, dest_group

CLEAN.mkdir(parents=True, exist_ok=True)
resume = {}

for an in ("2025", "2026"):
    # traffic
    rows = [json.loads(l) for l in (RAW / f"a_traffic_{an}.jsonl").read_text(encoding="utf-8").splitlines()]
    gardes = 0
    dates = set()
    with (CLEAN / f"pk_nb_traffic_{an}.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "campaign_id", "campaign_name", "status", "dest_code", "dest_group",
                    "naming", "cost", "clicks", "impressions"])
        for r in rows:
            c = r["campaign"]; m = r.get("metrics", {})
            if not is_non_brand(c.get("name")):
                continue
            cost = int(m.get("costMicros", 0) or 0) / 1e6
            clk = int(m.get("clicks", 0) or 0)
            imp = int(m.get("impressions", 0) or 0)
            if cost == 0 and clk == 0 and imp == 0:
                continue
            d = r["segments"]["date"]; dates.add(d); gardes += 1
            w.writerow([d, c["id"], c.get("name"), c.get("status"), dest_code(c.get("name")),
                        dest_group(c.get("name")),
                        "pipe" if "|" in (c.get("name") or "") else "legacy",
                        round(cost, 4), clk, imp])
    # conversions
    crows = [json.loads(l) for l in (RAW / f"a_conv_{an}.jsonl").read_text(encoding="utf-8").splitlines()]
    actions = collections.Counter()
    gardesc = 0
    with (CLEAN / f"pk_nb_daily_{an}.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "campaign_id", "campaign_name", "dest_code", "dest_group",
                    "conversion_action", "all_conversions", "all_conversions_value",
                    "all_conversions_by_conv_date", "all_conversions_value_by_conv_date"])
        for r in crows:
            c = r["campaign"]
            if not is_non_brand(c.get("name")):
                continue
            a = r.get("segments", {}).get("conversionActionName")
            if not a:
                continue
            m = r.get("metrics", {})
            v = float(m.get("allConversions", 0) or 0)
            vv = float(m.get("allConversionsValue", 0) or 0)
            bd = float(m.get("allConversionsByConversionDate", 0) or 0)
            bdv = float(m.get("allConversionsValueByConversionDate", 0) or 0)
            if v == 0 and vv == 0 and bd == 0:
                continue
            actions[a] += v
            gardesc += 1
            w.writerow([r["segments"]["date"], c["id"], c.get("name"), dest_code(c.get("name")),
                        dest_group(c.get("name")), a, round(v, 4), round(vv, 4),
                        round(bd, 4), round(bdv, 4)])
    resume[an] = (gardes, gardesc, min(dates), max(dates), actions)
    print(f"\n### {an}: traffic rows kept {gardes:,d}, conversion rows kept {gardesc:,d}")
    print(f"    dates actually returned: {min(dates)} to {max(dates)}")
    print(f"    {len(actions)} conversion actions present, top 12 by volume:")
    for a, n in actions.most_common(12):
        print(f"       {n:>12,.1f}  {a}")

print("\n### conversion actions present in 2026 but not 2025, and the reverse")
a25, a26 = set(resume['2025'][4]), set(resume['2026'][4])
print("   2026 only:", sorted(a26 - a25))
print("   2025 only:", sorted(a25 - a26))
