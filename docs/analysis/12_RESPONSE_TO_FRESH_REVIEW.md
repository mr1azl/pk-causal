# Response to the fresh review (`11_FRESH_REVIEW.md`)

*8 Oct 2026. I re-ran `scripts/pk_fresh_review.py` on the repo data: every number it quotes reproduces. Below,
what I accept, what I would qualify, and the revised position. Where this note and notes 02 to 10 disagree,
this note and the README section 3 table supersede them.*

## 1. Accepted, and what it changes

1. **"Outside the UK, VBB improved PK" is withdrawn.** It improved per Adobe searching visit only because CPC
   doubled. Per dollar, non-UK bookings were -13% and revenue -34% against 13 Jun to 19 Aug, and +10% / -6%
   against the cut fortnight, on 36 bookings. The honest reading is no clear gain and no clear loss outside the UK
   (part of the revenue fall is seasonal: brand revenue per booking fell 17% in September 2026 and 14% in 2025).
2. **"Total PK held up in September" is not evidence for VBB.** Brand rose from August to September in all six
   markets; the 2025 baseline contains the brand account rebuild; and non-brand bookings per dollar fell 9% in
   September 2026 against a 62% rise in September 2025. It was right as a description of the account, wrong as
   an argument for the switch.
3. **The UK evidence is one last-click fact, not three.** Adobe, the Floodlight ledger and `QR_Booking` record the
   same last-click bookings. The Google `Booking` tag, the only differently attributed measure, shows no UK drop in
   2 to 19 Sep (2.9 conversions on 616 clicks); its late-period drop is on 3.0 conversions and still filling in.
   My "-49% on the Google tag" was a pooled figure that hid this.
4. **It is GB, not UK+IE.** Ireland booked 1 on 75 visits after the switch (1.4 expected). GB: 0 against 4.5
   (p 0.011), the only one of 19 destinations below expectation; US, AU, DE, MY and the generic campaign are
   significantly above. Against the rest of PK's post-switch behaviour, GB's shortfall is large (1 against 14.7);
   against "nothing changed", one destination at p 0.01 out of 19 is close to chance.
5. **Two of my three UK drivers do not hold.**
   - "The bidder keeps buying UK": wrong. UK's spend share fell from 25% (cut fortnight) to 10% to 14%.
   - Reverse and generic queries as the mechanism: contradicted by May 2026, when the same campaigns ran 26%
     off-target and converted at their best rate (12.8 per 1,000). Query drift explains a quarter of the deficit
     at most. Negatives are still worth adding.
   - GFS: the mid-August rank fall is on all PK routes and in 2025 too; the UK-specific part is about half a rank.
   What survives: the rule-based UK search value is the most inflated relative to bookings (5.0 against 3.8 and
   2.9), and UK searches per click rose after the switch (Flight Search 0.35 to 0.46) while other groups did not.
6. **The ML value action is the most useful finding of the investigation.** PK records `QR_FlightSearch_VBB_ML` on
   the same searches. Its value over booking value is 2.2 / 2.4 / 2.0 for UK+IE / long-haul / regional, against
   5.0 / 3.8 / 2.9 for the rule-based values the PK portfolio bids on. ML values a UK search at $26.8, the rule at
   $61.2. Nobody, me included, had looked at it. (The India agent found the two India values 1.52x apart.)
7. **Cross-market result on orders per dollar:** CA +38% bookings / +70% revenue, MY +203% / +169%, SA -21% / -36%,
   PK +2% / -17%. SA, on ML values, is the weakest; CA, on rule-based values, the strongest. Value type alone does
   not explain the spread, which is one more reason to test rather than roll out.
8. **Brand migration is not ruled out.** Downgraded from "high" to "untested". The test exists: `QR_Booking` rows in
   the brand account by `FlightDestination` (custom variable already present).
9. **The CPC spike is the switch and its learning period.** "No target" is the obvious lever, not a demonstrated
   cause; downgraded from "high" to "likely".

## 2. Qualified

1. **`Flight Search (TEST Sept2026)`.** It first records on 20 Aug but at 0.02 to 0.03 per click in the cut
   fortnight, rising to 0.4 to 0.7 only from 2 Sep, and it carries zero value. It cannot have changed the pre-switch
   objective materially, and a zero-value action does not move a Maximise Conversion Value bidder. Worth confirming
   it is not in the portfolio goal, but low priority.
2. **What the 20 Aug "cut" was.** Fable is right that a shared budget cannot be cut per campaign. Account daily cost
   went from about $940 to about $450 on 20 Aug, close to the current shared budget of about $490. The likeliest
   reading is that the shared budget was roughly halved on 20 Aug and the old Maximise Conversions bidder dropped
   the country campaigns itself. If so, "the cut campaigns" are a bidder choice, not a list someone made, and the
   readout's "52 campaigns cut" description should change. `campaign_budget` history would confirm it.
3. **"No non-UK gains" against June to August** compares across that budget halving and a different campaign mix;
   against the cut fortnight (same budget) non-UK bookings per dollar were +10%. I would say "no measurable
   non-UK effect either way" rather than "no gains".

## 3. Revised position

**PK.**
- Move the UK+IE (in practice GB) campaigns back to Maximise Conversions on flight searches, on their own budget of
  about $60 to $70 a day, for three weeks. That is both the fix and the test: 4 to 8 bookings expected at the
  pre-switch rate; 0 to 1 means the cause is outside bidding.
- Keep the rest on VBB, with a target ROAS (or a CPC cap) set from the last eight weeks.
- Check whether the portfolio can bid on `QR_FlightSearch_VBB_ML`; if yes, switch to it before the UK campaigns
  rejoin.
- Run Fable's check 2: PK-site bookings to GB destinations by week and channel (Adobe), 2025 and 2026, plus brand
  `QR_Booking` rows by `FlightDestination`.

**India.** A measured test, not a rollout: ML or calibrated values (the India agent's 1.52x gap between the two
value actions makes the choice material), a target ROAS, the design B holdout, the blocking items in
`10_INDIA_PRELAUNCH_REVIEW.md`, and a destination-level guardrail on Adobe bookings rather than modelled conversions.
