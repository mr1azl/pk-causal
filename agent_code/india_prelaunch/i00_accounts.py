"""I0 step 1: every India account under MCC 1144701035.

customer_client carries no account_type in this API, so the engine (Google vs
Bing) is read per account from FROM customer, which does expose account_type
and engine_id. Writes data/clean/i0_india_accounts.csv.
No credentials are read or written here; lib_sa360 handles auth itself.
"""
import csv, re, sys
from lib_sa360 import stream, CLEAN, MCC

Q = ("SELECT customer_client.id, customer_client.descriptive_name, "
     "customer_client.currency_code, customer_client.time_zone, "
     "customer_client.status, customer_client.manager, "
     "customer_client.level, customer_client.hidden, "
     "customer_client.test_account FROM customer_client")

code, rows = stream(MCC, Q)
if code != 200:
    sys.exit(f"customer_client failed: {code} {rows}")
print(f"{len(rows):,d} accounts under the MCC")

def is_india(n):
    """India market token in either naming convention. Deliberately wide, then
    reviewed by eye, because a missed account is worse than a false positive."""
    t = [x.upper() for x in re.split(r"[-_|\s]+", n or "") if x]
    return bool({"IN", "IND", "INDIA"} & set(t))

cand = [r["customerClient"] for r in rows if is_india(r["customerClient"].get("descriptiveName"))]
print(f"{len(cand)} India candidates, reading account_type from each")

out = []
for c in cand:
    cid = c.get("id")
    at, eng = "", ""
    c2, cu = stream(cid, "SELECT customer.account_type, customer.engine_id, "
                         "customer.status, customer.manager FROM customer")
    if c2 == 200 and cu:
        at = cu[0]["customer"].get("accountType", "")
        eng = cu[0]["customer"].get("engineId", "")
    else:
        at = f"unreadable ({c2})"
    out.append({
        "id": cid, "name": c.get("descriptiveName"), "account_type": at,
        "engine_id": eng, "currency": c.get("currencyCode"),
        "time_zone": c.get("timeZone"), "status": c.get("status"),
        "manager": c.get("manager"), "level": c.get("level"),
        "hidden": c.get("hidden"), "test_account": c.get("testAccount"),
    })

out.sort(key=lambda x: (str(x["account_type"]), str(x["name"])))
dest = CLEAN / "i0_india_accounts.csv"
with open(dest, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

print(f"\n{len(out)} India accounts\n")
hdr = f"{'id':>12}  {'account_type':<16} {'status':<9} {'cur':<4} {'mgr':<6} name"
print(hdr); print("-" * len(hdr))
for r in out:
    print(f"{r['id']:>12}  {str(r['account_type']):<16} {str(r['status']):<9} "
          f"{str(r['currency']):<4} {str(r['manager']):<6} {r['name']}")
print(f"\nwrote {dest}")
