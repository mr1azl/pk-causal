# Prompt for an independent fresh review

*Paste the block below into a new session that has access to the `mr1azl/pk-causal` repo (merge PR #3 first, or
point it at branch `claude/peaceful-keller-g9kkzh`).*

```
You are reviewing an investigation into Qatar Airways' paid search in Pakistan (PK). Treat the existing analysis
as a claim to test, not as a conclusion to accept. I want an independent view, and I would rather hear that the
analysis is wrong than have it confirmed.

The decision this informs:
1. Should PK non-brand search be switched back from value-based bidding (VBB) to its previous strategy?
2. Is it safe to roll VBB out to India and similar markets, and with what conditions?

Repo: mr1azl/pk-causal. Start with README.md (facts, measurement traps, current conclusions with confidence,
open questions, repo map). Then:
- docs/source_material/VBB_Rollout_Readiness_readout.html: what was originally claimed about PK.
- docs/analysis/08_PK_DECISION.md: the current conclusions and recommendation.
- docs/reviews/: earlier reviews, including ones that changed the analysis.
- data/ (documented in data/README.md) and scripts/ (scripts/README.md): everything needed to reproduce.
- docs/agent_findings/: what the SA360 API agent found in rounds 3 to 6 (PK, SA, CA, MY).

How to work:
1. Rebuild the key numbers yourself from data/, not from the notes. At minimum:
   a. PK non-brand bookings and revenue by click date, UK+IE vs the rest, for 13 Jun-19 Aug, 20 Aug-1 Sep,
      2-19 Sep, 20 Sep-5 Oct 2026 (Adobe, data/adobe/).
   b. The same months in 2025 (seasonality).
   c. Brand and non-brand together, Aug vs Sep, 2025 and 2026.
   d. The UK effect on each booking measure: Adobe, the Floodlight ledger, QR_Booking all_conversions and
      Google's Booking tag.
   Where your numbers differ from the notes, say so and say which is right.
2. Try to break the main conclusions. In particular:
   - Is the UK drop real and large enough to act on, or mostly small numbers and the many segments examined?
   - Is "total PK held up in September" sound, or an artefact of brand moving for unrelated reasons, of the
     2025 comparison (2025 non-brand spend also fell in September), or of Adobe attribution?
   - Does the proposed UK mechanism (inflated UK search value, reverse-direction and generic queries, weaker
     Google Flights position) actually explain the drop, or is it a story fitted after the fact? What else could?
   - Were any explanations ruled out too quickly (seasonality, tracking, brand migration, competitors, fares)?
   - Is the CPC spike from the missing ROAS target, or something else?
3. Look for what the investigation never looked at. Examples: revenue per booking and route mix within
   destinations, Bing accounts, Performance Max, day-of-week or lag effects, the 20 Aug cut list itself,
   anything in the agent findings that was noted but not chased.
4. Keep the measurement traps in README section 2 in mind, and do not use "Bookings (FL)" / "Revenue (FL)".
5. Be explicit about uncertainty: give counts, not only rates, and say how many bookings a conclusion rests on.

Deliver one Markdown file, docs/analysis/11_FRESH_REVIEW.md, with:
1. Your answer to each decision question in two or three sentences, and how confident you are.
2. A table of the main conclusions in README section 3: agree / partly / disagree, with your own number and
   the file or script it came from.
3. Anything new you found, and anything the investigation got wrong.
4. The two or three checks or experiments that would most change the decision, in priority order.
Save any script you write in scripts/ with a usage line at the top, and commit both.

Rules: no credentials, gclids, order IDs or client IDs in any file you write; no em dashes in anything you write;
plain, direct language. If you need data that is not in the repo, say exactly what and why rather than guessing.
```
