# Rwanda utility infrastructure and data access for Bubble Man

**Verified (local scope record):** preparation iteration 2, researched 11 October 2026. Public documents and publication metadata only; no utility readings, repair rows or LeakDB labels were opened, no detector was run, and nobody was contacted. The protected September report remains unchanged.

## Read this first

**My inference:** Rwanda has useful existing metering and data-management work to build on. Our immediate problem is finding one suitable zone with retained readings and permission to use them. A meter installation, a management dashboard and a usable history of individual meter readings are three different things.

**Verified (source link):** Enabel's 2026 Bugesera/Rwamagana clarification reports intermittent supply, missing SCADA streams and no reliable historical flow/pressure for calibration. Network data are internal, with access for the awarded consultant. This dated assessment concerns the study systems. [Questions 4–13][enabel-answers]

**Unverified:** no Rwandan zone has been established here to satisfy all of Bubble Man's requirements: a complete metered boundary, continuous supply, compatible sub-daily history, storage information and independently understood incident dates. No public raw-flow API or downloadable WASAC meter history was confirmed.

**My inference:** first seek an existing Kigali monitoring zone through WASAC Utility's operations and data teams. Treat Bugesera/Rwamagana as a later intermittent-supply opportunity. Keep the public real-data candidates from [iteration 1](/Users/uwonkundathierryrugira/Bubble-man/research/loop/real-datasets.md) available for preparation outside Rwanda.

### Evidence labels

**Verified (source link)** means an inspected primary source states the fact; it does not mean the underlying measurements were independently audited. **Unverified** means not established from this review. **My inference** marks a recommendation or interpretation. A dated source proves a dated statement, not continued operation today.

## 1. Who operates the infrastructure

**Verified (source link):** WASAC Group describes two subsidiaries: **WASAC Utility**, delivering services, and **WASAC Development**, developing infrastructure. [Official organisation description][wasac-history]

**My inference:** the Utility operations/NRW team is the likely owner of usable operating histories and repair records; its IT/data team would arrange exports. Development and project teams could identify newly instrumented zones, but procurement records alone cannot establish data availability.

**Verified (source link):** a WASAC July 2026 NRW-expert tender estimates national non-revenue water at about 37.8%. [Tender][wasac-nrw]

**My inference:** that estimate supports the relevance of loss reduction. It is neither a measurement of physical leakage alone nor evidence that Bubble Man could recover that amount. NRW also includes billing and metering losses.

## 2. Areas and supply conditions

| Area | Documented evidence | Implication for the first pilot — my inference |
|---|---|---|
| Kigali: Kadobogo / Ruyenzi | **Verified:** historical DMA work in Kadobogo (Kacyiru branch) and Ruyenzi (Nyarugenge branch), with isolation and inlet measurement. [2024 project paper][kigali-paper] | Useful places to ask about existing records; their present boundaries and supply regime still need confirmation. |
| Kigali: other monitored branches | **Verified:** JICA documents vendor-server monitoring for Remera/Kanombe and a WASAC system for Nyarugenge/Gikondo/Kacyiru/Nyamirambo, substantially built in September 2021. [2022 brief, pp. 5–6][jica-brief] | Investigate retained meter-level histories before proposing new hardware. A branch is not automatically one hydraulically isolated zone. |
| Bugesera / Rwamagana | **Verified:** the study systems have the supply/data limitations stated above. [Clarification][enabel-answers] | Poor immediate fit for the unchanged continuous-supply method; potentially valuable for a separate design later. |
| Karongi: Rubengera / Bwishyura | **Verified:** WASAC's 2 October 2026 account reports a completed Kivu Belt plant, improved reliable supply and a resident's account of an end to rationing. It also identifies multiple reservoirs. [Official report][karongi] | A promising inquiry lead. One testimonial cannot establish continuous pressure throughout a zone; storage and history compatibility need checking. |
| Other secondary cities | **Unverified:** current zone-level hours of supply, DMA inventories and logger histories were not established for Huye, Musanze, Muhanga, Rubavu or Rusizi. | Choose on actual operating records, not city size or national access figures. |

**Verified (source link):** the latest entry visible on RURA's inspected water-statistics index covers Q2 2024; the linked report gives aggregate production, supply, billing and customer figures. [Index][rura-stats], [report][rura-q2]

**My inference:** these publications cannot establish 2026 continuity at a particular inlet. Website modification dates are not the dates of the underlying measurements. Improved access also does not establish round-the-clock supply.

## 3. Meters, loggers and accessible data

**Verified (source link):** JICA describes electromagnetic meters, transmission equipment, a Nyarugenge server and monthly NRW calculations. [Brief, pp. 5–6][jica-brief]

**Unverified:** operating status in October 2026; meter models, pulse outputs and pulse volumes; logging interval versus transmission interval; retained years; quality flags; local backups; vendor subscriptions; export formats, API availability, charges and ownership. Monthly NRW reporting does not establish that only monthly readings exist, or that finer readings remain available.

**Verified (source link):** Cenfri reports a WASAC executive dashboard tracking connections, consumption, revenue, production and cost in June 2026. [Dashboard account][cenfri-dashboard]

**My inference:** this is an encouraging data-governance route, but the dashboard's near-real-time indicators do not prove that 15-minute zone telemetry is available to Bubble Man.

**Verified (source link):** Enabel describes GIS/incident information and requires prototype sensors and interoperability. [Questions 8, 13–14][enabel-answers]

**My inference:** obtaining a permitted historical export is the lowest-dependency first step. A live radio connection or an API is not necessary to check a CSV sample. Buying a sensor before establishing its meter interface, recording settings and accessible output would leave the data problem unresolved.

### Questions for a later utility discussion

**My inference — proposed questions, not sent:**

1. Which single zone has every inlet, outlet and transfer identified, with confirmed boundary valves?
2. Has that zone actually maintained supply overnight? Can interruptions and pressure changes be documented?
3. Which meter/logger measures each boundary? What does its output represent, and how often is a reading saved?
4. Can the data owner provide a 2–4 week CSV sample with units, timestamp convention, quality flags and gaps left visible?
5. Is at least a year of comparable history retained? Do repairs and meter replacements create discontinuities?
6. Are there internal tanks? Can dimensions and time-stamped levels be provided?
7. Who owns the readings and can approve access? Does a vendor need to export them, and at what cost?
8. Do records distinguish first report, confirmation and repair completion? Are unsuccessful inspections also recorded?

**My inference:** answers to these questions decide pilot eligibility. Neither a smart-meter brand nor national mobile coverage alone answers them. Site signal, power, flooding and local buffering remain checks for any later sensor deployment.

## 4. Programmes and possible routes to the data owners

| Programme | Verified evidence and date | Relevance / remaining uncertainty |
|---|---|---|
| JICA Kigali NRW project | See the historical evidence in section 2. | **My inference:** seek retained histories from the successor team. **Unverified:** current equipment condition and access. |
| JICA KAIZEN / Ntora–Remera | **Verified:** JICA lists KAIZEN utility support for February 2022–March 2027 and Ntora–Remera works for December 2022–October 2026, addressing management, pressure and leakage. [Programme overview][jica-current] | **My inference:** relevant teams for operational context. **Unverified:** actual completion of the latter and any exported pilot histories. Listed end dates are not completion evidence. |
| WASAC–Cenfri | **Verified:** MoU signed 27 May 2025, planned through 30 April 2027; data strategy, internal capability, mapping and NRW investigation are in scope. [WASAC announcement][cenfri-mou] | **My inference:** a strong route to identify datasets and permissions. **Unverified:** an entitlement for Bubble Man to receive them. |
| Enabel CLIMURBA | **Verified:** Open.Enabel lists 19 December 2024–19 December 2029. The monitoring tender RWA23001-10007 is closed, with a displayed deadline of 26 March 2026. [Programme][climurba], [tender][enabel-tender] | **Unverified:** award, contractor and operational prototype status. A closed tender does not prove installation. |
| World Bank Group / PPIAF / IFC | **Verified:** historical Kigali bulk-water preparation included institutional support and recommendations on distribution monitoring/NRW. [2015 PPIAF note][ppiaf] | **Unverified:** a current dedicated World Bank-financed WASAC DMA-data programme or an accessible dataset arising from it. **My inference:** bulk production and zone inlet histories serve different purposes. |
| African Development Bank | **Verified:** WASAC's recent tender listing identifies AfDB funding for RSWSSP; the Karongi report also identifies AfDB funding. [Tender listing][wasac-tenders], [Karongi][karongi] | **My inference:** retain this financing distinction; do not relabel these as World Bank programmes. **Unverified:** dataset access for an external pilot. |

## 5. Publicly named people and teams

**My inference:** request routing to a responsible operations/data team before seeking executive sponsorship. These are public professional leads, not contacted people or confirmed supporters. The names below are tied to the publication dates; continuing roles and authority to approve data sharing are **unverified**.

| Lead | Verified public identification | Possible purpose — my inference |
|---|---|---|
| WASAC Utility NRW, network operations, mapping and IT/data teams | **Verified:** Utility's service remit above. [WASAC][wasac-history] **Unverified:** exact current department titles and data custodians. | Request these functions when seeking the zone, export and repair-record owners. |
| Maxime Mwiseneza | **Verified:** appointed WASAC Utility Managing Director in December 2025. [Appointment account][wasac-appointment] | Route a pilot request to the responsible operational team. |
| Jean Berchmans Bahige | **Verified:** December 2025 account identifies him as Commercial Services Director and outgoing acting MD; he is a co-author of the Kigali paper. [Appointment][wasac-appointment], [paper][kigali-paper] | Understand customer/billing records and the earlier project. |
| Dr. Asaph Kabaasha | **Verified:** named WASAC Group CEO in the May 2026 Labour Day account. [Official account][wasac-ceo] | Institutional sponsorship if a suitable pilot and data owner are identified. |
| Cenfri RED / WASAC partnership team; Hennie Bester | **Verified:** the October 2025 WASAC article identifies Bester as programme director. [MoU account][cenfri-mou] | Data inventory, integration and governance context. |
| JICA Rwanda water / KAIZEN team | **Verified:** relevant programmes are listed by JICA Rwanda. [Overview][jica-current] | Locate counterpart teams and retained project records. |
| Enabel CLIMURBA / MININFRA / WASAC project counterparts | **Verified:** Enabel's clarification assigns existing-data facilitation to MININFRA/WASAC. [Clarification][enabel-answers] | Clarify whether the prototype exists and whether any zone is suitable later. |

**Verified (source links):** WASAC publishes **info@wasac.rw** and **+250 788 181 427** at Centenary House, Nyarugenge. Cenfri publishes **info@cenfri.org** and its Kigali Heights office. [WASAC contact block][wasac-appointment], [Cenfri Rwanda][cenfri-rwanda]

**My inference:** these general institutional routes are preferable to invented personal emails or the emergency/anti-corruption lines. This report does not authorise or perform outreach.

## 6. Rechecking the September report's unverified claims

**Verified (local source link):** the inventory below covers the marked claims in [deep-research-report.md](/Users/uwonkundathierryrugira/Bubble-man/research/2026-09-28/deep-research-report.md), with source identification from its evidence log. Reverification means checking the attribution and scope; studies' published experiments were not independently reproduced.

### Rwanda and intermittent supply

| Earlier claim | Recheck |
|---|---|
| Cenfri MoU dates / mapping / NRW scope | **Verified:** confirmed above from WASAC's own dated announcement. [Source][cenfri-mou] |
| NRW composition | **Verified:** physical 80–90%, commercial 10–20%, for the **pilot areas**. [Brief, p. 8][jica-brief] |
| WASAC cannot sustain 24-hour supply | **Verified:** a historical project statement. **Unverified:** Kigali-wide 2026 conditions. Enabel supplies newer, limited evidence for its two study districts. [Brief, p. 14][jica-brief], [clarification][enabel-answers] |
| 35 electromagnetic + 1 ultrasonic + 2 mechanical meters; 29 pressure gauges | **Unverified:** exact inventory not reproduced from retrieved primary text. The full completion-report PDF timed out; the accessible journal text did not establish these counts. [JICA catalogue][jica-completion], [paper][kigali-paper] |
| Kigali branches cannot calculate separate NRW | **Verified:** dated to incomplete meters/customer-boundary work in 2022, not a current finding. [Brief, p. 13][jica-brief] |
| PRV trials reduced leakage 30–60% | **Verified:** the brief's narrative says this; its tables also include an **80%** night-flow reduction. Source discrepancy; avoid one unqualified range. [Brief, pp. 9–10][jica-brief] |
| NRW targets and results | **Verified:** Table 6 gives 37→20 target / 25 achieved and 68→25 target / 58 achieved. **My inference:** differences are **percentage points**. Earlier prose says 56% for Area 2; use the cited table, flag inconsistency. [Brief, pp. 8 and 11][jica-brief] |
| JICA study data cannot be public | **Verified:** the 2024 paper's availability statement says this for **that study**. It does not establish a blanket WASAC policy. [Paper][kigali-paper] |
| Enabel award / implementation unknown | **Unverified:** still not established; closed procurement and plans alone are insufficient. [Tender][enabel-tender] |
| Zarqa: tank filling invalidates one-day night-flow leakage estimation | **Verified:** paper supports the limitation; the study temporarily provided five days of continuous supply to saturate storage. Minimum times 00:15/04:45/07:15 and estimates 882.4→927.0 m³ also appear. **My inference:** the latter is about a 5% sensitivity, not detector accuracy. [Paper, pp. 3, 8 and 11][zarqa] |

### Other marked claims — attribution checks, no detector work

| Earlier claim | Recheck |
|---|---|
| 2026 review: 90 studies; median 97.2%; 25/40 above 95%; random/temporal split counts 32/9 | **Verified:** 90-study corpus. **Unverified:** the detailed numerical tallies and “only blind evaluation” wording were not reproduced in the retrieved primary text. Do not repeat them as established. [Review][review] |
| 2015 SPC: synthetic pressure EWMA works better; real flow bursts too small | **Verified:** author-institution abstract supports both, tied to its studied settings. Not a general impossibility result. [University publication record][spc2015] |
| “Ahn & Jun 2019”: coupling SPC helps | **Verified:** publisher abstract reports improvement on model-generated Austin data. Author is **Donghwi Jung**, not Jun. [Publisher issue/abstract][spc2019] |
| Vaquet et al.: weekends at short windows, seasonality at ≥2 weeks, small leaks hidden in model loss | **Verified:** these findings appear in sections 5.3 and 6.1 of their simulated-network study. [Authors' paper][drift] |
| Point adjustment can make random scores appear excellent | **Verified:** authors' abstract expressly reports this problem. [Paper][point-adjustment] |
| Wu & Keogh: triviality, density, labels, run-to-failure bias | **Verified:** paper identifies all four benchmark flaws. [Paper, p. 1][benchmarks] |
| Kapoor & Narayanan: 294 papers / 17 fields | **Verified:** published 2023 paper's public NSF record reports these. Their earlier arXiv abstract reports 329 instead; specify version rather than combine numbers. [Published paper record][leakage-published], [preprint][leakage-preprint] |
| Slovak data are scores; flow/pressure excluded; no label does not mean no leak | **Verified:** score-only public release and caution about missing fault labels. **Unverified:** exact exclusion claim not confirmed in retrieved text; do not treat it as a universal statement about flow usefulness. [Dataset metadata][slovak-data], [publisher text][slovak-paper] |
| Mazaev: controlled field experiments; some regions insensitive | **Verified:** release description supports both for the tested networks. No raw experiment files opened. [Release][mazaev] |
| No public intermittent-supply dataset with verified labels | **Unverified:** this review cannot establish global absence. The Zarqa paper is a study, not a confirmed complete labelled benchmark. |

**My inference:** the review's caution about incomparable evaluations remains useful. It does not justify attributing every high accuracy figure solely to lack of blind testing. Simulation results, real-system accuracy and warning yield are different measurements.

## 7. Remaining decisions and scope

**Unverified — information still needed:** a suitable current zone; meter/logging specification; retained readings and permission; supply/operating logs; storage and boundary completeness; incident-time definitions; vendor export costs; Enabel award status; exact historical equipment totals.

**My inference:** the founder and utility should choose the zone and data-sharing scope later. Existing historical monitoring makes that a concrete inquiry rather than a hardware-shopping exercise. The independent preparation backlog can continue while access remains unresolved.

**Verified (scope record):** no dataset download, account, form submission, message, sensor purchase, protected-file edit or evaluation occurred. Public document viewing was limited to sources under 200 MB; one 29.8 MB JICA document exceeded the browser's own limit and was not saved. Some publisher pages were blocked or incomplete; primary indexed text, institutional copies and accessible publisher PDFs were used where possible. Unresolved claims remain labelled rather than assumed true. This is bounded research, not an exhaustive audit of Rwanda's infrastructure.

[wasac-history]: https://wasac.rw/en/about/who-we-are
[wasac-nrw]: https://www.wasac.rw/en/public-information/tenders/tenderdetails/request-for-expressions-of-interest-re-advertisement-non-revenue-water-expert-1?cHash=7f890fed6af018574350aedf2410a453
[wasac-tenders]: https://www.wasac.rw/en/public-information/tenders
[wasac-appointment]: https://www.wasac.rw/en/public-information/news/d/cabinet-appoints-new-wasac-group-board-and-managing-director-for-wasac-utility?cHash=ca06a2489336ed789eb76227d5f8b9ab
[wasac-ceo]: https://www.wasac.rw/en/public-information/news/d/wasac-group-celebrates-labour-day-2026-with-a-call-to-enhance-service-delivery?cHash=bb02d08cbb43bde22b87f2806afa468c
[jica-brief]: https://www.jica.go.jp/oda/project/1502365/__icsFiles/afieldfile/oda/impfiles/r7mcj000000e0z3a-att/project_breaf_note_202202_en.pdf
[jica-completion]: https://openjicareport.jica.go.jp/618/618/618_412_12364485.html
[jica-current]: https://www.jica.go.jp/english/overseas/rwanda/activities/activity_08.html
[kigali-paper]: https://iwaponline.com/wpt/article/19/11/4328/105402/Cost-effective-non-revenue-water-reduction
[karongi]: https://www.wasac.rw/en/public-information/news/d/kivu-belt-water-supply-system-transforms-lives-in-karongi?cHash=b18ecc56b1959b19b8e0aec413acf120
[rura-stats]: https://www.rura.rw/sectors/water-sanitation/statistics
[rura-q2]: https://www.rura.rw/index.php?eID=dumpFile&f=121728&t=f&token=512aaa710a5c907731b0af935ed661b352ba1d11
[cenfri-mou]: https://www.wasac.rw/en/public-information/news/d/wasac-group-partners-with-cenfri-to-boost-data-driven-decision-making?cHash=c6d4b78245779e7df10c2edb65409b60
[cenfri-dashboard]: https://cenfri.org/articles/turning-data-into-decisions-lessons-on-dashboard-development/
[cenfri-rwanda]: https://cenfri.org/rwanda/
[climurba]: https://open.enabel.be/en/RWA/2715/updates/inclusive-and-climate-proof-urban-development-of-rwandese-secondary-cities.html
[enabel-tender]: https://www.enabel.be/tenders/consultancy-for-a-feasibility-study-digital-twin-development-and-detailed-design-for-real-time-water-network-monitoring-for-water-quality-and-leakages-detection-in-the-bugesera-and-rwamagana-water-d/
[enabel-answers]: https://www.enabel.be/app/uploads/2026/01/Proposed-Clarifications_Grouped-Answers.pdf
[ppiaf]: https://ppp.worldbank.org/public-private-partnership/sites/ppp.worldbank.org/files/2022-02/Rwanda-water-impact-stories-2.pdf
[zarqa]: https://mdpi-res.com/d_attachment/water/water-11-00048/article_deploy/water-11-00048.pdf
[review]: https://www.mdpi.com/2073-4441/18/18/2267
[spc2015]: https://experts.azregents.edu/en/publications/improving-the-rapidity-of-responses-to-pipe-burst-in-water-distri/
[spc2019]: https://ascelibrary.com/toc/jwrmd5/145/9
[drift]: https://arxiv.org/html/2401.01733v1
[point-adjustment]: https://arxiv.org/abs/2109.05257
[benchmarks]: https://arxiv.org/pdf/2009.13807
[leakage-published]: https://par.nsf.gov/servlets/purl/10513990
[leakage-preprint]: https://arxiv.org/abs/2207.07048
[slovak-data]: https://zenodo.org/records/15096167
[slovak-paper]: https://doi.org/10.1038/s41597-026-07203-5
[mazaev]: https://zenodo.org/records/7255403
