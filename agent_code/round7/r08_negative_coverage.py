"""R8: do the India shared lists actually block the reverse direction traffic
that was bought? 908 campaigns are covered by a list containing a "to india"
term, so the bare claim "no directional negative" was wrong. The question that
matters is whether those terms cover the queries that actually spent money.
"""
import csv, re, collections
from lib_gads import CLEAN
from pathlib import Path

IND = Path(__file__).resolve().parents[3] / "vbb_india_prelaunch/data/clean"
neg = list(csv.DictReader(open(CLEAN / "r7_india_shared_sets.csv", encoding="utf-8")))
spent = list(csv.DictReader(open(IND / "g4_reverse_terms.csv", encoding="utf-8")))
spent = [r for r in spent if r["bucket"] == "reverse"]
print(f"{len(neg):,d} negatives across the 12 attached lists, "
      f"{len(spent):,d} reverse direction terms that actually spent")

EX = {r["keyword"].lower().strip() for r in neg if r["match_type"] == "EXACT"}
PH = [r["keyword"].lower().strip() for r in neg if r["match_type"] == "PHRASE"]
BR = [set(r["keyword"].lower().split()) for r in neg if r["match_type"] == "BROAD"]
print(f"   exact {len(EX):,d}, phrase {len(PH):,d}, broad {len(BR):,d}")


def blocked(term):
    t = term.lower().strip()
    if t in EX:
        return "exact"
    for p in PH:
        if p and p in t:
            return "phrase"
    tw = set(t.split())
    for b in BR:
        if b and b <= tw:
            return "broad"
    return None


tot = blk = 0.0
reasons = collections.Counter()
unblocked = []
for r in spent:
    c = float(r["cost"]); tot += c
    why = blocked(r["search_term"])
    if why:
        blk += c; reasons[why] += c
    else:
        unblocked.append((r["search_term"], c))

print(f"\n=== would the attached lists have blocked the spend? ===")
print(f"reverse direction spend measured: {tot:,.0f} USD over 4 weeks")
print(f"blocked by an attached negative:  {blk:,.0f} USD ({blk/tot*100:.1f}%)")
print(f"NOT blocked:                      {tot-blk:,.0f} USD ({(tot-blk)/tot*100:.1f}%)")
if reasons:
    print("   by match type:", dict(reasons.most_common()))

print(f"\ntop 20 reverse direction terms no attached list blocks:")
for t, c in sorted(unblocked, key=lambda x: -x[1])[:20]:
    print(f"   {c:>8,.0f}  {t[:64]}")

with open(CLEAN / "r8_unblocked_reverse_terms.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["search_term", "cost_4w"])
    for t, c in sorted(unblocked, key=lambda x: -x[1]):
        w.writerow([t, round(c, 2)])
print(f"\nwrote r8_unblocked_reverse_terms.csv, {len(unblocked):,d} terms")
