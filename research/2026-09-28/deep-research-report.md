# Bubble-man deep research review

**Search date: 28 September 2026.** Sources fetched and quoted on that date.

**Status of this report.** A fan-out research workflow ran 106 agents. The search and
fetch stages completed (25 sources, ~125 extracted claims). The adversarial
verification stage failed almost entirely — 74 agents died on an organisation
monthly spend limit. So the automated "2 of 3 verifiers must refute" safety net did
**not** run. I therefore re-verified the load-bearing numbers by hand against primary
sources; those are marked **[verified]**. Claims marked **[unverified]** come from a
single fetched source and have not been cross-checked. Treat them accordingly.

---

## 1. Briefing in plain language

**The most useful single number.** BattLeDIM — the competition built on the exact
dataset we are using — was won with a **true positive rate of 65.22%, with 4 false
positives**, and the organisers state the best entries scored **about 50% of a
perfect score**. **[verified]** These were research teams with calibrated hydraulic
models, customer meter data and months of work.

That reframes our own expectations. We are not behind. A simple, honest method that
catches some leaks is a reasonable object of study, because even the best entrants
missed a third of them.

**The most useful warning.** A 2026 systematic review of 90 leak-detection studies
found a median headline accuracy of **97.2%**, with 25 of 40 studies reporting above
95% — while noting BattLeDIM was "the only blind evaluation identified" and topped out
at 65.22%. **[unverified, single source]** The gap is not because those methods are
better. It is because most were not evaluated blind. In the same review, 32 studies
used a **random** train/test split on time-series data; only 9 used a temporal
hold-out.

**What this means for us.** The dangerous mistake in this field is not a weak
detector. It is an evaluation that flatters a weak detector. We have already walked
into a small version of this ourselves: I ranked methods by "which produces the
calmest difference", and that criterion rewarded a rolling baseline for quietly
absorbing the leaks it was supposed to find.

**Recommendation: build the scorer before building another detector.** Details in §5.

---

## 2. What the evidence says, method by method

### Expected-flow baseline (what we built)
Learn typical flow for each hour and day type; flag departures. Needs only inlet flow
and a few weeks of history. Detects sustained increases; cannot locate. Fails when the
training period itself contains leaks — ours did — and when demand or operations shift.
**Appropriate for our stage.** This is the standard starting point, not a naive one.

### Minimum night flow (MNF)
At 02:00–04:00 most taps are shut, so remaining flow is mostly leakage.

**This is the finding most relevant to Rwanda.** A study of an intermittent-supply DMA
in Zarqa, Jordan states: *"One-day minimum night flow analysis (MNF) cannot be used to
estimate the leakage rate in intermittent supplies, because water keeps flowing during
night time to fill customers' tanks."* **[unverified, single source]**
[MDPI Water 11(1):48](https://www.mdpi.com/2073-4441/11/1/48)

The same study found the clock time of the minimum shifted between 00:15, 04:45 and
07:15 on consecutive days, and that changing the assumed night-consumption window from
1.5 h to 2 h moved the leakage estimate from 882 m³ to 927 m³ — a 5% swing from one
modelling choice.

**Implication:** a fixed 02:00–04:00 window is a continuous-supply assumption. In
Rwanda it may measure tank refilling, not leakage. Our Step B used exactly that fixed
window.

### Persistence rules, CUSUM, EWMA
Statistical process control: compare against historic mean and variance, require the
departure to persist.

- A 2015 comparison of six SPC methods: *"Synthetic data analyses suggest that the
  univariate EWMA method using nodal pressure provides the highest detectability"* —
  but on the **real** system, *"burst flows are proportionally too small to be
  detected."* **[unverified]**
  [J. Hydroinformatics 17(2):307](https://iwaponline.com/jh/article/17/2/307/3245/Improving-the-rapidity-of-responses-to-pipe-burst)
- Ahn & Jun (2019) found coupling two SPC methods with different characteristics
  *"can significantly improve pipe burst detection probability while reducing false
  alarm rates and average detection time."* **[unverified]**
  [ASCE JWRPM 145(9)](https://doi.org/10.1061/(ASCE)WR.1943-5452.0001104)

The synthetic-vs-real gap in the first study is the whole story in miniature.

### Change-point / drift detection
Vaquet, Hinder & Hammer tested drift detection on simulated networks:
*"model-loss-based detection schemes are only suitable for detecting large leakages…
the models generalize too well to out-of-distribution samples to reliably detect small
leakages."* And critically for us: *"a short window of just one day indicates drifts at
the weekends, while for a window length of two weeks (or more), the drift induced by
seasonal effects becomes stronger than the effect of the leak."* **[unverified]**
[arXiv 2401.01733](https://arxiv.org/pdf/2401.01733)

**This independently predicts our own result.** Window length is the dominant design
choice, and a two-week window is where the leak signal starts losing to everything else.
Our rolling 14-day baseline sat exactly on that boundary.

### Multi-sensor evidence, hydraulic models, machine learning
BattLeDIM's leading entries combined calibrated EPANET models with customer meter data
and residual analysis. That is where locating (as opposed to detecting) comes from. It
is also far beyond our current stage and requires a network model we do not have for
any Rwandan zone.

### Detect / locate / predict — keep these separate
- **Detect**: something is wrong in this zone. Flow alone can do this.
- **Locate**: which pipe. Needs pressure sensors *and* a calibrated hydraulic model.
- **Predict future failure**: which pipe will break next. Needs years of asset and
  break history. A different project; ignore for now.

Our work is detection only.

---

## 3. Evaluation: how this field goes wrong

### BattLeDIM's own scoring rule **[verified, from the published paper]**
- A detection is a **true positive** if `t_start ≤ t_detect ≤ t_end` and the isolated
  link is within `x_max = 300 m` of the leak.
- *"Once a leak is detected, it is added to the list Ld. Successful detections of
  leaks in Ld are given a score of zero (0), i.e., repeated detections of the same
  leakage are ignored."* — this is the alert-grouping rule we needed.
- Economic score = water saved from detection onward (€0.80/m³) minus crew cost
  (up to €500 per assignment), so **earlier detection scores higher** without a hard
  deadline.
- *"A decision was made in the creation of this benchmark to not include sensor
  time-delays and errors."* Real telemetry is messier than this dataset.

**Conflict found and resolved.** The competition website
([page_id=144](https://battledim.ucy.ac.cy/?page_id=144)) describes a true detection as
*"within Tmax=1, a week of the start of the leak."* The **published paper's** equation
5a uses the full leak lifetime (`t_start ≤ t_d ≤ t_end`), with no one-week cap. The
website text appears to be an earlier illustrative version. **Use the paper's rule.**

**Minor internal inconsistency in the paper itself:** the running text gives the perfect
score as €523,124, Table 4 gives €523,154. Immaterial, but noted.

**Arithmetic check (my inference).** 2019 contains 19 new leaks plus 4 carried over from
2018 that never end (p257, p427, p654, p810) = 23. 15/23 = 65.22%, 13/23 = 56.52%.
The reported rates are consistent with the configuration file we hold.

### Metric traps
- **Point adjustment** — the default protocol in time-series anomaly detection — was
  shown to award near-perfect F1 to *random* scores: *"even a random anomaly score can
  easily turn into a state-of-the-art TAD method."* **[unverified]**
  [arXiv 2109.05257](https://arxiv.org/abs/2109.05257). **Do not use point adjustment.**
- Wu & Keogh argue most anomaly-detection benchmarks suffer triviality, unrealistic
  anomaly density, mislabeled ground truth and run-to-failure bias. **[unverified]**
  [arXiv 2009.13807](https://arxiv.org/abs/2009.13807)
- Kapoor & Narayanan document leakage across 294 papers in 17 fields; temporal leakage
  and preprocessing-on-full-dataset are the two that threaten us. **[unverified]**
  [Patterns 2023](https://www.cell.com/patterns/fulltext/S2666-3899(23)00159-9)

### Review of our own experiment

| Assumption we made | Verdict |
|---|---|
| One training week is enough | **No.** Feb week gave 4.44 m³/h error, Jan week 12.79. Same method. |
| The baseline period was quiet | **No.** Four gradual leaks ran in it; known leakage grew 2.5 → 15.2 m³/h. |
| Smaller spread = better method | **No.** The rolling baseline scored best by absorbing the leaks. |
| Hourly averaging is harmless | Costs up to an hour of delay. Acceptable for now; state it. |
| Fixed 02:00–04:00 night window | Continuous-supply assumption. Fine for L-Town, unsafe for Rwanda. |

**What our experiment currently supports:** that a leak-sized change is visible by eye
in one known case, and that method choice and training period matter a great deal.
**What it cannot establish:** any detection rate, delay, or false-alarm rate whatsoever.
We have never scored a detection.

---

## 4. Datasets

| Dataset | Data origin | What it gives | Verdict |
|---|---|---|---|
| [BattLeDIM / L-Town](https://zenodo.org/records/4017659) | **Simulated** (EPANET model based on a real Cyprus network) | 2018+2019, 5-min, 33 pressure / 3 flow / 1 tank / 82 AMR; 33 labelled leaks, 15 abrupt 18 incipient | **Use now.** Best labels, and a published scoring rule. |
| [LeakDB](https://zenodo.org/records/13985057) | Simulated | Many scenarios; 13.9 GB full | Later robustness. Start with the GitHub sample. |
| [Mazaev et al.](https://zenodo.org/records/7255403) | **Controlled field experiments in operational networks** | Real pressure; simulated comparison; 195 MB | **Best reality check available.** Notes *"large parts of the network were insensitive to leaks."* |
| [Lab testbed](https://data.mendeley.com/datasets/tbrnp6vrnj/1) | Physical lab rig | 280 short acoustic/pressure signals | Only if we pursue acoustics. |
| [Slovak utility multi-source](https://zenodo.org/records/15096167) | **Real utility SCADA**, 1 year hourly | Flow, pressure, energy, groundwater; labels = ±7 days around confirmed leaks | **Newly found. Worth a look.** Caveats below. |

**New find, with a serious caveat.** The Slovak dataset is genuine utility telemetry with
leaks confirmed from a work-order system. But the published variables are **anomaly
scores on a 0–100 scale, not raw measurements**, and the authors state flow and pressure
*"did not meet the selection thresholds and were excluded"* as not statistically
significant. They also warn: *"The absence of a fault_d7 = 1 label does not imply
leak-free operation."* **[unverified]** So it cannot replace L-Town for our purpose, but
it is honest about label quality in a way simulations cannot be.

**No dataset found with intermittent supply and verified leak labels.** This is a real
gap. The Zarqa study describes intermittent supply but does not publish a labelled
dataset.

---

## 5. Rwanda

**Verified current.** WASAC and Cenfri signed an MoU on 27 May 2025 running to 30 April
2027, covering a data strategy, network mapping and investigation of NRW causes.
**[unverified, single source]**
[WASAC news](https://www.wasac.rw/en/public-information/news/d/wasac-group-partners-with-cenfri-to-boost-data-driven-decision-making)

**Historical, tied to a specific project.** A JICA NRW programme in Kigali reports:
physical losses are **80–90% of NRW** with commercial losses 10–20%; WASAC *"cannot
supply clean water to its customers stably through 24 hours daily"*; monitoring
equipment installed comprised 35 electromagnetic flow meters, 1 ultrasonic, 2
mechanical and 29 pressure gauges; and Kigali branches *"cannot calculate the NRW rate
separately."* PRV trials reduced leakage 30–60%. **[unverified]**
[JICA brief](https://www.jica.go.jp/oda/project/1502365/__icsFiles/afieldfile/oda/impfiles/r7mcj000000e0z3a-att/project_breaf_note_202202_en.pdf),
[Water Practice & Technology 19(11)](https://doi.org/10.2166/wpt.2024.263)

**Sobering:** that project's NRW reduction targets were 17% and 43%; achieved were 12%
and 10%. And its data *"cannot be made publicly available."*

**Still unverified.** The Enabel Bugesera/Rwamagana tender outcome. No award or
implementation status found.

**What intermittent supply does to our method (my inference, grounded in the Zarqa
study):** after a supply interruption, refilling customer rooftop tanks produces a
large, sustained, network-wide flow increase — the exact signature we are training a
detector to flag. Any Rwandan deployment needs the supply schedule as an input, not as
an afterthought. A detector without it will mostly detect the supply schedule.

---

## 6. Ideas worth a small experiment, ranked

1. **Event-level scorer using BattLeDIM's own rule.** Problem: we cannot compare
   methods honestly. Evidence: strongest in this report — the published rule is
   explicit. Effort: low, data in hand. Stop/go: if we cannot reproduce sensible
   scores on 2018, nothing downstream is trustworthy.
2. **Score frozen vs rolling baseline against the 14 known 2018 leaks.** Turns my
   qualitative "the rolling baseline absorbs leaks" into a measured detection rate.
   Effort: low, once (1) exists.
3. **Adaptive night window instead of fixed 02:00–04:00.** Evidence: Zarqa shows the
   minimum moves by hours. Effort: low. Directly de-risks the Rwanda transfer.
4. **Multi-meter agreement (p227 + p235 + PUMP_1).** We have used one of three meters.
   Requiring two to agree is the cheapest false-alarm reduction available.
   Effort: low-medium.
5. **Mazaev controlled-field data as a reality check.** Evidence: only real-leak data
   we can access. Effort: medium — needs a file-level audit first.

**On using a language model (Jev or otherwise).** Nothing found changes the
preparation document's position, which is correct: compute all numbers in ordinary
code, and treat any model confidence as an opinion, not a calibrated probability.
There is no measurable role for it until we have a scorer that could detect whether it
helps. Defer.

---

## 7. One recommended next experiment

**Build the event-level scorer, and use it to re-judge the two baselines we already have.**

**Inputs:** `2018_SCADA_Flows.csv`, `2018_Leakages.csv`, the scenario configuration
(14 leaks in 2018, 6 abrupt / 8 incipient). No downloads.

**Steps:**
1. Implement BattLeDIM's rule: a detection counts if it falls within the leak's active
   window; repeated detections of an already-detected leak score zero.
2. Group consecutive alert hours into one alert event.
3. Report, separately for abrupt and incipient leaks: leaks detected out of 14,
   detection delay from true onset, and false alerts per week.
4. Score the frozen-week and rolling-14-day baselines under identical inputs.

**What would justify continuing:** the scorer reproduces a sensible, explainable
result, and the two baselines separate — my expectation is the rolling one detects
fewer gradual leaks despite its calmer signal.

**What would justify stopping and rethinking:** both baselines detect almost nothing
at any threshold, which would say single-meter flow at p227 is not an adequate input
and we need multi-sensor evidence before tuning anything.

**Limitations to state up front:** simulated data; no sensor faults in this benchmark
by the organisers' explicit choice; 2018 is our development period so these numbers are
**not** a performance claim; the honest test is 2019, which stays sealed until the
method is frozen.
