"""A1 to A4: daily traffic and conversion data for PK non-brand, 2025 and 2026.

    cd scripts && python3 s02_a_seasonality_pull.py 2025
    cd scripts && python3 s02_a_seasonality_pull.py 2026

Two queries per month chunk, because segmenting by conversion_action_name forbids
cost and clicks in the same SELECT. Joined later on date and campaign id.

Writes data/raw/a_traffic_<year>.jsonl, data/raw/a_conv_<year>.jsonl
"""
import json, sys
from lib_sa360 import stream, chunks, RAW

PK = "4851538229"
WINDOWS = {"2025": ("2025-06-01", "2025-10-31"), "2026": ("2026-06-01", "2026-10-05")}
an = sys.argv[1]
D1, D2 = WINDOWS[an]

Q_TRAFFIC = ("SELECT segments.date, campaign.id, campaign.name, campaign.status, "
             "metrics.cost_micros, metrics.clicks, metrics.impressions "
             "FROM campaign WHERE segments.date BETWEEN '{a}' AND '{b}'")
Q_CONV = ("SELECT segments.date, campaign.id, campaign.name, segments.conversion_action_name, "
          "metrics.all_conversions, metrics.all_conversions_value, "
          "metrics.all_conversions_by_conversion_date, "
          "metrics.all_conversions_value_by_conversion_date "
          "FROM campaign WHERE segments.date BETWEEN '{a}' AND '{b}'")

for nom, Q in (("traffic", Q_TRAFFIC), ("conv", Q_CONV)):
    f = RAW / f"a_{nom}_{an}.jsonl"
    if f.is_file() and f.stat().st_size > 0:
        print(f"{f.name} already present, {sum(1 for _ in f.open()):,d} rows, skipping")
        continue
    total = 0
    with f.open("w", encoding="utf-8") as out:
        for a, b in chunks(D1, D2, 31):
            code, rows = stream(PK, Q.format(a=a, b=b))
            if code != 200:
                print(f"   {nom} {a}..{b}: HTTP {code} -> {str(rows)[:140]}")
                continue
            for r in rows:
                out.write(json.dumps(r, ensure_ascii=False) + "\n")
            total += len(rows)
            print(f"   {nom} {a}..{b}: {len(rows):,d} rows")
    print(f"{f.name}: {total:,d} rows total")
