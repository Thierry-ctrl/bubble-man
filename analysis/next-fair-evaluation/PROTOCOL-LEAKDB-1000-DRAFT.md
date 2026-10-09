# LeakDB Hanoi 1,000-scenario set — protocol DRAFT for one test

**Status: DRAFT for review. Not approved, not run.** Nothing from
`LeakDB/Hanoi_CMH_1000scenarios.zip` has been opened. The only exception is its inlet
files for scenario numbers 1–500, which were hashed during the revision-4 layout diagnosis
(`leakdb/run/layout-diagnosis.txt`): their bytes were read, but no value was inspected,
printed or kept. Its leak records, labels and `.inp` files are untouched. Exploratory,
synthetic data — never "validation".

## 1. Question

Does the **adaptive threshold** (`FINDINGS-LEAKDB-DIAGNOSIS.md`, §2) cut the
investigations that find no new leak, without losing sudden leaks, on a fresh set of
simulations it was not chosen on? And does it reach the operational target?

The frozen method runs alongside, on the same scenarios, as the comparator.

## 2. Why this set is a fair test, and its limits

- **Same network, separate simulation.** None of its inlet files match the 500-scenario
  set's, and the adaptive rule was chosen without seeing it.
- **Same generator family.** The development findings — demand that scales with the
  season, gradual leaks that switch on and off, leaks that stop — are probably present
  here too, but **that is not checked before warnings are committed**. It is reported
  afterwards (§8).
- A pass would show that the change holds up on new LeakDB simulations, not on real
  networks.

## 3. Data access order (nothing earlier in the list may depend on anything later)

1. This protocol, the run code and its tests are committed. The code is to be written, then
   tested on invented cases including the adaptive-threshold edge cases in §4. The archive
   is already on disk; its md5 was verified on 8 Oct 2026, and is re-verified before use.
2. Extract **only** `Hanoi_CMH/Scenario-N/Flows/Link_1.csv` from the named inner archive
   `LeakDB/Hanoi_CMH_1000scenarios.zip`, for **all scenarios 1–1000**, into a new folder.
   Member names are never printed; counts only. Commit the manifest: IDs, rows, SHA-256.
3. Generate both warning lists (adaptive and frozen) and the assessability table. **Commit
   before any leak file is extracted.**
4. Extract `Leaks/Leak_*.csv` for the manifest scenarios; build the leak table; commit.
5. Score once and report every number in §6–§8. No reruns, no setting changes. Any
   data-layout or code defect is documented, with the original output kept, before any
   correction.

## 4. Rules (no setting may change after approval)

**Common to both rules** — the frozen method of `PROTOCOL-LEAKDB.md` §5, unchanged:
- day types learned from days 1–14 (the 3× rule);
- night window: the lowest two consecutive hours over days 1–14;
- self-aligning day type from day 22;
- night value and step(D) = mean(nights D, D−1) − mean(nights D−2 … D−8);
- warnings from day 29: armed, re-arm below threshold, at least 7 days apart, issued at the
  end of the night window.

The not-assessable rules of `PROTOCOL-LEAKDB.md` §6 apply, judged on the frozen rule's
inputs.

**Comparator (frozen):** T = 4 × robust spread (IQR/1.349) of the steps on days 9–28.

**Primary (adaptive):**
- T(D) = 4 × robust spread of the finite steps on days D−56 to D−9 inclusive (never
  earlier than day 9), provided at least 20 values exist.
- Otherwise T(D) = the frozen T.
- If the spread is zero or undefined, the frozen T is used for that night.
- The rule is "step(D) ≥ T(D)". Re-arming uses the same night's T(D).

Edge cases to test before data:
- the switch from the frozen to the adaptive T as values accumulate;
- missing steps inside the window;
- a zero spread;
- that T(D) never uses the step of D or of nights D−1 … D−8.

## 5. Scoring (unchanged scorer, `analysis/scorer/leak_scorer.py`)

- **Scorer settings:** persistence 1, reporting lag 1 h, deadline 168 h from first positive
  leak flow, one-to-one matching.
- **Window:** day 29 00:00 to the last timestamp.
- **Leaks:** activity from first to last positive leak flow, placed on the inlet grid by row
  position; each scenario scored separately.
- **Judged:** sudden (abrupt) leaks. **Reported, not judged:** gradual (incipient) leaks.
- **Workload:** every warning is an investigation.
  - yield = credited ÷ warnings;
  - investigations without a new eligible leak = warnings − credited, split by scorer
    outcome;
  - false alerts reported as a count with leak-free exposure hours.
- **Chance comparison:** each rule separately, 47 whole-week shifts over days 29–364,
  the same k for every scenario; p = (1 + shifts ≥ real) / 48.
- **Reported sensitivity:** credit a leak that starts inside the flagged night hour
  (correction note §3). Does not change any verdict.

## 6. Success criteria (adaptive rule)

| | Criterion |
|---|---|
| G1 — enough events | ≥ 20 eligible sudden leaks in assessable scenarios (else **inconclusive**) |
| G2 — beyond chance | adaptive rule's sudden-leak p ≤ 0.05 |
| G3 — detection not worse | adaptive finds ≥ (frozen found − 5% of eligible sudden leaks) |
| G4 — fewer wasted investigations | investigations without a new eligible leak ≤ 50% of the frozen rule's |
| G5 — operational target | yield ≥ 50% — a *proposed* target, not a validated utility requirement |

**Verdicts, fixed now:**
- G1–G5 all met → "**promising on a held-out LeakDB simulation set**".
- G1–G4 met but G5 not → "**improved over the frozen rule, below the 50% target**". This is
  not a pass.
- G2, G3 or G4 failing → "**the adaptive threshold did not hold up on new simulations**".

**Expectation stated in advance:** on the development data the adaptive rule reached 45.9%.
Because it was chosen there, a lower figure is expected here, so G5 is **unlikely** to be
met. The test is still worth running, because G3 and G4 are the real question.

## 7. Reported per scenario, not only pooled

- the distribution of warnings and false alerts per scenario, for both rules;
- the number of scenarios with ≥ 5 false alerts;
- per-scenario sudden-leak detection, for both rules;
- the sudden leaks found by one rule but not the other, with the adaptive threshold at
  onset.

## 8. Reported after labels (does not change the verdict)

- Whether the development findings recur:
  - share of leaks that stop before year end;
  - share of gradual leaks switching on and off at least weekly;
  - share of false alerts in February, June and July, and on Friday or Saturday nights.
- Early-leak sensitivity, as in `PROTOCOL-LEAKDB.md` §8.1.

## 9. Known exposures

- **Development work:** all design choices in §4 were made on scenarios 11–500 of the
  500-scenario set, with their leak labels. Five candidate changes were examined there
  (`FINDINGS-LEAKDB-DIAGNOSIS.md`, §2). The adaptive rule was chosen as the best of those
  five.
- **Zero-spread fallback:** added for safety. It never occurred in the development data
  (0 nights), so the rule is identical to what was examined.
- **Generator knowledge:** the LeakDB generator code was read (§12 of `PROTOCOL-LEAKDB.md`).
- **The 1,000-scenario set itself:** inlet bytes of scenarios 1–500 were hashed (see Status).
  Nothing else was read.

## 10. Before approval, please decide

1. Whether G3's 5% margin and G4's 50% reduction are the right bars.
2. Whether to keep G5 at 50%, or report it without judging it, given the stated
   expectation.
