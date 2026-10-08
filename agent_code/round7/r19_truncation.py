"""R19: how much does booking lag actually truncate an 8 week window?

I have cited lag twice as a reason my ratios were understated. R18 measured it.
This converts the measured lag distribution into the thing that matters: the
share of eventual bookings that a window of a given length has already seen.

Method: build the empirical cumulative lag distribution F(t) from the click to
conversion lags on QR_Booking. For a click on day d of a window ending at day N,
the share of its bookings already observed is F(N - d). Average over the window.
"""
import collections, csv, datetime, statistics
from lib_sa360 import stream
from lib_gads import CLEAN

MARKETS = [("PK", "4851538229"), ("IN", "4034062923"),
           ("CA", "4096344384"), ("DE", "3218295582")]
D1, D2 = "2026-08-13", "2026-10-05"


def ts(s):
    for f in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime((s or "")[:19], f)
        except Exception:
            pass
    return None


ALL = []
per = {}
for lab, acc in MARKETS:
    c, rows = stream(acc,
        "SELECT segments.conversion_action_name, conversion.conversion_date_time, "
        "conversion.conversion_visit_date_time FROM conversion "
        f"WHERE segments.date BETWEEN '{D1}' AND '{D2}' "
        "AND segments.conversion_action_name = 'QR_Booking'")
    if c != 200:
        print(f"{lab}: {rows}"); continue
    lags = []
    for r in rows:
        a = ts(r["conversion"].get("conversionVisitDateTime"))
        b = ts(r["conversion"].get("conversionDateTime"))
        if a and b and b >= a:
            lags.append((b - a).total_seconds() / 86400)
    per[lab] = lags; ALL += lags
print(f"{len(ALL):,d} bookings with a measurable click to booking lag, four markets")


def F(lags, t):
    return sum(1 for x in lags if x <= t) / len(lags) if lags else 0


print("\n=== cumulative share of bookings observed, by days since the click ===")
HZ = [0.04, 1, 2, 3, 5, 7, 10, 14, 21, 28, 35]
print(f"{'market':<7}" + "".join(f"{('1h' if h<1 else f'{h:g}d'):>7}" for h in HZ))
print("-" * (7 + 7 * len(HZ)))
rows_out = []
for lab in [m[0] for m in MARKETS] + ["ALL"]:
    lg = ALL if lab == "ALL" else per.get(lab, [])
    if len(lg) < 20:
        continue
    print(f"{lab:<7}" + "".join(f"{F(lg,h)*100:>6.0f}%" for h in HZ))
    rows_out.append({"market": lab, "n": len(lg),
                     **{("1h" if h < 1 else f"{h:g}d"): round(F(lg, h) * 100, 1) for h in HZ}})

with open(CLEAN / "r19_lag_curve.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows_out[0].keys())); w.writeheader(); w.writerows(rows_out)

print("\n=== completeness of a window of N days, ending today ===")
print("   share of the bookings that window will eventually hold which are already visible")
print(f"{'window':<12}{'completeness':>14}{'understatement':>17}")
print("-" * 45)
comp = []
for N in (7, 14, 21, 28, 35, 42, 54, 60, 90):
    # a click on day d has had (N - d) days to convert; average F over the window
    s = sum(F(ALL, N - d) for d in range(N)) / N
    print(f"{N:>4} days{'':<3}{s*100:>13.1f}%{(1-s)*100:>16.1f}%")
    comp.append({"window_days": N, "completeness_pct": round(s * 100, 2),
                 "understatement_pct": round((1 - s) * 100, 2)})
with open(CLEAN / "r19_window_completeness.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(comp[0].keys())); w.writeheader(); w.writerows(comp)

n54 = next(c for c in comp if c["window_days"] == 54)
n14 = next(c for c in comp if c["window_days"] == 14)
print(f"\nThe 54 day window used for the FSV work is {n54['completeness_pct']:.1f}% complete, "
      f"so it understates bookings by {n54['understatement_pct']:.1f}%.")
print(f"A 14 day post-cap read is {n14['completeness_pct']:.1f}% complete, "
      f"understating by {n14['understatement_pct']:.1f}%.")
print("\nwrote r19_lag_curve.csv and r19_window_completeness.csv")
