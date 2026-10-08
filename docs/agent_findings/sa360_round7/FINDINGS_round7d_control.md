# Round 7d: the control test, and what it kills

Written 8 October 2026, in answer to a question I should have asked myself:
if Canada and Germany are just as badly calibrated and did not collapse, then
calibration cannot be the cause.

**The answer is that you are right.** Round 7b's destination miscalibration does
not explain PK. Two of its claims survive in weakened form and one framing was
simply wrong.

Four markets, same window, same method. 505,765 VBB rows.

---

## 1. The headline table

| market | searches | search value | sales | sales value | inflation base | ML | booking rate vs baseline |
|---|---|---|---|---|---|---|---|
| **PK** | 27,511 | 920,850 | 53 | 60,517 | **15.22x** | 8.78x | **-63%** |
| India | 145,772 | 3,724,110 | 135 | 138,504 | **26.89x** | 17.84x | not launched |
| **Canada** | 52,402 | 2,434,527 | 305 | 513,301 | **4.74x** | 3.10x | **-26%** |
| **Germany** | 26,501 | 1,469,844 | 258 | 306,605 | **4.79x** | 3.07x | not measured |

Destination spread, raw:

| market | destinations tested | median ratio | spread max over min | p90 over p10 | worst three |
|---|---|---|---|---|---|
| PK | 4 | 10.9 | 3x | **3.1x** | LHE 1.5x, LHR 1.3x, JFK 0.7x |
| India | 15 | 18.2 | 62x | **9.1x** | BER 4.9x, SFO 3.9x, LHR 2.9x |
| Canada | 28 | 3.7 | 35x | **8.7x** | DXB 3.2x, HYD 2.6x, AMD 2.4x |
| Germany | 33 | 5.4 | 16x | **4.3x** | FRA 3.4x, BOM 2.9x, ISB 2.3x |

**PK has the lowest destination spread of the four, and the worst outcome.**
Canada's spread is 2.8 times PK's and Canada lost less than half as much booking
rate.

---

## 2. Is PK's low spread just an artefact of having only 4 destinations?

Fair objection: more destinations means more chance of an extreme, and PK has 4
while Germany has 33. Bootstrap, drawing 4 destinations at random from each
market 2,000 times:

| market | pool | median spread at k=4 | p25 | p75 | P(a random 4 beats PK's 3.1) |
|---|---|---|---|---|---|
| PK | 4 | **3.1** | 3.1 | 3.1 | 100% |
| Germany | 33 | **3.5** | 2.1 | 5.5 | 56% |
| Canada | 28 | **4.3** | 2.7 | 9.5 | 70% |
| India | 15 | **6.5** | 3.8 | 12.5 | 88% |

Like for like, **PK is at the low end but Germany is right beside it**, 3.5
against 3.1, and more than half of Germany's random draws are worse than PK's
figure. PK's calibration is not unusually good; it is ordinary.

**Either way it is not unusually bad, and that is what matters.** The market that
lost 63 percent of its booking rate is the best calibrated of the four on the
axis a value bidder allocates along. Destination miscalibration cannot be the
cause of the PK collapse.

---

## 3. The framing in round 7b section 2 was wrong

I wrote that the proxy is "an order of magnitude too high" and treated 15.22x
and 26.89x as evidence of a broken tag. Decomposing the ratio shows what it
really measures:

> inflation = (mean search value / mean sale value) x (searches per sale)

| market | mean search | mean sale | **value ratio** | **searches per sale** | inflation |
|---|---|---|---|---|---|
| PK | 33.47 | 1,141.84 | **0.0293** | **519** | 15.22 |
| India | 25.55 | 1,025.96 | **0.0249** | **1,080** | 26.89 |
| Canada | 46.46 | 1,682.95 | **0.0276** | **172** | 4.74 |
| Germany | 55.46 | 1,188.39 | **0.0467** | **103** | 4.79 |

**The tag values a search at 2.5 to 4.7 percent of a booking in every market.**
That rule is close to constant. What varies by a factor of **ten** is how many
searches a market needs to produce a booking: 1,080 in India against 103 in
Germany.

So the 5.7x difference in "inflation" between India and Canada is not a tagging
difference. It is a market difference that the tag does not account for.

**The sharper statement, and the one I should have made:** the tag applies a
near constant search to booking value ratio across markets while the underlying
conversion rate varies tenfold, so **the tag is market blind**. In PK a search
should be worth about 1/519 of a booking and is valued at 1/34. In Germany it
should be worth about 1/103 and is valued at 1/21. Both are over-valued, PK by
roughly five times more.

That is a real and useful finding. It is not the finding I wrote in 7b.

---

## 4. So does any of it still bear on PK?

The over-valuation **level** does track the outcome across the two markets where
VBB launched and the outcome was measured: PK at 15.2x lost 63 percent, Canada
at 4.7x lost 26 percent. Tempting, and I am not going to lean on it, for three
reasons.

**n is two.** Two markets with an outcome is not a relationship.

**India sits at 26.9x, worse than PK, and has not launched**, so it cannot be
used as evidence in either direction.

**Most importantly, round 7b already established that absolute scale cannot be
the mechanism.** Under Maximize Conversion Value with no target ROAS, the bidder
spends the budget and maximises value. Multiplying every value by ten changes
nothing about which auctions it enters or what it pays. A uniformly inflated
signal has no lever to pull.

For the inflation level to matter, it would have to be inflated **unevenly in a
way that favours expensive inventory**. That is precisely what the destination
spread measures, and PK's is the lowest of the four.

**Conclusion: the FSV calibration is not the cause of the PK collapse.**

---

## 5. What is left standing

The mechanism from round 7 is untouched and remains the explanation:

> UK auctions clear at 1.04 while the rest of the PK account clears at 0.17 to
> 0.24. The 20 September CPC cap flattened everything to about 0.42, which is
> not binding on the cheap two thirds and is a 60 percent cut on UK+IE. UK+IE
> recovered its query footprint, 153 search terms per day against 136 at
> baseline, and did not recover its spend, 37 per day against 250. The other two
> segments ended above baseline.

That is a PK specific structural fact about auction prices, not a tagging fact,
and nothing in this control test touches it.

**What the calibration work is still good for**, on its own terms rather than as
a PK explanation:

- India's launch decision. The destination spread there is the worst of the four
  at 9.1x, and LHR and MAN sit at 2.89 times the median. That is a reason to
  recalibrate before launching, independent of what happened in PK.
- The market blindness in section 3 is a programme level issue worth raising:
  one value rule applied across markets whose conversion rates differ tenfold.
- Canada's own spread is 8.7x, second worst, which is worth someone's attention
  given Canada has already launched.

---

## 6. Corrections to the record

1. **Round 7b section 2, "the proxy is an order of magnitude too high."**
   Reframed. The tag applies a near constant 2.5 to 4.7 percent search to
   booking value ratio in every market; the apparent inflation differences are
   conversion rate differences the tag does not account for.
2. **Round 7b's implication that destination miscalibration contributed to PK.**
   Withdrawn. PK has the lowest destination spread of the four markets and the
   worst outcome, and this survives bootstrapping to equal destination counts.
3. **Round 7b section 3, "this corroborates and strengthens the UK flag in
   FINDINGS_india.md."** Still true **for India**, where LHR and MAN are at 2.89
   times the median. It says nothing about PK, where LHR is at 1.3 times the
   median on a four destination base.

---

## Limits

- PK rests on 53 sales and 4 testable destinations. Germany and Canada have 258
  and 305 sales and 33 and 28 destinations. PK's figures are the weakest in the
  table and every PK conclusion here should be re-run when more sales accumulate.
- Germany's outcome was never measured the way round 6 measured PK, SA, CA and
  MY, so it enters this test as a calibration observation only.
- The booking rate outcomes quoted are from round 6, measured on bookings per
  1,000 searches, 20 Sep to 5 Oct against 13 Jun to 19 Aug.
- The ML variant tracks base at 0.56 to 0.66 in every market, so nothing here
  changes if the portfolio reads the ML signal instead.
