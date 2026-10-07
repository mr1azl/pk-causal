# Round 4 log

Account 4851538229, PK non-brand. Periods: 13 Jun-19 Aug, 20 Aug-1 Sep (cut), 2-19 Sep (switch),
20 Sep-5 Oct. UK+IE kept split into "GB country (cut 20 Aug)" (2 campaigns) and "UK+IE rest" (64).
`lib_sa360.py` copied from round 3, extended with `segment()`, `PERIODS` and `GB_CUT_PREFIX`.

---

## D1. Where the clickers are

Scripts `d01_geo_pull.py`, `d02_geo_summary.py`, `d03_location_settings.py`.
Dates actually returned **2026-06-13 to 2026-10-05, 113 distinct days**, no gaps on either pull.

| file | rows |
|---|---|
| `data/raw/d1_geo_target_country.jsonl` | 86,865 |
| `data/raw/d1_user_location.jsonl` | 110,661 |
| `data/raw/d1_geo_constants.jsonl` | 203 of 205 criterion IDs resolved |

Both `segments.geo_target_country` and `user_location_view` return data. `user_location_view` is
the one that answers the question, since it carries the user's physical country.

### Share of clicks by the user's physical country

| segment | period | clicks | outside Pakistan |
|---|---|---|---|
| GB country (cut) | 13 Jun-19 Aug | 20,152 | 24.9% |
| GB country (cut) | 20 Aug-1 Sep | 1,295 | 21.4% |
| GB country (cut) | **2-19 Sep** | 214 | **43.5%** |
| GB country (cut) | 20 Sep-5 Oct | 110 | **20.0%** |
| UK+IE rest | 13 Jun-19 Aug | 9,568 | 14.5% |
| UK+IE rest | 20 Aug-1 Sep | 2,069 | 13.7% |
| UK+IE rest | **2-19 Sep** | 402 | **31.6%** |
| UK+IE rest | 20 Sep-5 Oct | 1,958 | **7.6%** |
| long-haul | 20 Aug-1 Sep | 7,282 | 8.6% |
| long-haul | 2-19 Sep | 1,758 | 24.2% |
| long-haul | 20 Sep-5 Oct | 8,275 | 11.4% |
| regional | 20 Aug-1 Sep | 14,123 | 2.3% |
| regional | 2-19 Sep | 3,867 | 16.5% |
| regional | 20 Sep-5 Oct | 9,818 | 3.5% |

The out of country share roughly **doubles in the switch window and then reverts**. UK+IE rest
ends at 7.6 percent, **about half its own pre switch level**. And the same spike and reversion
happens in long-haul (8.6 to 24.2 to 11.4) and regional (2.3 to 16.5 to 3.5), so it is not a UK
specific effect. It tracks the collapse in volume, not a change in who the campaigns reach.

Top non-Pakistan country is the United Kingdom in every UK+IE period, as expected for a UK
destination campaign: 4,023 clicks pre cut on the GB country campaigns, 79 in the switch window,
20 after. Nothing unusual appears in the tail: Ireland, Saudi Arabia, UAE, India, Spain, Canada,
all small.

### Location settings, active campaigns only

Restricted to the **486 campaigns with impressions** in the window, because the full non removed
set includes 3,190 paused legacy campaigns that drag the comparison:

| segment | PRESENCE_OR_INTEREST | PRESENCE |
|---|---|---|
| GB country (cut) | 2 | 0 |
| UK+IE rest | 64 | 0 |
| long-haul | 262 | 0 |
| regional | 157 | 0 |
| no destination | 0 | 1 |

**Every active PK non-brand campaign is `PRESENCE_OR_INTEREST` with negative `PRESENCE`**, 485 of
486. UK+IE is identical to the rest of the account. The mixed 60/40 picture seen before
restricting to active campaigns is entirely paused legacy campaigns.

**These are attributes, so the API returns the CURRENT value only.** A date range does not time
slice them. Nothing here can establish what the setting was in August, only what it is now.

### Targeted locations

21,038 LOCATION criteria across PK non-brand, 13 distinct locations. Every campaign targets
**Pakistan at country level**. A subset also carries positive city targeting (Islamabad, Lahore)
and negative city exclusions (Faisalabad, Islamabad, Karachi, Lahore, Multan, Peshawar, Sialkot),
which is a geo split structure, present in UK+IE and in long-haul and regional alike. No campaign
targets the UK or any destination market.

### One field reported but not interpreted

`user_location_view.targeting_location` looked like a presence against interest signal. It is not
safely readable as one. Checking the keys: of 46,530 campaign by date by country keys, **13,470
carry both a true and a false row for the same country**, and Pakistan itself has 15,356 keys with
a false row against 18,063 with a true row. The field splits a single country into two rows, so
"outside a targeted location" cannot be inferred from it. The split is written to
`data/clean/d1_targeting_location_split.csv` for completeness and is not used in any conclusion.

---

## D3. What changed in the UK+IE campaigns, 15 Aug to 5 Oct 2026

Scripts `d04_change_audit.py` plus the inventory step. Scope: the **66 UK+IE campaigns with
impressions** in the window.

`change_event` does not exist in this API, so `last_modified_time` is the only record available.
It gives the date of the **most recent** change per object, not a history, so an object edited
twice shows only the later edit. That is a real limit on this answer and is stated as such.

| level | objects | modified 15 Aug to 5 Oct | when |
|---|---|---|---|
| campaign | 66 | **66** | 12 on 2 Sep, 54 on 3 Sep |
| ad group | 198 | **72** | all on 25 Sep |
| keyword (`ad_group_criterion`) | 1,188 | **0** | 1,170 on 28 Apr, 18 on 22 May |
| campaign criterion | 3,476 | **0** | bulk Aug and Dec 2025, 198 on 12 Jul 2026 |

**138 objects in total, and 66 of them are the bid strategy switch itself.**

### The 25 September ad group change is not a change in anything live

All 72 are **PAUSED**, and across the entire 13 Jun to 5 Oct window they carried
**0.00 USD, 0 clicks and 0 impressions**. The other 126 ad groups are ENABLED and carried all of
it, 36,011 USD and 35,770 clicks. This is housekeeping on ad groups that were already dormant,
and it is the same 25 September action seen across the wider portfolio in round 3.

### Keyword inventory, UK+IE

1,188 criteria, and the picture is completely static:

- **all 1,188 ENABLED**, no paused, no removed
- **zero negatives**
- match types: 654 BROAD, 534 PHRASE
- created 2025-08-22 (1,170) and 2026-05-21 (18)
- **not one keyword modified after 22 May 2026**

No keyword was added, paused, removed or had its match type changed in the window. No negative
keyword was added. No location, audience or bid modifier criterion was touched.

### Conclusion for D3

**Nothing was changed in the UK+IE campaigns between 15 August and 5 October other than the bid
strategy on 2 and 3 September, and the pausing of 72 already dormant ad groups on 25 September.**

Written as a negative result because it eliminates a class of explanations: the UK zero is not
caused by a keyword cull, a new negative, a match type change, a location edit, an audience change
or a bid modifier. Subject to the caveat above that `last_modified_time` hides an earlier edit
when an object was touched more than once.

---

## D2. Device

Script `d05_device.py`. Two queries per chunk, joined on date and campaign, since
`conversion_action_name` forbids cost and clicks in the same SELECT.
`data/raw/d2_device_traffic.jsonl` and `d2_device_conv.jsonl`, 13 Jun to 5 Oct.

Conversions **are** segmentable by device, so QR_Booking by device was pulled as asked.

### Device mix of clicks

| segment | period | clicks | mobile | desktop | mobile CPC | desktop CPC |
|---|---|---|---|---|---|---|
| GB country (cut) | 20 Aug-1 Sep | 1,297 | 91.3% | 8.2% | 0.510 | 0.769 |
| GB country (cut) | 2-19 Sep | 214 | 87.4% | 11.7% | 2.046 | 3.392 |
| GB country (cut) | 20 Sep-5 Oct | 110 | 75.5% | 21.8% | 0.366 | 1.490 |
| UK+IE rest | 20 Aug-1 Sep | 2,069 | 89.2% | 10.5% | 0.368 | 0.565 |
| UK+IE rest | 2-19 Sep | 402 | 87.3% | 11.7% | 1.678 | 6.065 |
| UK+IE rest | 20 Sep-5 Oct | 1,958 | 84.4% | 15.0% | 0.316 | 0.929 |
| long-haul | 20 Aug-1 Sep | 7,282 | 87.5% | 12.1% | 0.196 | 0.360 |
| long-haul | 20 Sep-5 Oct | 8,275 | 82.8% | 16.9% | 0.308 | 1.189 |
| regional | 20 Aug-1 Sep | 14,123 | 91.4% | 8.5% | 0.166 | 0.296 |
| regional | 20 Sep-5 Oct | 9,818 | 84.9% | 14.8% | 0.254 | 0.801 |

Mobile share drifts down by a few points for UK+IE, 89.2 to 87.3 to 84.4 for the rest bucket. The
**same drift happens in every segment**, long-haul 87.5 to 82.8 and regional 91.4 to 84.9, so it is
not UK specific and it is small.

### QR_Booking by device

UK+IE has **no QR_Booking row on any device** in either September period. The table simply has no
entry for GB country or UK+IE rest after 1 September. Long-haul and regional both still record
bookings on mobile and desktop throughout. The UK zero is total across devices, not a device
artefact.

---

## D4. Weekly keyword table

Script `d06_weekly_keywords.py`. 1 Jun to 5 Oct 2026, all PK non-brand, `segments.week`.

| file | rows |
|---|---|
| `data/raw/d4_kw_traffic.jsonl` | 22,573 |
| `data/raw/d4_kw_conv.jsonl` | 74,547 |
| `data/clean/d4_weekly_keywords.csv` | **21,053** rows, 19 weeks, 2026-06-01 to 2026-10-05 |

QR_Booking conversions joined on week and criterion id: 363 week by keyword keys carry a booking.
Campaign name and destination code are kept on every row so destination groups can be derived
downstream. No summary produced, as requested.

---

## D5. Audiences and bid modifiers

Script `d07_audiences_modifiers.py`, scope the 66 UK+IE campaigns.

| resource | rows | notes |
|---|---|---|
| `campaign_audience_view` | 3,145 | 8,783 clicks attributed |
| `ad_group_audience_view` | **0** | none exist |
| `campaign_criterion` | 3,476 | 3,145 USER_LIST, 198 DEVICE, 66 LANGUAGE, 66 LOCATION, 1 KEYWORD |
| `ad_group_bid_modifier` | 594 | **every bid modifier is unset** |

- **No bid modifier is set anywhere.** All 594 ad group modifiers are null, and all 198
  campaign level device criteria are null across desktop, mobile and tablet.
- 3,145 USER_LIST criteria, roughly 48 per campaign, all carrying no bid modifier, so they are
  observation rather than targeting.
- **Zero campaign criteria modified on or after 15 August 2026.**
- One campaign level negative keyword exists, on `Google|PK|Dest|Country|XXX|IE|EN|MOD`, last
  modified 17 February 2026, so well before the window.

**Error and fix.** The first `ad_group_bid_modifier` query was refused with `UNRECOGNIZED_FIELD`
on `ad_group_bid_modifier.criterion_id`. That resource exposes only three selectable fields:
`bid_modifier`, `device.type` and `resource_name`. Re-queried against the field service and rerun.

---

## D6 (added). Exploration probe, and a correction to D3

Ran after the main round, to test which untouched resources return real data for this account.

| path | rows | with clicks | verdict |
|---|---|---|---|
| `age_range_view` | 1,386 | 480 | live |
| `gender_view` | 594 | 230 | live |
| `campaign_audience_view` | 3,145 | 647 | live |
| `ad_group_ad` | 1,141 | n/a | live |
| `ad_group_criterion.final_urls` | 1,188 | n/a | live |
| `segments.day_of_week` / `segments.hour` | 425 / 1,282 | all | live |
| `conversion_custom_variable` | **46 variables** | n/a | live, not yet read |
| `user_list`, `campaign_asset`, `ad_group_asset` | refused | | wrong field names, not retried |

### Correction to D3

**D3 understated the change set.** It covered campaign, ad group, `ad_group_criterion` and
`campaign_criterion`, but **not `ad_group_ad`**. The ads were modified in the window:

- **198 UK+IE ads were PAUSED on 7 September 2026.** The 198 that remain ENABLED were last
  modified 17 July and were not touched.
- The same thing happened in long-haul on the same day, 180 ads.

Three things stop this changing the D3 conclusion, but it should have been in it:

1. The paused set and the enabled set point to **the same landing page**,
   `qatarairways.com/en-pk/homepage.html`. Nothing about where a click lands changed.
2. It is **not UK specific**, long-haul got the same treatment on the same date.
3. Daily UK ad serving shows **no discontinuity at 7 September**. Impressions had already fallen
   from 2,798 on 1 Sep to 99 by 6 Sep, driven by the 2 September switch. Distinct ads serving
   drifts from about 64 to between 20 and 40, tracking the volume collapse, not a creative swap.

So the honest statement is: nothing changed in the UK campaigns other than the bid strategy, the
pausing of 72 dormant ad groups on 25 September, **and the pausing of 198 duplicate ads on
7 September that pointed at the same landing page as the live ones**.

### Landing pages

UK+IE and long-haul use the **same three** landing pages, in the same proportions:
`/en-pk/offers.html`, `/en-pk/homepage.html`, `/en-pk/offers/new-year-savings.html`. Every live ad
points at `/en-pk/homepage.html`. There is no UK specific landing page and therefore no UK
specific landing page change.

### Age and gender: no shift

Share of clicks, UK+IE:

| period | 25-34 | 18-24 | 35-44 | unknown | male |
|---|---|---|---|---|---|
| 13 Jun-19 Aug | 25% | 13% | 12% | 36% | 44% |
| 20 Aug-1 Sep | 29% | 17% | 14% | 29% | 48% |
| 2-19 Sep | 28% | 15% | 12% | 32% | 45% |
| 20 Sep-5 Oct | 27% | 17% | 12% | 29% | 50% |

Flat across the switch, and long-haul is equally flat (25-34 at 30 to 33 percent throughout).
Demographics are another negative: the people clicking UK ads are the same ages and the same
gender mix before and after.

---

## D6b. The four remaining in-API paths, run

### 1. Conversion custom variables: definitions readable, values not

Script `d08_custom_variables.py`. 46 variables exist, owned by the MCC, and they include exactly
the fields that would answer this: `FlightDestination` (u6), `FlightOrigin` (u5),
`destinationCountry` (u28), `transactionStatus` (u27), `ItineraryType`, `Cabin`, `TotalPax`,
`StartDate`, `EndDate`, `ValueFare`, `ValueFareAndYQ`.

**Their values cannot be read.** Both access paths are refused:
`segments.conversion_custom_variable` and `conversion.custom_variables` return
`UNRECOGNIZED_FIELD`, and no other field in the 792 field catalogue exposes a value. Only the
definitions are available. So no booking can be broken down by route or destination through
this API.

One configuration observation, offered as a signal and not a conclusion. Variables come in
ENABLED and PAUSED pairs sharing a Floodlight `u` tag. The older generation (u1 to u19) carries
`floodlight_variable_type: DIMENSION` with `cardinality: EXCEEDS_SEGMENTATION_LIMIT_BUT_NOT_STATS_LIMIT`,
meaning many distinct values are arriving. The newer batch (u20 to u31, including
`destinationCountry`, `transactionStatus`, `PaymentType`, `PromoCode`, `varProduct`) is
**`floodlight_variable_type: UNSET` with `cardinality: BELOW_ALL_LIMITS`**. Cardinality is a
coarse bucket, and a variable with three legitimate values would also read BELOW_ALL_LIMITS, so
this is not evidence that they are empty. The `UNSET` type on an ENABLED variable is the part
worth asking the tagging owner about.

### 2. Keyword level final URLs: none exist

**Zero of 1,188 UK+IE criteria carry a final URL, tracking template or final URL suffix**, and
zero of 1,080 in the long-haul sample. Destination URLs live only on the ads. Path closed.

### 3. Ads and landing pages: identical across segments

Covered in the D3 correction above. UK+IE and long-haul share the same three landing pages, every
live ad points at `/en-pk/homepage.html`, and the 7 September action paused 198 duplicate ads
pointing at the same page. No UK specific landing page exists, so there is no UK specific landing
page change to find.

### 4. Did the bookings move to brand rather than disappear?

Script `d09_did_bookings_move.py`. This was the most promising remaining hypothesis: if PK users
now reach the booking through brand search, the booking is credited to the brand account and
non-brand reads zero.

**They did not move.** `QR_Booking` per day:

| period | brand account | non-brand account |
|---|---|---|
| 13 Jun-19 Aug | 48.0 | 9.3 |
| 20 Aug-1 Sep | 45.3 | 6.4 |
| **2-19 Sep** | **43.0** | **1.1** |
| 20 Sep-5 Oct | 34.3 | 1.8 |

Brand is roughly flat across the switch and then declines. For a migration to brand it would have
had to **rise** by roughly the 8 bookings a day non-brand lost. It fell instead.

**Limit, and it closes the path rather than leaving it open.** The brand account runs only **3
campaigns**, `Google|PK|Brand|Hero|XXX|XXX|EN|EXT`, `Google|PK|Brand|Qatar|XXX|XXX|EN|EXT` and
`Google|PK|Brand|Airways|XXX|XXX|EN|MOD`. All three carry `XXX` in the destination field, so brand
has **no destination dimension at all** and UK cannot be isolated within it by any means this API
offers. The per day comparison above is the strongest test available, and it is negative.

### 5. Age and gender

Covered above. Flat across the switch for both UK and long-haul.

---

## Where the in-API search now stands

Every path inside the SA360 Reporting API that could plausibly explain a UK specific booking zero
has been run and come back negative: geography, device, campaign structure, location settings,
keywords and match types, negatives, audiences, bid modifiers, ads, landing pages, age, gender,
custom variable values, and migration to brand.

What remains is outside this API:

- **search terms**, which do not exist in the SA360 Reporting API at any level, so what queries UK
  ads now match cannot be seen here
- **the booking path itself**, walked end to end from a live PK search to a UK booking
- **Adobe against Floodlight row by row** for the same UK orders over the same dates
- **the Floodlight tag on the UK confirmation page**, checked for whether it fires and with what
  `u6` and `u28` values, which is the one question the custom variable metadata actually raises

---

## D7. `_PK-Generic-RMKT_Exact` in detail

Script `d11_rmk_deep_dive.py`. Campaign id 11136349619, started 2020-09-16, last modified
2026-07-21, so untouched during the investigation window.

Correctly noted by the user: this is CPA bidding, not ROAS, so a conversion action carrying no
value is not a defect here. The right efficiency metric is cost per conversion, computed below.

### It is not behaving as a remarketing campaign

`ad_group.targeting_setting.target_restrictions` reads:

```
[{"targetingDimension": "AUDIENCE",  "bidOnly": true},
 {"targetingDimension": "GENDER",    "bidOnly": true},
 {"targetingDimension": "AGE_RANGE", "bidOnly": true}, ...]
```

**`bidOnly: true` means observation, not targeting.** The audiences do not restrict who sees the
ad. And all **159 user list criteria carry no bid modifier**, so they do not change the bid either.
The lists are inert on both levers: they neither narrow reach nor adjust price. They are reporting
dimensions.

Supporting detail: the single ad group is named **"Generic Keywords"**, the campaign carries
**5,092 campaign level KEYWORD criteria**, and the 159 lists are auto generated
`boomuserlist::NNNNNNN` names, 48 of which picked up at least one click out of 6,576 attributed.

So the name says RMKT, the configuration says broad generic search with audience lists bolted on
for observation.

### Settings that make it a poor like for like control

| setting | this campaign | rest of the account |
|---|---|---|
| geo targeting | **PRESENCE** | PRESENCE_OR_INTEREST on all other 485 active campaigns |
| budget | **own, 50.29 USD a day** | shared 489.79 across 543 portfolio campaigns |
| bid strategy | own, `Generic Remarketing - Conversions Δ`, MAXIMIZE_CONVERSIONS | the VBB portfolio |
| **target CPA** | **NOT SET** | n/a |
| rank lost IS | **37 to 55%** | 0% on the portfolio |

It is the only PRESENCE campaign in the account, and the only one losing impression share to rank
rather than to budget. Different constraint, different geo rule, different budget. Useful as a bid
strategy control, not as a matched control for anything else.

### Performance: the CPA has doubled while never leaving Maximise Conversions

| period | days | cost/day | CPC | QR_FlightSearch | **cost per flight search** | QR_Booking | IS | budget lost | rank lost |
|---|---|---|---|---|---|---|---|---|---|
| 13 Jun-19 Aug | 68 | 23.4 | 0.453 | 1,568 | **1.02** | 12.0 | 40% | 10% | 50% |
| 20 Aug-1 Sep | 13 | 34.9 | 0.568 | 315 | **1.44** | 0.0 | 40% | 10% | 50% |
| 2-19 Sep | 18 | 38.4 | 0.615 | 429 | **1.61** | 5.0 | 37% | 7% | 55% |
| 20 Sep-5 Oct | 16 | **52.3** | **0.734** | 398 | **2.10** | 2.0 | 39% | **24%** | 37% |

Spend per day has more than doubled, cost per click is up 62 percent, and **cost per conversion on
the action it optimises against has doubled, 1.02 to 2.10**. Impression share is flat at about 40
percent throughout, so it is buying the same share of the market for twice the money.

It was not budget capped in June and July, 10 percent lost to budget on a 50.29 budget while
spending 23.4 a day. It is capped now, 52.3 a day against the same budget and 24 percent lost to
budget.

### Why this changes the switchback advice

This campaign **never switched**. It has been on Maximise Conversions with **no target CPA** the
whole time, and its cost per conversion still doubled. So the cost inflation across this account
is not purely a value based bidding artefact, and Maximise Conversions is not by itself a safe
harbour.

The actionable conclusion: **if campaigns are moved back, set a target CPA.** Unconstrained
Maximise Conversions on a capped budget is exactly what this campaign has been running, and it has
drifted from 1.02 to 2.10 per conversion without anyone changing a setting since July.
