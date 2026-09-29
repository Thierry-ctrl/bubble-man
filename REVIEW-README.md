# Bubble-man — review bundle

Water-leak detection experiments on the simulated BattLeDIM / L-Town 2018 dataset.
Bundled 29 September 2026. Self-contained: raw data included, scripts run offline.

## Status of each document — read this first

| File | Status |
|---|---|
| `analysis/scorer/FINDINGS-v3.md` | **CURRENT.** Headline results, after reviewer corrections. |
| `analysis/scorer/FINDINGS-v2.md` | **SUPERSEDED** by v3. |
| `analysis/scorer/WATER-ACCOUNTING.md` | **CURRENT.** Zone boundaries and the water balance. |
| `analysis/scorer/RULES.md` | **STALE.** Written for scorer v1. Its six rules no longer match the code. The module docstring in `leak_scorer.py` is authoritative. |
| `analysis/scorer/FINDINGS.md` | **SUPERSEDED** by FINDINGS-v2.md. |
| `analysis/scorer/v1-superseded/`, `v2-superseded/` | Earlier results, kept so changes can be traced. Each has a README saying what was wrong. |
| `research/2026-09-28/deep-research-report.md` | Research review. Claims marked `[verified]` vs `[unverified]`. |
| `research/2026-09-28/evidence-log.md` | Sources, dates, conflicts, open questions. |
| `research/2026-09-21/project-preparation.md` | Original project plan, written before this work. |

Some loose `score-*.csv`, `null-check*.json` and duplicate `alert-events-frozen-week.csv`
/ `alert-events-frozen_week.csv` files in `analysis/scorer/` are v1 leftovers.

## Headline result

Two frozen experiments on the boundary-corrected main-zone signal each associate
**9 of 12** known leaks. Warnings rotated to random times, preserving count and
duration, associate **10 and 11**. Neither experiment shows evidence of detection skill.
False alerts are 1 and 0 over 215 hours of leak-free exposure — far too little to
estimate a rate. Area C is not evaluable: it has zero leak-free hours in the window.

All matches are **timing associations**, not proof that a leak caused a warning. Our
signal names no pipe, so this is NOT the BattLeDIM competition score, which also
requires a location within 300 m.

## Reproducing

    python3 analysis/scorer/test_leak_scorer.py   # 18 worked checks, all should pass
    python3 analysis/scorer/run_main_zone.py      # the two frozen experiments

Requires pandas, numpy, matplotlib. No network access needed.

## Round 2 corrections (29 Sep, after review)

- Fixed: an alert issuable after its matched leak ended was credited. Now
  `retrospective_association`. Latent in our data (0 cases) but reachable.
- Leak activity redefined as positive simulated flow, not configured onset. Gradual
  leaks are silent up to 67.8 h after onset. No outcome changed; three delays per
  experiment lengthened (p810: 10.9 -> 154.9 h in A).
- New Year's Day explanation for experiment B tested and REFUTED; withdrawn. B's alert
  count remains unexplained.
- Sensor timing restated as an assumption supported by a consistency check.

## What a reviewer might most usefully attack

1. The matching rule credits an alert if its unusual run began inside the leak's life
   and it was issuable within 7 days. Is that deadline defensible for gradual leaks
   that produce no flow for their first 67 hours?
2. The null baseline rotates warnings circularly. It preserves count and duration but
   destroys seasonal alignment. Is a better null available?
3. Experiment B's calibration week (1–7 January) contains New Year's Day, which
   depressed the baseline and inflated every later difference.
4. Tank level is quantised to 0.01 m, capping Area C accuracy at about 2 m³/h hourly.
5. Flow-sensor averaging semantics are assumed, not documented by the organisers.

## Provenance

Data: BattLeDIM, Vrachimis et al., https://zenodo.org/records/4017659, CC BY 4.0.
L-Town telemetry is **simulated**, not measurements from a real town. The model file
named `L-TOWN_Real.inp` is the simulator's generation model, not evidence of real data.
