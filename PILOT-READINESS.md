# Bubble Man — ready for a first real utility data trial

*October 2026. Everything so far comes from simulated networks. Nothing here is evidence of
performance on a real utility's pipes.*

## 1. What we can show today

- **A clear, checkable method.** Every night, Bubble Man compares a zone's lowest flow with
  what it expected. If the last two nights jump well above the week before, it raises a
  warning for staff to investigate.
- **It finds sudden new leaks in simulation.** On 1,000 fresh simulated scenarios of a test
  network (LeakDB "Hanoi"), it flagged about 89% of new sudden leaks within a week. The
  median warning came about 13½ hours after the leak began. That is far more than chance
  would produce.
- **We fixed its main weakness, and the fix held up on data it was not tuned on.** The
  original version raised too many warnings in the busy season. Letting the warning level
  follow the last eight weeks:
  - cut warnings that pointed to no new leak by three-quarters;
  - lost about 2 points of detection;
  - raised the share of warnings that led to a new leak from 19% to 47%.

  That is still below our 50% working target.
- **Honest record-keeping.** We fix rules before looking at answers. We keep failures on
  record — our 2019 test failed — and we never present simulation as real-world proof.

## 2. The question the trial answers

**Does that improvement survive real operating conditions?** In particular, when the
warning level follows recent weeks, does the method still catch new leaks earlier than
they are currently reported? And does it keep the number of field visits manageable?

Real zones have real meters, real gaps and real night use. Repairs are recorded the way
people actually record them. Simulations have none of this.

## 3. The smallest suitable pilot

- **One water zone with a clear boundary**: we know every pipe where water enters or leaves.
- **Continuous (24-hour) supply.** Ideal, because night flow then mostly means leakage and a
  little night use.
- **An existing flow meter on each inlet** recording at least every 15 minutes, with a
  logger.
- **History:** a small sample first, two to four weeks, to check compatibility. Then **at
  least 12 months**, ideally 18–24.
- **Repair and work-order records** for the same zone and period.
- No new hardware for the first, retrospective stage.

## 4. Data we need

The format, as CSV files, is shown in `pilot/example-INVENTED/`; every value there is
**invented**.

| Item | Detail |
|---|---|
| **Flow readings** | Meter ID, time, value, unit, quality flag — one row per meter per reading |
| **Timestamps** | Local time **with UTC offset** (e.g. `2026-03-02T02:15:00+02:00`), and whether a value marks the reading moment or the end of an interval |
| **Units** | L/s, m³/h, or volume (m³ per interval, or cumulative meter total) — stated per meter |
| **Interval** | 15 minutes or finer (1, 5, 10, 15 or 30 min) |
| **Missing data** | Gaps left as gaps, not filled in. Estimated or faulty readings flagged, not removed silently. |
| **Meter details** | Type (electromagnetic or ultrasonic), size, install and last-check dates, known faults or replacements |

**Boundary information:**
- every inlet and outlet;
- transfers to and from neighbouring zones;
- tanks or reservoirs inside the zone, with level readings and dimensions;
- whether boundary valves are confirmed closed;
- number of connections;
- large night users, such as a hospital, bakery or factory.

**Operating logs:**
- supply interruptions;
- pump and valve changes;
- pressure-setting changes;
- meter faults and logger restarts;
- boundary changes.

Each needs a start and end time.

**Repair records.** Keep these **three times separate**:
1. **first report**: when someone first reported or noticed the problem;
2. **confirmation**: when staff confirmed a leak;
3. **repair**: when work started and finished.

Also include location, asset type (main, service pipe, hydrant, meter), visible or hidden,
how it was found, and **visits that found nothing**.

*The first report is not when the leak began.* It only tells us the leak began *no later
than* that.

## 5. How we will judge it — fairly, even with incomplete records

- **Every warning is an investigation.** Each one is classed as:
  - **leak found**;
  - **checked, nothing found**;
  - **not checked**. This stays *unknown*. It is never counted as right or wrong.
- **Detection:** for each confirmed leak, did a warning come **before its first report**, and
  how much earlier? That lead time is measurable. The true delay from leak start is not,
  because the start is unknown.
- **Beyond chance:** we repeat the comparison with the warnings shifted by whole weeks, as
  in our simulation tests.
- **Workload:** warnings per month for the zone, and staff time per visit.
- **No record ≠ no leak.** A period without repair records is called **"no recorded
  leak"**, never "leak-free". Warnings there stay unconfirmed until someone checks.
- **Two stages:**
  1. **Retrospective**, using history and records: cheap, and answers "would it have
     flagged known leaks earlier?".
  2. **Shadow**: run live for a few months. Staff check each warning, plus a few randomly
     chosen nights with no warning, so we know how often a visit finds a leak anyway.
- **The scoring rules are fixed in writing before we open the repair records.**

## 6. When the current method is the wrong tool

- **Intermittent or rationed supply.** Household tanks refilling at night look exactly like
  leakage. This is common in parts of Rwanda, so we need a continuous-supply zone, or a
  different method.
- **No inlet meter**, only daily totals, or readings slower than every 30 minutes.
- **An open or unknown boundary**, or unmetered transfers.
- **Tanks inside the zone** without level readings.
- **Night flow dominated by a few large users** with changing schedules.
- **Frequent valve, pump or pressure changes at night**, without a log of them.
- **Less than about a year of data**, or big gaps in the first two weeks: the method can't
  learn the zone's normal pattern.
- Bubble Man **does not locate leaks.** It says when a zone's night flow has changed, not
  which pipe is leaking.

## Files

- `pilot/UTILITY-REQUEST-DRAFT.md` — a message to send to a utility (not sent).
- `pilot/example-INVENTED/` — the requested format, invented.
- `pilot/convert_utility_data.py` — checks an export and converts it, without changing the
  detection rule.
- `pilot/run_frozen_rule.py` — runs the existing rules on the converted data.
- `pilot/SOFTWARE-GAPS.md` — deeper changes that still need real data or a decision.
