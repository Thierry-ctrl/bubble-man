# Accounting for tanks inside a water zone

**Draft design — standalone; not connected to the frozen tools.**

**Verified (local sources):** preparation item 5, 11 October 2026. The separate [function](/Users/uwonkundathierryrugira/Bubble-man/pilot/loop/storage_correction.py) and [36 checks](/Users/uwonkundathierryrugira/Bubble-man/pilot/loop/test_storage_correction_INVENTED.py) use invented tanks, dates and readings. No real data or detector was run. The [existing converter](/Users/uwonkundathierryrugira/Bubble-man/pilot/convert_utility_data.py) continues to refuse internal-storage zones by default.

## The idea in plain language

**My inference — physical accounting design:** water entering a zone can go to customers, escape through leaks or other losses, or increase the amount held in utility tanks. When those tanks drain, customers can receive water even if little enters through the zone's boundary. Correcting for the change in stored water therefore gives a better account of withdrawals and losses.

**My inference — proposed balance for a fixed boundary:**

```text
net boundary inflow = inlets + transfers in − outlets − transfers out

withdrawals and losses over an interval
    = net boundary inflow volume − sum of internal tank volume increases

mean withdrawals and losses (m³/h)
    = mean net boundary inflow (m³/h)
      − sum[V(end) − V(start)] / interval length in hours
```

**My inference:** filling is a positive storage change and is subtracted; draining is negative and is added back. Tank overflow or leakage remains a loss in this accounting unless separately measured and assigned to an external boundary flow. The result still mixes legitimate withdrawals with losses; it is not a leak volume or a diagnosis.

### One entirely invented example

**Verified (invented-case arithmetic; [check 1](/Users/uwonkundathierryrugira/Bubble-man/pilot/loop/test_storage_correction_INVENTED.py)):** a tank has an invented constant footprint of 100 m². During 30 minutes its water depth rises from 1.0 to 1.2 m, adding 20 m³. Mean net boundary inflow is 100 m³/h, so 50 m³ entered. Subtract the 20 m³ stored: 30 m³ remained for withdrawals and losses, or 60 m³/h. If the level instead falls by 0.2 m, the same inflow accompanies 140 m³/h of withdrawals and losses. These numbers demonstrate the signs, not utility performance.

## Which tanks belong in the calculation?

**My inference — proposed boundary rule:** include every utility storage tank **inside the selected hydraulic boundary**. Count each volume once. A pump feeding an internal tank is an internal transfer; subtracting its flow as an external outlet and also subtracting the tank's storage would double-count it. A transfer across the chosen boundary is already included in net boundary flow. Confirm the map, meter roles and valve status before constructing the inputs.

**My inference:** household tanks downstream of customer connections are a separate issue. For the usual utility distribution boundary, their refill is customer withdrawal, even when residents consume that water later. Correcting utility reservoirs does not solve night-time household refilling under intermittent supply. A different control boundary would need its own declared storage and metering design.

**Unverified:** a real zone's complete tank inventory, boundary and meter roles. The function's required `inventory_confirmed` boolean is a caller's explicit declaration, not independent proof. `False` blocks all correction; a confirmed empty inventory permits a clearly explicit pass-through.

## Inputs needed

**My inference — proposed input contract:**

| Input | Meaning and required checks |
|---|---|
| Net boundary flow | Mean signed rate in m³/h for an explicit start/end interval; derived from every boundary meter. An instantaneous reading at the end cannot silently replace an interval mean. Retain quality flags and missing components. |
| Tank level | Instantaneous water **depth in metres** at both exact interval endpoints. State its zero/reference datum. Surface elevation or raw pressure requires an approved conversion first. An interval-average level is not an endpoint. |
| Geometry | An approved water-depth versus stored-volume table, or a constant footprint with minimum/maximum depths and volume at the minimum. Geometry must match the physical tank and remain stable for the period. |
| Clock and availability | Timezone-aware times, synchronized measurement clocks, known interval conventions and receipt times where available. Logger receipt time and measurement time are different. |
| Inventory / uncertainty | Complete internal utility-tank inventory; valid/invalid reading flags; absolute level and mean-flow error bounds where known. Unknown accuracy remains unknown. |

**Verified ([EPA EPANET manual, tanks and volume curves](https://usepa.github.io/EPANET2.2/3_network_model.html)):** the manual distinguishes tank depth from bottom elevation and describes cylindrical geometry or a volume-versus-depth curve for other shapes, with minimum/maximum operating levels.

**My inference — implementation choice:** the prototype supports a constant footprint, a vertical cylinder (`π × diameter² / 4` footprint), and an approved monotone piecewise-linear volume table. A rectangular tank uses length × width as its footprint. A horizontal cylinder or irregular shape needs an appropriate volume table, not a vertical-cylinder formula. Geometry interpolation occurs only between table points; **there is no interpolation in time** and no extrapolation outside the approved range. Constant dead-storage offsets cancel from volume differences.

## Timing, gaps and precision

**My inference — proposed handling:** each corrected row describes the same explicit interval as its boundary flow. The end level is necessary, so its value cannot be used at the start. `not_before` is the later of the interval end and supplied receipt times for contributing readings. Without receipt times this is only a lower bound; it does not prove data arrived by then. Any future live pipeline must retain receipt history.

**Verified ([function](/Users/uwonkundathierryrugira/Bubble-man/pilot/loop/storage_correction.py)):** it requires one explicitly chosen interval duration and exact endpoints, normalises aware times to UTC, and rejects duplicate level timestamps or overlapping/out-of-order flow intervals. Missing, flagged or out-of-range levels for **any** tank make the whole interval unassessable. Missing flow does likewise. It does not snap timestamps, bridge an interval-duration mismatch, fill gaps or use partial-tank corrections. Existing gaps between flow intervals remain gaps; no rows are manufactured. Negative corrected values are retained with a review note.

**My inference:** `ok` means the stated arithmetic inputs were usable, not that a zone is pilot-ready. A negative result can expose a timing, measurement or boundary mismatch and needs investigation. Do not turn it into zero to make a cleaner graph. If geometry or sensors change, split the accounting period and approve the new geometry; do not difference across a replacement or datum reset.

**Verified (invented-case calculation; [check 27](/Users/uwonkundathierryrugira/Bubble-man/pilot/loop/test_storage_correction_INVENTED.py)):** with an invented 200 m² footprint and endpoint depth error bounded by ±0.005 m, the storage-rate error can reach ±24 m³/h over five minutes, versus ±4 m³/h over 30 minutes. The flow is assumed exact solely for that made-up check. This illustrates error amplification, not the accuracy of a particular sensor.

**My inference — uncertainty design:** if every endpoint and the mean boundary flow has a supplied absolute error bound, propagate the minimum/maximum possible volume changes through the geometry and sum them conservatively. The result is a bounded range, not a standard deviation or confidence interval. Bounds are conditional on exact approved geometry and time alignment; geometry error, drift, turbulence and clock jitter are not quantified. If any bound is unknown, retain the nominal correction and label measurement uncertainty unquantified. An error range outside the geometry makes the row unassessable rather than silently clipping it.

**My inference — future aggregation:** correct matching intervals before computing night minima or other nonlinear statistics. For longer mean intervals, conserve summed volumes and use actual durations; do not subtract a tank's separately chosen nightly minimum from the flow's minimum. Use endpoint volumes, not an averaged level, especially for nonconstant geometry. Any resampling/missingness policy belongs in a later approved adapter; this prototype does not implement one.

## Verification and remaining work

**Verified (invented checks):** 36/36 passed. Coverage includes fill/draw/steady levels; signed boundary flow; multiple tanks and missing tank records; cylindrical/nonconstant geometry and dead volume; exact endpoints, offsets, duplicates and receipt delay; gaps/flags; uncertainty including asymmetric volume curves; negative/nonfinite results; and an independently written fill/draw sequence whose total volume balance closes. All input numbers and dates are invented. The checks establish accounting behaviour only.

**Verified — repeat command, invented inputs only:**

```sh
python3 -B -m unittest discover -s pilot/loop -p 'test_storage_correction_INVENTED.py' -v
```

**Unverified:** field accuracy; adequate depth resolution; actual geometry; synchronized interval-mean boundary flow; complete tank inventory; usefulness for leak detection; compatibility with real exports. No confidence or performance threshold is proposed.

**My inference — before future integration:** agree the boundary, geometry, sampling/receipt meaning and uncertainty policy with the utility; obtain permitted example formats and readings; approve resampling and quality exclusions; then design and test a separate adapter. Wiring this function into the frozen detector is outside this completed preparation item. The independent export-format preparation can proceed without approving real use now.
