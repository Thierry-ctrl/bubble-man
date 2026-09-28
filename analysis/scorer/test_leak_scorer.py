"""Worked checks for scorer v2. Run: python3 analysis/scorer/test_leak_scorer.py

Each check is a tiny hand-built example whose right answer can be read off by eye.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from leak_scorer import Rules, find_alerts, mark_eligibility, score  # noqa: E402

HOURS = pd.date_range('2018-01-01', '2018-03-01 23:00', freq='h')
OPEN = Rules(max_delay_hours=None)     # no deadline; exercised separately
ONE = 1                                # one unusual hour is enough unless stated


def above(*spans):
    flagged = pd.Series(False, index=HOURS)
    for start, end in spans:
        flagged.loc[start:end] = True
    return flagged


def leaks(*rows):
    return pd.DataFrame([{'link': link, 'start': pd.Timestamp(s), 'end': pd.Timestamp(e),
                          'type': kind, 'diameter_m': 0.02, 'peak': pd.Timestamp(s),
                          'zone': 'main'} for link, s, e, kind in rows])


checks = []


def check(name):
    def wrap(fn):
        checks.append((name, fn)); return fn
    return wrap


@check('1. delay is measured from when the alert could be ISSUED, not when it began')
def _():
    # unusual from 02:00; persistence 6 met at 07:00; issuable 08:00. Leak began 00:00.
    r = score(above(('2018-02-01 02:00', '2018-02-01 20:00')), 6,
              leaks(('pA', '2018-02-01 00:00', '2018-02-10 00:00', 'abrupt')), OPEN)
    event = r['events'][0]
    assert event['run_start'].endswith('02:00:00'), event
    assert event['rule_satisfied_at'].endswith('07:00:00'), event
    assert event['issuable_at'].endswith('08:00:00'), event
    assert r['leaks'][0]['delay_hours'] == 8.0, r['leaks'][0]


@check('2. a run shorter than the persistence requirement raises no alert at all')
def _():
    r = score(above(('2018-02-01 02:00', '2018-02-01 04:00')), 6,
              leaks(('pA', '2018-02-01 00:00', '2018-02-10 00:00', 'abrupt')), OPEN)
    assert r['alert_events_total'] == 0, r
    assert r['overall']['missed'] == 1


@check('3. a leak with no warning is missed, not silently dropped')
def _():
    r = score(above(), ONE, leaks(('pA', '2018-02-01 00:00', '2018-02-10 00:00', 'abrupt')), OPEN)
    assert r['overall']['credited'] == 0 and r['overall']['missed'] == 1
    assert r['leaks'][0]['delay_hours'] is None


@check('4. a warning with NO leak running is a confirmed false alert')
def _():
    r = score(above(('2018-01-05 00:00', '2018-01-05 06:00')), ONE,
              leaks(('pA', '2018-02-01 00:00', '2018-02-10 00:00', 'abrupt')), OPEN)
    assert r['outcomes']['false_alert'] == 1, r['outcomes']
    assert r['events'][0]['leaks_running'] == []


@check('5. repeats of a credited leak score zero and are NOT false alerts')
def _():
    r = score(above(('2018-02-02 00:00', '2018-02-02 04:00'),
                    ('2018-02-04 00:00', '2018-02-04 04:00'),
                    ('2018-02-06 00:00', '2018-02-06 04:00')), ONE,
              leaks(('pA', '2018-02-01 00:00', '2018-02-10 00:00', 'abrupt')), OPEN)
    assert r['alert_events_total'] == 3
    assert r['overall']['credited'] == 1, 'one leak must not be caught three times'
    assert r['outcomes']['repeat_of_credited_leak'] == 2, r['outcomes']
    assert r['outcomes']['false_alert'] == 0


@check('6. a warning while an uncredited leak runs but past the deadline is UNATTRIBUTABLE')
def _():
    # leak starts 1 Feb; warning 20 Feb, far past a 7-day deadline; nothing credited yet.
    r = score(above(('2018-02-20 00:00', '2018-02-20 06:00')), ONE,
              leaks(('pA', '2018-02-01 00:00', '2018-02-28 00:00', 'abrupt')),
              Rules(max_delay_hours=168))
    assert r['outcomes']['unattributable'] == 1, r['outcomes']
    assert r['outcomes']['false_alert'] == 0, 'a leak WAS running; this is not a false alert'
    assert r['overall']['missed'] == 1, 'and the leak is still not credited'


@check('7. overlapping leaks give an ambiguous match with candidates recorded')
def _():
    r = score(above(('2018-02-06 00:00', '2018-02-06 04:00')), ONE,
              leaks(('pA', '2018-02-01 00:00', '2018-02-20 00:00', 'abrupt'),
                    ('pB', '2018-02-05 00:00', '2018-02-15 00:00', 'abrupt')), OPEN)
    event = r['events'][0]
    assert sorted(event['leaks_running']) == ['pA', 'pB'], event
    assert event['match_confidence'] == 'ambiguous'
    assert event['matched_leak'] == 'pB', 'most recent onset wins by default'
    assert r['overall']['credited'] == 1 and r['overall']['missed'] == 1


@check('8. a run already under way before onset is NOT credited to that leak')
def _():
    r = score(above(('2018-01-31 22:00', '2018-02-03 00:00')), ONE,
              leaks(('pA', '2018-02-01 00:00', '2018-02-10 00:00', 'abrupt')), OPEN)
    assert r['overall']['credited'] == 0, 'must not claim a pre-existing run'
    assert r['overall']['missed'] == 1
    assert r['outcomes']['false_alert'] == 1, 'it began when nothing was leaking'


@check('9. the deadline blocks a credit that arrives too late')
def _():
    late = score(above(('2018-02-20 00:00', '2018-02-20 06:00')), ONE,
                 leaks(('pA', '2018-02-01 00:00', '2018-02-28 00:00', 'abrupt')),
                 Rules(max_delay_hours=168))
    open_ = score(above(('2018-02-20 00:00', '2018-02-20 06:00')), ONE,
                  leaks(('pA', '2018-02-01 00:00', '2018-02-28 00:00', 'abrupt')), OPEN)
    assert late['overall']['credited'] == 0 and open_['overall']['credited'] == 1


@check('10. grouping: a one-hour lull splits runs only when tolerance is 0')
def _():
    flagged = above(('2018-02-02 00:00', '2018-02-02 03:00'),
                    ('2018-02-02 05:00', '2018-02-02 08:00'))
    assert len(find_alerts(flagged, 1, Rules(gap_tolerance_hours=0))) == 2
    assert len(find_alerts(flagged, 1, Rules(gap_tolerance_hours=1))) == 1


@check('11. one event cannot claim two leaks; the second stays missed')
def _():
    r = score(above(('2018-02-06 00:00', '2018-02-19 00:00')), ONE,
              leaks(('pA', '2018-02-01 00:00', '2018-02-20 00:00', 'abrupt'),
                    ('pB', '2018-02-05 00:00', '2018-02-15 00:00', 'abrupt')), OPEN)
    assert r['overall']['credited'] == 1 and r['overall']['missed'] == 1


@check('12. leaks beginning before the window are excluded, not counted as missed')
def _():
    r = score(above(), ONE, leaks(('pA', '2017-12-20 00:00', '2018-02-10 00:00', 'abrupt')), OPEN)
    assert r['overall']['eligible_leaks'] == 0
    assert r['leaks'][0]['outcome'] == 'not_scored'
    assert 'began before' in r['leaks'][0]['eligibility']


@check('13. abrupt and gradual leaks are summarised separately')
def _():
    r = score(above(('2018-02-02 00:00', '2018-02-02 04:00')), ONE,
              leaks(('pA', '2018-02-01 00:00', '2018-02-10 00:00', 'abrupt'),
                    ('pB', '2018-02-15 00:00', '2018-02-20 00:00', 'incipient')), OPEN)
    assert r['abrupt']['credited'] == 1 and r['abrupt']['missed'] == 0
    assert r['incipient']['credited'] == 0 and r['incipient']['missed'] == 1
    assert r['abrupt']['median_delay_hours'] == 25.0, r['abrupt']


@check('14. a leak running past the window end is flagged as censored')
def _():
    r = score(above(), ONE, leaks(('pA', '2018-02-01 00:00', '2019-06-01 00:00', 'incipient')), OPEN)
    assert r['leaks'][0]['censored_end'] is True
    assert r['leaks'][0]['eligibility'] == 'eligible'


@check('15. eligibility reports the reason, it does not guess')
def _():
    frame = mark_eligibility(leaks(('pA', '2018-05-05 00:00', '2018-06-10 00:00', 'abrupt')),
                             '2018-01-01', '2018-03-01', Rules())
    assert 'begins after' in frame.eligibility.iloc[0]


if __name__ == '__main__':
    failed = 0
    for name, fn in checks:
        try:
            fn(); print(f'  PASS  {name}')
        except AssertionError as problem:
            failed += 1; print(f'  FAIL  {name}\n        {problem}')
    print(f'\n{len(checks) - failed}/{len(checks)} checks passed')
    sys.exit(1 if failed else 0)
