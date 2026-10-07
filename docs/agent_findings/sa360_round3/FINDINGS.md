# PK round 3: findings

Scope: Google Ads account `Google-GCCLI-PK-EN` (4851538229), USD, Asia/Qatar.
Written 2026-10-07. Full method, row counts and errors in `LOG.md`.

Context being tested: PK non-brand moved to value based bidding on 2 September 2026, a budget cut
hit around 20 August 2026, and Adobe shows UK destination non-brand bookings at zero after
2 September.

---

## A. Is the UK drop seasonal? No.

**In 2025 there was no September drop.** UK+IE non-brand bookings by month:

| month | 2025 | 2026 |
|---|---|---|
| June | 21.3 | 152.5 |
| July | 42.6 | 94.1 |
| August | 33.3 | 110.6 |
| **September** | **39.3** | **5.9** |
| October (2026 partial) | 42.9 | 2.0 |

September 2025 sits **above** August 2025, and October 2025 is the strongest month of the five.
Weekly on aligned ISO weeks, 2025 weeks 36 to 44 run 8.6, 5.0, 10.0, 13.7, 8.0, 14.0, 11.0, 6.0,
5.9: flat throughout the window where 2026 collapses. The calendar is not the cause.

September 2026 is a **95 percent** fall against August. The other groups fell too but far less:
long-haul -65 percent, regional -71 percent. UK+IE fell roughly thirty points harder than either.

Two things found while setting this up that change how the numbers should be read.

The brief's non-brand filter excludes **zero** campaigns, and that is correct rather than a bug:
no campaign name in this account contains "brand" at all, because brand sits in the separate
account 1423602235. The whole of 4851538229 is non-brand by construction.

The naming convention in the brief covers only **589 of 15,868** campaigns. In the 2025 window,
**71 percent of spend sits on legacy names** such as `_PK-Country-XXX-AU-EN_phrase` and
`_PK-O&D-LHE-LHR-EN_exact`. A destination parser written only for the pipe form would have
silently dropped most of 2025 and produced a confident, wrong seasonality answer. The parser in
`lib_sa360.dest_code()` handles both forms: 289 destination codes, one campaign legitimately
without a destination, no unclassified residual.

UK+IE also grew as a share of PK non-brand spend, from **13.5 percent in 2025 to 39.5 percent in
2026**, so the market that collapsed is the one that had been scaled up hardest.

---

## B. What one PK Floodlight booking is, and why regional overstates

**One row is one transaction with quantity one.** All 89 Floodlight booking rows in the window
carry `conversion_quantity` of exactly 1000, the field being scaled by 1000, with no variation at
all. Not a basket of tickets, not a passenger count. Quantity carries no information here.

It is also not a duplicate problem. **1 of 88 distinct order IDs appears twice**, and both of its
rows carry revenue. Revenue is clean: 2 zero revenue rows out of 89, status `ENABLED` and
attribution `VISIT` on all 89, and `floodlight_original_revenue` agrees with
`conversion_revenue_micros` on every row.

### Why regional shows far more Floodlight bookings than Adobe

Two gaps that compound.

**First, two different measurement systems are being added together.** `QR_Booking` (id 415339895)
is the real Floodlight transaction tag, 90 day lookback, activity 2648297. `Booking`
(id 207919651) is a Google Ads **WEBPAGE** conversion with `GOOGLE_SEARCH_ATTRIBUTION` and a
**30 day** window. It is not a Floodlight tag, it produces **zero** conversion rows, and it
contributes 279 conversions and 288,826 USD. Worse, **three separate conversion actions are all
named `Booking`** with different attribution models, so any report segmenting on action name
merges them into one line.

**Second, the attributed number is multiples of the transaction ledger, and unevenly so.**

| group | `QR_Booking` all_conversions | actual transaction rows | inflation |
|---|---|---|---|
| UK+IE | 57.0 | 14 | 4.1x |
| long-haul | 74.0 | 24 | 3.1x |
| **regional** | **127.0** | **13** | **9.8x** |

Regional is inflated roughly three times harder than long-haul. In total the two actions report
**588 bookings and 685,419 USD** where the Floodlight ledger holds **89 transactions and
93,129 USD**.

So "Floodlight bookings" as reported is an attributed, modelled, cross device number from two
systems, and the regional campaigns are where the modelling adds the most. Adobe is counting
orders. The two will never agree, and the gap is widest exactly where the brief noticed it.

### The UK number

| group | period | `QR_Booking` | `Booking` | total |
|---|---|---|---|---|
| UK+IE | pre 2 Sep | 57.0 | 55.6 | 112.6 |
| UK+IE | **from 2 Sep** | **0.0** | 5.9 | **5.9** |
| long-haul | pre 2 Sep | 74.0 | 79.8 | 153.8 |
| long-haul | from 2 Sep | 24.0 | 42.3 | 66.3 |
| regional | pre 2 Sep | 127.0 | 58.3 | 185.3 |
| regional | from 2 Sep | 17.0 | 17.7 | 34.7 |

UK+IE Floodlight bookings go to **exactly zero** after 2 September. One single UK+IE transaction
row exists in the whole period to 5 October. The 5.9 still showing are entirely the WEBPAGE
action. Adobe is right, and the SA360 number that disagrees is the one coming from the non
Floodlight tag.

---

## C. UK cost per click and impression share at the switch

**Direct answer.** Cost per click **rose**, clicks **fell**, the top and absolute top
**impression share** metrics **fell**, and the lost share moved decisively onto **budget**, not rank.

| UK+IE, impression weighted | 20 Aug-1 Sep | **2-19 Sep** | change |
|---|---|---|---|
| cost per click | 0.444 | **2.187** | **x4.9** |
| clicks | 3,366 | **616** | -82% |
| impression share | 67.8% | 27.3% | -40 points |
| top impression share | 60.6% | 24.9% | -36 points |
| absolute top impression share | 18.6% | 15.0% | -4 points |
| lost to **budget** | 10.5% | **72.0%** | **+61 points** |
| lost to **rank** | 21.7% | **0.7%** | -21 points |

Keyword level is sharper: impression share 67.1 to **12.3 percent**, lost to budget 11.8 to
**87.6**, lost to rank 21.0 to **0.2**.

### The top share answer needs one correction to be useful

Top and absolute top impression share are shares of the **eligible market**, so they fall
mechanically when impression share falls. Dividing each by impression share gives position on the
impressions actually won, and that tells the opposite story:

| UK+IE | impr share | top / own impressions | **abs top / own impressions** | CPC |
|---|---|---|---|---|
| 20 Aug-1 Sep | 67.8% | 89.4% | **27.4%** | 0.444 |
| **2-19 Sep** | **27.3%** | 91.2% | **55.0%** | **2.187** |

**Absolute top placement on the impressions it won doubled**, 27.4 to 55.0 percent, while
impression share fell by about 60 percent. So paying 4.9 times more per click did buy much better
position, on far fewer impressions. The bidder traded breadth for position against a fixed budget.
That is the honest reading: the top share metrics fell as reported, but position improved.

### The loss was on budget

Lost to rank goes to **0.7 percent, then 0.0**. UK campaigns were not outbid. They won essentially
every auction they entered and ran out of money. Non UK rank lost never reaches zero over the same
window, 18.9 percent in September and 4.1 now, so this is sharper on UK than anywhere else.

By 20 September to 5 October UK recovers to 55.2 percent impression share at a cost per click of
0.422, close to pre switch, but **lost to budget is still 44.8 percent with rank lost at 0.0**.
The constraint is still the budget.

**Clamped values**: 1 to 3 percent of impressions, in the 2 to 19 September period only, on
`impr_share` and `budget_lost`. Flagged in `c3_period_summary.csv` and
`c2_ukie_cut_vs_rest.csv` as explicit columns rather than averaged in silently. Every other cell
is a real measurement.

### The 20 August cut and the 2 September switch are separable

The two GB country campaigns named in the brief carried **88 percent** of UK+IE spend before the
cut (28,464 of 32,298) and the cut effectively shut them down: 689 USD over the next 13 days,
then 470, then 69.

The other **64** UK+IE campaigns were not cut. Their spend is flat across the last three periods,
804, 877, 804. They show the **same September signature anyway**:

| UK+IE rest, never cut | 20 Aug-1 Sep | 2-19 Sep |
|---|---|---|
| cost per click | 0.389 | **2.182** (x5.6) |
| lost to budget | 6.3% | **75.3%** |
| lost to rank | 23.9% | **1.1%** |
| abs top / own impressions | 28.0% | **60.5%** |

So the switch effect reproduces cleanly in campaigns the budget cut never touched. September is
not an artefact of the August cut.

The two events also have **opposite signatures**, which is worth keeping distinct. At the 20 August
cut, UK daily spend fell from 475 to 115, cost per click **fell** from 1.087 to 0.444, and lost to
rank **rose** from 14.9 to 21.7 percent: bidding less and losing auctions. The 2 September switch
is the mirror image.

---

## C4. Why reported bookings are a multiple of the Floodlight ledger

| group | ledger rows | all_conversions | cross-device | same device | all / ledger | **same device / ledger** | cross-device share |
|---|---|---|---|---|---|---|---|
| UK+IE | 14 | 57.0 | 28.0 | 29.0 | 4.07x | **2.07x** | 49.1% |
| long-haul | 24 | 74.0 | 42.0 | 32.0 | 3.08x | **1.33x** | 56.8% |
| **regional** | 13 | 127.0 | **105.0** | 22.0 | **9.77x** | **1.69x** | **82.7%** |
| **total, both periods** | **89** | **310.0** | **185.0** | **125.0** | **3.48x** | **1.40x** | **59.7%** |

**Cross-device modelling is the whole of it.** It is 59.7 percent of all `QR_Booking` conversions,
and removing it collapses the gap from **3.48x to 1.40x** against the transaction ledger.

Regional is the extreme: **105 of its 127 attributed conversions are cross-device, 82.7 percent**,
against 49.1 for UK+IE and 56.8 for long-haul. Strip them and regional falls from 9.77x to
**1.69x**, in line with everything else.

So the 9.8x on regional is not a tagging fault, not duplication and not a zero revenue problem. It
is Google modelling journeys that start on one device and finish on another, at roughly half again
the rate it does for UK and long-haul traffic. Adobe counts the completing session. The residual
1.4x is ordinary attribution modelling and fractional credit.

Two oddities to flag: **UK+IE from 2 September reports 0.0 all_conversions while one real ledger
transaction exists**, and long-haul reports zero cross-device conversions at all in that period.

---

## Caveats and what is not covered

- Google Ads only. The two Bing PK accounts are out of scope.
- C4 covers `QR_Booking` only, so the WEBPAGE `Booking` action is excluded from the cross-device
  decomposition. That action produces no ledger rows at all, so it has nothing to compare against.
- The keyword pull in C2 is per period, not per day. C3 needs only period aggregates and the daily
  version would be two orders of magnitude larger; the script can produce it by restoring
  `segments.date` to the SELECT.
- `Bookings (FL)` and `Revenue (FL)` are not reachable through the API. The account exposes only
  two custom columns, `Bookings` and `Flight Searches`, both counts referencing
  `metrics.all_conversions`, neither carrying revenue. Logged as unavailable rather than
  substituted with something that looks similar.
- Clamped impression share values affect 1 to 2 percent of impressions, in the 2 to 19 September
  period only. They are flagged in `c3_period_summary.csv` rather than averaged in silently.
- The conversion row window is 2026-08-01 to 2026-10-05, so B compares pre and post 2 September
  within that window and does not extend back to June.
- Long-haul and regional membership is written out code by code in `lib_sa360.py` so the boundary
  can be audited. Six further UK and Ireland codes found in the data (LON, GLA, BHD, NCL, ABZ, ORK)
  are reported separately rather than folded into UK+IE, together 214 USD in 2025 and 0 in 2026.
