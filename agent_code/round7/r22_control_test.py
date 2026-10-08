"""R22: falsification test of the round 7b conclusion.

Round 7b said the FSV proxy is badly calibrated and implied that this is part of
why PK went wrong. If Canada and Germany, which did not lose booking rate the way
PK did, are just as badly calibrated, then miscalibration cannot be the cause.

Four markets, same window, same method, read against the outcome measured in
round 6.
"""
import csv, json, glob, collections, statistics
from lib_gads import RAW, CLEAN

rows = [json.loads(l) for p in sorted(glob.glob(str(RAW / "r14_*.jsonl")))
        for l in open(p, encoding="utf-8")]
print(f"{len(rows):,d} VBB rows, four markets, 13 Aug to 5 Oct")

# round 6 outcome: bookings per 1k searches, 20 Sep-5 Oct against 13 Jun-19 Aug
OUTCOME = {"PK": -63, "IN": None, "CA": -26, "DE": None}

A = collections.defaultdict(list)
for r in rows:
    A[(r["market"], r["type"], r["model"])].append(r["rev"])

print("\n=== 1. overall proxy inflation: search value over booking value ===")
print(f"{'market':<8}{'searches':>10}{'search val':>13}{'sales':>7}{'sales val':>12}"
      f"{'base ratio':>12}{'ml ratio':>10}{'outcome':>10}")
print("-" * 84)
out = []
for mkt in ("PK", "IN", "CA", "DE"):
    sb, bb = sum(A[(mkt, "search", "base")]), sum(A[(mkt, "sales", "base")])
    sm, bm = sum(A[(mkt, "search", "ml")]), sum(A[(mkt, "sales", "ml")])
    ns, nb = len(A[(mkt, "search", "base")]), len(A[(mkt, "sales", "base")])
    if not bb:
        continue
    oc = OUTCOME.get(mkt)
    print(f"{mkt:<8}{ns:>10,d}{sb:>13,.0f}{nb:>7,d}{bb:>12,.0f}"
          f"{sb/bb:>12.2f}{(sm/bm if bm else 0):>10.2f}"
          f"{(f'{oc:+d}%' if oc is not None else 'n/a'):>10}")
    out.append({"market": mkt, "searches": ns, "search_value": round(sb, 2),
                "sales": nb, "sales_value": round(bb, 2),
                "ratio_base": round(sb / bb, 2),
                "ratio_ml": round(sm / bm, 2) if bm else "",
                "mean_search_value": round(sb / ns, 2),
                "mean_sale_value": round(bb / nb, 2),
                "booking_rate_vs_baseline_pct": oc if oc is not None else ""})

print("\n=== 2. destination spread, the axis a value bidder allocates on ===")
print(f"{'market':<8}{'dests':>7}{'median':>9}{'min':>9}{'max':>9}{'spread':>9}"
      f"{'p90/p10':>9}  worst three")
print("-" * 92)
for mkt in ("PK", "IN", "CA", "DE"):
    D = collections.defaultdict(lambda: collections.Counter())
    for r in rows:
        if r["market"] != mkt or r["model"] != "base" or not r["dest"]:
            continue
        d = D[r["dest"].upper()]
        if r["type"] == "search":
            d["sn"] += 1; d["sv"] += r["rev"]
        elif r["type"] == "sales":
            d["bn"] += 1; d["bv"] += r["rev"]
    rank = [(k, v["sv"] / v["bv"]) for k, v in D.items() if v["bn"] >= 3 and v["sn"] >= 100]
    if len(rank) < 3:
        print(f"{mkt:<8}{len(rank):>7}   too few destinations with 3+ sales")
        continue
    rs = sorted(r for _, r in rank)
    med = statistics.median(rs)
    p10 = rs[max(0, int(len(rs) * 0.10))]; p90 = rs[min(len(rs) - 1, int(len(rs) * 0.90))]
    worst = ", ".join(f"{k} {v/med:.1f}x" for k, v in
                      sorted(rank, key=lambda x: -x[1])[:3])
    print(f"{mkt:<8}{len(rank):>7}{med:>9.1f}{min(rs):>9.1f}{max(rs):>9.1f}"
          f"{max(rs)/min(rs):>8.0f}x{p90/p10:>8.1f}x  {worst}")
    for o in out:
        if o["market"] == mkt:
            o.update({"destinations_tested": len(rank), "median_ratio": round(med, 2),
                      "min_ratio": round(min(rs), 2), "max_ratio": round(max(rs), 2),
                      "spread_max_over_min": round(max(rs) / min(rs), 1),
                      "spread_p90_over_p10": round(p90 / p10, 2)})

with open(CLEAN / "r22_calibration_four_markets.csv", "w", newline="", encoding="utf-8") as fh:
    cols = sorted({k for o in out for k in o})
    w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
    w.writeheader(); w.writerows(out)

print("\n=== 3. does the ML discount differ by market ===")
for mkt in ("PK", "IN", "CA", "DE"):
    sb, sm = sum(A[(mkt, "search", "base")]), sum(A[(mkt, "search", "ml")])
    if sb:
        print(f"   {mkt}: ml search value is {sm/sb:.3f} of base")

print("\n=== 4. the test ===")
pk = next((o for o in out if o["market"] == "PK"), None)
ca = next((o for o in out if o["market"] == "CA"), None)
de = next((o for o in out if o["market"] == "DE"), None)
if pk and ca:
    print(f"   PK ratio {pk['ratio_base']:.1f}x, CA ratio {ca['ratio_base']:.1f}x"
          + (f", DE ratio {de['ratio_base']:.1f}x" if de else ""))
    print(f"   PK destination spread {pk.get('spread_p90_over_p10','n/a')}, "
          f"CA {ca.get('spread_p90_over_p10','n/a')}"
          + (f", DE {de.get('spread_p90_over_p10','n/a')}" if de else ""))
    print(f"\n   PK booking rate against baseline {pk['booking_rate_vs_baseline_pct']}%, "
          f"CA {ca['booking_rate_vs_baseline_pct']}%")
print("\nwrote r22_calibration_four_markets.csv")
