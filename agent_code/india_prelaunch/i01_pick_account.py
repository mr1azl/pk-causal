"""I0 step 2: which India accounts actually carry spend, so the choice of main
non-brand account(s) is made on data and logged, not assumed from the name.
Window: 12 weeks to yesterday."""
import csv, sys
from lib_sa360 import stream, CLEAN, chunks

D1, D2 = "2026-07-16", "2026-10-07"     # 84 days, 12 weeks to yesterday

accts = list(csv.DictReader(open(CLEAN / "i0_india_accounts.csv", encoding="utf-8")))
out = []
for a in accts:
    if a["account_type"] != "GOOGLE_ADS":
        continue            # Bing is out of scope, same decision as PK
    cost = clicks = impr = 0.0
    camps = set()
    err = ""
    for d1, d2 in chunks(D1, D2, 31):
        c, rows = stream(a["id"],
            "SELECT campaign.id, metrics.cost_micros, metrics.clicks, metrics.impressions "
            f"FROM campaign WHERE segments.date BETWEEN '{d1}' AND '{d2}'")
        if c != 200:
            err = f"{c} {rows}"; break
        for r in rows:
            m = r.get("metrics", {})
            cost += int(m.get("costMicros", 0)) / 1e6
            clicks += int(m.get("clicks", 0))
            impr += int(m.get("impressions", 0))
            if int(m.get("costMicros", 0)) > 0:
                camps.add(r["campaign"]["id"])
    out.append({"id": a["id"], "name": a["name"], "cost_12w": round(cost, 2),
                "clicks_12w": int(clicks), "impressions_12w": int(impr),
                "campaigns_with_spend": len(camps), "error": err})

dest = CLEAN / "i0_account_spend.csv"
with open(dest, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

print(f"Google India accounts, {D1} to {D2}\n")
print(f"{'id':>12}  {'cost':>12} {'clicks':>10} {'camps w/ spend':>15}  name")
for r in sorted(out, key=lambda x: -x["cost_12w"]):
    print(f"{r['id']:>12}  {r['cost_12w']:>12,.0f} {r['clicks_12w']:>10,d} "
          f"{r['campaigns_with_spend']:>15,d}  {r['name']}" + (f"  ERR {r['error']}" if r["error"] else ""))
print(f"\nwrote {dest}")
