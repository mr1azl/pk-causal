# PK non-brand: how the keywords changed over time

*7 Oct 2026. Adobe v84, PK Google non-brand, 1 May 2025 to 5 Oct 2026, bookings by click date.
Reproduce with `python scripts/pk_keyword_trends.py data/adobe/v84_pk_2025-05-01_2026-10-05.parquet`
(run from `scripts/`). Volumes are small: UK+IE non-brand is 1 to 30 bookings a month, so single-month
rates move a lot.*

## Summary

1. **The keyword mix changed at account restructures, not at the VBB switch.** The big shifts happened in
   September 2025, January 2026 and May to August 2026. At the switch on 2 Sep 2026, only 1% to 2% of
   clicks went to keywords that had no click in the previous three months.
2. **The post-switch UK keyword mix should have converted better than before.** Priced at each keyword's
   13 Jun to 1 Sep 2026 conversion, the September mix implies 5.1 bookings per 1,000 clicks against 4.4 to
   4.6 in June to August. Actual: 1.4. The collapse is inside the same keywords.
3. **Long-haul and regional show the opposite.** Their post-switch actual conversion is well above what
   their keyword mix implies (long-haul 8.8 vs 2.7 per 1,000 in September, regional 1.9 vs 0.5). VBB is
   picking better clicks within keywords there, and worse ones, or ones that cannot book, in the UK.
4. **Correction to my earlier quick read:** I said more UK clicks were coming from keywords without a
   Pakistani origin after the switch. At month level the reverse is true: origin-named keywords rose
   from 52% to 57% of UK clicks in September. Both kinds stopped converting.

## 1. The restructures, visible in the keywords

Distinct keywords with a click per month, and share of clicks on the top 10:

| Month | UK+IE keywords | UK top-10 share | Long-haul keywords | Regional keywords | New-keyword click share (UK / LH / regional) |
|---|---:|---:|---:|---:|---|
| Aug 2025 | 422 | 23% | 1,199 | 2,109 | 5% / 6% / 8% |
| **Sep 2025** | **150** | **49%** | **465** | **397** | **24% / 44% / 38%** |
| Dec 2025 | 117 | 51% | 441 | 295 | 2% / 1% / 5% |
| Jun 2026 | 121 | 64% | 351 | 200 | 2% / 5% / 6% |
| Aug 2026 | 109 | 72% | 445 | 319 | 1% / 3% / 4% |
| **Sep 2026 (switch)** | 79 | 51% | 318 | 241 | **1% / 2% / 2%** |

- **September 2025: the account was rebuilt.** The pipe-named campaigns started on 22 Aug 2025 (SA360 log).
  The keyword count fell by 60% to 80%, a quarter to two fifths of clicks moved to new keywords, price-word
  keywords ("cheap", "deals", "fares") fell from about 18% of clicks to 1% to 4%, premium-cabin keywords
  appeared (10% to 18% of UK clicks), and "Pakistan to country" route campaigns started.
- **January 2026: UK moved from routes to destinations.** Airport-to-airport routes fell from 65% to 33% of
  UK clicks and city/airport destination campaigns rose from 28% to 60%. Keywords naming the origin fell
  from 68% to 37%.
- **May to August 2026: the GB country push.** UK clicks on country-name keywords went from 7% (March) to
  65% (July), driven by the two GB country campaigns that were then cut on 20 Aug. Regional moved the
  same way (country-name keywords 82% to 85%).
- **The switch itself changed little in the keyword set.** UK keyword count fell from 109 to 79, but almost
  no new keywords appeared. The shift back towards city and route keywords in September is the 20 Aug cut
  removing the country campaigns, not the bidder choosing new terms.

## 2. UK+IE keyword features, click share and bookings per 1,000 clicks

| Month | Origin named | Bk/1k | No origin | Bk/1k | Country name | City name | Airport code |
|---|---:|---:|---:|---:|---:|---:|---:|
| Jun 2026 | 50% | 6.2 | 50% | 4.9 | 48% | 35% | 18% |
| Jul 2026 | 47% | 5.2 | 53% | 4.0 | 65% | 25% | 10% |
| Aug 2026 | 52% | 8.7 | 48% | 2.3 | 59% | 31% | 10% |
| **Sep 2026** | 57% | **0.0** | 43% | 3.3 | 22% | 59% | 19% |

Every feature split goes to near zero in the UK in September. No keyword type kept converting, which is
why the mix test in section 3 finds no keyword explanation.

## 3. Keyword mix test by month

Each month's keyword mix priced at the keyword's 13 Jun to 1 Sep 2026 conversion (shrunk to the segment
mean), against what actually happened:

| Month | UK mix-implied | UK actual | Long-haul implied | LH actual | Regional implied | Regional actual |
|---|---:|---:|---:|---:|---:|---:|
| Jun 2026 | 4.57 | 5.53 | 2.56 | 3.69 | 0.51 | 0.35 |
| Jul 2026 | 4.37 | 4.54 | 2.47 | 1.83 | 0.56 | 0.70 |
| Aug 2026 | 4.58 | 5.66 | 2.49 | 2.72 | 0.70 | 0.78 |
| **Sep 2026** | **5.09** | **1.40** | 2.67 | **8.81** | 0.48 | **1.88** |

Before the switch, actual tracks the mix in all three groups. After it, the UK falls far below its mix
and the other two rise far above theirs. Same bidder, same month, opposite outcome by destination.

## 4. UK keywords, 13 Jun-1 Sep vs 2 Sep-5 Oct 2026

| Keyword | Clicks/day before | Bookings before | Clicks/day after | Bookings after |
|---|---:|---:|---:|---:|
| united kingdom flights | 28.8 | 5 | 1.4 | 0 |
| pakistan to united kingdom flights | 21.6 | 10 | 1.1 | 0 |
| flights to united kingdom | 13.6 | 2 | 0.5 | 0 |
| flights from islamabad to london | 5.0 | 3 | 0.6 | 0 |
| flights to london | 4.6 | 0 | 1.9 | 0 |
| lahore to london flights | 4.2 | 1 | 2.2 | 0 |
| lhe to lhr flights | 2.3 | 2 | 0.9 | 0 |
| karachi to london flights | 1.8 | 0 | 1.7 | 0 |
| manchester flights | 0.5 | 0 | 2.8 | 0 |

- The three country keywords that carried 17 of the UK's pre-switch bookings sat in the two GB country
  campaigns cut on 20 Aug. Their loss is the cut.
- The keywords that remain are route and city terms, including several that never booked even before
  ("flights to london", "karachi to london flights", "manchester flights"). They now take a larger share.
  This is a real but small mix effect, and the mix test already accounts for it: priced at their own
  history, the post-switch UK keywords should still convert at about 5 per 1,000.

## 5. What this means for the cause

- "The bidder bought the wrong UK keywords" is ruled out. It bought almost the same keywords, and those
  keywords used to convert.
- What changed is inside the keyword: which auctions, users or queries the bidder wins, or what users find
  when they search a UK route. That is what SA360 round 4 tests (user location, device, campaign changes
  since 15 Aug), together with the PK-UK fare and availability question.
- Data caveat: March 2026 has unusually low volume in every segment, brand included (Adobe or pull issue);
  it does not affect the periods compared here.
