# Pressure comparison — frozen before any outcome was examined

Exploratory study, **2018 data only**. 2019 untouched. Not a detector.
Committed before the analysis script was run; see git history.

## Question

When flow rises, do the pressure sensors say anything that helps tell a **new sudden leak**
apart from an **ordinary flow rise**?

## Data

- `2018_SCADA_Pressures.csv`: 33 sensors, 5-minute, complete (no gaps, no stuck sensors —
  the organisers excluded sensor faults by design).
- Zone from the network map: **30 main-zone sensors**, 3 in Area C (n1, n4, n31, excluded —
  Area C is outside the flow signal's boundary).
- One main-zone sensor sits downstream of PRV-3, which holds its pressure near a set-point.
  It is kept in the median (one of 30 cannot move a median much) and noted.

## What a live warning would calculate (no leak times, no locations)

1. **Flow-rise episodes, from flow alone.** The flow step from the earlier studies,
   `mean(diff, last 6 h) − mean(diff, the 24 h before)` on `p227 + p235 − PUMP_1`.
   Hours with a step ≥ **9.10 m³/h** — the threshold already frozen in
   `analysis/new-rise-realtime/`, from January — form episodes; consecutive hours are one
   episode. Each episode's **reference hour** is its hour of largest flow step.
2. **Pressure residual** for each main-zone sensor: hourly mean pressure minus the median
   for the same weekend/hour over **8–14 January** (same baseline construction as flow).
3. **Pressure step** for each sensor at the reference hour, using the same two windows as
   the flow step. Strictly backward-looking.
4. At each reference hour:

| Measure | Plain meaning | Units |
|---|---|---|
| `ΔQ` | how much flow rose | m³/h |
| `ΔP_med` | median pressure step across the 30 sensors — how much pressure fell overall | m |
| `ΔP_min` | the most negative single-sensor step | m |
| **`S = −ΔP_med / ΔQ`** | **overall pressure fall per unit of extra flow** | m per m³/h |
| **`C = (ΔP_med − ΔP_min) / ΔQ`** | **how much more the worst sensor fell than the typical one, per unit of extra flow** | m per m³/h |

## Expectation, stated in advance

Pressure across the main zone falls when more water flows, whatever the reason, because
pipe friction losses grow with flow. So `S` may be similar for leaks and ordinary rises.
A new leak, however, is extra outflow at **one** point; an ordinary demand rise is spread
over many customers. If pressure adds evidence, it is more likely to show in `C` — a drop
**concentrated** at some sensors rather than shared evenly.

`C` describes whether a drop is uneven. **It is not used, and must not be read, as a pipe
location.**

## Evaluation only — applied after the measures are computed

Each episode is labelled using leak information it never saw:

- **new abrupt leak**: an abrupt main-zone leak's first positive flow falls in the 12 hours
  up to the reference hour;
- **new gradual leak**: the same for a gradual leak;
- **no labelled new leak**: no main-zone leak of any kind began in the 72 hours up to the
  reference hour;
- **unclear**: anything else (a leak began 12–72 hours earlier).

Also recorded for every episode, to account for operating changes and overlap:
`PUMP_1` step (m³/h), tank level change over the recent window (m), and the number of
main-zone leaks already running.

## How the answer will be read

For each abrupt-leak episode, its percentile among **no-labelled-new-leak** episodes is
reported for `ΔQ`, `S` and `C`.

- **Adds useful evidence**: `S` or `C` places at least 5 of the 6 abrupt cases above the
  90th percentile of ordinary rises, where `ΔQ` alone does not.
- **Mixed**: some cases separate on `S` or `C` and others do not, or separation is
  explained by an operating change.
- **Adds nothing**: case percentiles on `S` and `C` look like ordinary rises.

Also: p673 is examined as a pair — the large flow rise on **4 March before its onset**,
against the rise **after** its onset.
