"""R3: what actually changed on 2 and 3 September, by campaign group.

Round 4 concluded "not one keyword was modified" from `last_modified_time`.
That field keeps only the MOST RECENT edit per object, so any edit made on
3 September that was later touched again is invisible to it. change_status
keeps the per-resource change date and shows 3,300 AD_GROUP_CRITERION and 974
CAMPAIGN_SHARED_SET changes on 3 September alone.

This script asks which campaigns those changes landed on, split UK+IE against
the rest, because the UK zero is the open question rounds 3 to 6 could not close.
"""
import csv, collections, json
from lib_gads import search, RAW, CLEAN, ACCOUNTS
from lib_sa360 import dest_group, segment

ACC = ACCOUNTS["pk_nonbrand"]

rows = [json.loads(l) for l in open(RAW / "r2_change_status.jsonl", encoding="utf-8")]
print(f"{len(rows):,d} change_status rows")

# campaign id -> name, so changes can be grouped by destination
names = {}
r, err = search(ACC, "SELECT campaign.id, campaign.name, campaign.status FROM campaign")
if err:
    raise SystemExit(err)
for x in r:
    names[x["campaign"]["id"]] = x["campaign"]["name"]
print(f"{len(names):,d} campaigns in the account")


def camp_id(cs, key):
    v = cs.get(key) or ""
    # resource names look like customers/X/campaigns/Y or .../campaignCriteria/Y~Z
    if "/campaigns/" in v:
        return v.split("/campaigns/")[1].split("~")[0]
    return None


WINDOWS = {"2026-08-19": "19 Aug", "2026-08-20": "20 Aug budget cut",
           "2026-09-02": "2 Sep switch", "2026-09-03": "3 Sep switch",
           "2026-09-17": "17 Sep", "2026-09-25": "25 Sep"}

print("\n=== changes on the key days, by destination group ===")
out = []
for day, label in WINDOWS.items():
    sel = [x["changeStatus"] for x in rows
           if (x["changeStatus"].get("lastChangeDateTime") or "")[:10] == day]
    if not sel:
        continue
    G = collections.defaultdict(collections.Counter)
    for cs in sel:
        cid = (camp_id(cs, "campaign") or camp_id(cs, "campaignCriterion")
               or camp_id(cs, "campaignSharedSet") or camp_id(cs, "adGroupCriterion")
               or camp_id(cs, "adGroup") or camp_id(cs, "campaignBudget"))
        g = segment(names.get(cid, "")) if cid else "unattributable"
        G[g][cs.get("resourceType")] += 1
    print(f"\n--- {day}  {label}  ({len(sel):,d} changes) ---")
    for g, c in sorted(G.items(), key=lambda kv: -sum(kv[1].values())):
        tot = sum(c.values())
        print(f"   {g:<28}{tot:>7,d}  " + ", ".join(f"{k} {v:,d}" for k, v in c.most_common(4)))
        for k, v in c.items():
            out.append({"date": day, "label": label, "segment": g,
                        "resource_type": k, "changes": v})

with open(CLEAN / "r3_switch_changes_by_group.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["date", "label", "segment", "resource_type", "changes"])
    w.writeheader(); w.writerows(out)

# status of the criteria that changed at the switch: added, removed or edited
print("\n=== resource_status of the 3 Sep ad group criterion changes ===")
sel = [x["changeStatus"] for x in rows
       if (x["changeStatus"].get("lastChangeDateTime") or "")[:10] == "2026-09-03"
       and x["changeStatus"].get("resourceType") == "AD_GROUP_CRITERION"]
st = collections.Counter(x.get("resourceStatus") for x in sel)
print(f"   {len(sel):,d} criteria: {dict(st.most_common())}")

print("\n=== resource_status of the campaign shared set changes at the switch ===")
for day in ("2026-08-20", "2026-09-02", "2026-09-03"):
    sel = [x["changeStatus"] for x in rows
           if (x["changeStatus"].get("lastChangeDateTime") or "")[:10] == day
           and x["changeStatus"].get("resourceType") == "CAMPAIGN_SHARED_SET"]
    if not sel:
        continue
    st = collections.Counter(x.get("resourceStatus") for x in sel)
    G = collections.Counter(segment(names.get(camp_id(x, "campaignSharedSet"), ""))
                            for x in sel)
    print(f"   {day}: {len(sel):,d} campaign shared set changes  {dict(st.most_common())}")
    for g, n in G.most_common():
        print(f"      {g:<28}{n:>6,d}")
print("\nwrote r3_switch_changes_by_group.csv")
