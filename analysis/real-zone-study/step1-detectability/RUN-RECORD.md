# Step 1 run record and review stop

**Verified (local records, 18 October 2026):** the fixed plan/implementation hashes in [FIXED-BEFORE-SELECTION.json](/Users/uwonkundathierryrugira/Bubble-man/analysis/real-zone-study/step1-detectability/FIXED-BEFORE-SELECTION.json) match `prepared.json` and current source files. Selected zones, in completeness order: 784, 1586, 664, 526, 698. The prepared record and 1,000 random start dates were saved before warning/injection outcomes.

**Verified:** 12 sizes × 200 starts × 5 zones = 12,000 separate injected copies; each ran both unchanged rules, giving 24,000 result rows. The trials share one real background per zone and have overlapping windows; “separate copies” does not mean statistically independent field evidence. All untouched warning times exactly match the prior saved lists.

**Verified — checks:** 14 tests on invented inputs cover preserved gaps/past, zero additions, existing warnings, response timing, selection, reproducible starts, night-flow reference, conditional delays and the grid minimum. A separate output audit checked all 24,000 rows, 120 curve points, control coincidences, ten minimum sizes, delay quartiles, source hashes and warning clocks. All five PNGs were visually reviewed; SVG versions are also supplied. No calculation table changed during rendering.

**Verified — reporting recovery:** the calculation run finished every trial and saved all numeric tables, then stopped because bundled Python lacked Matplotlib. No injections or detector runs were repeated. `render_saved.py` used the saved tables to create charts/report through the existing system Python. `finished.json` records the recovery, output hashes and reporting environment. The original `study.py` remains byte-identical to the preselection version. Its read guard rejected CSV paths other than the named flow/quality/warning/start inputs; the in-memory read trace was lost at the chart error and is not represented as a persisted audit log.

**Verified — environments:** calculations/checks used bundled Python 3.12.14, NumPy 2.3.5, pandas 2.2.3 (versions checked after the run). Reporting used system Python 3.9.6, Matplotlib 3.9.4, NumPy 2.0.2 and pandas 2.3.3. Rendering reads saved outcomes only. Reproduction needs a Python environment with those scientific packages; `study.py prepare` and `study.py run` refuse existing run output to prevent accidental overwriting.

**Verified — data attribution:** Yorkshire Water, N4 2016–17, [Data Mill North](https://datamillnorth.org/dataset/yorkshire-water-leakage-dma-15-minute-data-2zlgn), CC BY 4.0. Original flow size/SHA-256 match the saved download record. No download, repair-record access, contact, purchase, commit, merge or push occurred in this step. Existing uncommitted Yorkshire work remains separate.

**Unknown:** true background leaks, physical pressure/demand responses, real-world false alarms and operator awareness. The percent reference includes ordinary use and any existing losses. Delays are computed on the source's wall-clock grid, not verified receipt times. The 90% level is a descriptive convention, not a new product test.

**My judgement:** review [FINDINGS.md](/Users/uwonkundathierryrugira/Bubble-man/analysis/real-zone-study/step1-detectability/run/FINDINGS.md) before starting step 2. All later steps remain pending. If you want to save this step, these commands stage and commit only the new study folder; they have **not** been run:

```sh
cd /Users/uwonkundathierryrugira/Bubble-man
git add -- analysis/real-zone-study
git -c user.name="Uwonkunda Thierry Rugira" -c user.email="trugira@sandtech.com" commit --only --author="Uwonkunda Thierry Rugira <trugira@sandtech.com>" -m "Study injected leak detectability on five real Yorkshire zones" -m "Co-Authored-By: GPT-6 <noreply@anthropic.com>" -- analysis/real-zone-study
```
