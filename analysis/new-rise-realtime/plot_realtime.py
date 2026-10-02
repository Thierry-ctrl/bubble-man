"""Chart: does the real-time rule beat random placement on the same hours?"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]; OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'analysis/scorer'))
from leak_scorer import Rules, score  # noqa: E402

data = pd.read_csv(OUT / 'realtime-warnings.csv', parse_dates=['Timestamp']).set_index('Timestamp')
report = json.loads((OUT / 'realtime-results.json').read_text())
warn, open_ = data.new_rise_warning.astype(bool), data.alert_open.astype(bool)
leaks = pd.read_csv(ROOT / 'analysis/scorer/main-zone-leaks-A_reference_inherited.csv',
                    parse_dates=['start', 'end'])[['link', 'start', 'end', 'type', 'zone']]
leaks['diameter_m'], leaks['peak'], leaks['configured_start'] = 0.02, leaks.start, leaks.start
RULES = Rules(gap_tolerance_hours=0, reporting_lag_hours=1.0, max_delay_hours=168)

candidates = np.array([i for i, f in enumerate(open_) if f])
rng = np.random.default_rng(20261003); n = int(warn.sum())
total, abrupt, delay = [], [], []
for _ in range(300):
    picked = []
    for position in rng.permutation(candidates):
        if all(abs(position - p) >= 24 for p in picked):
            picked.append(position)
            if len(picked) == n:
                break
    series = pd.Series(False, index=data.index); series.iloc[picked] = True
    outcome = score(series, 1, leaks, RULES)
    total.append(outcome['overall']['credited']); abrupt.append(outcome['abrupt']['credited'])
    if outcome['overall']['median_delay_hours'] is not None:
        delay.append(outcome['overall']['median_delay_hours'])

real = report['new_rule']
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                     'axes.spines.top': False, 'axes.spines.right': False})
fig, axes = plt.subplots(1, 3, figsize=(14.5, 5.6))
fig.subplots_adjust(left=.055, right=.985, top=.73, bottom=.21, wspace=.28)
fig.suptitle('Does the real-time new-rise rule beat randomly-timed warnings?',
             x=.055, y=.965, ha='left', fontsize=18, weight='bold')
fig.text(.055, .888, '2018 DEVELOPMENT TEST. Rule frozen before scoring. Random warnings: same count, '
         'same 24 h spacing,', color='#4b5563')
fig.text(.055, .845, 'placed only in the 6,589 hours when a level alert was open — the only hours the '
         'real rule was allowed to fire.', color='#4b5563')

for axis, values, real_value, title, note in [
        (axes[0], total, real['leaks_credited'], 'All 12 leaks credited', 'random 95th = 11.0'),
        (axes[1], abrupt, real['abrupt_credited'], 'Abrupt leaks credited (the target)', 'random 95th = 6.0'),
        (axes[2], delay, real['median_delay_hours'], 'Median delay (hours)', 'lower is better')]:
    axis.hist(values, bins=18, color='#9ca3af', alpha=.8)
    axis.axvline(real_value, color='#146aab', linewidth=2.4, zorder=5)
    axis.text(real_value, axis.get_ylim()[1] * .93, f'  real\n  {real_value}', color='#146aab',
              fontsize=10, weight='bold', va='top')
    axis.set_title(title, loc='left', fontsize=12, pad=9)
    axis.set_xlabel(note, fontsize=9.5, color='#6b7280')
    axis.set_ylabel('random runs')
    axis.grid(axis='y', alpha=.18)
axes[2].axvline(report['experiment_a']['median_delay_hours'], color='#be720c',
                linewidth=2.2, linestyle='--', zorder=5)
axes[2].set_xlim(right=report['experiment_a']['median_delay_hours'] + 4)
axes[2].text(report['experiment_a']['median_delay_hours'] - 1.5, axes[2].get_ylim()[1] * .62,
             'Experiment A\n55.75  ', color='#be720c', fontsize=9.5, weight='bold',
             va='top', ha='right')

fig.text(.055, .105, 'On abrupt leaks — what the rule was built for — it is indistinguishable from chance: '
         '6 of 6, exactly as random placement achieves.', fontsize=10, color='#93431b', weight='bold')
fig.text(.055, .062, 'It credits every leak and halves the delay, but needs 4.69 warnings per week of open '
         'alert to do it: about 4.7 chances per leak by density alone.', fontsize=10, color='#4b5563')
fig.text(.055, .019, 'Simulated data. Timing matches are associations; this signal names no pipe and '
         'several leaks overlap every window.', fontsize=9)
fig.savefig(OUT / 'realtime-vs-random.png', dpi=170, facecolor='white')
(OUT / 'random-distributions.json').write_text(json.dumps(
    {'total_credited': total, 'abrupt_credited': abrupt, 'median_delay_hours': delay}, indent=2) + '\n')
print('saved; random abrupt distinct values:', sorted(set(abrupt)))
