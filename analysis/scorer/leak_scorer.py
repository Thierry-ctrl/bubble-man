"""Event-level scorer, version 2.

WHAT CHANGED FROM v1 (kept in v1-superseded/)
---------------------------------------------
1. TWO TIMESTAMPS, NOT ONE. v1 timed an alert at the first unusual hour, which is
   before anyone could have known. v2 records three moments:
       run_start          the first hour whose difference exceeds the threshold
       rule_satisfied_at  the hour at which the persistence requirement is met
       issuable_at        when the alert could actually be raised = one hour after
                          that, because an hourly average is only complete at the
                          end of its hour
   Detection delay is measured from `issuable_at`. v1 delays were too short.

2. NEUTRAL WORDS FOR UNMATCHED WARNINGS. v1 called them "late detections of genuine
   leakage". Nothing linked them to a leak; a leak merely happened to be running.
   v2 separates `false_alert` (no leak running in this zone at all) from
   `unattributable` (a leak was running, but no evidence ties this warning to it).

3. ZONES COME FROM THE NETWORK MAP, not from before/after flow steps. See
   `zone` on each leak. Parsing L-TOWN.inp shows p227 and p235 are two reservoir
   inlets feeding ONE connected 690-node network through PRV-1 and PRV-2; only
   PUMP_1 gates a genuinely separate 93-node area. So p227 and p235 are parallel
   inlets to the same zone, and their sum is that zone's inflow.

WHAT THIS TOOL STILL CANNOT DO
------------------------------
Our detectors name no pipe. A warning arriving while a leak runs is a coincidence in
time, not proof. Every match is labelled with its confidence, and no result here is
the BattLeDIM score, which also requires a location within 300 m.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
import re

import pandas as pd

ABRUPT, INCIPIENT = 'abrupt', 'incipient'


@dataclass
class Rules:
    """Every knob that changes a number. Change these, not the code."""
    gap_tolerance_hours: int = 0
    """Lull allowed inside one unusual run before it counts as two."""

    reporting_lag_hours: float = 1.0
    """Delay between the last hour used and the moment an alert can be raised.
    One hour because an hourly average is only complete at the end of its hour."""

    max_delay_hours: float | None = 168.0
    """How soon after onset an alert must be ISSUABLE to be credited.

    None reproduces the BattLeDIM paper, where any moment inside a leak's life
    counts. That is too generous here: in the main network a leak runs continuously
    from late January 2018 onward, so almost any warning lands inside one."""

    attribute_to: str = 'most_recent'


@dataclass
class AlertEvent:
    index: int
    run_start: pd.Timestamp        # first unusual hour
    rule_satisfied_at: pd.Timestamp  # persistence requirement met
    issuable_at: pd.Timestamp      # when it could actually be raised
    end: pd.Timestamp              # last unusual hour
    hours: int
    zone: str | None = None
    matched_leak: str | None = None
    match_confidence: str | None = None
    candidates: list = field(default_factory=list)
    leaks_running: list = field(default_factory=list)
    outcome: str = 'unclassified'


def find_alerts(above: pd.Series, persistence: int, rules: Rules) -> list[AlertEvent]:
    """Rule 1. `above` is True in each hour whose difference exceeds the threshold.

    A run of `persistence` consecutive such hours raises ONE alert. Runs shorter than
    that raise nothing. Both the start of the run and the moment the rule is met are
    recorded, because they are different questions.
    """
    assert above.index.is_monotonic_increasing, 'timestamps must be sorted'
    assert above.dtype == bool, 'expected a boolean series'
    step = pd.Timedelta(hours=1)
    runs, start, previous = [], None, None
    for stamp, flag in above.items():
        if flag:
            if start is None:
                start = stamp
            elif (stamp - previous) / step - 1 > rules.gap_tolerance_hours:
                runs.append((start, previous))
                start = stamp
            previous = stamp
    if start is not None:
        runs.append((start, previous))

    events, index = [], 0
    for run_start, run_end in runs:
        length = int((run_end - run_start) / step) + 1
        if length < persistence:
            continue                      # never became an alert
        satisfied = run_start + (persistence - 1) * step
        events.append(AlertEvent(
            index=index, run_start=run_start, rule_satisfied_at=satisfied,
            issuable_at=satisfied + pd.Timedelta(hours=rules.reporting_lag_hours),
            end=run_end, hours=length))
        index += 1
    return events


def load_leaks(config_path: Path, zones: dict | None = None) -> pd.DataFrame:
    """Leak truth from the BattLeDIM generation configuration. Evaluation only."""
    pattern = re.compile(
        r'^-\s*(p\d+),\s*([\d-]+\s[\d:]+),\s*([\d-]+\s[\d:]+),\s*([\d.]+),\s*(\w+),\s*([\d-]+\s[\d:]+)')
    rows = []
    for line in config_path.read_text().splitlines():
        found = pattern.match(line.strip())
        if found:
            link, start, end, diameter, kind, peak = found.groups()
            rows.append({'link': link, 'start': pd.Timestamp(start), 'end': pd.Timestamp(end),
                         'diameter_m': float(diameter), 'type': kind, 'peak': pd.Timestamp(peak),
                         'zone': (zones or {}).get(link, 'unknown')})
    leaks = pd.DataFrame(rows).sort_values('start').reset_index(drop=True)
    assert set(leaks.type) <= {ABRUPT, INCIPIENT}, f'unexpected types: {set(leaks.type)}'
    return leaks


def add_observed_activity(leaks: pd.DataFrame, leakages_csv: Path) -> pd.DataFrame:
    """Add the interval over which each leak actually produces flow.

    The configuration's `start` is when the simulator BEGINS a leak, but a gradual
    ("incipient") leak ramps from zero, so it can produce no measurable flow for hours
    or days afterwards. Using the configured window to decide whether "a leak was
    running" would count those silent hours as leaky and shrink the quiet period.

    Matching and quiet-period exposure therefore both use `active_from`/`active_to`
    (positive flow). The configured onset is kept so detection delay can be reported
    against both.
    """
    truth = pd.read_csv(leakages_csv, sep=';', decimal=',',
                        parse_dates=['Timestamp']).set_index('Timestamp')
    leaks = leaks.copy()
    leaks['configured_start'], leaks['configured_end'] = leaks.start, leaks.end
    first, last = [], []
    for leak in leaks.itertuples():
        if leak.link not in truth.columns:
            first.append(leak.start); last.append(leak.end); continue
        positive = truth[leak.link]
        positive = positive[(positive.index >= leak.start) & (positive.index <= leak.end) & (positive > 0)]
        first.append(positive.index.min() if len(positive) else pd.NaT)
        last.append(positive.index.max() if len(positive) else pd.NaT)
    leaks['active_from'], leaks['active_to'] = first, last
    leaks['silent_hours_after_onset'] = (
        (leaks.active_from - leaks.configured_start) / pd.Timedelta(hours=1)).round(2)
    # matching and exposure run on the observed activity interval
    leaks['start'], leaks['end'] = leaks.active_from, leaks.active_to
    assert leaks.start.notna().all(), 'a leak produced no positive flow at all'
    return leaks


def mark_eligibility(leaks, window_start, window_end, rules: Rules) -> pd.DataFrame:
    """Rule 2. Say out loud which leaks can be scored, and why not."""
    window_start, window_end = pd.Timestamp(window_start), pd.Timestamp(window_end)
    leaks = leaks.copy()
    if 'zone' not in leaks.columns:
        leaks['zone'] = 'unspecified'
    reasons = []
    for leak in leaks.itertuples():
        if leak.start < window_start:
            reasons.append('excluded: began before the evaluation window')
        elif leak.start > window_end:
            reasons.append('excluded: begins after the evaluation window')
        else:
            reasons.append('eligible')
    leaks['eligibility'] = reasons
    leaks['censored_end'] = leaks.end > window_end
    return leaks


def match_events(events, leaks: pd.DataFrame, rules: Rules):
    """Rules 3-5. Candidate selection applies EVERY filter to one shrinking set.

    The order matters, and getting it wrong is how a leak that had already stopped was
    once credited. Each step narrows the same frame:

      running  leaks active when the unusual run BEGAN
      alive    of those, still active when the alert could be ISSUED
      in_time  of those, within `max_delay_hours` of first positive flow
      free     of those, not already credited to an earlier alert
      eligible of those, scorable at all

    Eligibility and prior-credit are applied to `in_time`, never to `running`, so an
    expired leak can no longer be selected just because a live one shares the moment.
    """
    claimed: set[str] = set()
    for event in sorted(events, key=lambda e: e.run_start):
        running = leaks[(leaks.start <= event.run_start) & (event.run_start <= leaks.end)]
        event.leaks_running = list(running.link)
        if running.empty:
            event.outcome = 'false_alert'          # no leak active in this zone at all
            continue

        # Still leaking at the moment the alert could be raised?
        alive = running[event.issuable_at <= running.end.values]
        if alive.empty:
            event.outcome = 'retrospective_association'
            event.matched_leak = list(running.link)[0]
            event.match_confidence = 'retrospective'
            continue

        # Within the deadline. NOTE: `leaks.start` is first positive flow, so the
        # deadline runs from when the leak began producing water, not from its
        # configured onset. See the note in add_observed_activity.
        if rules.max_delay_hours is None:
            in_time = alive
        else:
            deadline = alive.start + pd.Timedelta(hours=rules.max_delay_hours)
            in_time = alive[event.issuable_at <= deadline.values]
        event.candidates = list(in_time.link)
        if in_time.empty:
            event.outcome = 'unattributable'       # still leaking, but too late to credit
            continue

        free = in_time[~in_time.link.isin(claimed)]
        if free.empty:
            event.outcome = 'repeat_of_credited_leak'
            event.matched_leak = list(in_time.link)[0]
            event.match_confidence = 'repeat'
            continue

        order = free.sort_values('start', ascending=(rules.attribute_to == 'earliest'))
        chosen = order.iloc[0]
        if chosen.eligibility != 'eligible':
            event.outcome = 'coincides_with_excluded_leak'
            event.matched_leak, event.match_confidence = chosen.link, 'excluded_leak'
            continue
        claimed.add(chosen.link)
        event.matched_leak = chosen.link
        event.outcome = 'credited'
        event.match_confidence = 'ambiguous' if len(free) > 1 else 'single_candidate'
    return events


def score(above: pd.Series, persistence: int, leaks: pd.DataFrame,
          rules: Rules | None = None) -> dict:
    rules = rules or Rules()
    window_start, window_end = above.index[0], above.index[-1]
    leaks = mark_eligibility(leaks, window_start, window_end, rules)
    events = find_alerts(above, persistence, rules)
    # An alert whose issue time falls past the last reading cannot be confirmed here.
    inside = []
    for event in events:
        if event.issuable_at > window_end:
            event.outcome = 'issuable_after_window'
        else:
            inside.append(event)
    events = match_events(inside, leaks, rules) + [e for e in events
                                                   if e.outcome == 'issuable_after_window']
    events.sort(key=lambda e: e.run_start)

    credited = {e.matched_leak: e for e in events if e.outcome == 'credited'}
    eligible = leaks[leaks.eligibility == 'eligible']
    per_leak = []
    for leak in leaks.itertuples():
        event = credited.get(leak.link)
        per_leak.append({
            'link': leak.link, 'type': leak.type, 'zone': leak.zone,
            'start': str(leak.start), 'end': str(leak.end),
            'eligibility': leak.eligibility, 'censored_end': bool(leak.censored_end),
            'outcome': ('credited' if event else
                        'not_scored' if leak.eligibility != 'eligible' else 'missed'),
            'alert_index': (event.index if event else None),
            'match_confidence': (event.match_confidence if event else None),
            'delay_hours_from_first_flow': (
                round((event.issuable_at - leak.start) / pd.Timedelta(hours=1), 2) if event else None),
            'delay_hours_from_configured_onset': (
                round((event.issuable_at - getattr(leak, 'configured_start', leak.start))
                      / pd.Timedelta(hours=1), 2) if event else None),
            'silent_hours_after_onset': getattr(leak, 'silent_hours_after_onset', None),
        })

    def summarise(kind=None):
        chosen = eligible if kind is None else eligible[eligible.type == kind]
        hits = [r for r in per_leak if r['outcome'] == 'credited' and r['link'] in set(chosen.link)]
        delays = [r['delay_hours_from_first_flow'] for r in hits]
        return {'eligible_leaks': int(len(chosen)), 'credited': len(hits),
                'missed': int(len(chosen)) - len(hits),
                'ambiguous': sum(1 for r in hits if r['match_confidence'] == 'ambiguous'),
                'median_delay_hours': (round(float(pd.Series(delays).median()), 2) if delays else None)}

    weeks = (window_end - window_start) / pd.Timedelta(weeks=1)
    tally = {name: sum(1 for e in events if e.outcome == name) for name in
             ('credited', 'false_alert', 'unattributable', 'repeat_of_credited_leak',
              'coincides_with_excluded_leak', 'retrospective_association',
              'issuable_after_window')}
    return {
        'window': [str(window_start), str(window_end)],
        'rules': asdict(rules), 'persistence': persistence,
        'alert_events_total': len(events), 'outcomes': tally,
        'false_alerts_per_week': round(tally['false_alert'] / weeks, 3) if weeks else None,
        'overall': summarise(), 'abrupt': summarise(ABRUPT), 'incipient': summarise(INCIPIENT),
        'leaks': per_leak,
        'events': [asdict(e) | {k: str(getattr(e, k)) for k in
                                ('run_start', 'rule_satisfied_at', 'issuable_at', 'end')}
                   for e in events],
    }
