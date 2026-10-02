"""One abrupt leak, traced from onset to warning. Reads only; changes nothing.

Experiment A settings, unchanged: signal p227+p235-PUMP_1 (hourly), baseline profile
from 8-14 January, threshold 10 m3/h, persistence 6 hours, reporting lag 1 hour.

Colour convention, as used throughout the project:
    blue   #146aab  observed flow
    orange #be720c  expected flow (our baseline)
    red    #93431b  known leak information (the answer sheet)
"""
import math
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
AREA = math.pi * 64
THRESHOLD, PERSISTENCE = 10, 6

flows = pd.read_csv(ROOT / 'data/l-town/readings/2018_SCADA_Flows.csv', sep=';', decimal=',',
                    parse_dates=['Timestamp']).set_index('Timestamp')
hourly = flows.resample('h').mean()
hourly['main_out'] = hourly.p227 + hourly.p235 - hourly.PUMP_1
hourly['weekend'] = hourly.index.dayofweek >= 5
hourly['hour'] = hourly.index.hour
profile = hourly.loc['2018-01-08':'2018-01-14'].groupby(['weekend', 'hour'])['main_out'].median()
index = hourly.loc['2018-01-15':'2018-12-31 23:00'].index
expected = pd.Series([profile.loc[(w, h)] for w, h in
                      zip(hourly.loc[index].weekend, hourly.loc[index].hour)], index=index)
difference = hourly.loc[index, 'main_out'] - expected

VIEW = slice('2018-03-02', '2018-03-12 23:00')
obs, exp, diff = hourly.loc[VIEW, 'main_out'], expected.loc[VIEW], difference.loc[VIEW]

ONSET = pd.Timestamp('2018-03-05 15:45')
RUN26_START, RUN26_END = pd.Timestamp('2018-03-04 05:00'), pd.Timestamp('2018-03-09 06:00')
BREAK = pd.Timestamp('2018-03-09 07:00')
RUN27_START = pd.Timestamp('2018-03-09 08:00')
SATISFIED = pd.Timestamp('2018-03-09 13:00')
ISSUABLE = pd.Timestamp('2018-03-09 14:00')

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                     'axes.spines.top': False, 'axes.spines.right': False})
fig, (top, bottom) = plt.subplots(2, 1, figsize=(13, 8.6), sharex=True,
                                  gridspec_kw={'height_ratios': [1.15, 1]})
fig.subplots_adjust(left=.075, right=.985, top=.785, bottom=.175, hspace=.32)
fig.suptitle('Why the warning for leak p673 arrived 94 hours late', x=.075, y=.975,
             ha='left', fontsize=20, weight='bold')
fig.text(.075, .925, 'L-Town simulation. Main-zone outflow = p227 + p235 − PUMP_1, hourly. '
         'Experiment A, unchanged.', color='#4b5563')
fig.text(.075, .888, 'Expected pattern learned from 8–14 January. Threshold 10 m³/h for 6 '
         'consecutive hours, then 1 hour to report.', fontsize=10, color='#4b5563')
fig.text(.075, .848, 'The leak was visible at once. The delay came from an alert that was '
         'already running before it started.', fontsize=10.5, color='#93431b', weight='bold')

top.plot(obs.index, obs, color='#146aab', linewidth=1.8, label='Observed flow', zorder=3)
top.plot(exp.index, exp, color='#be720c', linewidth=1.8, linestyle='--',
         label='Expected flow (baseline)', zorder=2)
top.set_ylabel('Flow (m³/hour)')
top.set_title('1. What the meter saw, against what the baseline expected', loc='left',
              fontsize=12.5, pad=10)
top.legend(loc='lower center', frameon=True, framealpha=.92, edgecolor='none',
           ncol=2, fontsize=10, bbox_to_anchor=(.5, -.02))
top.grid(axis='y', alpha=.18)

bottom.axhspan(0, THRESHOLD, color='#9ca3af', alpha=.10)
bottom.plot(diff.index, diff, color='#146aab', linewidth=1.6, zorder=3)
bottom.fill_between(diff.index, diff, THRESHOLD, where=diff > THRESHOLD,
                    color='#146aab', alpha=.13, zorder=2)
bottom.axhline(THRESHOLD, color='#374151', linewidth=1.4, linestyle='-', zorder=4)
bottom.text(pd.Timestamp('2018-03-02 02:00'), THRESHOLD + 2.5,
            f'threshold {THRESHOLD} m³/h', fontsize=9.5, color='#374151')
bottom.axhline(0, color='#9ca3af', linewidth=.9)
bottom.set_ylabel('Observed − expected\n(m³/hour)')
bottom.set_title('2. The difference, and why the first long run could not be credited',
                 loc='left', fontsize=12.5, pad=10)
bottom.grid(axis='y', alpha=.18)

# the 122-hour run that began before the leak
bottom.annotate('', xy=(RUN26_START, -46), xytext=(RUN26_END, -46),
                arrowprops=dict(arrowstyle='<->', color='#6b7280', linewidth=1.5))
bottom.text(RUN26_START + (RUN26_END - RUN26_START) / 2, -41,
            'run #26: 122 h above threshold, began 34 h BEFORE the leak — not creditable',
            ha='center', fontsize=9.5, color='#6b7280',
            bbox=dict(facecolor='white', edgecolor='none', alpha=.92, pad=2))
bottom.annotate('', xy=(RUN27_START, -46), xytext=(pd.Timestamp('2018-03-12 23:00'), -46),
                arrowprops=dict(arrowstyle='<->', color='#146aab', linewidth=1.5))
bottom.text(pd.Timestamp('2018-03-11 02:00'), -41, 'run #27: creditable',
            ha='center', fontsize=9.5, color='#146aab')

for axis in (top, bottom):
    axis.axvline(ONSET, color='#93431b', linestyle=':', linewidth=1.8, zorder=5)
    axis.axvline(ISSUABLE, color='#146aab', linestyle='-.', linewidth=1.6, zorder=5)
top.text(ONSET - pd.Timedelta(hours=3), top.get_ylim()[1] * .99,
         'leak p673 begins\n5 Mar 15:45\n28.4 m³/h', color='#93431b', fontsize=10,
         va='top', ha='right', weight='bold',
         bbox=dict(facecolor='white', edgecolor='none', alpha=.9, pad=2))
top.text(ISSUABLE + pd.Timedelta(hours=3), top.get_ylim()[1] * .99,
         'warning issuable\n9 Mar 14:00', color='#146aab', fontsize=10, va='top', weight='bold',
         bbox=dict(facecolor='white', edgecolor='none', alpha=.9, pad=2))
bottom.plot([BREAK], [diff.loc[BREAK]], marker='v', markersize=11, color='#93431b', zorder=7)
bottom.annotate('one hour below threshold (+6.97)\nbreaks the run',
                xy=(BREAK, diff.loc[BREAK] - 1.5),
                xytext=(pd.Timestamp('2018-03-07 18:00'), -24),
                ha='center', fontsize=9.5, color='#93431b', zorder=7,
                bbox=dict(facecolor='white', edgecolor='none', alpha=.92, pad=2),
                arrowprops=dict(arrowstyle='->', color='#93431b', linewidth=1.3))
bottom.set_ylim(-52, max(diff) * 1.12)

bottom.xaxis.set_major_locator(mdates.DayLocator())
bottom.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
bottom.set_xlim(pd.Timestamp('2018-03-02'), pd.Timestamp('2018-03-12 23:00'))
bottom.set_xlabel('Date (dataset timestamps)')

fig.text(.075, .093, 'The leak raised the difference immediately: +32 m³/h at 15:00, '
         '+52 at 16:00. It was never invisible.', fontsize=10, color='#4b5563')
fig.text(.075, .056, 'A timing match is an association only. This signal names no pipe, so it '
         'cannot show which leak caused the warning.', fontsize=10, color='#4b5563')
fig.text(.075, .019, 'Source: BattLeDIM, Vrachimis et al.  https://zenodo.org/records/4017659  '
         'CC BY 4.0. Simulated data.', fontsize=9)
fig.savefig(OUT / 'p673-walkthrough.png', dpi=170, facecolor='white')
print('saved', OUT / 'p673-walkthrough.png')
