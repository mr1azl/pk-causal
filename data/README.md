# Data

Everything the analysis used, as Parquet (large tables) or CSV (small agent outputs). No file holds a
gclid, Floodlight order ID, GA client ID or credential. Currency is USD unless stated. "PK" is the Pakistan
market, "NB" non-brand.

Load any Parquet file with `pandas.read_parquet(path)`.

## adobe/ : Adobe Analytics, eVar84 (SA360 tracking ID) daily pulls

One row per tracking ID per day. The tracking ID is built per click
(`account|campaign...|ad group|keyword|gclid|gclsrc`), so a row is one paid-search click on one day. Metrics are
credited to the eVar84 value on the hit, so a booking made days after the click shows on the booking day under
the click's ID. The analysis credits it back to the click day (`click_day` = first day the ID appears).

| File | Rows | Scope |
|---|---:|---|
| `v84_parsed_2026-05-01_2026-10-05.parquet` | 1,692,069 | Six markets (DE, CA, SA, PK, MY, SG), 1 May to 5 Oct 2026. Built by `scripts/load_v84.py`. |
| `v84_pk_2025-05-01_2026-10-05.parquet` | 1,078,309 | PK segment (plus a small tail of other markets; filter `cc == "PK"`), 1 May 2025 to 5 Oct 2026, both campaign naming conventions. Use with `scripts/pk_seasonality_adobe.py` (`load()`). |

Columns: `day`, `flight_search_visits` (visits with a flight search, event14), `bookings` (event27, orders),
`revenue` (event17, SalesIncYQ), `parsed`, `account`, `engine`, `cc` (market code from the account),
`campaign`, `ad_group`, `keyword`, `has_gclid`, `gclsrc`, `group` (Brand / Non-brand / PMAX, from the campaign
name; for 2025 legacy names use the `-Brand` account suffix, as `pk_seasonality_adobe.load()` does),
`click_key` (first 16 hex characters of SHA-256 of the raw tracking ID; the raw ID carried the gclid).

## sa360/ : SA360 Reporting API pulls by the user's agent

Findings and logs for each round are in `docs/agent_findings/`. The agent's code is in `agent_code/sa360/`
(round 3 only; later rounds' code was not handed over).

### round3/ (PK, seasonality, booking definitions, bids)
| File | What it is |
|---|---|
| `s01_pk_accounts.csv`, `s01_pk_nonbrand_campaigns.parquet` | PK accounts; all 15,868 campaigns of the PK non-brand account with parsed destination. |
| `pk_nb_traffic_2025.parquet`, `pk_nb_traffic_2026.parquet` | Date x campaign: cost, clicks, impressions, destination group. 1 Jun to 31 Oct 2025; 1 Jun to 5 Oct 2026. |
| `pk_nb_daily_2025.parquet`, `pk_nb_daily_2026.parquet` | Date x campaign x conversion action: `all_conversions` and value, by click date and by conversion date. |
| `a_seasonality_monthly.csv`, `a_seasonality_weekly_ukie.csv` | 2025 vs 2026 by destination group (bookings = `QR_Booking` + `Booking`). |
| `b1_booking_actions.csv` | Configuration of the 11 booking-like conversion actions. |
| `b2_booking_ledger.parquet` | The 89 Floodlight `QR_Booking` transaction rows, 8 Aug to 5 Oct 2026 (order IDs removed). |
| `b3_bookings_daily.csv`, `b4_bookings_by_destgroup.csv` | The ledger aggregated by day and by destination group. |
| `c1_campaign_daily_shares.parquet` | Date x campaign: cost, clicks, impressions, CPC and six impression-share metrics, 13 Jun to 5 Oct 2026. |
| `c2_*.csv`, `c3_period_summary.csv` | UK+IE vs the rest, GB country (cut 20 Aug) vs the other UK campaigns, four periods, impression weighted. |
| `c4_crossdevice_vs_ledger.csv` | `QR_Booking` all_conversions split into cross-device and same-device, against ledger rows. |

### round4/ (PK, who clicks UK ads and what changed)
| File | What it is |
|---|---|
| `d1_*.csv` | User location (physical country) by period, location settings and targeted locations (current values). |
| `d2_*.csv` | Device mix by period, and `QR_Booking` by device. |
| `d3_changes_15aug_5oct.csv`, `d3_ukie_keyword_inventory.csv` | Objects modified 15 Aug to 5 Oct (`last_modified_time`), and the 1,188 UK+IE keywords. |
| `d4_weekly_keywords.parquet` | Week x keyword, all PK non-brand, 1 Jun to 5 Oct 2026, with `QR_Booking` conversions and value. |
| `d5_audiences_modifiers.csv` | Audiences and bid modifiers on UK+IE campaigns. |
| `d6_*.csv` | Brand vs non-brand bookings (note: the brand account records no `QR_Booking` in any period, so this check cannot detect migration), conversion custom variables. |
| `d7_switchback_candidates.csv`, `d8_rmk_detail.csv` | The agent's switchback shortlist and the `_PK-Generic-RMKT_Exact` campaign detail. |

### round5_SA/ and round6_CA_MY/ (control markets)
Saudi Arabia (`e*`), Canada and Malaysia (`f_CA_*`, `f_MY_*`), PK on the same basis (`f_PK_by_period.csv`), and
`g1_window_reconciliation.csv`, which shows the CA and MY "conversion damage" disappears over the full post window.

## search_terms/ : Google Ads UI search terms reports, May to 7 Oct 2026

Monthly, cost and clicks only (the export has no conversions). Total rows removed.

| File | Rows | Notes |
|---|---:|---|
| `pk_nonbrand_2026-05_2026-10.parquet` | 264,784 | With columns added by `scripts/pk_search_terms.py`: `dest`, `ctype`, `is_uk`, `gb_country_cut`, `direction`, `competitor_airline`, `qatar_named`. |
| `pk_brand_2026-05_2026-10.parquet` | 11,396 | PK brand account. |
| `india_nonbrand_2026-05_2026-10.parquet` | 260,780 | India non-brand, rows with at least one click only, with `direction`, `group`, `agent_ota`, `competitor`, `brand_word`, `broad` from `scripts/india_search_terms.py`. |
| `india_brand_2026-05_2026-10.parquet` | 17,707 | India brand account. |

## gfs/ : Google Flight Search (Google Flights partner data), PK origins

Output of `notebooks/GFS_PK_UK.ipynb` (queries in `sql/gfs_pk_uk.sql`), run with all user countries. QR rows
only: the tables hold no competitor rows. Weekly, 1 Jun 2025 to 4 Oct 2026. Weights are relative volumes.

| File | What it is |
|---|---|
| `q0*_*.csv` | Checks: date coverage, user countries, partners, table schema. |
| `q1_competitiveness_weekly.csv` | QR cheapest share, price gap, participation, top impression share, demand weight; UK+IE vs other. |
| `q2_shopping_weekly.csv` | QR rank, best-flights share, selection rate when shown, share of selections; UK+IE vs other. |
| `q3_routes_*.csv` | Per PK-UK route, before vs from 2 Sep, 2026 and 2025. |
| `q4_competitors_weekly.csv` | Partner breakdown on PK-UK (QR only). |
| `headline.csv`, `c*.png` | 4 weeks before vs from 2 Sep in each year; charts. |
