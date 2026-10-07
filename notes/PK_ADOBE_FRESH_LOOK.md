# PK VBB on Adobe data: a fresh look

*7 Oct 2026. Source: the raw Adobe v84 daily files, 1 May to 5 Oct 2026 (158 days, 1.69M rows).
Each v84 value carries a gclid, so one row is one click on one day. Reproduce with
`scripts/load_v84.py` then `scripts/pk_adobe_analysis.py`. Raw files are not in the repo.*

**Method.** Bookings and revenue are assigned to the day the click first appears (click date), not
the day the booking happens. 80% of bookings land on the click day, 58% for PK non-brand, so booking
date would credit pre-switch clicks to the post-switch period. "UK+IE" is every PK non-brand campaign
whose destination is GB, IE or a UK or Irish airport.

## Headline

**On Adobe, VBB in PK did not fail across the board. It failed on one destination: the UK.**

- Non-brand bookings to everywhere except the UK and Ireland are back at their pre-cut level, on far fewer
  clicks.
- UK+IE non-brand went from about 0.7 bookings a day to 1 booking in 34 days. UK+IE was 31% of PK
  non-brand revenue from 13 Jun to 19 Aug and 63% during the budget-cut fortnight.
- The UK accounts for essentially all of the non-brand revenue PK has lost since the switch.

## 1. PK by click date, per day

| Period | Brand bookings | NB UK+IE clicks | NB UK+IE bookings | NB UK+IE revenue | NB other clicks | NB other bookings | NB other revenue |
|---|---:|---:|---:|---:|---:|---:|---:|
| 13 Jun-19 Aug | 27.1 | 126 | 0.65 | 546 | 693 | 1.18 | 1,213 |
| 20 Aug-1 Sep (cut) | 28.1 | 97 | 0.85 | 1,078 | 542 | 0.69 | 639 |
| 2-19 Sep (switch) | 29.9 | 11 | 0.00 | 0 | 103 | 1.00 | 876 |
| 20 Sep-5 Oct | 32.5 | 50 | 0.06 | 43 | 403 | 1.12 | 788 |

- **Brand is steady or rising,** so there is no market-wide drop in demand.
- **NB other:** clicks fell 81% at the switch and are now 26% below the cut period. Bookings went from
  0.69 a day in the cut period to 1.0 to 1.1 a day after the switch, back to the 13 Jun-19 Aug level.
  This is the same pattern as in Germany and Canada: fewer clicks, converting better.
- **NB UK+IE:** clicks fell 89% at the switch and are still 48% below the cut period, and the clicks
  that remain do not book.

## 2. UK+IE by campaign, 13 Jun-1 Sep vs 2 Sep-5 Oct

| Destination | Clicks a day before | Clicks a day after | Bookings before (81 days) | Bookings after (34 days) |
|---|---:|---:|---:|---:|
| GB (country campaigns) | 68.9 | 3.0 | 20 | 0 |
| LHR | 19.1 | 6.2 | 6 | 0 |
| LGW | 10.0 | 6.3 | 3 | 0 |
| MAN | 8.1 | 6.7 | 4 | 0 |
| EDI | 3.9 | 2.7 | 8 | 0 |
| BHX | 5.3 | 2.1 | 5 | 0 |
| DUB | 3.3 | 1.0 | 7 | 0 |
| IE | 2.8 | 1.2 | 2 | 1 |

- **Two separate failures.**
  - The GB country campaigns were almost switched off: clicks fell 96%. This matches the
    earlier SA360 finding that UK country spend fell from $258 to $15 a day.
  - The UK city and route campaigns kept 30% to 80% of their clicks but stopped converting.
- **Significance.**
  - After the switch, UK+IE campaigns received about 990 clicks. At the pre-switch rate of about
    5.6 bookings per 1,000 clicks, that predicts about 5.6 bookings. One was observed (Poisson
    p about 0.02).
  - Holding traffic at its pre-switch level, the expectation would have been 22 to 29 bookings.
- **Other markets.** Other markets' UK-destination campaigns (SA, MY, SG) show no September drop.
  The numbers are small, but this argues against a general UK seasonality.

## 3. What this changes in the earlier diagnosis

1. **Zero-revenue bookings are a Floodlight artefact.** Adobe has 0 bookings with zero revenue out of
   4,870 PK bookings. The 68% figure comes from the `Bookings (FL)` column, not from the site.
2. **PK non-brand is much smaller in Adobe than in Floodlight.** Adobe shows about 1.8 bookings a day before the
   switch, Floodlight about 9.5. eVar84 is overwritten by later clicks, so a non-brand click followed
   by a brand click is credited to brand. Neither source is wrong, but the two must not be mixed.
3. **"The bidder chases a value signal that does not track revenue" is too broad.** A destination-mix
   test (each period's search mix priced at pre-period revenue per search) gives a slightly higher
   implied value after the switch: $2.07 to $2.11 per search, against $1.84 to $1.87 before. Outside the UK the
   reallocation looks sound. The problem is specific to the UK.
4. **Revised leading cause:** the VBB value for PK-to-UK searches is too low. Either fallback values
   ($0.50) hit UK routes, or the UK ONDs are mis-priced in the value table. So the bidder dropped
   the GB country campaigns and outbid itself out of the UK queries that convert. This hypothesis
   is testable and narrow.

## 4. Checks this points to

1. VBB value per search for PK searches to UK and Irish destinations, before vs after 2 Sep: share at
   $0.50, share at $0, median. Compare with the same for the "other" destinations. This is C6.1 and
   C6.3 restricted to UK ONDs.
2. The value-table entries for the main PK-to-UK ONDs (LHE, ISB, KHI, MUX, SKT to LHR, LGW, MAN,
   BHX, EDI, DUB), including multi-airport London and multi-leg routes.
3. SA360 spend and CPC for the GB country campaigns, daily from 25 Aug to 5 Oct, to confirm they
   were bid down rather than paused or limited by something else.
4. Same-season UK booking volume for PK in 2025, if available, to close out seasonality.

## 5. Caveats

- Volumes are small: PK non-brand is 1 to 2 bookings a day in Adobe. Section 2 is significant in total
  but not campaign by campaign.
- The last days are right-censored: clicks from late September can still produce bookings after 5 Oct.
- Revenue is SalesIncYQ, currency not confirmed. Ratios and comparisons within Adobe are unaffected.
- Click date is the first day a v84 value appears in this window. Clicks before 1 May are
  credited to their first appearance.
