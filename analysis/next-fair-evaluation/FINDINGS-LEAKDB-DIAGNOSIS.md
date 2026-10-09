# Why most LeakDB warnings did not lead to a new leak — development diagnosis

*9 October 2026. **Development work** on the 490 already-scored LeakDB Hanoi scenarios
(11–500). Scenarios 1–10 were the public sample and were never scored. Leak labels are
used here only to explain results after the fact. The locked result in `RESULTS-LEAKDB.md`
(FAIL, yield 18.1%) and the failed 2019 L-Town result are unchanged. The separate
1,000-scenario set was not opened. Code and outputs: `leakdb-dev/`.*

Corrections to wording in the locked write-up (no score changes) are in
`CORRECTION-NOTE-2026-10-09.md`. Most importantly, LeakDB leaks **do** stop (median
duration 45 days), contrary to what the protocol said.

## 1. The 1,816 warnings that did not lead to a new leak

| Group | Warnings | Share of all 2,217 |
|---|---|---|
| **No leak flowing at all** (`false_alert`) | **932** | 42% |
| **An older leak was flowing** (`unattributable` 878, `coincides_with_excluded_leak` 4, `retrospective_association` 2) | **884** | 40% |
| Led to a new leak (`credited`) | 401 | 18% |

### Group 1 — no leak flowing (932): the January baseline falls behind the season

- **They barely cross the line.** The median step is 1.12× the threshold; credited
  warnings have a median of 5.0×.
- **They happen at weekends in the high-demand months.**
  - 89% fall in February, June or July.
  - 77% fall on Friday or Saturday nights.
- **Why.** LeakDB's demand is a weekly pattern *multiplied* by a yearly curve.
  - Median night flow rises about 26% from January (2,399 m³/h) to July (3,028 m³/h).
  - Our expected profile is a fixed amount learned in January, so the weekend rise in the
    observed night flow grows beyond it as demand climbs.
  - Each Friday–Saturday pair then looks like a jump against the weekday nights before it
    (trace A in `leakdb-dev/traces.png`).
  - In leak-free scenarios, the leak-free night residual in July sits about 8–9× the
    threshold above the January profile, and higher on weekend day types.
- **The threshold was set in the quietest season.** In each scenario, the step's spread
  over leak-free nights for the whole year is a median of **1.7×** its January spread. The
  threshold, 4× the January spread, is effectively about 2.4× the year's spread.
- **It is concentrated in the scenarios with the smallest thresholds:**

  | Threshold relative to night flow | Lowest quarter | 2nd | 3rd | Highest quarter |
  |---|---|---|---|---|
  | False alerts per scenario (mean) | 5.7 | 1.5 | 0.3 | 0.06 |

### Group 2 — an older leak flowing (884): LeakDB's "gradual" leaks switch on and off

- 719 of the 884 occurred while only a "gradual" (incipient) leak was flowing; another 53
  had both kinds, and 112 a sudden leak only.
- In **81%** of these warnings, the change in the leak's own night flow, by itself,
  exceeded the threshold. The warning was a reaction to the leak, not to demand.
- **But the leak was not growing.** 98% of LeakDB's gradual leaks switch on and off at
  night at least once a week: a median of 2.7 switches per week, with 31% of their active
  nights near zero. Sudden leaks do this 0.4% of the time.
  - Each time the leak switches back on, the step jumps and the rule fires again (trace B).
  - A median warning came 44 days after that leak began, long past the 7-day window in
    which it could count as new.
- **Reading it plainly:** these warnings point at a real, already-known leak. Whether that
  is wasted effort depends on whether the leak is already being handled. They also say as
  much about the simulator's on–off leaks as about the method.

### How it varies across scenarios (not only pooled totals)

- **Warnings per scenario:** median 2; 75th percentile 6; 90th percentile 12; maximum 29.
  78 scenarios had none.
- **Concentration:** 41% of the 1,816 warnings that found no new leak came from 10% of
  scenarios, and 73% from a quarter. 168 scenarios had no such warning at all.
- **Sudden leaks, per scenario:** 205 scenarios had at least one eligible sudden leak. In
  183 all were found; in 21 none was.
- **The 22 missed sudden leaks:**
  - 12 small or short — under about 1.25× the threshold at night, or ended within a week;
  - 7 blocked by the 7-day spacing after an earlier warning. In 5 of these, that earlier
    warning was the leak itself starting at 03:30, inside the night window, and was scored
    a false alert by the scorer's hour-start timing (trace C; correction note §3);
  - 2 in scenarios whose threshold an early leak had inflated (T = 670 and 1,799 m³/h);
  - 1 coinciding with another leak's change in flow.
- **Typical catch** (trace D): a sudden leak shows as a large, clean jump, credited a median
  of 14.5 hours after it started.

## 2. One proposed change: an adaptive threshold

**The rule.** Everything stays as frozen except the threshold:

> T(D) = 4 × the robust spread of the step over the previous eight weeks, ending nine
> nights before D (days D−56 to D−9). Until 20 such values exist, use the frozen January
> threshold.

The nine-night gap keeps the current step's own nights out of the estimate. Everything it
uses is available when the warning is issued.

**Why it fits the diagnosis.** The threshold rises when the season makes nights more
variable (group 1). It also rises while an on–off leak makes them jumpy (group 2). A new
sudden leak still produces a jump far above either: a median of about 10× the frozen
threshold at night.

### Development comparison (490 scenarios already scored; same scorer, same shift test)

| | Frozen | Adaptive threshold |
|---|---|---|
| Sudden leaks found / eligible | 212 / 234 | 208 / 234 |
| Median delay, sudden leaks | 14.5 h | 14.5 h |
| Gradual leaks associated / eligible | 189 / 238 | 173 / 238 |
| **Total investigations (warnings)** | **2,217** | **831** |
| **Investigations without a new eligible leak** | **1,816** | **450** |
| — no leak flowing (false alerts) | 932 | 138 |
| — older leak flowing (+ other) | 884 | 312 |
| Leak-free exposure (hours) | 3,195,348 | 3,195,348 |
| **Yield** | **18.1%** | **45.9%** |
| Week-shift comparison, sudden leaks: real vs best of 47 shifts | 212 vs 28 (p = 0.021) | 208 vs 11 (p = 0.021) |
| Scenarios with ≥ 5 false alerts | 79 | 0 |
| Scenarios where every sudden leak was found (of 205) | 183 | 179 |

**Cost:**
- 6 sudden leaks lost and 2 gained (`leakdb-dev/dev-compare-per-scenario.json`).
  - 5 of the 6 lost were small: their largest step was only 1.0–1.3× the frozen threshold,
    and the summer threshold rose past them.
  - 1 was a large leak in scenario 82, hidden because an on–off gradual leak had raised the
    threshold to 1,765 m³/h. That is the expected failure mode: an adaptive threshold can
    hide a new leak behind an older, noisy one.
- 16 fewer gradual leaks associated.

**It still misses the 50% operational target on the data it was chosen on.** A fresh test
would be expected to do no better, and probably somewhat worse.

### Alternatives examined (all on the same development data)

| Candidate | Warnings | Sudden found | False alerts | Yield | Why not chosen |
|---|---|---|---|---|---|
| Fixed threshold 6× January spread | 1,206 | 204 | 112 | 31.3% | Less gain, similar loss |
| Residual as a percentage of expected | 2,580 | 212 | 645 | 15.7% | More warnings during older leaks |
| Step minus the same weekday's step 1–3 weeks earlier (warnings from day 50) | 2,356 | 194 / 217 | 1,095 | 15.8% | Worse than frozen on the same window (yield 18.0%) |
| Warn only at a new 4-week high | 1,049 | 168 | 648 | 30.1% | Loses 44 sudden leaks |
| **Adaptive threshold** | **831** | **208** | **138** | **45.9%** | **Chosen** |

Five candidates were tried, each once, with no parameter search. Choosing the best of five
on the same data makes its result optimistic. That is why it needs a fresh test.

## 3. What this does and does not show

- **Shows, in this simulation:** most wasted investigations came from two specific
  mismatches:
  - a threshold set in January, applied to a year whose demand and variability grow;
  - a simulator whose gradual leaks switch on and off.

  Letting the threshold follow recent variability cut investigations without a new leak by
  three-quarters, at a cost of about 2% of sudden leaks.
- **Does not show:**
  - that the change works on a fresh dataset — the 1,000-scenario set is needed for that;
  - that it works on real networks, where leaks do not switch on and off on a simulator's
    schedule;
  - anything about how real gradual leaks behave.
- **What would help beyond rule changes:** something that tells demand apart from leakage
  at night. Examples are a pressure reading at the zone's critical point, or a sample of
  hourly customer meters, so a rising night is checked against consumption. LeakDB's data
  can't test this honestly: its pressures come from the same hydraulic model, and it has no
  separate consumption record.

## 4. Next step

A draft protocol for **one** test on the untouched 1,000-scenario set is in
`PROTOCOL-LEAKDB-1000-DRAFT.md`. Nothing from that set has been opened beyond the
inlet-file hashes recorded in revision 4.
