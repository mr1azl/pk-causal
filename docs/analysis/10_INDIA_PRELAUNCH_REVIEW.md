# India pre-launch: review of the SA360 agent's findings

*8 Oct 2026. Reviews `docs/agent_findings/sa360_india_prelaunch/FINDINGS.md` (account `Google-GCCLI-IN-EN-2`,
4034062923, data to 7 Oct) against the PK lessons (`08_PK_DECISION.md`) and the India search terms
(`09_INDIA_SEARCH_TERMS.md`).*

## Summary

The agent's checks are thorough and mostly right. I agree with **"do not launch on the PK configuration"**
and with most of the fix list. I disagree with three parts of the framing, and add two things that matter
more than anything in the go/fix table:

1. **GCC and Middle East is India's version of PK's UK, and the agent waves it through.** 169,236 clicks and
   about $40k in 8 weeks produced **5 Floodlight transactions** (ledger ROAS 0.28), while the bidder's signal
   says 32.8x on search value. The agent reads the ledger ratio (2.39x the median) as "measuring the absence
   of transactions". The absence of transactions is the finding: a value bidder will keep paying for GCC
   searches that the ledger says almost never book. Africa (2 transactions, ledger ROAS 0.11) is the same on a
   smaller scale. Queries are not the cause: 64% of GCC clicks are outbound India-to-Gulf searches.
2. **The decisive test of the reverse-direction risk is available and was not run.** India's VBB order IDs carry
   the searched route for `search` rows **and** for `sales` rows (bookings). Comparing the route direction of
   sales rows with that of search rows, per destination group, shows directly whether reverse-direction searchers
   ("Toronto to Delhi") book. In India they might: families in India often buy tickets for relatives abroad. If
   they book at a normal rate, the reverse queries are not a problem and negatives would cut good traffic.
   **The same test run on PK's UK campaigns before and after 2 Sep would settle the PK UK mechanism.**

## 1. Where I agree

| Agent check | Agree? | Note |
|---|---|---|
| 1. No target on any of the 10 portfolios; set one before the switch | Yes | Same as PK, SA, CA, MY. |
| 1. Which value signal the portfolio reads (`VBB` vs `VBB_ML`, 1.52x apart) | Yes, important | A target set on one and applied to the other is off by half. UI check before setting any target. |
| 2. UK+IE over-valued on both views (scale 0.69 to 0.74) | Yes | Milder than PK (1.4x median against PK's 1.9x), same direction. Rests on 24 ledger bookings. |
| 3. Fallback values not a problem (under 1.2% of value), except AZ | Yes | |
| 4. No bid headroom: 104% budget utilisation, 46% of spend below PK's rank-lost start | Yes, with a caveat | Daily spend above budget is normal for shared budgets (Google can spend up to 2x a day); the point stands that higher CPC cannot buy more volume. |
| 5. No reverse-direction negatives; 60% broad | Yes, with a UI check | Shared negative lists are invisible to the API, as the agent says. Matches my search terms read: 12% of non-brand spend off-target, reverse 9% of clicks on North America, UK+IE and GCC. |
| 6. Attributed bookings 7.3x the ledger, all of it cross-device | Yes | Worse than PK. Performance Max holds 42% of ledger bookings, so account-level reads are dominated by a campaign type that will not change. |
| 7. 646 campaigns modified 13-15 and 22-23 Sep | Yes, blocking | Find out what they were before setting a date. |
| `Dest\|City\|AUS` is Austin, Texas, buying Australia searches | Yes | Confirmed in the search terms: top queries "india to australia flight", "delhi to australia flight". $2.7k, zero bookings. Fix now, VBB or not. (My `09` note counted `AUS` as Oceania; that grouping was wrong.) |
| 8. Holdout design B (stratified, parallel portfolios with own budgets) | Yes | Exclude `O&D\|Country\|IN\|US` from the North America comparison or make it its own stratum. |

## 2. Where I disagree

1. **"The three conditions that produced the PK collapse."** PK did not collapse at account level: total PK paid
   search bookings rose 3% from August to September 2026 against a 24% seasonal fall in 2025, and non-UK
   non-brand held up (`08_PK_DECISION.md` section 7). What the missing target and the lack of headroom produced in
   PK was a CPC spike and lost volume for 2 to 3 weeks. The real damage was destination-specific (UK). For
   India the risk is the same: specific destination groups, not the whole account.
2. **GCC and Africa "flagged on the ledger only, not on attributed".** The attributed view in those groups is 95%
   to 98% cross-device modelling, so it is not independent evidence of bookings. With 5 and 2 real transactions,
   the ledger is the only real evidence there is, and it says these groups barely book. Treat GCC as flagged.
3. **Guardrails on attributed conversions for four groups.** A guardrail that is 95% to 98% modelled cannot
   detect a real fall in bookings. Use Adobe bookings for India (not yet pulled), or group GCC, Africa, Oceania
   and other into one ledger guardrail, or accept that those groups have no guardrail and limit their exposure.

## 3. What to do before India launches

**Blocking**
1. Find out what the 646 campaign edits of 13-15 and 22-23 Sep were.
2. Confirm in the UI which value signal each portfolio reads, then set a target ROAS on that signal (agent's
   starting point: 38x on rule-based search value, current realised return).
3. Run the sales-vs-search route direction test (above) for India, and for PK's UK campaigns before and after
   2 Sep. Decide on reverse-direction negatives from its result, not by default.

**Fix**
4. Fix the Austin `AUS` campaign and the bare "georgia" keywords.
5. Scale UK+IE search values by about 0.7; decide GCC and Africa explicitly (scale down, cap their spend, or
   leave them on the current strategy).
6. Check shared negative lists in the UI; add reverse-direction negatives only where step 3 says reverse
   searchers do not book.
7. Move the 113 `PRESENCE_OR_INTEREST` campaigns (mostly UK+IE) to `PRESENCE`, unless intended.

**Launch design**
8. Staged by tier portfolio, with design B holdouts on their own budgets; Performance Max out of the read.
9. Pull India Adobe v84 (same notebook as PK, India segment) so bookings can be measured without
   cross-device modelling, including the four groups that have no ledger guardrail.
10. No other changes in the two weeks either side of each stage.
