"""R23: two things the four market table forces me to check.

1 The destination spread is measured on 4 destinations in PK and 33 in Germany.
  More destinations means more chance of an extreme, so comparing raw spreads
  across markets with different n is not a fair test. Bootstrap: draw 4
  destinations at random from each market, 2,000 times, and compare like with
  like.

2 The overall inflation ratio is (mean search value x searches) over
  (mean sale value x sales). If a market needs five times as many searches per
  booking, its ratio is five times higher for reasons that have nothing to do
  with the tag. Decompose it.
"""
import csv, json, glob, collections, random, statistics
from lib_gads import RAW, CLEAN

random.seed(7)
rows = [json.loads(l) for p in sorted(glob.glob(str(RAW / "r14_*.jsonl")))
        for l in open(p, encoding="utf-8")]

print("=== 2. decomposition of the inflation ratio ===")
print(f"{'market':<8}{'mean search':>13}{'mean sale':>11}{'value ratio':>13}"
      f"{'searches/sale':>15}{'inflation':>11}{'check':>9}")
print("-" * 82)
out = []
for mkt in ("PK", "IN", "CA", "DE"):
    s = [r["rev"] for r in rows if r["market"] == mkt and r["model"] == "base" and r["type"] == "search"]
    b = [r["rev"] for r in rows if r["market"] == mkt and r["model"] == "base" and r["type"] == "sales"]
    if not b:
        continue
    ms, mb = sum(s) / len(s), sum(b) / len(b)
    spb = len(s) / len(b)
    infl = sum(s) / sum(b)
    print(f"{mkt:<8}{ms:>13.2f}{mb:>11.2f}{ms/mb:>13.4f}{spb:>15.1f}{infl:>11.2f}"
          f"{(ms/mb)*spb:>9.2f}")
    out.append({"market": mkt, "mean_search_value": round(ms, 2),
                "mean_sale_value": round(mb, 2), "value_ratio": round(ms / mb, 5),
                "searches_per_sale": round(spb, 1),
                "search_to_sale_rate_pct": round(len(b) / len(s) * 100, 3),
                "inflation_ratio": round(infl, 2)})

print("\n   the inflation ratio is the value ratio times the number of searches per sale.")
pk = next(o for o in out if o["market"] == "PK"); ca = next(o for o in out if o["market"] == "CA")
print(f"   PK needs {pk['searches_per_sale']:.0f} searches per booking, "
      f"CA needs {ca['searches_per_sale']:.0f}, a factor of "
      f"{pk['searches_per_sale']/ca['searches_per_sale']:.1f}.")
print(f"   PK inflation is {pk['inflation_ratio']/ca['inflation_ratio']:.1f} times CA's.")
print(f"   The per search value ratio differs by only "
      f"{pk['value_ratio']/ca['value_ratio']:.2f} times.")

print("\n=== 1. destination spread, bootstrapped to 4 destinations each ===")
B = {}
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
    B[mkt] = [v["sv"] / v["bv"] for v in D.values() if v["bn"] >= 3 and v["sn"] >= 100]

K = min(len(v) for v in B.values())
print(f"   drawing {K} destinations at random, 2,000 times, from each market\n")
print(f"{'market':<8}{'pool':>6}{'median spread':>15}{'p25':>8}{'p75':>8}"
      f"{'P(spread >= PK median)':>24}")
print("-" * 70)
samples = {}
for mkt, pool in B.items():
    sp = []
    for _ in range(2000):
        pick = random.sample(pool, K)
        sp.append(max(pick) / min(pick))
    sp.sort(); samples[mkt] = sp
pk_med = statistics.median(samples["PK"])
for mkt in ("PK", "IN", "CA", "DE"):
    sp = samples[mkt]
    p = sum(1 for x in sp if x >= pk_med) / len(sp)
    print(f"{mkt:<8}{len(B[mkt]):>6}{statistics.median(sp):>15.1f}"
          f"{sp[len(sp)//4]:>8.1f}{sp[3*len(sp)//4]:>8.1f}{p*100:>23.0f}%")

with open(CLEAN / "r23_decomposition.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
with open(CLEAN / "r23_bootstrap_spread.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["market", "pool_size", "median_spread_k4", "p25", "p75"])
    for mkt in ("PK", "IN", "CA", "DE"):
        sp = samples[mkt]
        w.writerow([mkt, len(B[mkt]), round(statistics.median(sp), 2),
                    round(sp[len(sp)//4], 2), round(sp[3*len(sp)//4], 2)])
print("\nwrote r23_decomposition.csv and r23_bootstrap_spread.csv")
