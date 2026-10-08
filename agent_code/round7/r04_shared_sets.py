"""R4: the shared negative lists swapped at the switch.

change_status shows 487 shared sets REMOVED and 487 ADDED on 3 September, and
56 removed plus 56 added on 2 September. SA360 cannot see shared sets at all,
so rounds 3 to 6 never knew this happened. This reads what was swapped, onto
which campaigns, and what is inside the lists.
"""
import csv, collections, json, sys
from lib_gads import search, write_jsonl, RAW, CLEAN, ACCOUNTS
from lib_sa360 import segment, dest_group

ACC = ACCOUNTS["pk_nonbrand"]

names = {}
r, err = search(ACC, "SELECT campaign.id, campaign.name, campaign.status FROM campaign")
if err:
    sys.exit(err)
for x in r:
    names[x["campaign"]["id"]] = x["campaign"]["name"]

# the shared sets themselves
sets_, err = search(ACC, "SELECT shared_set.id, shared_set.name, shared_set.type, "
                         "shared_set.status, shared_set.member_count, "
                         "shared_set.reference_count FROM shared_set")
if err:
    sys.exit(f"shared_set: {err}")
S = {}
for x in sets_:
    s = x["sharedSet"]
    S[s["id"]] = s
print(f"{len(S):,d} shared sets in the PK account")
for s in sorted(S.values(), key=lambda z: -int(z.get("memberCount", 0) or 0))[:15]:
    print(f"   {s['id']:<14} {str(s.get('type')):<18} {str(s.get('status')):<9} "
          f"members {str(s.get('memberCount','?')):>6}  refs {str(s.get('referenceCount','?')):>5}  "
          f"{s.get('name')}")

# which campaigns had which set swapped on each day
rows = [json.loads(l) for l in open(RAW / "r2_change_status.jsonl", encoding="utf-8")]
css = [x["changeStatus"] for x in rows if x["changeStatus"].get("resourceType") == "CAMPAIGN_SHARED_SET"]
print(f"\n{len(css):,d} campaign shared set changes in the 90 day window")

out = []
for day in sorted({(x.get("lastChangeDateTime") or "")[:10] for x in css}):
    sel = [x for x in css if (x.get("lastChangeDateTime") or "")[:10] == day]
    if len(sel) < 10:
        continue
    G = collections.defaultdict(collections.Counter)
    setcount = collections.Counter()
    for x in sel:
        cid = (x.get("campaign") or "").rsplit("/", 1)[-1]
        sid = (x.get("sharedSet") or "").rsplit("/", 1)[-1]
        g = segment(names.get(cid, "")) if cid in names else "campaign not in account"
        G[g][x.get("resourceStatus")] += 1
        setcount[(sid, x.get("resourceStatus"))] += 1
    print(f"\n--- {day}  {len(sel):,d} changes ---")
    for g, c in sorted(G.items(), key=lambda kv: -sum(kv[1].values())):
        print(f"   {g:<30} " + ", ".join(f"{k} {v:,d}" for k, v in c.most_common()))
        for k, v in c.items():
            out.append({"date": day, "segment": g, "operation": k, "campaigns": v})
    print("   lists involved:")
    for (sid, op), n in setcount.most_common(8):
        s = S.get(sid, {})
        print(f"      {op:<8} {sid:<14} members {str(s.get('memberCount','?')):>6}  "
              f"{s.get('name', '(set no longer exists)')}")

with open(CLEAN / "r4_shared_set_swaps.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["date", "segment", "operation", "campaigns"])
    w.writeheader(); w.writerows(out)

with open(CLEAN / "r4_shared_sets.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["shared_set_id", "name", "type", "status", "member_count", "reference_count"])
    for s in sorted(S.values(), key=lambda z: str(z.get("name"))):
        w.writerow([s.get("id"), s.get("name"), s.get("type"), s.get("status"),
                    s.get("memberCount"), s.get("referenceCount")])
print("\nwrote r4_shared_set_swaps.csv and r4_shared_sets.csv")
