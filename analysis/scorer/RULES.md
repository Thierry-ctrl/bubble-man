# How the scorer decides, in plain language

The scorer answers four questions for any method that can say "warn" or "don't warn"
each hour: how many known leaks it warned about, how many it missed, how many
unnecessary warnings it raised, and how long after each leak began the first matching
warning arrived.

Every rule below lives in `Rules` in `leak_scorer.py`. Change them there, not in the code.

## The six rules

**1. Group repeated warnings into one alert event.**
Warnings in consecutive hours are one event. A lull longer than `gap_tolerance_hours`
(default 0) starts a new one. Without this, one leak warned about for 300 hours would
look like 300 successes.

**2. Decide which leaks can fairly be scored.**
A leak counts only if it *began* inside the evaluation window. Leaks already running
when the window opens are reported as `excluded: began before the evaluation window` —
we cannot measure a delay from an onset we never saw. Leaks still running at the window
end are scored normally but flagged `censored_end`.

**3. Match an alert to a leak by time.**
An alert event matches a leak if the event **starts** inside the leak's life, and within
`max_delay_hours` of its onset. Using the event's start (not any part of it) is what
stops an alert that was *already running* before the leak began from taking credit for it.

**4. One alert, one leak. One leak, one alert.**
An event can be credited to at most one leak, and a leak to at most one event. A later
event about an already-credited leak scores **zero** — neither a hit nor a false alarm.
This copies BattLeDIM: *"repeated detections of the same leakage are ignored."*

**5. Say when a match is ambiguous.**
If several leaks were running when the alert started, the alert goes to the most recently
begun one and is labelled `ambiguous`, with every candidate recorded. Our detectors watch
one flow meter and name no pipe, so we can never *prove* which leak caused a warning.

**6. Delay is hours from leak onset to the start of its matching event.**

## Worked example

Leak `pA` runs 1 Feb – 10 Feb. Warnings fire 2 Feb 00:00–04:00, then again 4 Feb and 6 Feb.
A fourth warning fires on 5 Jan when nothing is leaking.

- Rule 1 → four alert events.
- Rule 3 → the 2 Feb event starts inside pA's life. Match.
- Rule 6 → delay = 24 hours.
- Rule 4 → the 4 Feb and 6 Feb events score zero. pA is caught **once**, not three times.
- The 5 Jan event matches nothing → **one unnecessary warning**.

Result: 1 leak matched, 0 missed, 1 unnecessary warning, 24-hour delay. This is check 1
and check 4 in `test_leak_scorer.py`.

## What this is NOT

This is **not** the BattLeDIM competition score. That score also requires the reported
location to fall within 300 m of the leak and converts everything into euros of water
saved minus repair-crew cost. We report no location, so we cannot compute it and do not
claim benchmark performance. Ours is the weaker question: *did a warning arrive while
this leak was running, soon after it began?*

## Why `max_delay_hours` matters more than it looks

The BattLeDIM paper counts a detection any time inside the leak's life. In L-Town 2018
that rule is nearly free: **a leak is running 100% of the hours**, with a median of four
at once. Almost any warning lands inside some leak. Setting a deadline (we use 168 hours,
the one-week window the competition website originally described) gives chance a much
smaller target to hit. See `null-check.json` for the evidence.

## Files

| File | What it is |
|---|---|
| `leak_scorer.py` | The reusable tool. `score(flagged, leaks, rules)` |
| `test_leak_scorer.py` | 13 worked checks; run it before trusting any number |
| `run_scorer.py` | Applies the scorer to our existing baselines across a declared grid |
| `null_check.py` | Asks whether randomly-timed warnings score just as well |
| `make_tables.py` | Produces the per-leak and per-event tables |
