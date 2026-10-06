# Night-flow step check — frozen rule

Committed before the full-year noise check and before any leak was scored. 2018 only;
2019 sealed; the simulator's generation model is not read. **Scope: detecting an
additional new leak only.** This rule cannot measure losses present for months — the input
audit showed the main zone has no customer meters.

## Signal

- `main_out = p227 + p235 − PUMP_1`, hourly means of the 5-minute readings (m³/h).
- Expected value: the frozen day-type baseline (`analysis/weekend-baseline/BASELINE-FROZEN.md`):
  median per hour over 1–14 January, day types Sun–Thu / Fri / Sat, assigned by the
  calendar date of the reading.
- **Night value for date D** = mean residual (`main_out − expected`) over the hours
  labelled 02:00 and 03:00 on date D, i.e. the readings from 02:00 to 03:55.

## Measure

    step(D) = mean(night D, night D−1) − mean(nights D−2 … D−8)

Two latest nights against the seven before them. If any of the nine nights is missing, no
step is computed for D. (2018 has no missing readings; the rule is stated anyway.)

## Timing

- The last reading used is 03:55 on date D. Under the timing assumption used throughout
  this project (the reading at `t` describes `[t, t+5 min]`, supported by a consistency
  check but not proven), it is complete at **04:00**.
- A warning for night D is therefore **issued at 04:00 on date D**. In the scorer it is
  entered as the hour labelled 03:00, which the unchanged one-hour reporting lag turns
  into an issue time of 04:00.
- *Correction to the audit:* the audit said "05:00". That double-counted the hour. 04:00 is
  the earliest moment every reading is available, and no earlier time is used.

## Warning rule

On each night D from **15 January to 31 December 2018**, issue a warning if all three hold:

1. `step(D) ≥ 10.0 m³/h` — the operational size declared in the audit, not tuned;
2. the rule is **armed**: it starts armed, is disarmed by a warning, and re-arms on the
   first later night whose step is below 10.0;
3. at least **7 days** (168 hours) have passed since the previous warning's issue time.

Edge cases:
- The seven "before" nights for the first evaluation nights (15–23 January) include
  training nights from 1–14 January. Those readings existed at the time, so they are used;
  their residuals are in-sample and will be close to zero.
- The rule does not depend on whether a level alert is open. It is a standalone rule.
- The warning series is not altered after it is generated.

## Scoring

The existing scorer, **unchanged**: `score(warnings, persistence=1, leaks, Rules(gap 0,
reporting lag 1 h, deadline 168 h))`. Leaks are the 12 labelled main-zone leaks, active
from first positive flow, as in `run_main_zone.py`. Evaluation window 15 Jan 00:00 –
31 Dec 23:00. Abrupt and gradual leaks reported separately; gradual leaks are outside this
method's purpose and are expected to be missed.

Reported: per-leak outcome and delay, every warning's outcome category, unmatched warnings,
and warnings per calendar month. The one-per-week cap is guaranteed by rule 3 and is
**not** evidence that the workload is acceptable.

## Comparison with shifted warnings

- **Domain:** the 350 nights from 15 January (Monday) to 30 December (Sunday) — exactly
  50 weeks. The window holds 351 nights; the 31 December night is left out because it
  cannot be shifted by whole weeks without leaving the domain.
- **Shifts:** the real warning nights within that domain, moved forward by k whole weeks,
  wrapping circularly, for **k = 1 … 49**. That is **49 distinct shifts**; k = 50 returns
  the original. Each keeps the count, the day of week, the 04:00 issue time, and every
  gap between warnings except the one across the wrap point.
- The real pattern is scored on the **same 350-night domain** so real and shifted are
  compared like with like; the full-window real result is reported separately.
- The 49 shifts are **not** independent trials: they are one pattern moved through the year.
  The one-sided p-value is `(1 + number of shifts crediting at least as many abrupt
  leaks) / 50`, so the smallest possible value is **0.02**.
- Boundary limits reported: whether any wrapped gap falls below 7 days, and that shifting
  moves warnings between seasons.

## Pre-declared judgement

- **Noise stop.** If the standard deviation of night-to-night change in the residual over
  the full window exceeds **4.5 m³/h** — twice January's 2.25 — a 10 m³/h threshold is no
  longer clearly above ordinary variation. This is reported first, before scoring.
- **Evidence beyond chance.** The real pattern credits more abrupt leaks than at least
  **47 of the 49 shifts** (≥ 95%).
- **Workload.** Reported as warnings per month and unmatched warnings per month. No
  acceptability threshold is claimed.
- **Worth a locked 2019 evaluation?** Only if there is evidence beyond chance. Even then,
  2019 stays sealed until the user explicitly approves opening it.
