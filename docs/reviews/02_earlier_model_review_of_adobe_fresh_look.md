# Review of the Adobe fresh look by the user's earlier model (pasted by the user, 7 Oct 2026)

*Verbatim from the conversation. Reviews `docs/analysis/02_PK_ADOBE_FRESH_LOOK.md` sections 1 to 6, using SA360
spend data and the real 20 Aug cut list. Responses are in section 7 of that note.*

---

Strong work, and the click-date attribution is a real methodological improvement over what I did. But there is one thing I want to check before you act on the headline.I went looking for the confound that caught the earlier analysis. **The headline survives, but the evidence presented for it does not.**

## The GB country campaigns are the 20 August budget cut, not the switch

`Google|PK|Dest|Country|XXX|GB|EN|MOD` and `Google|PK|O&D|Country|PK|GB|EN|MOD` are the **top two campaigns in my 20 August cut list**. Daily spend:

| | 13 Jun – 19 Aug | 20 Aug – 1 Sep | 2 Sep – 5 Oct |
|---|---|---|---|
| Dest Country GB | $320.6 | $38.8 | $13.0 |
| O&D Country PK-GB | $97.9 | $14.2 | $2.9 |

Those two are $418 of the $475 a day Pakistan spent on UK destinations, **88% of it**, and they were switched off on 20 August, thirteen days before VBB.

Section 2 compares "13 Jun–1 Sep" against "2 Sep–5 Oct", which folds the cut fortnight into the before period. So the −96% on GB country campaigns, presented as the first of "two separate failures", is the budget decision. Table 1 handles the periods correctly; Table 2 does not, and Table 2 is where the headline evidence sits.

## But the finding holds once you remove them

Excluding every campaign in the 20 August cut list, Pakistan non-brand:

| UK + IE | cost/day | clicks/day | CPC | IBE/day | **bookings/day** |
|---|---|---|---|---|---|
| 13 Jun – 19 Aug | $48 | 128 | $0.38 | 54 | **0.81** |
| 20 Aug – 1 Sep | $60 | 154 | $0.39 | 63 | **0.92** |
| 2 Sep – 5 Oct | $46 | 65 | $0.72 | 27 | **0.15** |

| everything else | cost/day | clicks/day | CPC | IBE/day | **bookings/day** |
|---|---|---|---|---|---|
| 13 Jun – 19 Aug | $207 | 951 | $0.22 | 308 | **3.49** |
| 20 Aug – 1 Sep | $286 | 1,460 | $0.20 | 453 | **2.15** |
| 2 Sep – 5 Oct | $307 | 463 | $0.66 | 173 | **2.85** |

The UK campaigns that were never cut were completely unaffected on 20 August, then dropped from 0.92 bookings a day to 0.15 at the switch. Everything else recovered to near its pre-cut level. **The UK result is real and it is attributable to the switch.**

## The sharper statement

It is not a traffic story. UK visits fell 57%, non-UK fell 62%. Almost identical.

It is a **conversion** story:

- UK booking rate **1.50% → 0.56%**, down 63%
- Everything else **1.13% → 1.65%**, up 46%

Buying less traffic normally improves conversion, because you keep the better queries. The UK did the opposite. That is a much stranger and more specific finding than "the UK lost traffic", and it is the version I would put in front of anyone.

## One hypothesis I would revise

Section 3 proposes that UK values are too low, so the bidder dropped out of UK queries. The relative CPC movement is consistent with that: UK CPC rose 85% while non-UK rose 230%, so the bidder did shift aggression away from the UK.

But a bid-level story predicts fewer, better-targeted UK clicks converting *better*. Conversion fell by nearly two thirds. Something changed in **which** UK queries were bought, not just how many. A low flat value alone does not produce that.

That is a composition question, and it is exactly what the keyword level will answer. Your instinct about going to keyword was right, and this result gives it a precise target rather than a fishing expedition: **what UK-destination queries did Pakistan buy before 2 September, and what is it buying now?**

## Two smaller challenges

**The eVar84 overwrite explanation does not fit the numbers.** If non-brand clicks followed by brand clicks were being recredited to brand, Adobe should show lower non-brand revenue *and* lower bookings. In September, Adobe PK non-brand revenue is 1.0x Floodlight while bookings are 0.3x. Revenue matches exactly. That points to the two systems counting bookings differently, not to attribution loss. Pakistan's implied average booking value is $954 in Adobe against $300 in Floodlight, a 3.2x gap, while Germany's is only 1.24x. Worth confirming what `event27` counts before that explanation goes in a report.

**The UK emerged from the data, so p 0.02 is not worth what it looks like.** If several destination groupings were examined, one clearing 0.05 is unremarkable. The genuine support is the corroboration: the non-cut UK campaigns show it independently, and the booking-rate divergence runs opposite to the rest of the market. I would lead on those rather than on the Poisson test.

## What I would check next

Their checks 1 and 2 are the right ones. I would add: **the UK non-cut campaigns kept their budget but halved their clicks at double the CPC.** Pull the bids and impression share for those specific campaigns around 2 September. If bids rose while clicks fell, the bidder was outbidding itself into a narrower, worse-converting slice of UK demand, which would explain both the CPC and the conversion collapse in one mechanism.
