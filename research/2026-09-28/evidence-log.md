# Evidence log — 28 September 2026

Search date: 2026-09-28. Method: automated fan-out research workflow (6 search angles,
25 sources fetched). **The adversarial verification stage failed** — 74 of 106 agents
stopped on an organisation monthly spend limit. Claims below marked `[V]` were
re-verified by hand against the primary source on 2026-09-28; `[U]` means single-source,
unverified.

## Primary sources verified by hand

| # | Source | Finding | Status |
|---|---|---|---|
| 1 | [BattLeDIM results paper, Zenodo 6641304](https://zenodo.org/records/6641304) (PDF, Vrachimis et al., dated 24 May 2022) | Tongji-Team TPR 56.52%, 3 FP, €264,873. Under Pressure TPR 65.22%, 4 FP, €260,562. Perfect score €523,124 (text) / €523,154 (Table 4). "best solutions in BattLeDIM achieved a score around 50%" | `[V]` |
| 2 | same | True detection: `t_start ≤ t_detect ≤ t_end` AND `x ≤ x_max`; `x_max = 300 m`; water €0.80/m³; crew €500 max | `[V]` |
| 3 | same | "Once a leak is detected, it is added to the list Ld. Successful detections of leaks in Ld are given a score of zero (0), i.e., repeated detections of the same leakage are ignored." | `[V]` |
| 4 | same | "A decision was made in the creation of this benchmark to not include sensor time-delays and errors." | `[V]` |
| 5 | Local `battledim-config.yaml` | 2018: 14 leaks (6 abrupt, 8 incipient). 2019: 19. Four 2018 leaks run to 2019-12-31 (p257, p427, p654, p810) | `[V]` |

## Conflicts found

- **Detection time window.** [Competition website page_id=144](https://battledim.ucy.ac.cy/?page_id=144)
  says "within Tmax=1, a week of the start of the leak". The **published paper**
  (eq. 5a) uses the full leak lifetime with no one-week cap. Website appears to be an
  earlier draft rule. **Resolution: use the paper.** `[V]`
- **Perfect score.** €523,124 in running text vs €523,154 in Table 4 of the same paper.
  Immaterial; noted for accuracy. `[V]`

## Single-source findings (not cross-checked)

| Source | Finding |
|---|---|
| [MDPI Water 18(18):2267](https://www.mdpi.com/2073-4441/18/18/2267) (2026-09-11 review, 90 studies) | Median headline accuracy 97.2%; >95% in 25 of 40; BattLeDIM "the only blind evaluation identified" at 65.22%. Random splits in 32 studies, temporal hold-out in 9, unclear in 42. Pressure used in 48 studies, acoustic 35, flow only 4. |
| [MDPI Water 11(1):48](https://www.mdpi.com/2073-4441/11/1/48) (Zarqa, Jordan) | One-day MNF invalid under intermittent supply — night flow refills customer tanks. MNF clock time shifted 00:15 / 04:45 / 07:15 across days. 1.5h→2h assumption moved leakage estimate 882→927 m³. |
| [arXiv 2401.01733](https://arxiv.org/pdf/2401.01733) (Vaquet et al.) | Model-loss drift detection suits only large leaks. 1-day window flags weekends; ≥2-week window lets seasonality dominate the leak. |
| [J. Hydroinformatics 17(2):307](https://iwaponline.com/jh/article/17/2/307/3245/Improving-the-rapidity-of-responses-to-pipe-burst) (2015) | EWMA on nodal pressure best on synthetic data; on the real system "burst flows are proportionally too small to be detected". |
| [ASCE JWRPM 145(9)](https://doi.org/10.1061/(ASCE)WR.1943-5452.0001104) (Ahn & Jun 2019) | Coupling SPC methods improves detection probability while reducing false alarms and delay. |
| [arXiv 2109.05257](https://arxiv.org/abs/2109.05257) (Kim et al., AAAI 2022) | Point adjustment turns random scores into "state-of-the-art". Do not use. |
| [arXiv 2009.13807](https://arxiv.org/abs/2009.13807) (Wu & Keogh) | Anomaly benchmarks suffer triviality, unrealistic density, mislabeled truth, run-to-failure bias. |
| [Patterns 2023](https://www.cell.com/patterns/fulltext/S2666-3899(23)00159-9) (Kapoor & Narayanan) | Leakage found in 17 fields, 294 papers. Temporal leakage and preprocessing-on-full-data are the relevant modes. |
| [Zenodo 15096167](https://zenodo.org/records/15096167) / [Sci Data](https://www.nature.com/articles/s41597-026-07203-5) | Real Slovak utility, 1 yr hourly. Published as 0–100 anomaly scores, not raw units. Flow and pressure excluded as not significant. "absence of a fault_d7 = 1 label does not imply leak-free operation." |
| [Zenodo 7255403](https://zenodo.org/records/7255403) (Mazaev et al.) | Controlled leak experiments in operational networks. "large parts of the network were insensitive to leaks". CC BY 4.0. |
| [JICA brief 2022](https://www.jica.go.jp/oda/project/1502365/__icsFiles/afieldfile/oda/impfiles/r7mcj000000e0z3a-att/project_breaf_note_202202_en.pdf) | WASAC cannot supply 24h/day; physical loss 80–90% of NRW; Kigali branches cannot calculate NRW separately; PRV trial cut leakage 30–60%. |
| [Water Practice & Technology 19(11):4328](https://doi.org/10.2166/wpt.2024.263) | Kigali monitoring: 35 electromagnetic + 1 ultrasonic + 2 mechanical flow meters, 29 pressure gauges. NRW targets 17% / 43%; achieved 12% / 10%. Data not publicly available. |
| [WASAC news](https://www.wasac.rw/en/public-information/news/d/wasac-group-partners-with-cenfri-to-boost-data-driven-decision-making) | WASAC–Cenfri MoU signed 2025-05-27, runs to 2027-04-30. Network mapping and NRW cause analysis in scope. |

## Unresolved questions

1. Enabel Bugesera/Rwamagana tender — **no award or implementation status found.**
   Must be asked directly, not inferred.
2. No public dataset found with **intermittent supply AND verified leak labels.**
   This is the central gap for Rwanda relevance.
3. Mazaev dataset file structure not yet audited — column definitions, sensor coverage,
   experiment splits unknown.
4. Whether any BattLeDIM team published per-leak detection delays (the paper reports
   TPR and economic score, not delay distributions).
5. Whether WASAC's Kigali DMA telemetry is retained at sub-daily resolution. The JICA
   material describes **monthly** NRW calculation, which would be far too coarse.

## Research process failure, recorded

The verification stage of the workflow did not run. Anything marked `[U]` above has the
same status as a single unchecked citation. Before any of it is used to justify a
design decision, verify it as I did for the BattLeDIM figures.
