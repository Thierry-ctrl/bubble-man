"""Worked checks for the scorer. Run: python3 analysis/scorer/test_leak_scorer.py

Each check is a tiny hand-built example whose right answer can be read off by eye,
so the counting rules can be trusted before they are pointed at real data.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from leak_scorer import Rules, group_alerts, mark_eligibility, score  # noqa: E402

HOURS = pd.date_range('2018-01-01', '2018-03-01 23:00', freq='h')
RULES = Rules(min_history_days=0)          # eligibility is tested separately


def warnings(*spans):
    """Boolean series, True during each (start, end) span given as strings."""
    flagged = pd.Series(False, index=HOURS)
    for start, end in spans:
        flagged.loc[start:end] = True
    return flagged


def leaks(*rows):
    return pd.DataFrame([{'link': link, 'start': pd.Timestamp(s), 'end': pd.Timestamp(e),
                          'type': kind, 'diameter_m': 0.02, 'peak': pd.Timestamp(s)}
                         for link, s, e, kind in rows])


checks = []


def check(name):
    def wrap(fn):
        checks.append((name, fn))
        return fn
    return wrap


@check('1. a caught leak is matched, with the right delay')
def _():
    result = score(warnings(('2018-02-02 00:00', '2018-02-02 04:00')),
                   leaks(('pA', '2018-02-01 00:00', '2018-02-10 00:00', 'abrupt')), RULES)
    assert result['overall']['matched'] == 1, result['overall']
    assert result['overall']['missed'] == 0
    assert result['leaks'][0]['delay_hours'] == 24.0, result['leaks'][0]
    assert result['leaks'][0]['match_confidence'] == 'single_candidate'


@check('2. a leak with no warning is missed, not silently dropped')
def _():
    result = score(warnings(), leaks(('pA', '2018-02-01 00:00', '2018-02-10 00:00', 'abrupt')), RULES)
    assert result['overall']['matched'] == 0
    assert result['overall']['missed'] == 1
    assert result['leaks'][0]['outcome'] == 'missed'
    assert result['leaks'][0]['delay_hours'] is None


@check('3. a warning with no leak running is an unnecessary warning')
def _():
    result = score(warnings(('2018-01-05 00:00', '2018-01-05 06:00')),
                   leaks(('pA', '2018-02-01 00:00', '2018-02-10 00:00', 'abrupt')), RULES)
    assert result['unmatched_alerts'] == 1, result
    assert result['overall']['matched'] == 0
    assert result['events'][0]['outcome'] == 'unmatched'


@check('4. repeated warnings about one leak count once, and are not false alarms')
def _():
    result = score(warnings(('2018-02-02 00:00', '2018-02-02 04:00'),
                            ('2018-02-04 00:00', '2018-02-04 04:00'),
                            ('2018-02-06 00:00', '2018-02-06 04:00')),
                   leaks(('pA', '2018-02-01 00:00', '2018-02-10 00:00', 'abrupt')), RULES)
    assert result['alert_events_total'] == 3, result['alert_events_total']
    assert result['overall']['matched'] == 1, 'one leak must not be caught three times'
    assert result['repeat_alerts_scored_zero'] == 2, result
    assert result['unmatched_alerts'] == 0, 'repeats must not be charged as false alarms'


@check('5. overlapping leaks give an ambiguous match, with candidates recorded')
def _():
    result = score(warnings(('2018-02-06 00:00', '2018-02-06 04:00')),
                   leaks(('pA', '2018-02-01 00:00', '2018-02-20 00:00', 'abrupt'),
                         ('pB', '2018-02-05 00:00', '2018-02-15 00:00', 'abrupt')), RULES)
    event = result['events'][0]
    assert sorted(event['candidates']) == ['pA', 'pB'], event
    assert event['match_confidence'] == 'ambiguous'
    assert event['matched_leak'] == 'pB', 'most recent onset wins by default'
    assert result['overall']['matched'] == 1, 'one warning cannot catch two leaks'
    assert result['overall']['missed'] == 1


@check('6. a warning already running before onset is NOT credited to that leak')
def _():
    result = score(warnings(('2018-01-31 22:00', '2018-02-03 00:00')),
                   leaks(('pA', '2018-02-01 00:00', '2018-02-10 00:00', 'abrupt')), RULES)
    assert result['overall']['matched'] == 0, 'must not take credit for a pre-existing alert'
    assert result['overall']['missed'] == 1
    assert result['unmatched_alerts'] == 1


@check('7. grouping: a one-hour lull splits events only when tolerance is 0')
def _():
    flagged = warnings(('2018-02-02 00:00', '2018-02-02 03:00'),
                       ('2018-02-02 05:00', '2018-02-02 08:00'))
    assert len(group_alerts(flagged, Rules(gap_tolerance_hours=0))) == 2
    assert len(group_alerts(flagged, Rules(gap_tolerance_hours=1))) == 1


@check('8. one event cannot claim two leaks; the second stays missed')
def _():
    result = score(warnings(('2018-02-06 00:00', '2018-02-19 00:00')),
                   leaks(('pA', '2018-02-01 00:00', '2018-02-20 00:00', 'abrupt'),
                         ('pB', '2018-02-05 00:00', '2018-02-15 00:00', 'abrupt')), RULES)
    assert result['overall']['matched'] == 1
    assert result['overall']['missed'] == 1


@check('9. leaks beginning before the window are excluded, not counted as missed')
def _():
    result = score(warnings(), leaks(('pA', '2017-12-20 00:00', '2018-02-10 00:00', 'abrupt')),
                   Rules(min_history_days=0))
    assert result['overall']['eligible_leaks'] == 0, result['overall']
    assert result['leaks'][0]['outcome'] == 'not_scored'
    assert 'began before' in result['leaks'][0]['eligibility']


@check('10. insufficient history excludes a leak, and says so')
def _():
    frame = mark_eligibility(leaks(('pA', '2018-01-05 00:00', '2018-02-10 00:00', 'abrupt')),
                             '2018-01-01', '2018-03-01', Rules(min_history_days=14))
    assert 'fewer than 14 days of history' in frame.eligibility.iloc[0]


@check('11. an alert coinciding with an excluded leak is neither hit nor false alarm')
def _():
    result = score(warnings(('2018-01-20 00:00', '2018-01-20 06:00')),
                   leaks(('pA', '2018-01-05 00:00', '2018-02-10 00:00', 'abrupt')),
                   Rules(min_history_days=14))
    assert result['alerts_coinciding_with_excluded_leak'] == 1, result
    assert result['unmatched_alerts'] == 0
    assert result['overall']['eligible_leaks'] == 0


@check('12. abrupt and incipient leaks are reported separately')
def _():
    result = score(warnings(('2018-02-02 00:00', '2018-02-02 04:00')),
                   leaks(('pA', '2018-02-01 00:00', '2018-02-10 00:00', 'abrupt'),
                         ('pB', '2018-02-15 00:00', '2018-02-20 00:00', 'incipient')), RULES)
    assert result['abrupt'] == {'eligible_leaks': 1, 'matched': 1, 'missed': 0,
                                'ambiguous_matches': 0, 'median_delay_hours': 24.0,
                                'max_delay_hours': 24.0}, result['abrupt']
    assert result['incipient']['matched'] == 0 and result['incipient']['missed'] == 1


@check('13. a leak running past the window end is flagged as censored')
def _():
    result = score(warnings(), leaks(('pA', '2018-02-01 00:00', '2019-06-01 00:00', 'incipient')),
                   RULES)
    assert result['leaks'][0]['censored_end'] is True
    assert result['leaks'][0]['eligibility'] == 'eligible', 'onset is in window, so it is scorable'


if __name__ == '__main__':
    failures = 0
    for name, fn in checks:
        try:
            fn()
            print(f'  PASS  {name}')
        except AssertionError as problem:
            failures += 1
            print(f'  FAIL  {name}\n        {problem}')
    print(f'\n{len(checks) - failures}/{len(checks)} checks passed')
    sys.exit(1 if failures else 0)
