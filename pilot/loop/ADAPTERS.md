# Utility export adapters

**Draft — checked with invented files only.**

**Verified (local sources):** preparation item 6, 11 October 2026. [export_adapters.py](/Users/uwonkundathierryrugira/Bubble-man/pilot/loop/export_adapters.py) reshapes readings into the three files accepted by the unchanged [utility converter](/Users/uwonkundathierryrugira/Bubble-man/pilot/convert_utility_data.py). [36 checks](/Users/uwonkundathierryrugira/Bubble-man/pilot/loop/test_export_adapters_INVENTED.py) pass using entirely invented files. There is no detector run, real-data evaluation or change to the converter.

## What it does

**Verified ([code](/Users/uwonkundathierryrugira/Bubble-man/pilot/loop/export_adapters.py)):** the adapter accepts explicitly mapped UTF-8 delimited files and `.xlsx` workbooks. It handles a long table with a meter ID on each row, or a wide table with one value column per meter. Decimal commas and declared thousands separators are normalised without converting units or rounding measurement precision. For example, an explicitly declared decimal comma makes `1,25` become `1.25`; `0` remains zero and a missing value remains blank.

**My inference:** its purpose is to remove file-layout friction before a permitted sample review. Successfully opening a file says nothing about leak-detection accuracy or whether the zone fits our method.

## Required mapping

**Verified ([invented mapping example](/Users/uwonkundathierryrugira/Bubble-man/pilot/loop/adapter-fixtures-INVENTED/example-mapping-INVENTED.json)):** a JSON file declares the input layout, column names and full meter/zone metadata. It includes units, whether a value is a rate/interval volume/cumulative total, recording interval and what the timestamp marks. Extra meter/zone metadata columns are retained.

**My inference — information to obtain from the data owner:**

| Setting | Meaning |
|---|---|
| `source_format` | `csv` or `xlsx`; no file-type guess. CSV uses an explicitly selected delimiter, comma by default. TSV can use a tab delimiter. |
| `layout` / `columns` | Long: meter ID, timestamp and value, with quality/unit fields when present. Wide: timestamp plus an explicit `series` mapping for every listed meter. |
| `sheet` / `header_row` | Excel sheet name is mandatory. Header row is one-based. Rows above it are outside the selected table; subsequent rows are read rather than guessed away. |
| `decimal_mark` / `thousands_separator` | Decimal point or comma; optional distinct grouping mark. Mixed or malformed grouping is rejected. Typed Excel numbers are already numeric and do not inherit display-locale punctuation. |
| `quality_map` | Exact source codes mapped to `ok`, `estimated`, `fault` or `missing`. Wide meters may share one explicitly mapped row-quality column. Unknown codes are rejected. Surrounding text whitespace is stripped for matching; original quality text remains in the audit. |
| `constant_quality` | Only for a source whose quality meaning is independently confirmed. No quality column does not justify automatically declaring everything `ok`. This setting is never supplied implicitly. |
| `missing_tokens` | Explicit text markers such as blank or `NA`. Do not choose markers based on favourable downstream results. |
| `timestamp_format` | Optional exact format for non-ISO timestamp text. A day/month order is not inferred. |
| `naive_utc_offset` | Required for native Excel datetimes or timestamp text lacking a timezone. Must be independently established, not borrowed from the computer or silently copied from zone metadata. |
| `ignore_columns` | Extra table columns may be ignored only by explicit name. Their names are recorded, and the unchanged source file remains the reference. |
| `meters` / `zone` | Full converter metadata, including boundary roles, supply/storage status and the zone's fixed local UTC offset. Unknown suitability fields remain unknown. |

**Verified ([openpyxl date documentation](https://openpyxl.readthedocs.io/en/stable/datetime.html)):** Excel dates have no timezone, and workbooks can use different date epochs. **Verified ([reader](/Users/uwonkundathierryrugira/Bubble-man/pilot/loop/export_adapters.py)):** the adapter uses the workbook reader's typed datetime and demands a declared fixed offset. It does not guess a date from an unformatted numeric cell. Explicit-offset ISO text preserves the represented instant. The input timestamp remains the measurement time; any later interval-end shift belongs to the existing converter.

## Output and audit

**Verified ([code](/Users/uwonkundathierryrugira/Bubble-man/pilot/loop/export_adapters.py)):** the destination must be a **new** folder. Validation finishes before creating it. An existing folder is refused, so original and previous exports are not overwritten. The output contains:

- `flow_readings.csv`: meter ID, explicit-offset timestamp, value, unit and quality;
- `meters.csv` and `zone.csv`: declared metadata in the existing converter's format;
- `source-audit.jsonl`: source row/field, original timestamp, value and quality, mapped quality and canonical output;
- `source-mapping.json`: the exact supplied configuration;
- `adapter-report.json`: source checksum, row counts, blank measurements, quality counts, duplicates and ignored column names.

**Verified ([code](/Users/uwonkundathierryrugira/Bubble-man/pilot/loop/export_adapters.py)):** blank measurements receive canonical quality `missing`; their previous mapped/source quality remains in the audit. Fault and estimated values are preserved with their flags for the existing converter to handle. Duplicate readings and source order remain intact. Gaps, negative measurements and cumulative-counter resets are not filled, sorted away or repaired. Numeric text uses decimal arithmetic without deliberate precision rounding; typed Excel numbers have the precision already stored by the workbook.

**My inference:** keep the original source alongside the mapping and output. CSV audit row numbers refer to logical table records, which can differ from physical file lines when quoted fields contain newlines. Excel row numbers refer to worksheet rows. A source checksum supports provenance; it does not validate the underlying sensor reading.

## Invented examples and verification

**Verified ([fixture directory](/Users/uwonkundathierryrugira/Bubble-man/pilot/loop/adapter-fixtures-INVENTED/)):** two CSV examples and one Excel workbook contain made-up meter readings. The workbook has long/wide tables storing UTC wall time, a separate local-time datetime example, and deliberately unsupported formula/merged-header examples. Every sheet identifies its data as invented. Native date offsets are explicitly declared in the test mappings.

**Verified (invented tests):** the valid CSV/Excel variants produce equivalent measurements and instants. Four long/wide CSV/Excel variants are also passed through the **unchanged converter**, which produces the same invented 30-minute output: first interval 4.75 m³/h, later incomplete/flagged intervals missing. These tiny files are correctly flagged as too short for detector evaluation. No wrapper or detector is imported or run.

**Verified (invented tests):** coverage includes decimal/grouping grammar, zero versus blank, quality mappings and shared flags, missing metadata, ambiguous dates, exact timestamps, duplicates/gaps, negative values/counter resets, source preservation, audit provenance, wrong worksheets, formulas, merged headers and refusing an existing destination. The final 36/36 checks passed on bundled Python 3.12.14, openpyxl 3.1.5 and pandas 2.2.3. The protected converter's checksum was unchanged across the format checks.

**Verified — Excel fixture authoring record:** the bundled Artifact Tool created the workbook. Initial attempts exposed timestamp coercion in the fixture writer; the final UTC examples use explicit modern Excel-1900 serial values with date formatting, independently read back as datetimes. Local-time examples use explicitly created date values. All five sheets were visually reviewed, and the saved input workbook was tested through the separate reader. This is fixture verification, not evidence that arbitrary utility workbooks preserve their intended timestamp meaning.

### Repeat the checks

**Verified — invented files only:** from the repository root, with the installed bundled runtime:

```sh
/Users/uwonkundathierryrugira/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -B -m unittest discover -s pilot/loop -p 'test_export_adapters_INVENTED.py' -v
```

**My inference — example invocation, invented source only:** use a new destination each time:

```sh
/Users/uwonkundathierryrugira/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -B pilot/loop/export_adapters.py pilot/loop/adapter-fixtures-INVENTED/long-decimal-comma-INVENTED.csv pilot/loop/adapter-fixtures-INVENTED/example-mapping-INVENTED.json pilot/loop/adapter-fixtures-INVENTED/_scratch/example-export-INVENTED
```

**My inference:** the resulting three CSVs are the converter input. Running a detector or evaluating real data remains outside this preparation item's authorised scope.

## Limits and next decisions

**Verified ([reader](/Users/uwonkundathierryrugira/Bubble-man/pilot/loop/export_adapters.py)):** Excel formulas/error cells in the selected table are rejected rather than trusting cached results. The input workbook is read without saving it. The library's `data_only=False` exposes formulas instead of their cached values. [Primary reader documentation](https://openpyxl.readthedocs.io/en/stable/tutorial.html#loading-from-a-file).

**Unverified:** compatibility with any actual utility export, the interpretation of its units/flags/times, complete boundary meters and sensor accuracy. Legacy `.xls`, macro-enabled workbooks, packed value/unit cells, merged/multi-row headers, footer summaries and vendor-specific binary formats need separate declared adapters. Workbooks are read in memory; large-file memory performance is untested. There is no SCADA API, live ingestion, daylight-saving handling, storage correction or operating/repair-record processing here.

**My inference:** before applying this to a permitted real sample, agree the schema, quality mapping, timestamp meaning/offset, meter semantics and supply/storage metadata. Format success must not override the converter's readiness or storage/supply checks. Independent pilot-paperwork preparation can proceed now.
