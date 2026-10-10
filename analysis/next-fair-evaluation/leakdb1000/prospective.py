"""Prospective scoring with explicit timing (PROTOCOL-LEAKDB-1000.md, section 5).

The night reading of night D is built from the 30-minute readings stamped
    ns:00, ns:30, ns+1:00, ns+1:30   on day D            (the contributing interval)
LeakDB readings are values at their timestamp, so the night reading is COMPLETE at the last
contributing stamp, t_last = D + ns h 30 min + 1 h. A warning is ISSUABLE at the end of the
night window, t_issue = D + (ns + 2) h, as in every earlier protocol.

A leak can be ASSOCIATED with a warning only if it could have affected a contributing
reading: its first positive flow is at or before t_last, and it was still flowing at the
first contributing stamp or later. Then, exactly as the frozen scorer's chain:
  running  first flow <= t_last  and  last flow >= t_first
  alive    still flowing at t_issue (last flow >= t_issue)       else retrospective_association
  in_time  t_issue - first flow <= 168 h                          else unattributable
  free     not already credited to an earlier warning            else repeat_of_credited_leak
  chosen   most recent first flow among free; credited if eligible, else coincides_with_excluded_leak
No leak running at all -> false_alert. Delay = t_issue - first flow.
This replaces the hour-start convention of the locked scorer (which timed a warning at
ns+1:00 and so could not see a leak first flowing at ns+1:30).
"""
from __future__ import annotations
import numpy as np
import pandas as pd

DEADLINE = pd.Timedelta(hours=168)
WARN_FROM, DOMAIN_DAYS = 28, 336
OUTCOMES = ('credited', 'false_alert', 'unattributable', 'repeat_of_credited_leak',
            'coincides_with_excluded_leak', 'retrospective_association')


def night_times(day0, d, ns):
    base = day0 + pd.Timedelta(days=int(d))
    return (base + pd.Timedelta(hours=ns), base + pd.Timedelta(hours=ns + 1, minutes=30),
            base + pd.Timedelta(hours=ns + 2))


def score(warn_days, day0, ns, leaks, first_day=WARN_FROM, last_day=364):
    """leaks: columns link, type, start (first positive flow), end (last positive flow)."""
    w0 = day0 + pd.Timedelta(days=first_day)
    w1 = day0 + pd.Timedelta(days=last_day, hours=23, minutes=30)
    lk = leaks[leaks.start.notna()].copy()
    lk['eligible'] = (lk.start >= w0) & (lk.start <= w1)
    claimed, events = {}, []
    for d in sorted(warn_days):
        if not (first_day <= d <= last_day):
            continue
        t_first, t_last, t_issue = night_times(day0, d, ns)
        e = {'day': int(d), 'issue': t_issue, 'outcome': None, 'leak': None, 'confidence': None}
        running = lk[(lk.start <= t_last) & (lk.end >= t_first)]
        if running.empty:
            e['outcome'] = 'false_alert'
        else:
            alive = running[running.end >= t_issue]
            if alive.empty:
                e['outcome'] = 'retrospective_association'
            else:
                in_time = alive[t_issue - alive.start <= DEADLINE]
                if in_time.empty:
                    e['outcome'] = 'unattributable'
                else:
                    free = in_time[~in_time.link.isin(list(claimed))]
                    if free.empty:
                        e['outcome'] = 'repeat_of_credited_leak'
                    else:
                        c = free.sort_values('start', ascending=False).iloc[0]
                        e['leak'] = c.link
                        if not c.eligible:
                            e['outcome'] = 'coincides_with_excluded_leak'
                        else:
                            e['outcome'] = 'credited'
                            e['confidence'] = 'ambiguous' if len(free) > 1 else 'single_candidate'
                            claimed[c.link] = (t_issue - c.start) / pd.Timedelta(hours=1)
        events.append(e)
    per_leak = [{'link': l.link, 'type': l.type, 'start': l.start, 'eligible': bool(l.eligible),
                 'outcome': 'credited' if l.link in claimed else ('missed' if l.eligible else 'not_scored'),
                 'delay_h': claimed.get(l.link)} for l in lk.itertuples()]
    tally = {o: sum(e['outcome'] == o for e in events) for o in OUTCOMES}
    summ = lambda t: {'eligible': sum(p['eligible'] and p['type'] == t for p in per_leak),
                      'credited': sum(p['outcome'] == 'credited' and p['type'] == t for p in per_leak)}
    return {'events': events, 'leaks': per_leak, 'outcomes': tally, 'warnings': len(events),
            'abrupt': summ('abrupt'), 'incipient': summ('incipient')}


def leak_free_hours(leaks, day0, first_day=WARN_FROM, last_day=364):
    """Hours (30-minute stamps / 2) in the window with no leak flowing."""
    g = pd.date_range(day0 + pd.Timedelta(days=first_day), day0 + pd.Timedelta(days=last_day, hours=23, minutes=30), freq='30min')
    on = np.zeros(len(g), bool)
    for l in leaks[leaks.start.notna()].itertuples():
        on |= (g >= l.start) & (g <= l.end)
    return float((~on).sum()) / 2


def shift_days(warn_days, k):
    return sorted(WARN_FROM + ((d - WARN_FROM + 7 * k) % DOMAIN_DAYS)
                  for d in warn_days if WARN_FROM <= d < WARN_FROM + DOMAIN_DAYS)


def shift_comparison(scen):
    """scen: dicts with warn_days, day0, ns, leaks. Same k for every scenario; scored on the
    48-week domain (days 29-364) with the prospective rule."""
    def pooled(k):
        a = n = 0
        for s in scen:
            r = score(shift_days(s['warn_days'], k), s['day0'], s['ns'], s['leaks'],
                      last_day=WARN_FROM + DOMAIN_DAYS - 1)
            a += r['abrupt']['credited']; n += r['outcomes']['credited']
        return a, n
    ra, rn = pooled(0)
    rows = [dict(zip(('k_weeks', 'abrupt', 'all'), (k, *pooled(k)))) for k in range(1, DOMAIN_DAYS // 7)]
    sh = pd.DataFrame(rows)
    return {'real_in_domain_abrupt': ra, 'real_in_domain_all': rn, 'distinct_shifts': len(sh),
            'shift_abrupt_max': int(sh.abrupt.max()), 'shift_abrupt_median': float(sh.abrupt.median()),
            'p_abrupt': (1 + int((sh.abrupt >= ra).sum())) / (len(sh) + 1)}, sh
