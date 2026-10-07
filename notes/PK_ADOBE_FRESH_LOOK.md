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

---

## 6. Campaign type and keyword mix

*Reproduce with `scripts/pk_keyword_mix.py`. Click date basis, PK Google non-brand, 13 Jun to 5 Oct.
Every `Dest|City` campaign targets an airport code (LHR, JFK, PER); there are no metro-code campaigns
(LON, NYC). The city-name vs airport-code split therefore shows up in the keywords, not the campaigns.*

### 6.1 Campaign type

Clicks per day, and bookings per 1,000 clicks in brackets:

| Campaign type | 13 Jun-19 Aug | 20 Aug-1 Sep (cut) | 2-19 Sep (switch) | 20 Sep-5 Oct |
|---|---:|---:|---:|---:|
| Destination: country (`Dest\|Country`) | 321 (1.7) | 169 (1.4) | 25 (6.7) | 60 (5.2) |
| Route: Pakistan to country (`O&D\|Country`) | 248 (1.4) | 78 (2.0) | 13 (0.0) | 104 (3.6) |
| Destination: city/airport (`Dest\|City`) | 100 (3.5) | 170 (1.4) | 33 (8.4) | 108 (2.3) |
| Route: airport to airport (`O&D\|Routes`) | 134 (3.7) | 202 (4.6) | 23 (9.9) | 157 (1.2) |
| Generic, legacy exact | 17 (4.4) | 20 (0.0) | 20 (16.6) | 23 (2.7) |

- **The 20 Aug cut was a cut to the country campaigns.**
  - Destination-country and Pakistan-to-country clicks fell 47% and 69%.
  - City and airport-route clicks rose 70% and 50%.
  - So the cut removed the two lowest-converting types (1.4 to 1.7 bookings per 1,000 clicks) and moved
    traffic to the two highest (3.5 to 3.7). That is why the cut fortnight looks efficient.
- **After the switch, conversion by type reversed.**
  - Country types now convert better: 3.6 to 5.2 per 1,000.
  - Routes and cities convert worse. Airport-to-airport routes fell from 3.7 to 1.2: 3 bookings on
    about 2,500 clicks, where the pre-switch rate predicts about 9.
- **The generic legacy campaign is flat throughout** (17 to 23 clicks a day). It looks outside the VBB
  portfolio, which needs confirming. If so, it is a small in-market control, and it shows no drop.

### 6.2 Campaign type, UK+IE only

| UK+IE campaign type | Bookings per 1,000 clicks, 13 Jun-1 Sep | Clicks after switch | Bookings after | Expected at old rate |
|---|---:|---:|---:|---:|
| Airport-to-airport routes (LHE-LHR, MUX-BHX...) | 7.4 to 10.9 | about 490 | 0 | about 4 |
| City/airport (LHR, MAN, LGW, EDI...) | 9.4 | about 360 | 0 | about 3.4 |
| Destination country (GB) | 2.2 to 8.5 | about 80 | 0 | under 1 |
| Pakistan to country (PK-GB) | 5.8 to 6.4 | about 60 | 1 | about 0.4 |

UK routes and UK cities were the best-converting non-brand segments in PK, at 7 to 11 bookings per
1,000 clicks against about 2 for non-brand overall. They are the ones that went to zero. Each cell is
borderline on its own (p about 0.02 to 0.03), but together they are clear.

### 6.3 Keyword mix

| Keyword feature | Click share 13 Jun-19 Aug | Click share 20 Sep-5 Oct | Bookings per 1,000 before | Bookings per 1,000 after |
|---|---:|---:|---:|---:|
| Destination as country name | 69% | 36% | 1.6 | 4.2 |
| Destination as city name | 20% | 39% | 3.4 | 1.4 |
| Destination as airport code (all phrase match) | 9% | 19% | 4.2 | 2.1 |
| Origin named as "Pakistan" | 30% | 23% | 1.4 | 3.6 |
| Origin as Pakistani city (Lahore, Karachi...) | 12% | 24% | 3.4 | 1.7 |
| Premium cabin (first or business class) | 4% | 3% | 2.6 | 0 |
| Price words (cheap, deals, fares) | 6% | 5% | 3.1 | 3.0 |

- **The keyword mix moved from broad to specific,** from country names to city names, airport codes and
  named Pakistani origins. Most of that shift happened at the 20 Aug cut, not at the switch.
- **The keyword mix itself is not the problem.** The post-switch keyword mix, priced at each keyword's
  pre-switch conversion, implies 2.07 to 2.18 bookings per 1,000 clicks, against 1.94 before. The bidder
  is choosing keywords that used to convert at least as well.
- **The loss is within the specific keywords.** City-name and airport-code keywords used to convert
  best (3.4 to 4.2) and now convert at 1.4 to 2.1. Revenue per click is 13% below what the mix implies
  ($1.83 against $2.10).
- **Breadth recovered.** Distinct keywords with a click per day: 213 before, 70 in the switch fortnight,
  211 since 20 Sep.
- **UK keywords:** "united kingdom flights", "pakistan to united kingdom flights" and "flights to
  united kingdom" fell from 8.5% of clicks to 0.6%. UK city keywords grew ("manchester flights" 0.1% to
  1.3%, "karachi to london flights" 0.2% to 0.7%) but produced no bookings.

### 6.4 What this adds

1. **The bidder's choice of keywords and campaigns looks reasonable on paper.** Priced at pre-switch
   performance, both the keyword mix and the campaign mix after the switch should convert slightly
   better than before.
2. **What broke is the conversion of the specific, high-intent traffic.** This covers route and city
   keywords, above all to the UK. The bidder still buys these clicks, at 30% to 80% of the old volume,
   but they stopped booking.
3. **That points away from "wrong keywords" and towards which auctions or users the bidder now wins
   within the same keywords.** With Maximise Conversion Value on search value, it can win queries on
   the same keyword that are search-heavy and booking-light, for example users who search many dates.
   Adobe cannot show the search term or the bid. The next step is the SA360 search-term report for UK
   route and city campaigns, before vs after 2 Sep, with the VBB value per conversion.
