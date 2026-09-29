# Main-zone evaluation, round 3 — 29 September 2026

Supersedes FINDINGS-v3.md (kept in `v3-superseded/`). Simulated L-Town 2018.
Development experiment. **Not evidence of anything working in Rwanda.** 2019 untouched.
Detector settings unchanged from v3.

## The defect, and why the v3 fix missed it

Reproduced exactly as reported. An older leak still running, a newer leak active
09:00–12:00, an unusual run starting 10:00 and issuable at 16:00 — v3 credited the
**newer** leak four hours after it had stopped.

The cause was a one-line inconsistency. v3 computed the deadline-qualified set
`in_time` from `running`, then separately filtered `running` down to leaks still alive
at issuance — but selected the winner from the **unfiltered** `in_time`. So an expired
leak stayed selectable whenever a live one shared the moment. The v3 end-of-leak guard
only fired when *every* candidate had expired.

`match_events` now narrows one frame in a fixed order, and every later rule applies to
the narrowed set:

    running   active when the unusual run BEGAN
    alive     of those, still active when the alert could be ISSUED
    in_time   of those, within the deadline
    free      of those, not already credited
    eligible  of those, scorable at all

Regression checks **19** (expired leak overlapped by a live one — must not be credited)
and **20** (identical overlap, newer leak still running — must be credited) pin the
behaviour from both sides. Check **21** separates a live-but-past-deadline leak
(`unattributable`) from an expired one (`retrospective_association`). **21/21 pass.**

## The deadline now starts at first positive flow — a rule change

Two distinct things arrived together in v3 and should not be confused:

- **A reporting change.** Delay is reported against both first positive flow and
  configured onset. This only adds a column.
- **A rule change.** Because `leaks.start` became the first-positive-flow time, the
  seven-day deadline now runs from **when a leak began producing water**, not from its
  configured onset. For gradual leaks that shifts the deadline later by up to 67.8
  hours, making it **more generous**. This changes which alerts can be credited.

The rule change is deliberate — a detector cannot be asked to find a leak before it
leaks — but it was not stated in v3, and it is not merely a reporting choice.

## What changed in the results

| | A — reference | B — calibrated |
|---|---|---|
| Leaks associated | 9 / 12 → **9 / 12** | 9 / 12 → **9 / 12** |
| — abrupt | 3 / 6 → **3 / 6** | 5 / 6 → **5 / 6** |
| — gradual | 6 / 6 → **6 / 6** | 4 / 6 → **4 / 6** |
| Median delay (first flow) | 55.8 → **55.8 h** | 28.9 → **28.9 h** |
| False alerts / quiet exposure | 1 in 215 h → **1 in 215 h** | 0 in 215 h → **0 in 215 h** |
| Randomly-timed warnings credit | 10.0 → **10.0** | 11.0 → **11.0** |
| Retrospective associations | 0 → **0** | 0 → **0** |
| Unattributable | 0 → **105** | 47 → **167** |
| Repeat of credited leak | 119 → **14** | 143 → **23** |

**No credit, delay, false alert or chance comparison changed.** Total alert events are
identical (129 and 199). The defect was latent in this data for the same reason as
before: our leaks rarely expire while an alert is forming.

**Two categories were relabelled, and the new labels read worse than reality.** Because
prior-credit is now applied to the deadline-qualified set, an alert arriving while a
credited leak is still leaking — but past its seven-day deadline — is `unattributable`
rather than `repeat_of_credited_leak`. This is the logically consistent ordering, but:

| | Unattributable | …of which a credited leak was running |
|---|---|---|
| A | 105 | **105 (100%)** |
| B | 167 | **121 (72%)** |

Every one of A's 105 occurs while a leak we had already flagged was still running. They
are operationally repeats — the crew already knows — even though the scorer cannot
credit them. Reading 105 as "mystery alerts" would be wrong. The figure is now recorded
as `unattributable_while_a_credited_leak_runs` in `main-zone-report.json`.

## Headline, unchanged

Both experiments associate **9 of 12** leaks. Randomly-timed warnings of the same count
and duration associate **10 and 11**. Three rounds of correction have not moved this:
**neither experiment shows evidence of detection skill.**

False alerts remain 1 and 0 across 215 hours of quiet exposure — too little to estimate
a rate. Area C remains not evaluable: zero leak-free hours in the window.

## Standing caveats

- Simulated data; sensor faults and delays excluded by the organisers.
- Tank level quantised to 0.01 m, capping Area C accuracy near 2 m³/h hourly.
- Flow and level averaging semantics **assumed**, supported by a consistency check
  (level rises in 0.16% of pump-off intervals under the assumption, 0.49% under the
  alternative) — not proven.
- Why B fires 199 times at 22.80 m³/h while A fires 129 at 10 m³/h is **unexplained**.
  The New Year's Day hypothesis was tested and refuted (1 Jan 139.19 m³/h vs 8 Jan
  137.23 — higher, not depressed). No replacement guess offered.
- All results are timing **associations**. Our signal names no pipe.
