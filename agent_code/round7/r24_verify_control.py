"""Verify FINDINGS_round7d_control.md from the clean tables."""
import csv
from lib_gads import CLEAN

ok, bad = [], []
def check(label, got, want, tol=0.02):
    good = (abs(got - want) <= tol * max(abs(want), 1e-9)) if isinstance(want, float) else got == want
    (ok if good else bad).append(f"{label}: got {got}, expected {want}")

rd = lambda f: list(csv.DictReader(open(CLEAN / f, encoding="utf-8")))

m = {r["market"]: r for r in rd("r22_calibration_four_markets.csv")}
for mkt, ns, nb, rb, rm in [("PK", 27511, 53, 15.22, 8.78), ("IN", 145772, 135, 26.89, 17.84),
                            ("CA", 52402, 305, 4.74, 3.10), ("DE", 26501, 258, 4.79, 3.07)]:
    r = m[mkt]
    check(f"{mkt} searches", int(r["searches"]), ns)
    check(f"{mkt} sales", int(r["sales"]), nb)
    check(f"{mkt} inflation base", float(r["ratio_base"]), rb)
    check(f"{mkt} inflation ml", float(r["ratio_ml"]), rm)

for mkt, dests, med, p90p10 in [("PK", 4, 10.9, 3.07), ("IN", 15, 18.2, 9.1),
                                ("CA", 28, 3.7, 8.69), ("DE", 33, 5.4, 4.33)]:
    r = m[mkt]
    check(f"{mkt} destinations", int(r["destinations_tested"]), dests)
    check(f"{mkt} median ratio", round(float(r["median_ratio"]), 1), med, 0.01)
    check(f"{mkt} p90 over p10", round(float(r["spread_p90_over_p10"]), 2), p90p10, 0.01)

d = {r["market"]: r for r in rd("r23_decomposition.csv")}
for mkt, vr, sps, infl in [("PK", 0.0293, 519.1, 15.22), ("IN", 0.0249, 1079.8, 26.89),
                           ("CA", 0.0276, 171.8, 4.74), ("DE", 0.0467, 102.7, 4.79)]:
    r = d[mkt]
    check(f"{mkt} value ratio", float(r["value_ratio"]), vr, 0.01)
    check(f"{mkt} searches per sale", float(r["searches_per_sale"]), sps, 0.01)
    check(f"{mkt} inflation identity",
          round(float(r["value_ratio"]) * float(r["searches_per_sale"]), 2), infl, 0.01)

vrs = [float(r["value_ratio"]) for r in d.values()]
check("value ratio range stays inside 0.024 to 0.047", min(vrs) > 0.024 and max(vrs) < 0.048, True)
sp = [float(r["searches_per_sale"]) for r in d.values()]
check("searches per sale vary at least tenfold", round(max(sp) / min(sp), 1), 10.5, 0.02)

b = {r["market"]: r for r in rd("r23_bootstrap_spread.csv")}
for mkt, pool, med in [("PK", 4, 3.1), ("DE", 33, 3.5), ("CA", 28, 4.3), ("IN", 15, 6.5)]:
    check(f"{mkt} bootstrap pool", int(b[mkt]["pool_size"]), pool)
    check(f"{mkt} bootstrap median spread", round(float(b[mkt]["median_spread_k4"]), 1), med, 0.03)

check("PK bootstrap spread is the lowest of the four",
      min(b, key=lambda k: float(b[k]["median_spread_k4"])), "PK")
check("PK raw destination spread is the lowest of the four",
      min(m, key=lambda k: float(m[k]["spread_p90_over_p10"])), "PK")

print(f"{len(ok)} checks passed")
for x in bad:
    print("  FAIL  " + x)
print("ALL CHECKS PASSED" if not bad else f"\n{len(bad)} FAILURES")
