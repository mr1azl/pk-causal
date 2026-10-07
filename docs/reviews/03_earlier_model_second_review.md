# Second review by the user's earlier model (pasted by the user, 7 Oct 2026)

*Verbatim from the conversation. Reviews section 7 of `docs/analysis/02_PK_ADOBE_FRESH_LOOK.md`, using Floodlight
with the real 20 Aug cut list. Responses are in section 8 of that note; the regional "value failure" it proposes
was later withdrawn (section 9, and `docs/analysis/03_PK_SA360_ROUND3.md`) because Floodlight aggregated
counts are inflated by cross-device modelling, most of all for regional.*

---

Their acceptance is sound and the correction is handled properly. Two things in the new table deserve a look before this goes further.Their handling of the correction is good: withdrawn in place, not quietly edited, and the p-value demoted below the corroboration. That is the right instinct.

But I ran the destination split on Floodlight with your real cut list, and **the headline claim does not hold**.

## Pakistan non-brand, 20 August cut campaigns excluded

| | | IBE/day | bookings/day | booking rate | revenue/day |
|---|---|---|---|---|---|
| **UK / IE** | 13 Jun – 19 Aug | 54 | 0.81 | 1.51% | $423 |
| | 20 Aug – 1 Sep | 63 | 0.92 | 1.46% | $886 |
| | **2 Sep – 5 Oct** | **27** | **0.15** | **0.54%** | **$25** |
| **other long-haul** | 13 Jun – 19 Aug | 86 | 1.18 | 1.37% | $571 |
| | 20 Aug – 1 Sep | 87 | 0.38 | 0.44% | $432 |
| | **2 Sep – 5 Oct** | **40** | **0.32** | **0.82%** | **$350** |
| **regional / other** | 13 Jun – 19 Aug | 222 | 2.31 | 1.04% | $712 |
| | 20 Aug – 1 Sep | 365 | 1.77 | 0.48% | $929 |
| | **2 Sep – 5 Oct** | **133** | **2.53** | **1.90%** | **$291** |

The UK collapse is real and it is the sharpest. But where the revenue went:

| | revenue lost per day | share of the loss |
|---|---|---|
| UK / IE | $398 | 38% |
| regional / other | $421 | **40%** |
| other long-haul | $221 | 21% |

**"The UK accounts for essentially all of the non-brand revenue PK has lost" is wrong.** It is about 38% against the June-to-August baseline, or 54% against the cut fortnight. Regional destinations lost at least as much.

## There are two failures, not one

**The UK failure is a conversion failure.** Booking rate 1.46% to 0.54%, on traffic that halved. That is the finding they have, and it stands.

**The regional failure is a value failure, and it is invisible in their framing.** Regional booking rate nearly doubled, 1.04% to 1.90%, the best conversion improvement in the account. And revenue still fell 59%. Those bookings are worth a fraction of what they were.

That is the average-booking-value collapse I flagged at the start, Pakistan's ABV down 49% while Germany's and Canada's rose 38% and 59%. The regional group is where it lives. Value bidding did exactly what it was asked to do in regional, won more conversions, and the conversions were cheap tickets.

By focusing on the UK, the note has found the dramatic failure and missed the systematic one. **The regional story is the more important one for the model**, because it is about the value signal being miscalibrated rather than one destination going wrong.

## The biggest undone check is seasonality, and it is pointed straight at the UK

Pakistan to UK is heavily family and VFR traffic. UK school terms start in early September. Families fly back in late August. A UK-specific booking collapse beginning 2 September is **exactly** what that seasonality predicts, and it would be entirely unrelated to bidding.

The control used, UK campaigns in Saudi, Malaysia and Singapore, does not test this. Those markets have no comparable term-time VFR pattern.

This is now the single largest threat to the finding and their check 4 is the one that matters most. If 2025 Pakistan-to-UK data exists, it settles the question in an afternoon. I would not let this conclusion travel further without it.

## Two smaller flags

**Adobe and Floodlight do not quite agree.** Adobe reports zero UK bookings over 34 days; Floodlight reports about five. Both are low, but a hard zero across 738 visits is the kind of number that sometimes means a tracking break rather than a demand collapse. Worth confirming the UK landing pages and tagging did not change around 2 September before the conclusion is attributed to bidding.

**The ticket-versus-order hypothesis predicts the wrong direction.** Their note suggests Floodlight counts tickets while Adobe counts orders, with large Pakistani family groups widening the gap. But the gap is *narrower* for UK traffic (Adobe 0.80% against Floodlight 1.51%, a factor of 1.9) than for everything else (0.16% against 1.13%, a factor of 7). If family size drove it, UK should show the wider gap, not the narrower one. The hypothesis needs rethinking or the counting settings need checking directly.

## What I would tell them next

Keep the UK finding, correct the headline to "the UK is the sharpest failure, about 40% of the revenue loss", and open a second thread on the regional group, where conversion improved and value collapsed. Then do the seasonality check before anything else, because if 2025 shows the same September UK pattern, the UK thread closes and the regional one becomes the whole story.

---

## User correction later in the session

On the claim in `docs/analysis/06_PK_ROUND4_REVIEW.md` that the pre-switch bidder was rewarded for bookings:

> False, it was rewarded on flight searches, not bookings.

Pre-switch strategy: Maximise Conversions on flight-search counts. Post-switch: Maximise Conversion Value on
`QR_FlightSearch_VBB` search values. Bookings were never in the objective.
