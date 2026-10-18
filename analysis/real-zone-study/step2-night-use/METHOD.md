# Step 2: night-flow accounting, with wide uncertainty

Written before computing the decomposition, 18 October 2026. This is a descriptive sensitivity study, not a new detector test or a preregistered validation. The five zone identities and property counts are already known.

## Scope and sources

Use only the existing N4 flow file, the authorised property-count download, and saved step-1 selection/provenance. Do not open repair records. No detector is imported, run, changed or given these estimates. No Git operation is performed.

Property counts: [Yorkshire Water / Data Mill North](https://datamillnorth.org/dataset/yorkshire-water-leakage-dma-15-minute-data-2zlgn), Apr 2016–Mar 2017, Creative Commons Attribution. `source/download.json` records the exact resource, size and checksum. Domestic and non-domestic counts are billing-property counts, not occupants, meters, business categories or verified occupied properties. Confirm each selected zone has exactly one N4 row and non-negative integer counts; stop otherwise. Do not use the separate postal-sector file or sum overlapping datasets.

## Rate assumptions — all in litres/property/hour

| Component | Working range | Basis and limitation |
|---|---|---|
| Household legitimate use | **1–4** | Analyst-chosen sensitivity range, **not a published interval**. It brackets the old UK 1.7 allowance and NI Water's later 2.48 estimate, and deliberately extends beyond both. Neither is a Yorkshire measurement. |
| Non-household legitimate use | **0.7–60.6** | Historical UK customer-category averages reported by Farley. Apply the lowest/highest category average to the whole zone as bounding scenarios because its category mix is unknown. These are **not limits on an individual customer's use**, nor guaranteed bounds on a DMA mean. |

References, checked 18 October 2026:

- [Farley, WHO, 2001, *Leakage Management and Control*](https://www.ircwash.org/sites/default/files/Farley-2001-Leakage.pdf), printed pp. 52, 80–81 and Table 7.2. Reproduces UK Managing Leakage (1994), describes large-user monitoring and measurement-duration limitations. The 1994 figures are old and UK-specific.
- [NI Water AIR 2009, independent reporter, section 4.3.8](https://www.uregni.gov.uk/files/uregni/media-files/AIR09%20Reporters%20Report%20Part%203%20Non-Financial%20Measures.pdf), PDF p. 35 / section page 14. Its 2.48 household estimate came from 2007–08 monitoring; its minimum-flow procedure used 15-minute minima, so it is contextual evidence of variation, **not a directly interchangeable hourly calibration**.
- [Fantozzi and Lambert, 2012](https://www.leakssuitelibrary.com/wp-content/uploads/2024/10/2012_FantozziLambert-RNUPaper2012-2022_07_24-18_35_15-UTC.pdf), pp. 1–5. Professional component accounting, fixed-hour measurement, and distinction between legitimate use and customer leakage. No universal night-use constant.

The range choices are judgement. Values outside them remain possible. In particular, exceptional industrial use, tank filling or irrigation is **not measured or bounded** by these counts. No local rate is inferred from the residual.

## Flow summary, separated from the step-1 proxy

The historic 1.7 allowance concerns a fixed **one-hour** measurement, so do not subtract it from the step-1 minimum two-hour proxy and call that a measured loss. Use a separate fixed-hour accounting summary:

1. Same five selected zones, in step-1 order: 784, 1586, 664, 526, 698.
2. Read the existing 15-minute file. Use only V, finite, non-negative values; convert L/s × 3.6 to m³/h. Remove duplicated zone/timestamps and the ambiguous 30 October 2016 01:00–02:00 hour. Reindex to the original 365-day wall-clock grid. No filling gaps. All four quarter-hours must exist for an hourly mean.
3. Require complete 00:00–06:00 nights. From the first 28 days' Monday–Friday nights, choose the whole hour (00, 01, …, 05) with the lowest median hourly flow; ties go to the earlier hour. Require at least ten such training nights. This describes observed low flow, not a known leak-free period.
4. Hold that hour fixed. Summarise Monday–Friday nights on days 28–364: median, 10th and 90th percentiles, complete/missing counts, monthly medians. Do not select a favourable season. The percentile span describes **variation across nights**, not measurement error or a confidence interval.
5. Recalculate finite half-hour coverage and the step-1 two-hour reference solely as a reader/unit cross-check; require agreement with saved step-1 figures. This does not rerun its warnings or injections.

Wall-clock times are those in the source file. We do not know whether readings denote interval starts or ends. At clock changes, retain the previous missing-data policy. The fixed hour selected from earlier readings can be imperfect later; the whole-year summary is not a fully calibrated utility leakage assessment.

## Calculation and interpretation

For H household and N non-household properties:

`use_low = (H × 1 + N × 0.7) / 1000`

`use_high = (H × 4 + N × 60.6) / 1000` m³/h.

At observed median flow Q, show the signed residual range `[Q − use_high, Q − use_low]` and the corresponding **conditional plausible leakage share**. Intersect possible legitimate use with `[0,Q]` first: if `use_low > Q`, the range assumptions are incompatible and the share is unavailable; otherwise the share is `[max(0, Q − use_high)/Q, (Q − use_low)/Q]`. A negative signed lower residual means the all-high-use corner is inconsistent with that Q; expose it and count nights where this occurs. It is not a negative leak or evidence for a zero leak.

Also show the wider scenario span combining the observed Q10/Q90 with the use ranges: the smallest feasible share at Q10 (or zero if Q10 is below use_low), and the largest share at Q90. This is an **envelope of rate assumptions and typical night-to-night variation**, not a probability statement. Keep incompatible endpoints visible in the CSV.

Report extra non-household use needed to erase a positive residual after the all-high-rate scenario: `max(0, Q − use_high)`, and that quantity per N non-household properties. This is a sensitivity calculation, not evidence that those users exist.

The unaccounted remainder can include utility leaks, customer plumbing leaks, unmeasured legitimate use, net transfers/storage, timing errors and meter/boundary errors. Treating it as possible physical leakage assumes accurate **net** zone inflow and stable storage/boundaries, none independently verified here. No utility/customer split, annual volume, Rwanda extrapolation, validated loss rate or new detector claim follows. Without the assumptions, the data do not identify a non-trivial leakage-share bound.

## Outputs and review boundary

Save property join, nightly values, hour selection, summary, assumptions, provenance and one explanatory figure under this new folder. Preserve earlier files byte-for-byte. Provide a short findings note distinguishing verified observations, conditional calculations and unknowns; give scoped manual commit commands. Stop for founder review before step 3.
