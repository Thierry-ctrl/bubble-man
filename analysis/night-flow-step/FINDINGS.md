# Night-flow step check — 6 October 2026

**2018 development test.** These leaks have been examined many times, and this method was
designed after a diagnostic showed night flow tracks 2018 leakage. Nothing here is a
performance claim. 2019 sealed; the generation model not read. Rule frozen and committed
(`b944498`) before any check or scoring; scorer unchanged.

**Scope: finding an additional new leak only.** This method cannot measure losses that
have been present for months.

## Short answer

- **Evidence beyond chance: yes, by the test set in advance** — the five real warnings beat
  every one of the 49 whole-week shifts on sudden leaks (one-sided p = 0.02, the smallest
  value 49 shifts allow).
- **Workload: very light** — 5 warnings in 351 nights, about one every ten weeks.
- **But it tripped one of its own stop conditions** (night-to-night noise), and it **missed
  half the sudden leaks**, every time because another leak was changing at the same moment.
- **Worth a locked 2019 evaluation: yes in principle — the first candidate in this project
  that is.** Two things should be settled first (below), and 2019 stays sealed until you
  decide.

## 1. Noise check, from readings alone (pre-declared, reported first)

| | Value |
|---|---|
| Night-to-night change, standard deviation, full window | **6.04 m³/h** |
| Pre-declared stop limit (2 × January's 2.25) | 4.5 m³/h |
| **Stop condition** | **triggered** |
| Robust spread of the same changes (IQR / 1.349) | 2.98 m³/h |
| Share of total variance from the 10 largest of 350 changes | **65%** |
| Missing nights | 0 |

The stop fired. Its cause is a handful of very large jumps rather than generally noisy
nights: the middle 90% of changes lie between −6.3 and +4.9 m³/h, but the extremes reach
−26 and +20. Looked at afterwards, the largest jumps line up with leak onsets and repairs —
the events the method is meant to see. In hindsight, a standard deviation was the wrong
statistic for this stop, because it is inflated by the signal itself. **That is a post-hoc
reading. The pre-declared condition fired and is recorded as fired.**

## 2. The warnings

Five warnings: **3 Feb, 6 Mar, 11 May, 8 Aug, 6 Oct**, each issued at 04:00.

| Month | Warnings | Associated with a leak | Not associated |
|---|---|---|---|
| Feb | 1 | 1 | 0 |
| Mar | 1 | 1 | 0 |
| May | 1 | 0 | 1 |
| Aug | 1 | 1 | 0 |
| Oct | 1 | 1 | 0 |
| All other months | 0 | 0 | 0 |

The one-per-week cap never came into play — the closest two warnings are more than five
weeks apart. The low count comes from the threshold and the re-arming rule, not the cap. A
light workload is a fact of 2018, not proof that the workload would be acceptable elsewhere.

**The one unmatched warning (11 May)** fired while the gradual leak p628 was growing, 8.4
days after it began — just outside the 7-day credit window. A labelled leak was running,
so it is `unattributable`, not a false alert. False alerts: **0**, but 2018 offers almost no
hours without a labelled main-zone leak, so that zero says little.

## 3. Per leak

| Leak | Type | Outcome | Delay from first flow |
|---|---|---|---|
| p673 | abrupt | **associated** | 12.3 h |
| p538 | abrupt | missed | — |
| p866 | abrupt | missed | — |
| p183 | abrupt | **associated** | 25.4 h |
| p158 | abrupt | **associated** | 1.4 h |
| p369 | abrupt | missed | — |
| p232 | gradual | associated | 72.3 h |
| p461, p427, p628, p654, p810 | gradual | missed | — |

**Sudden leaks: 3 of 6. Gradual: 1 of 6** (p232 ramps unusually fast). Median delay 18.8 h.

The 1.4 h delay for p158 is genuine: the leak began at 02:35, inside the 02:00–04:00 night
window, was flowing for 71% of it, and lifted night flow from 29.1 to 47.4 m³/h. The warning
went out at 04:00, the first moment all readings were in.

### Why three sudden leaks were missed — the same cause each time

Looked at afterwards, using leak records:

- **p538** produced the **largest step of the year (+42.6 m³/h)** — but the rule was
  **disarmed**. The 11 May warning had left the step above 10 every night since, so the rule
  never re-armed before p538 began.
- **p866** began **as p538 was being repaired**. One leak stopped while a smaller one
  started, so night flow fell and the step was negative throughout.
- **p369** began **three days after p158 ended**. The new leak brought night flow back to
  about where p158 had held it, so compared with the previous week little had changed
  (best step +6.7).

None of these is a threshold problem. Each is the step-versus-last-week design meeting
**overlapping leaks** — another leak starting, ending or growing within the comparison
window. In a network where leaks overlap most of the time, that limit is structural.

## 4. Against warnings placed at random

The real warnings, moved forward by whole weeks and wrapped around a 350-night domain
(15 Jan – 30 Dec, exactly 50 weeks). That gives **49 distinct shifts** — not 300; there are
only 49 different ways to shift a pattern by whole weeks within 50 weeks. Each keeps the
number of warnings, the day of week, the 04:00 issue time and the spacing. No wrapped
shift put two warnings closer than 7 days.

| | Real | 49 shifts |
|---|---|---|
| Sudden leaks associated | **3** | 0 in 25 shifts, 1 in 21, 2 in 3 — **never 3** |
| All leaks associated | **4** | 0 in 14, 1 in 20, 2 in 10, 3 in 5 — **never 4** |
| One-sided p-value | **0.02** (sudden), **0.02** (all) | |

Pre-declared pass: beat at least 47 of the 49 shifts on sudden leaks. **It beat all 49.**

How much weight this carries:
- **0.02 is the floor.** No result from 49 shifts can do better, and the shifts are one
  pattern moved through the year, not independent trials.
- **Three associations is a small count.** One fewer and the picture would be ordinary.
- **The idea was motivated by 2018 data.** The input audit found night flow tracks 2018
  leakage before this rule was written. A clean test needs data that played no part in
  designing it.
- **Boundary limit:** the 31 December night falls outside the whole-week domain. No warning
  fell on it, so the full-window and domain results agree.

## 5. Is it worth a locked 2019 evaluation?

**Yes in principle.** It is the first method in this project to beat its own random
comparison under a test fixed in advance, with a workload of a few warnings a year. It
answers the job it was built for — a new sudden leak — and the misses have a clear,
understood cause.

Two things to settle **before** opening 2019, both decisions rather than analyses:

1. **The noise stop.** It fired. Either it stands, and the method is dropped, or it is
   formally replaced by a robust spread statistic **before** 2019 is seen, recorded as a
   post-hoc amendment with the reason above. That is your call; I recommend replacing it,
   openly labelled, because the original statistic measures the signal as much as the
   noise.
2. **The full 2019 protocol, written and committed first:** rule and scorer unchanged;
   the 2019 domain and number of distinct shifts; the pass criterion; what counts as a
   sudden leak; how 2018's long-running leaks carried into 2019 are treated. No 2019
   reading until that is frozen.

**This result is not permission to open 2019.**

## 6. If 2019 is not approved — smallest next step

Look at the overlap problem directly, without new leaks: count, for each 2018 sudden leak,
whether another main-zone leak started, ended or was still growing within the 9-night
comparison window, and whether that predicts the misses. If overlap explains them, the next
design question is how to compare against a reference that excludes a recent change — which
is a design question, not a tuning exercise.

## Limits

- Simulated data; sensor faults and delays excluded by the organisers.
- Night-flow reasoning fails under intermittent supply, where household storage refills
  overnight — the expected situation in Rwanda.
- Associations are timing matches; no pipe is located, and in most cases other leaks were
  running.

## Files

| File | Contents |
|---|---|
| `RULE-FROZEN.md` | Exact rule, timing and edge cases, committed first |
| `night_signal.py` | Night residual and step, readings only |
| `noise_check.py`, `noise-check.json` | Full-year noise check |
| `run_night_step.py` | Warnings, scoring, the 49 shifts |
| `night-step-results.json` | Every number above |
| `per-leak.csv`, `warnings.csv`, `shifts.csv` | Traceable detail |
