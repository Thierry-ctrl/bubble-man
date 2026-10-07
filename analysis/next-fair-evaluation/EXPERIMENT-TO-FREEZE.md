# Next experiment — draft for freezing before any LeakDB leak record is seen

**Status: DRAFT. Not run. Nothing in LeakDB has been downloaded except the 10-scenario sample
in the public repository, whose file names were listed but whose files were not opened.**
To be approved, committed, and only then executed. Exploratory transfer test, **not
validation**.

## Purpose

Does the night-flow step idea, with a baseline that re-aligns weekdays from recent readings,
find **new sudden leaks** better than chance on a **different network and demand
realisation** than L-Town? Scope: new leaks only.

What this test **cannot** show: LeakDB's demand repeats on an exact 7-day cycle, so it never
slips by a day. The weekday re-alignment will not be exercised; this tests transfer, not the
specific repair. LeakDB leaks are never repaired and are often large, so it is probably
**easier** than L-Town. A pass is weak evidence; a fail is informative.

## Data

- **LeakDB, Hanoi network** (`Hanoi_CMH`), full archive, Zenodo record 13985057
  (`LeakDB.zip`, 13.9 GB, CC BY 4.0). Download needs your approval because of its size.
  Checksum against the Zenodo md5 before use.
- **Scenarios:** every Hanoi scenario numbered **11 or higher** present in the archive, in
  index order. **Scenarios 1–10 excluded**: their total leak count (9 leaks in 10 scenarios)
  became known from the public repository sample's file names.
- **Only file read before warnings are committed:** `Scenario-N/Flows/Link_1.csv` — the
  inlet pipe from the single reservoir. Extracted with a quiet path-pattern extraction;
  **the archive is never listed** (file names under `Leaks/` contain leak node IDs).
- **Not opened until warnings are committed:** `Leaks/`, `Labels.csv`, `Scenario-N_info.csv`,
  and every other flow, pressure or demand file.

## Method — one primary method, nothing else scored

Per scenario, on hourly means of the inlet flow (two 30-minute readings each, m³/h):

1. **Learning period: days 1–14.** For each day of the week, two examples. A day of the week
   gets its own profile if its distinctness (RMS of its two-day mean vs the median of all
   other days) exceeds **3 ×** the largest repeatability (RMS between the two examples of any
   day of the week) — the rule frozen in `analysis/weekend-baseline/BASELINE-FROZEN.md`.
   Otherwise it is pooled. Profiles = median per hour over days 1–14 of each type.
2. **Night window:** the two consecutive clock hours with the lowest mean flow in the pooled
   profile, fixed per scenario from days 1–14.
3. **Self-aligning day type (Idea A):** from day 22, each day's type is the profile whose
   z-scored 24-hour shape best matches the average z-scored shape of the same weekday on
   days D−7, D−14, D−21 (completed days only). Before day 22, the weekday mapping learned
   in step 1.
4. **Night value** = mean residual (flow − profile of the assigned type) over the night
   window. **Step(D)** = mean(nights D, D−1) − mean(nights D−2 … D−8).
5. **Threshold, per scenario:** T = **4 ×** robust σ, (Q3 − Q1)/1.349, of the steps on days
   9–28 (20 values). Declared now; not adjustable.
6. **Warning rule:** warn on night D if step ≥ T, armed, and ≥ 7 days since the previous
   warning; re-arm on the first later night with step < T. Issued at the end of the night
   window, when all its readings exist. Warnings from **day 29** on.

## Scoring

- Existing scorer, **unchanged**: persistence 1, reporting lag 1 h, deadline 168 h,
  one-to-one, window day 29 00:00 to the scenario's last timestamp.
- Leak activity from `Leak_*_demand.csv` (first to last positive leak flow); type from
  `Leak_*_info.csv`. Leaks whose first positive flow is before day 29 are "began before the
  window" and not scored.
- **Judged class: abrupt leaks.** Gradual (incipient) reported, not judged.
- **Every warning is an investigation.** Report total, credited, investigations without a
  new eligible leak, yield, and — measurable for the first time, because LeakDB has periods
  and whole scenarios with no leak — **false alerts with their exposure hours**.

## Comparison with chance

Within each scenario, warning nights on days 29–364 (48 whole weeks) are shifted by k whole
weeks, wrapping. The **same k is applied to every scenario**, and abrupt credits are pooled:
**47 distinct pooled shifts**, p = (1 + shifts ≥ real) / 48, floor 0.021. Shifts are one
pattern per scenario moved through the year, not independent trials; any wrapped gap under
7 days is reported.

## Pre-declared outcome

| | Criterion |
|---|---|
| E1 — enough events | ≥ 20 eligible abrupt leaks in total (else **inconclusive**) |
| E2 — beyond chance | pooled abrupt p ≤ 0.05 |
| E3 — workload | yield ≥ 50% — *proposed operational target, not a validated utility requirement* |
| Reported, not judged | false alerts per scenario-year with exposure; gradual leaks; delays (no causal reading) |

**E1–E3 met → "promising on LeakDB Hanoi under an exploratory transfer test"** (synthetic,
same modelling family as L-Town). Never "validated". Any of E2–E3 failing → **fail**.

## Order of operations

1. You approve this draft and the 13.9 GB download; it is committed (hash = protocol ID).
2. Download; verify md5; extract only `*/Hanoi_CMH/Scenario-*/Flows/Link_1.csv`, quietly,
   for scenarios ≥ 11. Commit the list of scenario IDs and row counts.
3. Generate all warnings. **Commit before any leak file is extracted.**
4. Extract `Leaks/` for the same scenarios; build the leak table; commit.
5. Score, run the 47 shifts, report every number above, whatever it shows. No reruns.

## Known exposures, stated now

- The LeakDB generator code was read: leaks start uniformly at random, run to the end of the
  year, are abrupt or incipient with equal probability, hole diameter 0.02–0.2 m, 0–2 per
  scenario. That is design knowledge, not outcomes; the threshold multiplier (4) and
  criteria above were not tuned to it, and none of it enters the warning rule.
- The LeakDB authors published minimum-night-flow detector scores on 500 Hanoi scenarios
  (aggregate, in the 2018 paper). Our method resembles theirs. Their results were not used.
