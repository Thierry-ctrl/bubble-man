# Why does the repaired level warning stay open for 5,826 hours? — 5 October 2026

**Retrospective explanation, 2018 only.** Labelled leak flow is used here to *explain* the
excess and must never feed a live warning. No detector built or tuned; scorer untouched;
2019 not read. All earlier results preserved.

## Answer: both — in roughly equal measure

During the long alert, the sustained excess is **44% labelled leak flow and 56% other flow**,
and **either part alone would keep the unchanged warning rule open for most of the year.**

## What was compared

Hourly, on the repaired baseline (Sun–Thu / Fri / Sat, 1–14 January):

    excess    = observed (p227 + p235 − PUMP_1) − expected
    leak part = known simulated flow of the 12 labelled main-zone leaks
    remainder = excess − leak part

The baseline is learned on 1–14 January, when no labelled main-zone leak produced flow, so
by the water accounting the leak part is exactly the labelled leakage and the remainder is
**non-labelled-leak flow above the January expectation.**

**What the remainder is not.** It is not automatically customer demand. It also contains
anything the simulator does that is not a labelled leak — for example, the paper describes
pressure-dependent demand, so a large leak lowers pressure and slightly reduces what
customers receive — plus any error in the January baseline. Those were not separated here.

## When the long alert starts, and what fills it

The run begins **3 May 06:00** and never closes before the year ends (31 Dec 23:00).

| Mean, m³/h | Excess | = Labelled leak | + Remainder |
|---|---|---|---|
| 15 Jan – 3 May, before the long alert | 23.9 | 15.0 | 8.9 |
| **3 May – 31 Dec, during it** | **47.0** | **20.6 (44%)** | **26.3 (56%)** |

Share of hours *within* the long alert in which each part, on its own, exceeds the 10 m³/h
threshold: **labelled leak 74%, remainder 86%.**

By month:

| | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Labelled leak | 0.1 | 11.7 | 37.8 | 3.9 | 39.4 | 13.7 | 5.2 | 20.3 | 12.1 | 32.8 | 22.7 | 17.4 |
| Remainder | −0.1 | 2.5 | 12.3 | 15.6 | 25.0 | 30.7 | **38.0** | 29.9 | 30.6 | 24.4 | 22.6 | 9.1 |

The two parts behave differently:

- **Labelled leakage comes in bursts** around abrupt leaks (March, May, October) on top of
  a floor that keeps rising: by December, three main-zone leaks that began in 2018 are
  still running and contribute 17.4 m³/h between them.
- **The remainder follows a smooth annual curve**: about zero in January, rising to a July
  peak of 38.0, back to 9.1 by December. In mid-July the alert is held open almost entirely
  by the remainder, with labelled leakage near 5 m³/h.

The baseline itself is not biased where it was meant to fit: across 15–23 January, with no
labelled main-zone leak flow, the remainder averages **−0.06 m³/h** (95th percentile 5.2).
The growth comes after January, not from a poor fit.

Is the remainder seasonal demand? The shape is what seasonal demand would look like, and
the dataset's own README notes that the nominal weekly demand profiles it supplies "do not
capture the yearly seasonality" — implying the simulated demand has one. That is
**consistent with seasonal customer demand; it is not proof**, for the reasons above.

## The diagnostic: what if the known leak flow were not there?

Same baseline, same rule (> 10 m³/h for 6 hours), 15 Jan – 31 Dec:

| | Hours with an alert open | Runs | Longest run |
|---|---|---|---|
| As observed | **86.1%** | 42 | **5,826 h** (3 May → 31 Dec) |
| Known leak flow **subtracted** | **54.6%** | 220 | 143 h (12 → 18 Jul) |
| Known leak flow **alone** | **62.2%** | 6 | 2,817 h (5 Sep → 31 Dec) |

Removing the labelled leaks breaks the 243-day alert into many short ones — but the alert
is **still open more than half the time**. And if customer demand had matched January
exactly, labelled leakage alone would have opened a **117-day** alert from September.

## Which part of the repair caused what

The repair changed two things at once. Separating them (the one-week Friday/Saturday
variant is a **diagnostic only** — one example of each day is not a usable profile):

| Grouping | Training | Sunday 11:00 crosses | Monday 11:00 crosses | Runs | Open | Longest | Mean excess |
|---|---|---|---|---|---|---|---|
| Mon–Fri / Sat+Sun | 1 week — **old** | 100% | 0% | 129 | 78.2% | 646 h | 39.8 |
| Mon–Fri / Sat+Sun | 2 weeks | 100% | 0% | 129 | 77.8% | 646 h | 39.4 |
| Sun–Thu / Fri / Sat | 1 week — *diagnostic only* | 12% | 41% | 47 | 86.1% | 5,796 h | 40.2 |
| Sun–Thu / Fri / Sat | 2 weeks — **new** | 10% | 31% | 42 | 86.1% | 5,826 h | 39.9 |

- **The day grouping did nearly everything.** It removed the Sunday artefact (100% → 10–12%)
  and it is what turned 129 short alerts into one 243-day alert.
- **The second training week mattered little.** It eased the leftover Monday pattern
  (41% → 31%) and barely moved anything else.
- **The mean excess is about 40 m³/h in all four versions.** No baseline variant changes how
  much excess flow there is. The old baseline's over-predicted Saturdays simply punctured
  the alert once a week; the repair removed the punctures and exposed an excess that was
  there all along.

## What the next method has to address

**Both problems — and they are of similar size.**

1. **A drifting expected-flow baseline.** A static January profile falls behind as
   non-labelled-leak flow grows by up to ~38 m³/h. On its own, that keeps the unchanged rule
   open 55% of the time. Adapting naively is not an option: the earlier synthetic test showed
   an adaptive median erases a sustained change after about half its window, which would
   absorb long-running leaks as readily as demand.

2. **New leaks on top of existing losses.** Labelled leakage accumulates through the year,
   and on its own would hold an alert open for 117 days. Once an alert is open, a level rule
   cannot say when a *further* leak starts — the p673 problem, now shown to be the normal case.

The underlying difficulty is that the two look alike to a single flow meter: both are slow,
sustained rises above January. Telling them apart needs evidence that does not depend on
the excess level alone — for example the *shape* over time (a smooth seasonal curve versus a
step or ramp), or a second kind of measurement.

## Limits

- Simulated data; the remainder's composition was not separated (demand change,
  pressure-dependent interactions, model losses, baseline error).
- 2018's leaks have been examined repeatedly; this is explanation, not evaluation.
- Weekly means smooth out hourly structure; the counterfactual alert figures are hourly.

## Files

| File | Contents |
|---|---|
| `decompose.py` | Decomposition, counterfactuals, baseline variants |
| `decomposition.json` | Every number above |
| `weekly-decomposition.csv` | Weekly excess, leak part, remainder, alert-open shares |
| `plot_weekly.py`, `weekly-decomposition.png` | The chart |
