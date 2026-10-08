"""R10: what PK's UK campaigns were actually matching, before and after 2 Sep.

492,946 search term rows, 13 Jun to 5 Oct, split by the four periods used in
rounds 3 to 6 and by the same segments, so this sits directly alongside the
earlier tables.

Three tests:
  1 did the queries UK campaigns bought change character at the switch
  2 is the reverse direction, searches for a flight TO Pakistan, bigger on UK
  3 did the concentration of spend move, which is how de-concentration showed
    up on the keyword side in round 3
"""
import csv, json, glob, collections, re
from lib_gads import RAW, CLEAN, PERIODS
from lib_sa360 import segment, is_non_brand

rows = []
for p in sorted(glob.glob(str(RAW / "r9_pk_terms_*.jsonl"))):
    for line in open(p, encoding="utf-8"):
        rows.append(json.loads(line))
rows = [r for r in rows if is_non_brand(r["campaign"].get("name"))]
print(f"{len(rows):,d} PK search term rows, non-brand")

PK_PLACES = ["pakistan", "karachi", "lahore", "islamabad", "peshawar", "multan",
             "faisalabad", "sialkot", "quetta", "rawalpindi", "khi", "lhe", "isb"]
PAIR = re.compile(r"\b([a-z][a-z\s]{1,24}?)\s+to\s+([a-z][a-z\s]{1,24}?)\b"
                  r"(?:\s+(?:flight|flights|ticket|tickets|fare|fares|airfare|business|"
                  r"first|cheap|price|deal|deals|booking)\b|$)")
TO_PK = re.compile(r"\bto\s+(" + "|".join(PK_PLACES) + r")\b")
FROM_PK = re.compile(r"\bfrom\s+(" + "|".join(PK_PLACES) + r")\b")
GENERIC = re.compile(r"^(cheap\s+)?(flight|flights|air\s?ticket|airline|ticket|tickets|"
                     r"book\s+flight|flight\s+booking|air\s+ticket)s?\b")


def direction(t):
    m = PAIR.search(t)
    if m:
        o, d = m.group(1).strip(), m.group(2).strip()
        o_pk = any(p == o or o.endswith(" " + p) for p in PK_PLACES)
        d_pk = any(p == d or d.endswith(" " + p) for p in PK_PLACES)
        if d_pk and not o_pk:
            return "reverse"
        if o_pk and not d_pk:
            return "outbound"
        if o_pk and d_pk:
            return "domestic"
        return "outbound"
    if FROM_PK.search(t):
        return "outbound"
    if TO_PK.search(t):
        return "reverse"
    return "outbound"


def period(d):
    for lab, a, b in PERIODS:
        if a <= d <= b:
            return lab
    return None


A = collections.defaultdict(lambda: collections.Counter())
terms = collections.defaultdict(collections.Counter)
for r in rows:
    d = r["segments"]["date"]
    per = period(d)
    if not per:
        continue
    seg = segment(r["campaign"]["name"])
    if seg in ("GB country (cut 20 Aug)", "UK+IE rest"):
        seg = "UK+IE"
    t = (r["searchTermView"].get("searchTerm") or "").lower()
    m = r["metrics"]
    cost = int(m.get("costMicros", 0)) / 1e6
    a = A[(seg, per)]
    a["cost"] += cost; a["clicks"] += int(m.get("clicks", 0)); a["rows"] += 1
    a["conv"] += float(m.get("conversions", 0) or 0)
    a[direction(t)] += cost
    if GENERIC.match(t):
        a["generic"] += cost
    a["mt_" + str(r["segments"].get("searchTermMatchType"))] += cost
    terms[(seg, per)][t] += cost

SEGS = ["UK+IE", "long-haul", "regional"]
print("\n=== PK search terms by segment and period ===")
print(f"{'segment':<12}{'period':<16}{'cost':>9}{'terms':>8}{'reverse':>9}{'%':>6}"
      f"{'generic':>9}{'%':>6}{'top200 share':>14}")
print("-" * 92)
out = []
for seg in SEGS:
    for lab, _, _ in PERIODS:
        a = A.get((seg, lab))
        if not a or a["cost"] < 1:
            continue
        tt = terms[(seg, lab)]
        top = sum(c for _, c in tt.most_common(200))
        print(f"{seg:<12}{lab:<16}{a['cost']:>9,.0f}{len(tt):>8,d}"
              f"{a['reverse']:>9,.0f}{a['reverse']/a['cost']*100:>5.1f}%"
              f"{a['generic']:>9,.0f}{a['generic']/a['cost']*100:>5.1f}%"
              f"{top/a['cost']*100:>13.1f}%")
        out.append({"segment": seg, "period": lab, "cost": round(a["cost"], 2),
                    "clicks": int(a["clicks"]), "distinct_terms": len(tt),
                    "reverse_cost": round(a["reverse"], 2),
                    "reverse_pct": round(a["reverse"] / a["cost"] * 100, 2),
                    "generic_cost": round(a["generic"], 2),
                    "generic_pct": round(a["generic"] / a["cost"] * 100, 2),
                    "top200_share_pct": round(top / a["cost"] * 100, 2),
                    "conversions": round(a["conv"], 1)})
    print()

with open(CLEAN / "r10_pk_terms_by_segment_period.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

print("=== match type of the query served, UK+IE, by period ===")
for lab, _, _ in PERIODS:
    a = A.get(("UK+IE", lab))
    if not a or a["cost"] < 1:
        continue
    mts = {k[3:]: v for k, v in a.items() if k.startswith("mt_")}
    tot = sum(mts.values()) or 1
    print(f"   {lab:<16} " + ", ".join(f"{k} {v/tot*100:.0f}%"
          for k, v in sorted(mts.items(), key=lambda x: -x[1])))

print("\n=== what UK+IE bought, top 12 terms by cost, before and after ===")
for lab in ("13 Jun-19 Aug", "2-19 Sep", "20 Sep-5 Oct"):
    tt = terms.get(("UK+IE", lab))
    if not tt:
        continue
    print(f"\n   --- {lab} ---")
    for t, c in tt.most_common(12):
        print(f"      {c:>8,.0f}  {t[:62]}")

with open(CLEAN / "r10_uk_top_terms.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["period", "search_term", "cost"])
    for lab, _, _ in PERIODS:
        for t, c in terms.get(("UK+IE", lab), {}).most_common(300):
            w.writerow([lab, t, round(c, 2)])
print("\nwrote r10_pk_terms_by_segment_period.csv and r10_uk_top_terms.csv")
