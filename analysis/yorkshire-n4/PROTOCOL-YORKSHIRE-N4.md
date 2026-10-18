# First real-data test — Yorkshire Water, Area N4 (protocol)

**Status: DRAFT until the founder commits it.** That commit is the freeze. Nothing from the
dataset has been downloaded. Only two things have been read: the first 4 KB of the N4 flow
file, to learn its columns, and the header of the property-count file. The repairs file has
not been opened.

**What this test is.** The first test of Bubble Man on **real** meters, in a **UK**
network with continuous supply. It does **not** test Rwanda and it does **not** validate
the method. Its records are mains-repair completion dates, so it can show **timing
associations** between warnings and later repairs. It cannot show detection delay, and it
cannot show false alerts.

## 1. Question

On real district meter areas (DMAs, the UK term for a metered zone), are recorded mains
repairs preceded by a night-flow warning in the same area more often than chance would
give? And what workload would the warnings create? Both unchanged rules are run: the
adaptive rule (primary) and the frozen rule (comparator).

## 2. Data

Source: *Yorkshire Water Leakage DMA 15 Minute Data*, Data Mill North / data.gov.uk,
CC BY 4.0. Credit: Yorkshire Water.

| File | Size | Opened when |
|---|---|---|
| `N4 2016_2017.csv` — 15-minute DMA flows, L/s, with validity codes V/I/M, 1 Apr 2016 – 31 Mar 2017 | 101,862,786 bytes, the published Content-Length | Step 1 |
| `Mains Repairs 2016-17.csv` | 85,226 bytes, published | Step 3, **after the warnings are committed** |

- **Why N4.** It is the smallest of the 20 regional files, which is why it was chosen. No
  flow or repair data from any region was seen before choosing.
- **Not used:** every other region, and the property and postal-sector files.

## 3. Order of steps

0. The founder commits this protocol and its code. The tests must pass first:
   - `test_yw_INVENTED.py`: 20/20;
   - `test_pipeline_INVENTED.py`: 5/5.
1. `step1_download_flow.py`: download the N4 flow file and check its size equals the
   published size; record the SHA-256. This record is committed together with step 2.
2. `step2_warnings.py`: convert every DMA, record which are assessable, and generate both
   warning lists, from flow readings only. **Commit `run/` before step 3.**
   - If the file breaks a rule in §4 — different columns, timestamps that can't be parsed,
     or a clock-change pattern other than §4's — stop. Keep the output, document the
     correction as a new revision and commit it before continuing.
3. `step3_download_repairs.py`: it refuses to run unless the warning list is committed and
   unchanged. Download the repairs file, record the SHA-256, commit.
4. `step4_score.py`: score once and report everything in §7. No reruns, no setting
   changes.

## 4. Reading the flows (`yw.py`, `read_area`)

- Required columns: `DMA, Date, Time, Flow, Flow Validity Code`. Anything else stops the
  run.
- Times are read as written, as wall-clock times with no time zone (UK local, presumably).
  A wall-clock time that appears twice, as happens at the autumn clock change, is dropped
  for those readings. A time that never appears, as at the spring change, stays missing.
  Nights touched by a clock change therefore drop out.
- **Validity:**
  - only code V is used; I, M and anything else count as missing;
  - negative flows count as missing and are counted in the report;
  - nothing is interpolated.
- **Units:** L/s × 3.6 = m³/h.
- **Grid:** a 30-minute value needs both of its 15-minute readings. The 365-day grid runs
  from 1 April 2016 00:00.
- **DMA identifiers** are compared as integers when numeric, so "011" and "11" match.

The flow figures are each DMA's measured inflow as published. Their boundaries,
transfers, storage and large night users are unknown and not corrected — a stated
limitation.

## 5. Rules — unchanged

The adaptive and frozen rules of `PROTOCOL-LEAKDB-1000.md` §4 (`leakdb1000/rules.py`),
with assessability as in `PROTOCOL-LEAKDB.md` §6:
- days 1–14 complete;
- at least 15 of the 20 threshold steps present;
- at least 300 step values from day 29.

**Expected cost:** the rule is strict about gaps. A single missing reading in the first
two weeks, or a few percent of missing nights, makes a DMA unassessable. That is a property
of the frozen method on real data and is reported, not relaxed.

**Repairs file.** It must contain exactly one column whose name includes "dma" and exactly
one whose name includes "date". Dates are read day-first and used as **dates only**.
Anything else stops the run for a documented correction.

## 6. Timing association — what counts

- **Eligible repair:** in an assessable DMA, completed between day 57 (27 May 2016) and day
  365, so that 28 days of possible warnings exist before it.
- **Preceded:** at least one warning in the same DMA on a night 1–28 days before the
  completion date. A warning on the completion day itself is reported separately, because
  the order within that day is unknown.
- **Warning followed by a repair:** a repair completes in the same DMA 1–28 days after the
  warning night.
- **28 days** is fixed now. Repairs can lag the start of a leak by days or weeks, and the
  start is unknown. It is not tuned. 7 and 14 days are **not** reported, to avoid choosing
  after the fact.
- **Words used in the report:** *preceded*, *followed*, *timing association*. **Never** used:
  *detected*, *false alert*, *missed leak*. Repairs are not a complete list of leaks. A
  warning with no later repair has no recorded outcome; it is not shown to be wrong.

## 7. Chance comparison, judged criteria and what is reported

- **Chance comparison:** for each rule, every DMA's warnings are shifted by k whole weeks
  within days 29–364, wrapping round, with the same k for all DMAs. That gives 47 shifts.
  The statistic is eligible repairs preceded, and p = (1 + shifts ≥ real) / 48.
- **Y1:** at least 20 eligible repairs in assessable DMAs; otherwise **inconclusive**.
- **Y2:** adaptive rule's p ≤ 0.05. If met: "**adaptive warnings preceded recorded repairs
  more often than chance**". If not: "**no association beyond chance detected**".
- **Reported for both rules:**
  - DMAs read and assessable, with reasons;
  - warnings, and warnings per DMA-month;
  - eligible repairs, the number and share preceded, and the median days before
    completion;
  - same-day-only cases;
  - warnings followed by a repair within 28 days;
  - the shift distribution.
- **No yield target is judged.** The records are incomplete, so the share of warnings
  followed by a repair is a lower bound on usefulness, not a yield.

## 8. What any result can and cannot mean

- **Can:** show whether the unchanged rules, on real meters, line up in time with work
  crews' repairs more than chance, and what warning rate they would generate.
- **Cannot:**
  - show detection delay, false alerts or leak location;
  - say anything about intermittent supply or Rwanda;
  - support claims about leaks that were never repaired.

  The data are from 2016–17.
- **Either way, the next step** remains a utility pilot with first-report times and field
  checks (`PILOT-READINESS.md`).

## 9. Revisions during the run

**Revision 1 — autumn clock change (before any repair record was downloaded).**
- **What happened.** Step 1 downloaded the flow file at exactly the published size. The
  first step 2 run then reported **0 duplicated timestamps**. That output is kept in
  `run/attempt1/`.
- **What the file actually does at the clock changes**, inspected from flow readings only:
  - **Spring (26 Mar 2017):** the 01:00–01:45 stamps are present with empty values. This
    is already handled as missing.
  - **Autumn (30 Oct 2016):** the file holds **one** copy of 01:00–01:45, with values, so
    it can't be told which of the two clock hours they belong to.
- **Fix.** Section 4 drops ambiguous hours, so the 01:00–01:45 readings on 30 Oct 2016 are
  now set to missing (`yw.AUTUMN_AMBIGUOUS`). Tests: invented-case 21/21, pipeline 5/5.
- **Unchanged:** every rule, criterion and setting. The fix was decided from timestamps
  alone; the repairs file has not been opened.
