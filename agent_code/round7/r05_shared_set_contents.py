"""R5: what is inside the list that replaced every other list on 3 September.

Every campaign had its old shared set removed and one new set, 12218345868,
added: 250 long-haul, 179 regional, 56 UK+IE, proportional to the account. The
question is whether the new list blocks traffic the old ones allowed.
"""
import csv, collections, sys
from lib_gads import search, CLEAN, ACCOUNTS
from lib_sa360 import segment

ACC = ACCOUNTS["pk_nonbrand"]
KEY = ["12218345868",                                   # the one added everywhere on 3 Sep
       "12089549173", "12069220122", "12069214392",     # the ones removed
       "12070848460", "12161807883", "12218921162", "12073259387", "12170646921"]

# shared_set with no status filter, so removed sets are included too
rows, err = search(ACC, "SELECT shared_set.id, shared_set.name, shared_set.type, "
                        "shared_set.status, shared_set.member_count, "
                        "shared_set.reference_count FROM shared_set "
                        "WHERE shared_set.id IN (" + ", ".join(KEY) + ")")
if err:
    sys.exit(err)
print(f"{len(rows)} of the {len(KEY)} key sets are readable\n")
print(f"{'id':<14}{'status':<10}{'members':>8}{'refs':>6}  name")
print("-" * 76)
for x in rows:
    s = x["sharedSet"]
    print(f"{s['id']:<14}{str(s.get('status')):<10}{str(s.get('memberCount','?')):>8}"
          f"{str(s.get('referenceCount','?')):>6}  {s.get('name')}")

print("\n=== contents of each readable set ===")
out = []
for x in rows:
    s = x["sharedSet"]
    sid = s["id"]
    c, err2 = search(ACC, "SELECT shared_criterion.criterion_id, shared_criterion.type, "
                          "shared_criterion.keyword.text, shared_criterion.keyword.match_type, "
                          "shared_set.id FROM shared_criterion "
                          f"WHERE shared_set.id = {sid}")
    if err2:
        print(f"\n   {sid}: {err2}"); continue
    kws = [(r["sharedCriterion"].get("keyword", {}).get("text", ""),
            r["sharedCriterion"].get("keyword", {}).get("matchType", "")) for r in c]
    mt = collections.Counter(m for _, m in kws)
    print(f"\n   --- {sid}  {s.get('name')}  ({len(kws):,d} criteria, {dict(mt)}) ---")
    for t, m in kws[:14]:
        print(f"        [{m}] {t[:70]}")
    if len(kws) > 14:
        print(f"        ... and {len(kws)-14:,d} more")
    for t, m in kws:
        out.append({"shared_set_id": sid, "shared_set_name": s.get("name"),
                    "status": s.get("status"), "keyword": t, "match_type": m})

if out:
    with open(CLEAN / "r5_shared_set_contents.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    print(f"\nwrote r5_shared_set_contents.csv, {len(out):,d} criteria")
