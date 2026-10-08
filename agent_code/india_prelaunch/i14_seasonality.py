"""I1d: same weeks of 2025 against 2026, so the launch weeks have a seasonal
baseline and a move after launch is not read as a season."""
import csv, collections
from lib_sa360 import CLEAN

rows = list(csv.DictReader(open(CLEAN / "i1_weekly_by_group.csv", encoding="utf-8")))
agg = collections.defaultdict(lambda: collections.Counter())
for r in rows:
    agg[(r["year"], r["dest_group"])] += collections.Counter(
        {k: float(r[k] or 0) for k in
         ["cost", "clicks", "qr_booking", "qr_booking_xdev", "booking_webpage",
          "flight_search", "vbb_value", "qr_booking_value"]})

groups = sorted({g for _, g in agg}, key=lambda g: -agg[("2026", g)]["cost"])
print(f"{'group':<28}{'clicks 25':>11}{'clicks 26':>11}{'CPC 25':>8}{'CPC 26':>8}"
      f"{'QRbk/1k 25':>12}{'QRbk/1k 26':>12}{'change':>9}")
print("-" * 99)
out = []
for g in groups:
    a, b = agg[("2025", g)], agg[("2026", g)]
    if not b["clicks"]:
        continue
    r25 = a["qr_booking"] / a["clicks"] * 1000 if a["clicks"] else 0
    r26 = b["qr_booking"] / b["clicks"] * 1000 if b["clicks"] else 0
    ch = (r26 / r25 - 1) * 100 if r25 else float("nan")
    print(f"{g:<28}{a['clicks']:>11,.0f}{b['clicks']:>11,.0f}"
          f"{(a['cost']/a['clicks'] if a['clicks'] else 0):>8.3f}{b['cost']/b['clicks']:>8.3f}"
          f"{r25:>12.2f}{r26:>12.2f}{ch:>8.0f}%")
    out.append({"dest_group": g, "clicks_2025": int(a["clicks"]), "clicks_2026": int(b["clicks"]),
                "cost_2025": round(a["cost"], 2), "cost_2026": round(b["cost"], 2),
                "cpc_2025": round(a["cost"] / a["clicks"], 4) if a["clicks"] else "",
                "cpc_2026": round(b["cost"] / b["clicks"], 4),
                "qr_booking_2025": round(a["qr_booking"], 1),
                "qr_booking_2026": round(b["qr_booking"], 1),
                "qr_bk_per_1k_2025": round(r25, 3), "qr_bk_per_1k_2026": round(r26, 3),
                "yoy_booking_rate_pct": round(ch, 1) if r25 else "",
                "xdev_pct_2025": round(a["qr_booking_xdev"] / a["qr_booking"] * 100, 1)
                                  if a["qr_booking"] else "",
                "xdev_pct_2026": round(b["qr_booking_xdev"] / b["qr_booking"] * 100, 1)
                                  if b["qr_booking"] else ""})

dest = CLEAN / "i1_yoy_by_group.csv"
with open(dest, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
print(f"\nwrote {dest.name}")
print("\ncross-device share of QR_Booking, 2025 against 2026:")
for r in out:
    print(f"   {r['dest_group']:<28} {str(r['xdev_pct_2025']):>6}%  ->  {str(r['xdev_pct_2026']):>6}%")
