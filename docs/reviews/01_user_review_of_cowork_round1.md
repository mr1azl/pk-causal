# Review of Cowork's first PK round (pasted by the user, 7 Oct 2026)

*Verbatim from the conversation. Written by the user (or their earlier assistant) after checking Cowork's
first-round numbers against the committed daily monitoring data. Cowork's brief is in
`docs/source_material/Cowork_handover_PK.md`.*

---

Cowork's work is useful and mostly well done. Its biggest find also weakens what we told the client about PK, so it needs one more round before anyone acts on it. I checked its numbers against our committed daily data.

## The most important finding: the two booking counts disagree, and only after the switch
Cost and clicks match our daily report almost to the dollar (963, 428 and 513 a day; cost per click 0.312, 0.225 and 1.479). So we are looking at the same campaigns. Bookings and revenue do not match:

| Period | Bookings a day, API booking actions (Cowork) | Bookings a day, Bookings (FL) (ours) | Revenue per booking, API | Revenue per booking, FL |
|---|---:|---:|---:|---:|
| 1 to 19 Aug | 9.21 | 11.16 | $1,215 | $346 |
| 20 Aug to 1 Sep | 6.38 | 6.54 | $1,446 | $423 |
| 2 to 19 Sep | **0.83** | **5.00** | $1,384 | **$110** |
| After 20 Sep | 1.33 | 3.12 | $1,191 | $672 |

- The two counts agree before the switch. After it, Bookings (FL) is about **6 times** the API count, and the extra "bookings" carry almost no revenue. That is where our 68% zero-revenue figure comes from.
- The API revenue per booking stays plausible, around $1,200 to $1,450. The FL figure does not. Our CM360 data gives about $1,460 a booking across the network.
- **If the API count is right, the switch cut PK bookings by about 87%, not 15%.** The six-market deck says PK lost bookings mostly to the budget cut and only modestly to the switch. That would no longer hold.
- On revenue, both sources agree: it collapsed at the switch.
- So I agree with Cowork that the 68% is a reporting problem, not a tag failure. But the result is more serious than its file suggests. Until this is reconciled, don't present the PK booking slide again.

## What holds up
- **The mechanism.** Cost per click rose about five times on a fixed budget, so traffic fell. Budget-lost impression share went from 7.7% to 62% and then 80% between 1 and 3 Sep. This fits our earlier read.
- **The switch dates.** All 543 campaigns were last modified on 2 or 3 Sep. That is real metadata, not inferred.
- **Value per search is stable** at about $39 to $42 a search over each long period. That is good news. It doesn't rule out our launch-week dip of 40%, which long averages would hide.
- **New facts:**
  - The daily budget is now $490.33, not $508.30.
  - A `Flight Search (TEST Sept2026)` action is live and counted as primary.
  - Three separate actions are named `Booking`.
  - The portfolio is owned by the manager account.

## What doesn't hold up or needs correcting
1. **The "20 Sep CPC cap" is not supported.** Cowork itself found that nothing was modified on 20 Sep and that the portfolio has no CPC ceiling. In our data, cost per click falls steadily from about 14 Sep: 1.45, 1.20, 0.99, 1.02, 0.95, 0.80, 0.72, 0.53. That looks like the bidder relearning, not a step change. **Did you or the client actually apply a cap?** If not, recommendation 4 ("replace the flat cap") falls away.
2. **"Rank lost 0% proves it never lost on rank" is circular.** From 4 to 17 Sep the report hits its limits: impression share shows its 10% floor and budget-lost its 90% ceiling. The three shares add to 100%, so rank-lost comes out as 0 automatically. Only the post-switch 0% is evidence.
3. **The conversion-level check covers only part of the bookings.** It used 87 booking rows, but Cowork's own daily table implies about 290 bookings in the same window. "Revenue intact" holds for those 87 rows only.
4. **Two booking rates that don't match.** Section 4 gives 7.37, 8.01, 6.81 and 2.70 bookings per thousand searches. The breakdown by campaign type gives 11.97, 16.16 and 7.56. The two use different booking actions. The "quality drop of 15% to 43%" needs one consistent definition. On our FL count there is no drop after 20 Sep (about 11 per thousand, the same as August).
5. **"The bidder maximises zero" is unlikely.** Our budget-shift analysis found spend followed the rule-based VBB value per dollar (t 3.8) and not the ML value (t -0.2). That only happens if the bidder sees the VBB values, so the portfolio probably has its own goal set to `QR_FlightSearch_VBB`. Reading the portfolio goal in the UI is still the right check.
6. **The August baseline was measured differently.** Cowork measured the zero-revenue share by campaign and week (32% to 64%). Ours is by portfolio and day (8% and 1% in August, from the same daily data). The finer split gives a higher share mainly because bookings and revenue land in different campaigns within the FL columns. That supports Cowork's point that these columns are inconsistent. It doesn't mean our baseline can't be reproduced.
7. **Not run yet:** C6 (the $0.50 fallback share and duplicate order IDs), C7, and the Bing accounts.

## Next round to paste into Cowork
> Keep working locally in `~/pk_vbb_investigation/`, same rules (scripts in `scripts/`, log in `LOG.md`, no credentials in files, no em dashes).
>
> 1. **Reconcile bookings day by day, 1 Aug to 4 Oct.** Build one daily table with:
>    - the `Bookings (FL)` and `Revenue (FL)` custom columns, queried through the API;
>    - the conversions and value of every booking-like action, separately: `QR_Booking`, each of the three `Booking` actions by id, `Flight Search (TEST Sept2026)`, and the `sales`-type rows of `QR_FlightSearch_VBB`.
>
>    Find which action or actions make up the gap between Bookings (FL) and the API count after 2 Sep. Do it by click date and by conversion date.
> 2. Explain why `FROM conversion` returns 87 booking rows while the metrics show about 290 bookings over the same dates.
> 3. Pick one booking definition and redo the section 4 table and the campaign-type table with it.
> 4. Remove the 20 Sep "CPC cap" unless there is evidence that a cap was set. Describe the post-14 Sep fall in cost per click as observed, cause unknown.
> 5. Note that rank-lost 0% from 4 to 17 Sep comes from the clamped values.
> 6. Read the portfolio's conversion goal in the SA360 UI and record it.
> 7. Run C6: the daily $0.50 share, the zero-value share and duplicate order IDs for PK non-brand.
