# PK VBB: why the switch did not work as expected

*7 Oct 2026. Working diagnosis, written before looking at the new dataset.
Sources: the VBB Rollout Readiness readout (7 Oct), the Cowork PK handover (5 Oct) and the review of
Cowork's first round, and the Adobe v84 handover (7 Oct). Nothing here has been re-computed from raw data.*

## 1. What happened, in order

| Date | Event | Evidence |
|---|---|---|
| 20 Aug | Budget cut on 52 PK non-brand campaigns: $838 to $169 a day (-80%) | Readout, budget table |
| 2 Sep | Switch to Maximise Conversion Value, rule-based `QR_FlightSearch_VBB`, no target ROAS, shared budget about $500 a day | Client; all 543 campaigns last modified 2 or 3 Sep |
| 2 to 13 Sep | Cost per click x5 to x7 (x13 on 8 Sep); budget-lost impression share 7.7% to 62% to 80%; searches -82% | Daily report, Cowork |
| 2 to 19 Sep | Revenue collapses in both Floodlight sources; bookings -87% on the API booking actions | Cowork daily table |
| From about 14 Sep | Cost per click falls steadily back to about $0.28 | Daily report |
| To 5 Oct | Revenue has not recovered | Readout |

The key point: cost per click normalised, revenue did not. Learning or budget alone would predict
revenue coming back with traffic. It did not, which points at the value signal.

## 2. What we think the cause is

**The bidder optimised faithfully on a value signal that does not track revenue in PK, and it entered
learning on a budget too small to absorb it.**

Why PK and not Canada (also rule-based, also switched 2 Sep, +153% revenue):

1. **The booking part of the value signal is weak in PK.** The VBB action receives search values plus
   `sales` rows with booking revenue. Floodlight captures about 16% of PK's Adobe revenue (40% in
   Germany). In PK the bidder sees little booking revenue and optimises mostly on search value.
2. **The search value in PK is noisy.** 24% of searches at the $0.50 fallback (1 Sep), 11.9% at zero
   (week of 6 Sep), value per search -40% in launch week, one ISB-LGW campaign carrying values from
   $0.50 to $84.08.
3. **Spend followed that value away from bookings.** Spend tracked the rule-based value per $ (t 3.8),
   not the ML value (t -0.2). UK country campaigns fell from $258 to $15 a day. If UK searches get low
   or fallback values, the bidder walks away from one of PK's main revenue routes.
4. **The budget was already starved.** The 20 Aug cut left the portfolio at about $500 a day when it
   entered learning on a new objective with no ROAS target, so it bought very few expensive clicks.

Status: a hypothesis consistent with the evidence, not yet tested directly.

## 3. Where the readout overstates PK

1. **"Pakistan's traffic has come back."** 535 visits a week is about 76 a day, against 387 a day
   before the switch (untouched campaigns). A trough of 143 a week cannot sit inside a post-switch average
   of 200 a day. The units do not reconcile, and traffic is still far below the pre-switch level.
2. **PK's mechanism row relies on `Bookings (FL)`.** Booking rate +42% and average booking value halved
   is the signature of extra zero-revenue bookings. On the API count the rate fell and revenue per booking
   held at $1,200 to $1,450. "The same mechanism in every market" does not hold for PK.
3. **"The loss was a budget decision, not the bidding."** On the untouched campaigns spend rose 16%
   ($313 to $363 a day) while revenue per $ fell from 3.7x to 2.4x. That is the bidding, on switched
   campaigns, with more money. "Not decidable" is right for the Causal Impact model; the direct
   comparison leans negative.

## 4. The booking count problem (related)

| Period | Bookings/day, API | Bookings/day, FL | Revenue/booking, API | Revenue/booking, FL |
|---|---:|---:|---:|---:|
| 1 to 19 Aug | 9.21 | 11.16 | $1,215 | $346 |
| 20 Aug to 1 Sep | 6.38 | 6.54 | $1,446 | $423 |
| 2 to 19 Sep | 0.83 | 5.00 | $1,384 | $110 |
| After 20 Sep | 1.33 | 3.12 | $1,191 | $672 |

- The API count fits the traffic: about 6 bookings per 1,000 searches after the switch vs about 10.7
  before. The FL count implies about 27 per 1,000, a 2.5x jump while cost per click rose 5x.
- FL revenue was about a third of API revenue even in August, so FL Revenue measures something
  different, not the same thing with gaps.
- The extra FL bookings carry less total revenue than the API ones, so they are not a superset. A new or
  changed zero-value booking source (one of the three `Booking` actions, or an activity added to the FL
  column's group) fits better than attribution or date lag.

## 5. Checks that would confirm or reject the cause

1. Value vs revenue by destination, pre-switch: VBB value per search against Adobe booking revenue per
   search. A weak or negative relationship confirms the cause.
2. Fallback and zero-value share by destination, UK routes first.
3. Spend shift vs booking shift by campaign family, before vs after.
4. Whether `sales` rows reach the VBB action in PK. Near zero means no booking feedback at all.
5. Booking reconciliation (section 4), including whether the FL gap follows the PK switch date or a
   calendar date across DE, CA and FR.

## 6. Decision it leads to

Five weeks in, cost per click has normalised and revenue has not. If check 1 confirms the cause, waiting
will not help. Options: revert PK to Maximise Conversions while the value feed is fixed; fix fallback
values and `sales` rows and restart; or add a ROAS target as a stopgap (only useful if value tracks
revenue).
