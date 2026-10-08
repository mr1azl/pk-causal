"""R11: the same table per day, because the four periods are 68, 13, 18 and 16
days long and raw totals are not comparable across them."""
import csv, collections
from lib_gads import CLEAN, PERIODS

DAYS = {"13 Jun-19 Aug": 68, "20 Aug-1 Sep": 13, "2-19 Sep": 18, "20 Sep-5 Oct": 16}
rows = list(csv.DictReader(open(CLEAN / "r10_pk_terms_by_segment_period.csv", encoding="utf-8")))

print("=== PK search term spend per day, by segment ===")
print(f"{'segment':<12}" + "".join(f"{lab:>16}" for lab, _, _ in PERIODS) + f"{'vs baseline':>13}")
print("-" * 88)
out = []
for seg in ["UK+IE", "long-haul", "regional"]:
    cells, base = [], None
    for lab, _, _ in PERIODS:
        r = next((x for x in rows if x["segment"] == seg and x["period"] == lab), None)
        v = float(r["cost"]) / DAYS[lab] if r else 0.0
        cells.append(v)
        if lab == "13 Jun-19 Aug":
            base = v
    ch = (cells[-1] / base - 1) * 100 if base else 0
    print(f"{seg:<12}" + "".join(f"{c:>16,.0f}" for c in cells) + f"{ch:>12.0f}%")
    for i, (lab, _, _) in enumerate(PERIODS):
        out.append({"segment": seg, "period": lab, "days": DAYS[lab],
                    "cost_per_day": round(cells[i], 2),
                    "vs_baseline_pct": round((cells[i] / base - 1) * 100, 1) if base else ""})

print("\n=== distinct search terms per day, the query footprint ===")
print(f"{'segment':<12}" + "".join(f"{lab:>16}" for lab, _, _ in PERIODS))
print("-" * 76)
for seg in ["UK+IE", "long-haul", "regional"]:
    cells = []
    for lab, _, _ in PERIODS:
        r = next((x for x in rows if x["segment"] == seg and x["period"] == lab), None)
        cells.append(int(r["distinct_terms"]) / DAYS[lab] if r else 0)
    print(f"{seg:<12}" + "".join(f"{c:>16,.0f}" for c in cells))

print("\n=== concentration: share of spend on the top 200 terms ===")
print(f"{'segment':<12}" + "".join(f"{lab:>16}" for lab, _, _ in PERIODS))
print("-" * 76)
for seg in ["UK+IE", "long-haul", "regional"]:
    cells = []
    for lab, _, _ in PERIODS:
        r = next((x for x in rows if x["segment"] == seg and x["period"] == lab), None)
        cells.append(float(r["top200_share_pct"]) if r else 0)
    print(f"{seg:<12}" + "".join(f"{c:>15,.1f}%" for c in cells))

with open(CLEAN / "r11_cost_per_day.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
print("\nwrote r11_cost_per_day.csv")
