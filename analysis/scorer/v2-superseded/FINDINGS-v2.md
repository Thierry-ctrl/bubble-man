# Main-zone evaluation, frozen rules — 29 September 2026

Simulated L-Town 2018 data. Development experiment. **Not evidence that anything works
in Rwanda, or anywhere.** 2019 untouched. Earlier results preserved in `v1-superseded/`.

## Pre-flight checks, before any scoring

**Do flow and level timestamps align?** Yes — identical 5-minute index, verified by
assertion. The paper states pressure sensors report a 5-minute average but says only
that flow and level "transmit every 5 minutes". Their averaging semantics are therefore
**assumed**, not documented.

**Does the forward storage difference use future information?** I tested which pairing
is physically right, using the fact that a tank can only fall while its pump is off
(39% of intervals):

| Pairing | Level rising while pump off |
|---|---|
| Forward, `L(t+1) − L(t)` | **0.16%** |
| Backward, `L(t) − L(t−1)` | 0.49% |

The forward pairing is the physically correct one: the flow reported at `t` applies over
`[t, t+5min]`. So it is **not** future leakage — it is a quantity describing an interval
that becomes knowable at the end of that interval.

**When does an hourly result become available?** The hourly value covering `[H, H+1)`
needs the level reading at `H+1:00`, so nothing is known before `H+1:00`. That is exactly
`reporting_lag_hours = 1.0`, and all delays are measured from it.

**Why were Area C outflows negative?** Not an accounting error — a **level-resolution
artefact**. The tank level is recorded to only **0.01 m**, giving 196 distinct values all
year. One step is:

| Averaging interval | One 0.01 m step as a rate |
|---|---|
| 5 minutes | **24.13 m³/h** — about 90% of Area C's mean outflow |
| 1 hour | 2.01 m³/h |
| 3 hours | 0.67 m³/h |

Every negative 5-minute value is an exact integer multiple of that step, and the worst
(−48.25 m³/h) is precisely two steps. Negatives fall from 4.10% to **0.02%** hourly, with
the worst at −0.13 m³/h. So hourly averaging is justified by the mechanism, not assumed.

**On the balance closing exactly.** `main + Area C + storage = inflow` is an algebraic
identity of how the three were defined. It confirms no arithmetic slip and **nothing
else**. It is not independent physical validation.

## The two experiments

Signal for both: **`p227 + p235 − PUMP_1`**, hourly, m³/h. Window 15 Jan – 31 Dec 2018.
12 main-zone leaks. Persistence 6 hours in both, so only the threshold and baseline week
differ. 15–23 January was used for neither baseline nor threshold.

| | A — reference | B — calibrated |
|---|---|---|
| Baseline profile week | 8–14 Jan | 1–7 Jan |
| Threshold | **10 m³/h**, inherited | **22.80 m³/h**, 99th percentile of the 8–14 Jan difference |
| Alert events | 129 | 199 |
| Leaks associated | **9 / 12** | **9 / 12** |
| — abrupt | 3 / 6 | 5 / 6 |
| — gradual | 6 / 6 | 4 / 6 |
| Median delay | 50.4 h | 28.9 h |
| Unattributable | 0 | 43 |
| Repeats (score zero) | 119 | 147 |
| False alerts, whole window | 1 | 0 |
| **False alerts in quiet window** | **1 in 215 h (8.96 days)** | **0 in 215 h (8.96 days)** |
| Randomly-timed warnings credit | 10.0 (95th: 12.0) | 11.0 (95th: 12.0) |

## What this shows

**Neither experiment beats chance.** Both associate 9 of 12 leaks; randomly-timed
warnings at the same rate and duration associate 10 and 11 respectively. The real result
is *below the random median* in both cases. There is no evidence of detection skill here.

**Calibration changed the profile of errors, not the total.** B catches more abrupt
leaks (5/6 vs 3/6) and fewer gradual ones (4/6 vs 6/6), and halves the delay. Same total.

**B raised the threshold yet fired more often.** 22.80 m³/h produced 199 alerts against
10 m³/h's 129. The cause is the baseline week: 1–7 January contains New Year's Day, so
the learned "normal" is depressed and every later difference is inflated. A documented
calibration procedure does not protect against an unrepresentative training week.

**The false-alert rate is not measurable.** 0–1 events in 215 hours. By the rule of
three, 0 events in 8.96 days puts only a 95% upper bound of about **0.33 events per
day** — which excludes almost nothing useful. Reported as a count with its exposure,
never as a rate.

**Area C: unavailable.** Zero leak-free hours between 15 Jan and 31 Dec, because `p257`
runs throughout. No false-alert performance can be stated for Area C in this window, and
none is.

## Language

Every result above is a **timing association**: a warning arrived while a leak was
running, soon after it began. Our signal names no pipe. None of this is proof that a
particular leak caused a particular warning.

## Limitations

- Simulated data; the organisers deliberately excluded sensor faults and time delays.
- Tank level quantised to 0.01 m, which sets a floor on Area C accuracy.
- Flow averaging semantics assumed, not documented.
- One threshold rule of one shape. A different detector could behave differently; this
  says nothing about flow as an input in general.
- Development-period numbers. Not performance.
