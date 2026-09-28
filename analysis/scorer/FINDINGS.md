# What the scorer found — 29 September 2026

Development experiment on simulated L-Town 2018 data. **Not evidence that anything works
in Rwanda, or anywhere.** 2019 was not touched.

## The headline: we cannot yet show these methods beat guessing

At the reference setting (threshold 10 m³/h, 6 hours' persistence, 7-day deadline):

| Method | Alert events | Leaks matched | Abrupt | Gradual | Unnecessary warnings/week | Median delay |
|---|---|---|---|---|---|---|
| Frozen training week | 244 | 12 / 13 | 5/6 | 7/7 | 3.87 | 14.9 h |
| Rolling 14 days | 53 | 6 / 13 | 4/6 | 2/7 | 0.38 | 9.9 h |
| Night only, rolling | 1 | 1 / 13 | 1/6 | 0/7 | 0.00 | 12.3 h |

**12 of 13 looks excellent. It is not.** We rotated each method's warnings to random
times — keeping the number and length of alerts identical, destroying only their
relationship to the leaks — and scored them again:

| Setting | Real | Random (median) | Random 95th pct | Verdict |
|---|---|---|---|---|
| frozen, 10 / 6 | 12 | 13 | 13 | **worse than chance** |
| frozen, 20 / 3 | 13 | 13 | 13 | no evidence |
| frozen, 20 / 24 | 7 | 5 | 7 | no evidence |
| rolling, 10 / 6 | 6 | 4 | 7 | no evidence |
| rolling, 20 / 3 | 6 | 3 | 5 | marginal |

Only one cell puts the real result above the random 95th percentile, and barely.
**Across the declared grid, these methods show no convincing evidence of detecting leaks
better than randomly-timed warnings at the same rate.**

## Why the naive version of the score was meaningless

In 2018 a leak is running **100% of the hours**, median four at once, maximum six. Under
the BattLeDIM paper's rule — a detection counts any time inside a leak's life — a warning
essentially cannot fail to match. Our first run duly reported 13/13 matched and **zero**
unnecessary warnings at almost every setting. That number measured how often we warned,
not whether we were right.

Adding the 7-day deadline is what made false alarms visible at all.

## What about the rolling baseline absorbing gradual leaks?

Directionally consistent, **not established.** Frozen matched 7/7 gradual leaks against
rolling's 2/7 — but frozen also fired 244 alerts to rolling's 53. At more comparable
alert rates (frozen 45 events vs rolling 53) the gradual counts are 3/7 and 2/7, well
inside chance variation. The earlier finding that a rolling baseline flattens across
growing leakage still stands on its own evidence; this scorer neither confirms nor
refutes it.

## Leaks and their outcomes

13 of the 14 known 2018 leaks are eligible. `p257` is excluded because it began on
8 January, before the evaluation window opened on 15 January — we never saw its onset.
Four leaks (`p257`, `p427`, `p654`, `p810`) run past 31 December and are flagged as
censored. Per-leak and per-event tables are in `leak-outcomes-*.csv` and
`alert-events-*.csv`; every summary number traces back to those rows.

## Limitations

- Simulated data. The organisers deliberately excluded sensor faults and time delays.
- One flow meter (`p227`) of three. No pressure sensors used.
- **No threshold has been chosen.** Our existing scripts emit differences, not warnings;
  the grid is illustrative and no cell is "our detector".
- Matching is by time only. No alert names a pipe, so no match is proof of detection.
- These are development-period numbers on leaks we can see. They are not performance.

## One recommended next experiment

**Use more than one meter before tuning anything.** We have used `p227` and ignored
`p235` and `PUMP_1`. The cheapest real test of whether there is any signal here is to
require two meters to move together before warning, then re-run this scorer — including
the random-rotation check — and see whether the result finally separates from chance.

Stop condition: if requiring agreement across meters still cannot beat randomly-timed
warnings, then flow alone at this network's scale is not a sufficient input, and the
next step is pressure data rather than better thresholds.
