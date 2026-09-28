"""Event-level scorer: did a warning arrive while a known leak was running?

WHAT THIS TOOL CLAIMS, AND WHAT IT DOES NOT
-------------------------------------------
Our detectors watch total flow at one meter. They can say "flow is higher than
expected"; they cannot say "the leak is on pipe p673". So a warning that arrives
while a leak is running is a COINCIDENCE IN TIME, not proof that the method found
that particular leak. Every match this tool reports is labelled with how confident
the association is, and the word used throughout is "match", never "detection".

This is deliberately NOT the BattLeDIM competition score. That score additionally
requires the reported location to be within 300 m of the leak, and converts the
result into euros of water saved minus crew cost. We cannot compute it, because we
report no location. See analysis/scorer/RULES.md.

THE RULES, IN ORDER
-------------------
1. Group    consecutive warning hours become ONE alert event. A lull shorter than
            `gap_tolerance_hours` does not split an event.
2. Eligible a leak counts in the denominator only if its onset falls inside the
            evaluation window with `min_history_days` of readings before it.
            Leaks starting earlier are excluded and reported as excluded.
3. Match    an alert event matches a leak if the event's START time lies inside
            [leak start, leak end], and — when `max_delay_hours` is set — within that
            many hours of onset. An event already running before a leak begins
            therefore CANNOT be credited to that leak.
4. One-to-one  each event is credited to at most one leak; each leak is credited to
            at most one event. A later event about an already-credited leak scores
            zero: it is neither a hit nor a false alarm, matching BattLeDIM's
            "repeated detections of the same leakage are ignored".
5. Ambiguity   when several leaks are active at an event's start, the event is
            attributed to the most recently started one, and the match is labelled
            `ambiguous` with every candidate recorded.
6. Delay    hours from leak onset to the start of its matching event.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
import re

import pandas as pd

ABRUPT, INCIPIENT = 'abrupt', 'incipient'


@dataclass
class Rules:
    """Every knob that changes a number. Change these, not the code below."""
    gap_tolerance_hours: int = 0      # lull allowed inside one alert event
    min_history_days: int = 14        # readings a leak needs before its onset
    attribute_to: str = 'most_recent'  # or 'earliest', when several leaks are active
    max_delay_hours: float | None = None
    """How soon after onset a warning must arrive to be credited.

    None reproduces the BattLeDIM paper, where any time inside the leak's life counts.
    That is far too generous here: in L-Town 2018 a leak is running 100% of the time,
    so almost any warning lands inside some leak and the score measures alert density
    rather than detection. Setting this to e.g. 168 (one week, the window the
    competition website originally described) gives chance a much smaller target."""


@dataclass
class AlertEvent:
    index: int
    start: pd.Timestamp
    end: pd.Timestamp
    hours: int
    matched_leak: str | None = None
    match_confidence: str | None = None   # single_candidate | ambiguous | None
    candidates: list = field(default_factory=list)
    outcome: str = 'unmatched'            # matched | unmatched | matched_excluded_leak


def group_alerts(flagged: pd.Series, rules: Rules) -> list[AlertEvent]:
    """Turn a boolean hourly series into alert events (rule 1)."""
    assert flagged.index.is_monotonic_increasing, 'timestamps must be sorted'
    assert flagged.dtype == bool, 'expected a boolean series'
    events, start, previous = [], None, None
    for stamp, flag in flagged.items():
        if flag:
            if start is None:
                start, previous = stamp, stamp
            else:
                lull = (stamp - previous) / pd.Timedelta(hours=1) - 1
                if lull > rules.gap_tolerance_hours:
                    events.append((start, previous))
                    start = stamp
                previous = stamp
    if start is not None:
        events.append((start, previous))
    return [AlertEvent(index=i, start=s, end=e,
                       hours=int((e - s) / pd.Timedelta(hours=1)) + 1)
            for i, (s, e) in enumerate(events)]


def load_leaks(config_path: Path) -> pd.DataFrame:
    """Read leak truth from the BattLeDIM scenario configuration.

    This file is the simulator's generation input, so it lists every leak that was
    actually simulated. Read it only for evaluation, never as a detector input.
    """
    pattern = re.compile(
        r'^-\s*(p\d+),\s*([\d-]+\s[\d:]+),\s*([\d-]+\s[\d:]+),\s*([\d.]+),\s*(\w+),\s*([\d-]+\s[\d:]+)')
    rows = []
    for line in config_path.read_text().splitlines():
        found = pattern.match(line.strip())
        if found:
            link, start, end, diameter, kind, peak = found.groups()
            rows.append({'link': link, 'start': pd.Timestamp(start), 'end': pd.Timestamp(end),
                         'diameter_m': float(diameter), 'type': kind, 'peak': pd.Timestamp(peak)})
    leaks = pd.DataFrame(rows).sort_values('start').reset_index(drop=True)
    assert set(leaks.type) <= {ABRUPT, INCIPIENT}, f'unexpected leak types: {set(leaks.type)}'
    return leaks


def mark_eligibility(leaks: pd.DataFrame, window_start, window_end, rules: Rules) -> pd.DataFrame:
    """Rule 2. Say out loud which leaks can and cannot be scored, and why."""
    window_start, window_end = pd.Timestamp(window_start), pd.Timestamp(window_end)
    earliest = window_start + pd.Timedelta(days=rules.min_history_days)
    leaks = leaks.copy()
    reasons = []
    for _, leak in leaks.iterrows():
        if leak.start < window_start:
            reasons.append('excluded: began before the evaluation window')
        elif leak.start < earliest:
            reasons.append(f'excluded: fewer than {rules.min_history_days} days of history before onset')
        elif leak.start > window_end:
            reasons.append('excluded: begins after the evaluation window')
        else:
            reasons.append('eligible')
    leaks['eligibility'] = reasons
    leaks['censored_end'] = leaks.end > window_end
    return leaks


def match_events(events: list[AlertEvent], leaks: pd.DataFrame, rules: Rules) -> list[AlertEvent]:
    """Rules 3-5. Greedy over events in time order, one-to-one both ways."""
    claimed: set[str] = set()
    for event in sorted(events, key=lambda e: e.start):
        deadline = leaks.end if rules.max_delay_hours is None else pd.concat([
            leaks.end, leaks.start + pd.Timedelta(hours=rules.max_delay_hours)], axis=1).min(axis=1)
        active = leaks[(leaks.start <= event.start) & (event.start <= deadline)]
        event.candidates = list(active.link)
        available = active[~active.link.isin(claimed)]
        if active.empty:
            # Nothing was running. This is an unnecessary warning.
            event.outcome = 'unmatched'
            continue
        if available.empty:
            # Every leak running now is already credited to an earlier event.
            # BattLeDIM scores these zero, so they are neither a hit nor a false alarm.
            event.outcome = 'repeat_of_matched_leak'
            event.matched_leak = list(active.link)[0]
            event.match_confidence = 'repeat'
            continue
        order = available.sort_values('start', ascending=(rules.attribute_to == 'earliest'))
        chosen = order.iloc[0]
        if chosen.eligibility != 'eligible':
            # Coincides with a leak we agreed not to score. Neither a hit nor a false alarm.
            event.outcome = 'matched_excluded_leak'
            event.matched_leak = chosen.link
            event.match_confidence = 'excluded_leak'
            continue
        claimed.add(chosen.link)
        event.matched_leak = chosen.link
        event.outcome = 'matched'
        event.match_confidence = 'ambiguous' if len(available) > 1 else 'single_candidate'
    return events


def score(flagged: pd.Series, leaks: pd.DataFrame, rules: Rules | None = None) -> dict:
    """Run the whole pipeline and return a fully traceable result."""
    rules = rules or Rules()
    window_start, window_end = flagged.index[0], flagged.index[-1]
    leaks = mark_eligibility(leaks, window_start, window_end, rules)
    events = match_events(group_alerts(flagged, rules), leaks, rules)

    matched = {e.matched_leak: e for e in events if e.outcome == 'matched'}
    eligible = leaks[leaks.eligibility == 'eligible']
    per_leak = []
    for _, leak in leaks.iterrows():
        event = matched.get(leak.link)
        delay = ((event.start - leak.start) / pd.Timedelta(hours=1)) if event else None
        per_leak.append({
            'link': leak.link, 'type': leak.type,
            'start': str(leak.start), 'end': str(leak.end),
            'eligibility': leak.eligibility, 'censored_end': bool(leak.censored_end),
            'outcome': ('matched' if event else
                        'not_scored' if leak.eligibility != 'eligible' else 'missed'),
            'matched_alert_index': (event.index if event else None),
            'match_confidence': (event.match_confidence if event else None),
            'delay_hours': (round(delay, 2) if delay is not None else None),
        })

    def summarise(kind=None):
        chosen = eligible if kind is None else eligible[eligible.type == kind]
        hits = [r for r in per_leak if r['outcome'] == 'matched' and r['link'] in set(chosen.link)]
        delays = [r['delay_hours'] for r in hits]
        return {
            'eligible_leaks': int(len(chosen)),
            'matched': len(hits),
            'missed': int(len(chosen)) - len(hits),
            'ambiguous_matches': sum(1 for r in hits if r['match_confidence'] == 'ambiguous'),
            'median_delay_hours': (round(float(pd.Series(delays).median()), 2) if delays else None),
            'max_delay_hours': (max(delays) if delays else None),
        }

    weeks = (window_end - window_start) / pd.Timedelta(weeks=1)
    unmatched = [e for e in events if e.outcome == 'unmatched']
    return {
        'window': [str(window_start), str(window_end)],
        'rules': asdict(rules),
        'alert_events_total': len(events),
        'unmatched_alerts': len(unmatched),
        'unmatched_alerts_per_week': round(len(unmatched) / weeks, 2) if weeks else None,
        'alerts_coinciding_with_excluded_leak': sum(1 for e in events
                                                    if e.outcome == 'matched_excluded_leak'),
        'repeat_alerts_scored_zero': sum(1 for e in events
                                         if e.outcome == 'repeat_of_matched_leak'),
        'overall': summarise(),
        'abrupt': summarise(ABRUPT),
        'incipient': summarise(INCIPIENT),
        'leaks': per_leak,
        'events': [asdict(e) | {'start': str(e.start), 'end': str(e.end)} for e in events],
    }
