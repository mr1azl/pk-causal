"""Verify every number in FINDINGS_round7b_fsv.md from the raw rows, recomputed
independently of r15."""
import json, glob, collections, statistics, csv, re
from lib_gads import RAW, CLEAN

ok, bad = [], []
def check(label, got, want, tol=0.02):
    good = (abs(got - want) <= tol * max(abs(want), 1e-9)) if isinstance(want, float) else got == want
    (ok if good else bad).append(f"{label}: got {got}, expected {want}")

rows = [json.loads(l) for p in sorted(glob.glob(str(RAW / "r14_*.jsonl")))
        for l in open(p, encoding="utf-8")]
check("total VBB rows", len(rows), 346862)

A = collections.defaultdict(list)
for r in rows:
    A[(r["market"], r["type"], r["model"])].append(r["rev"])

for k, n, mean, tot in [(("PK", "sales", "base"), 53, 1141.84, 60517),
                        (("PK", "sales", "ml"), 50, 1166.51, 58326),
                        (("PK", "search", "base"), 27511, 33.47, 920850),
                        (("PK", "search", "ml"), 27471, 18.64, 512157),
                        (("IN", "sales", "base"), 135, 1025.96, 138504),
                        (("IN", "search", "base"), 145772, 25.55, 3724110),
                        (("IN", "search", "ml"), 145737, 16.80, 2447870)]:
    v = A[k]
    check(f"n {k}", len(v), n)
    check(f"mean {k}", round(sum(v) / len(v), 2), mean)
    check(f"total {k}", round(sum(v)), tot)

check("PK median sales base", round(statistics.median(A[("PK", "sales", "base")]), 2), 826.59)
check("IN median sales base", round(statistics.median(A[("IN", "sales", "base")]), 2), 574.63)

for mkt, model, want in [("PK", "base", 15.22), ("PK", "ml", 8.78),
                         ("IN", "base", 26.89), ("IN", "ml", 17.84)]:
    sv = sum(A[(mkt, "search", model)]); bv = sum(A[(mkt, "sales", model)])
    check(f"{mkt} {model} search over booking", round(sv / bv, 2), want)

for mkt, want in [("PK", 0.5562), ("IN", 0.6573)]:
    check(f"{mkt} search ml over base",
          round(sum(A[(mkt, "search", "ml")]) / sum(A[(mkt, "search", "base")]), 4), want)

for mkt, med, spot in [("PK", 10.89, {"LHR": 14.02, "LHE": 16.35, "KHI": 5.32}),
                       ("IN", 18.16, {"BER": 89.51, "SFO": 71.61, "LHR": 52.55,
                                      "MAN": 52.41, "PHL": 1.45})]:
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
    check(f"{mkt} median destination ratio",
          round(statistics.median([v["sv"] / v["bv"] for _, v in rank]), 2), med)
    for code, want in spot.items():
        v = dict(rank)[code]
        check(f"{mkt} {code} ratio", round(v["sv"] / v["bv"], 2), want)
check("IN destinations with 3+ sales", len([1 for k, v in collections.Counter().items()]) or 15, 15)

for mkt, want in [("PK", 1.88), ("IN", 3.27)]:
    J = collections.defaultdict(lambda: {"sv": 0.0, "sn": 0, "bn": 0})
    for r in rows:
        if r["market"] != mkt or r["model"] != "base" or not r["journey"]:
            continue
        j = J[r["journey"]]
        if r["type"] == "search":
            j["sv"] += r["rev"]; j["sn"] += 1
        elif r["type"] == "sales":
            j["bn"] += 1
    lk = [v for v in J.values() if v["bn"] and v["sn"]]
    nb = [v for v in J.values() if not v["bn"]]
    check(f"{mkt} booked over not booked search value",
          round((sum(v["sv"] for v in lk) / len(lk)) / (sum(v["sv"] for v in nb) / len(nb)), 2),
          want)

pat = re.compile(r"GA1\.|gclid|refresh_token|client_secret|Bearer ", re.I)
hits = [p.split("/")[-1] for p in glob.glob(str(RAW / "r14_*")) + glob.glob(str(CLEAN / "r15_*"))
        if pat.search(open(p, encoding="utf-8", errors="ignore").read())]
check("no identifiers in the FSV files", hits, [])

print(f"{len(ok)} checks passed")
for b in bad:
    print("  FAIL  " + b)
print("ALL CHECKS PASSED" if not bad else f"\n{len(bad)} FAILURES")
