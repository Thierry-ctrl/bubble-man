# What live information could separate demand changes from sustained leakage? — 5 October 2026

2018 only; 2019 sealed. No detector built or tuned. Leak records were used **only** in
checks marked *retrospective*, never to choose an input or a threshold. The simulator's
generation model (`L-TOWN_Real.inp`) was not used.

## Short answer

**In the main zone, the current measurements cannot fully separate seasonal demand from
persistent leakage. In Area C, they can.** The difference is customer meters: Area C has
82, the main zone has none.

- Night flow narrows the confusion a lot, but leaves seasonal night use of up to **14 m³/h**
  in July — larger than several leaks.
- Area C's meters predict the *shape* of the main zone's extra demand well, but get its
  *size* wrong by about 30%, and nothing available in 2018 can correct that without leak
  records.

So of the two jobs below, **finding an additional new leak** can be tested credibly;
**investigating losses present for months** in the main zone cannot, until a utility
provides customer consumption for that zone.

## Two different jobs

| | Finding an additional new leak | Investigating losses present for months |
|---|---|---|
| Question | Did something change in the last day or two? | How much water is being lost, persistently? |
| Timescale | hours to days | weeks to months |
| What confuses it | daily and weekly demand patterns | seasonal demand drift |
| What it needs | a signal quiet enough to show a step | an independent estimate of demand |
| Testable now in the main zone? | **Yes** — a step over days is insensitive to slow drift | **No** — no independent demand estimate |
| Testable now in Area C? | Not attempted | **Yes** — water balance, below |

## Input audit

| Input | Covers main zone? | Independent of inlet flow? | What it can tell us | Uncertainty that remains |
|---|---|---|---|---|
| Inlet flow `p227 + p235 − PUMP_1` | Yes — defines it | — | Total demand + leakage | Cannot split the two; averaging semantics assumed |
| Night flow (02:00–04:00) | Yes | No, same meters — but samples the lowest-demand hours | Tracks labelled leakage closely (weekly r = 0.95, retrospective; daytime 0.75) | Seasonal night use up to 14 m³/h; Saturday early mornings run 74 vs 53 m³/h; invalid under intermittent supply |
| Pressure (30 main-zone sensors) | Yes | Partly — but responds mainly to total flow | A drop's size and evenness | Added nothing under the frozen measures; PRV set-points and pump operation move it; no sensor faults simulated |
| Pump flow `PUMP_1` | Boundary only | — | Needed to subtract the transfer to Area C | Driven by Area C demand and leaks |
| Tank level `T1` | No (Area C) | Yes | Area C storage change | Recorded to 0.01 m: ~2 m³/h accuracy hourly |
| **Customer meters (82)** | **No — all 82 in Area C** | **Yes** | Area C water balance; a demand reference for the main zone | Main-zone size of effect uncalibrated; 10 Area C nodes unmetered |
| Calendar | Yes | Yes | Weekly structure (Friday and Saturday distinct) | No holiday effect found; season not identifiable from the calendar alone |
| Nominal network model `L-TOWN.inp` | Yes | Yes (prior information) | Zones, sensor and meter locations, nominal demands | README: weekly patterns "do not capture the yearly seasonality"; parameters ±10%; valve status uncertain |
| *Leak flows, leak locations, generation model* | — | — | **Not inputs.** Retrospective checks only. | — |

## Diagnostics

`diagnostics.py` resolves three specific uncertainties.

**D1 — Do Area C's meters isolate losses?** Area C inflow (pump flow minus tank storage
change) minus metered consumption:

| m³/h | Jan | Mar | Jun | **Jul** | **Aug** | Oct | Dec |
|---|---|---|---|---|---|---|---|
| Inflow − metered | 6.41 | 8.56 | 8.78 | **13.97** | **14.70** | 8.64 | 8.52 |
| *Labelled Area C leak (retrospective)* | 4.74 | 6.74 | 6.73 | 11.84 | 12.70 | 6.74 | 6.74 |

Weekly correlation **0.999**, with a near-constant gap of about **1.9 m³/h** — already 1.7 on
1–7 January, before any Area C leak. That gap is the **10 unmetered Area C nodes**, which
the nominal model gives about 10% of Area C's demand. **Where customers are metered, a
water balance measures persistent losses almost exactly** — less whatever is unmetered.

**D2 — Can Area C's meters stand in for main-zone demand?** Area C metered demand relative
to its January expectation rises from 1.08 (Jan) to **1.38 (Jul)** and back to 1.09 (Dec).
Applying that index to the main zone's January expectation:

- tracks the main-zone remainder with weekly r = **0.82** and explains **62%** of its
  variation (retrospective);
- but predicts 27.0 m³/h of extra demand on average against a remainder of 20.6 —
  **about 30% too large**;
- after subtracting it, the excess tracks labelled leakage better (r 0.82 → **0.92**).

Real information, wrong scale. The main zone's demand evidently varies less with the
seasons than Area C's — plausibly a different mix of customers. The scale **cannot** be
calibrated from 2018 live data: the only period without labelled main-zone leaks is
January, which has almost no seasonal variation.

**D3 — Does night flow separate leakage from demand?** Main-zone excess at 02:00–04:00
against labelled leakage (retrospective):

| m³/h | Feb | Apr | Jun | **Jul** | Sep | Nov | Dec |
|---|---|---|---|---|---|---|---|
| Night excess − labelled leak | −1.2 | 5.6 | 11.2 | **14.4** | 13.2 | 11.0 | 4.5 |

Night flow cuts the non-leak excess from ~26 m³/h (daytime) to ~8 on average — but it rises
seasonally, because customers' night use rises too (Area C's metered night demand is 69%
above January in July). Night flow is also not naturally quiet: night-to-night changes have
a standard deviation of **10.3 m³/h**, because Saturday early mornings run far higher.
Against the day-type baseline, that falls to about **2.3 m³/h** (9 out-of-sample nights —
a thin estimate).

## What this means

**Persistent losses in the main zone smaller than roughly 10–15 m³/h cannot be told apart
from seasonal demand with these inputs.** That is not a modelling failure; the information
is not there.

But a **new** leak appears as a *step* in night flow over a day or two, while seasonal night
use drifts by about 0.7 m³/h a week. Against night-to-night noise of ~2.3 m³/h, a step of
10 m³/h should stand out. That is the job the available data can test.

## Smallest data request for a real utility

To make long-standing losses separable in a zone like L-Town's main zone:

1. **Customer consumption for the same zone as the inlet meter** — billing totals for all
   accounts, at least monthly, plus hourly or daily readings from a sample of smart meters
   or the largest users. This is the single item that changes the answer: D1 shows a
   metered water balance isolates losses almost exactly.
2. **A short night-use survey or step test** for the zone, so legitimate night consumption
   is measured rather than assumed.
3. **An operations log** — pump and valve changes, supply interruptions, and under
   intermittent supply the **supply schedule**, since refilling household storage at night
   breaks night-flow reasoning.

## Recommended next experiment: a night-flow step check for new leaks

*Specified here, not run.*

**Inputs (live only).** Main-zone outflow `p227 + p235 − PUMP_1`, mean over 02:00–04:00
each night, minus the frozen day-type January baseline.

**Measure.** `night step = mean of the last 2 nights − mean of the 7 nights before`.
Strictly backward-looking; available at 05:00 after the second night.

**Flag.** Step ≥ **10 m³/h** — declared as an operational "smallest new loss worth a visit",
the same size as the existing level threshold, and about four times January's
night-to-night noise (a thin estimate). Re-arm when the step falls back below 10; at most
one flag per 7 days. Nothing is tuned on 2018 leaks.

**Scoring.** The existing scorer, unchanged (credit if issuable within 7 days of first
positive leak flow, while the leak is still running). Abrupt and gradual leaks reported
separately; gradual leaks are not this method's job and are expected to be missed.

**Judged against random warnings.** The same number of flags, moved to other nights by
rotating the whole flag series by **whole weeks** (keeping day-of-week and flag spacing),
300 runs. Because flags are rare — at most one a week — random flags get roughly one
chance per 7-day leak window, unlike the earlier rules that fired several times per window.
This comparison can therefore actually tell skill from density.

**Pass on 2018 (development only).** Credits more abrupt leaks than 95% of the random runs,
**and** averages no more than one flag per week.

**Stop if:**
- it does not beat the random runs on 2018 abrupt leaks; or
- it averages more than one flag per week; or
- the night-to-night noise across the full year turns out much larger than January's,
  making 10 m³/h indistinguishable from ordinary variation.

**If it passes:** 2018's abrupt leaks have been studied many times, so a pass earns only
the right to a single, fully frozen evaluation on 2019 — with your explicit go-ahead before
2019 is opened.

## Limits

- Simulated data; sensor faults excluded by the organisers.
- The 2.3 m³/h night-noise figure rests on 9 nights.
- Night-flow reasoning fails under intermittent supply, the expected situation in Rwanda,
  where storage refills overnight. That is why the operations log and supply schedule are
  in the data request.
- Timing matches are associations. No pipe is located by any of this.

## Files

| File | Contents |
|---|---|
| `diagnostics.py` | D1–D3; retrospective checks clearly marked |
| `diagnostics.json` | All diagnostic numbers |
| `weekly-demand-reference.csv` | D2 weekly series |
| `weekly-night-day.csv` | D3 weekly series |
