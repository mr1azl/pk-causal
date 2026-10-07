# PK round 4: who clicks UK ads now, and what changed in the UK campaigns

Account 4851538229, PK non-brand, Google Ads. Written 2026-10-07.
Periods: 13 Jun-19 Aug, 20 Aug-1 Sep (cut), 2-19 Sep (switch), 20 Sep-5 Oct.
UK+IE kept split into "GB country (cut 20 Aug)", 2 campaigns, and "UK+IE rest", 64 campaigns.
Method, row counts and errors in `LOG.md`.

**Round 4 is a set of negative results, and that is its value.** It was asked to find who clicks
UK ads now and what changed in the UK campaigns. The answer to both is: nothing that explains the
zero. Four candidate causes are eliminated below, which narrows where the real cause can be.

---

## 1. Did the share of UK+IE clicks from outside Pakistan change at the switch, and from where?

**Yes it roughly doubled in the switch window, then reverted below its own baseline. It cannot
explain the zero, because bookings stayed at zero after it reverted.**

| segment | 13 Jun-19 Aug | 20 Aug-1 Sep | **2-19 Sep** | **20 Sep-5 Oct** |
|---|---|---|---|---|
| GB country (cut) | 24.9% | 21.4% | **43.5%** | **20.0%** |
| UK+IE rest | 14.5% | 13.7% | **31.6%** | **7.6%** |
| long-haul | 10.4% | 8.6% | 24.2% | 11.4% |
| regional | 2.5% | 2.3% | 16.5% | 3.5% |

Two things make this a dead end as a cause.

**It reverts.** UK+IE rest ends at 7.6 percent, roughly half its pre switch level and the lowest
of any period measured, while bookings remain at zero. If out of country traffic were the cause,
bookings should have returned when the mix did.

**It is not UK specific.** Long-haul and regional spike and revert on exactly the same schedule.
Every segment moves together, which points to the volume collapse changing the inventory mix for
a few weeks rather than to anything about who UK ads reach.

Where the out of country clicks come from is unremarkable and stable: the **United Kingdom** is
the top non-Pakistan country in every UK+IE period, as expected for UK destination campaigns,
4,023 clicks pre cut on the GB country campaigns and 79 in the switch window. Behind it, Ireland,
Saudi Arabia, the UAE, India, Spain and Canada, all small and all present before the switch too.

---

## 2. Did the device mix of UK+IE clicks change at the switch?

**No, not meaningfully, and the zero is present on every device.**

| segment | 20 Aug-1 Sep | 2-19 Sep | 20 Sep-5 Oct |
|---|---|---|---|
| UK+IE rest, mobile share | 89.2% | 87.3% | 84.4% |
| long-haul, mobile share | 87.5% | 88.1% | 82.8% |
| regional, mobile share | 91.4% | 91.7% | 84.9% |

Mobile share drifts down a few points for UK+IE, and the same drift appears in long-haul and
regional. Nothing UK specific.

More decisive: segmenting `QR_Booking` by device returns **no UK+IE row at all** for either
September period. Not a low number on one device, no row on any device. Long-haul and regional
keep recording bookings on both mobile and desktop throughout. The UK zero is total across
devices, so it is not a device measurement artefact.

---

## 3. Was anything changed in the UK+IE campaigns between 15 Aug and 5 Oct other than the bid strategy?

**No.**

Across the 66 UK+IE campaigns, **138 objects** were modified in the whole window:

| level | objects | modified | what it was |
|---|---|---|---|
| campaign | 66 | **66** | the bid strategy switch, 12 on 2 Sep and 54 on 3 Sep |
| ad group | 198 | **72** | all on 25 Sep |
| keyword | 1,188 | **0** | none since 22 May 2026 |
| campaign criterion | 3,476 | **0** | none since 12 Jul 2026 |

The 66 campaign edits **are** the switch. The 72 ad groups touched on 25 September are all
**PAUSED** and carried **0.00 USD, 0 clicks and 0 impressions** across the entire window; the 126
live ad groups carried all 36,011 USD and 35,770 clicks. That is housekeeping on already dormant
ad groups, the same action seen portfolio wide in round 3.

The keyword inventory is completely static: **1,188 criteria, all ENABLED, zero negatives**, 654
broad and 534 phrase, created 22 Aug 2025 or 21 May 2026, **none modified after 22 May 2026**.

From D5, there is also **no bid modifier set anywhere**: all 594 ad group modifiers are null and
all 198 campaign level device criteria are null. The 3,145 user list criteria carry no modifier,
so audiences are observation rather than targeting, and **none was modified on or after 15 August**.
One campaign level negative keyword exists, on the IE campaign, last touched 17 February 2026.

So: no keyword cull, no new negative, no match type change, no location edit, no audience change,
no bid modifier, no ad group change that touched anything live.

**Limit on this answer.** `change_event` does not exist in this API, so `last_modified_time` is
the only record and it shows the **most recent** edit per object, not a history. An object changed
on 1 September and again on 3 September shows only 3 September. The conclusion holds for anything
not subsequently overwritten.

---

## 4. Presence or presence or interest, and does UK differ?

**Every active campaign is `PRESENCE_OR_INTEREST`, and UK+IE is identical to the rest.**

Restricted to the **486 campaigns with impressions** in the window:

| segment | PRESENCE_OR_INTEREST | PRESENCE |
|---|---|---|
| GB country (cut) | 2 | 0 |
| UK+IE rest | 64 | 0 |
| long-haul | 262 | 0 |
| regional | 157 | 0 |
| no destination | 0 | 1 |

485 of 486, with negative targeting set to `PRESENCE` throughout. There is no difference between
UK and anything else to find here.

**A trap worth recording.** Across all 3,676 non removed campaigns the same query looks like a
60/40 split between the two settings. That is entirely paused legacy campaigns. Restricting to
campaigns that actually ran changes the answer completely.

Every campaign targets **Pakistan at country level**. A subset adds city level positive targeting
(Islamabad, Lahore) and city exclusions (Faisalabad, Islamabad, Karachi, Lahore, Multan, Peshawar,
Sialkot), a geo split structure present in UK+IE, long-haul and regional alike. No campaign targets
a destination market.

**These are attributes, so the API returns the current value only.** A date range does not time
slice them. Nothing here establishes what the setting was in August, only what it is now. If the
question is whether someone changed it during the window, `last_modified_time` on the campaign
answers that instead, and it says the only campaign level edits were on 2 and 3 September.

---

## What round 4 rules out, and what is left

Eliminated as causes of the UK zero:

- **who the ads reach**: out of country share spiked and reverted, moved in step with every other
  segment, and is now below its own baseline
- **device**: mix barely moved, and the zero holds on every device
- **campaign structure**: no keyword, negative, location, audience or bid modifier change
- **location settings**: identical to the rest of the account, and unchanged in the window

Combined with round 3, where cost per click and auction position returned to pre switch levels by
late September while bookings stayed at zero, the remaining explanation space is narrow. The
clicks arrive, in the same proportion from the same places on the same devices, through the same
keywords, and still produce flight searches. What they stop producing is a **UK destination
booking recorded against `QR_Booking`**.

That points downstream of the click and specific to UK destinations: the booking funnel for UK
routes, or the measurement of it, rather than anything in the campaign. The next test that would
actually separate those two is not in this API. It needs either the UK booking path checked end
to end against a live search, or Adobe and Floodlight compared row by row for the same UK orders
over the same dates.

Worth remembering from round 3 when reading that: the reported booking figure merges a Floodlight
tag with a Google Ads WEBPAGE conversion, and the 5.9 UK bookings still showing after 2 September
come entirely from the WEBPAGE action. The `QR_Booking` Floodlight count for UK+IE is exactly
zero, and one single UK+IE transaction row exists in the whole period to 5 October.

---

## Caveats

- Google Ads only; the two Bing PK accounts are out of scope.
- Attributes are current, not historical. Settings, bids and audience configurations reflect
  7 October, not August.
- `last_modified_time` records only the most recent edit per object.
- `user_location_view.targeting_location` looked like a presence against interest signal and is
  **not safely readable as one**: of 46,530 campaign by date by country keys, 13,470 carry both a
  true and a false row for the same country, and Pakistan itself has 15,356 keys with a false row.
  It is written to `data/clean/d1_targeting_location_split.csv` for completeness and used in no
  conclusion here.
- D4 is a data deliverable with no summary, as requested.
