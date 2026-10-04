"""Before/after chart for the weekend-baseline repair. Reads readings and saved results."""
from pathlib import Path
import sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

OUT = Path(__file__).resolve().parent; ROOT = OUT.parents[1]
sys.path.insert(0, str(ROOT / 'analysis/scorer'))
from leak_scorer import Rules, find_alerts  # noqa: E402

fl = pd.read_csv(ROOT / 'data/l-town/readings/2018_SCADA_Flows.csv', sep=';', decimal=',',
                 parse_dates=['Timestamp']).set_index('Timestamp').resample('h').mean()
m = fl.p227 + fl.p235 - fl.PUMP_1
G = {'old': (('2018-01-08', '2018-01-14 23:00'), lambda ix: np.where(ix.dayofweek >= 5, 'W', 'D')),
     'new': (('2018-01-01', '2018-01-14 23:00'),
             lambda ix: np.where(ix.dayofweek == 5, 'Sat', np.where(ix.dayofweek == 4, 'Fri', 'ST')))}
def resid(mode):
    (a, b), g = G[mode]; f = m.to_frame('v'); f['g'] = g(f.index); f['h'] = f.index.hour
    p = f.loc[a:b].groupby(['g', 'h'])['v'].median()
    return f.v - pd.Series([p.loc[(x, y)] for x, y in zip(f.g, f.h)], index=f.index)

W = slice('2018-01-15', '2018-12-31 23:00')
share, open_ = {}, {}
for mode in ('old', 'new'):
    r = resid(mode); st = (r.rolling(6).mean() - r.shift(6).rolling(24).mean()).loc[W]
    at11 = st[st.index.hour == 11]
    share[mode] = [(at11[at11.index.dayofweek == d] >= 9.10).mean() * 100 for d in range(7)]
    o = pd.Series(False, index=r.loc[W].index)
    for e in find_alerts(r.loc[W] > 10, 6, Rules(gap_tolerance_hours=0)):
        o.loc[e.issuable_at:e.end] = True
    open_[mode] = o
leaks = pd.read_csv(ROOT / 'analysis/scorer/main-zone-leaks-A_reference_inherited.csv', parse_dates=['start'])

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                     'axes.spines.top': False, 'axes.spines.right': False})
fig = plt.figure(figsize=(14, 7.6))
gs = fig.add_gridspec(2, 2, width_ratios=[1, 2.1], height_ratios=[1, 1])
fig.subplots_adjust(left=.06, right=.985, top=.775, bottom=.15, wspace=.22, hspace=.55)
fig.suptitle('Repairing the weekend baseline: the Sunday artefact goes, and so do some "detections"',
             x=.06, y=.965, ha='left', fontsize=17, weight='bold')
fig.text(.06, .905, 'L-Town 2018, main zone, exploratory. Old baseline: one Saturday + one Sunday pooled. '
         'New: Sun–Thu / Fri / Sat from 1–14 January.', color='#4b5563')
fig.text(.06, .865, 'Warning rules and scorer unchanged. These leaks were examined before; 2019 not used.',
         fontsize=10, color='#4b5563')

ax = fig.add_subplot(gs[:, 0])
days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']; x = np.arange(7)
ax.bar(x - .2, share['old'], .4, color='#9ca3af', label='old baseline')
ax.bar(x + .2, share['new'], .4, color='#146aab', label='new baseline')
ax.set_xticks(x); ax.set_xticklabels(days)
ax.set_ylabel('% of 11:00 hours with flow step ≥ 9.10 m³/h')
ax.set_title('1. Apparent sudden rise at 11:00,\n    by day of week', loc='left', fontsize=12, pad=9)
ax.text(6 - .2, share['old'][6] + 2, f"{share['old'][6]:.0f}%", ha='center', fontsize=10, weight='bold', color='#4b5563')
ax.text(6 + .2, share['new'][6] + 2, f"{share['new'][6]:.0f}%", ha='center', fontsize=10, weight='bold', color='#146aab')
ax.legend(frameon=False, fontsize=9.5, loc='upper left'); ax.grid(axis='y', alpha=.18); ax.set_ylim(0, 110)

for row, mode, colour, label in [(0, 'old', '#9ca3af', 'old baseline: 129 alert runs, longest 646 h'),
                                 (1, 'new', '#146aab', 'new baseline: 42 alert runs, one lasting 5,826 h')]:
    a = fig.add_subplot(gs[row, 1]); o = open_[mode]
    a.fill_between(o.index, 0, o.astype(int), step='post', color=colour, alpha=.55, linewidth=0)
    for t, kind in zip(leaks.start, leaks.type):
        a.axvline(t, color='#93431b', linewidth=1.6 if kind == 'abrupt' else .9,
                  linestyle='-' if kind == 'abrupt' else ':', alpha=.9)
    a.set_yticks([]); a.set_ylim(0, 1.05)
    a.set_title(f'{2 + row}. When a level alert was open — {label}', loc='left', fontsize=11.5, pad=6)
    a.xaxis.set_major_locator(mdates.MonthLocator()); a.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    a.set_xlim(o.index[0], o.index[-1])
fig.text(.385, .095, 'red lines: labelled leak onsets (solid = abrupt, dotted = gradual) — added afterwards for '
         'evaluation only', fontsize=9.5, color='#93431b')
fig.text(.06, .052, 'A leak can only be credited to an alert that STARTS after it. The old weekly Saturday dip kept '
         'restarting alerts; the new baseline leaves one open almost all year,', fontsize=10, color='#4b5563')
fig.text(.06, .018, 'so credited leaks fall from 9 to 3 — not because detection got worse, but because the '
         'artefact had been creating fresh starts.', fontsize=10, color='#4b5563')
fig.savefig(OUT / 'before-after.png', dpi=170, facecolor='white')
print('saved')
