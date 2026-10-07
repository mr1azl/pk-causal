# PK VBB on Adobe data: a fresh look

*7 Oct 2026. Source: the raw Adobe v84 daily files, 1 May to 5 Oct 2026 (158 days, 1.69M rows).
Each v84 value carries a gclid, so one row is one click on one day. Reproduce with
`scripts/load_v84.py` then `scripts/pk_adobe_analysis.py`. Raw files are not in the repo.*

**Method.** Bookings and revenue are assigned to the day the click first appears (click date), not
the day the booking happens. 80% of bookings land on the click day, 58% for PK non-brand, so booking
date would credit pre-switch clicks to the post-switch period. "UK+IE" is every PK non-brand campaign
whose destination is GB, IE or a UK or Irish airport.

## Headline

> **Revised twice after review (sections 7 and 8).** Section 2 folded the 20 Aug cut fortnight into
> "before". The UK share of the revenue loss depends on the source (section 8.1). Seasonality is not
> yet ruled out (section 8.3). Do not quote the UK result outside the team until 8.3 is done.

**The UK is the sharpest PK failure after the switch, and it is a conversion failure, not a traffic one.**

- On campaigns the 20 Aug cut did not touch, UK+IE and the rest lost about the same share of clicks
  at the switch (61% and 65%).
- The UK+IE booking rate went from 0.92% of search visits in the cut fortnight to zero (0 bookings in
  34 days, about 6 expected). The rest improved.
- The UK's share of the lost non-brand revenue is about 100% on Adobe but about 38% to 54% on
  Floodlight. The sources disagree on regional destinations, which is now a separate open thread
  (section 8.2).
- Seasonality, in particular the September UK student intake and VFR travel, could produce the same
  pattern and has not been tested.

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

> **Superseded by section 7.** This table folds the 20 Aug cut fortnight into "before". The GB country
> campaigns were the largest items in the 20 Aug cut, so their drop here is mostly the cut, not the
> switch.

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

- **Two separate failures** *(withdrawn, see section 7)*.
  - The GB country campaigns were almost switched off: clicks fell 96%. *Wrong attribution: their
    spend fell 88% on 20 Aug ($418 to $53 a day for the two campaigns). In Adobe their clicks halved
    on 20 Aug and went to near zero at the switch, so both events contributed.*
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
2. **PK non-brand is much smaller in Adobe than in Floodlight, on bookings.** Adobe shows about 1.8 bookings a
   day before the switch, Floodlight about 9.5. *The eVar84 overwrite explanation given here is
   withdrawn (section 7): in September Adobe revenue matches Floodlight while bookings are 0.3x, which
   points to the two systems counting bookings differently.*
3. **"The bidder chases a value signal that does not track revenue" is too broad.** A destination-mix
   test (each period's search mix priced at pre-period revenue per search) gives a slightly higher
   implied value after the switch: $2.07 to $2.11 per search, against $1.84 to $1.87 before. Outside the UK the
   reallocation looks sound. The problem is specific to the UK.
4. **Revised leading cause:** the VBB value for PK-to-UK searches is too low. Either fallback values
   ($0.50) hit UK routes, or the UK ONDs are mis-priced in the value table. So the bidder dropped
   the GB country campaigns and outbid itself out of the UK queries that convert. *Revised again in
   section 7: a low value alone predicts fewer UK clicks converting better, not worse.*

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

---

## 7. Review and corrections

*A second review checked this note against the SA360 cost data and the 20 Aug cut list. Each point
below was re-checked on the Adobe data with `scripts/pk_cut_adjusted.py`.*

### 7.1 The GB country campaigns were cut on 20 Aug, not at the switch (accepted)

- `Dest|Country|GB` and `O&D|Country|PK-GB` were the top two campaigns in the cut list. Their SA360 spend:
  $320.6 + $97.9 a day before 20 Aug, $38.8 + $14.2 in the cut fortnight, $13.0 + $2.9 after the
  switch. They were 88% of PK's UK-destination spend.
- In Adobe their clicks halved on 20 Aug (about 85 to about 40 a day) and went to near zero at the switch.
  So the cut started it and the switch finished it, but section 2's "96%, a switch failure" was wrong.
- The cut list used in 7.2 is inferred from Adobe: campaigns whose clicks fell 60% or more between
  10-19 Aug and 21-31 Aug (72 campaigns), plus the two GB country campaigns, whose clicks only
  halved. It should be replaced with the actual list when available.

### 7.2 On campaigns the cut did not touch, the UK result holds

Adobe, PK Google non-brand, click date, per day:

| Segment | Period | Clicks | Search visits | Bookings | Booking rate (per search visit) |
|---|---|---:|---:|---:|---:|
| UK+IE, not cut | 13 Jun-19 Aug | 36.8 | 38.6 | 0.31 | 0.80% |
| | 20 Aug-1 Sep | 55.5 | 58.2 | 0.54 | 0.92% |
| | 2 Sep-5 Oct | 21.7 | 22.9 | **0.00** | **0.00%** |
| Everything else, not cut | 13 Jun-19 Aug | 306.6 | 318.2 | 0.50 | 0.16% |
| | 20 Aug-1 Sep | 478.7 | 495.3 | 0.69 | 0.14% |
| | 2 Sep-5 Oct | 167.3 | 174.0 | 0.71 | 0.41% |

- The non-cut UK campaigns (UK city and UK airport-to-airport route campaigns) were unaffected on 20 Aug
  and lost all their bookings at the switch: 28 bookings in the 81 days before, 0 in the 34 days
  after. At the pre-switch rate per search visit, about 6.4 were expected.
- This matches the review's SA360/Floodlight figures (UK not cut: 0.92 to 0.15 bookings a day;
  everything else 2.15 to 2.85). The two sources agree on the direction and the timing.

### 7.3 A conversion story, not a traffic story (accepted)

- Clicks from the cut fortnight to after the switch: UK+IE -61%, everything else -65%. Almost the same.
- Booking rate: UK+IE 0.92% to 0%, everything else 0.14% to 0.41%. On Floodlight the review finds
  1.50% to 0.56% for the UK and 1.13% to 1.65% for the rest.
- Buying fewer clicks usually lifts conversion, because the better queries stay. The rest of PK did
  exactly that. The UK did the opposite. That is the finding to lead with.

### 7.4 The cause hypothesis, revised (accepted)

- A low or fallback VBB value for UK searches predicts that the bidder buys fewer UK clicks, keeps the
  better ones, and converts them at least as well. Relative cost per click fits (UK CPC +85% vs +230%
  elsewhere, per SA360), but conversion going to zero does not.
- Something changed in **which** UK queries or users are bought within the same campaigns and
  keywords. Section 6 points the same way: the keyword mix should have converted better, but the
  route and city keywords stopped converting.
- Working hypothesis: on Maximise Conversion Value with search value as the objective, the bidder wins
  UK auctions that produce many searches but few bookings, for example users who search many dates.
  Bids rising while clicks fall would confirm it.

### 7.5 The eVar84 overwrite explanation does not fit (accepted, replaced)

- In September, Adobe PK non-brand revenue is about 1.0x Floodlight, while bookings are about 0.3x.
  Attribution loss would lower both.
- Average booking value is about $954 in Adobe against about $300 in Floodlight (3.2x). In Germany
  the gap is 1.24x.
- One hypothesis to check, not yet a finding: Floodlight may count tickets (passengers) for PK
  bookings, while Adobe `event27` counts orders. Adobe revenue per ticket in PK is about $278, close
  to the Floodlight average booking value. Large family parties on PK-UK routes would make the gap
  bigger in PK than in Germany. Check the booking activity's counting method and what `event27`
  counts before any of this goes in a report.

### 7.6 Statistical weight (accepted)

- The UK was singled out after looking at the data, across several destination groupings, so a single
  p of 0.02 overstates the evidence.
- The real support is corroboration:
  - the non-cut UK campaigns show the drop independently of the cut;
  - Adobe and Floodlight agree on the timing;
  - the booking rate moves opposite to the rest of the market.
- On the non-cut campaigns, 0 against about 6.4 expected gives p about 0.002, but it should be quoted
  after the corroboration, not instead of it.

### 7.7 Next checks, updated

1. **The non-cut UK campaigns around 2 Sep:** daily max CPC or average CPC, impression share, top
   impression share and budget-lost / rank-lost share, from 20 Aug to 5 Oct. Bids up while clicks
   fall means the bidder outbid itself into a narrower, worse-converting slice of UK demand.
2. **SA360 search terms for the non-cut UK campaigns,** before vs after 2 Sep, with VBB value per
   conversion. This answers which UK queries were bought before and which are bought now.
3. VBB value distribution for UK-destination searches (fallback share, zero share, median), as before.
4. Booking counting: Floodlight booking activity counting method and `event27` definition (7.5).
5. Replace the inferred cut list with the actual 20 Aug list and re-run 7.2.

---

## 8. Second review: revenue split, regional value, seasonality

*Re-checked on Adobe with `scripts/pk_cut_adjusted.py`, which now splits the non-cut campaigns into
UK+IE, other long-haul (North America, Europe excluding UK and IE, Oceania), regional (everything
else) and the legacy generic campaign. The review's Floodlight split uses the real cut list and its
own destination groups, which may differ from these.*

### 8.1 "The UK accounts for essentially all the lost revenue": true on Adobe, not on Floodlight

Adobe, non-cut campaigns, per day:

| Group | Period | Search visits | Bookings (total) | Booking rate | Revenue | Revenue per booking |
|---|---|---:|---:|---:|---:|---:|
| UK+IE | 13 Jun-19 Aug | 38.6 | 0.31 (21) | 0.80% | $205 | $664 |
| | 20 Aug-1 Sep | 58.2 | 0.54 (7) | 0.92% | $753 | $1,399 |
| | 2 Sep-5 Oct | 22.9 | 0.00 (0) | 0% | $0 | |
| Other long-haul | 13 Jun-19 Aug | 135.4 | 0.38 (26) | 0.28% | $401 | $1,050 |
| | 20 Aug-1 Sep | 178.0 | 0.54 (7) | 0.30% | $551 | $1,023 |
| | 2 Sep-5 Oct | 64.1 | 0.29 (10) | 0.46% | $313 | $1,064 |
| Regional | 13 Jun-19 Aug | 164.9 | 0.04 (3) | 0.03% | $58 | $1,320 |
| | 20 Aug-1 Sep | 296.6 | 0.15 (2) | 0.05% | $88 | $571 |
| | 2 Sep-5 Oct | 87.4 | 0.21 (7) | 0.24% | $156 | $757 |
| Generic (legacy) | 13 Jun-19 Aug | 17.9 | 0.07 (5) | 0.41% | $93 | |
| | 2 Sep-5 Oct | 22.5 | 0.21 (7) | 0.92% | $102 | |

- **On Adobe,** net non-brand revenue lost per day is $187 against 13 Jun-19 Aug and $821 against
  the cut fortnight. The UK accounts for $205 and $753, so about 100% in both cases. Other long-haul lost
  $89 and $238. Regional and generic gained.
- **On Floodlight (the review's split),** the UK is $398 of the loss (38%), regional $421 (40%) and
  other long-haul $221 (21%).
- **The headline must name its source.** "The UK is the sharpest failure" holds in both. "Essentially
  all of the loss" holds only in Adobe.

### 8.2 The regional "value failure": real on Floodlight, not visible on Adobe

The review finds regional booking rate up from 1.04% to 1.90% while revenue fell 59%, and reads it as the bidder
buying cheap tickets. On Adobe:

- **Adobe barely sees regional non-brand bookings at all:** 3 in the 68 days before the switch,
  against about 2.3 a day (about 157) on Floodlight. The Floodlight/Adobe booking ratio is about 50x for
  regional, about 3x for other long-haul and about 2.6x for the UK.
- **Floodlight's regional revenue per booking after the switch is about $115.** That is below the
  cheapest Adobe booking from a regional campaign in the whole window ($81 to $2,623, median about
  $480 after the switch). It has the same signature as the post-switch Floodlight bookings with no
  revenue (section 4 of `PK_VBB_DIAGNOSIS.md`).
- **On Adobe, regional revenue rose** ($58 to $156 a day). Revenue per booking fell ($1,320 on 3
  bookings to $757 on 7), which fits the bidder buying cheaper regional tickets, but on counts this
  small it is not evidence either way.

Reading: the regional thread is worth opening, but on Floodlight it rests on a series where Floodlight
sees about 50 times the bookings Adobe does, at a value per booking no real ticket has. Resolve what
Floodlight counts for PK (checks 4 and 5 in 7.7) before treating it as a value-signal failure. If the API
booking actions (Cowork round 2) show the same regional pattern, it stands.

### 8.3 Seasonality is the largest open threat to the UK finding (accepted)

- PK to UK is heavily VFR and student traffic. Students for the September university intake book in
  July and August and stop at term start; VFR families return in late August. A UK-specific booking
  cliff on about 1 September is what both predict, with no bidding change needed.
- The control in section 2 (UK campaigns in SA, MY, SG) does not test this. Those markets have no
  comparable intake or term pattern. Withdrawn as evidence.
- Within 2026 the data cannot separate the two. UK non-cut bookings by click week were 1 to 3 a week through
  June to mid August, then 6 in the week of 24 to 30 Aug, the best week since June. A gradual
  seasonal fade would have shown before the switch; a last-minute intake surge followed by a cliff
  would look exactly like this.
- **Needed:** PK-to-UK non-brand bookings (or PK site bookings to UK, any channel) by week, Jun to Oct
  2025. If September 2025 shows the same cliff, the UK thread closes.

### 8.4 Tracking break: unlikely, but confirm (partly accepted)

- UK clicks still register search visits at the same rate (1.05 per click before and after), so the
  landing and search tagging work for UK traffic.
- The booking confirmation is the same page for every route on the PK site. A UK-only break in
  booking tracking would need route-specific tagging. Adobe also recorded a booking from a PK-IE
  campaign on 3 Oct.
- Floodlight's roughly 5 UK bookings after the switch carry about $25 a day in total, about $170 each.
  These are not UK tickets. On revenue the two sources agree that the UK went to about zero.
- Still worth one question to the web team: any change to UK route pages, fare display or the
  booking flow for UK destinations around 1 to 3 Sep (for example a fare or availability change on
  PK-UK routes, which would also hit conversion without any bidding cause).

### 8.5 Ticket-versus-order hypothesis (withdrawn)

The review is right: if family party size drove the gap, the UK (family VFR) should show the widest
gap. It shows the narrowest (about 2.6x) and regional the widest (about 50x). The gap tracks
destination group, not party size. What Floodlight counts for PK, especially for regional campaigns,
needs checking directly.

### 8.6 Order of next checks

1. **2025 PK-to-UK weekly bookings** (8.3). Decides whether the UK thread survives.
2. **What Floodlight counts for PK bookings** (counting method, attribution, lookback), and whether
   the API booking actions reproduce the regional pattern (8.2). Decides whether the regional
   thread exists.
3. Bids, impression share and search terms for the non-cut UK campaigns (7.7), only if 1 does not
   close the UK thread.
4. Re-run 8.1 with the real cut list and the review's destination groups, so both sources use the
   same definitions.
