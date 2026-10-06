"""Protocol 9724c60, step 6: score the committed warnings and all 51 week-shifts."""
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from common import ROOT
sys.path.insert(0, str(ROOT / 'analysis/scorer'))
from leak_scorer import Rules, score

RULES = Rules(gap_tolerance_hours=0, reporting_lag_hours=1.0, max_delay_hours=168)
warn = [pd.Timestamp(d) for d in pd.read_csv(HERE / 'warnings-2019.csv').night]       # the committed list
leaks = pd.read_csv(HERE / 'leaks-2019-scorer-list.csv', parse_dates=['start', 'end'])
leaks['diameter_m'], leaks['peak'], leaks['configured_start'] = 0.02, leaks.start, leaks.start
truth = pd.read_csv(ROOT / 'data/l-town/reference/2019_Leakages.csv', sep=';', decimal=',',
                    parse_dates=['Timestamp']).set_index('Timestamp')
eligible = leaks[leaks.status == 'eligible']; carried = list(leaks[leaks.status.str.startswith('carried')].link)

def series(nights, a, b):
    s = pd.Series(False, index=pd.date_range(a, b, freq='h'))
    for d in nights:
        t = d + pd.Timedelta(hours=3)
        if t in s.index: s.loc[t] = True
    return s

full = score(series(warn, '2019-01-01 00:00', '2019-12-31 23:00'), 1, leaks, RULES)
assert full['overall']['eligible_leaks'] == 17, full['overall']

# ---- 51 week-shifts on the 52-week domain -----------------------------------
dom = pd.date_range('2019-01-01', '2019-12-30', freq='D'); assert len(dom) == 364
pos = [dom.get_loc(d) for d in warn if d in dom]
def score_pos(p): return score(series([dom[i] for i in p], '2019-01-01 00:00', '2019-12-30 23:00'), 1, leaks, RULES)
real_dom = score_pos(pos)
rows, patterns = [], {tuple(sorted(pos))}
for k in range(1, 52):
    p = sorted((i + 7 * k) % 364 for i in pos); patterns.add(tuple(p))
    gaps = np.diff(p).tolist() + [p[0] + 364 - p[-1]]
    o = score_pos(p)
    rows.append({'k_weeks': k, 'sudden': o['abrupt']['credited'], 'gradual': o['incipient']['credited'],
                 'all': o['overall']['credited'], 'min_gap_days': int(min(gaps))})
sh = pd.DataFrame(rows)
rs, ra = real_dom['abrupt']['credited'], real_dom['overall']['credited']
p_sudden = (1 + int((sh.sudden >= rs).sum())) / 52
p_all = (1 + int((sh['all'] >= ra).sum())) / 52

# ---- workload: every warning is an investigation ----------------------------
ev = pd.DataFrame(full['events']); ev['night'] = pd.to_datetime(ev.run_start).dt.normalize()
issue = pd.to_datetime(ev.issuable_at)
main_cols = [c for c in leaks.link if c in truth.columns]
carried_flowing = [any(truth.loc[t, c] > 0 for c in carried) if t in truth.index else None for t in issue]
ev['during_carried_over_leak'] = carried_flowing
months = pd.date_range('2019-01-01', '2019-12-01', freq='MS').strftime('%b')
by_month = {m: {'warnings': int((ev.night.dt.strftime('%b') == m).sum()),
                'credited': int(((ev.night.dt.strftime('%b') == m) & (ev.outcome == 'credited')).sum())} for m in months}
credited = int((ev.outcome == 'credited').sum()); total = len(ev)
any_main = truth[main_cols].sum(axis=1).resample('h').mean().loc['2019-01-01':'2019-12-31 23:00']
exposure_no_labelled_leak = int((any_main <= 0).sum())

# ---- window composition for each credited warning (context, not cause) ------
night_flow = truth[main_cols][truth.index.hour.isin([2, 3])]
night_flow = night_flow.groupby(night_flow.index.normalize()).mean()
comp = []
for e in full['events']:
    if e['outcome'] != 'credited': continue
    d = pd.Timestamp(e['run_start']).normalize(); L = e['matched_leak']
    flows = lambda days: sum(1 for x in days if x in night_flow.index and night_flow.loc[x, L] > 0)
    latest = [d - pd.Timedelta(days=i) for i in (0, 1)]; before = [d - pd.Timedelta(days=i) for i in range(2, 9)]
    lk = next(r for r in full['leaks'] if r['link'] == L)
    comp.append({'warning_night': str(d.date()), 'leak': L, 'type': lk['type'], 'delay_h': lk['delay_hours_from_first_flow'],
                 'leak_nights_in_latest_pair': f'{flows(latest)}/2', 'leak_nights_in_7_before': f'{flows(before)}/7',
                 'other_candidates': [c for c in e['candidates'] if c != L]})

S = {'S0_noise': 'reported, not gating — see step2 (original 2018 noise stop failed and remains failed)',
     'S1_eligible_sudden': int((eligible.type == 'abrupt').sum()), 'S1_met': bool((eligible.type == 'abrupt').sum() >= 3),
     'S2_sudden_associated_full_window': full['abrupt']['credited'], 'S2_met': full['abrupt']['credited'] >= 2,
     'S3_p_sudden_domain': round(p_sudden, 4), 'S3_met': p_sudden <= 0.05,
     'S4_yield_full_window': round(credited / total, 4) if total else None, 'S4_met': (credited / total) >= 0.5 if total else False}
S['outcome'] = ('INCONCLUSIVE' if not S['S1_met'] else
                'PROMISING UNDER THE REVISED EXPLORATORY PROTOCOL' if (S['S2_met'] and S['S3_met'] and S['S4_met']) else 'FAIL')
res = {'protocol': '9724c60', 'warnings_commit': '2d0671b', 'criteria': S,
       'full_window': {k: full[k] for k in ('alert_events_total', 'outcomes', 'overall', 'abrupt', 'incipient')},
       'workload': {'total_warnings_all_investigations': total, 'credited': credited,
                    'investigations_without_an_eligible_new_leak': total - credited,
                    'yield': round(credited / total, 4) if total else None,
                    'warnings_during_a_carried_over_leak': int(sum(bool(x) for x in carried_flowing)),
                    'false_alerts': full['outcomes']['false_alert'],
                    'hours_with_no_labelled_main_zone_leak_flowing': exposure_no_labelled_leak,
                    'by_month': by_month},
       'shift_comparison': {'domain': '1 Jan - 30 Dec 2019, 364 nights', 'distinct_shifts': int(len(sh)),
                            'distinct_patterns_including_real': len(patterns),
                            'real_in_domain': {'warnings': len(pos), 'sudden': rs, 'all': ra,
                                               'gradual': real_dom['incipient']['credited']},
                            'shift_sudden_distribution': {int(k): int(v) for k, v in sh.sudden.value_counts().sort_index().items()},
                            'shift_all_distribution': {int(k): int(v) for k, v in sh['all'].value_counts().sort_index().items()},
                            'p_sudden': round(p_sudden, 4), 'p_all': round(p_all, 4),
                            'shifts_with_wrapped_gap_under_7_days': int((sh.min_gap_days < 7).sum())},
       'credited_window_composition': comp}
(HERE / 'step6-results.json').write_text(json.dumps(res, indent=2, default=str) + '\n')
pd.DataFrame(full['leaks']).to_csv(HERE / 'per-leak-2019.csv', index=False)
ev.drop(columns=['night']).to_csv(HERE / 'warnings-scored-2019.csv', index=False)
sh.to_csv(HERE / 'shifts-2019.csv', index=False)
print(json.dumps({k: res[k] for k in ('criteria', 'workload', 'shift_comparison')}, indent=2, default=str))
print("\nper leak:")
for r in full['leaks']:
    print(f"  {r['link']:5s} {r['type']:9s} {r['eligibility'][:30]:30s} {r['outcome']:10s} delay {r['delay_hours_from_first_flow']}")
print("\ncredited warnings, window composition:"); [print("  ", c) for c in comp]
