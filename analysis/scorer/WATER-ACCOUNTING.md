# Water accounting for the two zones

Established from `L-TOWN.inp` (nominal model) plus the SCADA flow and level files.
`PUMP_1` is the **only** link between the two areas, so the boundary is unambiguous.

## The network, in one paragraph

Two reservoirs, R1 and R2, feed one connected 690-node network through the metered
inlets `p227` and `p235` and pressure-reducing valves PRV-1 and PRV-2. From inside that
network, `PUMP_1` lifts water into tank T1, which then supplies a separate 93-node area
("Area C") by gravity. Nothing else crosses between the two.

## The two balances

**Main zone.** Water entering is `p227 + p235`. Water leaving is customer demand, plus
main-zone leakage, plus **the transfer to the tank**. So:

    main-zone demand + leakage  =  p227 + p235 - PUMP_1        [m3/h]

Without subtracting `PUMP_1`, every nightly tank refill looks like a rise in main-zone
consumption.

**Area C.** `PUMP_1` measures flow *into the tank*, not out of it, so it is not Area C's
consumption. The tank buffers the difference:

    Area C demand + leakage  =  PUMP_1 - (storage change)      [m3/h]
    storage change           =  tank area x level change, expressed as a rate
    tank area                =  pi x (16 m / 2)^2  =  201.0619 m2

## Worked example, 2018-03-06 02:00 -> 02:05

| Quantity | Value | Unit |
|---|---|---|
| `p227` | 70.230 | m³/h |
| `p235` | 78.260 | m³/h |
| `PUMP_1` | 44.050 | m³/h |
| tank level | 3.550 → 3.550 | m |
| level change | +0.0000 | m per 5 min |
| storage change | +0.0000 m × 201.06 m² = +0.000 m³ per 5 min → ×12 = **+0.000** | m³/h |

    MAIN   = 70.230 + 78.260 - 44.050 = 104.440 m3/h
    AREA C = 44.050 - (+0.000)        =  44.050 m3/h
    check  : 104.440 + 44.050 + 0.000 = 148.490  =  p227 + p235   OK

Over the whole of 2018 the balance closes exactly: main 174.86 + Area C 26.84 = 201.70
m³/h, equal to inflow minus storage change. Net storage moved −20.11 m³ across the year
(level 3.500 → 3.400 m), which is negligible against ~1.77 million m³ delivered.

## Assumptions, stated

- **Sampling.** Flows are instantaneous readings every 5 minutes; level likewise. The
  storage term uses a forward difference, so it assumes the level is a step-wise record
  of the same 5-minute grid. Flow and level timestamps were checked to be identical.
- **Resolution.** At 5-minute spacing the storage estimate is noisy — level is recorded
  to 3 decimals and the pump switches within an interval — giving a negative Area C
  outflow in 4.10% of intervals, which is physically impossible. **At hourly resolution
  this falls to 0.02%.** All evaluation therefore uses hourly means.
- **Flow direction.** `p227` and `p235` are assumed to flow reservoir→network and
  `PUMP_1` network→tank, as the model defines them. No reverse flow was checked for.
- **Other boundary flows.** The model shows none: no other link joins the two areas, and
  no export or emergency connection is represented. Real networks usually have some.
- **Tank geometry.** Cylindrical, 16 m diameter, constant cross-section between 0 and
  4 m. Observed range in 2018 was 1.950–3.900 m, inside that band.

## What the correction does to the signals

Measured at the arithmetic midpoint setting (threshold 10 m³/h, persistence 6 h,
7-day deadline), 12 main-zone leaks:

| Signal | Credited | Abrupt | Gradual | False alerts | Repeats | Median delay |
|---|---|---|---|---|---|---|
| `p227` only (v1) | 11/12 | 5/6 | 6/6 | 6 | 227 | 21.4 h |
| `p227+p235`, no pump correction | 11/12 | 5/6 | 6/6 | 7 | 192 | 21.4 h |
| **`p227+p235-PUMP_1` (correct)** | **9/12** | **3/6** | **6/6** | **1** | **119** | **50.4 h** |

The corrected signal is much quieter — false alerts fall from 6–7 to 1 and repeats
nearly halve — because the nightly pump cycle is no longer being read as consumption.
It also credits fewer leaks, but the threshold was inherited from a differently-scaled
signal and has not been recalibrated. **Do not read this as the corrected signal being
worse.**

## Are Area C leaks visible at the main inlets?

Yes, indirectly. Three distinct statements:

- **Physically connected:** every drop Area C uses passes through `PUMP_1` from the main
  network. The areas are not independent.
- **Indirect effect:** an Area C leak drains the tank faster, the pump runs longer, and
  raw inflow at the reservoirs rises. For leak `p31` (Area C, mean 7.50 m³/h), raw
  `p227+p235` rose **+6.87 m³/h** and `PUMP_1` rose **+7.93 m³/h**.
- **Practical detectability:** in the **boundary-corrected** main signal the same leak
  moved **−1.06 m³/h** — removed, as intended. So Area C leaks are observable in raw
  inflow but deliberately excluded from the corrected main signal, where they would
  otherwise be attributed to the wrong zone.

My earlier statement that Area C leaks were "never observable at the main inlets" was
wrong. Correct: not observable *in the corrected main-zone signal*, by design.

(The equivalent test for `p257` is confounded — main-zone leaks `p461` and `p232` begin
inside its comparison window — so `p31` is the cleaner demonstration.)

## Comparison periods, reassessed

| Zone | Leak-free hours in 2018-01-15..12-31 | Verdict |
|---|---|---|
| Main | 215 of 8424 (2.55%), 15–23 Jan | Usable, but thin |
| Area C | **0 of 8424** | **No false-alert rate can be measured at all** |

With 215 leak-free hours (~1.3 weeks) and 1 observed false alert, any false-alert rate
carries enormous uncertainty. It should be reported as a count with its exposure time,
never as a confident per-week rate.

## Language discipline

Every time match remains an **association**, not proof that a particular leak caused a
particular warning. Our signals name no pipe.
