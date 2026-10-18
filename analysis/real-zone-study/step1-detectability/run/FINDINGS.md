# What added leaks can the unchanged rules see?

**Verified — development results:** constant synthetic flow was added to real Yorkshire N4 readings. These are injected responses, not observed real-leak detection. No repairs were read and no pass/fail test was run.

**My judgement — fixed design:** five previously assessable zones selected only by exact completeness (numeric-ID tie break); 200 random start times per zone, shared across sizes/rules. Separate permanent steps: 0.5–32 m³/h plus 5–80% of each zone's minimum-night-flow reference. See [PLAN.md](/Users/uwonkundathierryrugira/Bubble-man/analysis/real-zone-study/step1-detectability/PLAN.md).

**Verified — response meaning:** a warning within 168 hours at a time absent from the untouched run (extra or retimed). Existing coincident warnings do not count. The unchanged rule keeps its learning, adaptive threshold, arming and spacing. Delays describe responders only.

| Zone | Night-flow reference, m³/h | Smallest tested 90% size: frozen / adaptive, m³/h | Untouched warnings/year: frozen / adaptive |
|---|---:|---:|---:|
| 784 | 5.56 | 4.00 / 4.00 | 2.17 / 3.25 |
| 1586 | 17.96 | 7.18 / 8.00 | 2.17 / 3.25 |
| 664 | 11.09 | 1.11 / 2.00 | 7.58 / 3.25 |
| 526 | 12.99 | 4.00 / 8.00 | 1.08 / 1.08 |
| 698 | 10.29 | 2.00 / 4.00 | 7.58 / 4.33 |

**Verified:** the 90% size requires that size and every larger tested size to reach 90%; it is a grid result, not an interpolated physical limit. The reference is the median daily minimum complete two-hour mean within 00:00–06:00, days 29–365. It includes customer use and any existing losses. Percent sizes are in `minimum-sizes.csv`; all probabilities/counts and conditional delay quartiles are in `curves.csv`.

**Verified:** `untouched.csv` gives warning counts over 337 calendar days, finite step nights, random-date seven-day warning coincidences and complete observation opportunities. Those warnings have unknown real outcomes. `trials.csv` preserves each start/size/rule result; `prepared.json` records selection, seeds and input/code hashes. Five paired-rule curves are below.

**My judgement — useful limit:** the adaptive rule's smallest tested size reaching the 90% convention ranges from 2 to 8 m³/h, about 18–72% of the zones' night-flow references. Four of five zones need a larger tested addition under the adaptive rule than under the frozen comparator. This trade-off belongs beside the untouched warning workload, not a claim that either rule wins.

**Verified — provenance:** data: Yorkshire Water N4, 2016–17, via [Data Mill North](https://datamillnorth.org/dataset/yorkshire-water-leakage-dma-15-minute-data-2zlgn), CC BY 4.0. Constant synthetic flow was added separately to the real background; charts describe those modified copies. Delays use the published wall-clock grid, not verified data-arrival or crew-awareness times.

**Unknown:** actual leak truth, pressure feedback, boundary/storage status and future performance. Additive steps omit pressure/demand interactions, gradual growth and repairs. Best-recorded zones and one reused year are not representative. Overlapping trials and a 200-date sample do not establish field confidence limits. No tuning or grid expansion followed outcomes.

**My judgement:** review the curves and workload before step 2. This study measures what added steps stand out against these backgrounds, not how often crews would find real leaks.

![Injected-step detectability for DMA 784](/Users/uwonkundathierryrugira/Bubble-man/analysis/real-zone-study/step1-detectability/run/dma-784-detectability.png)

![Injected-step detectability for DMA 1586](/Users/uwonkundathierryrugira/Bubble-man/analysis/real-zone-study/step1-detectability/run/dma-1586-detectability.png)

![Injected-step detectability for DMA 664](/Users/uwonkundathierryrugira/Bubble-man/analysis/real-zone-study/step1-detectability/run/dma-664-detectability.png)

![Injected-step detectability for DMA 526](/Users/uwonkundathierryrugira/Bubble-man/analysis/real-zone-study/step1-detectability/run/dma-526-detectability.png)

![Injected-step detectability for DMA 698](/Users/uwonkundathierryrugira/Bubble-man/analysis/real-zone-study/step1-detectability/run/dma-698-detectability.png)
