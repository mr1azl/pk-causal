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

## 3. Current conclusions (revised 8 Oct 2026)

Full argument: `docs/analysis/08_PK_DECISION.md`, as revised by `docs/analysis/11_FRESH_REVIEW.md` and
`docs/analysis/12_RESPONSE_TO_FRESH_REVIEW.md`.

| Conclusion | Confidence | Main evidence |
|---|---|---|
| Total PK paid search bookings rose 3% Aug to Sep 2026 (-24% in 2025). True of the account, **not evidence for VBB**: brand rose in all six markets, the 2025 baseline contains the brand rebuild, non-brand bookings per $ fell 9% (rose 62% in Sep 2025). | High (as description) | analysis 11 s4.2, 12 |
| Outside the UK, no measurable VBB effect either way: per $ bookings -13% / revenue -34% vs Jun-Aug, +10% / -6% vs the cut fortnight, on 36 bookings. Per-click "improvement" was a CPC artefact. | Medium | analysis 11 s3.1, 12 |
| The UK loss is GB: 0 bookings against 4.5 expected (p 0.011) after the switch; Ireland normal. It rests on one last-click record (Adobe = ledger = QR_Booking); the Google tag shows no drop in 2-19 Sep. | Medium-low | analysis 11 s3.4, 4.1 |
| Not seasonality, user location, device, campaign edits, location settings or keyword choice. Brand migration and a channel shift of GB bookings are **untested**. | High / untested | SA360 rounds 3-4, Adobe 2025, analysis 11 s4.4 |
| The rule-based search values over-rate UK relative to bookings (5.0 vs 3.8 long-haul, 2.9 regional); the ML values recorded in the same account are calibrated (2.2 / 2.4 / 2.0). Query drift and GFS do not explain the GB loss. | High (values) / mechanism untested | analysis 11 s4.3, 12 |
| The CPC spike and budget-limited serving are the switch's learning period; no market had a target, so "no target" is the likely lever, not a demonstrated cause. | Medium | analysis 11 s4.5 |
| On Adobe orders per $, VBB was positive in CA (+38%) and MY (+203%), negative in SA (-21%), flat in PK (+2%). | Medium | analysis 11 s5 |
| "CA -26% / MY -29% conversion damage" is an artefact of the last 16 days of attributed conversions. | High | agent's `g1`, analysis 11 |

**Recommendation (revised 8 Oct, see `docs/analysis/12_RESPONSE_TO_FRESH_REVIEW.md`):** move the UK+IE campaigns
back to the previous strategy on their own budget for three weeks (fix and test in one); keep the rest on VBB with a
target ROAS or CPC cap; switch the value signal to `QR_FlightSearch_VBB_ML` if the portfolio allows; check GB
bookings by channel. India: a measured test with ML or calibrated values, a target ROAS, a holdout and an Adobe
guardrail by destination, after the blocking items in analysis 10.

## 4. Open questions, and where this could be wrong

- **No direct test of the UK mechanism.** The decisive test is an experiment: UK campaigns back on the old strategy
  for 2 to 3 weeks. Without it, the UK drivers above are an explanation that fits, not a proof.
- **The UK effect rests on few bookings.** About 5 expected on Adobe, 1 seen; the Google tag shows no drop in 2-19 Sep.
- **Brand in September 2026** converted unusually well and its CPC rose 27% to 44% (PK `Brand|Hero` +27% is not
  mirrored in India). Not explained; needs brand impression share and auction insights.
- **The 2025 comparison** is imperfect: 2025 non-brand spend also fell in September, and 2025 UK campaigns were small
  and cheap.
- **GFS** has no competitor rows, so a competitor move on PK-UK (for example new direct capacity) cannot be seen.
- India pre-launch checks are done (`docs/agent_findings/sa360_india_prelaunch/`, reviewed in
  `docs/analysis/10_INDIA_PRELAUNCH_REVIEW.md`). Blocking: 646 campaign edits in September unexplained; which value
  signal the portfolios read; whether reverse-direction searchers book (test via the route on VBB `sales` rows).
- India GCC and Middle East: 169k clicks, 5 Floodlight transactions in 8 weeks; the value signal rates it highly.

## 5. Repo map and reading order

```
README.md                      this file
docs/
  VBB_CHECKLIST_NOUVEAU_MARCHE.md  pre-switch checklist for a new market (French)
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
    10_INDIA_PRELAUNCH_REVIEW.md review of the agent's India pre-launch checks; what blocks launch
    11_FRESH_REVIEW.md           independent review of 01 to 09 (Fable): rebuilt numbers, where they hold, where they do not
    12_RESPONSE_TO_FRESH_REVIEW.md what the fresh review changes; revised conclusions and next steps
    13_UK_SWITCHBACK_LIST.md     the 60 GB campaigns to move off VBB, how, and what to expect
    14_ROUND8_PAIRING_REVIEW.md  review of round 8 (13-market profiles, test power, pairing): power holds, priors do not
  agent_findings/              the SA360 agent's own FINDINGS and LOG per round (3: PK; 4: PK; 5: SA; 6: CA, MY; India pre-launch; 8: market profiles)
  reviews/                     reviews pasted into the chat (user, earlier model) and the user's correction
  prompts/                     prompts: agent data requests, India pre-launch, fresh review
  source_material/             documents the investigation started from (readout, handovers, API and GFS guides)
data/                          all data, see data/README.md
scripts/                       analysis scripts, see scripts/README.md
agent_code/sa360/              the SA360 agent's round 3 code
sql/, notebooks/               GFS queries and notebook; the Adobe pull notebook
```

Suggested reading for a fresh review: this README, then `docs/analysis/08_PK_DECISION.md`, `11_FRESH_REVIEW.md` and
`12_RESPONSE_TO_FRESH_REVIEW.md`, then
`docs/source_material/VBB_Rollout_Readiness_readout.html` (what was claimed) and the reviews, then the data.

## 6. Notes for a fresh reviewer

- Every claim in the analysis notes names its source file and, where possible, the script that reproduces it.
  Withdrawn or corrected claims are kept in place and marked, so the reasoning history is visible.
- Things worth challenging: whether the UK drop is large enough to act on; whether brand's September jump is
  partly the switch (halo) and should count in VBB's favour; whether the 2025 control is good enough; whether
  search-value calibration by destination is the right fix or a ROAS target alone would do.
- The user's own monitoring and readout figures use "Bookings (FL)"; prefer Adobe and the ledger when they disagree.
