# Locked 2019 run — results (protocol 9724c60, revised exploratory evaluation)

*7 October 2026. One run, in the protocol's order, with no changes to the rule, baseline,
scorer, exclusions or criteria.*

> **Outcome: FAIL under the revised exploratory protocol.**
> The original 2018 noise stop failed and remains failed; in this revised protocol the
> noise measures were reported, not gating. The 2019 leak schedule was visible before this
> run (protocol §2.4); the run was blind to the 2019 readings only.

## The result in plain language

The rule raised **46 warnings in 2019** — one almost every week, nearly all on Sundays or
Mondays — against 5 in the whole of 2018. Those warnings fell within seven days of
**every one of the 8 sudden leaks**. But so did the same warning pattern moved to other
weeks: **18 of the 51 week-shifts also reached all 8.** A warning stream that arrives
almost weekly will land inside a 7-day credit window for nearly any leak, wherever the
warnings are placed. The dates did not line up with leak starts any better than chance.

For an operator, it would have meant **46 investigations**, of which **32 found no new
eligible leak** within the credit window. About **one warning in three** was associated with
a new leak, below the proposed 50% target.

The main cause is in the data, found from the 2019 readings before any leak record was
opened: **the simulated weekly demand cycle sits one day later in 2019 than in 2018.**
Every 2019 weekday's average flow shape matches the *previous* weekday's 2018 shape
(r = 1.000). The frozen baseline assigns day types by calendar date, so in 2019 it compares
Saturday-like Sundays with the weekday profile. That puts a large rise into the night
signal every week and drives the step over 10 m³/h week after week.

## Criteria

| | Criterion | 2019 | Met? |
|---|---|---|---|
| S0 | Noise — reported, **not gating** | std **17.34**, robust **16.77** m³/h (2018: 6.04, 2.98) | — |
| S1 | At least 3 eligible sudden main-zone leaks | **8** | ✓ |
| S2 | Real warnings associate at least 2 sudden leaks (full year) | **8 of 8** | ✓ |
| S3 | p_sudden ≤ 0.05 (at most 1 of 51 shifts as good) | **p = 0.365** (18 shifts reach 8) | **✗** |
| S4 | Yield ≥ 50% — *proposed operational target* | **30.4%** (14 of 46) | **✗** |

S1 met, S3 and S4 failed → **FAIL.** S2 being met carries no weight on its own: chance
placement does as well (S3).

## Warnings and workload — every warning is an investigation

| | Count |
|---|---|
| **Total warnings = investigations** | **46** |
| Associated with an eligible new leak (`credited`) | 14 |
| **Investigations without an eligible new leak** | **32** |
| — `unattributable` (a labelled leak was flowing, but not a new eligible one within 7 days) | 32 |
| — `false_alert` | 0 |
| — other categories | 0 |
| Warnings issued while a carried-over 2018 leak was flowing | 46 of 46 |
| Hours in 2019 with no labelled main-zone leak flowing (false-alert exposure) | **0** |

Zero false alerts says nothing here: a labelled main-zone leak — at least one of the three
carried over from 2018 — was flowing in every hour of the year, so a false alert was
impossible by definition.

| Month | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Warnings | 4 | 2 | 4 | 5 | 2 | 4 | 4 | 4 | 5 | 3 | 4 | 5 |
| Associated | 2 | 0 | 2 | 2 | 0 | 1 | 2 | 2 | 0 | 2 | 1 | 0 |

Weekday of the 46 warnings: **Monday 28, Sunday 18**, no other day. Gaps between
consecutive warnings: exactly 7 days in 36 of 45 cases — the 7-day spacing rule set the
pace almost every week. In 2018 it never came into play.

## Per leak

**Sudden (judged): 8 associated, 0 missed.** Median delay 92.8 h.

| Leak | Outcome | Delay from first flow | Leak nights in latest pair / in the 7 before |
|---|---|---|---|
| p523 | associated | 125.0 h | 2/2 · 4/7 |
| p827 | associated | 81.5 h | 2/2 · 2/7 |
| p710 | associated | 13.8 h | 1/2 · 0/7 |
| p514 | associated | 127.3 h | 2/2 · 4/7 |
| p331 | associated | 41.8 h | 2/2 · 0/7 |
| p142 | associated | 104.1 h | 2/2 · 3/7 |
| p680 | associated | 115.3 h | 2/2 · 3/7 |
| p426 | associated | 38.6 h | 2/2 · 0/7 |

**Gradual (reported, not judged): 6 associated, 3 missed.** Median delay 48.1 h.

| Leak | Outcome | Delay | Leak nights, latest pair / 7 before |
|---|---|---|---|
| p653 | associated | 163.3 h | 2/2 · 5/7 |
| p193 | missed | — | — |
| p586 | associated | 25.1 h | 2/2 · 0/7 |
| p721 | associated | 24.7 h | 2/2 · 0/7 |
| p800 | associated | 29.9 h | 2/2 · 0/7 |
| p123 | missed | — | — |
| p455 | missed | — | — |
| p762 | associated | 66.3 h | 2/2 · 1/7 |
| p879 | associated | 66.8 h | 2/2 · 1/7 |

**Excluded as carried over from 2018:** p427, p654, p810 (main zone). **Outside the signal:**
Area C leaks p257, p277, p280. Exactly the four leaks expected from 2018 data were flowing at
the first 2019 timestamp.

Delays and window composition are reported as context, not as evidence of cause (§2.2).
Every association had a single candidate. Many delays exceed four days: with a warning
nearly every week, the warning that falls inside a leak's 7-day window is often simply the
next weekly one.

## Comparison with shifted warnings

| | Real | 51 week-shifts |
|---|---|---|
| Sudden leaks associated | **8** | 5 in 2 shifts, 6 in 12, 7 in 19, **8 in 18** |
| All leaks associated | **14** | 13 in 3, 14 in 15, 15 in 14, 16 in 16, **17 in 3** |
| One-sided p | sudden **0.365**; all **0.942** | |

**Boundary limitation:** the first warning (6 Jan) and last (30 Dec) are 6 days apart across
the wrap point, so every one of the 51 shifts contains one pair of warnings a day closer than
the rule permits. With 46 warnings, that affects one pair per shift and cannot explain a
p-value of 0.37.

## Noise (reported, not gating)

| | 2018 | 2019 | Original cutoff | Like-for-like robust cutoff |
|---|---|---|---|---|
| Std of night-to-night change | 6.04 | **17.34** | 4.5 | — |
| Robust spread | 2.98 | **16.77** | — | 2.22 |

Basis: nights 15 Jan – 31 Dec, 350 changes, within the span only. The weekday misalignment
dominates 2019's figure. **The original 2018 noise stop failed and remains failed.**

## Run record

| Step | Commit |
|---|---|
| Protocol revision 3 (option B) — protocol ID | `9724c60` |
| Run code, verified to reproduce 2018 exactly | `fd045b4` |
| 2019 flows verified (md5 matches Zenodo, no gaps); noise recorded; weekday shift noted | `04beb0b` |
| **46 warnings committed before any 2019 leak record was opened** | `2d0671b` |
| 2019 leak records verified (md5 matches); eligible list built | `bce3b85` |
| Scoring, 51 shifts, this report | this commit |

No code defect was found. No setting was changed, and nothing was rerun.

## What this shows — and what it does not

- **The frozen night-flow step check failed on its locked test.** Under the revised
  exploratory protocol, its warning dates did not align with 2019 leak starts better than
  chance, and two thirds of its warnings would have sent a crew out without a new leak to
  find.
- **The 2018 result did not carry over.** In 2018, five widely spaced warnings beat every
  shift. In 2019, the same rule fired weekly and matched everything — and so did chance.
- **The baseline's calendar assumption did not transfer.** A profile tied to calendar
  weekdays broke when the simulated weekly cycle moved by one day. That one-day slip is an
  artefact of how the simulation repeats its demand cycle; a real network would not slip
  like this, but holidays, schedule changes or supply rotas could misalign a calendar-based
  baseline in similar ways.
- It does **not** show that night flow carries no information about new leaks, or that a
  correctly aligned baseline would fail. Neither was tested, and 2019 can no longer test
  them fairly — it has now been used.

## What would be needed next

2019 is spent for this method. Any revised design — for example, one that learns weekday
alignment from recent readings rather than the calendar — would be chosen after seeing this
failure, so it would need **new data that has played no part in its design**: another
simulated benchmark such as a LeakDB scenario, or measured data from a real network.
