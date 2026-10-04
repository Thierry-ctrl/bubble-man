# Repairing the weekend baseline — 4 October 2026

**Exploratory.** These 2018 leaks were examined before; nothing here is a performance claim.
2019 not read. Replacement frozen in `BASELINE-FROZEN.md` (`d804f2c`) before the rerun.
Warning rules, scorer and pressure measures unchanged. All earlier results preserved.

## Short answer

The repair **fixes the Sunday artefact** — and in doing so shows that some of what looked
like detection was that artefact. It does **not** produce a working detector:

- the level warning now stays open for almost the whole year and credits only 3 leaks;
- the new-rise rule fires less, reaches the same abrupt leaks, and is clearly **faster** than
  random warnings — but still no better than random at **which** leaks it reaches;
- pressure, under the frozen comparison, adds nothing beyond what flow now shows on its own.

## 1. The Sunday problem, confirmed from raw readings

- **Saturday is the unusual day, not Sunday.** 2018 hourly means at 07:00: weekdays 194.0,
  Sunday 198.0, Saturday 130.4 m³/h. Daily means: weekdays 176.6, Sunday 175.6,
  Saturday 165.2.
- The old baseline learned "weekend" from one Saturday and one Sunday and averaged them. At
  07:00 that gave 127.6 — 30 below that Sunday, 30 above that Saturday.
- So every Sunday morning looked high and every Saturday looked low. The 11:00 Sunday step
  compares Sunday morning (mean residual +65.1) against a window full of Saturday (+29.8):
  a mean step of **+35.3 m³/h**. **All 50 Sundays crossed the 9.10 threshold.**
- **Not the pump.** At 07:00 main-zone outflow differs by 67.6 m³/h between Saturday and
  Sunday; pump flow differs by 1.6. The main-zone signal already subtracts the pump.

## 2. The replacement

From 1–14 January only, every day of the week repeats closely across its two examples (RMS
2.1–3.6 m³/h). Sunday–Thursday cannot be told apart (2.9–3.6 from the rest); **Friday (16.4)
and Saturday (25.6) can.** Frozen baseline: Sun–Thu / Fri / Sat, medians over 1–14 January,
static. Friday and Saturday rest on **two days each** — repeatable in January, unknown in
summer. An adaptive alternative was rejected: in a synthetic test it erased a sustained
+20 m³/h step after about half its window (10 days for a 2-week window, ~18 for 4 weeks).

## 3. Before and after

Both baselines ran through the same code; the old one reproduced the saved results exactly
(129 level alerts, 9/12, 55.75 h; 184 new-rise warnings, 12/12; 213 pressure episodes).

**Sunday artefact**

| | Old | New |
|---|---|---|
| Sunday 11:00 steps ≥ 9.10 | **50 of 50** | **10%** |
| Level alerts starting on a Sunday | 24 | 5 |
| New-rise warnings on a Sunday | 39 | 10 |
| Large "ordinary" flow rises (≥ 20 m³/h) | 44, all Sundays | **0** |
| Step at Sun 4 Mar 11:00 — the "rise before p673" | +31.6 | **−0.7** |

The large rise before p673, used in the walkthrough and the pressure study as an ordinary
rise, **was the artefact.** It no longer exists.

**Not fully clean:** share of 11:00 hours crossing 9.10, Monday to Sunday — old 0/46/16/22/
0/0/100%, new **31**/24/4/8/4/2/10%. Monday rises from 0% to 31%: Sunday afternoons run a
few m³/h lower than weekdays (mean residual 40.0 vs 44.6), which January's data was too
short to separate. A smaller weekly pattern remains.

**Level warning (difference > 10 m³/h for 6 h)**

| | Old | New |
|---|---|---|
| Alert runs | 129 | **42** |
| Share of hours an alert is open | 78.2% | **86.1%** |
| Longest run | 646 h | **5,826 h (~243 days)** |
| Leaks associated | 9 / 12 | **3 / 12** |
| — abrupt / gradual | 3 / 6 | **0 / 3** |
| Median delay | 55.8 h | 65.3 h |
| Random, free rotation (median / 95th) | 10 / 12 | 2 / 4 |
| Random, whole-week rotation (median / 95th) | 10 / 12 | 2 / 4 |

This looks like a collapse. It is mostly the removal of manufactured credit. A leak can
only be credited to an alert that **starts** after it. The old baseline's weekly Saturday
dip kept closing alerts and reopening them, giving every leak a fresh start to attach to —
3 of the old 9 credits came from runs that restarted on a Sunday. With the dip gone, the
alert opens in spring and **stays open until December**. Every abrupt leak began while it
was open. Neither version beats randomly-timed warnings.

The deeper reason is not weekends: a static January baseline sits below summer demand, so
the level warning is open nearly all the time. **As a detector on this baseline, it is not
usable.**

**New-rise rule (step ≥ 9.10 while a level alert is open)**

| | Old | New |
|---|---|---|
| Warnings | 184 | **129** |
| Per week of open alert | 4.69 | **2.99** |
| Leaks associated | 12 / 12 | 10 / 12 |
| Abrupt | 6 / 6 | **6 / 6** |
| The three the old level rule missed (p538, p866, p158) | all three | **all three** |
| Median delay | 15.2 h | **14.7 h** |
| Random, same hours (300 runs): leaks, median / 95th | 11 / 11 | 10 / 11 |
| Random: runs reaching 6/6 abrupt | 100% | **98.3%** |
| Random: median delay | 26.2 h | 35.0 h |
| Random: runs as fast as the real rule | 4.3% | **0.3% (1 of 300)** |

Fewer warnings, same abrupt leaks, and warnings arrive **much sooner** than randomly
placed ones — sooner than 299 of 300 random runs. But random placement still reaches 6/6
abrupt leaks 98% of the time, so the rule is no better at **which** leaks it reaches. Against
the criteria frozen in `analysis/new-rise-realtime/RULE-FROZEN.md` it still fails two of
three: it does not beat random on leaks reached, and 2.99 warnings per week exceeds the
budget of about 2. The timing result is the one genuinely stronger finding — from one of
many comparisons on already-studied data, so a lead, not a result.

(Sensitivity only, not used: re-applying the rule's calibration formula to the new baseline
would give a threshold of 4.43, not 9.10, because the new baseline fits January better.)

**Pressure study — frozen measures and criterion**

| Case | Flow-rise pct | S pct | C pct |
|---|---|---|---|
| p673 | **100.0** | 52.3 | 86.9 |
| p538 | **100.0** | 26.2 | 63.1 |
| p866 | **100.0** | 70.0 | 62.3 |
| p183 | **100.0** | 74.6 | 63.8 |
| p369 (first episode) | 10.0 | 0.0 | 70.0 |
| p369 (second episode) | 93.8 | 36.9 | 65.4 |

*Percentiles among 130 flow rises with no labelled new leak (old: 186).*

Criterion — at least 5 of 6 above the 90th percentile on S or C: **old 0 on S, 1 on C;
new 0 on S, 0 on C. Not met either way.** p673's concentration falls from the 100th to the
87th percentile: its earlier distinction was partly against an artefact rise.

The striking change is in the flow column. With the Sunday rises gone, **the flow step
alone places the four larger abrupt leaks above every flow rise with no labelled new leak.**
Pressure, measured this way, adds nothing on top. That is a flow result, observed
retrospectively on leaks already studied — it does not mean the flow step works as a live
warning, which section 3's new-rise results already tested.

Two quirks of the frozen labelling rule, reported rather than adjusted: **p158** has a clear
flow rise (22.8 m³/h) but it peaks 12.4 h after onset, 25 minutes outside the 12-hour window,
so it is labelled "unclear" and is not a case; **p369** produces two qualifying episodes and
is counted twice.

## 4. False alerts

The 215 hours from 15–23 January contain no labelled main-zone leak flow. A level alert was
open in **none** of them under either baseline. The level rule raised 1 (old) and 0 (new)
warnings there — counts over 215 hours, not a rate. The new-rise rule cannot fire without an
open alert, so its count there is 0 by construction and says nothing. No reliable false-alert
rate can be stated from 2018.

## 5. Does the repair help?

**Yes as a measurement repair; no as a detector repair.** It removed a manufactured weekly
rise, corrected the story of p673, and stopped the level rule from collecting credit the
artefact had been handing it. It made the new-rise rule quieter and faster without losing
any abrupt leak. It did not make either rule beat random warnings at choosing leaks, and it
did not make pressure useful under the measures already frozen.

## 6. Limits

- Exploratory: every leak here was examined before this baseline was designed.
- Friday and Saturday profiles rest on two January days each; a smaller weekly pattern
  remains (Monday 31%).
- Seasonal drift is untouched and now dominates: an alert open 86% of the time.
- Timing matches are associations. The signal names no pipe, and three or four leaks were
  running at every case.

## 7. Smallest sensible next step

**Separate seasonal drift from accumulated leakage before changing any rule.** Compare the
weekly mean residual under the new baseline against the labelled leak flow, for evaluation
only. If most of the year-long alert is seasonal demand, the problem is the baseline's
anchoring to January. If most is accumulated leakage, the alert is *correct* and the
real question is how to warn about a *new* leak on top of old ones. Those point to very
different next designs, and 2018 can answer which one we face without building anything.

## Files

| File | Contents |
|---|---|
| `diagnose_sunday.py`, `sunday-diagnosis.json` | The raw-reading diagnosis |
| `BASELINE-FROZEN.md` | Replacement, committed before the rerun |
| `rerun_with_new_baseline.py` | Old and new through identical code, with reproduction checks |
| `before-after.json` | Every number above |
| `pressure-episodes-old.csv`, `pressure-episodes-new.csv` | All pressure episodes, both baselines |
| `plot_before_after.py`, `before-after.png` | The chart |
