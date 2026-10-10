"""Reporting corrections (11 Oct 2026). Recomputes DESCRIPTIVE statistics only; no warning,
score, criterion or verdict changes. Both LeakDB Hanoi sets: development (500-set, scenarios
11-500) and held-out (1,000-set)."""
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE / 'leakdb1000')); import io1000
DATA = ROOT / 'data/leakdb'
SETS = {'development_500set': (HERE / 'leakdb/run', DATA / 'hanoi-inlet', DATA / 'hanoi-leaks', 'Q1_selfaligning_plain'),
        'heldout_1000set': (HERE / 'leakdb1000/run', DATA / 'hanoi1000-inlet', DATA / 'hanoi1000-leaks', None)}
out = {}
for name, (run, inlet, leakdir, _) in SETS.items():
    A = pd.read_csv(run / 'scenarios-assessability.csv')
    L = pd.read_csv(run / 'leaks-table.csv', parse_dates=['start', 'end'])
    L = L[L.never_flowed.astype(str) != 'True']
    final, stop, fluct, zero_share, any_zero = {}, [], [], [], []
    for k, g in L.groupby('scenario'):
        s = io1000.read_inlet(inlet / f'Scenario-{k}_Link_1.csv'); final_ts = s.index[-1]
        ns = int(A[A.scenario == k].night_start_hour.iloc[0])
        for r in g.itertuples():
            stop.append(r.end < final_ts)
            if r.type != 'incipient': continue
            v = pd.to_numeric(pd.read_csv(leakdir / f'Scenario-{k}/Leak_{r.link}_demand.csv').iloc[:, 1], errors='coerce').values
            n = v.reshape(-1, 2).mean(1).reshape(-1, 24)[:, ns:ns + 2].mean(1)
            d0 = int((r.start - s.index[0]) / pd.Timedelta(days=1)) + 1; d1 = int((r.end - s.index[0]) / pd.Timedelta(days=1))
            act = n[d0:d1]
            if len(act) < 7 or act.max() <= 0: continue
            fluct.append((np.abs(np.diff(act)) > 0.5 * act.max()).sum() / len(act) * 7 >= 1)
            zero_share.append(float((act <= 0).mean())); any_zero.append(bool((act <= 0).any()))
    # frozen no-leak warnings by exact calendar date of the warning night
    if name == 'development_500set':
        ev = pd.read_csv(HERE / 'leakdb-dev/dev-warnings.csv'); ev = ev[ev.outcome == 'false_alert']
        d0 = dict(zip(A.scenario, pd.to_datetime(A.day0)))
        dates = [d0[k].normalize() + pd.Timedelta(days=int(d)) for k, d in zip(ev.scenario, ev.day)]
    else:
        ev = pd.read_csv(run / 'warnings-scored-frozen.csv'); ev = ev[ev.outcome == 'false_alert']
        dates = [pd.Timestamp(t).normalize() for t in ev.issue]
    months = pd.Series([d.month for d in dates])
    out[name] = {
        'final_dataset_timestamp_example': str(final_ts),
        'share_of_flowing_leaks_whose_last_flow_precedes_the_final_dataset_timestamp': round(float(np.mean(stop)), 3),
        'frozen_no_leak_warnings_by_calendar_month': {int(m): int(c) for m, c in months.value_counts().sort_index().items()},
        'share_in_feb_jun_jul_exact_calendar': round(float(months.isin([2, 6, 7]).mean()), 3),
        'gradual_leaks_with_at_least_weekly_large_night_to_night_change': round(float(np.mean(fluct)), 3),
        'gradual_leaks_with_any_active_night_at_exactly_zero_leak_flow': round(float(np.mean(any_zero)), 3),
        'gradual_leaks_median_share_of_active_nights_at_zero': round(float(np.median(zero_share)), 3),
        'gradual_leaks_counted': len(fluct),
        'calendar_note': ('timestamps in the files (2017)' if name == 'development_500set'
                          else 'NOMINAL calendar: files carry a step counter; dates = 2017-01-01 + position')}
(HERE / 'reporting-corrections-2026-10-11.json').write_text(json.dumps(out, indent=2) + '\n'); print(json.dumps(out, indent=1))
