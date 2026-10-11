# Public real-network datasets for Bubble Man

Iteration 1 — metadata research checked 11 October 2026. No dataset files were downloaded, no flow or repair rows were inspected, and no detector was run. Public documentation, repository file metadata, published research, service schemas and one HTTP HEAD response were examined.

## Read this first

**Verified (source links):** three public releases describe real zone flow measurements paired with repair or leak records: [Yorkshire Water](https://datamillnorth.org/dataset/yorkshire-water-leakage-dma-15-minute-data-2zlgn), [Wessex Water's four zone packages](https://www.arcgis.com/sharing/rest/content/items/6d5a3e47147f4ebbac3115d623e7fc6e?f=json), and [KIOS's Cyprus dataset](https://github.com/KIOS-Research/Leakage-Repairs-Dataset).

**My inference:** these are meaningful routes to a first real-data check. The claim that progress depends entirely on getting a private utility export is now too restrictive. They do not yet establish compatibility with our frozen software, trustworthy leak onset times, or performance in Rwanda.

**Unverified:** none is confirmed here to contain independently recorded first-report times, a complete incident history, a full year of usable readings for a selected zone, and every operating condition the pilot needs. No release is marked ready for evaluation.

### Meaning of the evidence labels

- **Verified (source link)** means the named primary source states the fact, or a specified metadata response was observed. It does not mean that the underlying measurements or labels were independently audited.
- **Unverified** means the fact was not established from the inspected documentation. Unknown is not equivalent to absent.
- **My inference** means a judgement about suitability, access priorities or what a result could mean.

## Shortlist

| Priority — my inference | Candidate | Why investigate it next — my inference | Main unresolved issue |
|---|---|---|---|
| 1 | Yorkshire Water | A documented year of fine-resolution zone flows makes it the strongest immediate compatibility lead. | Repair completion dates cannot establish warning lead time before first report. |
| 2 | Wessex Water zone packages | Flow, actual pressure readings, jobs and repair schemas are provided together. | Published end date and export size unknown; `Burst_Date` needs a definition. |
| 3 | KIOS Cyprus | Small individual files and a clear licence make access straightforward. | Duration and report timestamp meaning unknown; inferred leak periods risk circular evaluation. |

## 1. Yorkshire Water: Leakage DMA 15 Minute Data

| Required field | Finding and evidence |
|---|---|
| Real network / contents | **Verified:** regional zone flows, property summaries and mains repair completion dates. [Government catalogue](https://www.data.gov.uk/dataset/27eed403-aee2-458d-94e4-d6840c14adfd/yorkshire-water-leakage-dma-15-minute-data). |
| Interval / units / quality | **Verified:** 15-minute flow in L/s; V = valid, I = invalid, M = missing. [Catalogue](https://www.data.gov.uk/dataset/27eed403-aee2-458d-94e4-d6840c14adfd/yorkshire-water-leakage-dma-15-minute-data). |
| Length | **Verified:** publisher resource descriptions specify April 2016–March 2017. **Unverified:** completeness and timezone behaviour for any chosen zone. [Publisher](https://datamillnorth.org/dataset/yorkshire-water-leakage-dma-15-minute-data-2zlgn). |
| Licence | **Verified:** publisher's licence link points to CC BY 4.0. The government catalogue's empty licence field is not the primary licence statement. [Publisher](https://datamillnorth.org/dataset/yorkshire-water-leakage-dma-15-minute-data-2zlgn). |
| Size | **Verified:** publisher lists 20 regional flow CSVs, labelled about 97.14–200.27 MB, plus an 83.23 kB repair CSV and property tables. Its display units are not assumed to be decimal bytes. [Publisher](https://datamillnorth.org/dataset/yorkshire-water-leakage-dma-15-minute-data-2zlgn). |
| Event times | **Verified:** completion dates. **Unverified:** onset, first-report time, confirmation time and whether every recorded repair addressed leakage. [Catalogue](https://www.data.gov.uk/dataset/27eed403-aee2-458d-94e4-d6840c14adfd/yorkshire-water-leakage-dma-15-minute-data). |
| Fit | **My inference:** promising for unchanged flow-rule compatibility and repair-associated diagnostics. It cannot presently support our desired “warning before first report” endpoint. |

**Verified (source link; HEAD only):** the [Area N4 resource](https://datamillnorth.org/download/2zlgn/7728e628-f816-4fe4-99f1-648af54df878/N4%202016_2017.csv) returned HTTP 200, `text/csv`, and `Content-Length: 101862786`. That is 101.86 decimal MB, or 97.14 MiB. No response body was requested. This checks one public flow endpoint, not all files or the repair download.

**Verified (source link):** a research paper using this release says repair timestamps and reasons are unavailable; repairs can occur hours, days or weeks after a leak becomes noticeable. The authors infer leakage intervals from flow behaviour rather than treating repair dates as onset. [McMillan et al., dataset discussion](https://researchportal.northumbria.ac.uk/ws/portalfiles/portal/165093893/1-s2.0-S0043135423014239-main.pdf).

**My inference:** selecting a region by small file size can be justified before seeing outcomes. Selecting a zone because its plots have an obvious repaired leak would flatter the test. UK clock changes, signed net flow, quality flags and any storage still need assessment. A metadata refresh in 2026 does not make these historical readings recent.

## 2. Wessex Water: four actual zone packages

**Verified (source links):** each package is public and declares CC BY 4.0. Publisher descriptions identify recorded measurements and operational records from an actual water zone. The word “Scenario” in the title does not make all of its contents simulated. Metadata was checked for [zone package 1](https://www.arcgis.com/sharing/rest/content/items/6d5a3e47147f4ebbac3115d623e7fc6e?f=json), [2](https://www.arcgis.com/sharing/rest/content/items/67b74ac6fc874c1b862f88e96bc861a4?f=json), [3](https://www.arcgis.com/sharing/rest/content/items/e8043c40f5c343fa889e771b43056dee?f=json) and [4](https://www.arcgis.com/sharing/rest/content/items/34a9a72ab24c41f1b8d5968119d0c985?f=json).

| Required field | Finding and evidence |
|---|---|
| Contents | **Verified:** measured flow/pressure, asset and model information, `Scenario_Jobs`, and `Scenario_Repairs`. [Package 1 metadata](https://www.arcgis.com/sharing/rest/content/items/6d5a3e47147f4ebbac3115d623e7fc6e?f=json), [service schema](https://services.arcgis.com/3SZ6e0uCvPROr4mS/arcgis/rest/services/Wessex_Water_Leakage_Scenario_1_Data_/FeatureServer?f=json). |
| Interval / length | **Verified:** measured readings every 15 minutes from 1 April 2025 00:00; job selection also starts then. **Unverified:** final reading date, continuous duration and completeness. [Package 2 description](https://www.arcgis.com/sharing/rest/content/items/67b74ac6fc874c1b862f88e96bc861a4?f=json). |
| Licence / size | **Verified:** CC BY 4.0. **Unverified:** actual export bytes. ArcGIS item `size: 0` is not evidence of an empty dataset or a zero-byte export. [Package 3 metadata](https://www.arcgis.com/sharing/rest/content/items/e8043c40f5c343fa889e771b43056dee?f=json). |
| Event times | **Verified:** job description refers to resolution dates. **Unverified:** `Burst_Date`'s operational meaning, onset and first-report times. [Package 4 description](https://www.arcgis.com/sharing/rest/content/items/34a9a72ab24c41f1b8d5968119d0c985?f=json), [repair schema](https://services.arcgis.com/3SZ6e0uCvPROr4mS/arcgis/rest/services/Wessex_Water_Leakage_Scenario_1_Data_/FeatureServer/5?f=json). |
| Fit | **My inference:** the richest compatibility lead; insufficient metadata to confirm the roughly year-long input the current tools require. |

**Verified (source link):** [flow schema](https://services.arcgis.com/3SZ6e0uCvPROr4mS/arcgis/rest/services/Wessex_Water_Leakage_Scenario_1_Data_/FeatureServer/6?f=json) lists reading time, type, asset, measure, unit and value. No quality-flag column is exposed there. **Unverified:** whether corrections can be identified elsewhere or whether all listed meters belong in the zone balance.

**My inference:** use measured telemetry for a real-data test. The separately named `Model_Pressure_24hr` represents a model's typical day and would not be independent real pressure evidence. Do not assume `CUS` customer loggers should be subtracted as boundary outlets. Spatial coordinates have been shifted, so actual geographic pipe-location claims would also need caution. [Publisher's distinctions](https://www.arcgis.com/sharing/rest/content/items/6d5a3e47147f4ebbac3115d623e7fc6e?f=json).

## 3. KIOS: Cyprus Leakage-Repairs-Dataset

| Required field | Finding and evidence |
|---|---|
| Contents | **Verified:** publisher describes actual Cyprus zone inlet measurements paired with processed repair logs. [README](https://github.com/KIOS-Research/Leakage-Repairs-Dataset). |
| Interval / length | **Verified:** five-minute inlet readings. **Unverified:** calendar range, usable duration, units and supply continuity. [README](https://github.com/KIOS-Research/Leakage-Repairs-Dataset). |
| Licence | **Verified:** README declares CC BY 4.0. [README](https://github.com/KIOS-Research/Leakage-Repairs-Dataset). |
| Size | **Verified:** six raw-flow CSVs of 7,263,464–10,551,185 bytes, totalling 56,545,782 bytes; one 285,983-byte processed report CSV. Together 56,831,765 bytes (~56.83 decimal MB). [GitHub file metadata](https://api.github.com/repos/KIOS-Research/Leakage-Repairs-Dataset/git/trees/main?recursive=1). |
| Event times | **Verified:** published code expects a report `timestamp`. **Unverified:** whether it means first report, inspection, work order or repair completion. [Processing entry point](https://github.com/KIOS-Research/Leakage-Repairs-Dataset/blob/main/preprocessing/pipeline.py). |
| Fit | **My inference:** potentially useful raw telemetry plus incident records; proceed only after clarifying timestamp meaning and period length. |

**Verified (source link):** metadata was checked at repository revision `6d560fc0c5cc9694d5be1ddc3fa3c8aa649c5bcc`; its tree was not truncated. The processed-flow directory contains a placeholder, while raw-flow files and a processed report file are listed. File presence and sizes do not prove data quality. [Revision tree](https://api.github.com/repos/KIOS-Research/Leakage-Repairs-Dataset/git/trees/6d560fc0c5cc9694d5be1ddc3fa3c8aa649c5bcc?recursive=1).

**Verified (source link):** the public processing code matches report dates to night-flow drops and estimates leak periods using those readings. [Label construction code](https://github.com/KIOS-Research/Leakage-Repairs-Dataset/blob/main/preprocessing/leak_detector.py).

**My inference:** leak starts inferred from the same flow signal are not independent answers for a flow detector. Use independently understood report/repair timestamps as uncertain event evidence. Do not adopt these inferred onset labels or the repository's interpolation and cleaning rules as our evaluation truth. This is a limitation of a proposed test, not a claim that the published dataset is fabricated.

## Other leads screened

**My inference:** none of the following is currently a verified complete substitute for a real zone-flow-plus-event-record test. Every required metadata field is retained even when unknown.

| Lead | Contents / interval / length | Licence / size | Event-time meaning / fit |
|---|---|---|---|
| [Wessex daily zone data](https://www.arcgis.com/sharing/rest/content/items/7103d8ee6c114bc29c33f84b47294987?f=json) | **Verified:** daily night-flow and derived leakage summaries for four zones. **Unverified:** full calendar span. | **Verified:** CC BY 4.0. **Unverified:** export bytes. | **Unverified:** paired incident timing in this separate summary product. **My inference:** useful context, but daily summaries cannot reproduce the frozen rule's full daily-shape inputs. Use the measured packages above. |
| [Affinity night-flow monitoring metadata](https://www.arcgis.com/sharing/rest/content/items/db5976c9e50e42f299346fa17ff17942?f=json) | **Verified:** derived night-flow series, monthly publication; documentation warns of automatic infilling. **Unverified:** reading interval and full span. | **Verified:** CC BY 4.0; item metadata size 185,925,632 bytes. **Unverified:** export size (service size is not a download estimate). | **Unverified:** matching repair records or onset/report definitions. **My inference:** telemetry lead, insufficient event evidence for the planned evaluation. |
| [South East Water distribution input](https://opendata.southeastwater.co.uk/datasets/distribution-input/) | **Verified:** 2023 daily company totals, although upstream readings are collected every 15 minutes; some gaps are filled. | **Verified:** portal links an Open Data Licence. **Unverified:** applicable terms and bytes of the listed bundle. | **Unverified:** matching zone-level event history. **My inference:** company totals cannot identify a bounded zone or reconstruct nightly readings. |
| [Ofwat leakage dataset](https://www.ofwat.gov.uk/publication/leakage-dataset-june-2025/) | **Verified:** annual company leakage performance, 1992–2024. | **Verified:** listed size 157.52 KB. **Unverified:** dataset-specific licence. | **My inference:** sector context; annual totals cannot score timed zone warnings. **Unverified:** any event records in this release. |
| [Babela et al. urban-network dataset](https://zenodo.org/records/15096167) | **Verified:** hourly anomaly scores and a ±7-day event-proximity label. **Unverified:** exact calendar span. | **Verified:** CC BY 4.0; [metadata](https://zenodo.org/api/records/15096167) lists 818,525-byte CSV and 1,441-byte README. | **Unverified:** original event timestamp meaning. **My inference:** scores are not raw inlet measurements; proximity labels are not precise onset/report records. |
| [Mazaev et al. field experiments](https://zenodo.org/records/7255403) | **Verified:** field pressure measurements and simulated pressure scenarios. **Unverified:** sampling interval, full duration and suitable inlet telemetry. | **Verified:** CC BY 4.0 and 195,518,700-byte archive in [metadata](https://zenodo.org/api/records/7255403). | **Verified:** controlled field-leak experiments are described. **Unverified:** exact start-time semantics. **My inference:** potential later pressure work, not a verified current flow-rule dataset. |
| [Hera real-zone research](https://cris.unibo.it/retrieve/handle/11585/1020130/04e14314-1b2c-4621-9780-4bdd0ce09769/Combining%20SCADA%20and%20smart%20meter%20data%20to%20improve%20anomaly%20detection.pdf) | **Verified:** study used real 15-minute net flow, January 2022–July 2024, plus repair logs. | **Unverified:** public data release, data licence and size. The accessible paper is not the dataset. | **Unverified:** first-report versus completion time. **My inference:** an academic partnership lead, not data we can access here without asking. |

**Verified (source link):** [LeakDB's primary description](https://zenodo.org/records/1313116) explicitly identifies artificially created scenarios. **My inference:** more such scenarios would not satisfy this search for real operating data. Existing simulated evaluations remain outside this iteration.

## What a human decision would enable later

**My inference:** investigate Yorkshire's licence and one region's format first; inspect Wessex's calendar coverage and recorded-date definitions next; clarify the Cyprus report meaning before relying on its labels. This ranking is based on metadata, not on observed leak outcomes.

**Unverified — questions before any real evaluation:**

1. Which zone has a complete metered boundary, continuous supply, no uncorrected internal storage and enough history?
2. Are timestamps actual measurements, interval endpoints or estimated values? What timezone and clock-change convention apply?
3. Do event records distinguish first report, confirmation, repair start and completion? Can leakage-related work be distinguished from other work?
4. Are the logs complete enough to interpret missing records? Can the provenance of any inferred leak labels be kept separate?
5. What bytes would be transferred, and what attribution is required? Wessex export sizes remain unknown.

**My inference:** completion-only records support a limited repair-associated analysis, with unmatched warnings kept unknown. They cannot establish how much earlier an operator would have been alerted than the first report. Define that limited question in a new protocol before exposing event rows. A result in another country would still require testing under Rwanda's operating conditions.

**Verified — scope record:** no dataset CSV or archive was saved or made available for inspection. There were no repository clones, service feature-row queries, account creation, messages, forms or detector execution. One attempted browser open of the Yorkshire CSV returned an unsupported-content-type error; no rows were delivered. The subsequent access check used a separate HEAD request, which inspected headers only. Accessing data or contacting authors is outside this completed metadata-search item and remains subject to the goal's restrictions.

## Search coverage and reproducibility

**Verified — research activity:** searches covered UK water-company portals and Stream, government open-data catalogues, Zenodo, publisher repositories and academic supplements. General queries included “real water distribution dataset DMA flow time series burst repair records public dataset”, “UK water company open data district metered area flow leakage repair dataset”, and “public real water distribution flow leakage dataset SCADA repair logs”. Third-party indexes were used for discovery; the shortlist was checked against primary pages or APIs.

**Unverified:** the search is not an exhaustive inventory of every public utility dataset. Public availability, licences and metadata may change. Where the browser could not render ArcGIS/GitHub metadata, small public metadata JSON responses were read in memory and their relevant fields recorded above. No subscription, contact or data-file access is claimed.
