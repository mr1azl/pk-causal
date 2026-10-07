# PK: SA360 round 3 (seasonality and what a Floodlight booking is)

*7 Oct 2026. Pulled by the SA360 API agent; its scripts, log and summary tables are in `docs/agent_findings/sa360_round3/`
(large daily files and raw rows are not in the repo). Cross-checks in
`scripts/pk_sa360_round3_checks.py`. All counts below are `all_conversions` unless they say "ledger".*

## Summary

1. **Seasonality does not explain the UK collapse.** In 2025 PK UK+IE non-brand bookings per click did
   not fall in September: they rose. In 2026 they fell 91%. Long-haul and regional did better than
   their 2025 seasonal pattern in September 2026, the UK much worse.
2. **"Bookings (FL)" adds two measurement systems.** It sums `QR_Booking` (a Floodlight transaction,
   90-day lookback) and `Booking` (a Google Ads website conversion with data-driven attribution and a 30-day
   window, no Floodlight tag behind it). Neither the API nor the custom-column endpoint exposes
   `Revenue (FL)`.
3. **The Floodlight transaction ledger matches Adobe.** 89 `QR_Booking` transaction rows from 8 Aug to 5 Oct,
   against 89 Adobe PK non-brand bookings over the same dates; 49 rows are identical (same day,
   campaign and revenue to the dollar). Revenue per row is about $1,050. Only 2 of 89 rows have zero
   revenue.
4. **The aggregated counts are inflated, most of all for regional.** `QR_Booking` all_conversions is 3.5x the
   ledger overall: 4.1x for UK+IE, 3.1x for long-haul and 9.8x for regional. Add the `Booking` action
   and "bookings" are about 6.6x the ledger. This is why Floodlight showed about 50x more regional bookings than
   Adobe, and why the regional "value failure" appeared.

## 1. Seasonality, 2025 vs 2026

`QR_Booking` per 1,000 clicks, PK non-brand, by month:

| Group | 2025 Jun | Jul | Aug | **Sep** | 2026 Jun | Jul | Aug | **Sep** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| UK+IE | 2.75 | 2.12 | 0.99 | **2.30** | 6.22 | 3.18 | 5.43 | **0.50** |
| Long-haul | 2.72 | 1.47 | 1.38 | **0.95** | 4.84 | 3.07 | 2.98 | **2.97** |
| Regional | 1.30 | 0.83 | 1.15 | **0.64** | 3.75 | 3.33 | 2.31 | **3.09** |

- **UK+IE:** Aug to Sep was +132% in 2025 and -91% in 2026. Monthly UK+IE bookings (both actions)
  were 33 in August 2025 and 39 in September 2025, and October 2025 was the highest month of the five. The weekly
  2025 series is flat from week 36 to week 44.
- **Long-haul and regional** fell 31% and 44% from August to September in 2025, and were flat or up in
  2026. So against the seasonal norm, the switch helped them and hurt the UK.
- **Searches per click held for the UK** (0.42 Flight Search per click in both August and September
  2026). UK users still click and search at the same rate; they stop booking. That also argues
  against a landing page or search-tracking break.

**Caveats.**
- 2025 UK+IE was a small, cheap programme (about $1,000 to $2,500 a month, cost per click about $0.20) on
  mostly legacy campaigns. In 2026 it was large and expensive (up to $16,000 a month, about $0.90 to $1.15), so
  the traffic is not like for like.
- UK counts in 2025 are 11 to 26 a month.
- The test rules out a recurring September UK cliff in PK paid search. It cannot rule out
  something specific to September 2026, such as a fare, availability or schedule change on PK-UK
  routes.

## 2. What a Floodlight "booking" is

| Action | Type | Attribution, lookback | Rows in ledger (8 Aug-5 Oct) | all_conversions (1 Aug-5 Oct) |
|---|---|---|---:|---:|
| `QR_Booking` (415339895) | Floodlight transaction | 90 days | 89 | 309 |
| `Booking` (207919651) | Google Ads webpage | data-driven, 30 days | n/a (not Floodlight) | 279 |
| Two other `Booking` actions | webpage, dormant | last click, 30 days | 0 | 0 |

- Quantity is 1 on every ledger row: one row is one transaction, not a ticket count. The
  ticket-versus-order idea is dead.
- 1 of 88 order IDs appears twice, both rows with revenue. Duplicates are not the zero-revenue
  mechanism.
- Ledger UK+IE after 2 Sep: **1 row**, on 18 Sep (MUX-BHX). Adobe has the same booking, from a click on
  27 Aug. So **no UK booking from a post-switch click in either system.** `QR_Booking`
  all_conversions for UK+IE after 2 Sep is also 0.0; the 5.9 UK "bookings" Floodlight showed are all
  the Google Ads `Booking` action.

## 3. What this changes

1. **The UK thread survives its biggest threat.** On three sources (Adobe clicks, the Floodlight ledger, and
   Floodlight all_conversions), UK+IE bookings from post-switch clicks are zero or close to it, and
   2025 shows no September cliff.
2. **The regional "value failure" from the second review is withdrawn.** It rested on Floodlight
   aggregated bookings, which overstate regional bookings about 10 times against the transaction ledger,
   at a value per booking no real ticket has. On the ledger, regional goes from 13 rows (about $10,800)
   before 2 Sep to 8 rows (about $7,400) after: a fall, not a collapse in value per booking (about
   $830 to $920). On Adobe, regional revenue rose.
3. **The 68% zero-revenue figure has an explanation.** The ledger has 2.2% zero-revenue rows. The
   aggregated "Bookings (FL)" adds a Google Ads count (`Booking`) and attributed Floodlight counts that
   carry no matching transaction. Days where only those land show bookings with no revenue.
4. **Every market's readout uses these columns.** "Bookings (FL)" in all six markets mixes the two
   actions, and the inflation differs by destination mix. The PK result should be rebuilt on the
   ledger or on Adobe. The other markets should be checked the same way before their booking figures
   are quoted again, although revenue-based results are less exposed than booking counts.

## 4. Open and next

- **Section C of the agent prompt (bids, impression share, keyword level for UK) has not been run yet.**
  It is now the main test of the mechanism: why do UK clicks after the switch search at the same
  rate but never book?
- **Something specific to PK-UK in September 2026:** fares, availability, schedule or a site change
  on UK routes. One question to the commercial or web team.
- **Why `QR_Booking` all_conversions is 3.5x its own ledger, and 9.8x for regional.** Candidates are
  cross-device or modelled conversions and the 90-day lookback. The agent can split all_conversions
  into `cross_device_conversions` and the rest.
- **Search terms for the UK campaigns before and after 2 Sep,** from the SA360 UI, since the API has
  no search-term report.
