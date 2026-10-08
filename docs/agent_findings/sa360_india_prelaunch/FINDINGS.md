# India pre-launch checks for value based bidding

Account `Google-GCCLI-IN-EN-2` (4034062923), Google non-brand, under MCC 1144701035.
Data to 7 October 2026. Written 8 October 2026.

Windows used, and why they differ: 12 weeks (16 Jul to 7 Oct) for the baseline and the structure,
8 weeks (13 Aug to 7 Oct) wherever the booking ledger is one side of a ratio so both sides cover
the same days, 4 weeks (10 Sep to 7 Oct) for the search value file and the headroom read.

---

## Go or fix first

| # | check | state | what it would take |
|---|---|---|---|
| 1 | Target ROAS set on the portfolio | **FIX FIRST** | None of the 10 portfolios has a target CPA, a target ROAS or a CPC ceiling. Proposed starting target is **38x on VBB search value**, the account's current realised return. Set it before the switch, not after. |
| 2 | Value calibration by destination | **FIX FIRST** | **UK+IE** is over-valued on both measures, 1.35 to 1.44 times the median. Scale its search values by **0.69 to 0.74**. North America is over-valued on the attributed view alone, scale 0.71. |
| 3 | Fallback and zero share of search values | **GO** | Nothing is valued at zero. 18 to 47 percent of searches fall back to 0.50 but they carry under 1.2 percent of value in every group that matters. One exception: **AZ at 93.9 percent fallback**, 20 percent of that destination's value. |
| 4 | Bid headroom | **FIX FIRST** | **46 percent of spend sits below PK's 21.7 percent rank-lost starting point.** The account is already at **104 percent budget utilisation** on 10 shared budgets, one at 208 percent. There is no room to absorb a CPC rise. |
| 5 | Reverse direction negatives | **FIX FIRST** | **1,021 of 1,021 campaigns have none.** 986 have no campaign-level negative at all. 60 percent of keywords are broad. 17.7 percent of North America's search value already comes from searches for flights to India. |
| 6 | Measurement | **FIX FIRST** | Attributed bookings run **7.3 times** the ledger and attributed revenue **10.1 times**. Same-device over ledger is 1.00 to 1.12, so cross-device modelling is not part of the gap, it is all of it. Four of seven groups have no usable transaction-based guardrail. |
| 7 | Changes scheduled near launch | **ANSWER NEEDED** | **646 of 1,022 enabled campaigns were modified in the last 30 days**, clustered 13 to 15 and 22 to 23 September. What those edits were is not recoverable from this API. A budget cut 13 days before the switch confounded every PK read. |
| 8 | Holdout and guardrails | **READY, with one gap** | Both designs below. North America cannot be balanced because one campaign is 67 percent of the group. Guardrails are usable on the ledger for three groups of seven. |

**Recommendation: do not launch on the PK configuration.** Four of the eight checks are fix-first,
and three of them (no target, no headroom, no directional negatives) are the exact three conditions
that produced the PK collapse, all present here at the same time and in a more constrained account.

---

## What India is

A long-haul outbound market, which is the opposite shape to PK.

| group | share of 12w spend | enabled campaigns | rank lost | cross-device on bookings |
|---|---|---|---|---|
| North America | 42.3% | 288 | 21.6% | 77.8% |
| Europe excl UK+IE | 23.6% | 376 | 27.4% | 82.7% |
| GCC and Middle East | 18.6% | 121 | 35.4% | 98.1% |
| UK+IE | 9.5% | 128 | 23.8% | 78.7% |
| Africa | 3.5% | 76 | 26.0% | 94.2% |
| Oceania | 1.9% | 8 | 23.3% | 98.2% |
| other | 0.6% | 24 | 32.1% | 88.2% |

South and South-East Asia and India-coded campaigns exist in the account, 726 of them, but every
one is paused or removed and none spent in the window.

The structure is clean: 100 percent pipe naming, destination parses on 100 percent of spend, and
10 portfolios tiered by route value (Elite, Tier 1, Tier 2 High/Mid/Low, Tier 3, Push, New Dest).
That tiering makes a staged launch possible, which PK did not have.

**One correction to the brief's framing.** India's CPC has already risen **6.2 times year on year**,
0.047 to 0.290, with no VBB involved, because the account moved to Maximize Conversions at some
point. 2025 is a usable seasonal shape for booking rate and useless as a CPC baseline. Everything
here is measured against 2026.

---

## 1. Target ROAS

All ten portfolios are MCC owned, all `MAXIMIZE_CONVERSIONS`, and **none has a target CPA, a target
ROAS or a CPC ceiling**. The only thing constraining spend today is the budget. Switching to
Maximize Conversion Value without a target does not add a constraint, it changes what is maximised
and leaves the same uncapped structure against the same fixed budgets. That is the PK
configuration, reproduced.

Realised return over the last 8 weeks, 170,530 USD of spend:

| group | cost | ROAS on VBB search value | ROAS on attributed bookings | ROAS on ledger revenue |
|---|---|---|---|---|
| North America | 61,131 | 33.3 | 6.1 | 1.17 |
| Europe excl UK+IE | 41,540 | 44.6 | 9.6 | 0.92 |
| GCC and Middle East | 39,973 | 32.8 | 8.7 | **0.28** |
| UK+IE | 17,219 | **52.4** | 10.0 | 0.74 |
| Africa | 6,584 | 44.8 | 11.5 | **0.11** |
| Oceania | 3,105 | 29.6 | 11.5 | 1.47 |
| **all** | **170,530** | **38.2** | **8.4** | **0.83** |

**Proposed starting target: 38x on VBB search value**, which holds spend roughly where it is today
and lets the bidder reallocate rather than escalate. Lower it deliberately later if volume is
wanted, with the guardrails below watching.

Two things to be careful about before using this number.

**It depends on which signal the portfolio actually reads**, and that is not visible in this API.
`QR_FlightSearch_VBB` and `QR_FlightSearch_VBB_ML` fire on effectively the same events (289,498
against 289,485 over 12 weeks) but carry values **1.52 times apart** (10.58M against 6.96M). A
target set against one and applied to the other is wrong by half. `primary_for_goal` is false on
both and the primary list is identical in SA and India, so that flag is not the selector; the
selection happens in the portfolio's conversion settings, which only the UI shows.

**The 0.83 ledger ROAS is not a profitability statement.** It is 8 weeks of Floodlight-attributed
gross ticket revenue over 8 weeks of cost, it is left-truncated by booking lag, and it excludes
whatever converts outside the Floodlight window or through other channels. It is reported because
the spread across groups is informative, not because 0.83 is the true return.

---

## 2. Value calibration: UK+IE again

Search value per click against booking value per click, 13 Aug to 7 Oct.

| group | ratio vs median (ledger) | ratio vs median (attributed) | scale needed | flagged |
|---|---|---|---|---|
| **UK+IE** | **1.44x** | **1.35x** | 0.69 to 0.74 | **both views** |
| North America | 0.58x | **1.40x** | 0.71 | attributed only |
| GCC and Middle East | **2.39x** | 0.96x | 0.42 | ledger only |
| Africa | **8.00x** | 1.00x | 0.12 | ledger only |
| Europe excl UK+IE | 1.00x | 1.19x | 1.00 | no |
| Oceania | 0.41x | 0.66x | 2.42 | no |

**UK+IE is the only group flagged on both views.** PK's failure was UK campaigns whose search value
ran 5.7 against 3.0 for regional. India's UK+IE is milder but it is the same group, the same
direction, and visible before launch rather than after.

Where the two views disagree, that disagreement is the finding, not noise. Africa and GCC and
Middle East look extreme on the ledger and ordinary on the attributed view because they have almost
no ledger bookings: their ledger ratio is measuring the absence of transactions.

**Eleven of the top 30 destinations have zero transactions in 8 weeks**, together 108,734 clicks and
**27,519 USD**: AE (48,195 clicks, 11,976 USD), AUS, GE, RUH, AZ, KE, AUH, NO, IST, EG, CH. Every
one carries a positive search value per click between 6.61 and 15.39. A value bidder has a signal
to chase there and no booking evidence behind it.

---

## 3. The search value signal itself

Measured on 80,927 non-brand VBB search rows, 10 Sep to 7 Oct. India's order IDs carry the route
the user actually searched, so this answers directly what PK could only infer.

**Fallback is not the problem.** Nothing is valued at zero anywhere. Between 18 and 47 percent of
searches fall back to exactly 0.50, but 0.50 against a 12 to 38 average means the fallback rows
carry under 1.2 percent of value in every group that matters. Worst single destination is **AZ at
93.9 percent fallback**, carrying 20 percent of that destination's value.

**Route attribution is the problem.**

| group | same place | different place | share of value off route | searched a flight to India |
|---|---|---|---|---|
| North America | 64.1% | 35.9% | 26.9% | **17.7%** |
| UK+IE | 73.8% | 26.2% | 28.6% | **14.9%** |
| Europe excl UK+IE | 74.3% | 25.7% | 22.7% | 9.0% |
| GCC and Middle East | 80.2% | 19.8% | 33.1% | 10.6% |
| Africa | 82.6% | 17.4% | 12.3% | 4.9% |
| Oceania | 83.0% | 17.0% | 27.9% | 6.3% |

**Nearly one in five of the search value credited to North America campaigns comes from somebody
searching for a flight to India.** Top pairs: Canada to Delhi 404 rows, Toronto to Delhi 228, Dubai
to Delhi 183, Gatwick to Delhi 129, Toronto to Amritsar 110, UAE to Delhi 95, Toronto to Ahmedabad
92. Under value bidding, that value is what the bidder raises its price to win.

**One campaign is simply mis-targeted and should be fixed regardless of VBB.**
`Google|IN|Dest|City|XXX|AUS|EN|PHR` is Austin, Texas. **1,105 of its 1,595 search rows, 69 percent,
are searches for Melbourne, Sydney, Adelaide and Brisbane.** "AUS" reads as Australia to searchers.
It spent 2,699 USD in 8 weeks and produced zero bookings. The sibling `GE` campaigns have the same
shape of problem: they bid on the bare word "georgia", which in English also names a US state.

---

## 4. Bid headroom: there is none

**Every enabled campaign sits on one of 10 shared budgets, and the account is already running at
104.4 percent utilisation**, 2,972 USD of daily budget against 3,102 USD actually spent per day.
Five of the ten budgets are over 100 percent, one at **208 percent**.

PK's collapse was not caused by a high bid in the abstract. It was caused by a higher bid meeting a
fixed shared budget with no slack, which pinned budget-lost impression share above 90 percent for
14 days while rank-lost sat at exactly 0.0. **India has less slack than PK had, before anything
changes.**

The second condition is also present. PK entered its switch at 21.7 percent rank lost and its CPC
rose 6.6 times; SA entered at 53 percent and rose 2.1 times. Low rank lost means bidding higher
wins almost nothing extra, so the bidder escalates price without buying volume.

**64 campaigns, 32,158 USD over 4 weeks, 46 percent of the spend measured, sit below PK's starting
point.** By group: Oceania 86 percent of its spend, Africa 62, North America 58, Europe 48, UK+IE
43, GCC and Middle East 34.

The standout object in the account is **`Google|IN|O&D|Country|IN|US|EN|MOD`**: 73,542 USD over 12
weeks, the single largest campaign, at **4.8 percent rank lost and 84 percent impression share**, on
the budget running at 208 percent, with **zero negative keywords**. There is almost nothing left for
it to win by bidding higher and no budget to pay for it.

---

## 5. Query hygiene

| | |
|---|---|
| Keywords, enabled non-brand | 11,844 |
| Broad | 7,140 (60%) |
| Phrase | 4,704 (40%) |
| Exact | **0** |
| Campaign level negatives | 239, on 35 campaigns, 232 of them flight numbers |
| Ad group level negatives | **0**, confirmed two ways |
| Campaigns with a reverse direction negative | **0 of 1,021** |
| Campaigns with no negative at all | 986 of 1,021 |

Broad campaigns carry 87 percent of spend. Sixty percent broad match with no directional negatives
anywhere is the mechanism behind the reverse-direction value in section 3. Both ends are measured,
neither is inferred.

**The one claim here I would not act on without a UI check.** `shared_set`, `shared_criterion` and
`campaign_shared_set` do not exist in the SA360 API, zero fields each, so shared negative lists are
invisible from here. If the team keeps directional negatives in a shared list, "0 of 1,021" is
wrong. Worth five minutes in the UI before anyone builds negatives.

Search terms are also unavailable in this API and were not substituted with anything. The UI export
of the last 8 weeks is still needed.

---

## 6. Measurement

| group | ledger bookings 8w | attributed | ratio | cross-device | same-device over ledger |
|---|---|---|---|---|---|
| Europe excl UK+IE | 49 | 310 | 6.33 | 82.6% | 1.10 |
| North America | 58 | 264 | 4.55 | 75.8% | 1.10 |
| GCC and Middle East | 5 | 226 | **45.20** | 97.8% | 1.00 |
| UK+IE | 24 | 130 | 5.42 | 79.2% | 1.12 |
| Africa | 2 | 48 | 24.00 | 95.8% | 1.00 |
| Oceania | 1 | 31 | 31.00 | 96.8% | 1.00 |
| **search non-brand** | **140** | **1,022** | **7.30** | | **1.10** |

**Same-device over ledger is 1.00 to 1.12 in every group.** Strip cross-device and the attributed
count collapses onto the ledger almost exactly. Cross-device modelling is not part of the
inflation, it is all of it. PK's equivalent ratios landed at 1.43 to 1.69, so India is further gone
than the market that failed.

Revenue: 141,468 USD in the ledger against 1,431,513 attributed, **10.1 times**.

Ledger structure is sound and matches every other market examined: `conversion_quantity` is 1000 on
all 243 rows so one row is one transaction, status ENABLED on all, attribution VISIT on all,
`floodlight_original_revenue` agrees with `conversion_revenue_micros` on all 243, one duplicate
hashed order ID.

**Performance Max holds 103 of 243 India bookings, 42 percent.** It is not a search portfolio and
would not move in this launch, but any before-and-after read at account level will be dominated by
a campaign type that did not change.

Small-count caveat: GCC and Middle East, Africa, Oceania and other rest on 5, 2, 1 and 1 ledger
rows. Direction reliable, magnitude not.

---

## 7. Changes near launch

**646 of 1,022 enabled campaigns were modified in the last 30 days**, clustered on 14 September
(223), 13 September (154), 22 September (102), 23 September (102) and 15 September (57). Zero ad
groups were modified.

What those edits were is not recoverable: `change_event` does not exist in this API and
`last_modified_time` keeps only the most recent edit per object. A budget cut 13 days before the
switch confounded every PK read, and this is a larger change set than that. **This needs an answer
from whoever made them before a launch date is set.**

Also current: 113 campaigns are on `PRESENCE_OR_INTEREST` rather than `PRESENCE`, 5,621 USD over
12 weeks, concentrated in **UK+IE (2,026 USD)**, the group already flagged on value calibration.
The other 909 are on the tight setting, which is better than PK, where everything was
`PRESENCE_OR_INTEREST`.

---

## 8. Holdout and guardrails

**A structural fact decides the design.** Budget maps one to one onto portfolio: each of the 10
budgets carries exactly one portfolio. But 7 of the 10 budgets carry campaigns from more than one
destination group. So a holdout drawn at portfolio level is automatically budget separated, and one
drawn inside a portfolio is not: treated campaigns bidding higher would starve holdout campaigns
sharing their budget, and the test would measure budget contention instead of the strategy.

**Design A, hold out whole portfolios.** Clean inference, no contention, no per-group balance.

| portfolio | campaigns | spend 8w | share | CPC | bookings per 1k | mix |
|---|---|---|---|---|---|---|
| OnD Tier 2 Mid Routes | 41 | 50,424 | 31.6% | 0.597 | 2.77 | North America 81% |
| OnD Tier 1 Routes | 96 | 48,352 | 30.3% | 0.260 | 1.63 | GCC 33%, Europe 23% |
| OnD Tier 2 Low Routes | 60 | 38,722 | 24.2% | 0.256 | 1.75 | GCC 52%, Europe 23% |
| OnD T3 Routes V2 | 69 | 10,312 | 6.5% | 0.264 | 1.69 | Europe 36%, GCC 26% |

**Design B, campaign level stratified by destination group.** Balanced, but needs the budget split.

| group | campaigns | held out | spend held | share | CPC gap | booking rate gap | budgets shared |
|---|---|---|---|---|---|---|---|
| GCC and Middle East | 39 | 1 | 6,971 | 17.7% | -1% | +3% | 1 |
| UK+IE | 46 | 1 | 4,359 | 27.7% | -5% | -2% | 1 |
| Africa | 31 | 2 | 1,202 | 20.7% | +2% | +11% | 2 |
| Europe excl UK+IE | 134 | 10 | 6,023 | 16.0% | -2% | -25% | 3 |
| North America | 47 | 22 | 8,635 | 15.1% | **-61%** | -26% | 5 |
| Oceania | 5 | 3 | 361 | 12.0% | -7% | -100% | 0 |

**Recommended: design B, with each tier portfolio given a parallel holdout portfolio and its own
budget sized to that arm's recent spend.** That is the only version that is both balanced and free
of contention. It costs setup work, and without it the holdout measures the wrong thing.

**North America cannot be balanced.** `Google|IN|O&D|Country|IN|US|EN|MOD` is 67 percent of the
group's spend at a CPC of 0.90 against 0.30 for the rest, so whichever arm holds it sets that arm's
CPC. It has to be its own stratum, or stay in the treated arm with the group read excluding it.
Oceania has too few campaigns to split at all.

### Guardrails

Weekly bookings per 1,000 clicks over 8 weeks, with the exact Garwood one-sided 90 percent Poisson
lower bound. **A group below its bound for two consecutive weeks after launch is flagged.**

| group | clicks 8w | ledger bookings | ledger mean | **ledger bound** | attributed mean | **attributed bound** | usable |
|---|---|---|---|---|---|---|---|
| North America | 112,065 | 58 | 0.52 | **0.43** | 2.36 | 2.17 | yes |
| Europe excl UK+IE | 151,647 | 49 | 0.32 | **0.27** | 2.04 | 1.90 | yes |
| UK+IE | 58,391 | 24 | 0.41 | **0.31** | 2.23 | 1.98 | yes |
| GCC and Middle East | 169,236 | 5 | 0.03 | 0.01 | 1.34 | **1.22** | no |
| Africa | 24,711 | 2 | 0.08 | 0.02 | 1.94 | **1.59** | no |
| Oceania | 11,805 | 1 | 0.08 | 0.01 | 2.63 | **2.04** | no |
| other | 3,899 | 1 | 0.26 | 0.03 | 3.33 | **2.22** | no |

**Only three of seven groups have a usable transaction-based guardrail.** GCC and Middle East is
the sharpest case: more clicks than any other group, 169,236, and **five real bookings in eight
weeks**. A bound of 0.01 per 1,000 clicks is a number nothing could ever breach.

Those four groups can only be watched on the attributed number, which runs about seven times the
ledger and is 95 to 98 percent cross-device modelled in exactly those groups. Each threshold above
is labelled with the measure it belongs to, because a guardrail written against one and watched on
the other would never fire.

---

## What I got wrong along the way

Recorded because the corrected numbers are the ones above and the intermediate ones may have been
quoted in progress notes.

1. **Route match, first pass: 35.9 percent on-route.** Wrong. It counted a country code and a city
   inside that country as a mismatch (AE against DXB, CDG against PAR, LHR against LON). Resolving
   every code to a country or metro first gives 64 to 83 percent.
2. **Inflation table, first pass** put 103 ledger rows in "other" and their attributed twins in
   "none", because the ledger query had no non-brand filter while the inventory excludes
   Performance Max. Performance Max is now a separate line.
3. **Holdout selection, first pass** picked whichever campaign sat nearest the group mean
   regardless of size, so North America held out one campaign carrying 67 percent of the group.
4. **Combined risk score in i41** was dominated by budget utilisation, a property of the shared
   budget rather than of the campaign, so every campaign on the 208 percent budget sorted to the
   top. Replaced with two separate rankings.

---

## Limits

- Google only. The three Bing India accounts were excluded, the same decision taken for PK.
- `change_event` does not exist, so the September edits are dated but not described.
- Attributes are current values, never time sliced. Only metrics are time sliced.
- Shared negative lists are not readable from this API at all.
- Search terms are not available from this API; the UI export is still outstanding.
- Portfolio conversion settings, including which VBB variant a portfolio reads, are not exposed.
- Destination groups are a judgment. Turkey and the Caucasus are counted as Europe, Egypt and the
  Maghreb as Africa, India-coded campaigns as their own group. Caucasus is 3.03 percent of spend,
  so that one is material; each group is one editable set in `lib_sa360.py`.
- Order IDs carry GA client IDs in a shifting position. They were parsed for the type and OND
  tokens only, the tail was never read or written, and `data/raw/` was checked afterwards and
  contains no identifier of any kind.
