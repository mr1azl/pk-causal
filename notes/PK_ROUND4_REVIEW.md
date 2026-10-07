# PK: review of SA360 round 4, and where the cause now points

*7 Oct 2026. Agent output in `sa360_round4/` (FINDINGS.md, LOG.md). Value check in
`scripts/pk_value_per_search.py` on the round 3 SA360 tables.*

## 1. What round 4 settles (accepted)

| Candidate cause | Round 4 result | Verdict |
|---|---|---|
| Clicks now come from outside Pakistan | UK+IE rest out-of-country share 14% before, 32% in the switch weeks, **8% from 20 Sep**. The same spike and reversion in long-haul and regional | Ruled out |
| Device mix | Mobile share 89% to 84%, the same drift in every group; UK `QR_Booking` is zero on every device | Ruled out |
| Campaign edits | Only the bid strategy (2 and 3 Sep) and 72 already-dead ad groups paused on 25 Sep. No keyword, negative, match type, location, audience or bid-modifier change since May to July 2026 | Ruled out |
| Location setting | All 485 active campaigns PRESENCE_OR_INTEREST on Pakistan; UK identical to the rest | Ruled out (current values only) |

Caveat the agent states and that stands: `last_modified_time` shows only the latest edit per object, and
settings are current values, not history.

## 2. The cleanest test is the late period

From 20 Sep to 5 Oct the UK+IE campaigns the cut did not touch had, against before the switch:

- clicks 122 a day (SA360), against 141 (13 Jun-19 Aug) and 159 (cut fortnight);
- cost per click 0.41, against 0.40 and 0.39;
- absolute-top position on won impressions 27%, against 28%;
- out-of-country share 8%, against 14%; the same devices; the same 1,188 keywords.

At the pre-switch rate (about 2.2 to 3.4 bookings per 1,000 clicks on Adobe), about 4 to 7 bookings were
expected. Adobe recorded 0 (p about 0.01 to 0.001). Every observable property of the traffic is back to
normal except the outcome.

## 3. Where I disagree with the agent's conclusion

The agent concludes the cause is "downstream of the click": the UK booking funnel, or its measurement.

- **Measurement is already ruled out.** Adobe (eVar84 on the booking hit) and Floodlight (`QR_Booking`
  transaction rows) are independent tags, and they agree row by row: 49 of 89 bookings are identical
  on day, campaign and revenue, and both hold the same single UK row (18 Sep, from a 27 Aug click). A
  UK-only break in both systems at once is very unlikely. The row-by-row comparison the agent proposes
  is the one done in round 3.
- **A funnel or fare change is still possible but is a coincidence of timing.** UK bookings by click week
  were 6, 2, 2, 9 in August and 1, 0, 0, 0, 1, 0 from 31 Aug. An external event would have to start within a
  day or two of the switch. Worth one question to the commercial team, not the leading hypothesis.

## 4. What the bidder sees: UK is its best traffic

`QR_FlightSearch_VBB` value per search and per click, from SA360:

| Group | Period | Searches per click | Value per search | Search value per click | Search value per $ | Booking revenue per click |
|---|---|---:|---:|---:|---:|---:|
| UK+IE | 13 Jun-19 Aug | 0.44 | $60.7 | $26.7 | 24.5 | $5.43 |
| | 20 Aug-1 Sep | 0.52 | $65.1 | $33.8 | 76.3 | $6.32 |
| | 2-19 Sep | 0.47 | $63.3 | $29.5 | 13.5 | **$0** |
| | 20 Sep-5 Oct | 0.52 | $58.7 | $30.4 | **72.0** | **$0** |
| Long-haul | 20 Sep-5 Oct | 0.44 | $48.4 | $21.3 | 46.6 | $3.15 |
| Regional | 20 Sep-5 Oct | 0.35 | $26.0 | $9.2 | 27.4 | $0.84 |

- **In the bidder's objective, UK clicks are the most valuable per click and per dollar of any
  destination** ($30 of search value per click, 72 per dollar in late September). They earn that whether or
  not anyone books: UK booking revenue per click is zero while the search value is unchanged.
- **Before the switch the strategy was Maximise Conversions, and the `Booking` action is marked primary**
  (round 3, B1). If that was the goal, the old bidder was rewarded for bookings. The new one is rewarded
  about $60 for every UK search.
- **So the mechanism that fits everything:** on Maximise Conversion Value with search value as the target,
  the bidder looks for UK users and queries that produce many high-value searches. Within the same broad
  and phrase keywords (654 of 1,188 UK keywords are broad), it can win different queries and different
  users at the same price and position. Those who search the most need not be those who book: students
  comparing fares, people checking prices over several days, travel agents. Searches per click on UK rose
  from 0.44 to 0.52; long-haul and regional did not move.
- **Why UK and not the others:** UK has by far the highest value per search ($59 to $65, against $48 long-haul
  and $26 to $33 regional), so the pull towards searchers is strongest there. Elsewhere the search value is
  lower and the bidder's choices happened to improve bookings.

This is a hypothesis that fits all the evidence so far. It has not been tested directly.

## 5. Tests that would confirm or reject it

1. **Search terms for the UK campaigns, 1 Aug to 5 Oct, from the SA360 UI** (the API has none). Prediction:
   after 2 Sep the matched queries shift towards research-type queries (price, dates, "cheap", airport or
   city names without travel intent, reverse direction) within the same keywords.
2. **Searches per visit on Adobe, UK vs the rest, before and after.** Needs the count of flight searches
   per visit (event count, not visits with a search). Prediction: UK searches per visit up, booking per
   visit to zero.
3. **The decisive test, an experiment:** take the UK+IE campaigns out of the VBB portfolio for two to three
   weeks, back to the previous strategy (or a booking-based goal), keep everything else on VBB. If UK
   bookings come back within days, the value signal is the cause. Cheaper and faster than more analysis.
4. **The commercial question in parallel:** any change to PK-UK fares, availability, schedule or
   competitor capacity around 1 to 3 Sep.
