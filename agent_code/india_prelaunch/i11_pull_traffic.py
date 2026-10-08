"""I1a: daily campaign traffic plus auction share metrics for the India non-brand
account, 12 weeks to yesterday. Resumable: one JSONL per month chunk, skipped if
it already exists, so the 180s shell limit never costs a completed chunk.

Impressions are kept so the 10.0 and 90.0 reporting clamps can be weighted and
flagged rather than averaged blind.
"""
import json, os, sys
from lib_sa360 import stream, chunks, RAW, IN_ACCOUNT

D1, D2 = sys.argv[1], sys.argv[2]
SHARES = ["search_impression_share", "search_top_impression_share",
          "search_budget_lost_impression_share", "search_rank_lost_impression_share"]
Q = ("SELECT segments.date, campaign.id, campaign.name, campaign.status, "
     "metrics.cost_micros, metrics.clicks, metrics.impressions, "
     + ", ".join(f"metrics.{f}" for f in SHARES) +
     " FROM campaign WHERE segments.date BETWEEN '{d1}' AND '{d2}' "
     "AND metrics.impressions > 0")

for d1, d2 in chunks(D1, D2, 31):
    path = RAW / f"i1_traffic_{d1}_{d2}.jsonl"
    if path.exists():
        print(f"   skip {path.name} ({sum(1 for _ in open(path, encoding='utf-8')):,d} rows)")
        continue
    c, rows = stream(IN_ACCOUNT, Q.format(d1=d1, d2=d2))
    if c != 200:
        sys.exit(f"FAILED {d1}..{d2}: {c} {rows}")
    with open(path, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, separators=(",", ":")) + "\n")
    print(f"   {path.name}: {len(rows):,d} rows")
print("traffic pull complete")
