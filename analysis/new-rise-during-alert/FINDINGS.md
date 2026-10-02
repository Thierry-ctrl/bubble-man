# Can we see a new rise while a warning is already open? — 2 October 2026

Retrospective test on simulated L-Town 2018. The scorer and its results are unchanged;
2019 was not read. No rule was added to the detector and no threshold was selected.

## The question

Leak p673 began while a level alert had already been open for 34 hours, so the detector
could not mark a new event and the warning arrived 94 hours late. Would a simple measure
of **change** have seen it?

## The measure, declared before looking

    step(t) = mean(difference over hours t-5 .. t) - mean(difference over hours t-29 .. t-6)

A recent 6-hour window against the 24 hours before it, on the same observed-minus-expected
difference Experiment A already uses. Strictly backward-looking: every hour is complete by
`t`, so the value exists at `t+1`. Leak labels were used **only** to choose cases and to
exclude control hours — never as input.

## Samples

| | Count |
|---|---|
| Hours scored (15 Jan – 31 Dec) | 8,395 |
| Hours with a level alert already open | **6,589 (78.5%)** |
| Control hours: alert open, no main-zone onset within ±72 h | 5,438 |
| Control 12-hour blocks (for like-for-like comparison) | 4,377 |
| Abrupt main-zone leaks examined | 6 |
| …of which had an alert **already open** at onset | **6 of 6** |

That last line is the point: every abrupt leak in 2018 began while the detector was
already alerting. This is not a corner case — it is the normal situation.

## Results

| Leak | Max step in 12 h | Peak at | Percentile among control blocks | Level rule said |
|---|---|---|---|---|
| p538 | **36.69** | +10.4 h | 97.6th | **missed** |
| p673 | 31.92 | +5.2 h | 92.9th | credited (94 h late) |
| p866 | 30.28 | +9.9 h | 92.1th | **missed** |
| p183 | 23.42 | +9.4 h | 90.9th | credited |
| p158 | 16.57 | +2.4 h | 89.6th | **missed** |
| p369 | 16.40 | +2.9 h | 89.3th | credited |

**All six land in the top 11% of comparable control blocks — including the three the
level rule missed entirely.** If each case were a random draw from the control
distribution, all six exceeding the 75th percentile (11.84 m³/h) would happen by chance
about 2 in 10,000 times. Four of the six also exceed the 90th percentile.

This is the first result in this project that is clearly better than chance.

### A methodological correction, made before reading anything into it

The first version compared a 12-hour **maximum** for the cases against **single** control
hours, which flattered the measure by 5–8 percentile points (reporting 95.9–99.6th
instead of 89.3–97.6th). The table above is the like-for-like comparison. Both figures
are kept in `new-rise-results.json`.

## How often it would react with no new leak

| Cut | Abrupt leaks reached | Control episodes | Per week of open alert |
|---|---|---|---|
| 16.40 | **6 / 6** | 41 | **1.27** |
| 20.00 | 4 / 6 | 39 | 1.20 |
| 25.00 | 3 / 6 | 39 | 1.20 |
| 30.00 | 3 / 6 | 36 | 1.11 |

Reported, **not** selected. The shape matters more than any row: raising the cut from
16.4 to 30 loses half the leaks and removes only five control episodes. The control
distribution has a heavy tail — its 95th percentile (34.57) exceeds four of the six
cases — so the two populations overlap badly at the top.

## It does nothing for gradual leaks

Max step in the 12 hours after each gradual onset: p461 2.29, p232 1.96, p427 7.09,
p628 4.24, p654 9.25, p810 6.82 m³/h. Every one is below every abrupt case. A step
measure looks for a step; a leak that ramps over weeks does not make one. **This idea
addresses abrupt leaks only** — half the 2018 main-zone events.

## What stays uncertain

- **Overlapping leaks.** Other leaks were running throughout every case window — p461
  and p427 during p673, for instance. The step cannot be attributed to the new leak
  rather than to a change in one already running. A timing match is **not** proof that a
  particular pipe leaked.
- **"Control" does not mean nothing happened.** Those hours have no *labelled* leak
  onset. Real demand surges, pump and valve changes are unlabelled and will be in there.
  Some of the 41 control episodes may be genuine events we cannot see.
- **Six events.** Three of them separate well, three sit near the boundary. Six is too
  few to fit anything to.
- Simulated data; sensor faults and transmission delays excluded by the organisers.

## Does a "new change during an open alert" rule look promising?

**Promising enough to continue, not enough to adopt.** The honest summary: a measure
that cost two lines of arithmetic put all six abrupt leaks in the top 11% of comparable
quiet periods, and flagged three the level rule missed completely. That is a real signal
where previously there was none.

But at a cut that reaches all six it would also fire about **1.27 times a week** while an
alert is open, and the tail of ordinary variation overlaps most of the cases. As a
standalone trigger it would not be usable.

## Smallest sensible next step

**Check whether the step and the level rule disagree in a useful way on the three missed
leaks.** p538, p866 and p158 were never credited by Experiment A, yet all three produce a
clear step. Score the step measure through the existing event-level scorer — unchanged —
including the random-timing comparison, and see whether it credits those three leaks at a
false-alert cost the level rule cannot match.

That is one run of machinery that already exists. It needs no new model, no tuning, and
it would answer whether this is worth developing or should be dropped.

## Files

| File | Contents |
|---|---|
| `new_rise.py` | The test. Reproducible, offline. |
| `plot_new_rise.py` | Builds the chart. |
| `new-rise-results.json` | Method, sample counts, cases, control distributions, sweep. |
| `step-series.csv` | The step measure, alert-open flag and difference, hour by hour. |
| `new-rise.png` | The chart. |
