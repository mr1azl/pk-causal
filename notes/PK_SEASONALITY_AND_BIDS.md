# PK: seasonality on Adobe 2025, and what the bidder did (SA360 section C)

*7 Oct 2026. Sources: Adobe v84 for PK, 1 May 2025 to 5 Oct 2026 (`data/adobe/v84_pk_2025-05-01_2026-10-05.parquet`,
`scripts/pk_seasonality_adobe.py`), and the SA360 agent's section C and C4 (`sa360_round3/FINDINGS.md`,
`sa360_round3/data/c*.csv`).*

## Summary

1. **Seasonality is ruled out on two independent sources.** On Adobe, PK UK+IE non-brand bookings rose
   from August to September 2025 (9 to 14 by click date, booking rate +150%) and collapsed in 2026 (20 to 1,
   rate -80%). SA360 2025 says the same. The weekly 2025 series has no September cliff.
2. **At the switch the bidder bid up everywhere, not just on the UK.** Cost per click rose about 5 times on UK and
   6 times on everything else, and lost impression share moved from rank to budget on both. The auction
   mechanics were portfolio-wide.
3. **By late September the UK auction looked like before the switch, and still produced nothing.** From 20 Sep to 5 Oct, UK
   cost per click (0.42) and absolute-top position on won impressions (27%) were back at their
   20 Aug-1 Sep levels (0.44 and 27%). Clicks were half (129 against 259 a day). Bookings stayed at zero.
   So price and position cannot explain the persisting UK zero. Something about **who** clicks, or what
   they find when they search, changed.

## 1. Seasonality on Adobe, PK non-brand by click date

| Segment | Aug 2025 bookings | Sep 2025 | Rate change | Aug 2026 | Sep 2026 | Rate change |
|---|---:|---:|---:|---:|---:|---:|
| Brand | 866 | 658 | +6% | 905 | 956 | +32% |
| NB UK+IE | 9 | **14** | **+150%** | 20 | **1** | **-80%** |
| NB long-haul | 16 | 10 | 0% | 23 | 21 | +167% |
| NB regional | 12 | 2 | -100% | 11 | 6 | +100% |

Rate is bookings per 1,000 search visits.
- UK+IE bookings by click week, 2025: Jul 4, 4, 1, 1; Aug 1, 4, 1, 2; Sep 2, 2, 4, 5, 1. No cliff.
  2026: Aug 6, 2, 2, 9; then 1, 0, 0, 0, 1, 0 from 31 Aug.
- The legacy campaign names (73k of 143k PK non-brand clicks in 2025) are parsed: `_PK-Country-XXX-GB-EN_phrase`,
  `_PK-O&D-LHE-LHR-EN_exact`, `_PK-D-XXX-LHR-EN_phrase`. Brand is taken from the `-Brand` account suffix,
  which catches legacy brand names like `PK-Brand Qatar-EN_exact`.
- The user's agent ran the same comparison on a slimmer copy of this file, by booking date: UK Aug 8 to Sep
  15 in 2025, 19 to 4 in 2026. Same answer.
- Caveat as before: 2025 UK traffic was smaller and cheaper, and small counts. But Adobe and SA360 agree, on
  different counting.

## 2. What the bidder did (SA360 section C)

Impression-weighted, campaign level:

| | Period | CPC | Impr. share | Abs. top on won impr. | Lost to budget | Lost to rank | Clicks/day |
|---|---|---:|---:|---:|---:|---:|---:|
| UK+IE | 20 Aug-1 Sep | 0.44 | 67.8% | 27% | 10.5% | 21.7% | 259 |
| | 2-19 Sep | 2.19 | 27.3% | 55% | 72.0% | 0.7% | 34 |
| | 20 Sep-5 Oct | 0.42 | 55.2% | 27% | 44.8% | 0.0% | 129 |
| Everything else | 20 Aug-1 Sep | 0.20 | 47.6% | 30% | 13.3% | 39.0% | 1,708 |
| | 2-19 Sep | 1.27 | 23.1% | 50% | 58.0% | 18.9% | 375 |
| | 20 Sep-5 Oct | 0.41 | 53.0% | 34% | 42.9% | 4.1% | 1,202 |

- **The switch bought position with price, on a fixed budget, everywhere.** UK was more extreme on rank (0.7%
  then 0.0%) but the same pattern holds for the rest.
- **The non-cut UK campaigns show it too** (cost per click 0.39 to 2.18, budget lost 6% to 75%, rank lost 24% to 1%), so it is
  not the 20 Aug cut.
- **The agent's "UK was never outbid, it ran out of money" is right, but it describes the whole portfolio.** It
  does not separate the UK from the destinations that kept converting.
- **The key comparison is the late period.** UK price and position recovered to cut-period levels; the
  rest of PK settled at about twice its old cost per click (0.20 to 0.41). Yet the rest converts and the UK does not.

## 3. C4: why Floodlight counts are inflated

Cross-device modelled conversions are 60% of `QR_Booking` all_conversions (83% for regional). Without
them, all_conversions is 1.40x the transaction ledger instead of 3.48x, and regional is 1.69x instead of
9.77x. This settles the regional gap: it is Google's cross-device modelling, not tagging.

One caution on the agent's "from 2 Sep" rows: modelled cross-device conversions are reported with a lag,
so zero cross-device conversions after 2 Sep for long-haul and UK may partly be reporting delay. The
pre-switch ratios are the reliable ones.

## 4. What is left to explain, and the checks that would

The UK clicks after the switch search at the same rate per click (0.42 Flight Search per click, SA360)
and land in comparable auction positions by late September, but never book. Candidates, each testable:

1. **Who clicks: geography.** If the PK campaigns use "presence or interest" targeting, the value-based
   bidder may now win UK-destination queries from users outside Pakistan (for example in the UK,
   searching the reverse route), who search but cannot or do not book on the PK site. SA360 API:
   `user_location_view` or `segments.geo_target_country` on the UK campaigns, before and after 2 Sep,
   plus `campaign.geo_target_type_setting` (current value only).
2. **Who clicks: device and audience.** `segments.device` on the UK campaigns before and after, and any
   audience or observation lists on them.
3. **What they find: fares and availability.** A change on PK-UK fares, inventory or schedule around
   2 Sep would stop bookings without any bidding cause, and would show the same "search but no book"
   pattern. One question to the commercial team. A check on the non-UK destinations in the same week
   (they kept converting) makes a site-wide cause unlikely.
4. **What they searched: search terms.** SA360 UI export for the UK campaigns, 1 Aug to 5 Oct, with date.
   The API has no search-term report.

Checks 1 and 3 are the most likely to explain a destination-specific zero, and 1 can be pulled by the
SA360 agent today.
