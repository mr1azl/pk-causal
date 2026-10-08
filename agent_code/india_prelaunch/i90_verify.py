"""Verification pass: re-derive every headline number in FINDINGS_india.md from
the clean CSVs independently of the scripts that produced them, and fail loudly
on any disagreement."""
import csv, json, glob, collections
from lib_sa360 import CLEAN, RAW, in_dest_group, is_non_brand

ok, bad = [], []
def check(label, got, want, tol=0.02):
    good = (abs(got - want) <= tol * max(abs(want), 1e-9)) if isinstance(want, float) \
           else got == want
    (ok if good else bad).append(f"{label}: got {got}, expected {want}")

rd = lambda f: list(csv.DictReader(open(CLEAN / f, encoding="utf-8")))

g = rd("i0_group_spend.csv")
tot = sum(float(r["cost_12w"]) for r in g)
check("12w non-brand spend", round(tot), 251592)
na = [r for r in g if r["dest_group"] == "North America"][0]
check("North America share", float(na["share_pct"]), 42.34)
check("North America enabled", int(na["enabled"]), 288)

inf = rd("i2_inflation_by_group.csv")
srch = [r for r in inf if "Performance Max" not in r["dest_group"]]
L = sum(int(r["ledger_rows"]) for r in srch)
A = sum(float(r["all_conversions"]) for r in srch)
X = sum(float(r["cross_device"]) for r in srch)
check("search ledger rows", L, 140)
check("search all_conversions", round(A), 1022)
check("inflation ratio", round(A / L, 2), 7.30)
check("same-device over ledger", round((A - X) / L, 2), 1.10)
lrev = sum(float(r["ledger_revenue"]) for r in srch)
arev = sum(float(r["all_conversions_value"]) for r in srch)
check("revenue inflation", round(arev / lrev, 1), 10.1)
pm = [r for r in inf if "Performance Max" in r["dest_group"]][0]
check("pmax ledger rows", int(pm["ledger_rows"]), 103)
check("pmax share of all bookings", round(int(pm["ledger_rows"]) / (L + int(pm["ledger_rows"])) * 100), 42)

cal = rd("i3_calibration_by_group.csv")
uk = [r for r in cal if r["dest_group"] == "UK+IE"][0]
check("UK+IE vs median ledger", float(uk["vs_median_ledger"]), 1.44)
check("UK+IE vs median attributed", float(uk["vs_median_attributed"]), 1.35)
check("UK+IE flagged both", uk["flag_ledger"] + uk["flag_attributed"], "yesyes")
flagged_both = [r["dest_group"] for r in cal
                if r["flag_ledger"] == "yes" and r["flag_attributed"] == "yes"]
check("only UK+IE flagged on both", flagged_both, ["UK+IE"])

dst = rd("i3_calibration_by_destination.csv")
nb = [r for r in dst if r["no_bookings_in_window"] == "yes"]
check("top30 with no bookings", len(nb), 11)
check("their clicks", sum(int(r["clicks"]) for r in nb), 108734)
check("their cost", round(sum(float(r["cost"]) for r in nb)), 27519)

rm = rd("i3_route_match_by_group.csv")
nam = [r for r in rm if r["dest_group"] == "North America"][0]
check("North America reverse direction", float(nam["reverse_direction_pct"]), 17.7)
ukm = [r for r in rm if r["dest_group"] == "UK+IE"][0]
check("UK+IE reverse direction", float(ukm["reverse_direction_pct"]), 14.9)

bud = rd("i4_shared_budgets.csv")
check("budgets carrying enabled campaigns", len(bud), 10)
check("enabled campaigns on them", sum(int(r["enabled_campaigns"]) for r in bud), 1021)
daily = sum(float(r["daily_amount"]) for r in bud)
spend = sum(float(r["spend_per_day"]) for r in bud)
check("account utilisation", round(spend / daily * 100, 1), 104.4)
check("budgets over 100pct", sum(1 for r in bud if float(r["utilisation_pct"]) > 100), 5)

hd = rd("i4_headroom_by_campaign.csv")
elig = [r for r in hd if r["rank_lost"] != "" and float(r["cost_4w"]) >= 100]
below = [r for r in elig if float(r["rank_lost"]) < 21.7]
check("campaigns below PK rank lost", len(below), 64)
check("their 4w spend", round(sum(float(r["cost_4w"]) for r in below)), 32158)
check("share of eligible spend", round(sum(float(r["cost_4w"]) for r in below) /
                                       sum(float(r["cost_4w"]) for r in elig) * 100), 46)

rev = rd("i5_reverse_direction_check.csv")
check("destination campaigns checked", len(rev), 1021)
check("with a reverse negative", sum(1 for r in rev
                                     if r["has_reverse_direction_negative"] == "yes"), 0)
check("with no negative at all", sum(1 for r in rev if int(r["negatives_on_campaign"]) == 0), 986)

pf = rd("i6_portfolios.csv")
check("portfolios", len(pf), 10)
check("all maximize conversions", {r["type"] for r in pf}, {"MAXIMIZE_CONVERSIONS"})
check("none with a target", {r["target_cpa"] for r in pf} | {r["target_roas"]for r in pf}, {"NOT SET"})

gr = rd("i7_guardrails.csv")
check("groups with usable ledger guardrail", sum(1 for r in gr if r["usable"] == "yes"), 3)
gcc = [r for r in gr if r["dest_group"] == "GCC and Middle East"][0]
check("GCC ledger bookings", int(gcc["ledger_bookings_8w"]), 5)
check("GCC clicks", int(gcc["clicks_8w"]), 169236)

ro = rd("i8_target_roas.csv")
allr = [r for r in ro if r["dest_group"] == "ALL"][0]
check("account ROAS on VBB", float(allr["roas_on_vbb_search_value"]), 38.2)
check("account ROAS on ledger", float(allr["roas_on_ledger_revenue"]), 0.83)

fb = rd("i3_fallback_by_group.csv")
check("zero-valued rows anywhere", {float(r["zero_pct"]) for r in fb}, {0.0})
worst = max(fb, key=lambda r: float(r["fallback_share_of_value_pct"]))
check("worst group fallback share of value under 3.2pct",
      float(worst["fallback_share_of_value_pct"]) < 3.2, True)

# privacy sweep over everything that was written
import re
pat = re.compile(r"GA1\.|gclid|refresh_token|client_secret|Bearer ", re.I)
hits = []
for p in glob.glob(str(RAW / "*")) + glob.glob(str(CLEAN / "*")):
    try:
        t = open(p, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue
    if pat.search(t):
        hits.append(p.split("/")[-1])
check("no identifiers or credentials in raw or clean", hits, [])

print(f"{len(ok)} checks passed")
for b in bad:
    print("  FAIL  " + b)
print("ALL CHECKS PASSED" if not bad else f"\n{len(bad)} FAILURES")
