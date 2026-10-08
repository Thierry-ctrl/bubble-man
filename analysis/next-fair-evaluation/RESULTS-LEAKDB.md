# LeakDB Hanoi — results of the single locked run (8 Oct 2026)

Protocol: `PROTOCOL-LEAKDB.md`, revision 4 (commit 0dbd107). Simulated data, exploratory
test — not validation. The failed 2019 L-Town result (`../night-flow-step/RESULTS-2019.md`)
is unchanged.

## Verdict

**Q1 (network transfer): FAIL**, on the workload criterion. This exact method — the night-flow
step check with the self-aligning baseline, threshold 4 × early robust spread — **failed
on LeakDB Hanoi**. Too few of its warnings led to a new leak. The result says nothing
about other night-flow approaches or other settings.

| Criterion | Result | Met? |
|---|---|---|
| E1 — at least 20 eligible sudden leaks | 234 | yes |
| E2 — sudden leaks found beyond chance | 212 of 234 found within 7 days; the best of 47 week-shifts found 28; p = 0.021 (the floor) | yes |
| E3 — yield of at least 50% (proposed operational target) | **18.1%** (401 of 2,217 warnings) | **no** |

**Q2 (controlled weekly slip): the self-aligning baseline re-aligned.** This verdict was
fixed from flow readings alone and committed before any leak record was opened. It is a
separate question and does not offset the Q1 failure.

## Q1 — every warning is an operator investigation

490 scenarios (11–500), all assessable; 2,217 warnings, a median of 2 per scenario.

| Scorer outcome | Warnings | What it means |
|---|---|---|
| credited | **401** | issued within 7 days of a new leak starting (212 sudden, 189 gradual) |
| false_alert | 932 | no leak flowing at all |
| unattributable | 878 | a leak was flowing, but it had started more than 7 days earlier (LeakDB leaks are never repaired) |
| coincides_with_excluded_leak | 4 | within 7 days of a leak that began before day 29 |
| retrospective_association | 2 | the leak's recorded flow had ended before the warning could be issued |
| **Investigations without a new eligible leak** | **1,816** | 82% of all warnings |

- **Sudden leaks:** 212 of 234 found. Median time from first leak flow to warning across
  all credited leaks: 16.5 h. Timing is association, not proof that a warning was caused by
  that leak.
- **Gradual leaks** (reported, not judged): 189 of 238 associated.
- **False alerts:** 932, against 3,195,348 hours with no leak flowing (summed over
  scenarios, from day 29). The 116 scenarios with no leak at all produced 309 warnings, all
  of them false alerts. In simulation this is a count with its exposure, not a utility
  false-alert rate.
- **No real warning fell on day 365**, the night outside the shift comparison.
- **Wrapped gaps:** every shift has some scenario whose warnings sit under 7 days apart
  across the wrap point. A whole-week rotation keeps the gaps between warnings when the
  year is treated as a loop, so the real list has the same property. Reported, as the
  protocol requires.

**What this means.** The step check reacts strongly to the arrival of a new sudden leak.
On LeakDB's often-large leaks it found 91% of them, far above chance. But for every warning
that led to a new leak, about four did not. On this simulation, at these settings, an
operator would mostly be sent to investigate nothing new.

### Early leaks (reported; does not change the verdict)

- **36 scenarios** had a leak flowing before day 29:
  - 22 from days 1–14, so their learned profiles were affected;
  - 14 from days 15–28, affecting the threshold only.
- **Effect on thresholds:** a median of 7.1 × the median threshold of the other scenarios
  (range 0.5 to 48.6). Early leaks made those scenarios much less sensitive.
- **Their warnings:** 63, of which 9 were credited.
- **Without those 36 scenarios:** E1 228, p = 0.021, yield 18.2% — still **FAIL**.

## Q2 — controlled weekly slip (separate question)

In each scenario's stress copy, day 150 is played twice. Every later day then carries the
pattern of the previous weekday, the same kind of slip that broke 2019. 474 of the 490
scenarios exercise it.

| Label-free measure (settled days 172–366) | Fixed weekday map | Self-aligning |
|---|---|---|
| Extra warnings caused by the slip | **+10,690** | **−2** |
| Extra warnings in the 21-day transition | +1,015 | +608 |
| Day-type agreement, stress copy vs plain | — | 99.25% vs 99.25% |

Gate: the fixed map gained 22.6 settled warnings per exercised scenario, above the minimum
of 1, so the check was informative. Verdict: "**re-aligned after a one-day slip in this
controlled check.**"

After leak labels (reported, not judged; leaks first flowing on day 150 set aside):

| Run | Warnings | Credited | Yield | Sudden found |
|---|---|---|---|---|
| Self-aligning, plain | 2,211 | 396 | 17.9% | 210 / 231 |
| Fixed map, plain | 2,182 | 396 | 18.1% | 210 / 231 |
| Self-aligning, stress copy | 2,828 | 396 | 14.0% | 209 / 231 |
| Fixed map, stress copy | 13,898 | 375 | 2.7% | 189 / 231 |

**What Q2 shows:** the repair does what it was designed to do — on a different weekly
pattern, after a neat one-day slip, it returns to normal within about three weeks, while a
fixed calendar keeps firing. The transition still costs about 600 extra warnings across
474 scenarios.

**What Q2 does not show:** that the repair handles real changes in weekly patterns, such as
holidays, Ramadan, new supply rotas or intermittent supply. Idea A was built after seeing
this kind of slip, so a pass was expected. In ordinary scenarios it simply agreed with the
fixed map, so it did not cause the Q1 failure either.

## Defects found during the run, with corrections

1. **Archive layout.** The archive held two loose example scenarios and two separate Hanoi
   sets, of 500 and 1000 scenarios. The first extraction stopped with nothing extracted; its
   output is kept in `leakdb/run/step3-attempt1-output.txt`. A label-free diagnosis
   (`leakdb/run/layout-diagnosis.txt`) showed:
   - `Hanoi_CMH.zip` is the 500-scenario benchmark: the public sample matches its
     scenarios 1–10 byte for byte.
   - The 1000-scenario set is a different simulation.

   Revision 4 fixed the choice to `Hanoi_CMH.zip`, scenarios 11–500. It was committed
   before extraction. The 1000-scenario set was not used; only its inlet files were hashed.
2. **Step 5 summary count.** `timestamps_disagree_with_inlet` printed −1018: a boolean column
   read as generic objects was negated with `~`. The original output is unchanged in
   `step5-leaks.json`. The correct value is 0 of 509 (`step5-correction-note.json`). The
   leak table and all scores are unaffected.
3. **One leak record never flowed** (scenario 241, gradual). It is reported and not scored,
   as the protocol says.

## What this result does and does not establish

- **Established, on this simulation:** at the frozen settings, the method finds new sudden
  leaks far more often than chance would. But about 82% of its warnings would send staff to
  look for a new leak that isn't there. The weekly-pattern repair works on the exact slip it
  was designed for.
- **Not established:**
  - anything about real pipes or real Rwandan networks;
  - a utility false-alert rate;
  - leak location;
  - how other night-flow methods, thresholds or warning rules would perform.

  No setting was tuned, and no second evaluation was run. Trying a higher threshold here
  would be a new, untested method and would need fresh data.
- **Held out for the future:** LeakDB's separate 1000-scenario Hanoi set. Its leak outcomes
  are untouched. Any future test there needs its own protocol written first.

## Files (`leakdb/run/`)

`step3-extract.json`, `manifest-inlet.csv` · `warnings-all-runs.csv`,
`scenarios-assessability.csv`, `step4-warnings.json` · `leaks-table.csv`,
`step5-leaks.json`, `step5-correction-note.json` · `step6-results.json`,
`per-scenario-q1.csv`, `shifts-q1.csv`, `step6-stdout.txt`.
