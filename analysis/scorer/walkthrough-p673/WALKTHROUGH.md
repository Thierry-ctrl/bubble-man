# One leak, traced end to end: p673

Experiment A, settings unchanged. Signal: main-zone outflow `p227 + p235 − PUMP_1`,
hourly. Baseline: median by hour and day-type over 8–14 January. Threshold 10 m³/h for
6 consecutive hours, then 1 hour before a warning can be issued.

Every number below was read from the saved results and re-derived from the raw readings.
Nothing was tuned; no new detector was built; raw data and previous results untouched.

## 1. When the leak began

| | |
|---|---|
| Configured onset | **5 March 2018, 15:45** |
| First positive flow | **5 March 2018, 15:45** — identical, 0 hours silent (it is an abrupt leak) |
| Size once running | **28.40 m³/h** |
| Leak ends | 23 March 2018, 10:25 |

## 2–3. What the meter showed, against what the baseline expected

At the onset hour the difference jumped immediately:

| Hour | Observed | Expected | Difference |
|---|---|---|---|
| 5 Mar 14:00 | 197.58 | 170.16 | +27.42 |
| 5 Mar 15:00 | 191.15 | 158.98 | +32.17 |
| **5 Mar 16:00** | **211.64** | **159.31** | **+52.33** |
| 5 Mar 17:00 | 212.93 | 163.48 | +49.45 |

The step of roughly +20 m³/h between 15:00 and 16:00 matches the known 28.4 m³/h leak.
**The leak was never invisible.**

## 4–5. When the difference crossed the threshold — and the catch

It had already crossed, long before. The difference first went above 10 m³/h at
**4 March 05:00** (+18.46) and then stayed above it **continuously for 122 hours**,
through the leak onset and on to 9 March 06:00. Verified: all 122 hours above threshold,
none below.

Across 1–9 March, **184 of 199 hours (92%)** were above the threshold.

So the six-hour persistence requirement was satisfied repeatedly — but by a run that
**began 34 hours and 45 minutes before p673 existed**. That run is alert event **#26**
in the saved events file. The scorer refuses to credit it, because an alert already
under way cannot have been caused by a leak that had not yet started.

The run finally broke at **9 March 07:00**, when the difference dipped to **+6.97**, a
single hour below threshold. A fresh run began at **9 March 08:00** (+24.73).

## 6. The earliest a warning could be issued

| Step | Time |
|---|---|
| Run #27 starts (first hour above threshold) | 9 Mar **08:00** |
| Sixth consecutive hour — rule satisfied | 9 Mar **13:00** |
| Hourly average complete, warning issuable | 9 Mar **14:00** |

Delay from onset: 5 Mar 15:45 → 9 Mar 14:00 = **94.25 hours**.
This matches `delay_hours_from_first_flow` in `main-zone-leaks-A_reference_inherited.csv`
exactly.

**Start of an unusual run ≠ when a warning is available.** Run #27 began at 08:00, but
nothing could be reported until 14:00 — five hours to satisfy persistence, one more for
the hour to finish.

## 7. How the scorer classified it

Event #27: `credited`, matched to `p673`, confidence `single_candidate`.

Three leaks were running when it began — `p461`, `p427`, `p673` — but only `p673` was
within the seven-day deadline. `p461` started 23 January and `p427` 13 February, both far
outside. One candidate, so the match is not ambiguous.

## Earlier unusual periods that were not credited

| Event | Run started | Ran for | Outcome | Why |
|---|---|---|---|---|
| #23 | 1 Mar 05:00 | 25 h | `unattributable` | Only `p461` and `p427` running, both past their deadline |
| #24 | 2 Mar 10:00 | 20 h | `unattributable` | Same |
| #25 | 3 Mar 11:00 | 13 h | `unattributable` | Same |
| **#26** | **4 Mar 05:00** | **122 h** | `unattributable` | **Began before p673 started, so cannot be credited to it** |
| #27 | 9 Mar 08:00 | 359 h | `credited` → p673 | Began after onset, inside the deadline |

Event #26 is the whole story. It covered the leak onset and the following three and a
half days. Had it begun a few hours later, the delay would have been near zero.

## In plain language

**What this shows.** The detector saw this leak immediately — flow jumped about 20 m³/h
within the hour. But it had been crying wolf since the day before, for reasons unrelated
to p673, and our rules will not let a warning that was already running take credit for a
leak that started later. The 94-hour "delay" measures when a *fresh, creditable* warning
appeared, not when the leak became visible.

**What caused the delay.** Not weak signal. An alert already in progress. The detector
was above its threshold 92% of the time that week, so a new run could only begin after
the signal happened to dip below the threshold for one hour on 9 March. The delay was
set by that accident of timing, not by anything about the leak.

**Why a timing match still proves nothing.** Our signal is one number for a whole zone.
It names no pipe. Three leaks were running when the warning fired; the scorer picked
`p673` because the others were outside the seven-day window — a bookkeeping rule, not
evidence. A crew sent out on this warning would know only that the zone was using more
water than expected. And when a detector is above threshold 92% of the time, it will
coincide with almost any event, which is exactly why randomly-timed warnings score as
well as real ones.

## Files

| File | Contents |
|---|---|
| `p673-walkthrough.png` | The chart |
| `plot_walkthrough.py` | Script that builds it (read-only) |
| `hourly-series.csv` | Observed, expected and difference, 25 Feb – 15 Mar |
