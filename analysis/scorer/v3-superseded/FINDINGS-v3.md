# Main-zone evaluation, after reviewer corrections — 29 September 2026

Supersedes FINDINGS-v2.md (kept in `v2-superseded/`). Simulated L-Town 2018 data.
Development experiment. **Not evidence of anything working in Rwanda.** 2019 untouched.

## What the reviewer found, and what it cost

**The defect is real. It changed no number here.** The scorer credited an alert whose
issue time fell after the matched leak had already ended. I checked our results: **zero**
such cases in either experiment, and zero alerts issuable past the window end. The bug
was latent, not active.

It is reachable, though. Constructed case: leak runs 09:00–12:00, the unusual run begins
10:00, persistence 6 makes the alert issuable at 16:00 — four hours after the leak
stopped. v2 credited that. v3 records it as `retrospective_association`: a real
coincidence, but not a warning anyone could have acted on. Checks 16 and 18 are a matched
pair — same alert, only the leak's end date differs — so the rule is isolated.

New outcomes: `retrospective_association` and `issuable_after_window`. 18/18 checks pass.

## Leak activity now means positive flow, not configured onset

A gradual leak ramps from zero, so the configuration's start time can precede any
measurable water loss. Silent periods after onset, main zone:

| Leak | Silent after onset |
|---|---|
| p427 | **67.8 h** |
| p810 | 63.6 h |
| p654 | 53.5 h |
| p461 | 19.5 h |
| p628 | 3.9 h |
| p232 | 1.2 h |
| all abrupt leaks | 0.0 h |

v2 matched against the configured window while measuring quiet exposure from positive
flow — two different definitions. v3 uses positive flow for both. Delay is reported
against **both** first-positive-flow and configured onset.

## What changed in the results

**No outcome changed.** Every credited/missed decision is identical. But three delays
per experiment moved, and they are exactly the gradual leaks with long silent periods:

| Leak | Silent | A: delay v2 | A: delay v3 | B: delay v2 | B: delay v3 |
|---|---|---|---|---|---|
| p810 | 63.6 h | 10.9 h | **154.9 h** | 12.9 h | **80.9 h** |
| p654 | 53.5 h | 34.3 h | **79.3 h** | 8.3 h | **60.3 h** |
| p427 | 67.8 h | 68.6 h | **123.6 h** | missed | missed |
| p628 | 3.9 h | — | — | 7.1 h | **23.1 h** |

*(delays above measured from configured onset, so v2 and v3 are directly comparable)*

The cause: v2 credited alerts that fired while a gradual leak was **still producing no
water**. Those credits were spurious — the leak cannot have caused a warning before it
leaked. v3 refuses them and credits a later alert instead.

Median delay from configured onset: **A 50.4 → 83.4 h, B 28.9 → 80.9 h.** Measured from
first positive flow instead: A 55.8 h, B 28.9 h.

## Headline results, corrected

| | A — reference | B — calibrated |
|---|---|---|
| Baseline week / threshold | 8–14 Jan / 10 m³/h inherited | 1–7 Jan / 22.80 m³/h (99th pct of 8–14 Jan) |
| Alert events | 129 | 199 |
| **Leaks associated** | **9 / 12** | **9 / 12** |
| — abrupt | 3 / 6 | 5 / 6 |
| — gradual | 6 / 6 | 4 / 6 |
| Median delay (from first flow) | 55.8 h | 28.9 h |
| Retrospective associations | 0 | 0 |
| Issuable past window end | 0 | 0 |
| Unattributable | 0 | 47 |
| Repeats (score zero) | 119 | 143 |
| **False alerts in quiet window** | **1 in 215 h (8.96 days)** | **0 in 215 h (8.96 days)** |
| Randomly-timed warnings credit | 10.0 (95th: 12.0) | 11.0 (95th: 12.0) |

Quiet exposure is now derived from the same positive-flow definition used for matching,
rather than hard-coded, so the two cannot drift apart. It remains 215 hours.

**Neither experiment beats chance.** Both associate 9 of 12; randomly-timed warnings
associate 10 and 11. Unchanged by these corrections.

## Two claims withdrawn

**New Year's Day.** I explained experiment B's higher alert count by saying 1 January
depressed its baseline week. **Tested and refuted.** Daily mean main-zone outflow on
1 Jan is 139.19 m³/h against 137.23 on 8 Jan — *higher*, not lower. Including 1 January
moves the week mean by +0.39 m³/h, and the two candidate weeks differ by 136.87 vs
136.11 m³/h. The simulation generates demand from weekly profiles, so there is no
holiday effect to find.

**Why B fires 199 times at 22.80 m³/h when A fires 129 times at 10 m³/h is therefore
unexplained.** I am not substituting another guess.

**Sensor timing.** Previously described as established. It is an **assumption supported
by a consistency check**. The organisers document 5-minute averaging for *pressure*
sensors only; for flow and level they state just that readings transmit every 5 minutes.
Assuming the reading at `t` describes `[t, t+5min]`, the level rises in 0.16% of
pump-off intervals against 0.49% under the alternative — consistent with the assumption,
not proof of it.

## Limitations

- Simulated data; sensor faults and delays deliberately excluded by the organisers.
- Tank level quantised to 0.01 m, capping Area C accuracy near 2 m³/h hourly.
- Flow and level averaging semantics assumed, not documented.
- Area C remains **not evaluable** for false alerts: zero leak-free hours in the window.
- All results are timing **associations**. Our signal names no pipe.
- Development-period numbers. Not performance.
