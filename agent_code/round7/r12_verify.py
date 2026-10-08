"""Verification: re-derive every headline number in FINDINGS_round7.md from the
clean tables, independently of the scripts that produced them."""
import csv, json, glob, collections
from lib_gads import CLEAN, RAW

ok, bad = [], []
def check(label, got, want, tol=0.02):
    good = (abs(got - want) <= tol * max(abs(want), 1e-9)) if isinstance(want, float) else got == want
    (ok if good else bad).append(f"{label}: got {got}, expected {want}")

rd = lambda f: list(csv.DictReader(open(CLEAN / f, encoding="utf-8")))

t = rd("r10_pk_terms_by_segment_period.csv")
g = lambda s, p: next(x for x in t if x["segment"] == s and x["period"] == p)
D = {"13 Jun-19 Aug": 68, "20 Aug-1 Sep": 13, "2-19 Sep": 18, "20 Sep-5 Oct": 16}

for seg, p, want in [("UK+IE", "13 Jun-19 Aug", 1.040), ("UK+IE", "20 Sep-5 Oct", 0.417),
                     ("long-haul", "13 Jun-19 Aug", 0.238), ("regional", "13 Jun-19 Aug", 0.173),
                     ("long-haul", "20 Sep-5 Oct", 0.456), ("regional", "20 Sep-5 Oct", 0.336)]:
    r = g(seg, p)
    check(f"CPC {seg} {p}", round(float(r["cost"]) / int(r["clicks"]), 3), want)

for seg, want_base, want_end, want_ch in [("UK+IE", 250, 37, -85), ("long-haul", 125, 144, 15),
                                          ("regional", 132, 150, 14)]:
    b = float(g(seg, "13 Jun-19 Aug")["cost"]) / 68
    e = float(g(seg, "20 Sep-5 Oct")["cost"]) / 16
    check(f"spend/day {seg} baseline", round(b), want_base)
    check(f"spend/day {seg} after cap", round(e), want_end)
    check(f"spend/day {seg} change pct", round((e / b - 1) * 100), want_ch)

for p, want in [("13 Jun-19 Aug", 136), ("2-19 Sep", 63), ("20 Sep-5 Oct", 153)]:
    check(f"UK terms/day {p}", round(int(g("UK+IE", p)["distinct_terms"]) / D[p]), want)

rows = [json.loads(l) for l in open(RAW / "r2_change_status.jsonl", encoding="utf-8")]
day = lambda d: [x["changeStatus"] for x in rows
                 if (x["changeStatus"].get("lastChangeDateTime") or "")[:10] == d]
check("change_status rows total", len(rows), 77121)
check("20 Aug changes", len(day("2026-08-20")), 5043)
check("2 Sep changes", len(day("2026-09-02")), 774)
check("3 Sep changes", len(day("2026-09-03")), 5397)
c = collections.Counter(x.get("resourceType") for x in day("2026-09-03"))
check("3 Sep ad group criteria", c["AD_GROUP_CRITERION"], 3300)
check("3 Sep campaign shared sets", c["CAMPAIGN_SHARED_SET"], 974)
st = collections.Counter(x.get("resourceStatus") for x in day("2026-09-03")
                         if x.get("resourceType") == "CAMPAIGN_SHARED_SET")
check("3 Sep shared sets removed", st["REMOVED"], 487)
check("3 Sep shared sets added", st["ADDED"], 487)
stc = collections.Counter(x.get("resourceStatus") for x in day("2026-09-03")
                          if x.get("resourceType") == "AD_GROUP_CRITERION")
check("3 Sep criteria all CHANGED", set(stc), {"CHANGED"})

ev = [json.loads(l) for l in open(RAW / "r2_change_event.jsonl", encoding="utf-8")]
bud_days = {(x["changeEvent"].get("changeDateTime") or "")[:10] for x in ev
            if x["changeEvent"].get("changeResourceType") == "CAMPAIGN_BUDGET"}
check("days with a budget update", len(bud_days), 24)
users = {x["changeEvent"].get("user_hash") for x in ev}
check("distinct users", len(users), 4)
check("no raw email survives", any("@" in str(x["changeEvent"].get("user_hash", "")) for x in ev), False)

ind = rd("r7_india_shared_sets.csv")
check("India criteria on attached lists", len(ind), 28469)
# 12 lists are attached; one of them, "Ad Hoc Super MCC", has zero members, so
# only 11 contribute criteria. Both numbers are true and the findings say so.
check("India attached lists with criteria", len({r["shared_set_id"] for r in ind}), 11)
rev = {r["keyword"].lower() for r in ind if r["is_reverse_direction"] == "yes"}
check("India reverse direction negatives", len(rev), 48)

unb = rd("r8_unblocked_reverse_terms.csv")
check("India unblocked reverse terms", len(unb), 865)
check("India unblocked spend", round(sum(float(r["cost_4w"]) for r in unb)), 3717)

sets_ = rd("r4_shared_sets.csv")
check("PK shared sets", len(sets_), 42)
cont = rd("r6_shared_set_contents.csv")
check("PK criteria across live sets", len(cont), 67543)
check("PK reverse direction criteria", sum(1 for r in cont if r["is_reverse_direction"] == "yes"), 566)

import re
pat = re.compile(r"refresh_token|client_secret|developer-token|Bearer |@[a-z0-9.-]+\.(com|net|org)", re.I)
hits = [p.split("/")[-1] for p in glob.glob(str(RAW / "*")) + glob.glob(str(CLEAN / "*"))
        if pat.search(open(p, encoding="utf-8", errors="ignore").read())]
check("no credentials or emails in output", hits, [])

print(f"{len(ok)} checks passed")
for b in bad:
    print("  FAIL  " + b)
print("ALL CHECKS PASSED" if not bad else f"\n{len(bad)} FAILURES")
