"""R7: resolve the open caveat on FINDINGS_india.md.

I reported "0 of 1,021 India campaigns have a reverse direction negative" and
flagged it as the one claim I would not act on, because SA360 cannot read shared
negative lists. PK turns out to have 42 shared sets and 6,283 attachments, so
the caveat was well placed. This answers it for India.
"""
import csv, collections, re, sys
from lib_gads import search, CLEAN, ACCOUNTS

ACC = ACCOUNTS["in_nonbrand"]

sets_, err = search(ACC, "SELECT shared_set.id, shared_set.name, shared_set.type, "
                         "shared_set.status, shared_set.member_count, "
                         "shared_set.reference_count FROM shared_set")
if err:
    sys.exit(err)
S = {x["sharedSet"]["id"]: x["sharedSet"] for x in sets_}
live = [s for s in S.values() if s.get("status") == "ENABLED"]
print(f"India: {len(S)} shared sets, {len(live)} enabled")

names = {}
r, err = search(ACC, "SELECT campaign.id, campaign.name FROM campaign "
                     "WHERE campaign.status = 'ENABLED'")
for x in r:
    names[x["campaign"]["id"]] = x["campaign"]["name"]

att, err = search(ACC, "SELECT campaign.id, campaign_shared_set.shared_set "
                       "FROM campaign_shared_set WHERE campaign.status = 'ENABLED'")
if err:
    sys.exit(err)
A = collections.defaultdict(list)
for x in att:
    A[x["campaign"]["id"]].append((x["campaignSharedSet"].get("sharedSet") or "").rsplit("/", 1)[-1])
print(f"{len(names):,d} enabled campaigns, {len(att):,d} attachments on {len(A):,d} of them")

IN_PLACES = ["india", "delhi", "mumbai", "bombay", "bangalore", "bengaluru", "chennai",
             "madras", "hyderabad", "kolkata", "calcutta", "ahmedabad", "kochi", "cochin",
             "trivandrum", "goa", "amritsar", "nagpur", "calicut", "pune", "lucknow",
             "chandigarh", "jaipur"]
REV = re.compile("|".join(r"to\s+" + c for c in IN_PLACES))

used = sorted({sid for v in A.values() for sid in v})
print(f"{len(used)} distinct lists are actually attached to enabled campaigns\n")
print(f"{'id':<14}{'members':>9}{'reverse':>9}  name")
print("-" * 76)
rows_out = []
rev_by_set = {}
for sid in used:
    s = S.get(sid, {})
    c, e2 = search(ACC, "SELECT shared_criterion.keyword.text, "
                        "shared_criterion.keyword.match_type "
                        f"FROM shared_criterion WHERE shared_set.id = {sid}")
    if e2:
        print(f"{sid:<14}  {e2[:50]}"); continue
    kws = [(x["sharedCriterion"].get("keyword", {}).get("text", "") or "",
            x["sharedCriterion"].get("keyword", {}).get("matchType", "")) for x in c]
    rev = [t for t, _ in kws if REV.search(t.lower())]
    rev_by_set[sid] = set(t.lower() for t in rev)
    print(f"{sid:<14}{len(kws):>9,d}{len(rev):>9,d}  {s.get('name','(unknown)')}")
    for t, m in kws:
        rows_out.append({"shared_set_id": sid, "shared_set_name": s.get("name"),
                         "keyword": t, "match_type": m,
                         "is_reverse_direction": "yes" if REV.search(t.lower()) else "no"})
    if rev:
        for t in rev[:6]:
            print(f"      reverse: {t[:60]}")

covered = sum(1 for cid in names if any(rev_by_set.get(s) for s in A.get(cid, [])))
print(f"\n=== the answer ===")
print(f"enabled India campaigns: {len(names):,d}")
print(f"campaigns with at least one shared list attached: {len(A):,d}")
print(f"campaigns covered by a list containing a reverse direction negative: {covered:,d}")
tot_rev = sum(len(v) for v in rev_by_set.values())
print(f"distinct reverse direction negatives across all attached lists: {tot_rev:,d}")

if rows_out:
    with open(CLEAN / "r7_india_shared_sets.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows_out[0].keys()))
        w.writeheader(); w.writerows(rows_out)
    print(f"\nwrote r7_india_shared_sets.csv, {len(rows_out):,d} criteria")
