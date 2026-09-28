# Bubble-man: water-leak detection project preparation

Research checked on 21 September 2026. This is a proposed research and build plan, not a report of a working detector. The sensor datasets have not yet been downloaded in full or evaluated. Source metadata, the L-Town README and scenario configuration have been saved locally; the latter two match the publisher's checksums.

**The first product**

Build software that helps a water-network operator answer: “Which area should we inspect, and what evidence supports that?” Start with detecting existing leaks and ranking investigations. Predicting future pipe failures is a separate project requiring different historical evidence.

The initial demonstration replays a public water-network dataset. A later pilot observes one measured section of a real network. A small physical pipe rig is optional; it is not a prerequisite for a utility conversation.

**The simplest explanation**

Imagine a neighbourhood with a water meter at its entrance and pressure gauges at several places inside. The entrance meter measures how much water passes through. Pressure gauges measure how strongly the water pushes. We also want to know whether pumps are running, tanks are filling, and supply is currently available.

Our software learns what usually happens under comparable conditions. It notices persistent changes, checks whether several instruments agree, and produces an inspection suggestion. An operator checks the evidence and a field crew establishes what actually happened.

A higher inlet flow is not automatically leakage. Customers may be using more water, or tanks may be filling. Lower pressure may reflect an outage, pump change, or measurement fault. The system must be allowed to say “insufficient evidence.”

Three different things fit together:

| Piece | Plain meaning | What we use it for |
|---|---|---|
| Dataset | A recording of past readings, with answers where available | Replay events and measure whether we detect them |
| Hydraulic simulator | A physics-based model of pipes and water movement | Create controlled what-if experiments |
| Operational digital twin | A model of a particular physical network, maintained using its measurements | Compare that network's expected and observed behaviour |

Replaying L-Town does not create a digital twin of Kigali. Moving to WASAC needs its network description, measurement mapping, calibration, operating context and validation.

**Datasets worth using**

| Resource | What is actually available | Recommended role |
|---|---|---|
| [BattLeDIM / L-Town](https://zenodo.org/records/4017659) | Simulated network telemetry, a pipe-network model and leak truth | First benchmark and replay demonstration |
| [LeakDB](https://zenodo.org/records/13985057) | Many synthetic leak scenarios across network models; full archive is 13.9 GB | Later robustness testing; start with a small [repository example](https://github.com/KIOS-Research/LeakDB) |
| [Mazaev and colleagues' field experiments](https://zenodo.org/records/7255403) | Replication data for controlled leaks in operational water networks; 195.5 MB archive | Second-stage reality check after inspecting its internal structure |
| [Experimental testbed dataset](https://data.mendeley.com/datasets/tbrnp6vrnj/1) | Physical laboratory measurements using pressure, acoustic and acceleration sensors | Useful if we later explore acoustic equipment or a physical rig |
| [WNTR](https://usepa.github.io/WNTR/hydraulics.html) | Software that generates hydraulic simulations, including leaks and pressure-dependent delivery | Create our own stress tests; it is a tool, not an additional measured dataset |

The laboratory resource contains 280 short signals from a 47-metre PVC testbed with induced leak and no-leak conditions. It is physical experimental data, not recordings of a city's long-term operations. Its acoustic data require a different processing pipeline from slow pressure/flow telemetry. [Dataset description](https://data.mendeley.com/datasets/tbrnp6vrnj/1).

The field-experiment resource was published by researchers with Ghent University–imec, De Watergroep and Hydroscan. It explicitly studies disagreement between simulated and measured pressures and uncertainty in locating leaks. Access is public, but column definitions, timing, sensor coverage and experiment splits still need a file-level audit before use. [Publisher record](https://zenodo.org/records/7255403).

Zenodo metadata identifies the L-Town, LeakDB and field-experiment data releases as CC BY 4.0; the laboratory release also displays CC BY 4.0. Preserve attribution and exact release identifiers. The KIOS code repositories identify EUPL-1.2, which is separate from the data license. Local metadata snapshots record the checked dataset licenses.

**The L-Town starter package**

L-Town provides 2018 and 2019 observations at five-minute intervals. Its README identifies 33 pressure sensors, three flow sensors, one tank-level sensor and 82 automated customer meters. Pressure and tank level are in metres; flow is in cubic metres/hour; customer demand is in litres/hour. [README](https://zenodo.org/records/4017659/files/README.txt?download=1), [challenge data description](https://battledim.ucy.ac.cy/?page_id=33).

The saved scenario configuration contains 33 leak events: 14 starting in 2018 and 19 in 2019, with 15 abrupt and 18 gradually developing events. Some leaks continue across the year boundary. These counts were checked directly in the configuration; they do not imply 33 independent training examples suitable for a large model.

The starter manifest selects approximately 75.87 MB: both years of flow, pressure and tank-level CSVs, both leak-truth files, the nominal network, repair report, README and configuration. Customer-demand files can be added later. The full 550.5 MB release includes duplicate spreadsheet representations and a much larger generation model. [Release and file list](https://zenodo.org/records/4017659).

Keep the truth files and the full leak configuration separate from detector inputs. The detector must not see future leak locations or times. Use the nominal `L-TOWN.inp` model for realistic benchmark work. The file called `L-TOWN_Real.inp` is the simulator's generation model, not evidence of measurements from a real town.

**Build sequence and completion checks — our proposed plan**

| Step | Work | Evidence needed before moving on |
|---|---|---|
| 1. Inspect and replay | Download selected files; verify checksums, units, timestamps and sensor IDs; display readings chronologically | A reproducible replay with an explicit data-quality report |
| 2. Establish a simple detector | Compare current values with past values at comparable times; combine persistent flow and pressure changes | A frozen baseline and an honest report of misses, delays and false alarms |
| 3. Add a small physics model | Use WNTR to create controlled leak, demand, supply and sensor scenarios | We can explain why a scenario changes the signals and identify what the model cannot represent |
| 4. Test optional AI triage | Give Jev compact event summaries; compare with rules and a small conventional classifier | Evidence that AI improves a useful measure on held-out cases |
| 5. Prepare a utility demonstration | Show replay, inspection queue, supporting evidence and operator outcomes | A short demo plus a one-zone data request, with performance and limits visible |
| 6. Run a local pilot | Partner on measurement access and hydraulic review; calibrate and observe without controlling equipment | Prospective field results agreed and reviewed with operators |

For planning, allow about four to six part-time weeks for steps 1–5 if data loading and tooling go smoothly. This is a working estimate, not a verified delivery commitment. An attractive replay can be built sooner than a trustworthy detector. Access arrangements and a real pilot require a separate timetable.

Start locally with Python for calculations and WNTR, simple files or SQLite for results, and a small dashboard. Choose the final interface after the first replay works. A GPU, new sensors and a cloud deployment are not requirements for the first benchmark. Public data access does not carry a dataset purchase price; developer time, connectivity, storage and optional API usage still have costs. The earlier conversation's hardware and pilot price ranges have not been validated by supplier quotations.

**How we test without accidentally giving ourselves the answers**

Use an earlier portion of 2018 for development and a later portion for threshold selection; freeze the method before the 2019 evaluation. Split by time and event, never by random individual rows. Carryover leaks must be reported separately from new leak onsets in 2019. Historical data already contain leaks, so do not label all of 2018 as healthy.

If labels help select clean baseline periods, document that assistance and use only labels from the development period. Fit normalization and preprocessing only on past data. During replay, every decision sees the past and present, never later samples. Do not interpolate using future observations. Keep the final test answers out of prompts, feature generation and tuning.

Compare methods using the same sensor inputs and alert budget. Combine repeated triggers into incidents so one leak does not count as hundreds of successful detections. Report at least:

- Fraction of distinct leaks detected, with event counts.
- Detection delay, separating sudden and gradual events.
- False alerts per zone per week, and false alerts during outages/restoration.
- Correct search-area ranking and uncertainty; do not promise an exact pipe without evidence.
- Data availability, sensor-fault handling and periods where the system abstains.
- Inspection yield: how many recommended investigations discover a confirmed problem.

Later, agree pilot targets with the utility's crew capacity. Estimated leak volume is not automatically measured water saved. Savings need verified repairs and a before/after comparison accounting for pressure, demand and supply changes. Do not advertise a single accuracy percentage dominated by long periods without new leaks.

**Rwanda findings that affect the design**

For the Bugesera/Rwamagana assignment, Enabel's clarification document describes internal GIS and billing data, missing SCADA streams and hydraulic models, unavailable reliable historical calibration flow/pressure data, and intermittent supply. It also identifies incident/leakage history as available. These are statements for that tender context and time, not a current nationwide audit. Detailed data access was reserved for the selected consultant. [Clarifications, questions 1–13](https://www.enabel.be/app/uploads/2026/01/Proposed-Clarifications_Grouped-Answers.pdf).

Therefore our additional tests should include supply stopping, supply returning, legitimate demand surges, pump/valve changes, missing readings, stuck sensors, sensor drift, slow leaks and multiple simultaneous incidents. Pressure-dependent simulation helps with low-pressure delivery, but a basic hydraulic model is not sufficient proof of realistic pipe emptying/refilling, air pockets or fast pressure transients. Have a hydraulic specialist review those assumptions. [WNTR hydraulic capabilities](https://usepa.github.io/WNTR/hydraulics.html).

Enabel's public notice is closed, with a 26 March 2026 deadline. The pages checked do not establish who ultimately implemented the work or whether a functioning twin is now available. Ask for current status rather than assuming a system exists. [Tender notice](https://www.enabel.be/tenders/consultancy-for-a-feasibility-study-digital-twin-development-and-detailed-design-for-real-time-water-network-monitoring-for-water-quality-and-leakages-detection-in-the-bugesera-and-rwamagana-water-d/).

Cenfri reported an existing WASAC executive dashboard in June 2026, covering operational and financial indicators. An additional generic dashboard is therefore a weak differentiator. Our proposed contribution is the evidence-backed inspection queue and the record of what each investigation found. This is a product inference, not a statement that existing systems lack every such feature. [Cenfri update](https://cenfri.org/articles/turning-data-into-decisions-lessons-on-dashboard-development/).

Also, non-revenue water includes commercial and measurement losses as well as physical leaks. This first project addresses only part of that problem. The prior chat's national percentages and targets are not adopted here as verified current figures. [WASAC partnership description](https://www.wasac.rw/en/public-information/news/d/wasac-group-partners-with-cenfri-to-boost-data-driven-decision-making?cHash=c6d4b78245779e7df10c2edb65409b60).

**Jev's place in the experiment**

Jev returns typed judgments, not prose explanations. TypeSafe specifically warns about arithmetic, date comparison and numerical precision. Calculate trends, durations, volume estimates and hydraulic differences in ordinary code. Give Jev short event summaries and narrowly defined choices. [Introduction](https://docs.typesafe.ai/introduction), [documented limitations](https://docs.typesafe.ai/model-jaggedness/jev-1.13).

Example input, entirely illustrative: “Neighbouring pressure sensors show a persistent drop. Inlet flow is above its recent comparable baseline. Supply is on. No scheduled pump change is recorded. One sensor is offline.” Candidate outputs could be “investigate possible leak,” “check instrumentation,” “expected operating change,” or “insufficient evidence.”

This is a hypothesis to test. L-Town alone does not label customer complaints, all sensor faults, or crew-priority decisions. Synthetic cases can test plumbing and obvious logic, but they cannot establish real operator-triage performance. Add expert-reviewed cases and eventually verified field outcomes.

Compare detector-plus-rules with detector-plus-Jev on identical held-out events. If Jev adds no measurable benefit, omit it. TypeSafe's confidence statistic is distinct from the probability of a particular class; neither is automatically a calibrated probability of a real leak in Rwanda. Validate any probability claims locally. [Confidence documentation](https://docs.typesafe.ai/confidence).

Keep the core detector and dashboard operational during provider outages. Log model version, inputs, decisions and operator disposition. Jev outputs can become proposed labels for review; confirmed repair findings and verified no-leak investigations should ground future model training. Repeatedly training on an unverified model's guesses would reinforce its errors.

**The minimum later data request — proposed, not yet sent**

Ask WASAC's non-revenue-water/network-operations team and its data/IT counterpart for one suitable measured area. Involve a hydraulic engineer early. Ask Cenfri about existing data integration and Enabel about the current status and implementer of its monitoring project.

| Requested information | Why it matters |
|---|---|
| Zone boundary and every known inlet/outlet | Establish what is inside the area and where water crosses it |
| Pipe/valve/tank/pump layout, elevations and operational connectivity | Relate signals to the physical network |
| Timestamped flow, pressure and tank readings, units and device IDs | Establish a usable baseline and align observations |
| Supply schedules, valve operations, pump status and outages | Explain pressure changes that are not leaks |
| Sensor specifications, calibration and missing-data history | Distinguish network events from instrument problems |
| Leak/repair records and inspections that found no leak | Evaluate both detections and false alarms |
| Aggregated consumption by suitable area and time | Help separate expected use from unexplained changes |

Request several weeks to a few months of observations if available; required duration depends on supply cycles, seasonality and event frequency. Billing totals cannot substitute for synchronized operational flow measurements. Use customer identifiers only if required for an agreed purpose; raw personal details are not needed for the initial leak benchmark.

If suitable telemetry does not exist, the first partnership activity becomes a measurement campaign. Sensor number and placement should follow a site survey and observability assessment, not a generic shopping list. A measured zone also needs a working response process: who reviews an alert, who inspects, and who records the result.

**First concrete deliverable**

A local replay of L-Town showing sensor traces, a ranked inspection queue and a separate truth view for evaluation. The key demonstration is: the software sees only available measurements, raises an alert, explains the measured evidence, and is then checked against known outcomes. Success is an honest, repeatable experiment that gives us a basis for a one-zone partnership.
