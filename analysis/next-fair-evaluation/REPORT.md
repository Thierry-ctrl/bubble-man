# Preparing the next fair evaluation — 7 October 2026

The 2019 night-flow failure stands exactly as reported in
`analysis/night-flow-step/RESULTS-2019.md`. Nothing here repairs it after the fact or scores a
new detector. L-Town findings below are **development work** on readings already used; they
are not validation.

## 1. What went wrong in 2019, in plain language

L-Town's simulated demand is **one year of patterns, replayed**. Each 2019 day repeats the
2018 day with the same calendar date (average daily-shape correlation 0.999), not the same
weekday (0.969). Because 2018 has 52 weeks **plus one day**, the replay lands one weekday
late: 2019's Sundays behave like 2018's Saturdays, its Saturdays like Fridays, and so on.

Our baseline expected each day to behave like its **calendar** weekday. In 2019 it compared
Saturday-like Sundays with an ordinary-weekday profile and saw a jump every week. Every week
the step crossed 10 m³/h, and the rule fired almost weekly.

A real network would not slip by exactly a day like this. But anything that changes *which
days behave alike* — holidays, a new supply rota, a school calendar, Ramadan, a market day
moving — would mislead a calendar-fixed baseline in the same way.

## 2. Two baseline ideas that use only readings available at warning time

*Development diagnostics on L-Town 2018–2019 readings; no leak labels used
(`baseline_ideas_dev.py`, `baseline-ideas-dev.json`).*

**Idea A — let each weekday choose its profile.** Keep the January profiles (Sun–Thu, Fri,
Sat) and their levels. Each day, look at the last three completed examples of the same
weekday, average their 24-hour *shapes* (scaled so level does not matter), and use whichever
January profile that shape most resembles.

**Idea B — compare with the same weekday in recent weeks.** No calendar profile at all: the
last two nights against the same two weekdays in each of the previous three weeks (median).

| | Original (calendar) | Idea A | Idea B |
|---|---|---|---|
| Spread of the step, 2018 (robust σ, m³/h) | 4.10 | 4.10 | 7.33 |
| Spread of the step, 2019 | **13.15** | **3.79** | 14.96 |
| Share of nights with step ≥ 10, 2019 | 26% | 9% | 35% |
| Days where the chosen type differs from the calendar | — | 0% in 2018, 41% in 2019 | — |
| Synthetic +20 m³/h permanent leak: nights it stays ≥ 10 | 5 | 5 | 13 |
| Day types changed by that synthetic leak | — | **0** | — |

Idea A changed nothing in 2018, where the calendar was right. In 2019 it found the slip by
itself — giving Sundays the Saturday profile and Saturdays the Friday profile — and the
step's spread returned to 2018's level. Idea B is calendar-free but noisier.

### Could an adapting baseline absorb a long-running leak?

- **Idea A: low risk for a steady leak.** It adapts only the *label*, judged by daily
  *shape*. A constant extra flow does not change shape, and the synthetic leak changed no
  label. The profile *levels* stay frozen from January, so nothing drifts up to meet a leak.
  Remaining risks: a leak whose flow varies through the day (real leaks respond to pressure,
  which is higher at night) slightly changes shape; a week that resembles none of the three
  January patterns gets the least-bad one; a change in weekly pattern takes three weeks to
  be recognised; and an intermittent supply schedule would break the shape matching
  entirely.
- **Idea B: real risk.** Its reference is the last three weeks, so a steady leak becomes
  "normal" after about **two weeks** (13 nights in the synthetic test). That is tolerable for
  spotting a *new* leak, but a leak repaired inside the reference weeks can hide a new one —
  the cause of two of the 2018 misses.

**Proposed: Idea A.** It addresses the 2019 failure without letting levels adapt.

## 3. Candidate datasets for an untouched test

| Dataset | What it is | Flow/pressure time series | Leak start times | Network map | Events | Different from L-Town? | Verdict |
|---|---|---|---|---|---|---|---|
| **LeakDB — Hanoi** (Zenodo 13985057) | Simulated; same team as BattLeDIM | Every link's flow, every node's pressure, 30 min, 1 year per scenario | Yes, per leak (start, type, size) | Yes (`.inp`) | 500 scenarios in the original paper; 0–2 leaks each | **Different network** (31 junctions, one reservoir, no storage) and **different demand realisation** (exact weekly cycle × yearly curve × noise, re-randomised per scenario; pipe parameters ±25%). **Same modelling family.** | **Best available** |
| LeakDB — Net1 | As above | As above | Yes | Yes | As above | Different network, but a pump and tank complicate the inlet signal | Second choice |
| LeakG3PD (GitHub) | "An updated and improved version of LeakDB" | Pressures, demands; Google Drive | Yes | Yes | Many scenarios | Same generator lineage as LeakDB; adds node-level demand shifts and Net3 | Not independent of LeakDB |
| Mazaev et al. (Zenodo 7255403) | **Real** operational network in Belgium ("BKTown"), controlled hydrant leaks, plus simulated scenarios | **Pressure only**: mobile loggers 8 Jul – 17 Nov 2020 and 8 Dec 2020 – 15 Feb 2021; **no flow meter** in the raw data | Two experiment files of ~400 bytes each (not opened) | Yes (calibrated and uncalibrated `.inp`) | A handful of controlled leaks | Genuinely different and real | Unsuitable for a flow method; a candidate later for pressure work |
| Slovak utility (Zenodo 15096167) | Real utility | **Anomaly scores only**, not raw flow; flow and pressure dropped by the authors | ±7-day windows | No | Few | Real, but unusable for this method | Unsuitable |
| Lab testbed (Mendeley tbrnp6vrnj) | 47 m PVC rig | 30-second acoustic and pressure snapshots | Controlled | — | 280 snapshots | No long time series | Unsuitable |
| BattLeDIM L-Town | Simulated | — | — | — | — | Used in 2018 and 2019 | Spent |

**Independence, plainly:** LeakDB is the most different dataset available with what this
method needs, but it is **not independent in method**: the same research group, the same
kind of simulated leak, pressure-driven demand, and no sensor faults. It tests whether the
idea transfers to another network and another demand realisation — not whether it works on
real pipes.

**Practical limits found:**
- The public repository holds only **10 Hanoi scenarios with 9 leaks** — too few. The full
  archive is a single **13.9 GB** download.
- Listing those 10 scenarios' file names revealed their leak count, and LeakDB file names
  contain leak node IDs. So the test **excludes scenarios 1–10** and **never lists** the full
  archive.
- LeakDB leaks are **never repaired** and hole sizes run 0.02–0.2 m. On a 5,500 m³/h network
  that is roughly 0.4% to 40% of demand. Many will be easy. And the weekly cycle never slips,
  so Idea A's repair is not exercised.

## 4. Recommendation

**Use LeakDB Hanoi as the next testbed**, with the experiment in `EXPERIMENT-TO-FREEZE.md`
approved and committed before any leak record is opened. Treat a pass as "promising under an
exploratory transfer test", and a fail as decisive for this idea.

It cannot replace real data. For the question that matters in Rwanda, the smallest real-utility
request is unchanged in spirit from the input audit, made specific:

1. **Inlet flow** for one zone with known boundaries, every 15 minutes or finer, for at
   least **12 months**, with pump, valve and supply-schedule logs.
2. **Repair and work-order records** for that zone over the same period, each with the time
   the leak was first reported, confirmed type, and location — at least **10 confirmed new
   leaks**, plus records of visits that found nothing.
3. For long-standing losses (a separate job): customer consumption for the same zone —
   monthly billing for all accounts, and hourly readings from a sample.

## 5. The next experiment — summary

Fully specified in `EXPERIMENT-TO-FREEZE.md`:

- LeakDB Hanoi, every scenario numbered 11 and above; **only the inlet flow file read**
  before warnings are committed.
- Idea A baseline learned per scenario from days 1–14; night window from those days; step =
  last 2 nights vs the 7 before; threshold **4 × robust σ** of days 9–28; warnings from
  day 29; re-arm and 7-day spacing as before.
- Existing scorer unchanged; abrupt leaks judged, gradual reported; every warning counted as
  an investigation; false alerts measurable for the first time.
- **47 pooled whole-week shifts**; pass needs ≥ 20 eligible abrupt leaks, p ≤ 0.05, and yield
  ≥ 50% (a proposed target).
- Warnings committed before leak files are extracted. One run; no reruns.

## Sources

- LeakDB: [Zenodo record 13985057](https://zenodo.org/records/13985057) (metadata: 13.9 GB,
  CC BY 4.0); [GitHub, KIOS-Research/LeakDB](https://github.com/KIOS-Research/LeakDB)
  (generator code `leakDataset.py`, `demandGenerator.py`, `Hanoi_CMH.inp`);
  [original paper, WDSA/CCWI 2018](https://ojs.library.queensu.ca/index.php/wdsa-ccw/article/download/12315/7911/23124)
  (saved as `research/2026-10-07/leakdb-wdsa-ccwi-2018.pdf`).
- LeakG3PD: [GitHub, matheuspilotto/LeakG3PD](https://github.com/matheuspilotto/LeakG3PD).
- Mazaev et al.: [Zenodo record 7255403](https://zenodo.org/records/7255403) (archive downloaded to a
  scratch folder, md5 matched, file names listed; no file opened);
  [paper, Water Supply 2023](https://iwaponline.com/ws/article/23/1/162/92471/Probabilistic-leak-localization-in-water)
  (publisher page refused automated access).
- Slovak utility: [Zenodo record 15096167](https://zenodo.org/records/15096167).
- Laboratory testbed: [Data in Brief / PMC10147960](https://pmc.ncbi.nlm.nih.gov/articles/PMC10147960/).
