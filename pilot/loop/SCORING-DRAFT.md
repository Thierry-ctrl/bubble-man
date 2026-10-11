# Draft scoring for real utility records

**not frozen — needs human approval before any real records are seen**

**Verified (local scope):** preparation item 3, 11 October 2026. The standalone prototype and checks use invented records only. No real incident/repair rows, LeakDB labels or detector outputs were evaluated in this iteration.

## The question we can answer

**Verified (local source link):** [PILOT-READINESS.md](/Users/uwonkundathierryrugira/Bubble-man/PILOT-READINESS.md) distinguishes first report, confirmation and repair completion. It says a missing record does not establish a leak-free period and an unchecked warning remains unknown.

**My inference — proposed interpretation:** a first report is an upper bound on when a confirmed leak began, provided the report actually concerns that leak. It does not tell us its start. A warning before that report can be an **early timing association**, not proven detection of that leak. Repair completion is a different event and cannot replace the first report silently.

**My inference — INVENTED example:** a warning on Monday and a first report on Wednesday are two days apart. The leak might have begun on Tuesday. We can report the two-day interval; we cannot say the Monday warning detected that leak. This is why timing associations and field findings stay separate below.

**Unverified:** real record meanings, completeness, inspection sensitivity, staffing capacity and suitable zone data remain unknown. This draft is not a claim about real utility performance.

## 1. Decide the protocol before opening records

**My inference — proposed sequence:**

1. Agree the zone, one detection rule, timezone, dates, data permission and record meanings using a schema or blank export specification. Do not inspect real event rows yet.
2. Approve this scoring protocol: incident deduplication, report-time precision, observation cutoff, warning/record eligibility, missing-data rules, comparison method and staff workload target.
3. Build and freeze any necessary input adapter and the readings-only exposure calendar. The calendar lists nights when the unchanged method could issue a warning. Derive exclusions from declared reading-quality and operating rules, never leak outcomes.
4. Save and commit the warning list, exposure calendar and checksums before opening permitted incident records. Keep both rule lists separate if a comparator is approved.
5. Open the records once within the approved scope, reconcile duplicate tickets without looking at warning matches, and preserve a raw-to-canonical audit trail. Record changes in meaning or completeness; do not improvise favourable scoring changes.
6. Score and report the complete set, including exclusions, ambiguous links, unknown visits and limitations. Protocol amendments become disclosed exploratory work, not a rerun of the same untouched test.

**My inference:** a retrospective timing study is preparation for a later live shadow trial. Historical “would have warned” calculations do not establish what a crew would actually have found.

## 2. Inputs and meanings

**My inference — proposed data contract:**

| Input | Required meaning |
|---|---|
| Warning | Stable ID, zone and earliest actual **issuable time**, with explicit UTC offset. One rule per invocation. Do not use the start of a signal run as if staff could already have received it. |
| Evaluation window | One zone, fixed local UTC offset, start inclusive and end exclusive. In this prototype the end is also the observation cutoff for records and visits. |
| Exposure calendar | Approved issue timestamps from readings/operating information. For the present method these are the applicable 04:00 times after its learning/warm-up requirements. Gaps stay visible. The prototype consumes this calendar; it does not compute it from readings. |
| Canonical incident | Stable deduplicated ID and zone, confirmation time, first-report time or bounds, optional repair completion, and an independently recorded pre-existing flag. Preserve location, asset, report source and provenance in the eventual adapter/audit export. |
| Inspection | ID, zone, warning or random-control origin, planning and actual check time, outcome, finding IDs and recorded staff time. A random control also needs its selection probability and selection audit. |

**My inference:** repeated tickets and follow-up repairs may concern one incident. The deduplication criteria need utility approval; unique CSV row IDs alone do not make them distinct leaks. Do not invent first-report times from a flow plot or from the warning dates.

**My inference:** a date-only report is a range from that local day's midnight through its final microsecond. Never assign it a fake exact midnight. Equal bounds mean an exact timestamp. If timestamp meanings or chronology are inconsistent, quarantine the source rows for review; do not silently repair them.

**Verified (local source links):** the existing [converter](/Users/uwonkundathierryrugira/Bubble-man/pilot/convert_utility_data.py) records the local offset in its conversion report and writes naive local-standard-time flow timestamps. The [warning wrapper](/Users/uwonkundathierryrugira/Bubble-man/pilot/run_frozen_rule.py) writes both rules with `issue_time_local` and no stable warning-ID column. **My inference:** a later adapter must select one rule, restore the approved offset from metadata, and create stable IDs. The prototype is not wired into these files.

## 3. Retrospective timing associations

**My inference — proposed horizon:** look for a warning in the **seven days before first report**, strictly before the report. Seven days is a proposal to approve, not a validated real-world onset deadline. Report the exact horizon; do not choose it by which value catches more recorded events.

**My inference — proposed record eligibility:** use confirmed, deduplicated incidents in the chosen zone, with usable report bounds. Exclude explicitly pre-existing records, missing reports, unconfirmed cases, confirmation after the cutoff, reports without a full preceding seven-day calendar span, and report ranges crossing the cutoff. An incident with no approved warning opportunity is unassessable. Show the number of available issue opportunities per incident, including variation caused by gaps.

**My inference — proposed warning eligibility:** keep **every in-window warning** in the operator workload. For timing comparison only, use warnings in the approved exposure calendar with a complete seven-day follow-up span before the cutoff. Exclude the final incomplete span uniformly, even when a known later report would make one warning look successful. Preserve all excluded warning rows and reasons.

**My inference — proposed time rule:** for warning time `w` and report bounds `[a,b]`, a guaranteed pre-report timing link requires `w < a` and `b − w ≤ 7 days`. “Guaranteed” applies to the reported bounds only, not leak existence or cause. The lead interval is `[a − w, b − w]`. If only some possible report times qualify, list an uncertain link separately. A warning exactly at an exact first-report time is not early.

**My inference — proposed ambiguity rule:** retain every candidate link. Use the maximum **one-to-one timing-association count**: one warning can contribute at most one incident and one incident at most one warning. Report the candidate lists, warnings with multiple candidates and records with multiple candidate warnings. The count is bookkeeping, not selection of a leaking pipe. Its share of eligible records is called **record-association share**, never leak sensitivity or detection rate.

**My inference:** show the count both under the guaranteed bounds and when uncertain date-only links are allowed. The latter is an uncertainty diagnostic, not an alternative headline to choose after scoring. Zero eligible records produces no ratio, rather than a perfect or zero detection score.

**My inference — labels:** an unmatched exposed warning is **“no recorded eligible leak”**. A recorded incident with no candidate warning is **“no pre-report association”**. Neither means “false alert” or “missed leak.” The true onset, background leakage and unrecorded events are unknown. A warning linked to an older incident may still be valuable to staff; its field finding belongs in the separate assessment.

## 4. Field findings and workload

**My inference — proposed outcomes:**

| Warning investigation episode | Recorded interpretation |
|---|---|
| Leak found | At least one completed follow-up records a confirmed finding with an auditable incident ID. No pipe-localisation or onset claim is inferred. |
| Checked, nothing found | Completed checks found nothing and no follow-up remains pending/incomplete. This is not proof the zone was leak-free. |
| Unknown | No visit, an incomplete check, or a pending follow-up without a recorded finding. A timing match never changes this to “leak found.” |

**My inference:** count every warning as one investigation episode and every follow-up visit separately. Several findings within one episode still count once. Different warning episodes may rediscover the same incident: retain their visit findings but also report distinct incident IDs and repeat findings, so they are not mistaken for separate new leaks. A later finding supersedes earlier negative checks; a pending follow-up after a negative check remains unknown.

**My inference — proposed report:** show all three counts, completion coverage, and finding yield **among completed investigation episodes**: `found / (found + checked_nothing_found)`. Present this alongside the unknown count and total warnings. It is not a precision estimate for all warnings, and it is not directly comparable with LeakDB's label-based yield. Selective inspection can make it optimistic.

**My inference:** report warnings per calendar month, visit count, recorded staff minutes and the number of visits missing that measurement. Unknown staff time is not zero. Keep retrospective record associations out of field-yield numerators.

## 5. Random control visits in a shadow trial

**My inference — proposed design:** staff inspect warning nights and a randomly selected sample of **eligible no-warning nights** using comparable effort and search scope. Pre-agree selection probability, staffing budget, time of inspection and operational exclusions. Log every selection, cancellation, incomplete visit and outcome. Do not replace a cancelled or negative control with a more convenient or promising one after seeing results.

**My inference:** the live selection must be made using information available that night, after determining whether a warning exists and before any visit outcome. A practical design is an approved fixed-probability draw on each eligible no-warning night. If seasons/supply regimes need separate groups, define them and their probabilities first; compare findings within those groups and keep unequal sampling explicit.

**Verified (local code link):** [the prototype](/Users/uwonkundathierryrugira/Bubble-man/pilot/loop/real_record_scoring.py) includes a closed-calendar **invented-case planning helper**: uniform selection without replacement, no incident inputs, recorded pool hash/seed/inclusion probability. **My inference:** this is not a live scheduler; retrospective selection from a full future warning calendar cannot demonstrate a real-time implementation.

**My inference:** report completed-check yield and completion coverage for controls separately from warning episodes. A higher warning yield is useful operational evidence, but warning and control nights were not randomly assigned to receive a warning, and a recorded probability alone does not prove the randomisation plan was followed. Staff inspection consistency and selection logs need auditing.

## 6. Whole-week shift comparison

**Verified (source link):** Yuan and Shou explain that time-series shuffling can invalidate ordinary permutation tests and circular shifts can create artificial end/start neighbours. Their proposed test's guarantees require stationarity; those guarantees do not automatically apply to this pilot design. [2024 primary methods paper](https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.3002758)

**My inference — proposed descriptive comparison:**

1. Preselect a fixed-offset window containing an integer number of whole weeks. Keep any remainder outside the timing comparison and disclose it; its warnings still belong in a separately stated workload report.
2. Use the observed warnings in complete approved timing exposure. Rotate the whole set by each nonzero whole-week offset, wrapping within that window. This preserves weekday and clock time.
3. Keep the records, horizon and exposure calendar fixed. Reject an **entire rotation** if any warning lands outside complete approved exposure. Do not drop individual shifted warnings or relax the mask to create more comparison patterns.
4. Report identity rotations, duplicate time patterns and exposure rejections. Compare each distinct valid pattern once, using the same one-to-one timing count.
5. Show the observed count, every reference count, and the number at least as high. The prototype's `(1 + at_least_as_high) / (1 + distinct_valid_patterns)` is a **descriptive rank fraction**, not a formal p-value. With no valid patterns, report “not assessable.” With few patterns, report the limited resolution.

**My inference:** seasons, interruption schedules, missingness and inspection practices may change through the year. The valid rotations can be a selected subset, and wrapping changes adjacency. No significance or “beats chance” decision should be based on this fraction until the null hypothesis and comparability assumptions receive separate approval. Do not transfer statistical guarantees from the cited paper to this different procedure. This proposal changes no earlier locked result.

## 7. Prototype coverage and checks

**Verified (local code/test links):** [real_record_scoring.py](/Users/uwonkundathierryrugira/Bubble-man/pilot/loop/real_record_scoring.py) provides separate timing, field-visit, invented control-selection and week-shift functions. [test_real_record_scoring_INVENTED.py](/Users/uwonkundathierryrugira/Bubble-man/pilot/loop/test_real_record_scoring_INVENTED.py) contains only made-up cases. There are no file loaders or detector imports.

**Verified (test run, 11 October 2026):** 39 checks passed on Python 3.9.6, including an independent brute-force check of all 512 invented three-warning/three-incident graphs. The cases cover report bounds, exact horizon edges, overlapping incidents, repeat associations/findings, missing reports, pre-existing records, censoring, exposure gaps, unknown visits, follow-ups, staff-time gaps, random-control audit fields and rejected/duplicate week-shifts. An initial import failure on Python 3.9 was corrected with postponed type annotations before the successful run.

**Verified — repeat command, invented cases only:**

```sh
python3 -B -m unittest discover -s pilot/loop -p 'test_*INVENTED.py' -v
```

**Unverified:** real-file compatibility, approved incident deduplication, an online control sampler, production quarantine/audit exports, eligibility-calendar generation and any real utility result. These checks establish draft bookkeeping behaviour only.

## 8. Decisions needed before a real evaluation

**My inference — human/utility approval checklist:** confirm first-report meaning and precision; define pre-existing/deduplication rules; approve the seven-day horizon and minimum per-record exposure; choose dates and follow-up cutoff; approve reading/operating exclusions; select the statistical interpretation and minimum usable comparison patterns; agree control sampling and inspection effort; and set a feasible monthly investigation budget.

**My inference:** the provisional 50% simulation target is not automatically a utility requirement. No real-data pass/fail bar is approved here. Approval and authorised access are required before applying this draft to real event rows; independent preparation items can continue meanwhile.
