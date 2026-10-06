# Draft protocol — one locked 2019 evaluation of the night-flow step check

**Status: DRAFT for review. Nothing in this document has been run on 2019.** No 2019
reading is present in the project; none has been downloaded. Approval of this protocol,
and of the noise-check choice in §4, is required before anything in §11 happens.

Scope: **detecting an additional new leak in the main zone.** Not a measure of losses
present for months.

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
| Robust spread of the same changes: 2.98 m³/h | ✓ |

## 2. Issues found that could mislead — and how this protocol handles them

1. **Carried-over leaks would be credited as new.** The 2019 leak file begins at
   1 Jan 2019 00:00. A leak running since 2018 therefore shows its "first positive flow"
   at exactly the window start, and the unchanged scorer treats it as **eligible and new**
   (demonstrated with a constructed example: credited at 52 h). → §6 excludes these
   leaks explicitly, identified from **2018 data alone**.
2. **Late credits are weak evidence.** The step compares the last 2 nights with the 7
   before. A leak that began more than ~2 days before a warning sits partly in both
   windows, so the step cannot be responding to its onset — yet the 7-day deadline still
   credits it (2018: p232 at 72 h). The shift comparison applies the same deadline, so the
   p-value stays fair; per-leak delays over 48 h will be **flagged** as unlikely to be
   causal.
3. **"Unattributable" warnings still cost an operator a visit.** The scorer does not count
   them as false alerts. → §8 counts **every** warning as an investigation.
4. **The 2019 leak schedule is not blind.** It sits in `battledim-config.yaml` next to the
   2018 rows. During scorer development (28–29 Sep 2026) the full 33-leak table, including
   2019 pipe IDs, start times and types, was printed on screen. The rule's parameters were
   declared in the input audit without reference to it, and the 2019 *readings* have never
   been downloaded. But **this evaluation is blind to readings, not to the leak schedule.**
   A reviewer should weigh that.
5. **The shift comparison is coarse and not independent.** Its smallest possible p-value
   is fixed by the number of weeks, and the shifts are one pattern moved through the year.
6. **A warning's scorer hour is 03:00.** A leak starting between 03:00 and 03:55 on night D
   cannot be credited to D's warning even if it lifted that night's value. This is
   conservative and is left unchanged.

## 3. Unchanged rule and baseline

Exactly as `RULE-FROZEN.md` (`b944498`); no parameter changes.

- Signal: `p227 + p235 − PUMP_1`, hourly means of the 5-minute readings.
- Baseline: medians per hour over **1–14 January 2018**, day types Sun–Thu / Fri / Sat,
  assigned by each reading's calendar date (2019 dates use 2019 weekdays).
- Night value for date D: mean residual over the hours labelled 02:00 and 03:00.
- `step(D) = mean(night D, D−1) − mean(nights D−2 … D−8)`.
- Warn if `step ≥ 10.0`, armed, and ≥ 7 days since the previous warning. Re-arm on the
  first later night with step < 10.0.
- Issue time **04:00** on date D (scorer hour 03:00 + the unchanged 1-hour lag).

## 4. Noise check — original on record, amended candidate for approval

**Original (kept on record, unchanged):** standard deviation of night-to-night change in
the night residual over the evaluation nights; stop if **> 4.5 m³/h**.
*2018: 6.04 — FAILED.* That failure stands and is reported in every summary.

**Amended candidate (A1) — proposed, not adopted:**

    robust_sigma = (Q3 − Q1) / 1.349
    over the night-to-night changes of the night residual, 2 Jan – 31 Dec 2019
    (364 changes), readings only, computed before any leak record is opened.
    Gate passes if robust_sigma ≤ 4.5 m³/h.

Why amend: the standard deviation is dominated by a handful of large jumps — in 2018 the
10 largest of 350 changes carried 65% of the variance — and those jumps are largely the
leak onsets and repairs the method exists to see. A statistic inflated by the signal cannot
tell whether ordinary nights are too noisy. The interquartile range ignores the extremes.

What the amendment does **not** change: the cutoff (4.5, twice January's reference) and the
data it is computed on. Only the statistic changes.

Full disclosure: A1 is proposed **after** seeing 2018, where it would read 2.98 and pass.
A cutoff tailored to that value (for instance "threshold ≥ 3 robust sigmas", i.e. 3.33)
was considered and **rejected** because choosing a cutoff after seeing the number it must
clear is tuning. Keeping the original cutoff is the most conservative amendment available.

**Decision required:** (a) the original check stands — on 2018's evidence the method
should be dropped and this protocol not run; or (b) A1 replaces it, labelled throughout as
a post-hoc amendment. Both statistics are reported in 2019 either way.

## 5. Start of year, warm-up and re-arming

- The rule runs **continuously from 15 Jan 2018 to 31 Dec 2019**. 2018 nights supply the
  warm-up, so `step` exists from 1 Jan 2019.
- State on entering 2019 is whatever the 2018 run leaves. From 2018 results: last warning
  6 Oct 2018 (spacing irrelevant by 1 Jan); the step fell below 10 after it, so the rule
  enters 2019 **armed**. The run asserts this.
- Only warnings issued on 1 Jan – 31 Dec 2019 are evaluated.
- The run asserts that the 2019 file begins at 2019-01-01 00:00, five minutes after the
  2018 file ends, with no gap.

## 6. Leaks: carried over, eligible, and typed

- **Carried over from 2018 — excluded.** Main-zone leaks still flowing at
  2018-12-31 23:55 in the 2018 file: **p427, p654, p810**. (p257 is also flowing, in Area C,
  outside this signal.) Before scoring, their start is set to their 2018 first-positive-flow
  time so the unchanged scorer classes them as "began before the window". Warnings coinciding
  with them are counted in §8.
- **Eligible:** main-zone leaks whose first positive simulated flow in the 2019 leak file
  falls between 2019-01-01 00:00 and 2019-12-31 23:00, excluding the three above.
- **Zone:** assigned by the same network-map procedure as 2018 — link endpoints in the
  690-node component fed by p227 and p235. Area C leaks are not eligible.
- **Type:** sudden (`abrupt`) or gradual (`incipient`), from the leak schedule.
- **Activity:** first to last positive simulated flow; the scorer's deadline runs from
  first positive flow.

## 7. Missing readings

Exactly as the current code behaves, documented rather than changed:

- an hour's value per meter is the mean of whichever 5-minute readings exist;
- the main-zone value is missing if any of the three meters has no reading in that hour;
- a night is missing if either of its two hours is missing;
- `step` is missing if any of its nine nights is missing;
- a missing night neither arms nor disarms the rule and issues no warning.

The number of missing 5-minute readings and missing nights is reported **before** scoring.
(2018 had none.)

## 8. Scoring and workload

- Existing scorer, unchanged: `Rules(gap 0, reporting lag 1 h, max delay 168 h)`;
  persistence 1; window 2019-01-01 00:00 – 2019-12-31 23:00.
- Credit requires the warning's hour to fall inside the leak's activity, with the warning
  issuable within 168 h of first positive flow and while the leak still flows.
- **Reported separately:** sudden leaks (judged) and gradual leaks (reported, not judged —
  outside the method's purpose).
- **Per leak:** outcome, delay from first positive flow, and a flag on delays over 48 h.
- **Every warning is an operator investigation.** Reported: total warnings; warnings by
  month; each warning's scorer outcome (`credited`, `unattributable`,
  `repeat_of_credited_leak`, `coincides_with_excluded_leak`, `false_alert`,
  `retrospective_association`, `issuable_after_window`); warnings during a carried-over leak;
  **investigations without an eligible new leak = total − credited**; and
  **yield = credited ÷ total**.
- False alerts are reported as a count with its exposure hours, never as a rate.

## 9. Comparison with shifted warnings

- **Domain:** 1 Jan 2019 (Tuesday) – 30 Dec 2019 (Monday): 364 nights, exactly 52 weeks.
  The 31 December night is outside it; a real warning there is reported in the
  full-window result only.
- **Shifts:** real warning nights in the domain moved by k whole weeks, k = 1 … 51,
  wrapping circularly — **51 distinct shifts**. Each keeps count, weekday, 04:00 issue time
  and spacing, except the one gap across the wrap point; any wrapped gap under 7 days is
  reported.
- Real and shifted patterns are scored on the same domain, with the same leak list.
- **p_sudden = (1 + shifts associating at least as many sudden leaks as the real
  warnings) / 52.** Smallest possible value 0.019. Same for all leaks (reported, not judged).

**Limitations, stated in advance:** shifts are one pattern moved through the year, not
independent trials; they move warnings between seasons; they test *when* warnings fall,
holding their number fixed, so they say nothing about whether the count is reasonable; and
with few warnings the distribution is coarse.

## 10. What counts as success

All required:

| | Criterion |
|---|---|
| **S0 — gate** | The approved noise check (§4) passes on 2019 readings, before scoring |
| **S1 — enough events** | At least **3** eligible sudden main-zone leaks exist in 2019 |
| **S2 — real hits** | The real warnings associate at least **2** eligible sudden leaks |
| **S3 — beyond chance** | p_sudden ≤ **0.05** (at most 1 of the 51 shifts does as well or better) |
| **S4 — workload** | Yield ≥ **50%**: at least half of all warnings associate an eligible new leak |

- **Pass:** S0–S4 all met.
- **Inconclusive:** S1 not met — too few events to judge, whatever else happens.
- **Fail:** S0 fails, or S1 is met and any of S2–S4 fails.

S4 is a draft operational choice for your review — a judgement about acceptable workload,
not a statistical result. It was not derived from 2018 (where yield was 4 of 5).

## 11. Exactly what would happen in the single run

1. **You approve** this protocol and the §4 choice. The approved version is committed;
   its git hash becomes the protocol ID.
2. Download **`2019_SCADA_Flows.csv` only**; verify its checksum against the Zenodo record;
   assert continuity with 2018. Report missing readings.
3. Compute night residuals, steps and **both** noise statistics. Record S0. **Commit.**
4. Generate the warnings with the unchanged rule. Record the full warning list. **Commit —
   before any 2019 leak record is opened.**
5. Download `2019_Leakages.csv`; verify its checksum. Assign zones; apply the §6 exclusions;
   build the eligible list. **Commit the leak list.**
6. Score; run the 51 shifts; compute S1–S4 and all §8 workload figures.
7. Write `RESULTS-2019.md` reporting every number specified here, whatever it shows.

**No second run.** No parameter changes. If a code bug is found after step 4, the fix and
the reason are documented, the original output is kept alongside, and both are reported.
A failure is reported as a failure.

## 12. What remains uncertain

- **Label blindness:** the 2019 leak schedule was displayed during earlier work (§2.4).
- **Overlap:** all three 2018 misses came from overlapping leaks; 2019 will likely contain
  similar overlaps, and the protocol does not attempt to correct for them.
- **Power:** the number of eligible sudden main-zone leaks in 2019 is not known without
  opening the schedule. If small, the result may be inconclusive or fragile.
- **Simulation:** sensor faults and delays were excluded by the organisers; night-flow
  reasoning fails under intermittent supply, as in Rwanda.
