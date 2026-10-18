# First real-data test — Yorkshire Water, Area N4: results

Protocol `PROTOCOL-YORKSHIRE-N4.md`, frozen at fb9a949. Revision 1 (853594a) handled the
autumn clock change before any repair was seen. Warnings were committed at e4e198f before
the repairs file was downloaded. Scored once.

**Real UK meters, 2016–17, continuous supply.** This says nothing about Rwanda and is not a
validation. The repair records are mains-repair *completion dates*. They are not leak start
times and not a full list of leaks, so everything below is about **timing associations**.

## Verdict (pre-declared): **no association beyond chance detected**

| | Result |
|---|---|
| Y1: at least 20 eligible repairs | 130 — met |
| Y2: adaptive rule's p ≤ 0.05 | **p = 0.0625** — not met. 50 repairs were preceded by a warning; 2 of the 47 week-shifts reached 50 or more. |

The frozen rule gave the same p (52 preceded; also 2 shifts at or above it).

## What happened

| | Frozen | Adaptive |
|---|---|---|
| DMAs read / assessable | 74 / 43 | 74 / 43 |
| Warnings (nights to investigate) | 167 | 138 |
| Warnings per DMA per month | 0.35 | 0.29 |
| Eligible repairs (assessable DMAs, from day 57) | 130 | 130 |
| **Repairs preceded by a warning 1–28 days earlier** | **52 (40%)** | **50 (38%)** |
| Median days from that warning to the repair | 11.5 | 10.5 |
| Repairs with a warning only on the completion day | 8 | 10 |
| Warnings followed by a repair within 28 days | 46 (28%) | 40 (29%) |
| Week-shifted warnings: median / max repairs preceded | 32 / 59 | 31 / 58 |

**Unassessable DMAs:** 31 of 74 (42%), all because of gaps:
- 24 had an incomplete first two weeks;
- 6 had too few complete nights;
- 1 had too few steps to set its threshold.

**Data quality:** 5% of readings were invalid and 1% missing. 6,534 readings marked valid
were negative and were treated as missing.

A warning with no repair within 28 days is **not** shown to be wrong. Most leaks never
appear in a mains-repair list. Service-pipe and customer-side leaks are absent from it,
and many leaks are never found.

## What the shift comparison missed — described after the result, not part of the verdict

The only two shifts that matched or beat the real count moved the warnings **1 and 2 weeks
earlier**. Every shift at least 4 weeks away in either direction reached at most 42
(adaptive) and 44 (frozen).

Adaptive warnings relative to repairs in the same DMA:

| Weeks before (−) or after (+) the repair completion day | −5 | −4 | −3 | −2 | −1 | same day | +1 | +2 | +3 | +4 | +5 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Warning–repair pairs | 11 | 9 | 13 | 15 | 19 | 15 | 7 | 12 | 3 | 9 | 6 |

Warnings build up in the weeks before repairs and peak in the last week and on the repair
day itself.

**The design flaw.** The 28-day window is wider than a 1–2 week shift. So a short shift
keeps much of the real timing — it is not "chance". The pre-declared test was therefore
conservative, and its verdict stands. A future test should leave out shifts within the
window's width, or use a narrower window, **fixed before the data are seen**. These data
must not be re-scored to rescue this result.

The same-day cluster could reflect leaks rising until they are fixed. It could equally come
from the repair work itself: shutting valves, draining and recharging the main. These data
cannot tell the two apart.

## What this means

- **First contact with real meters.** The unchanged rules ran on real UK data at a modest
  warning rate, about one warning per DMA every 3–4 months.
- **Strictness about gaps.** 42% of zones could not be assessed because of gaps — a
  practical weakness that will matter more in Rwanda.
- **Not proven.** About 4 in 10 recorded repairs had a warning in the month before, and
  warnings cluster towards repair dates. Under the test fixed in advance, that was **not
  shown to be beyond chance**, so it remains a suggestion, not a finding.
- **What would settle it:** first-report times and field checks of warnings. Those are what
  the utility pilot in `PILOT-READINESS.md` asks for, and this public dataset lacks them.

Files (`run/`): `step1-download.json`, `attempt1/`, `warnings-both-rules.csv`,
`dma-assessability.csv`, `step2-warnings.json`, `step3-repairs-download.json`,
`repairs-*.csv`, `shifts-*.csv`, `step4-results.json`, `step4-stdout.txt`.
