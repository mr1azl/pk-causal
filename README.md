# PK value-based bidding investigation

Why did Qatar Airways' Pakistan (PK) paid search look broken after its non-brand campaigns moved to value-based
bidding (VBB) on 2 Sep 2026? Should PK be switched back, and is it safe to roll VBB out to India and similar
markets?

This README is the entry point. It summarises the facts, the data, the traps, and the current conclusions with
how sure we are of each, so a fresh reviewer can start without the chat history.

---

## 1. Facts and timeline

| Date | Event |
|---|---|
| 22 Aug 2025 | PK non-brand account rebuilt with new pipe-named campaigns (`Google\|PK\|Dest\|Country\|XXX\|GB\|EN\|MOD`); 2025 is mostly legacy names (`_PK-Country-XXX-GB-EN_phrase`). |
| Jan to Aug 2026 | Mix shifts: UK moves from route to city campaigns (Jan), then a big push on GB country campaigns (May to Aug). |
| 30 Jul 2026 | DE and SG switch to VBB. |
| **20 Aug 2026** | **Budget cut** on about 50 to 70 PK non-brand campaigns, including the two GB country campaigns (88% of PK's UK spend). |
| **2-3 Sep 2026** | **Switch.** PK, SA, CA, MY non-brand portfolios move to Maximise Conversion Value. |
| 7 Oct 2026 | Analysis date; data runs to 5 Oct. |

- **Before the switch:** Maximise Conversions on flight-search counts (no target).
- **After the switch:** Maximise Conversion Value on `QR_FlightSearch_VBB`, the value of each flight search from a
  route value table. PK and CA use rule-based values, SA and MY ML values. **No target ROAS, no CPC limit** in any
  of the four portfolios; all are owned by the MCC (1144701035). PK shares one budget of about $490 a day.
- **Bookings were never in the bidding objective**, before or after.
- PK accounts: non-brand Google `4851538229` (all of it non-brand), brand `1423602235`, plus two Bing accounts (not
  analysed).

## 2. How bookings are measured, and the traps

| Measure | What it is | Use it? |
|---|---|---|
| **Adobe eVar84** (`data/adobe/`) | One row per click (tracking ID with gclid); bookings are orders (event27), revenue SalesIncYQ. Credit them to the click day. | **Yes, main source.** |
| **Floodlight ledger** (`QR_Booking`, `FROM conversion`) | One row per transaction, quantity 1. Matches Adobe: 89 vs 89 bookings, 49 identical rows. | **Yes.** |
| `QR_Booking` all_conversions | Attributed, includes Google cross-device modelling: 3.5x the ledger overall, 9.8x for PK regional (83% cross-device). Modelled conversions arrive late, so the last 2 to 3 weeks read low. | Comparisons only. |
| `Booking` (Google Ads webpage tag) | A separate Google tag, data-driven attribution, 30 days. No Floodlight behind it. | Good fast cross-check. |
| **"Bookings (FL)" / "Revenue (FL)"** (readout, daily monitoring) | Adds `QR_Booking` and `Booking`: two systems summed. Source of the "68% zero-revenue bookings". | **No.** |

Other traps, each of which misled an earlier read:
1. **The 20 Aug cut sits 13 days before the switch.** Any before/after that folds 20 Aug to 1 Sep into "before"
   blames the switch for the cut.
2. **Two campaign naming conventions.** A pipe-only parser drops 71% of 2025 spend. `scripts/pk_seasonality_adobe.py`
   and `agent_code/sa360/lib_sa360.py` parse both.
3. **Brand is not a clean control.** Brand CPC and conversion moved in September 2026 for their own reasons (the
   same brand CPC rise appears in India, which did not switch). The Causal Impact readout used brand as the control.
4. **Small numbers.** PK non-brand is 1 to 2 Adobe bookings a day; the UK is a fraction of that.
5. **Impression share clamps** at 10% and 90%. **SA360 attributes are current values, not history.**
6. **Rule-based "value per search"** can be joined to the route searched, not to the campaign.

## 3. Current conclusions (7 Oct 2026)

Full argument: `docs/analysis/08_PK_DECISION.md`.

| Conclusion | Confidence | Main evidence |
|---|---|---|
| Total PK paid search held up in September 2026: bookings +3% Aug to Sep, against -24% in 2025 (brand beat its seasonal pattern; non-brand fell about as every September). | Medium-high | Adobe, analysis 08 s7 |
| Outside the UK, PK non-brand bookings held through the switch and improved per click. | Medium-high | Adobe click date; Google `Booking` tag |
| The UK fall is real and UK-specific: about -50% bookings per click on the Google tag; about 1 booking against 5 expected on Adobe and the ledger. | Medium | Adobe, ledger, Google tag, 2025 control |
| Not seasonality, not tracking, not user location, device, campaign edits, location settings, keyword choice or brand migration. | High for each | SA360 rounds 3-4, Adobe 2025, search terms, brand search terms |
| Likely drivers of the UK fall: the UK search value is the most inflated relative to booking value (5.7 vs 3.0 regional); UK campaigns now buy reverse-direction and generic queries (off-target 6% in Aug to 22-28% in Sep-Oct); QR's Google Flights position on PK-UK weakened from mid-August. | Medium-low: consistent with the data, not tested directly | analysis 06-08 |
| The CPC spike (2 to 7 times) and budget-limited serving after the switch come from bidding with no ROAS target. Seen in all four markets. | High | SA360 rounds 3, 5, 6 |
| "CA -26% / MY -29% conversion damage" is an artefact of using the last 16 days of attributed conversions. | High | agent's own `g1` reconciliation |

**Recommendation:** do not switch PK back wholesale. Add a target ROAS (or a CPC limit), fix the UK (recalibrate
UK search values or move UK campaigns to a booking-based goal), add reverse-direction and generic negatives, and
measure on the ledger or Adobe. For India: launch with a ROAS target, value calibration by destination, query
cleanup at least two weeks before, a holdout, and a weekly guardrail per destination group.

## 4. Open questions, and where this could be wrong

- **No direct test of the UK mechanism.** The decisive test is an experiment: UK campaigns back on the old strategy
  for 2 to 3 weeks. Without it, the UK drivers above are an explanation that fits, not a proof.
- **The UK effect rests on few bookings.** About 5 expected on Adobe. The Google tag (more volume) says about half.
- **Brand in September 2026** converted unusually well and its CPC rose 27% to 44% (PK `Brand|Hero` +27% is not
  mirrored in India). Not explained; needs brand impression share and auction insights.
- **The 2025 comparison** is imperfect: 2025 non-brand spend also fell in September, and 2025 UK campaigns were small
  and cheap.
- **GFS** has no competitor rows, so a competitor move on PK-UK (for example new direct capacity) cannot be seen.
- India pre-launch SA360 checks (`docs/prompts/INDIA_PRELAUNCH_PROMPT.md`) have not been run yet.

## 5. Repo map and reading order

```
README.md                      this file
docs/
  analysis/                    my analysis notes, in the order they were written
    01_PK_VBB_DIAGNOSIS.md       first diagnosis, before any raw data (partly superseded)
    02_PK_ADOBE_FRESH_LOOK.md    Adobe click-level analysis; keyword mix; two review rounds with corrections in place
    03_PK_SA360_ROUND3.md        seasonality (SA360 2025), what a Floodlight booking is
    04_PK_SEASONALITY_AND_BIDS.md seasonality on Adobe 2025, bids and impression share
    05_PK_KEYWORD_TRENDS.md      keyword mix May 2025 to Oct 2026
    06_PK_ROUND4_REVIEW.md       location, device, changes; value per search (with a correction)
    07_PK_GFS_CHECK.md           Google Flights price, visibility, demand
    08_PK_DECISION.md            the decision note: cause, switchback, India; brand in depth
    09_INDIA_SEARCH_TERMS.md     India query risks before launch
  agent_findings/              the SA360 agent's own FINDINGS and LOG per round (3: PK; 4: PK; 5: SA; 6: CA, MY)
  reviews/                     reviews pasted into the chat (user, earlier model) and the user's correction
  prompts/                     prompts given to the agents (data requests, India pre-launch)
  source_material/             documents the investigation started from (readout, handovers, API and GFS guides)
data/                          all data, see data/README.md
scripts/                       analysis scripts, see scripts/README.md
agent_code/sa360/              the SA360 agent's round 3 code
sql/, notebooks/               GFS queries and notebook; the Adobe pull notebook
```

Suggested reading for a fresh review: this README, then `docs/analysis/08_PK_DECISION.md`, then
`docs/source_material/VBB_Rollout_Readiness_readout.html` (what was claimed) and the reviews, then the data.

## 6. Notes for a fresh reviewer

- Every claim in the analysis notes names its source file and, where possible, the script that reproduces it.
  Withdrawn or corrected claims are kept in place and marked, so the reasoning history is visible.
- Things worth challenging: whether the UK drop is large enough to act on; whether brand's September jump is
  partly the switch (halo) and should count in VBB's favour; whether the 2025 control is good enough; whether
  search-value calibration by destination is the right fix or a ROAS target alone would do.
- The user's own monitoring and readout figures use "Bookings (FL)"; prefer Adobe and the ledger when they disagree.
