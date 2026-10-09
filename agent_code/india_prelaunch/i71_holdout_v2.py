"""I7a, second pass. Two corrections to i70.

1. Budget maps one to one onto portfolio: each of the 10 budgets carries exactly
   one portfolio. So a holdout drawn at portfolio level is automatically budget
   separated, and a holdout drawn inside a portfolio is not, because 7 of the 10
   budgets span more than one destination group.
2. The nearest to the mean selection in i70 was wrong. It picked whichever single
   campaign sat closest to the group mean regardless of size, so North America
   held out one campaign carrying 67 percent of the group's spend. Selection now
   excludes any campaign larger than 40 percent of its group and stops as soon as
   the running total is within 15 to 30 percent.

Both designs are produced, because they trade off against each other and the
choice is the client's:
  A  portfolio level, clean inference, no per group balance
  B  campaign level stratified by destination group, balanced, but needs the
     budget split or the arms contend for the same money
"""
import csv, json, glob, collections, statistics
from lib_sa360 import RAW, CLEAN, in_dest_group

D1, D2 = "2026-08-13", "2026-10-07"
inv = {r["campaign_id"]: r for r in csv.DictReader(
    open(CLEAN / "i0_campaign_inventory.csv", encoding="utf-8"))}
pf_name = {r["portfolio_id"]: r["name"] for r in csv.DictReader(
    open(CLEAN / "i6_portfolios.csv", encoding="utf-8"))}

A = collections.defaultdict(lambda: collections.Counter())
for p in sorted(glob.glob(str(RAW / "i1_traffic_2026-*.jsonl"))):
    for line in open(p, encoding="utf-8"):
        r = json.loads(line)
        if not (D1 <= r["segments"]["date"] <= D2):
            continue
        cid = r["campaign"]["id"]
        if cid not in inv or inv[cid]["status"] != "ENABLED":
            continue
        m = r.get("metrics", {})
        A[cid]["cost"] += int(m.get("costMicros", 0)) / 1e6
        A[cid]["clicks"] += int(m.get("clicks", 0))
for p in sorted(glob.glob(str(RAW / "i1_conv_2026-*.jsonl"))):
    for line in open(p, encoding="utf-8"):
        r = json.loads(line)
        if not (D1 <= r["segments"]["date"] <= D2) \
           or r["segments"]["conversionActionName"] != "QR_Booking":
            continue
        if r["campaign"]["id"] in A:
            A[r["campaign"]["id"]]["bk"] += float(r.get("metrics", {}).get("allConversions", 0))

cand = []
for cid, a in A.items():
    if a["clicks"] < 200 or a["cost"] < 50:
        continue
    nm = inv[cid]["name"]
    cand.append({"campaign_id": cid, "name": nm, "dest_group": in_dest_group(nm),
                 "portfolio_id": (inv[cid]["bidding_strategy"] or "").rsplit("/", 1)[-1],
                 "budget_id": (inv[cid]["campaign_budget"] or "").rsplit("/", 1)[-1],
                 "cost_8w": round(a["cost"], 2), "clicks_8w": int(a["clicks"]),
                 "cpc": round(a["cost"] / a["clicks"], 4),
                 "bookings_8w": round(a["bk"], 1),
                 "bk_per_1k_clicks": round(a["bk"] / a["clicks"] * 1000, 3)})
TOT = sum(c["cost_8w"] for c in cand)

print("=== design A: hold out whole portfolios, which are whole budgets ===")
P = collections.defaultdict(list)
for c in cand:
    P[c["portfolio_id"]].append(c)
print(f"{'portfolio':<36}{'camps':>7}{'spend 8w':>11}{'share':>7}{'CPC':>7}{'bk/1k':>7}  top groups")
print("-" * 105)
prows = []
for pid, cs in sorted(P.items(), key=lambda kv: -sum(c["cost_8w"] for c in kv[1])):
    s = sum(c["cost_8w"] for c in cs); cl = sum(c["clicks_8w"] for c in cs)
    bk = sum(c["bookings_8w"] for c in cs)
    g = collections.Counter()
    for c in cs:
        g[c["dest_group"]] += c["cost_8w"]
    mix = ", ".join(f"{k.split()[0]} {v/s*100:.0f}%" for k, v in g.most_common(3))
    print(f"{pf_name.get(pid,pid)[:34]:<36}{len(cs):>7,d}{s:>11,.0f}{s/TOT*100:>6.1f}%"
          f"{s/cl:>7.3f}{bk/cl*1000:>7.2f}  {mix}")
    prows.append({"portfolio_id": pid, "portfolio": pf_name.get(pid, pid), "campaigns": len(cs),
                  "spend_8w": round(s, 2), "share_of_spend_pct": round(s / TOT * 100, 2),
                  "cpc": round(s / cl, 4), "bk_per_1k_clicks": round(bk / cl * 1000, 3),
                  "group_mix": mix})
with open(CLEAN / "i7_portfolio_profile.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(prows[0].keys())); w.writeheader(); w.writerows(prows)

print("\n=== design B: campaign level, stratified by destination group ===")
G = collections.defaultdict(list)
for c in cand:
    G[c["dest_group"]].append(c)
hold = []
print(f"{'group':<26}{'camps':>7}{'held':>6}{'spend held':>12}{'share':>7}{'excluded as too big':>21}")
print("-" * 80)
for g, cs in sorted(G.items(), key=lambda kv: -sum(c["cost_8w"] for c in kv[1])):
    tot = sum(c["cost_8w"] for c in cs)
    if tot <= 0 or len(cs) < 4:
        for c in cs:
            c["arm"] = "treated (group too small to split)"
        hold += cs; continue
    big = [c for c in cs if c["cost_8w"] > 0.40 * tot]
    pool = [c for c in cs if c not in big]
    mcpc = sum(c["cpc"] * c["cost_8w"] for c in cs) / tot
    mbk = sum(c["bk_per_1k_clicks"] * c["cost_8w"] for c in cs) / tot
    scpc = statistics.pstdev([c["cpc"] for c in cs]) or 1
    sbk = statistics.pstdev([c["bk_per_1k_clicks"] for c in cs]) or 1
    for c in pool:
        c["dist"] = (((c["cpc"] - mcpc) / scpc) ** 2 + ((c["bk_per_1k_clicks"] - mbk) / sbk) ** 2) ** 0.5
    picked, acc = [], 0.0
    for c in sorted(pool, key=lambda x: x["dist"]):
        if acc >= 0.15 * tot:
            break
        if acc + c["cost_8w"] > 0.30 * tot and acc > 0.10 * tot:
            continue
        picked.append(c); acc += c["cost_8w"]
    for c in picked:
        c["arm"] = "holdout"
    for c in cs:
        c.setdefault("arm", "treated")
    hold += cs
    print(f"{g:<26}{len(cs):>7,d}{len(picked):>6,d}{acc:>12,.0f}{acc/tot*100:>6.1f}%{len(big):>21,d}")

print(f"\n=== design B match quality ===")
print(f"{'group':<26}{'CPC hold':>10}{'CPC trt':>9}{'gap':>7}{'bk/1k hold':>12}"
      f"{'bk/1k trt':>11}{'gap':>7}{'budgets shared':>16}")
print("-" * 100)
qual = []
for g in sorted({c["dest_group"] for c in hold}):
    h = [c for c in hold if c["dest_group"] == g and c["arm"] == "holdout"]
    t = [c for c in hold if c["dest_group"] == g and c["arm"] == "treated"]
    if not h or not t:
        continue
    def wm(rows, key):
        s = sum(r["cost_8w"] for r in rows)
        return sum(r[key] * r["cost_8w"] for r in rows) / s if s else 0
    hc, tc = wm(h, "cpc"), wm(t, "cpc")
    hb, tb = wm(h, "bk_per_1k_clicks"), wm(t, "bk_per_1k_clicks")
    shared = len({c["budget_id"] for c in h} & {c["budget_id"] for c in t})
    print(f"{g:<26}{hc:>10.3f}{tc:>9.3f}{(hc/tc-1)*100:>6.0f}%{hb:>12.2f}{tb:>11.2f}"
          f"{((hb/tb-1)*100 if tb else 0):>6.0f}%{shared:>16,d}")
    qual.append({"dest_group": g, "holdout_campaigns": len(h), "treated_campaigns": len(t),
                 "holdout_spend_8w": round(sum(c["cost_8w"] for c in h), 2),
                 "treated_spend_8w": round(sum(c["cost_8w"] for c in t), 2),
                 "holdout_cpc": round(hc, 4), "treated_cpc": round(tc, 4),
                 "cpc_gap_pct": round((hc / tc - 1) * 100, 1),
                 "holdout_bk_per_1k": round(hb, 3), "treated_bk_per_1k": round(tb, 3),
                 "bk_gap_pct": round((hb / tb - 1) * 100, 1) if tb else "",
                 "budgets_shared_between_arms": shared})

with open(CLEAN / "i7_holdout_campaigns.csv", "w", newline="", encoding="utf-8") as fh:
    cols = ["campaign_id", "name", "dest_group", "arm", "budget_id", "portfolio_id",
            "cost_8w", "clicks_8w", "cpc", "bookings_8w", "bk_per_1k_clicks"]
    w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
    w.writeheader(); w.writerows(sorted(hold, key=lambda c: (c["dest_group"], c["arm"])))
with open(CLEAN / "i7_holdout_match_quality.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(qual[0].keys())); w.writeheader(); w.writerows(qual)
print("\nwrote i7_portfolio_profile.csv, i7_holdout_campaigns.csv, i7_holdout_match_quality.csv")
