# LeakDB Hanoi protocol — revision 4

**Status: approved for one run (7 Oct 2026), with the correction below: all scoring and
week-shift code written, tested on invented leak cases, and committed before the download.** Nothing from the full LeakDB archive
has been downloaded. No new leak record has been opened. The 2019 L-Town failure
(`analysis/night-flow-step/RESULTS-2019.md`) is unchanged and is not re-scored here.
Revision 1 was the draft `EXPERIMENT-TO-FREEZE.md` (commit 5874bea); revision 2 was commit
043c7e4. Detector settings and success criteria are identical in all three.
Exploratory, synthetic data — **never "validation"**.

## 1. Two separate questions

| | Question | How it is answered | Judged? |
|---|---|---|---|
| **Q1 — transfer** | Does the night-flow step check, with the self-aligning baseline, find new sudden leaks better than chance on a different network and demand realisation (LeakDB Hanoi)? | LeakDB scenarios as published, unaltered | **Yes** (§9) |
| **Q2 — weekly-slip repair** | When the weekly pattern slips by one day, does the self-aligning baseline re-align, where a fixed weekday map does not? | A controlled stress copy of the same readings (§7) | **Separately** (§9), never pooled with Q1 |

LeakDB's weekly demand pattern repeats exactly every 7 days and never shifts. **Q1 says
nothing about Q2.** In ordinary LeakDB scenarios the self-aligning step should simply agree
with the fixed weekday map; a Q1 pass is not evidence that the repair works.

## 2. What changed

**Revision 4 (this one) — data-layout correction, 8 Oct 2026.** No setting, criterion or
code path that touches flow values changed.
- **What happened.** The download matched Zenodo's size and md5. The first
  `step3_extract.py` run then stopped, extracting nothing. The output is kept in
  `leakdb/run/step3-attempt1-output.txt`.
- **Archive layout.** The archive is not one Hanoi folder. It holds:
  - two loose example scenarios, `LeakDB/Hanoi_CMH/Scenario-1` and `Scenario-2`;
  - `LeakDB/Hanoi_CMH.zip`, 500 scenarios;
  - `LeakDB/Hanoi_CMH_1000scenarios.zip`, 1000 scenarios;
  - Net1 and the paper's code.
  The extractor found the two loose scenarios, excluded them as below 11, and stopped.
- **Label-free diagnosis** (`leakdb/run/layout-diagnosis.txt`), from inlet files and file
  counts only. No leak, label or `.inp` file was opened or listed.
  - The GitHub public sample is byte-identical to scenarios 1–10 of
    `Hanoi_CMH.zip`, and matches none of the 1000-scenario set.
  - The two sets share no identical inlet file among their 500 common scenario numbers.
    They are separate simulations.
  - The loose examples match neither set.
- **Decision.** The test set is `LeakDB/Hanoi_CMH.zip` — the 500-scenario benchmark of the
  2018 paper that this protocol describes — **scenarios 11–500 (490)**. Scenarios 1–10 stay
  excluded, because they are the public sample.
  - The 1000-scenario set is **not used**. It is a separate simulation whose leak outcomes
    are untouched; only its inlet files were hashed. That makes it the natural held-out set
    for any future replication, which would need its own protocol.
  - The two loose examples are not used.
- **Code change.** `extract()` gains `inner_member`. Steps 3 and 5 name
  `LeakDB/Hanoi_CMH.zip` explicitly.
- **Tests.** The pipeline test now includes decoys copying this layout: a loose folder and a
  second Hanoi archive. Results: 11/11, plus invented-case scoring 30/30.

**Revision 3** — code frozen before data. No setting or criterion changed.
- Scoring, week-shift and Q2 code (`leakdb/scoring.py`, `step3_extract.py` … `step6_score.py`)
  written and committed **before any LeakDB leak record is opened**, and before the download.
- Tested on invented cases (`leakdb/test_scoring.py`, 30/30): issue timing, the 168-hour
  deadline (exactly 168 h credited, 168.5 h not), leaks already flowing at day 29 and the
  window edge, one-to-one matching (repeat, two candidates, two leaks), never-repaired leaks,
  per-scenario scoring when node names repeat, week shifts wrapping across the year boundary,
  47 shifts and the p formula, Q2 leak-time mapping, leak-file reading and exposure hours.
- End-to-end run of steps 3–6 on an invented 32-scenario archive (`leakdb/test_pipeline.py`,
  10/10), including that no leak file exists before step 5.
- Leak-file details fixed from the generator code (§9): format; leak times placed on the
  inlet file's grid by row position; two leaks on one node appear as one record.
- Q2: leaks first flowing on day 150 are removed from the leak table in all four Q2 runs.
- Step 5 refuses to run unless the warning list is committed and unchanged in git.

**Revision 2** — relative to revision 1:

1. Q1 and Q2 separated; a controlled weekly-slip stress check added for Q2 (§7).
2. Rules for missing readings and unusable scenarios declared before any data (§6).
3. Early leaks (before warnings start): no label-based exclusion or recalibration;
   effect reported afterwards (§8).
4. The 10 public sample scenarios used for code checks only; results in §10.
5. Download size, md5 and disk space checked; extraction tested so that leak-revealing
   file names are never shown (§4).
6. Day of week defined by position in the series, not by the timestamp's calendar date
   (§5). The public sample is stamped 2017, the generator code 2018; the weekly pattern
   follows position in both.
7. "False alerts are measurable for the first time" narrowed (§8.3): LeakDB leaks are never
   repaired, so false alerts can only occur before a scenario's first leak.

Unchanged: the method's settings, the threshold multiplier (4), the 7-day spacing, the
scorer, the chance comparison, E1–E3.

## 3. Data

- **LeakDB**, Zenodo record 13985057, file `LeakDB.zip`, **13,888,061,642 bytes
  (12.93 GiB)**, `md5:d607929ef7caea432e663aee8071f2d7` (Zenodo API, 7 Oct 2026). CC BY 4.0.
- **Network:** Hanoi (`Hanoi_CMH`): 31 junctions, one reservoir, no tanks, pumps or valves;
  base demand 5,538.9 m³/h. Inlet = pipe `1`, file `Scenario-N/Flows/Link_1.csv`.
- **Scenarios:** scenarios **11–500** of the benchmark set `LeakDB/Hanoi_CMH.zip` (§2,
  revision 4). The actual list is committed at extraction. **Scenarios 1–10
  are excluded**: they match the public sample, whose file names revealed 9 leaks.
- **Read before warnings are committed:** only `Flows/Link_1.csv` per scenario.
- **Not opened until warnings are committed:** `Leaks/`, `Labels.csv`, each scenario's
  `.inp` (it may encode leaks), every other flow, pressure and demand file, and the
  published detector results in the LeakDB GitHub repository.

## 4. Download, disk and extraction safety

- **Disk:** 46 GiB free on 7 Oct 2026. Peak need ≈ 26 GiB: the archive (12.93 GiB), plus,
  if Hanoi is a zip inside the zip, a temporary copy of it (≤ 12.93 GiB, deleted after). The
  extracted inlet files are about 0.5 MB each. **Before downloading, at least 30 GiB must be
  free; otherwise stop.**
- **Location:** `data/leakdb/` (git-ignored). The archive is not committed. The extracted
  inlet files are identified by a committed manifest (scenario, row count, SHA-256).
- **Verification:** exact byte size and md5 must match, or stop.
- **Extraction:** `leakdb/extract_inlet.py`. It reads member names into memory to find
  matches but **never prints or writes them**. It extracts only paths ending exactly in
  `Hanoi_CMH/Scenario-N/Flows/Link_1.csv` (or `Scenario-N/Flows/Link_1.csv` inside a nested
  `Hanoi_CMH.zip`), for N ≥ 11. It reports only counts and scenario numbers. With any other
  layout, or with two inlet files for one scenario, it extracts nothing and stops. No
  archive listing (`unzip -l`, Finder, Archive Utility) is ever used.
- **Tested** (§10) on mock archives whose leak files carry a marker string, in a flat, a
  nested and an unknown layout. The marker never appeared in any output or file name.
  On the real public sample, `--min-scenario 11` extracted nothing.

## 5. Method (unchanged from revision 1; code `leakdb/method.py`)

Per scenario, on hourly means of the inlet flow (both 30-minute readings required), in m³/h.
**Day 1 is the first day in the file; weekday = (day − 1) mod 7.**

1. **Day types, days 1–14.** For each weekday, two examples. Repeatability = RMS between
   them; distinctness = RMS of their mean against the median of the other 12 days. A
   weekday gets its own type if distinctness > **3 ×** the largest repeatability; otherwise
   it joins one pooled type. Profiles = hourly median over days 1–14 of each type.
2. **Night window:** the two consecutive clock hours (not crossing midnight) with the
   lowest median flow over days 1–14.
3. **Self-aligning type (Idea A):** from day 22, each day takes the profile whose
   standardised 24-hour shape best matches (Pearson correlation) the standardised mean of
   the same weekday's days D−7, D−14, D−21. Before day 22, the weekday map from step 1.
4. **Night value** = mean of (flow − assigned profile) over the night window.
   **Step(D)** = mean(nights D, D−1) − mean(nights D−2 … D−8).
5. **Threshold:** T = **4 ×** (Q3 − Q1)/1.349 of the steps on days 9–28 (20 values).
6. **Warning:** night D, from day 29, if step ≥ T, the rule is armed, and ≥ 7 days have
   passed since the last warning. Re-arms on the first later night with step < T. Issued at
   the end of the night window.

## 6. Missing readings and unusable scenarios — declared now, label-free

- The file is placed on a 365-day, 30-minute grid from its first timestamp; absent,
  duplicated or non-numeric readings become missing. Rows beyond 365 days are ignored.
- An hour needs both readings; a night needs both hours; a step needs all nine nights.
  A missing step issues no warning and leaves the armed state unchanged.
- If any of days 1–14 lacks an hourly value, the day types cannot be learned.
- Idea A keeps the weekday map for a day if any of D−7, D−14, D−21 is incomplete.
- **A scenario is "not assessable"** if any of these hold: the inlet file is absent or
  unreadable; days 1–14 are incomplete; **fewer than 15 of the 20 threshold steps exist**;
  their robust spread is zero or undefined; or fewer than 300 step values exist from
  day 29. A first timestamp not at 00:00 is also not assessable.
- Not-assessable scenarios issue no warnings. They are listed with their reason in the
  warnings commit, **before any leak file is extracted**. Their leaks are reported
  separately and are outside E1–E3. The decision uses flow readings only.
- No other exclusion, re-run or per-scenario adjustment exists.

## 7. Q2 — controlled weekly-slip stress check

**Why it is fair enough to run.** The 2019 failure arose because L-Town's demand replay
played one weekday twice at New Year, and every later day carried the pattern of the
weekday before. The same disruption can be recreated exactly on LeakDB readings, and its
effect measured without leak labels. LeakDB's weekly pattern has distinct weekend days. In
the generator's template, adjacent weekdays' night levels differ by up to about 13% of the
mean night flow, and all ten sample scenarios learned four day types. So a slip can matter.

**What changes:** only the order of days. In a stress copy of each inlet series, **day 150
is played twice** (the copy becomes day 151). Every later day moves one day later and so
carries the pattern of the preceding weekday — the 2019 kind of slip. The copy is 366 days
long. No reading value is altered.

**What stays fixed:** every setting in §5 and §6; the days 1–14 learning; the night window;
the threshold (days 9–28 lie before the repeat, so T is identical); the scorer. Both day
150 and its repeat are fixed now for all scenarios.

**Runs:** each assessable scenario is run four ways — {Idea A, fixed weekday map} ×
{plain, stress copy}. **All four warning lists are committed with the Q1 warnings, before
any leak file is extracted.** Only "Idea A, plain" is the Q1 method.

**Periods (stress-copy day numbers):** transition days 151–171 (Idea A cannot fully
re-align until all three look-back days follow the repeat); **settled days 172–366**.
Stress-copy day d ≥ 151 corresponds to plain day d − 1.

**Measures (no leak labels):**
- **M1 — type agreement, settled period:** the share of days whose assigned type equals the
  type of the weekday pattern the day actually carries. Compared for Idea A on the stress
  copy versus Idea A on the corresponding plain days.
- **M2 — excess warnings, settled period:** warnings in the stress copy minus warnings on
  the corresponding plain days, pooled over scenarios, for each method. The transition
  period is reported separately and not judged.

**Exercised scenario:** assessable in all four runs, and some pair of adjacent weekdays
has different learned types (so the slip changes at least one day's type).

**Interpretation, declared now:**
- **Not informative** if fewer than 20 scenarios are exercised, or if the fixed weekday map
  gains fewer than 1 settled-period warning per exercised scenario on average. In that case
  the slip barely matters in LeakDB, and Q2 is reported as **untested**.
- Otherwise, "**Idea A re-aligned after a one-day slip in this controlled check**" if both:
  - M1 on the stress copy ≥ M1 on the plain series − 0.05;
  - Idea A's settled-period excess ≤ 25% of the fixed map's excess.

  If either fails: "**did not re-align**".
- After leak labels (reported, **not judged**): abrupt-leak credits and yield for all four
  runs. For the stress copy, leak times after day 150 move one day later. Leaks whose first
  positive flow falls on day 150 are set aside in all four runs.

**What a positive Q2 result would mean:** only that the mechanism corrects the exact kind
of slip it was designed after, on a different weekly pattern and noise level. Idea A was
built *after* seeing that failure, so a pass is expected and mostly confirms the code
works. A failure would be informative.

**What Q2 cannot show.** Real changes in weekly patterns are not neat one-day slips. Some
change the *shape* of a day (Ramadan, a new supply rota). Some touch single days (public
holidays such as Umuganura or Kwibohora). Some appear gradually (school terms), or are
caused by intermittent supply. The self-aligning baseline can only choose among the
January shapes it learned, and needs three weeks to follow any change. Testing that needs
**real inlet flow (15-minute or finer) covering at least one full year — ideally two —
with dated records of holidays, rota or schedule changes and supply interruptions, logged
independently of the flow data, plus repair records for scoring.** No public dataset found
provides this.

## 8. Early leaks — no label-based action before warnings are frozen

Leaks start at uniformly random times, so some scenarios will have a leak flowing during
days 1–28. That can distort the learned profiles (days 1–14) or widen the early spread and
raise the threshold (days 9–28). **No scenario is selected, excluded or recalibrated using
leak labels.** The threshold stays as in §5 for every assessable scenario.

### 8.1 Reported afterwards (does not change any verdict)
- Number of scenarios with a leak whose first positive flow precedes day 29, split into
  days 1–14 (profiles affected) and days 15–28 (threshold only).
- For those scenarios: the ratio of their threshold to the median threshold of scenarios
  with no leak flowing before day 29; their warnings by scorer outcome; their eligible leaks.
- E1–E3 recomputed **without** those scenarios, as a sensitivity line only.

### 8.2 How they are scored
Leaks whose first positive flow is before day 29 00:00 are "began before the window" and
are not credited (scorer rule). Warnings matched to them are `coincides_with_excluded_leak`
and count as investigations without a new eligible leak.

### 8.3 False alerts
LeakDB leaks never stop. A warning is a `false_alert` only if **no** leak is flowing; after
a scenario's first leak, unmatched warnings become `unattributable`. False alerts are
reported as a count with exposure = hours from day 29 with no leak flowing, summed over
scenarios. They are **never** reported as a rate on their own.

## 9. Scoring and pre-declared outcomes

**Q1 scoring** — "Idea A, plain" only:
- Existing scorer, **unchanged** (`analysis/scorer/leak_scorer.py`): persistence 1;
  reporting lag 1 h; deadline 168 h from first positive flow; one-to-one matching; window
  from day 29 00:00 to the scenario's last timestamp.
- Leak activity is taken from `Leak_*_demand.csv` (first to last positive flow), and leak
  type from `Leak_*_info.csv`.
  - The demand file has columns `Timestamp, Description` (m³/h).
  - Rows are placed on the inlet file's 30-minute grid by position, and whether the
    timestamps agree is recorded.
  - LeakDB writes one file pair per leak node. If two leaks share a node, they appear as one
    record, with the type from the surviving info file.
  - A record that never flows is reported and not scored.
- Each scenario is scored separately (node names repeat across scenarios); counts are then
  pooled.
- Abrupt leaks are judged. Gradual (incipient) leaks are reported, not judged.
- Every warning counts as an investigation:
  - **yield** = credited ÷ total warnings (a credit to a leak of either type counts);
  - **investigations without a new eligible leak** = total − credited.

**Chance comparison (Q1):** warning nights on days 29–364 (48 whole weeks) are shifted by
k whole weeks, with wrapping. The same k applies to every scenario, and abrupt credits are
pooled. That gives **47 distinct shifts**, p = (1 + shifts ≥ real) / 48, floor 0.021. A
real warning on day 365 is scored in the full window but lies outside the shift domain;
it is reported separately. Any wrapped gap under 7 days is reported.

| Q1 | Criterion |
|---|---|
| E1 — enough events | ≥ 20 eligible abrupt leaks in assessable scenarios (else **inconclusive**) |
| E2 — beyond chance | pooled abrupt p ≤ 0.05 |
| E3 — workload | yield ≥ 50% — *a proposed operational target, not a validated utility requirement* |
| Reported, not judged | false alerts with exposure (§8.3); gradual leaks; delays (no causal reading); not-assessable scenarios; early-leak sensitivity (§8.1) |

E1–E3 met → "**promising on LeakDB Hanoi under an exploratory transfer test**". If E2 or E3
fails → **fail**.

**Q2:** verdict per §7, reported in its own section, never combined with Q1.

## 10. Code checks on the public sample (done; scenarios 1–10, excluded)

`leakdb/check_code_on_sample.py` → `leakdb/sample-code-check.json`, **17 of 17 checks
passed**. What was checked:
- **Extraction safety:** the three mock layouts, and the real sample wrapped as a nested
  archive.
- **Loader:** 17,520 rows each, regular 30-minute steps, start at 00:00, nothing missing.
- **Units:** flow is always positive; the yearly mean is 1.00–1.02 × Hanoi's base demand,
  which confirms m³/h.
- **Warning generation:** all 40 runs assessable. Warnings only from day 29, with step ≥ T,
  at the end of the night window, ≥ 7 days apart.
- **Stress copy:** 366 days, day 150 repeated, and warnings before the repeat identical to
  the plain run.

Label-free structure recorded: all ten scenarios learned 4 day types, with the night window
starting at 02:00.

**Not done:** no sample scenario was scored. No leak file, `Labels.csv`, scenario `.inp`
or published result was opened. Warning counts, dates and thresholds were neither printed
nor saved. No setting was changed after the checks.

## 11. Order of operations

1. Revision 3 and all code committed; tests pass. Any later change → a new revision,
   committed before the step it affects, with the original output kept.
2. Check free space ≥ 30 GiB. Download to `data/leakdb/raw/`; `step3_extract.py` verifies
   size and md5.
3. `step3_extract.py` extracts the inlet files (scenarios ≥ 11). Commit the manifest:
   scenario IDs, row counts, SHA-256.
4. `step4_warnings.py`: the four warning lists, the assessability table, and the label-free
   Q2 measures and verdict. **Commit before any leak file is extracted.**
5. `step5_leaks.py`: extract `Leaks/` for the manifest scenarios, build the leak table, and
   commit it.
6. `step6_score.py`, once: Q1, the shifts, the early-leak sensitivity, and Q2 after labels.
   Report every number, whatever it shows. No reruns. A data-layout or code defect is
   documented, and the original output kept, before any correction.

## 12. Known exposures

- **Generator code read:** leaks start uniformly at random, never end, are abrupt or
  incipient with equal probability, have hole diameters of 0.02–0.2 m, and number 0–2 per
  scenario. This is design knowledge, not outcomes.
- **Generator weekly template examined** (§7) only to judge whether a slip check could be
  informative; it contains no leak information.
- **Public sample:** file names only (revealing 9 leaks in scenarios 1–10, hence
  their exclusion), plus the code checks of §10.
- **Published results:** the LeakDB authors published aggregate minimum-night-flow detector
  scores on Hanoi (2018 paper). Our method resembles theirs; their results were not used.

## 13. What the full test would and would not establish

**Would establish (if E1–E3 pass):** that the night-flow step check, with no settings
changed, flags new sudden leaks more often than chance on a second simulated network with
its own demand noise, and at a stated workload.

**Would not establish:**
- that it works on real pipes, real meters or intermittent supply;
- that it handles real changes in weekly patterns (Q1 cannot; Q2 covers only a neat
  one-day slip);
- that it finds small or gradual leaks;
- a reliable false-alert rate;
- where a leak is.

LeakDB comes from the same research group and modelling approach as L-Town. Its leaks are
often large and never repaired, so a pass is weak evidence. A fail on Q1 would be decisive
for this idea in its current form.
