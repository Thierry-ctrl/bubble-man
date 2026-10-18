# Next real evidence: can a warning arrive before staff already know?

*Decision brief, 18 October 2026. Public documentation, schemas and code were read; no
measurement or incident rows were opened. Labels: **Verified** (a source says it),
**Unknown** (not established), **Recommendation** (my judgement).*

## 1. What Yorkshire N4 established — and left open

**Verified** (`analysis/yorkshire-n4/RESULTS-YORKSHIRE-N4.md`; outcome unchanged):
- The unchanged rules ran on real UK meters. 43 of 74 DMAs could be assessed.
- 50 of 130 eligible mains repairs (38%) had an adaptive warning 1–28 days before them.
- The pre-declared verdict: **no association beyond chance detected** (p = 0.0625).
- The repairs file has two columns, `DMA` and `Date`. The publisher describes `Date` as the
  repair **completion** date.

**What it could not answer.** A completion date is the end of the story: after the leak
began, after someone noticed it, after it was confirmed. So Yorkshire can't say whether a
warning came before staff knew. It also can't say how much earlier a warning was than the
first report.

**Open methodological question, not a finding.** The only shifts that matched the real
count moved warnings 1–2 weeks. That *may* mean short shifts keep part of the real timing.
It may equally mean warnings and repairs share slow, zone-level patterns. **Unknown**
which. Dropping those shifts would not by itself show success, and Yorkshire must not be
re-scored.

**Wording to flag in the Yorkshire write-up** (left unchanged, as asked):
- "Most leaks never appear in a mains-repair list … many leaks are never found." No source
  is given. *Mains-only* is implied by the file's name; "most leaks" is unsupported.
- "The pre-declared test was therefore conservative." This is an inference. It should read
  "may have been conservative".
- "Warnings build up in the weeks before repairs and peak in the last week and on the repair
  day." This was described after the result, from overlapping warning–repair pairs, with no
  uncertainty shown. It is description, not evidence.
- In my chat summary, "near miss" and "some of the evidence still points in the right
  direction" overstate a result that did not meet its pre-set bar.

## 2. The two remaining public leads

| What we need | **Wessex Water** (4 DMA packages + regional repairs data) | **Cyprus** (KIOS Leakage-Repairs-Dataset) |
|---|---|---|
| First-report or discovery time recorded independently | **No.** Jobs have one `Job_Date`, described as "the date the job was resolved". Repairs have one `Burst_Date`, undefined. The regional mains-repairs data has only `ClosedDate`. **Verified** | **Unknown.** Reports have one `timestamp`, with `area`, `topic`, `severity`, `repeated`, `reason` and `action`. Its meaning is undocumented. **Verified** (from code) |
| Report, confirmation and completion kept separate | **No.** One date per record. **Verified** | **No.** One timestamp per record. **Verified** |
| Matching flow history | 15-minute inflow, outflow and large-customer loggers from 1 Apr 2025. End date unknown. The publisher warns values "may be raw verified data or … corrected". **Verified** / **Unknown** | 5-minute inlet flow for 6 areas, 7.3–10.6 MB each. Span unknown. **Verified** / **Unknown** |
| Matching records to zones | Package jobs and repairs: same DMA, yes. Regional repairs: division and sub-area only, so no. **Verified** | By `area`. **Verified** (from code) |
| Access | CC BY 4.0, public, one-off extracts. **Verified** | CC BY 4.0, public GitHub. **Verified** |
| Missing operating information | Supply schedule, storage, valve log, meter-fault log. Coordinates are deliberately shifted. | Boundaries, storage, supply continuity, meter faults, units. Raw repair logs are not published, only a processed file. |
| Independence | Yes, records are separate from the flows. | Leak periods in the repository are **inferred from flow drops**, so they are not independent. Only the reports' own timestamps could be. |

**One useful extra from Wessex (Verified).** The regional data marks repairs as
*proactive*, meaning found by the company's own monitoring, or *reactive*, meaning reported
by customers. It has no times and no DMA, so it can't support a timing test.

**What each owner would need to answer.**
- **KIOS (Cyprus):** "In `data/processed_reports_data/leak_reports.csv`, what does
  `timestamp` record: the time a customer or staff member first reported the problem, the
  time a work order was created, the time the leak was confirmed, or the time the repair
  was completed? And is the date of the earliest report about the same leak kept anywhere?"
- **Wessex:** "Is `Burst_Date` the date the burst was first reported, found, or repaired?
  Is a first-report date held for these jobs?"

## 3. Recommended route

**Recommendation: ask KIOS that one Cyprus question, and keep the Rwanda utility pilot as
the real goal.**

Why Cyprus, judged on the data's design and not on any result:
- It is the only public lead whose record *might* be a report time. The `repeated` and
  `topic` fields look like a fault-report log, but that is my inference.
- It already pairs those records with an area's inlet flow.
- It is small (57 MB), openly licensed, and from the group whose LeakDB data we have
  already used carefully.

Wessex is ruled out for this question: every date it publishes is a single
job, burst or closing date.

**If KIOS says `timestamp` is a report time,** a test could honestly ask: "Do warnings come
before recorded fault reports in the same area more often than week-shifted warnings?" The
test would be:
- frozen in advance, with the shift design question from §1 settled before any data is
  seen;
- run without using the repository's flow-inferred leak periods.

**If it is a repair or closing time, or unknown,** no public route answers the question, and
a **utility partnership is needed**. The existing request already fits; no new version is
needed: [`pilot/UTILITY-REQUEST-DRAFT.md`](../UTILITY-REQUEST-DRAFT.md). It asks for repair
records with first report, confirmation and repair times kept separate. Scoring would follow
[`pilot/loop/SCORING-DRAFT.md`](SCORING-DRAFT.md), still a draft awaiting approval.

**Smallest first step.** No download. One written clarification from KIOS about one column.
Only then download the 57 MB, under a new protocol.

## 4. The single next action needed from you

**Send the KIOS question above** (§2) to the dataset maintainers, for example as an issue on
the GitHub repository or by email to KIOS. I have not contacted anyone.

## Sources

- Yorkshire: [Data Mill North dataset](https://datamillnorth.org/dataset/yorkshire-water-leakage-dma-15-minute-data-2zlgn); `analysis/yorkshire-n4/run/step4-results.json` (columns `DMA`, `Date`).
- Wessex packages: [item metadata](https://www.arcgis.com/sharing/rest/content/items/6d5a3e47147f4ebbac3115d623e7fc6e?f=json) (descriptions of flow, jobs, CUS loggers); [service schema](https://services.arcgis.com/3SZ6e0uCvPROr4mS/arcgis/rest/services/Wessex_Water_Leakage_Scenario_1_Data_/FeatureServer?f=json) (`Scenario_Jobs.Job_Date`, `Scenario_Repairs.Burst_Date`, `Flow_Pressure_15min`).
- Wessex regional repairs: [2025–26 item](https://www.arcgis.com/sharing/rest/content/items/5a18b3a990e6469ea243cf2b34e16f8c?f=json) (fields `RepairType`, `LeakageCause`, `ClosedDate`, `Division`, `SubArea`); [2020–25 item](https://www.arcgis.com/sharing/rest/content/items/72e08aa1d12e4ea2bd068bae21e423f2?f=json).
- Cyprus: [README](https://github.com/KIOS-Research/Leakage-Repairs-Dataset); [processing code](https://github.com/KIOS-Research/Leakage-Repairs-Dataset/blob/main/preprocessing/leak_detector.py) (report fields; leak periods matched to flow drops); [file list](https://api.github.com/repos/KIOS-Research/Leakage-Repairs-Dataset/git/trees/main?recursive=1).
- Rwanda: `research/loop/rwanda-utility-landscape.md`. No public Rwandan flow data or report-time records were found.
