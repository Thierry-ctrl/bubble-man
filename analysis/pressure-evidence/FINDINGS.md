# Does pressure help tell a new sudden leak from an ordinary flow rise? — 4 October 2026

**Exploratory, 2018 only.** 2019 untouched. No detector built. The comparison was frozen
in `COMPARISON-FROZEN.md` and committed (`ac3d5eb`) before any outcome was examined.
Every measure is computed from readings alone; leak times were applied afterwards.

## Answer: mixed

Pressure added clear evidence in **one** of six sudden-leak cases under the pre-declared
test, and a suggestive but **post-hoc** pattern in four more. It did not meet the bar I set
in advance, and the most striking contrast turned out to be against an artefact of our own
baseline rather than against ordinary network behaviour.

## What went in

- **Sensors**: 33 in the file, complete — no gaps, no stuck readings (the organisers
  excluded sensor faults). **30 in the main zone** by the network map; Area C's three
  (n1, n4, n31) excluded. One main-zone sensor sits behind PRV-3, which holds its pressure
  near a set-point.
- **Flow rises**: hours where the flow step reached 9.10 m³/h — the threshold already frozen
  in `analysis/new-rise-realtime/` — grouped into **213 episodes**. Labelled afterwards:
  186 with no labelled new leak, 6 just after an abrupt leak, 1 after a gradual leak,
  20 unclear.
- **Two pressure measures** at each episode's peak, same windows as the flow step:
  **S**, the typical sensor's pressure fall per m³/h of extra flow; and **C**, how much more
  the worst sensor fell than the typical one, per m³/h.

## Results

| Leak | Flow rise | S pct | **C pct** | C | Pump step | Leaks already running |
|---|---|---|---|---|---|---|
| p673 | 31.9 | 78.5 | **100.0** | 0.0344 | +12.3 | 3 |
| p538 | 36.7 | 81.2 | 33.9 | 0.0034 | +4.5 | 3 |
| p866 | 30.3 | 80.6 | 37.1 | 0.0048 | +7.9 | 3 |
| p183 | 23.4 | 64.5 | 67.7 | 0.0135 | −16.9 | 4 |
| p158 | 16.6 | 38.2 | 52.7 | 0.0092 | −1.6 | 4 |
| p369 | 16.4 | 37.6 | 66.7 | 0.0128 | +13.3 | 4 |

*Percentiles are among the 186 rises with no labelled new leak. Flow rise in m³/h, C in m per m³/h.*

**Against the pre-declared criterion** — S or C placing at least 5 of 6 cases above the
90th percentile of ordinary rises — **it fails**: S places none, C places one.

### The p673 pair

Two flow rises of almost identical size, 34 hours apart:

| | Flow rise | Typical sensor | Worst sensor | Sensors falling > 0.5 m |
|---|---|---|---|---|
| 4 Mar 11:00, before onset | 31.6 m³/h | −0.16 m | −0.19 m | **0 of 30** |
| 5 Mar 21:00, after p673 began | 31.9 m³/h | −0.49 m | −1.58 m | **14 of 30** |

Before onset, pressure fell by almost the same small amount everywhere. After it, the
fall was three times larger and uneven. That is the clearest contrast in the study.

### Two confounders

**Pump operation.** Across ordinary rises, concentration rises with pump activity
(correlation with the size of the pump step, +0.35). The 25 ordinary rises with a pump step
above +10 m³/h reach C up to **0.0329**; p673, with a pump step of +12.3, scores **0.0344**.
p673 still sits above all of them, but only just. For p538 and p866 the worst sensor is
**n54, the pump's own intake** — their concentration may be the pump, not the leak.

**Overlapping leaks.** Three or four leaks were already running at every case. A pressure
change cannot be assigned to the newest one rather than a shift in one already running.

## A post-hoc pattern — and what it turned out to be

Chosen **after** seeing the chart, so not a result: restricted to rises of 20 m³/h or more,
the four comparable leaks (p673, p538, p866, p183) each exceed **every** large ordinary rise
that did not coincide with a big pump step. Large ordinary rises have C ≈ 0.001 — an almost
perfectly even pressure fall.

Checking why revealed something more important than the pattern itself.

## A flaw in our baseline: a flow rise every Sunday

**All 44 of those large ordinary rises fall on a Sunday, and 42 of them at 11:00.** They are
spread evenly across the year. Sunday-morning flow (05:00–11:00) averages **192.5 m³/h**
against Saturday's **152.7**, but Experiment A's baseline pools both into a single "weekend"
profile learned from just two January days, 13 and 14 January. Every Sunday morning
therefore looks like a sudden rise.

Consequences:

- **The large rise before p673 on 4 March is one of them** — it was a Sunday at 11:00. Its
  even pressure drop is what a demand change spread over every customer should look like.
- The post-hoc separation above is mostly pressure telling a leak apart from **this one
  artefact**, not from the full range of ordinary network behaviour. That is genuinely
  encouraging — a demand-pattern shift *is* an ordinary flow rise — but it is narrow.
- **Every flow-based result in this project so far** — level alerts, the new-rise studies,
  the p673 walkthrough — has been operating on a signal that manufactures a rise every
  week. This was not acted on here; it should be fixed before anything else is concluded.

## What this does and does not show

- Pressure **can** look different when a sudden leak starts: in p673's case, sharply so.
- Under the comparison I committed to in advance, it did **not** separate the six cases
  from ordinary rises in general.
- The two small rises (p158, p369, about 16.5 m³/h) look ordinary on both measures.
- A concentrated pressure drop says the drop is **uneven**. It does not locate a pipe,
  and nothing here should be read as one.

## Smallest sensible next step

**Fix the weekend baseline, then re-run this comparison unchanged on 2018.** Separate
Saturdays from Sundays, or learn the weekend profile from more than two days. That removes
a manufactured rise from every Sunday, leaves a more honest set of ordinary flow rises to
compare against, and tells us whether the pressure contrast survives against real
operating variation rather than one artefact. No new detector, no new threshold, and
2019 stays reserved.

## Files

| File | Contents |
|---|---|
| `COMPARISON-FROZEN.md` | The comparison, committed before outcomes were examined |
| `pressure_evidence.py` | Computes everything; labels applied in its last section only |
| `plot_pressure.py` | The chart |
| `pressure-results.json` | Counts, distributions, cases, p673 pair, pump check |
| `episodes.csv` | All 213 flow-rise episodes with their measures and labels |
| `pressure-evidence.png` | The chart |
