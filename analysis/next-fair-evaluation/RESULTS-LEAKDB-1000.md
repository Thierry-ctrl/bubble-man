# LeakDB Hanoi 1,000-scenario set — results of the single held-out test (10 Oct 2026)

Protocol: `PROTOCOL-LEAKDB-1000.md`, frozen at commit bf45959, with correction 1 (file format)
at commit 0d718f3, made before any warning or leak record existed.

**This is a fresh simulation test on the same generator family, not validation on real
networks.** The locked 490-scenario result (`RESULTS-LEAKDB.md`, FAIL) and the failed 2019
L-Town result are unchanged.

## Verdict: **improved, but below the practical target**

On 1,000 new simulations of the Hanoi network, the adaptive threshold cut warnings without a
newly eligible leak by three-quarters. It lost about 2 percentage points of sudden-leak
detection. Its yield, 47.2%, is below the provisional 50% target. So this is not a pass.

| Criterion (experimental decision bars, not utility requirements) | Result | Met? |
|---|---|---|
| G1 — at least 20 eligible sudden leaks | 473 | yes |
| G2 — sudden leaks beyond chance (adaptive) | 419 found; best of 47 week-shifts 20; p = 0.021 (the floor) | yes |
| G3 — detection no more than 5 points below frozen | 88.6% vs 90.5% (−1.9 points) | yes |
| G4 — at least 50% fewer warnings without a new leak | 877 vs 3,475 (−75%) | yes |
| G5 — yield of at least 50% (provisional practical target) | **47.2%** | **no** |

## Both methods — every warning counted as an investigation

1,000 scenarios, all assessable. The leak records hold 1,022 leaks in 763 scenarios: 506
sudden and 516 gradual. 2 records never flow and are not scored.

| | Frozen (comparator) | Adaptive (primary) |
|---|---|---|
| **Warnings (investigations)** | **4,286** | **1,660** |
| Credited (a newly eligible leak within 7 days) | 811 | 783 |
| **Yield** | **18.9%** | **47.2%** |
| Warnings without a newly eligible leak | 3,475 | 877 |
| — **no leak flowing** (false alerts) | 1,825 | 292 |
| — **during an older leak** | 1,650 | 585 |
| Leak-free exposure (hours, summed over scenarios) | 6,563,212 | 6,563,212 |
| **Sudden leaks** found / eligible | 428 / 473 (90.5%) | 419 / 473 (88.6%) |
| Median delay, sudden | 13.0 h | 13.5 h |
| **Gradual leaks** associated / eligible (reported, not judged) | 383 / 480 (79.8%) | 364 / 480 (75.8%) |
| Median delay, gradual | 22.0 h | 21.0 h |
| Week-shift test, sudden: real vs best (median) of 47 shifts | 428 vs 40 (28) | 419 vs 20 (9) |

The detailed outcomes of warnings during an older leak:

| Outcome | Frozen | Adaptive |
|---|---|---|
| `unattributable` | 1,638 | 573 |
| `coincides_with_excluded_leak` | 11 | 11 |
| `retrospective_association` | 1 | 1 |

These warnings coincided in time with a leak that had started more than 7 days earlier. That
is a temporal association only: it shows neither that the leak caused the warning nor that
anyone already knew about the leak. These warnings are reported separately and not assumed to
be wasted. *(wording corrected 11 Oct 2026; see `CORRECTION-NOTE-2026-10-11.md`)*

## Across scenarios

| Per scenario | Frozen | Adaptive |
|---|---|---|
| Warnings: median / 75th / 90th percentile / maximum | 2 / 6 / 11 / 31 | 1 / 3 / 4 / 9 |
| No-leak warnings: median / 75th / 90th percentile / maximum | 0 / 2 / 6 / 24 | 0 / 0 / 1 / 5 |
| Scenarios with ≥ 5 no-leak warnings | 147 | 1 |
| Scenarios with an eligible sudden leak | 414 | 414 |
| — every sudden leak found | 369 | 360 |
| — none found | 36 | 41 |

## Leaks found by one method but not the other

**Sudden leaks:** 15 found only by frozen, 6 only by adaptive. **Gradual leaks:** 29 found
only by frozen, 10 only by adaptive. The list is in `leakdb1000/run/step6-results.json`.

- **Found by frozen only (44).**
  - In 37, the adaptive threshold at onset was above the leak's largest step in its first
    8 nights. Most were small leaks: 23 never exceeded 1.5× the frozen threshold.
  - A few were large leaks behind a threshold raised by an earlier, noisy leak, up to about
    2,100 m³/h.
  - In the other 7, the adaptive threshold was below the leak's largest step. Threshold
    height alone does not explain these misses; the timing of the crossing, spacing or
    arming must have differed. Not traced further.
- **Found by adaptive only (16).** In 7 of these, the frozen January threshold had been
  inflated by a leak already flowing early (above 1,000 m³/h). The adaptive threshold
  recovered once that period left its 8-week window.

## Did the development findings recur? (after labels; reported, not judged)

| Finding from the 500-scenario development set | Here |
|---|---|
| Last leak flow precedes the dataset's final timestamp | 100% of flowing leaks (development 100%) |
| Gradual leaks with a night-to-night change above half their peak night flow at least once a week | 98.2% (development 97.9%) |
| Gradual leaks with night-window leak flow at exactly zero, median share of active nights | 31% (development 31%) |
| Frozen no-leak warnings in February, June or July (exact calendar date; nominal calendar here) | 88.7% (development 89.6%) |
| …and on the weekday positions that dominated (index mod 7 = 5 or 6) | 77.4% (development 77%) |

**Early leaks:** 65 scenarios had a leak before day 29. Without them: G3 88.9% vs 91.3%, G4
836 vs 3,344, yield 47.6%. The verdict is the same.

## Run record, including the defect

1. Protocol, code and invented-case tests frozen at **bf45959** (31/31 and 11/11).
2. Archive re-verified: size and md5. All 1,000 inlet files extracted
   (**34df57d**). Nothing else.
3. **Defect.** The first warning run stopped on its first file and wrote nothing. The
   1,000-scenario files carry `Index` 1–17,520 instead of timestamps. The original output
   is kept in `leakdb1000/run/step4-attempt1-output.txt`.
   - The fix places step *n* at a nominal 30-minute grid, which changes no rule.
   - It was tested (4/4; pipeline 12/12), documented as protocol §10 and committed
     (**0d718f3**) before re-running.
4. Both warning lists committed before any leak record (**0d23e7c**).
5. Leak records extracted and committed (**a779327**). All 1,022 use the Index format, and
   all positions agree with the inlet grid.
6. Scored once with the prospective timing rule, both methods and both chance comparisons.
   No reruns.

## What this establishes, and what it does not

- **Establishes, on fresh LeakDB simulations:** the development diagnosis was not specific
  to the 500 scenarios it came from.
  - Most no-leak warnings came from the January threshold falling behind a seasonal year.
  - A threshold that follows the last eight weeks removes most of them, and holds detection
    of sudden leaks within 2 points.
  - The improvement held on data the rule was not chosen on: development yield 46.6% under
    the same timing rule, here 47.2%.
- **Does not establish:**
  - that the 50% practical target is met;
  - that the method works on real networks. Real leaks don't follow this simulator's
    fluctuating leak flows, and real demand isn't a smooth seasonal curve;
  - a utility false-alert rate;
  - leak location;
  - anything about other night-flow methods.

  The network, generator and modelling choices are the same as in development.
- **What would move this forward:** real data — one zone's inlet flow for a year, with
  repair records — or a second signal that tells demand apart from leakage at night.
  Further rule changes tuned on LeakDB would mostly fit this simulator.

## Files (`leakdb1000/run/`)

`manifest-inlet.csv`, `step3-extract.json` · `step4-attempt1-output.txt` ·
`warnings-both-rules.csv`, `scenarios-assessability.csv`, `step4-warnings.json` ·
`leaks-table.csv`, `step5-leaks.json` · `step6-results.json`, `per-scenario-frozen.csv`,
`per-scenario-adaptive.csv`, `warnings-scored-frozen.csv`, `warnings-scored-adaptive.csv`,
`shifts-frozen.csv`, `shifts-adaptive.csv`, `step6-stdout.txt`.
