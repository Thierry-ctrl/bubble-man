"""Why does the repaired-baseline level warning stay open for 5,826 hours? 2018 only.

RETROSPECTIVE EXPLANATION. Labelled leak flow is used here to explain the excess, and
must never be an input to a live warning. No detector is built or tuned; the scorer is
not touched; 2019 is not read.

Accounting (WATER-ACCOUNTING.md): main-zone outflow p227 + p235 - PUMP_1 equals
main-zone demand plus main-zone leakage. The new baseline is learned on 1-14 January,
when no labelled main-zone leak produced flow. So, hour by hour:

    excess    = observed - expected
    leak part = known simulated flow of the 12 labelled main-zone leaks
    remainder = excess - leak part

The remainder is NON-LABELLED-LEAK FLOW above the January expectation. It includes
changing customer demand, but also anything else the simulator does that is not a
labelled leak (e.g. pressure-dependent effects of leaks on delivered demand, model
background losses) and any error in the January baseline. It is not, by itself, proof of
seasonal customer demand.
"""
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'analysis/scorer'))
from leak_scorer import Rules, find_alerts  # noqa: E402  (read-only)

W = ('2018-01-15', '2018-12-31 23:00')
THRESHOLD, PERSISTENCE = 10, 6

def read(path):
    return pd.read_csv(ROOT / path, sep=';', decimal=',', parse_dates=['Timestamp']).set_index('Timestamp')

flows = read('data/l-town/readings/2018_SCADA_Flows.csv').resample('h').mean()
observed = flows.p227 + flows.p235 - flows.PUMP_1
truth = read('data/l-town/reference/2018_Leakages.csv')
zones = dict(pd.read_csv(ROOT / 'analysis/scorer/leak-zones-from-network-map.csv')[['link', 'zone']].values)
main_links = [c for c in truth.columns if zones.get(c) == 'main']
assert len(main_links) == 12, main_links
leak = truth[main_links].sum(axis=1).resample('h').mean()      # same hourly intervals as flow

GROUPS = {
    'MonFri|SatSun': lambda ix: np.where(ix.dayofweek >= 5, 'SatSun', 'MonFri'),
    'SunThu|Fri|Sat': lambda ix: np.where(ix.dayofweek == 5, 'Sat', np.where(ix.dayofweek == 4, 'Fri', 'SunThu')),
}
TRAINING = {'1 week (8-14 Jan)': ('2018-01-08', '2018-01-14 23:00'),
            '2 weeks (1-14 Jan)': ('2018-01-01', '2018-01-14 23:00')}

def expected(group, train):
    frame = observed.to_frame('v'); frame['g'] = GROUPS[group](frame.index); frame['h'] = frame.index.hour
    profile = frame.loc[train[0]:train[1]].groupby(['g', 'h'])['v'].median()
    return pd.Series([profile.loc[(g, h)] for g, h in zip(frame.g, frame.h)], index=frame.index)

def alert_summary(diff):
    runs = find_alerts(diff > THRESHOLD, PERSISTENCE, Rules(gap_tolerance_hours=0))
    open_ = pd.Series(False, index=diff.index)
    for e in runs:
        open_.loc[e.issuable_at:e.end] = True
    longest = max(runs, key=lambda e: e.hours) if runs else None
    return {'runs': len(runs), 'share_open': round(float(open_.mean()), 4),
            'longest_h': longest.hours if longest else 0,
            'longest_from': str(longest.run_start) if longest else None,
            'longest_to': str(longest.end) if longest else None}, open_

# ---------------- 1. the repaired baseline, decomposed ------------------------
exp_new = expected('SunThu|Fri|Sat', TRAINING['2 weeks (1-14 Jan)'])
excess = (observed - exp_new).loc[W[0]:W[1]]
leak_w = leak.loc[W[0]:W[1]]
remainder = excess - leak_w

actual, open_actual = alert_summary(excess)
no_leak, open_no_leak = alert_summary(remainder)          # diagnostic: subtract known leak flow
leak_only, open_leak_only = alert_summary(leak_w)         # diagnostic: leak flow alone vs the rule

weekly = pd.DataFrame({'excess': excess, 'leak': leak_w, 'remainder': remainder,
                       'open_actual': open_actual, 'open_without_leak': open_no_leak}).resample('W-SUN').mean()
weekly.to_csv(OUT / 'weekly-decomposition.csv', index_label='week_ending')

long_from, long_to = pd.Timestamp(actual['longest_from']), pd.Timestamp(actual['longest_to'])
during = pd.DataFrame({'excess': excess, 'leak': leak_w, 'remainder': remainder}).loc[long_from:long_to]
before = pd.DataFrame({'excess': excess, 'leak': leak_w, 'remainder': remainder}).loc[W[0]:long_from - pd.Timedelta(hours=1)]
quiet = remainder.loc['2018-01-15':'2018-01-23 22:00']   # no labelled main-zone leak flow here

hours_over = lambda s: round(float((s > THRESHOLD).mean()), 4)
monthly = pd.DataFrame({'excess': excess, 'leak': leak_w, 'remainder': remainder}).resample('MS').mean().round(2)

result = {
    'definitions': 'excess = observed - expected (new baseline); leak = 12 labelled main-zone leaks; remainder = excess - leak',
    'actual_alert': actual,
    'diagnostic_without_known_leak_flow': no_leak,
    'diagnostic_known_leak_flow_alone': leak_only,
    'longest_run_window': [str(long_from), str(long_to)],
    'during_longest_run_mean': during.mean().round(2).to_dict(),
    'before_longest_run_mean': before.mean().round(2).to_dict(),
    'during_longest_run_share_of_excess_from_leak': round(float(during.leak.mean() / during.excess.mean()), 3),
    'hours_over_threshold_during_longest_run': {'excess': hours_over(during.excess),
                                                'leak_alone': hours_over(during.leak),
                                                'remainder_alone': hours_over(during.remainder)},
    'no_labelled_leak_window_15_23_Jan_remainder': {'mean': round(float(quiet.mean()), 2),
                                                    'p95': round(float(np.percentile(quiet, 95)), 2)},
    'monthly_mean_m3_per_hour': {str(k.date()): v for k, v in monthly.to_dict('index').items()},
}

# ---------------- 2. which part of the repair did what? ------------------------
variants = []
for group in GROUPS:
    for tname, train in TRAINING.items():
        e = (observed - expected(group, train))
        diff = e.loc[W[0]:W[1]]
        step = (e.rolling(6).mean() - e.shift(6).rolling(24).mean()).loc[W[0]:W[1]]
        sun11 = step[(step.index.dayofweek == 6) & (step.index.hour == 11)]
        mon11 = step[(step.index.dayofweek == 0) & (step.index.hour == 11)]
        summary, _ = alert_summary(diff)
        quiet_bias = float((e.loc['2018-01-15':'2018-01-23 22:00']).mean())
        variants.append({'grouping': group, 'training': tname,
                         'note': 'DIAGNOSTIC ONLY - not deployable' if (group == 'SunThu|Fri|Sat' and tname.startswith('1'))
                         else ('old (Experiment A)' if group == 'MonFri|SatSun' and tname.startswith('1')
                               else ('new (frozen)' if group == 'SunThu|Fri|Sat' else 'diagnostic')),
                         'sunday_11_cross_9_10': round(float((sun11 >= 9.10).mean()), 3),
                         'monday_11_cross_9_10': round(float((mon11 >= 9.10).mean()), 3),
                         'mean_excess_whole_window': round(float(diff.mean()), 2),
                         'mean_excess_15_23_Jan': round(quiet_bias, 2), **summary})
result['baseline_variants'] = variants
(OUT / 'decomposition.json').write_text(json.dumps(result, indent=2) + '\n')

print(f"ACTUAL (new baseline): {actual}")
print(f"  without known leak flow: {no_leak}")
print(f"  known leak flow alone:   {leak_only}")
print(f"\nlongest run {long_from} -> {long_to}")
print(f"  mean before it  (m3/h): {before.mean().round(2).to_dict()}")
print(f"  mean during it  (m3/h): {during.mean().round(2).to_dict()}")
print(f"  share of excess from labelled leak during it: {result['during_longest_run_share_of_excess_from_leak']:.0%}")
print(f"  hours over 10 during it: {result['hours_over_threshold_during_longest_run']}")
print(f"\n15-23 Jan (no labelled main-zone leak flow): remainder mean {quiet.mean():.2f}, 95th {np.percentile(quiet,95):.2f}")
print("\nmonthly means (m3/h):"); print(monthly.to_string())
print("\nBASELINE VARIANTS")
for v in variants:
    print(f"  {v['grouping']:15s} {v['training']:18s} Sun11 {v['sunday_11_cross_9_10']:5.0%} Mon11 {v['monday_11_cross_9_10']:5.0%} "
          f"| runs {v['runs']:3d} open {v['share_open']:6.1%} longest {v['longest_h']:5d} h | mean excess {v['mean_excess_whole_window']:6.2f}, 15-23 Jan {v['mean_excess_15_23_Jan']:6.2f}  [{v['note']}]")
