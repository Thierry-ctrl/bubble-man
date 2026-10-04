"""Chart for the pressure study. Reads saved results and readings; changes nothing."""
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent; ROOT = OUT.parents[1]
t = pd.read_csv(OUT / 'episodes.csv', parse_dates=['reference_hour'])
ordinary, cases = t[t.label == 'no labelled new leak'], t[t.label == 'new abrupt leak']

pr = pd.read_csv(ROOT / 'data/l-town/readings/2018_SCADA_Pressures.csv', sep=';', decimal=',',
                 parse_dates=['Timestamp']).set_index('Timestamp').resample('h').mean()
z = pd.read_csv(ROOT / 'data/l-town/pressure-sensor-zones.csv').set_index('sensor').zone
main = list(z[z == 'main'].index)
def step(s):
    f = s.to_frame('v'); f['we'] = f.index.dayofweek >= 5; f['hr'] = f.index.hour
    pf = f.loc['2018-01-08':'2018-01-14'].groupby(['we', 'hr'])['v'].median()
    r = f.v - pd.Series([pf.loc[(w, h)] for w, h in zip(f.we, f.hr)], index=f.index)
    return r.rolling(6).mean() - r.shift(6).rolling(24).mean()
steps = pd.DataFrame({s: step(pr[s]) for s in main})
before = steps.loc['2018-03-04 11:00'].sort_values().values
after = steps.loc['2018-03-05 21:00'].sort_values().values

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                     'axes.spines.top': False, 'axes.spines.right': False})
fig, (left, right) = plt.subplots(1, 2, figsize=(14, 6.3), gridspec_kw={'width_ratios': [1, 1.25]})
fig.subplots_adjust(left=.065, right=.985, top=.745, bottom=.2, wspace=.24)
fig.suptitle('When flow rises, does pressure say whether a new leak started?', x=.065, y=.965,
             ha='left', fontsize=18, weight='bold')
fig.text(.065, .893, 'L-Town 2018, 30 main-zone pressure sensors. Measures computed from readings '
         'alone; leak labels applied afterwards.', color='#4b5563')
fig.text(.065, .851, 'Pressure step = recent 6 h minus the 24 h before, against a January baseline — '
         'the same windows as the flow step.', fontsize=10, color='#4b5563')

x = np.arange(1, len(main) + 1)
left.bar(x - .2, before, width=.4, color='#9ca3af', label='4 Mar 11:00 — rise BEFORE onset (no labelled new leak)')
left.bar(x + .2, after, width=.4, color='#93431b', label='5 Mar 21:00 — rise AFTER p673 began')
left.axhline(0, color='#6b7280', linewidth=.9)
left.axhline(-.5, color='#6b7280', linewidth=.8, linestyle=':')
left.text(len(main) + .4, -.47, '−0.5 m', fontsize=8.5, color='#6b7280', ha='right', va='bottom')
left.set_title('1. p673: two flow rises of the same size (31.6 vs 31.9 m³/h)\n'
               '    — pressure response at each sensor, most negative first', loc='left', fontsize=11.5, pad=9)
left.set_xlabel('the 30 main-zone sensors, sorted (order differs between the two bars)')
left.set_ylabel('pressure step (m)')
left.legend(frameon=False, fontsize=9, loc='center right', bbox_to_anchor=(1.0, .28))
left.grid(axis='y', alpha=.18)
left.text(2.0, -1.45, '14 of 30 sensors fall\nmore than 0.5 m', color='#93431b', fontsize=9.5, weight='bold')
left.text(16, -.80, 'grey bars, before onset:\nnone fall more than 0.5 m', color='#4b5563', fontsize=9.5)

pump = ordinary.pump_step > 10
right.scatter(ordinary.dQ[~pump], ordinary.C[~pump], s=22, color='#9ca3af', alpha=.7,
              label=f'ordinary rise (n={int((~pump).sum())})')
right.scatter(ordinary.dQ[pump], ordinary.C[pump], s=40, facecolor='none', edgecolor='#be720c',
              linewidth=1.4, label=f'ordinary rise with pump step > +10 m³/h (n={int(pump.sum())})')
right.scatter(cases.dQ, cases.C, s=85, color='#93431b', zorder=5, label='rise just after an abrupt leak began')
for r in cases.itertuples():
    right.annotate(r.leak, (r.dQ, r.C), xytext=(6, 4), textcoords='offset points', fontsize=9.5,
                   color='#93431b', weight='bold')
right.axhline(np.percentile(ordinary.C, 90), color='#374151', linewidth=1, linestyle='--')
right.text(right.get_xlim()[1] * .99 if False else ordinary.dQ.max(), np.percentile(ordinary.C, 90) + .0008,
           '90th pct of ordinary rises', fontsize=8.5, color='#374151', ha='right')
right.set_title('2. All flow rises in 2018: is the pressure drop concentrated?\n'
                '    C = how much more the worst sensor fell than the typical one, per m³/h',
                loc='left', fontsize=11.5, pad=9)
right.set_xlabel('flow rise ΔQ (m³/h)')
right.set_ylabel('concentration C (m per m³/h)')
right.legend(frameon=False, fontsize=8.8, loc='upper right', bbox_to_anchor=(1.0, .82))
right.grid(alpha=.15)

fig.text(.065, .098, 'Only p673 stands clearly apart — and ordinary rises with heavy pump activity reach '
         'almost as high (max 0.033 vs 0.034). The other five look like ordinary rises.',
         fontsize=10, color='#4b5563')
fig.text(.065, .058, 'A concentrated pressure drop says the drop is uneven. It does not locate a pipe. '
         'Three or four leaks were already running at every case.', fontsize=10, color='#4b5563')
fig.text(.065, .018, 'Source: BattLeDIM, Vrachimis et al.  https://zenodo.org/records/4017659  CC BY 4.0. '
         'Simulated data. 2019 not used.', fontsize=9)
fig.savefig(OUT / 'pressure-evidence.png', dpi=170, facecolor='white')
print('saved')
