# Data

All files are Parquet (zstd). Nothing here holds a gclid, order ID, GA client ID or credential.

| File | Source | Rows | What it is |
|---|---|---:|---|
| `adobe/v84_parsed_2026-05-01_2026-10-05.parquet` | Adobe Analytics, eVar84 daily pull | 1,692,069 | One row per tracking ID per day, all six markets: flight search visits, bookings, revenue (SalesIncYQ), and the parsed account, campaign, ad group, keyword, market and campaign group. The raw tracking ID carried the gclid, so it is replaced by `click_key`, the first 16 hex characters of its SHA-256. Built by `scripts/load_v84.py`, then hashed. |
| `adobe/v84_pk_2025-05-01_2026-10-05.parquet` | Adobe Analytics, PK pull | 1,078,309 | Same format as the 2026 file, PK segment, 1 May 2025 to 5 Oct 2026, both campaign naming conventions. Use `scripts/pk_seasonality_adobe.py`; filter `cc == "PK"` (a small tail of other markets passes the segment). |
| `sa360_round3/c1_campaign_daily_shares.parquet` | SA360 API | 37,742 | Date x campaign cost, clicks, impressions, CPC and the six impression share metrics, 13 Jun to 5 Oct 2026. |
| `sa360_round3/pk_nb_daily_2025.parquet`, `_2026` | SA360 API, PK non-brand account | 199,782 / 151,501 | Date x campaign x conversion action: all_conversions and value, by click date and by conversion date. 2025 is 1 Jun to 31 Oct, 2026 is 1 Jun to 5 Oct. |
| `sa360_round3/pk_nb_traffic_2025.parquet`, `_2026` | SA360 API | 131,496 / 40,675 | Date x campaign: cost, clicks, impressions, with destination code and group. |
| `sa360_round3/s01_pk_nonbrand_campaigns.parquet` | SA360 API | 15,868 | Every campaign in the PK non-brand account, with status and parsed destination. |
| `sa360_round3/b2_booking_ledger.parquet` | SA360 API, `FROM conversion` | 89 | Floodlight `QR_Booking` transaction rows, 8 Aug to 5 Oct 2026: campaign, conversion and visit time, revenue, quantity, status. Order IDs removed. |

The scripts in `scripts/` take the Adobe file directly, for example
`python scripts/pk_cut_adjusted.py data/adobe/v84_parsed_2026-05-01_2026-10-05.parquet`.
The SA360 agent's own scripts and log are in `sa360_round3/`.
