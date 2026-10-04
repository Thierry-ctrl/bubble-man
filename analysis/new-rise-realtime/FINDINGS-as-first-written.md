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
hours when a level alert was open, 300 runs:

| | Real rule | Random placement |
|---|---|---|
| All leaks credited | 12 | median 11, 95th 11.0, max 12 |
| **Abrupt credited** | **6** | **6 in every one of 300 runs** |
| Median delay | 15.17 h | median 24.61 h (5th–95th: 14.9–35.2) |

**On abrupt leaks — the class the rule was built for — it is exactly as good as placing
warnings at random, and not once in 300 runs did chance do worse.** The mechanism is
simple arithmetic: 184 warnings across 6,589 open-alert hours is one every 35.8 hours,
and each leak has a 168-hour deadline window. That is about **4.7 chances per leak by
density alone**.

The only hint of genuine signal is in timing, not selection: the real median delay of
15.17 h sits near the 5th percentile of the random distribution. Faster than chance
usually manages, but inside its range.

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

## Files

| File | Contents |
|---|---|
| `RULE-FROZEN.md` | The rule, committed before scoring |
| `run_realtime.py` | Calibration, warning generation, scoring, random comparison |
| `plot_realtime.py` | Builds the chart |
| `realtime-results.json` | Threshold, exposure, per-leak outcomes, random distributions |
| `realtime-leaks.csv`, `realtime-events.csv`, `realtime-warnings.csv` | Traceable detail |
| `random-distributions.json` | All 300 random runs |
| `realtime-vs-random.png` | The chart |
