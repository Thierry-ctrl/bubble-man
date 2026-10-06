"""Independent re-check of the 2018 night-step claims. Reads ONLY 2018-derived leak records.

The original run_night_step.py parses battledim-config.yaml, which also contains the 2019
leak schedule. This check avoids that file entirely: leak records come from
analysis/scorer/main-zone-leaks-A_reference_inherited.csv (12 main-zone 2018 leaks, start
= first positive flow, end = last positive flow). Detector and scorer are unchanged.
"""
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent; ROOT = OUT.parents[1]
sys.path.insert(0, str(OUT)); sys.path.insert(0, str(ROOT / 'analysis/scorer'))
from night_signal import night_series          # noqa: E402
from leak_scorer import Rules, score           # noqa: E402

RULES = Rules(gap_tolerance_hours=0, reporting_lag_hours=1.0, max_delay_hours=168)
night, step = night_series()

# rule, re-implemented from RULE-FROZEN.md rather than imported
warn, armed, last = [], True, None
for d, s in step.loc['2018-01-15':'2018-12-31'].items():
    if not np.isfinite(s): continue
    if s < 10.0: armed = True; continue
    if armed and (last is None or (d + pd.Timedelta(hours=4)) - last >= pd.Timedelta(days=7)):
        warn.append(d); armed, last = False, d + pd.Timedelta(hours=4)

leaks = pd.read_csv(ROOT / 'analysis/scorer/main-zone-leaks-A_reference_inherited.csv', parse_dates=['start', 'end'])
leaks = leaks[['link', 'type', 'zone', 'start', 'end']].copy()
leaks['diameter_m'], leaks['peak'], leaks['configured_start'] = 0.02, leaks.start, leaks.start
assert len(leaks) == 12 and set(leaks.zone) == {'main'}

def series(nights, a, b):
    s = pd.Series(False, index=pd.date_range(a, b, freq='h'))
    for d in nights:
        t = d + pd.Timedelta(hours=3)
        if t in s.index: s.loc[t] = True
    return s

full = score(series(warn, '2018-01-15 00:00', '2018-12-31 23:00'), 1, leaks, RULES)
dom = pd.date_range('2018-01-15', '2018-12-30', freq='D'); pos = [dom.get_loc(d) for d in warn if d in dom]
patterns = {tuple(sorted((i + 7 * k) % 350 for i in pos)) for k in range(50)}
shift_abrupt, shift_all = [], []
for k in range(1, 50):
    p = sorted((i + 7 * k) % 350 for i in pos)
    o = score(series([dom[i] for i in p], '2018-01-15 00:00', '2018-12-30 23:00'), 1, leaks, RULES)
    shift_abrupt.append(o['abrupt']['credited']); shift_all.append(o['overall']['credited'])
real_dom = score(series([dom[i] for i in pos], '2018-01-15 00:00', '2018-12-30 23:00'), 1, leaks, RULES)

ch = night.loc['2018-01-15':'2018-12-31'].diff().dropna()
q1, q3 = np.percentile(ch, [25, 75])
v = {
    'warnings': [str(d.date()) for d in warn],
    'credited': full['overall']['credited'], 'abrupt': f"{full['abrupt']['credited']}/{full['abrupt']['eligible_leaks']}",
    'gradual': f"{full['incipient']['credited']}/{full['incipient']['eligible_leaks']}",
    'outcomes': full['outcomes'],
    'events': [(e['run_start'][:16], e['outcome'], e['matched_leak'], e['match_confidence'], e['candidates'])
               for e in full['events']],
    'distinct_whole_week_patterns_including_original': len(patterns),
    'real_in_domain_abrupt': real_dom['abrupt']['credited'],
    'shift_abrupt_counts': {int(k): int(c) for k, c in zip(*np.unique(shift_abrupt, return_counts=True))},
    'p_abrupt': (1 + sum(a >= real_dom['abrupt']['credited'] for a in shift_abrupt)) / 50,
    'p_all': (1 + sum(a >= real_dom['overall']['credited'] for a in shift_all)) / 50,
    'noise_std': round(float(ch.std()), 2), 'noise_robust_sigma': round(float((q3 - q1) / 1.349), 2),
}
(OUT / 'verify-2018.json').write_text(json.dumps(v, indent=2, default=str) + '\n')
print(json.dumps(v, indent=2, default=str))
