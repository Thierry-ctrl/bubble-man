"""Weekly chart: what fills the gap between observed and expected? Reads saved results."""
import json
from pathlib import Path
import pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

OUT = Path(__file__).resolve().parent
w = pd.read_csv(OUT / 'weekly-decomposition.csv', parse_dates=['week_ending']).set_index('week_ending')
res = json.loads((OUT / 'decomposition.json').read_text())
start, end = (pd.Timestamp(t) for t in res['longest_run_window'])

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                     'axes.spines.top': False, 'axes.spines.right': False})
fig, (top, bot) = plt.subplots(2, 1, figsize=(13, 8.4), sharex=True, gridspec_kw={'height_ratios': [1.6, 1]})
fig.subplots_adjust(left=.075, right=.985, top=.80, bottom=.17, hspace=.32)
fig.suptitle('Why the level warning stays open for 243 days: labelled leaks AND other excess flow',
             x=.075, y=.965, ha='left', fontsize=17, weight='bold')
fig.text(.075, .905, 'L-Town 2018, main zone (p227 + p235 − PUMP_1), repaired baseline, weekly means. '
         'Retrospective explanation only.', color='#4b5563')
fig.text(.075, .862, 'Excess = observed − expected. Split into the known flow of the 12 labelled main-zone '
         'leaks, and the remainder.', fontsize=10, color='#4b5563')

for a in (top, bot):
    a.axvspan(start, end, color='#146aab', alpha=.07, zorder=0)
x = w.index
top.fill_between(x, 0, w.leak, step='mid', color='#93431b', alpha=.75, label='known labelled leak flow')
top.fill_between(x, w.leak, w.leak + w.remainder, step='mid', color='#9ca3af', alpha=.75,
                 label='remainder: non-labelled-leak flow above the January expectation')
top.plot(x, w.excess, color='#146aab', linewidth=1.6, drawstyle='steps-mid', label='total excess')
top.axhline(10, color='#374151', linestyle='--', linewidth=1.1)
top.text(x[1], 12, 'level-warning threshold 10 m³/h', fontsize=9, color='#374151')
top.axhline(0, color='#6b7280', linewidth=.8)
top.set_ylabel('m³/hour (weekly mean)')
top.set_title('1. Each week\'s excess, split into its two parts', loc='left', fontsize=12, pad=8)
top.legend(frameon=False, fontsize=9.3, loc='upper left', ncol=1)
top.grid(axis='y', alpha=.18)
top.text(pd.Timestamp('2018-07-20'), top.get_ylim()[1] * .93,
         f"long alert: {start:%d %b} → {end:%d %b}", color='#146aab', fontsize=10, weight='bold')

bot.plot(x, w.open_actual * 100, color='#146aab', linewidth=1.9, drawstyle='steps-mid',
         label=f"as observed — open {res['actual_alert']['share_open']:.0%} of hours, longest run {res['actual_alert']['longest_h']:,} h")
bot.plot(x, w.open_without_leak * 100, color='#6b7280', linewidth=1.7, drawstyle='steps-mid',
         label=f"with known leak flow subtracted — open {res['diagnostic_without_known_leak_flow']['share_open']:.0%}, "
               f"longest run {res['diagnostic_without_known_leak_flow']['longest_h']} h")
bot.set_ylabel('% of hours\nalert open')
bot.set_ylim(0, 105)
bot.set_title('2. The unchanged warning rule, with and without the known leak flow', loc='left', fontsize=12, pad=8)
bot.legend(frameon=False, fontsize=9.3, loc='lower right')
bot.grid(axis='y', alpha=.18)
bot.xaxis.set_major_locator(mdates.MonthLocator()); bot.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
bot.set_xlim(x[0] - pd.Timedelta(days=4), x[-1] + pd.Timedelta(days=4))

d = res['during_longest_run_mean']
fig.text(.075, .093, f"During the long alert: excess {d['excess']:.1f} m³/h = labelled leaks {d['leak']:.1f} (44%) + "
         f"remainder {d['remainder']:.1f} (56%). Either part alone exceeds the threshold in most of its hours.",
         fontsize=10, color='#4b5563')
fig.text(.075, .055, 'The remainder is non-labelled-leak flow: it rises from ~0 in January to a July peak and falls '
         'back by December — consistent with seasonal demand, not proof of it.', fontsize=10, color='#4b5563')
fig.text(.075, .017, 'Source: BattLeDIM, Vrachimis et al.  https://zenodo.org/records/4017659  CC BY 4.0. '
         'Simulated data. Leak truth used only to explain; never as a warning input. 2019 not used.', fontsize=9)
fig.savefig(OUT / 'weekly-decomposition.png', dpi=170, facecolor='white')
print('saved')
