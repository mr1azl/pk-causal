# PK VBB: an independent review of the investigation

*7 Oct 2026. Written from the data in `data/` without taking the notes' numbers on trust. Every figure below is
printed by `python scripts/pk_fresh_review.py` (sections A to L); the section letter is given next to each number.
Conventions: Adobe bookings and revenue are credited to the click day; "UK+IE" and "long-haul" follow
`scripts/pk_seasonality_adobe.py`; cost and SA360 clicks come from `data/sa360/round3`; the "Bookings (FL)" and
"Revenue (FL)" columns are not used anywhere. One definition the notes never state: the Adobe pull returns only
tracking IDs that carry a metric, so an Adobe "click" is a click that produced a flight-search visit or a booking.
Adobe counts about 31% of SA360 clicks (26,630 of 82,978 in August). Adobe "bookings per click" is therefore
bookings per searching visit, not per click.*

## 1. The two decisions

**1. Should PK non-brand be switched back from VBB?** Not wholesale, but not for the reason the decision note
gives. Outside the UK there is no gain to protect: on the same spend (about $480 a day) the non-UK campaigns
produced 13% fewer bookings per dollar and 34% less revenue per dollar than in June to August (36 bookings
against 80), and about the same as the cut fortnight (9 bookings). The only measurable effect of the switch is the
GB loss, 1 booking against 5 to 8 expected on about 1,000 searching visits, worth $500 to $1,000 a day of revenue
on $55 to $75 a day of spend. I would move the UK+IE campaigns back to the previous strategy on their own budget
now, which is both the fix and the test, add a target ROAS or CPC cap to the rest, and decide on the rest after
three weeks. Confidence: high that there is no non-UK gain to lose; medium that the switch caused the GB loss
(the plain test gives p 0.01 to 0.03 on one observed booking; the contrast with the rest is much stronger).

**2. Is it safe to roll VBB out to India?** Not as a rollout; yes as a measured test. On actual Adobe orders per
SA360 dollar, VBB is clearly positive in CA (+38% bookings, +70% revenue) and MY (+203%, +169%), negative in SA
(-21%, -36%) and flat to negative in PK (+2%, -17%). Two of four is not a programme result, and every market's
pre/post comparison is confounded by an August booking surge that lifted brand bookings 26% to 58% from July to
August in all six markets. PK also shows that the rule-based value table over-values one destination group by
1.3 to 1.7 times relative to the bookings it produces, while the ML values recorded in the same account are
calibrated within 10% across groups. India should launch with ML or calibrated values, a target ROAS, a holdout,
clean conversion goals and a destination-level booking guardrail on Adobe. Confidence: medium.

## 2. The README section 3 conclusions, tested

| README conclusion | Verdict | My number (script section) |
|---|---|---|
| Total PK paid search held up in September 2026: bookings +3% against -24% in 2025; brand beat its seasonal pattern, non-brand fell as every September | Partly | Reproduced: 961 to 991 in 2026, 903 to 685 in 2025 (C). But PK brand's +6% is what brand did in all six markets (CA +9%, DE +4%, MY +2%, SA -2%, SG +14%), the 2025 brand -24% coincides with the brand account rebuild that September, and non-brand bookings per dollar fell 9% in Sep 2026 against a 62% rise in Sep 2025. Non-brand in the other 2 Sep markets rose (CA +67%, MY +287%) or fell less (SA -18%). True in total, not evidence for VBB. |
| Outside the UK, non-brand bookings held through the switch and improved per click | Partly, and the framing is wrong | Held: 1.06 a day after against 1.18 before on the same $468 to $495 a day (A). Per click improved only because CPC doubled (0.22 to 0.41). Per dollar: bookings -13%, revenue -34% against June to August; +10% and -6% against the cut fortnight. 36 bookings. |
| The UK fall is real and UK-specific: about -50% on the Google tag, about 1 against 5 expected on Adobe and the ledger | Partly | Adobe: 1 against 5.6 expected (p 0.025), or 0 GB against 4.5 at GB's own rate (p 0.011) on 993 searching visits; against the rest, which rose 164% per visit, 1 against 14.7 (D, E). It is GB, not UK+IE: Ireland booked 1 on 75 visits (1.4 expected). The Google tag reads 4.7 per 1,000 clicks in 2 to 19 Sep (no drop, 2.9 bookings) and 1.45 from 20 Sep (3.0 bookings, censored); the -49% is the pooled figure. GB was the only one of 19 destinations below expectation; five were significantly above. |
| Not seasonality, tracking, user location, device, campaign edits, location settings, keyword choice or brand migration: high for each | Partly | Seasonality: agree (14 UK bookings in Sep 2025, rate up; B). Location, device, edits, keywords: agree on what was checked. Tracking: a tag break is unlikely, but a shift of the last click to brand or direct would look identical in Adobe and Floodlight and was not tested. Brand migration: not ruled out; the check used cannot detect it (the brand account records no QR_Booking in any period). Medium, not high. |
| Likely drivers: UK search value most inflated (5.7 against 3.0); reverse and generic queries (6% to 22 to 28%); weaker Google Flights position from mid-August | Partly | Inflation confirmed and sharpened: rule value / booking value 5.0 (UK), 3.8, 2.9; the ML action in the same account gives 2.2, 2.4, 2.0 (F). But the bidder cut UK's spend share from 25% to 10 to 14%, so it did not "keep buying" UK. Query drift: May 2026 had 26% off-target (19% reverse) and converted at 12.8 per 1,000 (G); the on-target queries in Sep to Oct (about 1,500 clicks) produced 0 to 1 bookings. GFS: the rank fall from mid-August is on all PK routes and in 2025 too; July to early August 2026 was unusually strong. |
| The CPC spike and budget-limited serving come from bidding with no ROAS target; seen in all four markets | Partly | The spike is timed to the switch (CPC 0.23 on 1 Sep, 0.98 on 2 Sep, 3.09 on 8 Sep, 0.28 by 30 Sep) and the unswitched remarketing campaign stayed at 0.5 to 0.8 (scratch check on `c1`). No market ran with a target, so "no target" is the obvious lever, not a demonstrated cause. |
| CA -26% and MY -29% are artefacts of the last 16 days of attributed conversions | Agree | Adobe orders per dollar: CA +38%, MY +203% over the full post window (I). PK's own QR_Booking by click date reads 1.46 per 1,000 for the rest in the late period while Adobe reads +64%: the late window of all_conversions is unusable (D). |

## 3. The numbers rebuilt

### 3.1 PK non-brand by click date, UK+IE against the rest (A)

| | Cost a day | Adobe bookings | Bookings a day | Revenue a day | Bookings per $1k | Revenue per $ | CPC |
|---|---:|---:|---:|---:|---:|---:|---:|
| UK+IE 13 Jun-19 Aug | $475 | 44 | 0.65 | $546 | 1.36 | 1.15 | 1.09 |
| UK+IE 20 Aug-1 Sep | $115 | 11 | 0.85 | $1,078 | 7.37 | 9.39 | 0.44 |
| UK+IE 2-19 Sep | $75 | 0 | 0.00 | $0 | 0 | 0 | 2.19 |
| UK+IE 20 Sep-5 Oct | $55 | 1 | 0.06 | $43 | 1.15 | 0.78 | 0.42 |
| Rest 13 Jun-19 Aug | $468 | 80 | 1.18 | $1,213 | 2.51 | 2.59 | 0.22 |
| Rest 20 Aug-1 Sep | $348 | 9 | 0.69 | $639 | 1.99 | 1.83 | 0.20 |
| Rest 2-19 Sep | $476 | 18 | 1.00 | $876 | 2.10 | 1.84 | 1.27 |
| Rest 20 Sep-5 Oct | $495 | 18 | 1.12 | $788 | 2.27 | 1.59 | 0.41 |

The bookings and revenue match analysis 02 section 1 exactly. The cost columns are new. They change the reading:
the rest spent the same after the switch as before the cut and produced the same bookings with less revenue
(revenue per booking $1,031 before, $788 after, on 36 bookings). All PK non-brand: 1.93 bookings per $1k and 1.86
revenue per $ in June to August, 3.32 and 3.71 in the cut fortnight, 1.98 and 1.55 after the switch.

### 3.2 The same months in 2025 (B)

| Segment | Aug 2025 | Sep 2025 | Aug 2026 | Sep 2026 |
|---|---:|---:|---:|---:|
| Brand bookings (per 1,000 searching visits) | 866 (18.6) | 658 (19.2) | 905 (24.3) | 956 (31.0) |
| NB UK+IE | 9 (2.4) | 14 (5.0) | 20 (5.7) | 1 (1.4) |
| NB long-haul | 16 (2.0) | 10 (1.7) | 23 (2.7) | 21 (8.8) |
| NB regional | 12 (0.9) | 2 (0.3) | 11 (0.8) | 6 (1.9) |

Matches analysis 04. Seasonality as a recurring September UK cliff is ruled out on 14 bookings.

### 3.3 Brand and non-brand together (C)

| | Aug 2025 | Sep 2025 | Aug 2026 | Sep 2026 |
|---|---:|---:|---:|---:|
| Total bookings | 903 | 685 (-24%) | 961 | 991 (+3%) |
| Total revenue | $884k | $575k (-35%) | $1,016k | $869k (-14%) |
| Non-brand SA360 cost | $19.5k | $8.8k (-55%) | $24.3k | $16.6k (-32%) |
| Non-brand bookings per $1k | 1.90 | 3.07 (+62%) | 2.31 | 2.11 (-9%) |

Matches analysis 08 section 7.2. Including the two Bing accounts changes nothing (PK Bing non-brand is 0 to 4
bookings a month; all engines together went 1,041 to 1,035 in 2026 and 964 to 750 in 2025).

### 3.4 The UK on each booking measure, per 1,000 SA360 clicks (D)

| UK+IE | Adobe | Floodlight ledger (visit date) | QR_Booking all_conversions (click date) | Google Booking tag (click date) |
|---|---:|---:|---:|---:|
| 13 Jun-19 Aug | 1.48 (44) | 0.27 (8, ledger starts 2 Aug) | 5.28 (157) | 4.55 (135) |
| 20 Aug-1 Sep | 3.27 (11) | 2.08 (7) | 4.75 (16) | 4.99 (17) |
| 2-19 Sep | 0 (0) | 0 (0) | 0 (0) | 4.71 (2.9) |
| 20 Sep-5 Oct | 0.48 (1) | 0 (0) | 0 (0) | 1.45 (3.0) |

Counts in brackets. Two corrections to how the notes read this table. First, Adobe, the ledger and QR_Booking are
three records of the same last-click bookings on the same clicks, so "three sources agree" is one fact measured
three ways, not three confirmations. The ledger and Adobe overlap on about two thirds of their UK rows (each has
four or five the other lacks), and both show zero from post-switch clicks. Second, the Google tag is the only
measure with a different attribution (data-driven, fractional), and it shows no UK drop in 2 to 19 Sep; late
modelled conversions would raise that number, not lower it. Only the censored late period reads low on the tag.
Lag is not the reason: 96% of UK and non-UK bookings arrive within 16 days of the click (L).

## 4. Trying to break the conclusions

### 4.1 Is the UK drop real and large enough to act on?

- **Counts.** After the switch the UK+IE campaigns received 993 Adobe searching visits (2,684 SA360 clicks) and
  produced 1 booking, from an Ireland campaign on 2 Oct. The 2 to 19 Sep period alone is uninformative: 190
  visits, 1.1 expected, 0 seen (p 0.35). The weight is in 20 Sep to 5 Oct: 803 visits, 4.5 expected, 1 seen
  (p 0.06), and that period is right-censored. Pooled: 5.6 expected, 1 seen, p 0.025. On the campaigns the cut
  did not touch, 1 against about 8 expected since 8 June (p 0.002).
- **Look-elsewhere.** Four destination groups and 19 destination countries with two or more bookings were
  examined (E). GB is the only one significantly below its pre-switch rate (0 against 4.5, p 0.011). US, AU, DE,
  MY and the generic campaign are significantly above theirs. Against a null of "nothing changed anywhere",
  one country at p 0.01 out of 19 is close to what chance produces. Against the observed behaviour of the rest,
  which converted 2.6 times better per visit after the switch, the UK's expected count is 14.7 and the deficit is
  far beyond chance. The honest statement is: the UK is the one segment that moved the other way, and the
  evidence that it moved down at all rests on one booking against five to eight expected.
- **GB, not UK+IE.** Ireland campaigns booked 9 times on 490 visits before and once on 75 after (1.4 expected).
  The zero is on GB destinations.
- **Size.** UK revenue was $546 a day in June to August and $1,078 a day in the cut fortnight on $115 a day of
  spend. After the switch it is $0 to $43 a day on $55 to $75. The loss is $500 to $1,000 a day of Adobe revenue,
  or 15 to 30 bookings a month, against 35 non-brand bookings in September. The fix is cheap and reversible,
  so the bar for acting is low even though the evidence is thin.

### 4.2 Is "total PK held up in September" sound?

No, as evidence about VBB. The total held because brand bookings rose 6% while non-brand fell 38%.

- **Brand did the same everywhere.** Brand bookings August to September 2026: CA +9%, DE +4%, MY +2%, PK +6%,
  SA -2%, SG +14% (C). PK brand's conversion rate did jump more than most (24.3 to 31.0 per 1,000 visits; SA
  51.3 to 58.4, SG 63.0 to 69.4, the others flat), but it only returned to its May level (30.6).
- **The 2025 baseline is a restructure month.** The brand account was rebuilt during September 2025: the legacy
  Hero campaign and the new pipe-named one both carry clicks that month, and brand clicks fell 26%. The -24%
  "seasonal" fall is partly that. One prior year is a weak baseline either way.
- **Non-brand did worse than its own September, per dollar.** In September 2025 non-brand spend fell 55% and
  bookings 27%, so bookings per dollar rose 62%. In September 2026 spend fell 32% and bookings 38%, so bookings
  per dollar fell 9% and revenue per dollar fell 21%. "Non-brand fell about as every September" is true of the
  count and false of the efficiency, and efficiency is what a bidding strategy is for.
- **Adobe attribution.** By booking month instead of click month the brand numbers are 923 to 966 (+5%). The
  right-censoring of September 2026 clicks works against "held up", not for it. No artefact here.
- **Halo.** 207 extra brand bookings in September 2026 above the August rate cannot be separated from a few UK
  bookings that may have finished on a brand click. The data in the repo cannot tell, and the brand-search-terms
  check does not help because a UK booking through brand does not need a UK word in the query.

### 4.3 Does the proposed mechanism explain the drop?

Three parts were proposed. One is strengthened, one is contradicted, one is overstated.

- **UK search value is inflated: strengthened, and a fix exists in the account.** For 13 Jun to 1 Sep, rule-based
  search value per click over QR_Booking value per click is 5.0 for UK+IE, 3.8 long-haul, 2.9 regional (F). The
  PK account also records `QR_FlightSearch_VBB_ML` on every search (98,606 against 98,592 rule-based). Its ratio
  to booking value is 2.2, 2.4 and 2.0: calibrated within 10% across groups. ML values a UK search at $26.8
  against the rule's $61.2, a long-haul search at $25.5 against $40.6. The rule table tells the bidder a UK
  click is worth 1.45 times a long-haul click; bookings say 1.1; ML says 1.0. Nobody in the investigation used the
  ML action.
- **"So the bidder keeps buying UK clicks": contradicted.** UK's share of spend was 50% before the cut, 25% in
  the cut fortnight, 14% in 2 to 19 Sep and 10% from 20 Sep (A). The bidder bought less UK, not more. After the
  switch it put spend back into the cut long-haul and regional country campaigns ($4 to $68 and $6 to $52 a
  day) but not into the cut UK campaigns, two of which are the GB country campaigns ($58 to $8) (K). What the value signal can still do is change which
  UK clicks are bought. One observable did move only for the UK: searches per click rose from 0.44 to 0.52 on
  the VBB action and from 0.35 to 0.46 on Flight Search (+18% and +28%), while long-haul and regional stayed
  flat (H). Analysis 06 said every observable property of UK traffic was back to normal; this one is not. It is
  consistent with a value bidder selecting UK clickers who are more likely to search, and it is a small effect.
- **Reverse-direction and generic queries: contradicted by May 2026.** On the UK campaigns the cut did not touch,
  off-target clicks were 26% in May (19% reverse direction) and those campaigns converted at 12.8 bookings per
  1,000 visits, the best month in the window (G). In September to October off-target is 22 to 28%, mostly generic
  terms on one broad-match Manchester campaign, and conversion is 0 to 2.6. The 72 to 78% of clicks that are still
  outbound or UK-only queries, about 1,500 in the search-terms report, produced 0 to 1 bookings. Query drift can
  explain a quarter of the deficit at most. Adding negatives is still worth doing; it is not the mechanism.
- **Google Flights position: overstated.** QR's average rank on PK-UK was 2.7 to 2.8 in late July to early
  August 2026, better than the 3.3 to 3.7 of 2025, then 4.4 to 4.9 from 23 Aug against 3.9 to 4.3 in 2025. Other
  PK routes moved the same way in both years (4.6 to 4.8 then 5.1 to 5.8 in 2026; 4.7 to 4.9 then 5.2 to 5.8 in 2025). The UK-specific residual is about half
  a rank. Selection rate when shown went from above 2025 (0.39 to 0.43 against 0.30 to 0.36) to slightly below it (0.18 to 0.23 against 0.22 to 0.25). The
  GFS weeks of 2 to 30 Aug 2026 hold 2 to 6 days of data each, which the GFS note does not mention. From 20 Sep
  QR was the cheapest much less often on all PK routes (UK 0.38 then 0.23; other 0.36 then 0.17), and the
  non-UK campaigns kept booking through it.
- **What else could it be.** (a) Chance on one booking. (b) A shift in where GB bookings finish: a non-brand
  UK click followed by a brand or direct booking is credited to brand in Adobe and in Floodlight alike, and the
  Google tag, which would credit the UK click a share, is the one measure that did not fall in 2 to 19 Sep.
  (c) A GB-specific demand or fare event in September 2026 that GFS, with QR rows only, cannot show. None of
  these is tested by anything in the repo.

### 4.4 Explanations ruled out too quickly

- **Brand migration.** Listed as ruled out at high confidence in the README; the decision note itself says the
  check cannot detect it. The Floodlight conversion rows carry `FlightDestination` and `FlightOrigin` custom
  variables (`d6_conversion_custom_variables.csv`), so brand-account QR_Booking rows to GB destinations by week
  would settle it. Not pulled.
- **A new primary conversion action on the cut day.** `Flight Search (TEST Sept2026)` first records on 20 Aug
  2026 and runs at 0.4 to 0.7 per click after the switch, more than `Flight Search` itself (J, H). The first
  review noted it is live and primary. Nobody checked whether it sits in the portfolio's conversion goal. If it
  does, the pre-switch bidder's objective changed on 20 Aug and the "cut fortnight" is not a clean before.
- **The cut itself.** The notes treat 20 Aug as a budget cut on about 52 campaigns. From SA360 cost it is 36
  campaigns at $3 or more a day going from $743 to $67 a day, almost all country campaigns, in all three groups
  (K). The README also says PK shares one budget of about $490 a day. Both cannot be true in the same form: a
  shared budget cannot be cut on specific campaigns. Whether the 20 Aug event was per-campaign budgets, a shared
  budget halved and the old bidder starving the country campaigns, or something else, is not recorded, and
  `last_modified_time` on the campaigns was overwritten by the 2 to 3 Sep switch.
- **Competitors and fares.** GFS has no competitor rows. The `operating_airline` column the GFS note mentions
  was not queried. The commercial question about PK-UK fares and capacity was raised in three notes and never
  answered.

### 4.5 The CPC spike

The spike is the switch. Portfolio CPC was 0.17 to 0.28 from 21 Aug to 1 Sep, 0.98 on 2 Sep, 1.91 on 3 Sep,
peaked at 3.09 on 8 Sep and declined to 0.28 by 30 Sep; spend sat at the $490 cap from 3 Sep; the one
non-brand campaign outside the portfolio (`_PK-Generic-RMKT_Exact`, Maximise Conversions, no target) stayed at
0.44 to 0.96. SA, CA and MY show the same shape. So it is not seasonal auction pressure and not the cut. Whether
a target ROAS would have prevented it cannot be shown from these four markets, because none had one; a target or
a CPC cap is the standard way to bound a learning period, which is reason enough to set one.

## 5. What the investigation never looked at, and what it got wrong

New findings:

1. **The ML value action exists in PK and is calibrated.** See 4.3. It is the most direct fix for the one
   mechanism that survives, and the most useful thing to check before India.
2. **Per-dollar results across the four 2 Sep markets on Adobe orders** (I): CA +38% bookings and +70% revenue
   per dollar, MY +203% and +169%, SA -21% and -36%, PK +2% and -17%. SA is the market the agent called "the
   control that exonerates the strategy"; on orders per dollar it is the worst of the four. PK is the only
   market whose spend fell into the switch (-42%); the others' rose 15% to 50%.
3. **UK searches per click rose 18% to 28% after the switch and nowhere else** (H).
4. **Ireland did not go to zero** (E). The finding is about GB.
5. **The bidder reallocated away from the UK**, including from the GB country campaigns it could have refunded
   (K). "Keeps buying UK" is wrong.
6. **May 2026 UK campaigns ran 26% off-target queries and converted at their best rate** (G).
7. **A primary conversion action started on the cut day** (J).
8. **Adobe "clicks" are searching visits.** Not an error, but it should be stated wherever a per-click rate is
   quoted, and it means SA360 clicks are the right denominator for cost.
9. **Bing and Performance Max are not a factor in PK.** Bing non-brand is 0 to 4 bookings a month; PK has no
   Performance Max rows in Adobe. India does have Performance Max (19% off-target per analysis 09).
10. **Lag and day of week do not explain anything.** Booking lag is the same for UK and non-UK (96% within
    16 days); UK click share by weekday is flat apart from the 2 to 3 Sep launch days.
11. **Revenue per booking.** Non-UK revenue per booking fell from $1,031 to $788 after the switch (80 and 36
    bookings), which is why non-UK revenue per dollar is down 34% while bookings per dollar are down 13%. Brand
    revenue per booking fell 17% in September 2026 and 14% in September 2025, so that part is seasonal.
12. **GFS August 2026 weeks are partial** (2 to 6 days of data).

Where the investigation is wrong or overstated:

- "Switching everything back would give up the non-UK gains" (08 section 1): there are no non-UK gains on any
  per-dollar measure.
- "On three sources, UK bookings from post-switch clicks are zero" (03): one last-click fact recorded three
  times; the one differently attributed measure did not fall in the first switch period.
- "Brand beat its seasonal pattern by about 30 points" (08 section 7.2): brand rose in every market; the 2025
  baseline contains the brand rebuild.
- "Non-brand fell about as much as it does every September" (08): per dollar it fell while September 2025 rose.
- "The bidder keeps buying UK clicks" and "reverse-direction queries tripled" as the cause (08 section 4): the
  spend share fell; May 2026 shows the query mix converting normally.
- "Every observable property of the traffic is back to normal except the outcome" (06 section 2): searches per
  click are up for the UK only.
- "Not brand migration: high" (README section 3): untested.
- "High" for the ROAS-target explanation of the CPC spike: the switch and its learning period are demonstrated;
  the target is an inference.
- The remaining UK drivers are described as "consistent with the data". Two of the three are not.

What holds: the Adobe tables in 02, 04 and 08; the seasonality check; the Floodlight ledger reading and the
cross-device explanation of inflated counts; the CA and MY artefact; the search-value inflation for the UK; the
list of things that did not change in the UK campaigns.

## 6. The checks that would most change the decision, in priority order

1. **Move the 66 UK+IE campaigns back to Maximise Conversions on flight searches, on their own budget of about
   $60 to $70 a day, for three weeks.** Keep the rest on VBB with a target ROAS set from the last eight weeks'
   value per dollar. Read on Adobe and the ledger by click date. At the pre-switch rate, 700 to 1,000 searching
   visits should give 4 to 8 bookings; 0 to 1 means the cause is outside bidding and the UK finding should be
   dropped from the India decision. This answers decision 1 directly and is cheaper than any further analysis.
2. **PK-site bookings to GB destinations by week and channel, 2025 and 2026.** From Adobe: bookings (event27) and
   revenue by flight destination and by marketing channel (paid search brand, paid search non-brand, direct,
   organic, other), 1 Jun to 5 Oct in both years. From SA360: QR_Booking conversion rows for the PK brand
   account with the `FlightDestination` custom variable, same window. If GB bookings fell on every channel, the
   cause is demand or fares; if they moved to brand or direct, it is attribution or migration; if only non-brand
   lost them, it is the bidding. This decides whether check 1's result generalises and whether the readout's
   brand control is contaminated.
3. **Switch the PK portfolio's value to the ML action, or scale the UK route values by about 0.45, before any
   re-inclusion of the UK, and run the same calibration table for India before launch.** Requires confirming
   that `QR_FlightSearch_VBB_ML` can be set as the portfolio goal in PK. Alongside it, two configuration
   questions for the SA360 agent: the portfolio's conversion goal composition (is `Flight Search (TEST
   Sept2026)` in it, since when), and the `campaign_budget` resources for the PK non-brand campaigns (what the
   20 Aug cut was mechanically).

## 7. Data not in the repo that I would need, and why

| Data | Why |
|---|---|
| Adobe PK bookings and revenue by week, flight destination and marketing channel, Jun to Oct 2025 and 2026 | The only way to tell a GB demand fall from a channel shift from a bidding effect (check 2). |
| SA360 `conversion` rows for QR_Booking on the PK brand account with FlightDestination and FlightOrigin, 1 Jun to 5 Oct 2026 | Direct test of brand migration; the current `d6` check cannot see it. |
| The PK portfolio's conversion goal composition and the settings and history of `Flight Search (TEST Sept2026)` | A primary action went live on the cut day; the before period may not be clean. |
| `campaign_budget` for every PK non-brand campaign, with amounts, shared flag and `last_modified_time` | To know what the 20 Aug cut was. |
| Whether `QR_FlightSearch_VBB_ML` is eligible as a bidding goal in PK, and its model's training target | Needed before recommending it as the fix. |
| DE and SG non-brand daily cost, 13 Jun to 5 Oct 2026 | To put the two 30 Jul markets on the same orders-per-dollar basis as the other four. |
| GFS competitiveness rows with `operating_airline` for PK-UK routes | The only way to see a competitor move on PK-UK. |
