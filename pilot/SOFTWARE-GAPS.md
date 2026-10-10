# What the software does and does not yet do with real utility data

**Done now** (`convert_utility_data.py`, `run_frozen_rule.py`, tests 14/14 on invented data).
The tools accept the export format described in `PILOT-READINESS.md`:
- Check columns, units and timestamps; an explicit UTC offset is required.
- Convert L/s, m³/h, m³/s, interval volumes and cumulative totals to m³/h.
- Treat flagged, duplicate, off-grid, reset or negative readings as missing. Nothing is
  interpolated.
- Build the zone's net inflow (inlets + transfers in − outlets − transfers out) on the
  30-minute grid the frozen method reads.
- Run the two existing rules unchanged.

The detection rules were not modified.

**Deeper changes, not made** — each needs a decision, and most need real data first:

| Gap | Why it matters | What it would take |
|---|---|---|
| **Storage inside the zone** | Tank filling and draining changes net inflow at night | Tank geometry plus level readings, then a storage term in the net-inflow sum. The converter currently refuses such zones unless told to inspect them. |
| **Intermittent or scheduled supply** | Household tanks refilling after an interruption look like leakage | A different method, or excluding the affected nights using the supply schedule. A design and protocol decision, not a format fix. |
| **More than one year** | The frozen reader takes 365 days from the first midnight | A continuous version, as in the 2019 L-Town run, re-validated before use |
| **Gaps in the first 14 days** | The frozen method marks the zone not assessable | Choosing a later, complete learning period — a protocol decision |
| **Operating-log events** (meter faults, valve changes) | They are listed but not used to mask nights | Rules for masking nights, written and frozen before results are seen |
| **Scoring against repair records** | The current scorer needs the true leak start, which real records never give; the first report is only an upper bound | A new scorer for "warning before first report", field-visit outcomes and unvisited warnings. It must be designed and frozen before pilot records are opened. |
| **Large night users** (bakery, hospital, industry) | Their night use moves the baseline | Their schedules, or a separate meter for them |
| **Live use** (daily data, notifying staff) | Everything runs on historical files today | An ingestion and notification service, built after the retrospective check |
| **Daylight saving, several zones, nested zones** | Not handled | Not needed for a first Rwandan single-zone pilot (Rwanda keeps UTC+2 all year) |
