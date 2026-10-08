"""R6: PK's negatives as they stand today, including the shared lists that
SA360 could not see at all.

Also establishes whether the shared set churn is automation: the sets swapped on
3 September no longer exist, so they were created, attached, detached and
deleted inside the 90 day window.
"""
import csv, collections, re, sys
from lib_gads import search, CLEAN, ACCOUNTS
from lib_sa360 import segment, dest_code

ACC = ACCOUNTS["pk_nonbrand"]

sets_, err = search(ACC, "SELECT shared_set.id, shared_set.name, shared_set.type, "
                         "shared_set.status, shared_set.member_count, "
                         "shared_set.reference_count FROM shared_set")
if err:
    sys.exit(err)
S = {x["sharedSet"]["id"]: x["sharedSet"] for x in sets_}
print(f"=== {len(S):,d} shared sets exist today ===")
print(f"{'id':<14}{'status':<10}{'members':>9}{'refs':>6}  name")
print("-" * 80)
for s in sorted(S.values(), key=lambda z: -int(z.get("memberCount") or 0)):
    print(f"{s['id']:<14}{str(s.get('status')):<10}{str(s.get('memberCount','?')):>9}"
          f"{str(s.get('referenceCount','?')):>6}  {s.get('name')}")

names = {}
r, err = search(ACC, "SELECT campaign.id, campaign.name, campaign.status FROM campaign "
                     "WHERE campaign.status = 'ENABLED'")
if err:
    sys.exit(err)
for x in r:
    names[x["campaign"]["id"]] = x["campaign"]["name"]
print(f"\n{len(names):,d} enabled campaigns")

att, err = search(ACC, "SELECT campaign.id, campaign_shared_set.shared_set, "
                       "campaign_shared_set.status FROM campaign_shared_set "
                       "WHERE campaign.status = 'ENABLED'")
if err:
    sys.exit(f"campaign_shared_set: {err}")
A = collections.defaultdict(list)
for x in att:
    cid = x["campaign"]["id"]
    sid = (x["campaignSharedSet"].get("sharedSet") or "").rsplit("/", 1)[-1]
    A[cid].append(sid)
print(f"{len(att):,d} current attachments across {len(A):,d} campaigns")

G = collections.defaultdict(collections.Counter)
for cid, nm in names.items():
    g = segment(nm)
    G[g]["campaigns"] += 1
    if A.get(cid):
        G[g]["with_list"] += 1
print(f"\n{'segment':<30}{'enabled':>9}{'with a shared list':>20}")
print("-" * 60)
for g, c in sorted(G.items(), key=lambda kv: -kv[1]["campaigns"]):
    print(f"{g:<30}{c['campaigns']:>9,d}{c['with_list']:>20,d}")

# contents of every live set, and the directional test
IN_PK = ["pakistan", "karachi", "lahore", "islamabad", "peshawar", "multan", "faisalabad",
         "sialkot", "quetta", "rawalpindi"]
REV = re.compile("|".join(r"to\s+" + c for c in IN_PK))
rows_out = []
print("\n=== contents of the live sets ===")
for sid, s in S.items():
    c, err2 = search(ACC, "SELECT shared_criterion.criterion_id, shared_criterion.type, "
                          "shared_criterion.keyword.text, shared_criterion.keyword.match_type "
                          f"FROM shared_criterion WHERE shared_set.id = {sid}")
    if err2:
        print(f"   {sid}: {err2}"); continue
    kws = [(r["sharedCriterion"].get("keyword", {}).get("text", "") or "",
            r["sharedCriterion"].get("keyword", {}).get("matchType", "")) for r in c]
    rev = [t for t, _ in kws if REV.search(t.lower())]
    print(f"\n   --- {s.get('name')} ({sid}), {len(kws):,d} criteria, "
          f"{len(rev)} reverse direction ---")
    for t, m in kws[:10]:
        print(f"        [{m}] {t[:68]}")
    if len(kws) > 10:
        print(f"        ... and {len(kws)-10:,d} more")
    for t, m in kws:
        rows_out.append({"shared_set_id": sid, "shared_set_name": s.get("name"),
                         "keyword": t, "match_type": m,
                         "is_reverse_direction": "yes" if REV.search(t.lower()) else "no"})

if rows_out:
    with open(CLEAN / "r6_shared_set_contents.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows_out[0].keys()))
        w.writeheader(); w.writerows(rows_out)
    nrev = sum(1 for r in rows_out if r["is_reverse_direction"] == "yes")
    print(f"\n{len(rows_out):,d} criteria across the live sets, "
          f"{nrev} of them reverse direction")
    print("wrote r6_shared_set_contents.csv")
