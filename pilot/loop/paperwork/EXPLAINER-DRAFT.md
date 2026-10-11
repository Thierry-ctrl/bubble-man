# Bubble Man: a first utility-data trial

*Draft discussion document - 11 October 2026*

## What we want to help with

**My inference - proposal:** help staff decide when to investigate a water zone by spotting unusual rises in night flow, using meter data the utility already holds.

## What the simulations show

**Verified:** on 1,000 fresh LeakDB simulations, the improved rule flagged about 89% of eligible sudden leaks within a week. For those flagged, the median warning delay was 13.5 hours. About 47% of all warnings matched a new leak under the scoring rules, below our provisional 50% target. Some other warnings occurred during older leaks. These are simulation results, not real-utility performance. [Saved results][results]

## The smallest useful trial

**My inference - proposal:** start with one clearly bounded zone, preferably continuous supply and existing logged flow meters. First request 2-4 weeks of readings to check format and quality. Prefer 15-minute readings or finer; compatible regular 30-minute readings may also be usable. If suitable and authorised, use at least a year of history, operating logs and separate incident records. No new hardware is proposed for this first stage.

## How we would judge it

**My inference - proposal:** agree the rule and evaluation before incident records are opened. Ask whether warnings precede first reports of confirmed leaks, and count the work needed to investigate them. A first report is not a leak's start, so an earlier warning is a timing association, not proof it detected that leak. Keep unchecked warnings unknown. Time-shifted warnings provide a descriptive reference, not automatic proof. A later live trial would record inspections, including some randomly chosen no-warning nights. [Scoring draft][scoring]

## What remains uncertain

**Unverified:** performance on real readings, manageable staff workload and a suitable available zone. **Verified:** the current prototype identifies a change in a zone, not a leaking pipe. Rationed supply, tank refilling, storage and operating changes need special attention; the present tools do not establish suitability for those conditions. [Pilot guide][pilot]

## The decision now

**My inference - proposal:** identify the zone and data owner, agree permitted use and confidentiality, and review a small readings-only sample. Detailed incident records stay separate until the evaluation is fixed. Nothing has been sent or approved.

[results]: /Users/uwonkundathierryrugira/Bubble-man/analysis/next-fair-evaluation/RESULTS-LEAKDB-1000.md
[scoring]: /Users/uwonkundathierryrugira/Bubble-man/pilot/loop/SCORING-DRAFT.md
[pilot]: /Users/uwonkundathierryrugira/Bubble-man/PILOT-READINESS.md
