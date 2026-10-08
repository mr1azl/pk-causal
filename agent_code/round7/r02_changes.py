"""R2: the real change log for PK.

Two resources, two windows, discovered by probing:
  change_status  90 days, back to about 10 Jul. Says WHAT changed and WHEN,
                 across campaigns, budgets, criteria and shared sets. Covers
                 the 20 Aug budget cut and the 2 Sep switch.
  change_event   30 days only, back to 9 Sep. Says WHO changed WHAT with old
                 and new values. Covers the 20 Sep CPC cap and nothing earlier.

Rounds 3 to 6 had neither and inferred every date from the daily series.
User emails are personal data: they are hashed before anything is written.
"""
import csv, collections, hashlib, json, sys
from lib_gads import search, write_jsonl, RAW, CLEAN, ACCOUNTS, chunks

ACC = ACCOUNTS["pk_nonbrand"]
def h(x):
    return hashlib.sha256(str(x).encode()).hexdigest()[:12] if x else ""

# ---- change_status, the 90 day window -------------------------------------
path = RAW / "r2_change_status.jsonl"
if path.exists():
    rows = [json.loads(l) for l in open(path, encoding="utf-8")]
    print(f"skip change_status ({len(rows):,d} rows)")
else:
    rows = []
    # 7 day chunks keep each call under the 10,000 row LIMIT ceiling
    for d1, d2 in chunks("2026-07-11", "2026-10-07", 7):
        r, err = search(ACC,
            "SELECT change_status.last_change_date_time, change_status.resource_type, "
            "change_status.resource_status, change_status.campaign, "
            "change_status.ad_group, change_status.campaign_budget, "
            "change_status.campaign_criterion, change_status.ad_group_criterion, "
            "change_status.shared_set, change_status.campaign_shared_set "
            "FROM change_status "
            f"WHERE change_status.last_change_date_time >= '{d1}' "
            f"AND change_status.last_change_date_time <= '{d2}' "
            "LIMIT 10000")   # change_status requires an explicit LIMIT, max 10k
        if err:
            sys.exit(f"change_status {d1}..{d2} FAILED: {err}")
        rows += r
        print(f"   {d1} to {d2}: {len(r):,d}")
    write_jsonl(path, rows)
    print(f"change_status total {len(rows):,d} rows")

D = collections.defaultdict(collections.Counter)
for x in rows:
    c = x["changeStatus"]
    day = (c.get("lastChangeDateTime") or "?")[:10]
    D[day][c.get("resourceType")] += 1

print("\n=== PK change_status by day, resources that moved ===")
print(f"{'date':<12}{'total':>7}  breakdown")
print("-" * 86)
for day in sorted(D):
    t = sum(D[day].values())
    if t < 5:
        continue
    mix = ", ".join(f"{k} {v:,d}" for k, v in D[day].most_common(5))
    mark = ""
    if day in ("2026-08-20", "2026-08-21"): mark = "  <= budget cut"
    if day in ("2026-09-02", "2026-09-03"): mark = "  <= VBB switch"
    if day in ("2026-09-20", "2026-09-21", "2026-09-22"): mark = "  <= CPC cap"
    print(f"{day:<12}{t:>7,d}  {mix}{mark}")

with open(CLEAN / "r2_change_status_by_day.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["date", "resource_type", "changes"])
    for day in sorted(D):
        for k, v in D[day].most_common():
            w.writerow([day, k, v])

# ---- change_event, the 30 day window with old and new values ---------------
path2 = RAW / "r2_change_event.jsonl"
if path2.exists():
    ev = [json.loads(l) for l in open(path2, encoding="utf-8")]
    print(f"\nskip change_event ({len(ev):,d} rows)")
else:
    ev = []
    for d1, d2 in chunks("2026-09-09", "2026-10-07", 7):
        r, err = search(ACC,
            "SELECT change_event.change_date_time, change_event.change_resource_type, "
            "change_event.resource_change_operation, change_event.changed_fields, "
            "change_event.client_type, change_event.user_email, "
            "change_event.campaign, change_event.ad_group, "
            "change_event.old_resource, change_event.new_resource "
            "FROM change_event "
            f"WHERE change_event.change_date_time >= '{d1}' "
            f"AND change_event.change_date_time <= '{d2}' "
            "LIMIT 10000")
        if err:
            print(f"   change_event {d1}..{d2}: {err}"); continue
        for x in r:                       # hash the email before it is written
            c = x.get("changeEvent", {})
            if "userEmail" in c:
                c["user_hash"] = h(c.pop("userEmail"))
        ev += r
        print(f"   {d1} to {d2}: {len(r):,d}")
    write_jsonl(path2, ev)
    print(f"change_event total {len(ev):,d} rows")

print("\n=== PK change_event, 9 Sep to 7 Oct, who changed what ===")
E = collections.defaultdict(collections.Counter)
users = collections.Counter(); clients = collections.Counter()
for x in ev:
    c = x["changeEvent"]
    day = (c.get("changeDateTime") or "?")[:10]
    E[day][f"{c.get('changeResourceType')}/{c.get('resourceChangeOperation')}"] += 1
    users[c.get("user_hash", "?")] += 1
    clients[c.get("clientType", "?")] += 1
print(f"{'date':<12}{'total':>7}  breakdown")
print("-" * 86)
for day in sorted(E):
    t = sum(E[day].values())
    mix = ", ".join(f"{k} {v:,d}" for k, v in E[day].most_common(4))
    mark = "  <= CPC cap window" if day in ("2026-09-20", "2026-09-21", "2026-09-22") else ""
    print(f"{day:<12}{t:>7,d}  {mix}{mark}")
print(f"\ndistinct users (hashed): {len(users)}")
for u, n in users.most_common():
    print(f"   {u}  {n:,d} changes")
print(f"client types: {dict(clients.most_common())}")

with open(CLEAN / "r2_change_event_by_day.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["date", "resource_and_operation", "changes"])
    for day in sorted(E):
        for k, v in E[day].most_common():
            w.writerow([day, k, v])
print("\nwrote r2_change_status_by_day.csv and r2_change_event_by_day.csv")
