"""R15: are the FSV proxy values aligned with booking values?

The sales rows inside the VBB tag carry the real transaction value AND the OnD,
so for the first time search value and booking value can be compared on the same
key, by destination, without going through the campaign name.

Four questions:
  A do ML and non-ML differ on sales, or only on searches
  B what is the search value to booking value ratio, overall and by destination
  C which destinations are mispriced, and by how much
  D at journey level, does a user whose searches were valued highly actually book
"""
import csv, json, glob, collections, statistics
from lib_gads import RAW, CLEAN

rows = []
for p in sorted(glob.glob(str(RAW / "r14_*.jsonl"))):
    for line in open(p, encoding="utf-8"):
        rows.append(json.loads(line))
print(f"{len(rows):,d} VBB rows, 13 Aug to 5 Oct, PK and IN, both models")

T = collections.Counter((r["market"], r["model"], r["type"]) for r in rows)
print("\n=== row counts by market, model and type ===")
for k, v in sorted(T.items()):
    print(f"   {k[0]:<4}{k[1]:<6}{k[2]:<10}{v:>9,d}")

print("\n=== A. do the two models differ on sales, or only on searches ===")
print(f"{'market':<8}{'type':<9}{'model':<7}{'n':>8}{'mean':>10}{'median':>9}{'total':>13}")
print("-" * 66)
A = collections.defaultdict(list)
for r in rows:
    A[(r["market"], r["type"], r["model"])].append(r["rev"])
for k in sorted(A):
    v = A[k]
    if len(v) < 5:
        continue
    print(f"{k[0]:<8}{k[1]:<9}{k[2]:<7}{len(v):>8,d}{sum(v)/len(v):>10.2f}"
          f"{statistics.median(v):>9.2f}{sum(v):>13,.0f}")

for mkt in ("PK", "IN"):
    s_b = sum(A.get((mkt, "sales", "base"), [])); s_m = sum(A.get((mkt, "sales", "ml"), []))
    q_b = sum(A.get((mkt, "search", "base"), [])); q_m = sum(A.get((mkt, "search", "ml"), []))
    if s_b:
        print(f"\n   {mkt}: sales value ml/base = {s_m/s_b:.4f}  "
              f"({'identical' if abs(s_m/s_b - 1) < 0.001 else 'DIFFERENT'})")
    if q_b:
        print(f"   {mkt}: search value ml/base = {q_m/q_b:.4f}")

print("\n=== B. search value against booking value, same tag, same window ===")
out = []
for mkt in ("PK", "IN"):
    for model in ("base", "ml"):
        sea = [r for r in rows if r["market"] == mkt and r["model"] == model and r["type"] == "search"]
        sal = [r for r in rows if r["market"] == mkt and r["model"] == model and r["type"] == "sales"]
        if not sea or not sal:
            continue
        sv, bv = sum(r["rev"] for r in sea), sum(r["rev"] for r in sal)
        print(f"   {mkt} {model:<5}: {len(sea):>7,d} searches worth {sv:>12,.0f}, "
              f"{len(sal):>4,d} sales worth {bv:>11,.0f}  ->  search value is "
              f"{sv/bv:>6.2f}x the booking value it is meant to proxy")
        out.append({"market": mkt, "model": model, "searches": len(sea),
                    "search_value": round(sv, 2), "sales": len(sal),
                    "sales_value": round(bv, 2),
                    "search_over_booking_value": round(sv / bv, 3),
                    "mean_search_value": round(sv / len(sea), 3),
                    "mean_sale_value": round(bv / len(sal), 2),
                    "implied_conversion_rate_pct": round(len(sal) / len(sea) * 100, 3)})
with open(CLEAN / "r15_fsv_overall.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

print("\n=== C. by destination, where the proxy is mispriced ===")
for mkt in ("PK", "IN"):
    D = collections.defaultdict(lambda: collections.Counter())
    for r in rows:
        if r["market"] != mkt or r["model"] != "base" or not r["dest"]:
            continue
        d = D[r["dest"].upper()]
        if r["type"] == "search":
            d["sn"] += 1; d["sv"] += r["rev"]
        elif r["type"] == "sales":
            d["bn"] += 1; d["bv"] += r["rev"]
    rank = [(k, v) for k, v in D.items() if v["bn"] >= 3 and v["sn"] >= 100]
    if not rank:
        print(f"\n   {mkt}: no destination has 3 or more sales and 100 or more searches")
        continue
    ratios = [v["sv"] / v["bv"] for _, v in rank]
    med = statistics.median(ratios)
    print(f"\n   --- {mkt}, {len(rank)} destinations with 3+ sales, median ratio {med:.2f} ---")
    print(f"   {'dest':<6}{'searches':>10}{'srch val':>11}{'sales':>7}{'sale val':>11}"
          f"{'ratio':>8}{'x median':>10}{'scale':>8}")
    rws = []
    for k, v in sorted(rank, key=lambda x: -(x[1]["sv"] / x[1]["bv"])):
        ra = v["sv"] / v["bv"]
        print(f"   {k:<6}{v['sn']:>10,.0f}{v['sv']:>11,.0f}{v['bn']:>7,.0f}{v['bv']:>11,.0f}"
              f"{ra:>8.2f}{ra/med:>10.2f}{med/ra:>8.2f}")
        rws.append({"market": mkt, "dest": k, "searches": int(v["sn"]),
                    "search_value": round(v["sv"], 2), "sales": int(v["bn"]),
                    "sales_value": round(v["bv"], 2), "ratio": round(ra, 3),
                    "vs_median": round(ra / med, 3), "scale_to_median": round(med / ra, 3),
                    "flag": "yes" if ra > 1.3 * med else "no"})
    with open(CLEAN / f"r15_fsv_by_dest_{mkt}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rws[0].keys())); w.writeheader(); w.writerows(rws)

print("\n=== D. journey level: do highly valued searchers actually book ===")
for mkt in ("PK", "IN"):
    J = collections.defaultdict(lambda: {"sv": 0.0, "sn": 0, "bv": 0.0, "bn": 0})
    for r in rows:
        if r["market"] != mkt or r["model"] != "base" or not r["journey"]:
            continue
        j = J[r["journey"]]
        if r["type"] == "search":
            j["sv"] += r["rev"]; j["sn"] += 1
        elif r["type"] == "sales":
            j["bv"] += r["rev"]; j["bn"] += 1
    booked = [v for v in J.values() if v["bn"]]
    nb = [v for v in J.values() if not v["bn"]]
    linked = [v for v in booked if v["sn"]]
    print(f"\n   {mkt}: {len(J):,d} journeys, {len(booked):,d} with a sale, "
          f"{len(linked):,d} of those also have searches in window")
    if nb and linked:
        print(f"      mean search value, journeys that booked:     "
              f"{sum(v['sv'] for v in linked)/len(linked):>8.2f}")
        print(f"      mean search value, journeys that did not:    "
              f"{sum(v['sv'] for v in nb)/len(nb):>8.2f}")
        r_ = (sum(v['sv'] for v in linked)/len(linked)) / (sum(v['sv'] for v in nb)/len(nb))
        print(f"      ratio: {r_:.2f}x  "
              f"({'the proxy does separate bookers' if r_ > 1.2 else 'THE PROXY DOES NOT SEPARATE BOOKERS'})")
print("\nwrote r15_fsv_overall.csv and r15_fsv_by_dest_*.csv")
