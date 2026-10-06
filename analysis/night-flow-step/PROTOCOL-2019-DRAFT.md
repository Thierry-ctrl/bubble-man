# Protocol — one locked 2019 evaluation of the night-flow step check (revised, exploratory)

**Status: revision 3 (7 October 2026) — option B chosen by the user. This is a revised,
exploratory evaluation, not the evaluation originally planned.** Committed before any 2019
file is obtained; the commit hash is the protocol ID.

> **The original 2018 noise stop failed and remains failed.** It was not passed, waived on
> merit, or reinterpreted. In this revised protocol the 2019 noise measures are **reported
> but do not gate** the result.
>
> **The week-shift comparison does not replace the noise check.** It tests something
> different: whether the warning *dates* line up with leak starts better than the same
> pattern moved to other weeks. It says nothing about whether ordinary night-to-night
> variation is small relative to the 10 m³/h threshold.
>
> **If S1–S4 are met, the result is described as "promising under the revised exploratory
> protocol"** — never as validation, and never as a pass of the original test.
>
> **The 2019 leak schedule was previously visible** (§2.4). This evaluation is blind to the
> 2019 readings, not to the list of 2019 leaks.

Scope: **detecting an additional new leak in the main zone.** Not a measure of losses
present for months.

### Revision 3 — what changed from revision 2

1. Option **B** recorded as chosen; the framing box above added; §4.5 and §10 wording
   aligned with it.
2. **Clarifications fixed before the run, not changes to the criteria:** S2 and S4 are
   computed on the full 2019 window (1 Jan – 31 Dec); S3 on the 52-week shift domain
   (1 Jan – 30 Dec), as §9 already required. The scorer's leak list contains the eligible
   2019 main-zone leaks **and** the three carried-over leaks (with their 2018 start times,
   so they are classed "began before the window"); Area C leaks are not in the list, as in
   2018. File checksums are checked against the md5 values published by the Zenodo record.

### Revision 2 — what changed from revision 1

1. **§2.2 and §8:** withdrew the claim that credits after 48 hours are unlikely to be caused
   by the leak. The step's nine-night window keeps a leak's onset in the comparison for up
   to eight nights (§2.2 gives the arithmetic). Delays are now reported without assigning
   causality.
2. **§4:** the noise calculation now uses one stated basis for both years. On that basis
   the 2018 value is unchanged (2.98). But the earlier amendment compared a **robust**
   statistic with a cutoff derived from a **standard deviation**. Put on a like-for-like
   basis, the cutoff becomes 2.22, and **2018 fails the amended check as well**. The
   recommendation to adopt it is withdrawn; §4.5 sets out the remaining options.
3. **§10:** the 50% yield is labelled a proposed operational target, not a validated
   utility requirement. S0 now follows the §4.5 decision.
4. **§6, §8, §12:** carried-over leaks' 2018 start times added; a note that most 2019
   warnings may fall "during" a carried-over leak; noise-reference fragility added.

---

## 1. What was verified on 2018 before writing this

Re-checked through an independent path (`verify_2018.py`, `verify-2018.json`) that reads
only 2018-derived leak records and re-implements the rule from its written description:

| Claim | Verified |
|---|---|
| 5 warnings: 3 Feb, 6 Mar, 11 May, 8 Aug, 6 Oct | ✓ |
| Sudden leaks associated 3 of 6; gradual 1 of 6 | ✓ |
| 1 unmatched warning (`unattributable`), 0 false alerts | ✓ |
| Every association has a single candidate | ✓ |
| 49 distinct whole-week shifts (50 distinct patterns incl. original) | ✓ |
| Sudden associations across shifts: 0 in 25, 1 in 21, 2 in 3; one-sided p = 0.02 | ✓ |
| Noise: night-to-night std 6.04 m³/h > 4.5 → **original noise stop failed** | ✓ |

## 2. Issues that could mislead — and how this protocol handles them

1. **Carried-over leaks would be credited as new.** The 2019 leak file begins at
   1 Jan 2019 00:00, so a leak running since 2018 shows its "first positive flow" at exactly
   the window start, and the unchanged scorer treats it as **eligible and new**
   (demonstrated with a constructed example: credited at 52 h). → §6 excludes these leaks
   explicitly, identified from **2018 data alone**.

2. **Delay does not establish cause — in either direction.**
   `step(D) = mean(nights D, D−1) − mean(nights D−2 … D−8)`. For a constant leak of size
   *L* whose first full night is *S*, a warning on night *S + k* sees:

   | k | Leak nights in the latest pair | Leak nights in the 7 before | Step |
   |---|---|---|---|
   | 0 | 1 of 2 | 0 of 7 | +0.50 *L* |
   | 1 | 2 of 2 | 0 of 7 | +1.00 *L* |
   | 2 | 2 of 2 | 1 of 7 | +0.86 *L* |
   | 3 | 2 of 2 | 2 of 7 | +0.71 *L* |
   | 4 | 2 of 2 | 3 of 7 | +0.57 *L* |
   | 5 | 2 of 2 | 4 of 7 | +0.43 *L* |
   | 6 | 2 of 2 | 5 of 7 | +0.29 *L* |
   | 7 | 2 of 2 | 6 of 7 | +0.14 *L* |
   | 8 | 2 of 2 | 7 of 7 | 0 |

   The nights before the leak stay in the comparison until night *S + 8*; each night after
   *S + 1* moves one more leak night into the "before" window and dilutes the step by
   one-seventh of *L*. A 20 m³/h leak keeps the step at or above 10 through *S + 4*; a
   28 m³/h leak through *S + 5*. A gradual leak that keeps growing can hold it there
   longer. So a credit several days after onset **can** reflect the leak, and a short
   delay does not prove that it does. Delays are **reported, not interpreted causally**
   (§8). The shift comparison applies the same deadline to every pattern, so the p-value
   is unaffected.

3. **"Unattributable" warnings still cost an operator a visit.** → §8 counts **every**
   warning as an investigation.

4. **The 2019 leak schedule is not blind.** It sits in `battledim-config.yaml` next to the
   2018 rows. During scorer development (28–29 Sep 2026) the full 33-leak table, including
   2019 pipe IDs, start times and types, was printed on screen. The rule's parameters were
   declared in the input audit without reference to it, and the 2019 *readings* have never
   been downloaded. **This evaluation is blind to readings, not to the leak schedule.**

5. **The shift comparison is coarse and not independent.** Its smallest possible p-value is
   fixed by the number of weeks, and the shifts are one pattern moved through the year.

6. **A warning's scorer hour is 03:00.** A leak starting between 03:00 and 03:55 on night D
   cannot be credited to D's warning even if it lifted that night's value. Conservative;
   left unchanged.

## 3. Unchanged rule and baseline

Exactly as `RULE-FROZEN.md` (`b944498`); no parameter changes.

- Signal: `p227 + p235 − PUMP_1`, hourly means of the 5-minute readings.
- Baseline: medians per hour over **1–14 January 2018**, day types Sun–Thu / Fri / Sat,
  assigned by each reading's calendar date (2019 dates use 2019 weekdays).
- Night value for date D: mean residual over the hours labelled 02:00 and 03:00.
- `step(D) = mean(night D, D−1) − mean(nights D−2 … D−8)`.
- Warn if `step ≥ 10.0`, armed, and ≥ 7 days since the previous warning. Re-arm on the first
  later night with step < 10.0.
- Issue time **04:00** on date D (scorer hour 03:00 + the unchanged 1-hour lag).

## 4. Noise check

### 4.1 Original — on record, unchanged

Standard deviation of night-to-night change in the night residual; stop if **> 4.5 m³/h**,
where 4.5 = 2 × the standard deviation over the January reference (2.25, §4.3).
**2018: 6.04 — FAILED.** That failure stands and is reported in every summary.

### 4.2 Common basis for both years

The same calendar span and first-night rule in each year:

- **Nights 15 January – 31 December** of the year (351 nights in both 2018 and 2019).
- **Changes within the span only:** `change(D) = night(D) − night(D−1)` for D = 16 January
  … 31 December. The first night, 15 January, has no change; nothing before the span is
  used. **350 changes in each year.**
- Why 15 January: in 2018, 1–14 January trained the baseline, so their residuals are
  in-sample and artificially small. Excluding the same dates in 2019 keeps the season and
  span identical.
- Sensitivity, 2018 only: using the full calendar year instead (changes 2 Jan – 31 Dec,
  364) gives a robust spread of 2.96 rather than 2.98 — immaterial.

### 4.3 The January reference — and why it matters

Both cutoffs are anchored to the only 2018 period with no labelled main-zone leak flow
outside the training weeks: **nights 15–23 January 2018, changes 16–23 January — 8 values.**

| Statistic | January reference | ×2 cutoff | 2018, common basis | 2018 result |
|---|---|---|---|---|
| Standard deviation (original) | 2.25 | **4.5** | 6.04 | **fails** |
| Robust spread, (Q3 − Q1) / 1.349 | 1.11 | **2.22** | 2.98 | **fails** |

**Eight values cannot anchor either cutoff reliably.** An interquartile range from eight
numbers rests on a couple of points; the factor-of-two gap between the two January figures
shows how unstable the reference is.

### 4.4 The amended candidate, corrected

Revision 1 proposed the robust spread against the **4.5** cutoff. That compared a robust
statistic with a threshold built from a standard deviation — not like for like. On a
consistent basis (robust statistic, robust reference, common dates) the amended check
would be:

    robust_sigma = (Q3 − Q1) / 1.349 over the 350 changes, 16 Jan – 31 Dec
    pass if robust_sigma ≤ 2.22  (2 × 1.11, the robust January reference)

**2018 fails it (2.98 > 2.22).** The amendment therefore does **not** offer a consistent
route past the noise check, and the recommendation to adopt it is **withdrawn**.

For the record, the inconsistent version (robust spread vs 4.5) would pass 2018 at 2.98.
It is not proposed.

### 4.5 Decision — option B chosen

**Chosen: (B).** The options as they were presented:

- **(A) Drop.** The noise check failed on 2018 under the original statistic and under a
  like-for-like robust version. On that evidence the method is not taken to 2019, and
  this protocol is not run.
- **(B) Run, with the noise check reported but not gating.** Both statistics (§4.1, §4.4)
  are computed on 2019 readings and reported; neither decides the outcome, which rests on
  S1–S4 (§10). This **demotes a gate after it failed**, which is what moving the goalposts
  looks like; it is a weaker protocol and is labelled as one in every result. The noise
  question — is a 10 m³/h step clearly above ordinary night-to-night variation? — remains
  **unanswered by S3**, which tests only whether warning dates align with leak starts.
- **(C) Not offered:** any other cutoff now (for example one tied to the threshold, 10/3 =
  3.33) would be chosen after seeing 2018's 2.98.

## 5. Start of year, warm-up and re-arming

- The rule runs **continuously from 15 Jan 2018 to 31 Dec 2019**. 2018 nights supply the
  warm-up, so `step` exists from 1 Jan 2019.
- State entering 2019, from 2018 data: last warning 6 Oct 2018; the step last reached 10 on
  10 Oct and fell below it on 11 Oct; steps on 24–31 Dec 2018 range from −1.8 to +0.2. The
  rule therefore enters 2019 **armed**, with no spacing constraint. The run asserts this.
- Only warnings issued on 1 Jan – 31 Dec 2019 are evaluated.
- The run asserts that the 2019 file begins at 2019-01-01 00:00, five minutes after the
  2018 file ends, with no gap.

## 6. Leaks: carried over, eligible, and typed

- **Carried over from 2018 — excluded.** Main-zone leaks still flowing at
  2018-12-31 23:55 in the 2018 file:

  | Leak | Type | First positive flow (2018 file) |
  |---|---|---|
  | p427 | gradual | 2018-02-16 04:15 |
  | p654 | gradual | 2018-07-07 09:10 |
  | p810 | gradual | 2018-07-30 18:40 |

  (p257 is also flowing, in Area C, outside this signal.) Before scoring, each one's start
  is set to the 2018 time above, so the unchanged scorer classes it as "began before the
  window".
- **Eligible:** main-zone leaks whose first positive simulated flow in the 2019 leak file
  falls between 2019-01-01 00:00 and 2019-12-31 23:00, excluding the three above.
- **Zone:** assigned by the same network-map procedure as 2018 — link endpoints in the
  690-node component fed by p227 and p235. Area C leaks are not eligible.
- **Type:** sudden (`abrupt`) or gradual (`incipient`), from the leak schedule.
- **Activity:** first to last positive simulated flow; the deadline runs from first
  positive flow.

## 7. Missing readings

Exactly as the current code behaves, documented rather than changed:

- an hour's value per meter is the mean of whichever 5-minute readings exist;
- the main-zone value is missing if any of the three meters has no reading in that hour;
- a night is missing if either of its two hours is missing;
- `step` is missing if any of its nine nights is missing;
- a missing night neither arms nor disarms the rule and issues no warning;
- a missing night breaks the noise changes on either side of it (no change is computed
  across a gap).

The number of missing 5-minute readings and missing nights is reported **before** scoring.
(2018 had none.)

## 8. Scoring and workload

- Existing scorer, unchanged: `Rules(gap 0, reporting lag 1 h, max delay 168 h)`;
  persistence 1; window 2019-01-01 00:00 – 2019-12-31 23:00.
- Credit requires the warning's hour to fall inside the leak's activity, with the warning
  issuable within 168 h of first positive flow and while the leak still flows.
- **Reported separately:** sudden leaks (judged) and gradual leaks (reported, not judged —
  outside the method's purpose).
- **Per leak:** outcome and delay from first positive flow. For each associated warning,
  the number of the nine window nights on which the associated leak was flowing, split
  into the latest pair and the seven before — reported as **context, not as proof of
  cause** (see §2.2).
- **Every warning is an operator investigation.** Reported: total warnings; warnings by
  month; each warning's scorer outcome (`credited`, `unattributable`,
  `repeat_of_credited_leak`, `coincides_with_excluded_leak`, `false_alert`,
  `retrospective_association`, `issuable_after_window`);
  **investigations without an eligible new leak = total − credited**; and
  **yield = credited ÷ total**.
- Warnings issued while a carried-over leak was flowing are also counted. If those leaks
  run through 2019, this will include most warnings and says nothing about cause by itself.
- False alerts are reported as a count with its exposure hours, never as a rate.

## 9. Comparison with shifted warnings

- **Domain:** 1 Jan 2019 (Tuesday) – 30 Dec 2019 (Monday): 364 nights, exactly 52 weeks.
  The 31 December night is outside it; a real warning there is reported in the full-window
  result only.
- **Shifts:** real warning nights in the domain moved by k whole weeks, k = 1 … 51, wrapping
  circularly — **51 distinct shifts**. Each keeps count, weekday, 04:00 issue time and
  spacing, except the one gap across the wrap point; any wrapped gap under 7 days is
  reported.
- Real and shifted patterns are scored on the same domain, with the same leak list.
- **p_sudden = (1 + shifts associating at least as many sudden leaks as the real
  warnings) / 52.** Smallest possible value 1/52 = 0.019. Same for all leaks (reported,
  not judged).

**Limitations, stated in advance:** shifts are one pattern moved through the year, not
independent trials; they move warnings between seasons; they test *when* warnings fall,
holding their number fixed, so they say nothing about whether the count is reasonable; and
with few warnings the distribution is coarse.

## 10. What counts as success

| | Criterion |
|---|---|
| **S0 — noise** | **Reported, not gating** (option B) — both statistics on the §4.2 basis. The original 2018 noise stop **failed and remains failed**. |
| **S1 — enough events** | At least **3** eligible sudden main-zone leaks exist in 2019 |
| **S2 — real hits** | The real warnings associate at least **2** eligible sudden leaks (full 2019 window) |
| **S3 — beyond chance** | p_sudden ≤ **0.05** — at most 1 of the 51 shifts does as well or better ((1 + 1)/52 = 0.038; (1 + 2)/52 = 0.058) |
| **S4 — workload** | Yield ≥ **50%** over the full 2019 window — a **proposed operational target**, not a validated utility requirement |

- **Promising under the revised exploratory protocol:** S1–S4 all met. Not validation;
  not a pass of the original test, whose noise stop failed.
- **Inconclusive:** S1 not met — too few events to judge, whatever else happens.
- **Fail:** S1 met and any of S2–S4 fails.

S4 is a judgement about acceptable workload, offered for review. It is not a statistical
result, not derived from any utility's practice, and not derived from 2018 (where 4 of 5
warnings were associated). A real deployment would set it with the utility's crew capacity.

## 11. Exactly what would happen in the single run

1. Option B approved; this version is committed and its git hash becomes the protocol ID.
2. Download **`2019_SCADA_Flows.csv` only**; verify its checksum against the Zenodo record;
   assert continuity with 2018. Report missing readings.
3. Compute night residuals, steps and **both** noise statistics on the §4.2 basis. Record
   them. **Commit.**
4. Generate the warnings with the unchanged rule. Record the full warning list. **Commit —
   before any 2019 leak record is opened.**
5. Download `2019_Leakages.csv`; verify its checksum. Assign zones; apply the §6 exclusions;
   build the eligible list. **Commit the leak list.**
6. Score; run the 51 shifts; compute S1–S4 and all §8 figures.
7. Write `RESULTS-2019.md` reporting every number specified here, whatever it shows.

**No second run.** No parameter changes. If a code bug is found after step 4, the fix and
the reason are documented, the original output is kept alongside, and both are reported.
A failure is reported as a failure.

## 12. What remains uncertain

- **Noise gate:** failed on 2018 under both the original and a like-for-like robust
  statistic, and remains failed; both cutoffs rest on eight January changes (§4.3). In this
  revised protocol it does not gate, and nothing in 2019 can change the 2018 failure.
- **Label blindness:** the 2019 leak schedule was displayed during earlier work (§2.4).
- **Overlap:** all three 2018 misses came from overlapping leaks; 2019 will likely contain
  similar overlaps, and the protocol does not correct for them.
- **Power:** the number of eligible sudden main-zone leaks in 2019 is unknown without
  opening the schedule. If small, the result may be inconclusive or fragile.
- **Simulation:** sensor faults and delays were excluded by the organisers; night-flow
  reasoning fails under intermittent supply, as in Rwanda.
