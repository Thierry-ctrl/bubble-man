# LeakDB Hanoi 1,000-scenario set — protocol for one test (frozen)

**Status: approved 10 Oct 2026 with the decisions below; frozen at the commit that adds this
file and the code in `leakdb1000/`.** This is a **fresh simulation test on the same
generator family**, not validation on real networks.

**What has been read from `LeakDB/Hanoi_CMH_1000scenarios.zip`:** only the inlet files of
scenario numbers 1–500, which were hashed during the revision-4 layout diagnosis. No value
was inspected. Its leak records, labels and `.inp` files are untouched.

Unchanged: the locked 490-scenario result (`RESULTS-LEAKDB.md`, FAIL) and the failed 2019
L-Town result.

## 1. Question

On fresh simulations it was not chosen on, does the **adaptive threshold** cut warnings that
lead to no newly eligible leak, without losing sudden leaks? And does it reach the
provisional practical target? The frozen method runs alongside on the same scenarios as the
comparator.

Warnings during an older leak are reported as their own group. They point at a leak that
was already flowing, and are **not necessarily wasted investigations**.

## 2. What this test can and cannot show

- **Same network (Hanoi), separate simulation.** None of its inlet files match the
  500-scenario set's. The adaptive rule was chosen on that other set
  (`FINDINGS-LEAKDB-DIAGNOSIS.md`).
- **Same generator family.** The development findings are probably present here too:
  - demand that scales with the season;
  - gradual leaks that switch on and off;
  - leaks that stop.

  They are checked only after labels (§8).
- **A positive result** would mean the change holds up on new LeakDB simulations. It would
  not mean it works on real networks.

## 3. Data access order

Nothing earlier in this list may depend on anything later.

0. This protocol, the code and the invented-case tests are committed:
   - `leakdb1000/test_rules_and_scoring.py`: 31/31;
   - `leakdb1000/test_pipeline.py`: 11/11.
1. `step3_extract.py`:
   - re-verify the archive's size and md5;
   - extract **only** `Hanoi_CMH/Scenario-N/Flows/Link_1.csv` from the named inner archive,
     for all scenarios, into `data/leakdb/hanoi1000-inlet/`, printing counts only, never
     member names;
   - commit the manifest.
2. `step4_warnings.py`: both warning lists and the assessability table, from inlet files
   only. **Commit before step 3.**
3. `step5_leaks.py`: it refuses to run unless the warning list is committed and unchanged.
   It then extracts `Leaks/Leak_*.csv` and builds the leak table, which is committed.
4. `step6_score.py`: score once. Report every number in §6–§8.
   - No reruns and no setting changes.
   - If a data-layout or code defect prevents a trustworthy result, preserve the original
     output and explain what happened **before** any correction.

## 4. Rules — no setting may change

**Common to both rules** — the frozen method of `PROTOCOL-LEAKDB.md` §5, unchanged
(`leakdb/method.py`):
- day types learned from days 1–14 (the 3× rule);
- night window: the lowest two consecutive hours over days 1–14;
- self-aligning day type from day 22;
- night value and step(D) = mean(nights D, D−1) − mean(nights D−2 … D−8);
- warnings from day 29: armed, re-arm below threshold, at least 7 days apart.

The not-assessable rules of `PROTOCOL-LEAKDB.md` §6 apply, judged on the frozen rule's
inputs. An unassessable scenario issues no warnings under either rule.

**Comparator (frozen):** T = 4 × robust spread (IQR/1.349) of the steps on days 9–28.

**Primary (adaptive)** (`leakdb1000/rules.py`):
- T(D) = 4 × robust spread of the finite steps on days D−56 to D−9 inclusive (never earlier
  than day 9), provided at least 20 such values exist.
- Otherwise T(D) = the frozen T. A zero or undefined spread also falls back to the frozen T;
  this happened on 0 nights in development.
- A warning needs step(D) ≥ T(D). Re-arming uses the same night's T(D).
- Checked to reproduce the development rule's warnings exactly on all 490 development
  scenarios.

## 5. Timing and scoring — the prospective rule (`leakdb1000/prospective.py`)

This resolves the 03:30 issue in `CORRECTION-NOTE-2026-10-09.md` §3. LeakDB readings are
values at their timestamps, every 30 minutes. With a night window starting at hour *ns*,
for night D:

| Moment | Definition | Example (ns = 2) |
|---|---|---|
| Contributing readings | stamps ns:00, ns:30, ns+1:00, ns+1:30 on day D | 02:00, 02:30, 03:00, 03:30 |
| Night reading complete | the last contributing stamp | 03:30 |
| Warning issuable | end of the night window, ns+2:00 (unchanged from every earlier protocol) | 04:00 |

**Association.** A leak can be associated with a warning only if it could have affected a
contributing reading. Its first positive flow must be at or before the last contributing
stamp, and its last positive flow at or after the first. Then, in order (the same chain as
the locked scorer):
1. **Alive:** still flowing at the issue time; otherwise `retrospective_association`.
2. **In time:** issue time minus first flow ≤ 168 h; otherwise `unattributable`.
3. **Free:** not already credited to an earlier warning; otherwise
   `repeat_of_credited_leak`.
4. **Chosen:** the most recent first flow among the free leaks. It is `credited` if it is
   eligible, otherwise `coincides_with_excluded_leak`.

No leak flowing at all → `false_alert`. Delay = issue time − first flow.

- A leak first flowing after the last contributing reading — 04:00, say, or later that day
  — **cannot** be claimed by that night's warning. A later warning may claim it.
- These rules were tested on invented cases before any held-out reading was opened. The
  cases covered:
  - leaks starting at 01:30, 02:00, 03:00 or 03:30 (credited), and at 04:00 or 10:00 (not);
  - a pre-existing warning that must not claim a later leak;
  - the 168-hour boundary;
  - leaks ending inside the night;
  - early leaks and the window edge;
  - one-to-one matching;
  - year-boundary shifts.

  On 200 random invented scenarios with onsets away from the night edge, it agrees with the
  locked scorer.
- **The same rule scores both methods and both chance comparisons.**

**Other scoring settings** (as before):
- window: day 29 00:00 to the last timestamp;
- leak activity from first to last positive flow, placed on the inlet grid by row position;
  each scenario scored separately;
- sudden (abrupt) leaks judged; gradual (incipient) leaks reported separately;
- every warning counted as an investigation:
  - **yield** = credited ÷ warnings;
  - warnings without a newly eligible leak = warnings − credited, split into **warnings with
    no leak flowing** (`false_alert`) and **warnings during an older leak** (all other
    non-credited outcomes);
- false alerts reported as a count with leak-free hours (30-minute stamps ÷ 2).

**Chance comparison:** for each rule, 47 whole-week shifts over days 29–364, the same k
for every scenario; p = (1 + shifts ≥ real) / 48.

## 6. Success criteria (adaptive rule) — experimental decision bars, not validated utility requirements

| | Criterion |
|---|---|
| G1 — enough events | ≥ 20 eligible sudden leaks in assessable scenarios (else **inconclusive**) |
| G2 — beyond chance | adaptive rule's sudden-leak p ≤ 0.05 |
| G3 — detection | adaptive sudden-leak detection rate ≥ frozen rate − **5 percentage points** |
| G4 — fewer warnings without a new leak | adaptive warnings without a newly eligible leak ≤ **50%** of the frozen rule's |
| G5 — provisional practical target | adaptive yield ≥ 50% |

**Verdicts:**
- G1–G5 all met → "**promising on held-out LeakDB simulations**".
- G1–G4 met, G5 missed → "**improved, but below the practical target**". This is not a pass.
- G2, G3 or G4 missed → "**the adaptive threshold did not hold up on new simulations**".

**Expectation stated in advance.** In development, the adaptive rule's yield was 45.9%
under the locked scorer and 46.6% under the prospective rule
(`leakdb-dev/DEV-SENSITIVITY-PROSPECTIVE-TIMING.md`). It was chosen on that data, so a lower
figure is expected here. G5 is unlikely to be met.

## 7. Reported per scenario and per leak

For both rules:
- warnings and warnings with no leak flowing, per scenario;
- scenarios with ≥ 5 such warnings;
- per-scenario sudden-leak detection.

Also: sudden and gradual leaks found by one rule but not the other, with the adaptive
threshold at onset.

## 8. Reported after labels — does not change the verdict

- Whether the development findings recur:
  - leaks stopping before the last timestamp;
  - gradual leaks switching on and off at least weekly;
  - the frozen rule's no-leak warnings in February, June and July, and on the day-of-week
    positions that dominated in development.
- Early-leak sensitivity: the criteria recomputed without scenarios that had a leak before
  day 29.

## 9. Known exposures

- **Development:** design choices were made on scenarios 11–500 of the 500-scenario set,
  with labels. Five candidate changes were examined; the adaptive rule was the best of five.
- **The prospective timing rule** was defined after the 03:30 cases were found in
  development. Its development sensitivity was computed after the rule and the criteria
  were fixed, and was not used to change either.
- **The 1,000-scenario set:** its inlet bytes for scenarios 1–500 were hashed. Nothing else
  was read.
- **Generator code** was read earlier (`PROTOCOL-LEAKDB.md` §12).

## 10. Corrections during the run

**Correction 1 — file format (10 Oct 2026; before any warning or leak record existed).**
- **What happened.** The first `step4_warnings.py` run stopped on its first file, and no
  warning was written. The output is kept in `leakdb1000/run/step4-attempt1-output.txt`.
- **Cause.** The 1,000-scenario files carry a step counter, not timestamps:
  - header `Index,Value`, with Index running 1 to 17,520 in every one of the 1,000 inlet
    files, checked before correcting;
  - the 500-scenario files used `Timestamp,Value`;
  - the frozen reader required `Timestamp`.
- **Fix** (`leakdb1000/io1000.py`):
  - Step *n* is placed at a nominal time, 1 Jan 2017 00:00 + (n − 1) × 30 min. The method
    uses only position in the series, so the nominal origin changes no warning or score.
  - A gap or disorder in Index stops the run rather than being realigned.
  - Leak files are read with the same rule, still placed by row position. Each record
    notes its format and whether its positions agree with the inlet grid.
  - Timestamp-format files pass through unchanged to the frozen reader.
- **Tests:** `test_io1000.py` 4/4. The pipeline test now uses the Index format for the
  target set: 12/12. Invented-case scoring: 31/31.
- **Unchanged:** every rule, setting and criterion.
