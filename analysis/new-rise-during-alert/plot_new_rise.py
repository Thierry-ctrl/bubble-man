"""Chart for the new-rise test. Reads the saved series; changes nothing."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
CASE_WINDOW = 12

data = pd.read_csv(OUT / 'step-series.csv', parse_dates=['Timestamp']).set_index('Timestamp')
report = json.loads((OUT / 'new-rise-results.json').read_text())
step, alert_open = data.step_m3_per_hour, data.alert_open.astype(bool)
leaks = pd.read_csv(ROOT / 'analysis/scorer/main-zone-leaks-A_reference_inherited.csv',
                    parse_dates=['start'])

near = pd.Series(False, index=step.index)
for onset in leaks.start:
    near.loc[onset - pd.Timedelta(hours=72):onset + pd.Timedelta(hours=72)] = True
control_mask = alert_open & ~near
blocks = step.rolling(CASE_WINDOW).max()[
    (control_mask.rolling(CASE_WINDOW).min().astype(float) == 1).fillna(False)]

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                     'axes.spines.top': False, 'axes.spines.right': False})
fig, (left, right) = plt.subplots(1, 2, figsize=(13.5, 6.4), gridspec_kw={'width_ratios': [1.5, 1]})
fig.subplots_adjust(left=.07, right=.985, top=.755, bottom=.185, wspace=.26)
fig.suptitle('Can a measure of CHANGE see a new leak while a level alert is already open?',
             x=.07, y=.965, ha='left', fontsize=18, weight='bold')
fig.text(.07, .893, 'L-Town simulation, 2018. Step = mean difference over the last 6 hours '
         'minus the 24 hours before them.', color='#4b5563')
fig.text(.07, .848, 'Strictly backward-looking. Leak labels used only to choose cases and '
         'exclude control hours, never as input.', fontsize=10, color='#4b5563')

VIEW = slice('2018-03-02', '2018-03-12 23:00')
view, open_view = step.loc[VIEW], alert_open.loc[VIEW]
ONSET = pd.Timestamp('2018-03-05 15:45')
left.fill_between(view.index, -14, 42, where=open_view, color='#9ca3af', alpha=.22,
                  step='mid', label='level alert already open', zorder=1)
left.plot(view.index, view, color='#146aab', linewidth=1.7, zorder=3, label='step measure')
left.axhline(0, color='#9ca3af', linewidth=.9)
left.axvline(ONSET, color='#93431b', linestyle=':', linewidth=1.8, zorder=4)
peak_at = view.loc[ONSET:ONSET + pd.Timedelta(hours=CASE_WINDOW)].idxmax()
left.plot([peak_at], [view.loc[peak_at]], marker='o', markersize=9, color='#93431b', zorder=5)
left.annotate(f'step peaks at {view.loc[peak_at]:.1f} m³/h\n5.2 h after onset',
              xy=(peak_at, view.loc[peak_at]), xytext=(pd.Timestamp('2018-03-07 06:00'), 36),
              fontsize=9.5, color='#93431b',
              bbox=dict(facecolor='white', edgecolor='none', alpha=.92, pad=2),
              arrowprops=dict(arrowstyle='->', color='#93431b', linewidth=1.3))
left.text(ONSET - pd.Timedelta(hours=3), -11.5, 'leak p673 begins\n5 Mar 15:45', ha='right',
          fontsize=9.5, color='#93431b', weight='bold')
left.set_ylim(-14, 42)
left.set_ylabel('Step (m³/hour)')
left.set_xlabel('Date (dataset timestamps)')
left.set_title('1. Around p673: the alert was open the whole time,\n    yet the step still rises',
               loc='left', fontsize=12, pad=10)
left.legend(loc='upper left', frameon=False, fontsize=9.5)
left.grid(axis='y', alpha=.18)
left.xaxis.set_major_locator(mdates.DayLocator(interval=2))
left.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
left.set_xlim(pd.Timestamp('2018-03-02'), pd.Timestamp('2018-03-12 23:00'))

right.hist(blocks, bins=55, color='#9ca3af', alpha=.75,
           label=f'control blocks (n={len(blocks)})')
colours = {'credited': '#146aab', 'missed': '#93431b'}
ordered = sorted(report['cases'], key=lambda c: c['max_step_m3_per_hour'])
top = right.get_ylim()[1]
for i, case in enumerate(ordered):
    value = case['max_step_m3_per_hour']
    colour = colours[case['scorer_outcome_experiment_A']]
    right.axvline(value, color=colour, linewidth=1.7, zorder=4)
    right.text(value, top * (.47 - .058 * i), f" {case['link']}", fontsize=9.5,
               color=colour, weight='bold', zorder=6,
               bbox=dict(facecolor='white', edgecolor='none', alpha=.95, pad=1.5))
right.set_xlabel('Step over 12 hours (m³/hour)')
right.set_ylabel('12-hour control blocks')
right.set_title('2. The six abrupt leaks against hours\n    when nothing new began',
                loc='left', fontsize=12, pad=10)
right.grid(axis='y', alpha=.18)
handles = [plt.Line2D([], [], color='#146aab', linewidth=1.7, label='leak the level rule caught'),
           plt.Line2D([], [], color='#93431b', linewidth=1.7, label='leak the level rule MISSED'),
           plt.Rectangle((0, 0), 1, 1, color='#9ca3af', alpha=.75, label=f'control blocks (n={len(blocks)})')]
right.legend(handles=handles, frameon=True, framealpha=.93, edgecolor='none',
             fontsize=9, loc='upper left')

fig.text(.07, .092, 'All six land in the top 11% of comparable control blocks — including three the level '
         'rule missed entirely. But the control tail overlaps them:', fontsize=10, color='#4b5563')
fig.text(.07, .055, 'the 95th percentile of control blocks (34.6) exceeds four of the six. A cut at the '
         'weakest case reaches 6/6 and still fires 1.27 times a week without a new leak.',
         fontsize=10, color='#4b5563')
fig.text(.07, .017, 'Source: BattLeDIM, Vrachimis et al.  https://zenodo.org/records/4017659  CC BY 4.0. '
         'Simulated data. A timing match is not proof that a particular pipe leaked.', fontsize=9)
fig.savefig(OUT / 'new-rise.png', dpi=170, facecolor='white')
print('saved', OUT / 'new-rise.png')
