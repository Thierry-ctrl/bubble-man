# Step 2 run record and review stop

**Scope:** descriptive night-use accounting, following the founder's review of step 1. This adds only step-2 artifacts and updates the study's progress log. Existing detector files and locked results are unchanged.

**Download:** `source/DMA-property-count-2016-2017.csv`, Yorkshire Water via Data Mill North, CC BY 4.0. Download size 39,098 bytes; MD5 `98e08e78ae4ead4c3ce85e34f2c9629c`, equal to the publisher's metadata. URL, SHA-256, licence and authorisation are in `source/download.json`. The canonical URL initially returned 403; adding a query refreshed its public download redirect. No other utility data was downloaded.

**Assumptions fixed before calculation:** `METHOD.md` and `assumptions.json`, with hashes in `run/provenance.json`. The household 1–4 range is analyst judgement; the non-household 0.7–60.6 range spans old UK category means. Neither is a measured Yorkshire distribution or a guaranteed bound. This was not a new validation protocol.

**Reader:** standalone `accounting.py`; no detector or repair reader imported. Its calculation-phase CSV read guard admitted only the named property and flow files. `run/provenance.json` records both paths. Hash checks before/after the calculation separately read the declared protected files, including previous warning CSVs as raw bytes. They do not parse outcomes. All 42 protected hashes match, including step-1 inputs/outputs and frozen detector/validation files. Selected-zone finite half-hour counts and step-1 two-hour references also reproduce exactly.

**Checks:** nine invented-input tests cover incompatible use/flow ranges, physical feasibility, units, missing quarters, historical hour selection, insufficient training, duplicate property rows and missing/invalid counts. An independent one-off streaming CSV reader, using separate date/quarter-hour aggregation, reproduced the five chosen hours, complete-night counts, percentiles and median-share endpoints; `run/audit.json` records the values. Numeric output checksums match provenance. No claim of real-leak accuracy or false-alarm reduction follows.

**Recovery disclosure:** the first calculation saved every numeric CSV, then its read guard rejected opening its own output to compute a checksum. The guard was corrected only for the post-calculation hash phase; the original tables are preserved in `run-attempt1/`. The accounting calculation was repeated and every numeric CSV is byte-identical. `reporting-recovery.json` records the original hashes and equality. No detector run occurred in either attempt. An invented missing-count check also caught an input-validation error before calculation; missing strings now stop cleanly.

**Environment:** system Python 3.9.6, NumPy 2.0.2, pandas 2.3.3, Matplotlib 3.9.4. The scientific plot was rendered from saved summaries and visually reviewed. Full SVG and PNG are supplied.

## Outputs

- `FINDINGS.md`: short interpretation and review stop.
- `run/summary.csv`: component ranges, signed residuals, conditional shares, night-variation envelope, incompatible-corner counts, exceptional-use sensitivity and step-1 reference cross-check.
- `run/properties.csv`: the five exact property joins.
- `run/hour-selection.csv`: all six training-hour medians per zone.
- `run/nights.csv`: 1,205 candidate weekday-zone nights, including missing status.
- `run/monthly.csv`: monthly accounting-hour medians.
- `run/provenance.json`, `run/audit.json`: provenance and verification.
- `run/night-flow-accounting.png` / `.svg`: measured flow and conditional scenario ranges.

## Reproduction

Read the method and assumptions first. The full calculation refuses an existing `run/` folder; reproduce in a separate copy of the study with the same relative source paths, preserving this run. Test and render commands below are safe against existing numeric outputs:

```sh
cd /Users/uwonkundathierryrugira/Bubble-man
python3 -m unittest discover -s analysis/real-zone-study/step2-night-use -p 'test_*INVENTED.py'
python3 analysis/real-zone-study/step2-night-use/render_saved.py
```

## Optional manual commit — not executed

Step 1 and step 2 are both currently untracked in the new study folder. After review, these commands save both steps and their progress log, without adding files outside this study. Inspect the staged diff before committing:

```sh
cd /Users/uwonkundathierryrugira/Bubble-man
git add -- analysis/real-zone-study
git diff --cached --stat -- analysis/real-zone-study
git commit --only -m "Add five-zone detectability and conditional night-use accounting" -- analysis/real-zone-study
```

No commit, merge or push was run. Stop for founder review before step 3; the overall five-step goal remains incomplete.
