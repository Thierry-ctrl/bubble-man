# Step 2 — what might account for night flow?

18 October 2026. **Descriptive accounting; no detector change or new validation result.**

**The useful finding:** in three of the five zones, the measured night flow substantially exceeds our broad ordinary-use scenarios. That is a reason to investigate the remainder. It is **not a measurement of leakage**. In the other two zones, the answer depends especially strongly on the assumed customer use.

## What we know, and what we assumed

**Verified:** the authorised [Yorkshire Water property-count file](https://datamillnorth.org/dataset/yorkshire-water-leakage-dma-15-minute-data-2zlgn) supplies household/non-household counts for all five previously selected N4 zones. Its 39,098 bytes match the publisher's size and MD5. Counts cover 2016–17; they do not identify business types, actual occupancy or night-time use.

**Judgement:** use **1–4 L/household/hour**, a deliberately broad sensitivity range rather than a published interval. Historical UK references include the 1994 allowance of 1.7 and NI Water's 2007–08 monitoring estimate of 2.48. Use **0.7–60.6 L/non-household/hour**, spanning historical UK customer-category averages. These old figures are **not Yorkshire measurements, individual-user limits, confidence intervals or Rwanda estimates**. Sources and the measurement caveats are in [METHOD.md](/Users/uwonkundathierryrugira/Bubble-man/analysis/real-zone-study/step2-night-use/METHOD.md).

**Verified:** a separate, fixed one-hour summary avoids mixing the old hourly allowance with step 1's two-hour proxy. The first 28 days choose each zone's hour; later complete weekdays supply the summaries. All zones chose 02:00–03:00 except 1586, which chose 03:00–04:00. There are 241 later weekday nights each, with one excluded incomplete night in 664. Training is not known to be leak-free.

## Conditional calculation

Subtract the ordinary-use range from median measured flow. The percentage is the **conditional plausible leakage share of that night flow**, assuming the unexplained remainder is physical loss and the boundary/meter assumptions hold.

| Zone | Households / non-households | Median flow, m³/h | Assumed ordinary use, m³/h | Conditional plausible leakage share |
|---|---:|---:|---:|---:|
| 784 | 1,455 / 56 | 5.46 | 1.49–9.21 | **0–73%** |
| 1586 | 1,880 / 151 | 18.59 | 1.99–16.67 | **10–89%** |
| 664 | 640 / 13 | 11.14 | 0.65–3.35 | **70–94%** |
| 526 | 626 / 31 | 13.47 | 0.65–4.38 | **67–95%** |
| 698 | 163 / 26 | 10.35 | 0.18–2.23 | **78–98%** |

Allowing the observed 10th–90th percentile night-flow variation as well widens these scenario spans to **0–77%, 0–90%, 65–94%, 60–96% and 76–99%**, respectively. These are sensitivity envelopes, not statistical confidence intervals or guaranteed bounds.

**An exposed inconsistency:** the all-high-use scenario exceeds every observed accounting night in 784, and 42 of 241 in 1586. The signed residuals remain in the CSV. The displayed lower share is zero where some use inside the assumed range could account for all flow; it does not say zero leakage was measured. No low-use endpoint exceeds an observed accounting night.

![Measured night flow and conditional accounting ranges](/Users/uwonkundathierryrugira/Bubble-man/analysis/real-zone-study/step2-night-use/run/night-flow-accounting.png)

## What could overturn the interpretation?

**Unknown:** exceptional users, tank filling, zone transfers/storage, boundary integrity, meter accuracy and interval timing. The business range contains category **averages**, not maximum possible use. For example, an additional **7.79 m³/h** of legitimate use beyond the high-use scenario would erase 664's remaining median excess. We have no business-meter data to exclude that explanation. Without the assumptions, these data do not establish a useful lower bound on leakage.

**Unknown:** where physical loss happens. Subtracting legitimate use leaves possible utility leakage **and customer plumbing leakage**. Neither can be separately estimated here. Night-flow shares also cannot be converted into annual water loss without further evidence, including pressure behaviour.

**My judgement:** this strengthens the case for checking existing background losses as well as watching for new rises. A substantial steady leak could already be part of a detector's normal background. Step 1's response to newly added flow and this accounting exercise answer different questions. Neither establishes real-leak detection accuracy.

**Verified checks:** nine invented-input checks pass. An independent streaming read reproduces all five hours, night counts, flow summaries and median accounting ranges. All 42 protected step-1/source/result files retain their hashes. A post-calculation checksum-guard error was corrected; all five numeric tables are byte-identical before/after the correction. No repair file was opened, no detector was imported/run, and nothing feeds the detector. No commit, merge, push or outreach occurred.

**Review stop:** step 2 is complete. Steps 3–5 have not started. See [RUN-RECORD.md](/Users/uwonkundathierryrugira/Bubble-man/analysis/real-zone-study/step2-night-use/RUN-RECORD.md) for outputs, reproduction and optional manual commit commands.
