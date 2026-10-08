"""I7b: guardrail table. Weekly QR_Booking bookings per 1,000 clicks over the
last 8 weeks, by destination group, with the mean and a one sided 90 percent
Poisson lower bound. A group below its bound for 2 consecutive weeks after
launch is flagged.

The bound is the exact Garwood lower limit, lambda_lo = 0.5 * chi2_q(0.10, 2k)
divided by the exposure in thousands of clicks. The chi square quantile is
inverted here with the regularised incomplete gamma function and a bisection,
so nothing has to be installed.

Both measures are reported. The ledger is what actually happened; the attributed
count is what a dashboard will show, and it runs about 7 times higher (I2), so a
guardrail written against one and watched on the other would never fire.
"""
import csv, json, glob, collections, datetime, math
from lib_sa360 import RAW, CLEAN, in_dest_group, is_non_brand

D1, D2 = "2026-08-13", "2026-10-07"


def gammainc_lower_reg(s, x, terms=2000):
    """Regularised lower incomplete gamma P(s, x), series expansion."""
    if x <= 0:
        return 0.0
    if x < s + 1:
        term = 1.0 / s; total = term
        for n in range(1, terms):
            term *= x / (s + n); total += term
            if term < total * 1e-14:
                break
        return total * math.exp(-x + s * math.log(x) - math.lgamma(s))
    # continued fraction for the upper tail, then complement
    tiny = 1e-300
    b = x + 1 - s; c = 1 / tiny; d = 1 / b; h = d
    for i in range(1, terms):
        an = -i * (i - s); b += 2
        d = an * d + b; d = tiny if abs(d) < tiny else d
        c = b + an / c; c = tiny if abs(c) < tiny else c
        d = 1 / d; de = d * c; h *= de
        if abs(de - 1) < 1e-14:
            break
    q = math.exp(-x + s * math.log(x) - math.lgamma(s)) * h
    return 1 - q


def chi2_q(p, df):
    """Quantile of chi square with df degrees of freedom, by bisection."""
    if df <= 0:
        return 0.0
    lo, hi = 0.0, max(10.0, df * 10.0)
    while gammainc_lower_reg(df / 2, hi / 2) < p:
        hi *= 2
    for _ in range(200):
        mid = (lo + hi) / 2
        if gammainc_lower_reg(df / 2, mid / 2) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def poisson_lower(k, exposure, conf=0.90):
    """One sided lower bound on the rate, Garwood. k events over `exposure`."""
    if exposure <= 0:
        return 0.0
    if k == 0:
        return 0.0
    return 0.5 * chi2_q(1 - conf, 2 * k) / exposure


def week(d):
    dt = datetime.date.fromisoformat(d)
    return (dt - datetime.timedelta(days=dt.weekday())).isoformat()


inv = {r["campaign_id"]: r["name"] for r in csv.DictReader(
    open(CLEAN / "i0_campaign_inventory.csv", encoding="utf-8"))}

clicks = collections.Counter()
for p in sorted(glob.glob(str(RAW / "i1_traffic_2026-*.jsonl"))):
    for line in open(p, encoding="utf-8"):
        r = json.loads(line); d = r["segments"]["date"]
        if not (D1 <= d <= D2):
            continue
        nm = inv.get(r["campaign"]["id"])
        if nm is None or not is_non_brand(nm):
            continue
        clicks[(in_dest_group(nm), week(d))] += int(r.get("metrics", {}).get("clicks", 0))

ledger = collections.Counter()
for p in sorted(glob.glob(str(RAW / "i2_ledger_*.jsonl"))):
    for line in open(p, encoding="utf-8"):
        c = json.loads(line); nm = c["campaign"].get("name")
        if not is_non_brand(nm):
            continue
        ledger[(in_dest_group(nm), week(c["segments"]["date"]))] += 1

attrib = collections.Counter()
for p in sorted(glob.glob(str(RAW / "i1_conv_2026-*.jsonl"))):
    for line in open(p, encoding="utf-8"):
        r = json.loads(line); s = r["segments"]
        if not (D1 <= s["date"] <= D2) or s["conversionActionName"] != "QR_Booking":
            continue
        nm = inv.get(r["campaign"]["id"])
        if nm is None or not is_non_brand(nm):
            continue
        attrib[(in_dest_group(nm), week(s["date"]))] += float(
            r.get("metrics", {}).get("allConversions", 0))

weeks = sorted({w for _, w in clicks})
groups = sorted({g for g, _ in clicks}, key=lambda g: -sum(
    clicks[(g, w)] for w in weeks))

out = []
print(f"=== weekly QR_Booking per 1,000 clicks, {D1} to {D2} ===\n")
for g in groups:
    cl = [clicks[(g, w)] for w in weeks]
    lk = [ledger[(g, w)] for w in weeks]
    ak = [attrib[(g, w)] for w in weeks]
    tot_cl = sum(cl)
    if tot_cl < 1000:
        continue
    exposure = tot_cl / 1000
    lmean = sum(lk) / exposure
    amean = sum(ak) / exposure
    llo = poisson_lower(sum(lk), exposure)
    alo = poisson_lower(int(round(sum(ak))), exposure)
    wr = [f"{(lk[i]/cl[i]*1000 if cl[i] else 0):.2f}" for i in range(len(weeks))]
    print(f"{g}")
    print(f"   clicks {tot_cl:>9,d}   ledger bookings {sum(lk):>4,d}   attributed {sum(ak):>7,.0f}")
    print(f"   ledger      mean {lmean:>6.2f} per 1k, 90% lower bound {llo:>6.2f}")
    print(f"   attributed  mean {amean:>6.2f} per 1k, 90% lower bound {alo:>6.2f}")
    print(f"   weekly ledger rate: {' '.join(wr)}")
    out.append({"dest_group": g, "weeks": len(weeks), "clicks_8w": tot_cl,
                "ledger_bookings_8w": sum(lk),
                "ledger_mean_per_1k": round(lmean, 3),
                "ledger_lower_bound_90pct": round(llo, 3),
                "attributed_bookings_8w": round(sum(ak), 1),
                "attributed_mean_per_1k": round(amean, 3),
                "attributed_lower_bound_90pct": round(alo, 3),
                "weekly_ledger_rates": " ".join(wr),
                "usable": "yes" if sum(lk) >= 10 else "no, under 10 bookings in 8 weeks"})

with open(CLEAN / "i7_guardrails.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

print("\n=== guardrail table to watch after launch ===")
print(f"{'group':<26}{'watch on ledger':>17}{'watch on attributed':>21}{'usable':>8}")
print("-" * 74)
for r in out:
    print(f"{r['dest_group']:<26}{r['ledger_lower_bound_90pct']:>17.2f}"
          f"{r['attributed_lower_bound_90pct']:>21.2f}"
          f"{('yes' if r['usable']=='yes' else 'no'):>8}")
print("\nwrote i7_guardrails.csv")
