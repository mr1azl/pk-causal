"""R9: PK search terms across the four periods. The UK zero, finally testable.

Rounds 3 and 4 eliminated geography, device, structure, settings, keywords,
audiences, bid modifiers, ads, landing pages, demographics and brand migration
as explanations for UK+IE bookings going to zero on 2 September and staying
there. The one avenue that could not be opened was what the campaigns were
actually matching. SA360 has no search term report; the Google Ads API does.

Resumable: one file per chunk.
"""
import json, sys
from lib_gads import search, write_jsonl, RAW, ACCOUNTS, chunks

ACC = ACCOUNTS["pk_nonbrand"]
Q = ("SELECT search_term_view.search_term, search_term_view.status, "
     "segments.search_term_match_type, segments.date, campaign.id, campaign.name, "
     "metrics.impressions, metrics.clicks, metrics.cost_micros, "
     "metrics.conversions, metrics.conversions_value, metrics.all_conversions "
     "FROM search_term_view WHERE segments.date BETWEEN '{d1}' AND '{d2}'")

total = 0
for d1, d2 in chunks("2026-06-13", "2026-10-05", 14):
    path = RAW / f"r9_pk_terms_{d1}_{d2}.jsonl"
    if path.exists():
        n = sum(1 for _ in open(path, encoding="utf-8"))
        print(f"   skip {path.name} ({n:,d})"); total += n; continue
    rows, err = search(ACC, Q.format(d1=d1, d2=d2))
    if err:
        sys.exit(f"FAILED {d1}..{d2}: {err}")
    write_jsonl(path, rows)
    print(f"   {path.name}: {len(rows):,d}")
    total += len(rows)
print(f"PK search terms: {total:,d} rows, 2026-06-13 to 2026-10-05")
