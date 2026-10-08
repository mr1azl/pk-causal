# GB switchback: campaigns to move off VBB

*8 Oct 2026. Full list: `13_uk_switchback_campaigns.csv` (campaign ID, name, destination, cost and Adobe bookings
by period).*

## What to move

All **60 enabled GB campaigns** in the PK non-brand account (4851538229), meaning every campaign whose destination is
GB, LHR, LGW, MAN, BHX or EDI. All 60 sit on the same portfolio (`biddingStrategies/12222452141`) as the rest of PK.
The 2 paused UK campaigns stay paused. Source: `data/sa360/round3/s01_pk_nonbrand_campaigns.parquet`, enabled
campaigns with `dest_group == "UK+IE"`.

- 20 of the 60 had little or no spend after the switch. They move anyway, so that GB traffic does not sit under two
  bidding strategies at once.
- The two GB country campaigns account for 89% of GB spend from Jun to Aug:
  - `22932501781` `Google|PK|Dest|Country|XXX|GB|EN|MOD`
  - `22922582106` `Google|PK|O&D|Country|PK|GB|EN|MOD`

**Ireland (10 campaigns, DUB and IE) stays on VBB.** Ireland shows no loss (1 booking after the switch on about
$4 a day), and keeping it on VBB leaves a small comparison group. This narrows the earlier "UK+IE" recommendation.

| Period (Adobe, by click day) | GB cost | GB bookings | IE cost | IE bookings |
|---|---:|---:|---:|---:|
| 13 Jun - 19 Aug | $31,936 | 37 | $358 | 7 |
| 20 Aug - 1 Sep (cut) | $1,448 | 9 | $47 | 2 |
| 2 Sep - 5 Oct (VBB) | $2,094 | 0 | $128 | 1 |

## How

1. **Strategy:** Maximise Conversions with no target, the setup used before 2 Sep. Use a standard
   (campaign-level) strategy or a new portfolio that holds only these 60 campaigns.
2. **Goal:** the same flight-search conversion action(s) that were primary before the switch, not
   `QR_FlightSearch_VBB` and not the zero-value TEST action. Confirm which action that was before changing anything.
3. **Budget:** a separate budget of about **$60-70 a day**, which matches GB spend under VBB ($61 a day). Leave the
   other campaigns on the $490 shared budget, reduced by the same amount. If GB stays on the shared budget, the two
   strategies compete for the same money and the test cannot be read.
4. **Rest of PK:** stays on VBB. Add a target ROAS or a CPC cap, and use `QR_FlightSearch_VBB_ML` if the portfolio
   allows it.

## What to expect, honestly

At the Jun-Aug GB rate (37 bookings per $31.9k), $61 a day buys about **1.5 Adobe bookings in 3 weeks**. Three weeks
will not prove anything statistically. Treat the move as a **fix that removes the one segment with a measured loss**,
not as a clean experiment. Read it on Adobe GB bookings per $ against Ireland and the rest of PK, and keep it running
past 3 weeks if the numbers are still too small. Allow 1 to 2 weeks of learning after the change.
