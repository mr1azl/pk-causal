"""I6: the portfolios India sits on today, read from the MCC because portfolios
owned by the manager account are invisible from the client account (PK lesson).
Plus geo target type settings, targeted locations, and last_modified_time across
campaigns, ad groups, keywords and budgets over the last 30 days.
Attributes are current values only, never time sliced.
"""
import csv, collections, sys
from lib_sa360 import stream, CLEAN, MCC, IN_ACCOUNT, in_dest_group, is_non_brand

inv = list(csv.DictReader(open(CLEAN / "i0_campaign_inventory.csv", encoding="utf-8")))
en = [r for r in inv if r["status"] == "ENABLED"]
pf = collections.Counter((r["bidding_strategy"] or "").rsplit("/", 1)[-1] for r in en)
spend = collections.Counter()
for r in en:
    spend[(r["bidding_strategy"] or "").rsplit("/", 1)[-1]] += float(r["cost_12w"] or 0)

print(f"{len(en):,d} enabled non-brand campaigns on {len(pf)} portfolios\n")
out = []
for sid, n in pf.most_common():
    row = {"portfolio_id": sid, "enabled_campaigns": n, "cost_12w": round(spend[sid], 2)}
    found = False
    for src, lab in ((IN_ACCOUNT, "account"), (MCC, "MCC")):
        c, b = stream(src, "SELECT bidding_strategy.id, bidding_strategy.name, "
                           "bidding_strategy.type, bidding_strategy.status, "
                           "bidding_strategy.maximize_conversions.target_cpa_micros, "
                           "bidding_strategy.maximize_conversion_value.target_roas, "
                           "bidding_strategy.maximize_conversion_value.cpc_bid_ceiling_micros, "
                           "bidding_strategy.maximize_conversion_value.cpc_bid_floor_micros "
                           f"FROM bidding_strategy WHERE bidding_strategy.id = {sid}")
        if c == 200 and b:
            s = b[0]["biddingStrategy"]
            mc = s.get("maximizeConversions", {}) or {}
            mv = s.get("maximizeConversionValue", {}) or {}
            tcpa = mc.get("targetCpaMicros")
            row.update({"owner": lab, "name": s.get("name"), "type": s.get("type"),
                        "status": s.get("status"),
                        "target_cpa": round(int(tcpa) / 1e6, 2) if tcpa else "NOT SET",
                        "target_roas": mv.get("targetRoas", "NOT SET"),
                        "cpc_ceiling": mv.get("cpcBidCeilingMicros", "NOT SET"),
                        "cpc_floor": mv.get("cpcBidFloorMicros", "NOT SET")})
            found = True
            break
    if not found:
        row.update({"owner": "not readable", "name": "", "type": "", "status": "",
                    "target_cpa": "", "target_roas": "", "cpc_ceiling": "", "cpc_floor": ""})
    out.append(row)
    print(f"  {sid}  {row['enabled_campaigns']:>4,d} campaigns  {row['cost_12w']:>10,.0f} USD  "
          f"owner={row['owner']:<12} type={row['type']:<24} "
          f"targetCPA={row['target_cpa']}  targetROAS={row['target_roas']}  "
          f"cpcCeiling={row['cpc_ceiling']}")

with open(CLEAN / "i6_portfolios.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

# geo target type setting and targeted locations
c, rows = stream(IN_ACCOUNT, "SELECT campaign.id, campaign.name, "
                             "campaign.geo_target_type_setting.positive_geo_target_type, "
                             "campaign.geo_target_type_setting.negative_geo_target_type "
                             "FROM campaign WHERE campaign.status = 'ENABLED'")
print(f"\ngeo target type setting ({c}):")
if c == 200:
    g = collections.Counter()
    for r in rows:
        s = r["campaign"].get("geoTargetTypeSetting", {}) or {}
        g[(s.get("positiveGeoTargetType"), s.get("negativeGeoTargetType"))] += 1
    for k, n in g.most_common():
        print(f"   positive={k[0]}  negative={k[1]}  {n:,d} campaigns")

c, rows = stream(IN_ACCOUNT, "SELECT campaign.id, campaign_criterion.location.geo_target_constant, "
                             "campaign_criterion.negative, campaign_criterion.type "
                             "FROM campaign_criterion WHERE campaign.status = 'ENABLED' "
                             "AND campaign_criterion.type = 'LOCATION'")
print(f"\nlocation criteria ({c}): {len(rows) if c==200 else rows}")
if c == 200:
    loc = collections.Counter()
    for r in rows:
        cc = r["campaignCriterion"]
        key = (cc.get("location", {}).get("geoTargetConstant", "?"), cc.get("negative", False))
        loc[key] += 1
    print("   top targeted locations by campaign count:")
    for (gt, negv), n in loc.most_common(10):
        print(f"      {gt:<34} negative={negv}  {n:,d}")

# last modified over 30 days
print("\nlast_modified_time, last 30 days (attributes are current values only):")
for res, q in [("campaign", "SELECT campaign.id, campaign.last_modified_time FROM campaign "
                            "WHERE campaign.status = 'ENABLED'"),
               ("ad_group", "SELECT ad_group.id, ad_group.last_modified_time FROM ad_group "
                            "WHERE ad_group.status = 'ENABLED' AND campaign.status = 'ENABLED'")]:
    c, rr = stream(IN_ACCOUNT, q)
    if c != 200:
        print(f"   {res}: FAILED {c} {rr}"); continue
    key = "lastModifiedTime"
    d = collections.Counter((x[res.replace("_g", "G").replace("ad_group", "adGroup")]
                             .get(key) or "?")[:10] for x in rr)
    recent = {k: v for k, v in d.items() if k >= "2026-09-08"}
    print(f"   {res}: {len(rr):,d} enabled, {sum(recent.values()):,d} modified in the last 30 days")
    for k, v in sorted(recent.items(), reverse=True)[:8]:
        print(f"      {k}  {v:>6,d}")
