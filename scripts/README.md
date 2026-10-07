# Scripts

Run from the repo root with Python 3.10+, `pandas`, `pyarrow` (and `py7zr` only to unpack raw uploads).
Every script prints its tables to stdout; none writes back into `data/` unless an output path is given.

| Script | Input | What it answers | Used in |
|---|---|---|---|
| `load_v84.py` | raw Adobe daily CSVs (`v84_YYYY-MM-DD.csv`) | Parses the tracking ID into account, campaign, ad group, keyword; writes one Parquet file. | building `data/adobe/` |
| `pk_adobe_analysis.py` | `data/adobe/v84_parsed_2026-05-01_2026-10-05.parquet` | PK by click date: brand, NB UK+IE, NB other; zero-revenue bookings; UK by campaign. | analysis 02 |
| `pk_keyword_mix.py` | same | PK NB campaign type and keyword features by period; keyword and campaign mix tests. | analysis 02 s6 |
| `pk_cut_adjusted.py` | same (optional cut list) | Campaigns not hit by the 20 Aug cut: UK+IE, long-haul, regional, generic; Poisson test. | analysis 02 s7-8 |
| `pk_sa360_round3_checks.py` | `data/sa360/round3` + Adobe file | Bookings per click 2025 vs 2026; Floodlight ledger vs Adobe row match. | analysis 03 |
| `pk_seasonality_adobe.py` | `data/adobe/v84_pk_2025-05-01_2026-10-05.parquet` | 2025 vs 2026 by segment; parses both naming conventions; `load()` is reused by other scripts. | analysis 04 |
| `pk_keyword_trends.py` | same (run from `scripts/`) | Keyword breadth, turnover, feature mix and keyword mix test, May 2025 to Oct 2026. | analysis 05 |
| `pk_value_per_search.py` | `data/sa360/round3` | VBB search value per click and per $ vs booking revenue, by group. | analysis 06 |
| `pk_d4_match_type.py` | `data/sa360/round4/d4_weekly_keywords.parquet` | UK+IE vs rest by match type, weekly keywords. | analysis 06 s6 |
| `pk_booking_tags_by_group.py` | `data/sa360/round3` + `c1_campaign_daily_shares.parquet` | Bookings per click on both booking tags; search value / booking value by group. | analysis 08 |
| `pk_search_terms.py` | PK search terms CSV (UI export) | Direction and intent of the queries bought on UK campaigns. | analysis 08 |
| `pk_brand_search_terms.py` | PK brand search terms CSV | Brand queries by destination named. | analysis 08 s7 |
| `pk_brand_vs_nonbrand.py` | PK Adobe file | Brand vs non-brand bookings and revenue by month, 2025 and 2026. | analysis 08 s7 |
| `india_search_terms.py` | India non-brand and brand search terms CSVs | Reverse, third-country, generic, agent/OTA and competitor share; brand CPC and leakage. | analysis 09 |

Examples:

```bash
python scripts/pk_cut_adjusted.py data/adobe/v84_parsed_2026-05-01_2026-10-05.parquet
python scripts/pk_seasonality_adobe.py data/adobe/v84_pk_2025-05-01_2026-10-05.parquet
python scripts/pk_booking_tags_by_group.py data/sa360/round3 data/sa360/round3/c1_campaign_daily_shares.parquet
(cd scripts && python pk_keyword_trends.py ../data/adobe/v84_pk_2025-05-01_2026-10-05.parquet)
```

The two search-term scripts take the raw UI CSV export (not kept in the repo); their classified output is in
`data/search_terms/`, so the classification can be inspected without rerunning them.
