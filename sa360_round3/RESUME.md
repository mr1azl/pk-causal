# Resume point, round 3

Paused 2026-10-07 at the user's request, after B, before C.
Nothing is in flight. Every script below is re-runnable from the command line and all pulled data
is already on disk, so C starts from a clean state with no re-pulling of A or B.

## Done

**Setup** `s01_setup_accounts_campaigns.py`
PK account 4851538229, USD, Asia/Qatar. 15,868 campaigns, the brief's non-brand filter excludes
zero of them. Two naming conventions, parser in `lib_sa360.dest_code()` handles both.

**A, seasonality** `s02_a_seasonality_pull.py`, `s03_a_build_clean.py`, `s04_a_seasonality_compare.py`
Answered. No September drop in 2025. 2026 UK+IE fell 95 percent against 65 and 71 for the others.

**B, Floodlight bookings** `s05_b1_conversion_actions.py`, `s06_b2_conversion_rows.py`,
`s07_b3_b4_booking_analysis.py`
Answered. One row is one transaction, quantity one. Duplicates 1 of 88. Reported bookings are two
different measurement systems summed, and `QR_Booking` alone is 3.5x its own transaction ledger,
9.8x on regional.

## Still to do

**C, bids and auction share on UK campaigns.** Nothing pulled yet.

- C1 daily, 2026-08-01 to 2026-10-05, every PK non-brand campaign: cost, clicks, impressions,
  average_cpc, search_impression_share, search_top_impression_share,
  search_absolute_top_impression_share, search_click_share,
  search_budget_lost_impression_share, search_rank_lost_impression_share.
- C2 same metrics from `keyword_view`, selecting `ad_group_criterion.keyword.text` and
  `ad_group_criterion.keyword.match_type`, UK+IE campaigns only.
- C3 summary, UK+IE against everything else, weighted by impressions, for four periods:
  **13 Jun to 19 Aug** (needs pulling, it is outside the A and B windows),
  20 Aug to 1 Sep, 2 to 19 Sep, 20 Sep to 5 Oct. Flag any share sitting at exactly 10 or 90.

**Hand back.** `FINDINGS.md` answering A, B and C, and a check that no clean CSV carries an order
ID or a client ID.

## Notes for whoever picks this up

- Chunk date ranges with `lib_sa360.chunks()`, 31 days. A single query over the full C1 window
  across 15,868 campaigns will time out at 120 seconds otherwise.
- `segments.conversion_action_name` forbids `metrics.cost_micros` and `metrics.clicks` in the same
  SELECT. Two queries, join on date and campaign id.
- Impression share clamps: a flat 10.0 means below 10, a flat 90.0 means above 90. Flag, do not
  average as if real.
- Order IDs are already SHA-256 hashed in `data/raw/b2_booking_conversions.jsonl`; the plaintext
  was never written to disk.

## Files on disk

```
round3/
  LOG.md                                  setup, A and B logged in full
  RESUME.md                               this file
  scripts/   lib_sa360.py s01 s02 s03 s04 s05 s06 s07
  data/raw/  a_traffic_2025 a_conv_2025 a_traffic_2026 a_conv_2026
             s01_customer_clients s01_campaigns b1_conversion_actions
             b2_booking_conversions (order IDs hashed)
  data/clean/ s01_pk_accounts s01_pk_nonbrand_campaigns
              pk_nb_traffic_2025 pk_nb_daily_2025
              pk_nb_traffic_2026 pk_nb_daily_2026
              a_seasonality_monthly a_seasonality_weekly_ukie
              b1_booking_actions b3_bookings_daily b4_bookings_by_destgroup
```
