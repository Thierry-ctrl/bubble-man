# Bubble Man

**Early warnings of new water leaks, from the flow meters utilities already have.**

Bubble Man watches the water flowing into a district metered zone at night, when almost
everyone is asleep. If the night flow jumps above what that zone normally uses, it raises a
warning so a field team can investigate sooner. The aim is to help water utilities in
**Rwanda** reduce the water they lose to leaks. That loss is a large share of the water they
produce: national non-revenue water was estimated at about 38% in 2026, though not all of it
is physical leakage.

This repository is a research project in progress, not a finished product. Every result
below is labelled as **simulated** or **real**, and failed tests are kept on record.

## How it works

1. Learn each zone's normal 24-hour flow pattern for each type of day, from its first two
   weeks of readings.
2. Each night, compare the quietest two hours with that pattern.
3. Warn when the last two nights rise well above the week before. The **adaptive** version
   sets "well above" from the zone's own recent variability over the previous eight weeks.
4. Leave at least 7 days between warnings, and only warn again once the rise has settled.

## What has been tested so far

Each test had its rules **written and committed before its results were looked at**.

| Test | Data | Outcome |
|---|---|---|
| L-Town 2019 | Simulated (BattLeDIM) | **Failed.** The simulator's demand replays by calendar date, so the weekly pattern slipped and broke the baseline. |
| LeakDB Hanoi, 490 scenarios | Simulated | **Failed** the workload target. 91% of sudden leaks were found, but only 18% of warnings led to a new leak. |
| LeakDB Hanoi, 1,000 held-out scenarios | Simulated | **Improved, but below the practical target.** The adaptive threshold cut warnings that found no new leak by 75%, lost about 2 points of detection, and reached 47% against a 50% target. |
| Yorkshire Water, area N4 | **Real** UK meters, 2016–17 | **No association beyond chance detected** (p = 0.0625). 38% of mains repairs had a warning in the 28 days before; repair dates are completion dates, not when leaks began. |
| Five real Yorkshire zones, leaks added artificially | Real flows plus injected leaks | The method reliably notices a new constant leak from about **2–8 m³/h**, roughly 1–1.5 days after it starts. Smaller leaks are mostly invisible. |

**What this means:** the method behaves sensibly and is honestly tested. It has **not yet
been shown to find real leaks earlier than they are currently reported.** Proving that needs
utility records of when each leak was first reported, plus field checks of warnings.

## Where to look

| Folder or file | What it holds |
|---|---|
| [`PILOT-READINESS.md`](PILOT-READINESS.md) | Plain-language guide: what Bubble Man can show today, and what a utility pilot needs |
| [`pilot/`](pilot/) | Utility data format (invented example), converter, request draft, scoring draft |
| [`analysis/next-fair-evaluation/`](analysis/next-fair-evaluation/) | LeakDB protocols and results, including the 1,000-scenario held-out test |
| [`analysis/yorkshire-n4/`](analysis/yorkshire-n4/) | First real-data test: protocol, code and results |
| [`analysis/real-zone-study/`](analysis/real-zone-study/) | Detectability on real zones, night-flow accounting, preregistered detector comparison |
| [`analysis/night-flow-step/`](analysis/night-flow-step/) | Original method and the failed 2019 L-Town test |
| [`research/`](research/) | Literature review, Rwanda utility landscape, public dataset survey |
| [`COMMIT-ID-MAP.md`](COMMIT-ID-MAP.md) | Commit IDs were rewritten before publication. Documents quote the old IDs; this maps them to the new ones. |

Older L-Town experiments sit in the other `analysis/` folders. [`REVIEW-README.md`](REVIEW-README.md)
describes that earlier bundle.

## Running the checks

Python 3.9+ with `pandas` and `numpy`. All tests use **invented** data:

```bash
python3 pilot/test_pilot_tools.py
python3 analysis/next-fair-evaluation/leakdb1000/test_rules_and_scoring.py
python3 analysis/yorkshire-n4/test_yw_INVENTED.py
```

Large datasets aren't stored here. Their run scripts download them and check their
fingerprints: LeakDB (13.9 GB) and the Yorkshire area flow files.

## What it cannot do yet

- **Zones with intermittent supply.** Common in Rwanda: household tanks refilling at night
  look exactly like leakage.
- **Locating a leak.** It flags when a zone's night flow changes, not which pipe.
- **Seeing steady, long-standing leaks.** A change detector treats them as normal. Ranking
  zones by unexplained night flow is a separate job; it was explored in the real-zone study.
- **Live operation.** No daily data feed, alerts or field app yet.

## Data sources and credits

- **BattLeDIM / L-Town:** Vrachimis et al., [Zenodo 4017659](https://zenodo.org/records/4017659),
  CC BY 4.0. Included in `data/l-town/`.
- **LeakDB:** Vrachimis et al., KIOS Research,
  [Zenodo 13985057](https://zenodo.org/records/13985057), CC BY 4.0. Not included.
- **Yorkshire Water** Leakage DMA 15 Minute Data, via
  [Data Mill North](https://datamillnorth.org/dataset/yorkshire-water-leakage-dma-15-minute-data-2zlgn),
  CC BY 4.0. Only the zone property-count file is included.

## Licence

The project's own code and documents **do not have a licence yet**. Until one is chosen, all
rights are reserved. The datasets above keep their own CC BY 4.0 licences.

## Author

Uwonkunda Thierry Rugira — [github.com/Thierry-ctrl](https://github.com/Thierry-ctrl)
