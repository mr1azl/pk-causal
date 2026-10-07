# PK VBB round 3: handover package

Qatar Airways Pakistan non-brand search, Google Ads account 4851538229, USD, Asia/Qatar.
Investigating a booking collapse after the 2 September 2026 move to value based bidding.
Built 2026-10-07 from the SA360 Reporting API.

## Read in this order

1. `FINDINGS.md` answers the three questions: is the UK drop seasonal, what a Floodlight booking
   actually is, and what the bidder did to UK cost per click and auction share at the switch.
2. `LOG.md` is the working record: every script, the date range actually returned, row counts,
   key numbers, and each error with its fix. Read it before trusting or re-deriving any figure.
3. `data/clean/` has the tables behind every number in FINDINGS.
4. `scripts/` reproduces all of it.

## The three answers in one line each

**A.** Not seasonal. September 2025 UK+IE bookings were 39.3, above August 2025, while September
2026 was 5.9 against 110.6.

**B.** One Floodlight booking is one transaction with quantity one. The reported booking number
adds a Floodlight tag to a Google Ads WEBPAGE conversion, two different measurement systems, and
cross-device modelling accounts for 60 percent of the Floodlight side, 83 percent on regional.

**C.** Cost per click rose 4.9x, clicks fell 82 percent, impression share fell 40 points, and the
loss moved from rank (21.7 to 0.7 percent) onto budget (10.5 to 72.0). UK was never outbid.

## What is in data/clean

| file | what it holds |
|---|---|
| `s01_pk_accounts.csv` | the four PK accounts with currency and time zone |
| `s01_pk_nonbrand_campaigns.csv` | all 15,868 campaigns with destination code and group |
| `pk_nb_traffic_2025.csv`, `pk_nb_traffic_2026.csv` | date x campaign cost, clicks, impressions |
| `pk_nb_daily_2025.csv`, `pk_nb_daily_2026.csv` | date x campaign x conversion action |
| `a_seasonality_monthly.csv`, `a_seasonality_weekly_ukie.csv` | the 2025 against 2026 comparison |
| `b1_booking_actions.csv` | full config of all 11 booking conversion actions |
| `b3_bookings_daily.csv`, `b4_bookings_by_destgroup.csv` | the 89 row transaction ledger, aggregated |
| `c1_campaign_daily_shares.csv` | date x campaign traffic and all six auction share metrics |
| `c2_ukie_keywords_by_period.csv` | UK+IE keyword level by period |
| `c2_ukie_cut_vs_rest.csv`, `c2_ukie_keywords_cut_vs_rest.csv` | the two GB campaigns cut on 20 Aug against the other 64 |
| `c3_period_summary.csv` | UK+IE against everything else, four periods, impression weighted |
| `c4_crossdevice_vs_ledger.csv` | cross-device split against the transaction ledger |

## Things that will mislead you if you do not know them

- **Two naming conventions.** The `Google|PK|Dest|Country|XXX|GB|EN|MOD` form covers only 589 of
  15,868 campaigns. In 2025, 71 percent of spend is on legacy names like
  `_PK-Country-XXX-AU-EN_phrase`. `lib_sa360.dest_code()` parses both. A pipe-only parser drops
  most of 2025 and can reverse the seasonality conclusion.
- **The non-brand filter excludes nothing**, correctly: no campaign name in this account contains
  "brand", because brand sits in account 1423602235.
- **Impression share clamps.** Below 10 percent reports as exactly 10.0, above 90 as exactly 90.0.
  Affected cells are carried as explicit `*_clamped_pct_of_impressions` columns, never averaged in
  silently. Here it is 1 to 3 percent of impressions, in 2 to 19 September only.
- **Top and absolute top impression share are shares of the eligible market**, so they fall when
  impression share falls. Divide by impression share for position on impressions actually won.
  Both readings are in FINDINGS; quoting either alone is misleading.
- **`all_conversions` is not a count of orders.** It is modelled, attributed and cross-device.
  Against the transaction ledger it runs 3.48x overall and 9.77x on regional.
- **`Bookings (FL)` and `Revenue (FL)` are not reachable through the API.** The account exposes two
  custom columns, both counts, neither carrying revenue.
- **Attributes are current, not historical.** Only metrics are time sliced, so reading a bid with
  an August date range returns today's value.

## Not included and why

`data/raw/` is excluded. It holds the untouched API responses and is large. Order IDs in it are
already SHA-256 hashed, and the plaintext was never written to disk, but the handover rule is that
raw rows stay in place. Re-pull it with the scripts if you need it.

Credentials are not included and appear in no script. `lib_sa360.py` reads `CLIENT_ID`,
`CLIENT_SECRET` and `REFRESH_TOKEN` from the environment or a local `.env` that is not in this
package.

## Scope and limits

Google Ads only; the two Bing PK accounts are out of scope. C2 keyword data is per period, not per
day. The conversion row window is 1 August to 5 October 2026. Destination group membership is
written out code by code in `lib_sa360.py` so the boundary is auditable.
