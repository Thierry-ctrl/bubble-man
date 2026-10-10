# Correction note — 11 October 2026 (reporting only; no outcome changes)

No warning, score, criterion or verdict changes. The recorded outcomes stand:
- 490-scenario locked run: FAIL;
- 1,000-scenario held-out test: improved, but below the practical target;
- 2019 L-Town: FAIL.

Recomputed by `reporting_corrections.py` → `reporting-corrections-2026-10-11.json`.

| Issue | Was | Corrected |
|---|---|---|
| Leak endings compared with the **latest leak ending** (1,000-set), not the dataset's final timestamp | 99.9% stop before the end | **100%** of flowing leaks end before the file's final timestamp, in both sets. Comparing with the latest leak ending was wrong by construction: at least one leak always equals it. |
| Months by **day ÷ 30.42**, not the calendar | 89% development, 87.2% held out (Feb/Jun/Jul) | **89.6%** development, **88.7%** held out, by exact calendar date. The held-out files carry a step counter, so their dates are nominal (1 Jan 2017 + position). |
| "Gradual leaks **switch on and off**" | Inferred from a weekly-change statistic | That statistic counts night-to-night changes larger than half the leak's peak night flow, and **by itself does not establish switching to zero**. A separate measure does: night-window leak flow is exactly zero on a median 31% of active nights, in both sets. |
| Warnings during older leaks "point at a leak", "a reaction to the leak", "already-known leak" | Implied cause and prior knowledge | They are **temporal associations**: the warning came while a leak that began more than 7 days earlier was flowing. That shows neither cause nor that the utility knew about the leak. |

Edited, with in-place markers:
- `RESULTS-LEAKDB-1000.md`
- `FINDINGS-LEAKDB-DIAGNOSIS.md`
- `CORRECTION-NOTE-2026-10-09.md`
- `PROTOCOL-LEAKDB-1000.md` (§1 wording only; rules and criteria untouched)
