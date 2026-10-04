# Does the new-rise observation survive as a real-time rule? — 3 October 2026

**2018 DEVELOPMENT TEST.** These six leaks were examined before the rule was written, so
nothing here is a performance claim. The rule was frozen in `RULE-FROZEN.md` and
committed **before** this scoring ran (git `72955bc`). The scorer was imported unchanged.
2019 untouched. Previous results preserved.

## Decision: drop it as a standalone real-time trigger

By the criteria declared before scoring, two of three fail — including the one that
matters most.

| Pre-declared criterion | Result |
|---|---|
| Credits ≥2 of the three leaks Experiment A missed | **PASS** — all three (p538, p866, p158) |
| Beats the random comparison on the same hours | **FAIL** — see below |
| Under ~2 extra warnings per week of open alert | **FAIL** — 4.69 per week |

## Could a threshold be chosen without the six outcomes? Yes — and it mattered

The reserved quiet window (15–23 January) **could not be used**: a level alert is open for
**0 of its 186 hours**, so it contains no example of the regime this rule operates in.
That also means the rule has **no leak-free exposure anywhere in 2018** — its false-alert
count of 0 is vacuous, true by construction rather than by performance.

Calibration therefore used **2–14 January** (307 hourly values, main-zone leak-free,
entirely before the evaluation window):

    median 0.41 + 3 × (IQR/1.349 = 2.90)  →  threshold 9.10 m³/h

**That is far below the values the retrospective study saw at the six onsets (16.40 to
36.69).** The quiet period's spread is small, so a conventional 3-sigma cut is permissive
and the rule fires 184 times. Choosing a stricter cut is a legitimate question, but it
**cannot be answered on these six leaks** without tuning on the outcomes we are testing.

## What the rule did

| | New-rise rule | Experiment A |
|---|---|---|
| Warnings issued | **184** | 129 |
| Leaks credited | **12 / 12** | 9 / 12 |
| Abrupt credited | **6 / 6** | 3 / 6 |
| Gradual credited | 6 / 6 | 6 / 6 |
| Median delay | **15.17 h** | 55.75 h |
| Of the three A missed | **all three credited** | — |
| Unattributable / repeats | 139 / 33 | 105 / 14 |

Read alone, that is a transformation: every leak caught, the three misses recovered, the
delay cut by three quarters.

## Why it is not a transformation

Randomly-placed warnings — same count, same 24-hour spacing, placed only in the 6,589
hours when a level alert was open. **All figures in this table come from the 300 saved
runs in `random-distributions.json`, summarised by `summarise_random.py` into
`random-summary-300.json`** — the same runs the chart plots.

| | Real rule | Random placement (300 runs) |
|---|---|---|
| All leaks credited | 12 | median 11, 95th 11.0, max 12; 4.0% of runs reach 12 |
| **Abrupt credited** | **6** | **6 in every one of 300 runs** |
| Median delay | 15.17 h | median **26.17 h** (5th–95th: **15.81–39.62**); **4.3%** of runs as fast or faster |

*Corrected in review — see "Review notes" below. The delay row originally cited 24.61 h
(14.9–35.2) from an unsaved check.*

**On abrupt leaks — the class the rule was built for — it is exactly as good as placing
warnings at random, and not once in 300 runs did chance do worse.** The mechanism is
simple arithmetic: 184 warnings across 6,589 open-alert hours is one every 35.8 hours,
and each leak has a 168-hour deadline window. That is about **4.7 chances per leak by
density alone**.

The only hint of genuine signal is in timing, not selection: the real median delay of
15.17 h is matched or beaten by **4.3%** of random runs, just below the random 5th
percentile of 15.81 h. That is marginal evidence that the rule fires *sooner* than chance,
from one comparison among several made on data already studied — not strong enough to
rest on, and it does not change which leaks are credited.

## What happened to the retrospective finding

It was real but could not carry the weight placed on it. The earlier study took the
**maximum** step in a 12-hour window **anchored on each leak's known start time**. That
is information a real-time rule does not have. Asked to find the same rises without
knowing where to look, and with a threshold that could not be tuned to them, the rule has
to fire often enough that chance reproduces the result.

## Limits of what any of this can show

- **Overlapping leaks.** Other leaks were running through every window. The step cannot
  be attributed to the new leak rather than to a change in one already running.
- **No pipe is identified.** The signal is one number for a whole zone. A timing match is
  an association, never evidence that a particular pipe leaked.
- **No measurable false-alert rate.** The rule fires only while a level alert is open;
  2018's only leak-free hours have no open alert. Its cost can be described as a warning
  rate, not as a false-alert rate.
- **Six abrupt events**, already studied. Far too few to fit or select anything on.

## What would change the answer

A stricter threshold is the obvious question, and it is genuinely open — but it must not
be chosen on these leaks. It would need the sealed 2019 data (19 leaks, of which several
abrupt) or a different network. Until then, "a higher cut might work" is a hypothesis,
not a finding.

The more useful lesson is structural: **any rule that must fire several times per leak
window will be matched by chance under this scorer.** Getting past that needs evidence
that narrows *where*, not just *when* — which means pressure sensors, not a better
threshold on a single flow signal.

## Review notes (4 October 2026)

Added after review. The frozen rule, the scorer and `realtime-results.json` are
**unchanged**. The original text is preserved in `FINDINGS-as-first-written.md`.

### 1. Which random runs each number comes from

Three sets of random runs exist, and the first version of this report mixed them:

| Source | Runs | Seed | Saved? | Records delay? |
|---|---|---|---|---|
| `run_realtime.py` → `realtime-results.json` | 200 | 20261003 | yes | **no** |
| `plot_realtime.py` → `random-distributions.json` (the chart) | 300 | 20261003 | yes | yes |
| an ad hoc check during writing | 100 | 7 | **no** | yes |

The credited-leak figures agree between the 200 and 300 runs (median 11, 95th 11,
max 12; abrupt 6/6 every time). **The delay figures did not come from either saved set** —
they came from the unsaved 100-run check, so the report's delay row contradicted its own
chart. The table above now cites the 300 saved runs throughout. Consequence: the real
delay moves from "inside the random range" to "just below its 5th percentile". The
decision is unchanged — it rests on criteria 2 and 3, which fail either way.

`realtime-results.json` still reports its own 200-run summary; it is labelled by its run
count and is not cited in the table.

### 2. Did calibrating on the baseline's own January week make the threshold too permissive?

The concern is legitimate: the baseline profile is built from 8–14 January, and the
threshold was calibrated on 2–14 January, so half the calibration hours are in-sample.
In-sample residuals *are* smaller — the level residual's interquartile range is 5.08 m³/h
on 8–14 January against 6.54 on 2–7 January.

But the step measure subtracts one window of residuals from another, and that shrinkage
largely cancels:

| Calibration slice | Hours | Robust sigma | Threshold it would give |
|---|---|---|---|
| As frozen, 2–14 Jan | 307 | 2.90 | **9.10** |
| Out-of-sample only, 2–7 Jan | 139 | 2.81 | 8.71 |
| In-sample only, 8–14 Jan | 168 | 2.98 | 9.38 |

The out-of-sample threshold is *lower*, not higher. **What can be established: the overlap
did not make the threshold materially more permissive** — the three candidates differ by
under 0.7 m³/h, against case values of 16–37. The threshold was not revised.

### 3. What actually made it permissive: season

A diagnostic on the step's month-by-month spread, computed on the evaluation window and
**not used to change anything**:

| Month | Step sigma | Level alert open |
|---|---|---|
| Jan | 3.25 | 0% |
| Mar | 7.28 | 92% |
| Jul | **13.92** | 86% |
| Dec | 5.29 | 83% |

Ordinary variation in the step roughly **quadruples** between January and July; across all
open-alert hours its sigma is 7.11 against the calibration's 2.90. The only leak-free
data in 2018 falls in its quietest month, so any threshold calibrated there will be
scaled to January and fire far more often in summer. This is a structural limit of the
dataset for this approach, not a calibration error that a different January slice fixes.

## Files

| File | Contents |
|---|---|
| `RULE-FROZEN.md` | The rule, committed before scoring |
| `run_realtime.py` | Calibration, warning generation, scoring, random comparison |
| `plot_realtime.py` | Builds the chart |
| `realtime-results.json` | Threshold, exposure, per-leak outcomes, random distributions |
| `realtime-leaks.csv`, `realtime-events.csv`, `realtime-warnings.csv` | Traceable detail |
| `random-distributions.json` | All 300 random runs (the chart's data) |
| `summarise_random.py`, `random-summary-300.json` | Reproducible summary cited by the tables |
| `FINDINGS-as-first-written.md` | This report before review corrections |
| `realtime-vs-random.png` | The chart |
