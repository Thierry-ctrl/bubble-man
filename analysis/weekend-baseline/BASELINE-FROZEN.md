# Replacement baseline — frozen before any rerun

**Exploratory.** These 2018 leaks have already been examined; nothing here is a performance
claim. 2019 is not read. Committed before `rerun_with_new_baseline.py` was run.

## The problem being repaired

Diagnosed from raw 2018 readings (`diagnose_sunday.py`, `sunday-diagnosis.json`):

- In L-Town, **Saturday is the unusual day, not Sunday.** Sunday's hourly flow tracks
  Monday–Friday closely; Saturday mornings run far lower (07:00 means across 2018:
  weekday 194.0, Sunday 198.0, Saturday 130.4 m³/h).
- The current baseline pools Saturday and Sunday into one "weekend" profile built from a
  single Saturday (13 Jan) and a single Sunday (14 Jan) — the median of two values, i.e.
  their average. It therefore **under-predicts every Sunday morning and over-predicts every
  Saturday**.
- The flow step at Sunday 11:00 compares Sunday morning (mean residual +65.1) with a window
  dominated by over-predicted Saturday (+29.8). **All 50 Sundays in the window exceed the
  9.10 m³/h step threshold**, against 17% of weekday 11:00s and 0% of Saturday 11:00s.
- **Not the pump.** At 07:00, main-zone outflow differs by 67.6 m³/h between Saturday and
  Sunday while pump flow differs by 1.6 m³/h; the main-zone signal already subtracts the
  pump.

## How the replacement was chosen — January readings only

On 15 January, only 1–14 January would have been available. Those 14 days contain **no
labelled main-zone leak** (the first, p461, produces flow from 23 January) and end before
the reserved 15–23 January window, which stays untouched. They hold two examples of every
day of the week.

For each day of the week, from those two weeks alone:

| | Mon | Tue | Wed | Thu | **Fri** | **Sat** | Sun |
|---|---|---|---|---|---|---|---|
| Repeatability — its two examples vs each other (RMS m³/h) | 3.6 | 3.2 | 3.6 | 3.6 | 3.0 | 2.1 | 3.5 |
| Distinctness — vs the median of all other days (RMS m³/h) | 3.2 | 3.5 | 2.9 | 3.5 | **16.4** | **25.6** | 3.6 |

**Rule:** a day of the week gets its own profile if its distinctness exceeds three times
the largest repeatability (3 × 3.6 = 10.8 m³/h); otherwise it is pooled. Friday and
Saturday exceed it; the other five do not. The gap is wide enough that any multiplier
between about 1 and 4.5 gives the same grouping.

The whole-year diagnosis is what revealed the problem. The **grouping itself is decided on
January readings alone** — no leak label, no evaluation-period reading, no score.

## The replacement, frozen

| | Old (Experiment A) | **New** |
|---|---|---|
| Training days | 8–14 January (7 days) | **1–14 January (14 days)** |
| Day types | Mon–Fri / Sat+Sun | **Sun–Thu / Fri / Sat** |
| Days behind each profile | weekday 5, weekend 2 | **Sun–Thu 10, Fri 2, Sat 2** |
| Statistic | median per hour | median per hour (unchanged) |
| Adapts over time? | no | **no** |

Applied identically to the main-zone flow signal (`p227 + p235 − PUMP_1`) and, for the
pressure study, to each pressure sensor. Using the same grouping for pressure is an
**assumption** — pressure variation is driven by demand — not separately tested.

Two things change at once: grouping, and the training span (needed to get two Fridays and
two Saturdays). The rerun does not separate their effects.

## Limitations, quantified

- **Friday and Saturday profiles rest on two days each.** Those two agree closely (RMS 3.0
  and 2.1 m³/h), so the shape is repeatable *in January* — but January is one season, and
  nothing in the training data says the shapes hold in summer.
- **Seasonal drift is not repaired.** The static January profile still sits below summer
  demand. Previously a level alert was open in 78% of hours; this repair is not expected to
  change that much.
- **New Year's Day** is included as an ordinary weekday; it sits 2.5 m³/h RMS from the
  weekday profile, within normal day-to-day variation.

## Why not an adaptive baseline

Tested with a synthetic, label-free check: a permanent +20 m³/h step injected into the real
series on 1 February, against a baseline that re-learns from the previous N weeks of the
same day type.

| Window | Step falls below half its size | Effectively absorbed |
|---|---|---|
| 2 weeks | 11 Feb (10 days) | 11 Feb |
| 4 weeks | 18 Feb (17 days) | 19 Feb |
| 8 weeks | 4 Mar (31 days) | 6 Mar |

Because it takes a median, an adaptive baseline erases a sustained change after roughly
half its window. **Any leak that lasts longer than that becomes "normal".** Rejected.

## What the rerun keeps unchanged

- Level-warning rule: difference > 10 m³/h for 6 hours. Scorer and matching rules.
- New-rise rule: step threshold **9.10 m³/h**, only while a level alert is open, re-arm
  below threshold, 24-hour minimum gap. The number is kept as frozen. (Re-applying its
  calibration formula to the new baseline is reported once as a sensitivity, not used.)
- Pressure study: episodes at step ≥ 9.10, measures S and C, labels, and the decision
  criterion (at least 5 of 6 abrupt cases above the 90th percentile on S or C).
- Random comparisons as before, plus a rotation by **whole weeks**, which keeps the
  day-of-week and hour-of-day pattern intact — the fairer test now that the weekly cycle
  is known to matter.

Both baselines run through identical code; the old one must reproduce the saved results
before any new number is trusted.

## Language

Periods with no labelled onset are called **"no labelled new leak"**, never "leak-free".
False alerts are reported as **counts with their exposure time**, never as a reliable rate.
