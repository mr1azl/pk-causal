"""Verify every number in FINDINGS_round7c_lag.md from the clean tables."""
import csv
from lib_gads import CLEAN

ok, bad = [], []
def check(label, got, want, tol=0.02):
    good = (abs(got - want) <= tol * max(abs(want), 1e-9)) if isinstance(want, float) else got == want
    (ok if good else bad).append(f"{label}: got {got}, expected {want}")

rd = lambda f: list(csv.DictReader(open(CLEAN / f, encoding="utf-8")))

a = rd("r18_click_to_conversion_lag.csv")
b = [r for r in a if r["action"] == "QR_Booking"]
check("markets with a booking lag row", len(b), 4)
for mkt, n, med, p90, s24 in [("PK", 80, 1.5, 266.9, 75.0), ("IN", 237, 1.2, 212.3, 71.7),
                              ("CA", 471, 0.9, 120.6, 77.3), ("DE", 347, 0.95, 187.8, 72.6)]:
    r = next(x for x in b if x["market"] == mkt)
    check(f"{mkt} n", int(r["n"]), n)
    check(f"{mkt} median h", float(r["median_h"]), med, 0.06)
    check(f"{mkt} p90 h", float(r["p90_h"]), p90, 0.05)
    check(f"{mkt} within 24h", float(r["same_day_pct"]), s24, 0.01)

c = rd("r19_lag_curve.csv")
al = next(r for r in c if r["market"] == "ALL")
check("pooled bookings", int(al["n"]), 1135)
for k, want in [("1h", 49.0), ("1d", 74.0), ("3d", 82.0), ("7d", 90.0),
                ("14d", 95.0), ("21d", 97.0), ("28d", 100.0)]:
    check(f"curve {k}", round(float(al[k])), round(want))

d = rd("r19_window_completeness.csv")
for n, comp in [(7, 84.0), (14, 88.5), (28, 92.9), (54, 96.3), (90, 97.8)]:
    r = next(x for x in d if int(x["window_days"]) == n)
    check(f"completeness {n}d", round(float(r["completeness_pct"]), 1), comp, 0.005)
    check(f"understatement {n}d", round(float(r["understatement_pct"]), 1), round(100 - comp, 1), 0.02)

e = rd("r18_search_to_booking_lag.csv")
check("journey join markets", len(e), 4)
for r in e:
    check(f"{r['market']} journey median under 0.05 d", float(r["median_days"]) < 0.05, True)
    check(f"{r['market']} journey all within 1d", float(r["within_1d"]), 100.0)

print(f"{len(ok)} checks passed")
for x in bad:
    print("  FAIL  " + x)
print("ALL CHECKS PASSED" if not bad else f"\n{len(bad)} FAILURES")
