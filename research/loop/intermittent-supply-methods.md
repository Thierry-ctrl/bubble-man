# Leak assessment when water supply is intermittent

Preparation item 4 — 11 October 2026. Literature review only.

**Verified (local scope):** no detector was implemented, tuned, run or scored; no utility readings or LeakDB labels were inspected. Public documents were viewed without saving datasets. Earlier results and pilot tools remain unchanged.

## The problem in plain language

**Verified ([Zarqa field study][zarqa]):** when water returns, households can refill storage tanks even while residents sleep. The lowest useful flow can occur outside the usual night hours. The study therefore warns against estimating leakage from one night's inflow in an intermittent system.

**My inference:** our present question, “did night flow rise?”, becomes ambiguous: it could reflect a new leak, a longer supply period, different pressure or more tank refilling. Removing a few hours after supply starts would not establish which explanation is right. Zero flow while water is off is not evidence that damaged pipes will not leak once pressurised.

**Unverified:** no reviewed source establishes that Bubble Man's unchanged rule works under rationed supply, or supplies an independently validated warning threshold for Rwanda.

## What previous work actually demonstrates

The evidence labels describe what a publication states, not independent reproduction of its results. “My inference” marks proposed applications and limits for Bubble Man.

| Approach | Evidence and scope | Inputs needed / limits for Bubble Man — my inference |
|---|---|---|
| **Measure after customer storage has filled** | **Verified:** the Zarqa field study supplied one zone continuously for five days; it reported stable repetition after approximately 63 hours. It measured inlet flow and pressure at 15-minute intervals, estimated legitimate consumption and used pressure information to estimate losses. [Paper][zarqa] | Potential route for a utility-led audit of **existing losses**. Requires a verified boundary, usable meters, consumption estimates and demonstrably filled storage. It is not a tested online new-leak detector under the ordinary rationing schedule. Neither five days nor 63 hours is a universal waiting period. |
| **Adjust loss accounting for changing supply** | **Verified:** Al-Washali and colleagues examine supplied-volume regression and supply-time normalisation of non-revenue water. Estimating actual supply time is itself uncertain; their Sana'a discussion identifies missing valve and pumping records. [2019 paper][nrw], [author's thesis chapter][thesis] | Useful for assessing whether apparent improvement merely follows supplying less water. Needs consistent inlet volumes, consumption/billing, storage and actual supplied hours. Non-revenue water includes metering and commercial losses; it is not all physical leakage and does not identify a newly leaking pipe. |
| **Represent filling, draining and household tanks in a hydraulic model** | **Verified:** Abdelazeem and Meyer synthesise intermittent-network modelling in SWMM, representing withdrawal, storage, consumption and pipe filling/draining; their demonstrated numerical stability and mass conservation concern simulations. [2025 paper][swmm] **Verified:** a separate uncertainty study finds supply characteristics strongly influence simulated performance, with tank size also important. [2026 paper][uncertainty] | A possible later way to predict refill patterns. Needs topology, elevations, pipe properties, valve/pump behaviour, pressures and household-storage assumptions, calibrated against field readings. A stable simulation is not evidence of useful leak detection. Adding tanks to a conventional pressurised model does not by itself validate pipe-emptying and air behaviour. |
| **Use storage-level measurements at individual buildings** | **Verified:** Tamari and Ploquet propose automatic tank gauging and report application to six buildings supplied through roof tanks. Their abstract distinguishes this from conventional pressurised-network methods. [2012 publisher abstract][buildings] | May support a separate investigation of **building-side** leakage. Needs tank geometry, level measurements and a defensible account of filling and legitimate use. The abstract does not provide enough detail to reproduce that separation here. Six buildings do not establish performance for a whole water zone or leaking main. |
| **Choose field investigation methods by supply regime** | **Verified:** JICA's Kenya project mapped continuous and intermittent areas separately to choose appropriate investigation techniques. It reports difficulty estimating leakage by minimum night flow in intermittent areas; its map associates step tests with continuously supplied areas. [2020 brief, pp. 4–5][jica] | Supports working with utility crews and pressurised supply periods. A field step test means controlled valve operations to narrow a section, not our arithmetic night-flow step. This brief does not establish a universal method or accuracy for intermittently supplied areas. No valve operation is proposed here. |

**Verified ([Zarqa study][zarqa]):** reducing pressure can also make leaking water harder to hear. **My inference:** acoustic instruments are possible field tools, but should not be assumed equally effective when pressure is low or water is off. This review does not establish their cost or detection performance in Rwanda.

## A readings-based idea worth considering later

**My inference — hypothesis, not a validated method:** compare like phases of successive supply cycles, rather than assuming the same clock hour has the same meaning every day. A comparison might account for elapsed time since water actually returned, duration of the preceding interruption, pressure and whether tank refilling has settled. A sustained excess in genuinely comparable conditions could then justify inspection.

**Unverified:** the reviewed sources do not provide a blinded field evaluation of this exact rule. There may be no stable late-supply phase if water switches off before storage fills. No fixed “skip the first two hours” rule, sensitivity threshold or warning guarantee follows from the literature. No implementation was made.

## Check the meter before interpreting the pattern

**Verified ([Perugia laboratory study][meters]):** tests of mechanical customer meters during pipe filling found air-related over-reading and possible damage; the paper investigates remedial arrangements. This is equipment-specific laboratory evidence, not an error rate for every meter.

**My inference:** ask which meters operate in completely filled pipes, how faults and air are handled, and what calibration evidence exists. Customer mechanical meters, electromagnetic zone meters and ultrasonic instruments cannot be assigned the same error from this study. A suspicious recorded flow could be partly a measurement problem; a sensor brand alone does not resolve it.

## What a Rwandan utility would need to provide

**Verified ([Rwanda context review](/Users/uwonkundathierryrugira/Bubble-man/research/loop/rwanda-utility-landscape.md), [Enabel clarification][enabel]):** the 2026 assessment of the Bugesera/Rwamagana study systems describes intermittent supply and inadequate historical flow/pressure data. That is evidence about those systems, not every zone in Rwanda.

**My inference — proposed data request, not sent:**

1. **Actual supply periods:** recorded start/end times of water delivery, pressure availability at representative points, pumping and valve operations, plus the planned rota. A planned opening time is not proof that distant customers received water then.
2. **Boundary flow and storage:** synchronized inlet/outlet/transfer readings, confirmed zone boundaries and meter identities; utility tank dimensions and levels if storage is inside the zone. Customer tank withdrawal and later consumption are different events.
3. **Pressure:** inlet and representative high/low or distant points, sensor elevations and units. Low pressure, water-off periods and missing sensor records must remain distinguishable.
4. **Customer behaviour:** prevalence and capacity of household tanks, float-valve/refill arrangements, large night users and changes in connection count or schedules. A representative survey may be more realistic than instrumenting every property; its uncertainty must be retained.
5. **Measurement quality:** timestamp convention, sampling interval versus transmission interval, quality flags, outages, meter replacements, calibration and pipe-full conditions. Communication gaps are not zero water use.
6. **Independent incident history:** first report, confirmation and repair times separately; location/asset and investigation findings, including unsuccessful or incomplete visits. Do not infer leak starts from the same flow used by the detector and call them independent truth.

**Unverified:** whether any proposed zone currently retains all these inputs, whether export is permitted, and what field staffing can sustain. No zone is declared suitable.

## Recommendation for this project

**My inference:** retain a continuously supplied, clearly bounded zone as the first unchanged-rule trial. If only intermittent supply is available, first characterise supply cycles, measurement quality and customer storage; use a separate protocol before evaluating any new approach. A utility-led saturation audit could assess existing losses where operationally feasible, while an online cycle-based warning method remains a research question.

**My inference:** pressure and tank-level sensors may help explain flow, but extra measurements do not automatically distinguish leaks from refill. The useful first step is establishing which explanation can be checked with data already held by the utility. There is no justification here to buy equipment, promise country-wide coverage or reopen simulator tuning.

## Sources, access and remaining questions

**Verified — access record:** Zarqa, the Perugia laboratory paper and JICA's brief were inspected as public PDFs through the browser. Wiley abstracts/text and primary publisher-indexed text were also read. Direct opens of the NRW and building pages were blocked; their accessible primary indexed text and the author's thesis chapter support the limited statements above. No account, form, dataset download or contact occurred.

**Unverified:** this bounded review is not an exhaustive proof that no intermittent detector exists. It does not establish detection rates, location accuracy, sensor costs or Rwanda performance. Before a future experiment, resolve whether representative supply cycles have a stable pressurised phase, how customer storage and legitimate withdrawals can be separated, and whether independent incident/inspection records exist.

[zarqa]: https://mdpi-res.com/d_attachment/water/water-11-00048/article_deploy/water-11-00048.pdf
[nrw]: https://www.mdpi.com/2073-4441/11/6/1220
[thesis]: https://pure.tudelft.nl/ws/portalfiles/portal/85455598/2020_IHE_PHD_THESIS_AL_WASHALI_i.pdf
[swmm]: https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2024WR039551
[uncertainty]: https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2024WR039282
[buildings]: https://www.tandfonline.com/doi/abs/10.1080/1573062X.2012.660959
[jica]: https://www.jica.go.jp/project/english/kenya/012/materials/c8h0vm0000f5y5nm-att/briefnote_202006.pdf
[meters]: https://research.unipg.it/retrieve/51d72991-a6f0-40fb-ae30-b7be06aecdd4/4273885e-2d1f-4403-8d51-75afba402187.pdf
[enabel]: https://www.enabel.be/app/uploads/2026/01/Proposed-Clarifications_Grouped-Answers.pdf
