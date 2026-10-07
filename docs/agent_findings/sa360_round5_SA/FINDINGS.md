# Round 5: the SA market, and what it tells us about PK

Account `Google-GCCLI-SA-EN-2`, 7879272266, USD, Asia/Qatar. Same test set as PK, same four
periods. Method and row counts in `LOG.md`.

**SA is the control PK never had.** It switched on the same dates, onto the same kind of MCC owned
portfolio, with the same absence of a ROAS target. It got the same bidding behaviour. It did not
get the same outcome. That separates what the strategy causes from what is wrong in PK.

---

## The mechanism reproduces exactly

| at the switch, 20 Aug-1 Sep to 2-19 Sep | PK | SA |
|---|---|---|
| cost per click | 0.225 to **1.479**, x6.6 | 0.317 to **0.673**, x2.1 |
| impression share lost to **rank** | 21.7% to **0.7%** | 53% to **1%** |
| impression share lost to **budget** | 10.5% to **72%** | 14% to **61%** |

Both markets stopped losing auctions on rank almost entirely and started losing them to budget.
Neither was outbid. Both bid themselves out of volume against a fixed budget. **This is a property
of the strategy, not of Pakistan.**

Two differences in degree are worth noting. SA's cost per click rose only half as far, and SA
started far more rank constrained, 53 percent against PK's 21.7, so it had less headroom to bid up
before it ran into the budget. That plausibly explains why SA was hurt less, and it is a reason to
expect the same strategy to behave differently again in a third market.

---

## The outcome does not reproduce at all

| bookings per 1,000 searches | PK | SA |
|---|---|---|
| 13 Jun-19 Aug | 7.4 | 8.16 |
| 20 Aug-1 Sep | 8.0 | 10.89 |
| **2-19 Sep** | 6.8 | **13.83** |
| **20 Sep-5 Oct** | **2.7** | **9.76** |

**SA's conversion rate went up through the switch and is still above its own baseline.** PK's fell
63 percent. Same strategy, same dates, opposite result.

In absolute terms SA lost volume but not efficiency: bookings a day went 4.62 to 2.75, a 40 percent
fall driven by searches falling, while PK fell around 80 percent on a collapsing rate as well.

### No SA destination group went to zero

SA's UK+IE: **1 booking in the ledger before 2 September and 5 after.** It went up. Volumes are
small, 17 to 20 searches a day, so the honest reading is "no collapse" rather than growth. Long-haul
and regional both held their rate too.

PK's UK+IE went to **exactly zero** and stayed there.

---

## The measurement gap between the two markets

Attributed conversions against the actual transaction ledger, same metric, same action, same dates:

| | PK regional | SA regional |
|---|---|---|
| all_conversions / ledger rows | **9.77x** | **2.15x** |
| cross-device share of all_conversions | **82.7%** | **25%** |

PK regional reports nearly ten attributed bookings per real transaction, SA just over two. Strip
cross-device from both and they converge, 1.69x against 1.60x. So the gap is almost entirely Google
modelling device-switching journeys at three times the rate in PK as in SA.

That is a market level measurement difference, not a bidding one, and it deserves its own question
to the measurement owner regardless of the booking investigation.

Structurally the ledgers are identical: `conversion_quantity` is 1000 on every row in both markets,
so one row is one transaction; zero revenue runs at 2.2 percent in PK and 2.7 in SA; duplicate
order IDs are 1 in 88 and 1 in 183. Nothing about the tag behaves differently.

---

## The change audit says the same thing in both markets

| level | SA objects | modified 15 Aug-5 Oct |
|---|---|---|
| campaign | 2,893 | 2,610, which **is** the switch |
| ad group | 106,982 | **42** |
| keyword | **1,593,182** | **0** |

Not one of 1.59 million SA keywords was touched. Same as PK, where not one of 1,188 UK keywords
was touched. In both markets the only change of substance is the bid strategy.

SA has one event PK does not: **172 campaigns modified on 14 September**, inside the switch window.
Not investigated in this round and worth a look if SA is pursued.

---

## What this does to the PK conclusion

Round 4 ended by saying PK's UK zero sits downstream of the click and is UK specific, having ruled
out geography, device, structure, settings, keywords, audiences, ads, landing pages, age, gender
and migration to brand. SA tightens that considerably.

**The strategy is exonerated as a sufficient cause.** The same portfolio type, switched the same
day with the same missing ROAS target, produced the same bidding pathology in SA and left its
conversion rate intact. Value based bidding cost PK volume. It did not cost PK its conversion rate,
because it did not cost SA's.

**So the PK booking collapse, and the UK zero inside it, needs a PK specific and UK specific
explanation**, which is exactly where round 4 pointed: the booking path or its measurement for UK
routes out of Pakistan. SA now rules out the obvious alternative, that the strategy itself breaks
conversion tracking.

**And the cross-device gap is a second, separate finding.** PK's 9.77x against SA's 2.15x is large
enough that PK booking numbers and SA booking numbers are not comparable at face value in any
reporting, whatever happens with the investigation.

---

## Recommended next steps

1. **Treat the PK UK booking path as the open question**, and test it outside this API: walk a UK
   booking end to end from a live PK search, and compare Adobe against Floodlight row by row for the
   same UK orders.
2. **Raise the cross-device gap separately.** 9.77x against 2.15x on the same metric is a reporting
   problem in its own right.
3. **Reconsider the switchback plan in light of SA.** The strategy is not what broke conversion in
   PK, so moving campaigns back to Maximise Conversions buys volume back but will not restore the
   UK zero. The round 4 advice stands on volume grounds, with a target CPA, and should not be sold
   as a fix for the booking problem.
4. **Look at the 172 SA campaigns modified on 14 September** if SA is pursued further.

---

## Caveats

- SA volumes by destination group are small outside regional. UK+IE runs 17 to 20 searches a day,
  so its numbers show absence of collapse, not a reliable rate.
- SA started far more rank constrained than PK, 53 percent against 21.7, which limits how cleanly
  the two can be compared on the bidding side.
- Attributes are current, not historical. Settings reflect 7 October.
- `last_modified_time` records only the most recent edit per object.
- The 172 SA campaigns modified on 14 September are unexplained.
- Round 5 covers the SA EN-2 account only. `Google-GCCLI-SA-AR` carries 28,779 USD and 705
  QR_Booking on a single campaign and was not examined.
