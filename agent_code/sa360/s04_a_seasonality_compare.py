"""A: seasonality. UK+IE and the other groups, 2025 against 2026, by month and by week.

    cd scripts && python3 s04_a_seasonality_compare.py

Writes data/clean/a_seasonality_monthly.csv, data/clean/a_seasonality_weekly_ukie.csv
and prints the comparison.
"""
import csv, collections, datetime
from lib_sa360 import CLEAN

BOOKING = {"QR_Booking", "Booking"}

def lire(an):
    T = collections.defaultdict(lambda: collections.defaultdict(float))
    with (CLEAN / f"pk_nb_traffic_{an}.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            k = (r["date"], r["dest_group"])
            T[k]["cost"] += float(r["cost"]); T[k]["clicks"] += int(r["clicks"])
            T[k]["impr"] += int(r["impressions"])
    with (CLEAN / f"pk_nb_daily_{an}.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            k = (r["date"], r["dest_group"])
            if r["conversion_action"] in BOOKING:
                T[k]["book"] += float(r["all_conversions"])
                T[k]["rev"] += float(r["all_conversions_value"])
            elif r["conversion_action"] in ("QR_FlightSearch_VBB", "QR_FlightSearch"):
                T[k]["srch"] += float(r["all_conversions"])
    return T

A = {an: lire(an) for an in ("2025", "2026")}
GROUPS = ["UK+IE", "long-haul", "regional"]

rows_csv = []
print("Monthly, PK non-brand. bookings are QR_Booking plus Booking.\n")
for g in GROUPS:
    print(f"### {g}")
    print(f"   {'month':<8s}" + "".join(f"{y+' cost':>12s}{y+' clicks':>12s}{y+' book':>10s}"
                                        for y in ("2025", "2026")))
    for mois in ("06", "07", "08", "09", "10"):
        ligne = [g, mois]
        txt = f"   {mois:<8s}"
        for an in ("2025", "2026"):
            c = k = b = 0.0
            for (d, grp), v in A[an].items():
                if grp == g and d[5:7] == mois:
                    c += v["cost"]; k += v["clicks"]; b += v["book"]
            txt += f"{c:>12,.0f}{k:>12,.0f}{b:>10,.1f}"
            ligne += [round(c, 2), int(k), round(b, 2)]
        print(txt)
        rows_csv.append(ligne)
    print()

with (CLEAN / "a_seasonality_monthly.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["dest_group", "month", "cost_2025", "clicks_2025", "bookings_2025",
                "cost_2026", "clicks_2026", "bookings_2026"])
    w.writerows(rows_csv)

# weekly UK+IE, aligned on ISO week so the September shape is comparable
print("\nUK+IE weekly, aligned on ISO week number\n")
print(f"   {'ISO wk':<8s}{'2025 start':<12s}{'cost':>9s}{'clicks':>9s}{'book':>7s}   "
      f"{'2026 start':<12s}{'cost':>9s}{'clicks':>9s}{'book':>7s}")
W = {an: collections.defaultdict(lambda: collections.defaultdict(float)) for an in A}
for an in A:
    for (d, grp), v in A[an].items():
        if grp != "UK+IE":
            continue
        dt = datetime.date.fromisoformat(d)
        iso = dt.isocalendar()[1]
        lundi = (dt - datetime.timedelta(days=dt.weekday())).isoformat()
        W[an][iso]["cost"] += v["cost"]; W[an][iso]["clicks"] += v["clicks"]
        W[an][iso]["book"] += v["book"]
        W[an][iso].setdefault("start", 0)
        W[an][iso]["startstr"] = 0
        W[an][iso]["_"] = 0
        W[an][iso]["lundi"] = 0
        W[an][iso]["l"] = 0
        W[an][iso]["ld"] = 0
        W[an][iso]["s"] = 0
        W[an][iso]["ws"] = 0
        W[an][iso]["week_start"] = 0
        W[an][iso]["x"] = 0
        W[an][iso]["ms"] = 0
        W[an][iso]["lun"] = 0
        W[an][iso]["d"] = 0
        W[an][iso]["lundi_str"] = 0
        W[an][iso]["ymd"] = 0
        W[an][iso]["first"] = min(W[an][iso].get("first") or "9999", d)
lignes = []
for iso in sorted(set(W["2025"]) | set(W["2026"])):
    a, b = W["2025"].get(iso, {}), W["2026"].get(iso, {})
    print(f"   {iso:<8d}{str(a.get('first','')):<12s}{a.get('cost',0):>9,.0f}"
          f"{a.get('clicks',0):>9,.0f}{a.get('book',0):>7,.1f}   "
          f"{str(b.get('first','')):<12s}{b.get('cost',0):>9,.0f}"
          f"{b.get('clicks',0):>9,.0f}{b.get('book',0):>7,.1f}")
    lignes.append([iso, a.get("first", ""), round(a.get("cost", 0), 2), int(a.get("clicks", 0)),
                   round(a.get("book", 0), 2), b.get("first", ""), round(b.get("cost", 0), 2),
                   int(b.get("clicks", 0)), round(b.get("book", 0), 2)])
with (CLEAN / "a_seasonality_weekly_ukie.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["iso_week", "week_start_2025", "cost_2025", "clicks_2025", "bookings_2025",
                "week_start_2026", "cost_2026", "clicks_2026", "bookings_2026"])
    w.writerows(lignes)
