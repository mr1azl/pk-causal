# Data requests: PK seasonality and the open checks

*7 Oct 2026. Two sources: the Adobe notebook `aa_v84_daily_pull.ipynb` (re-run for other dates) and the
SA360 API agent. Order matters: request 1 decides whether the UK thread survives.*

## 1. Adobe notebook: same pull for 2025 (seasonality)

Goal: did PK non-brand UK bookings also stop around 1 September in 2025?

Changes in the config cell only:

```python
START_DATE = "2025-06-01"
END_DATE   = "2025-10-31"
RAW_DIR    = "aa_v84_raw_2025"            # new folder, so 2025 and 2026 files never mix
OUTPUT_CSV = "aa_daily_market_group_2025.csv"
```

- Run cells 2 and 3. Cell 3 is optional; only the raw daily files are needed. Zip `aa_v84_raw_2025/`
  and send it, as before. `scripts/load_v84.py` reads it as is.
- The market segment is a "v84 contains" filter, so it works for any date range. If 2025 used older
  account names (no `-PK-EN`), PK will come back empty: check the first day's file for PK rows before
  running the whole range.
- Before running, in `post_report`: remove `print(URL, HEADERS, body)` (it prints the token), put back
  `timeout=60`, and drop `verify=False` in favour of the CA bundle.
- Optional, cheap: also pull 2026-01-01 to 2026-04-30 into `aa_v84_raw_2026a`, for a longer 2026
  baseline.

**What would close the UK thread:** in 2025, UK+IE non-brand bookings at a summer level through
August, then near zero from September, with no bidding change. What would keep it open: September
2025 at a similar level to June to August 2025.

**Caveat:** this only works if PK ran comparable UK non-brand campaigns in 2025. If the 2025 campaign
structure differs, the better test is in 1b.

### 1b. Better seasonality test, if a destination dimension exists in Adobe

A PK point-of-sale report independent of paid search: weekly bookings by destination country (or
OND), PK site, all channels, Jun to Oct 2025 and Jun to Oct 2026. This shows the PK-to-UK booking
season directly, whatever the campaign setup. It needs the Adobe dimension that holds the booked
destination; use it if you know the ID.

## 2. SA360 agent

Paste as is:

> Work locally, scripts saved to files, no credentials in any file, no em dashes. PK account under MCC
> 1144701035 (account 4851538229 if that is PK; confirm with `customer_client`). Remember the gotchas:
> query portfolios from the MCC, segmenting by conversion action forbids cost and clicks in the
> same query, impression share clamps at 10 and 90, attributes are current not historical.
>
> **A. Seasonality, 2025 (highest priority).** Daily, 2025-06-01 to 2025-10-31, every PK non-brand
> search campaign: `campaign.name`, `segments.date`, `metrics.cost_micros`, `metrics.clicks`,
> `metrics.impressions`. Separately, the same dates by `segments.conversion_action_name`:
> `metrics.all_conversions`, `metrics.all_conversions_value`, by click date and by conversion date.
> Then the same two queries for 2026-06-01 to 2026-10-05. Output one CSV per year. The campaign names
> carry the destination code (`Google|PK|Dest|Country|XXX|GB|EN|MOD`), so no mapping is needed.
>
> **B. Non-cut UK campaigns around the switch.** Daily, 2026-08-01 to 2026-10-05, for every PK
> non-brand campaign whose destination is GB, IE, LHR, LGW, MAN, BHX, EDI or DUB, and for all other
> PK non-brand campaigns as a comparison: cost, clicks, impressions, average CPC,
> `search_impression_share`, `search_top_impression_share`, `search_absolute_top_impression_share`,
> `search_click_share`, `search_budget_lost_impression_share`, `search_rank_lost_impression_share`.
> Keep impressions so the shares can be weighted. Same at keyword level (`FROM keyword_view`, select
> `ad_group_criterion.keyword.text`, `ad_group_criterion.keyword.match_type`) for the UK campaigns
> only.
>
> **C. What Floodlight counts for PK bookings.** For every booking-like conversion action in the PK
> account (`QR_Booking`, each `Booking` by id): `conversion_action.*` config (counting, attribution
> model, lookback, primary, included). Then from `FROM conversion`, 2026-08-01 to 2026-10-05, for those
> actions: conversion date, visit date, revenue micros, floodlight original revenue, quantity, status,
> attribution type, campaign name, and the order ID **hashed** (never write raw order IDs or client
> IDs to any output). Report per day and per campaign: rows, sum of quantity, revenue, rows with zero
> revenue, duplicate hashed order IDs. Then the same totals per destination group (UK+IE, North
> America / Europe / Oceania, everything else) using the destination code in the campaign name.
>
> Hand back the CSVs and a short `LOG.md` of every query, row counts and date ranges returned.

## What each answers

| Request | Question | Section of `docs/analysis/02_PK_ADOBE_FRESH_LOOK.md` |
|---|---|---|
| 1 / 1b | Is the September UK drop seasonal? | 8.3 |
| 2A | Same question on Floodlight, plus a 2025 baseline for every destination group | 8.1, 8.3 |
| 2B | Did the bidder bid up and narrow into a worse slice of UK demand? | 7.4, 7.7 |
| 2C | Why Floodlight sees about 50x the regional bookings Adobe does, and whether FL "bookings" are orders, tickets or duplicates | 8.2, 8.5 |

The API has no search term report, so "which UK queries were bought" still needs the SA360 UI
search-term export for the UK campaigns, 1 Aug to 5 Oct 2026, with the date as a column.
