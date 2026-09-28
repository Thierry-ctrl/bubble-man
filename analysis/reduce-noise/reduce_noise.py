"""Can we make the difference less noisy before we try to threshold it?

Step A showed the hour-by-hour difference at p227 swings so widely that a
change the size of the March 5 leak would sit inside ordinary variation.
Two standard ideas, tested here on the SAME window as Step A so the numbers
are directly comparable:

  night flow   Use only 02:00-04:00, when customer taps are mostly closed, so
               what remains is dominated by leakage rather than demand. This
               is the water industry's usual "minimum night flow" idea.
  rolling      Relearn the expected pattern from the previous 14 days each
               day, instead of freezing one week forever.

The answer sheet is NOT opened in this script. We are only measuring spread:
a smaller spread means a lower threshold becomes usable, which means smaller
leaks could be caught. Whether it actually catches leaks is a later question.

Colours: blue #146aab observed, orange #be720c expected, red #93431b truth.
"""
from pathlib import Path
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
METER = 'p227'
HISTORY_DAYS = 14
NIGHT_HOURS = [2, 3]                      # 02:00-04:00
SCORE_FROM, SCORE_TO = '2018-01-15', '2018-02-28'
FIXED_FROM, FIXED_TO = '2018-01-08', '2018-01-14'

raw = pd.read_csv(ROOT / 'data/l-town/readings/2018_SCADA_Flows.csv',
                  sep=';', decimal=',', parse_dates=['Timestamp']).set_index('Timestamp')[METER]
selected = raw.loc['2018-01-01':SCORE_TO]
assert selected.index.is_unique and not selected.isna().any()
assert (selected.index.to_series().diff().dropna() == pd.Timedelta(minutes=5)).all()
assert (selected.resample('h').count() == 12).all()

hourly = selected.resample('h').mean().to_frame('flow')
hourly['weekend'] = hourly.index.dayofweek >= 5
hourly['hour'] = hourly.index.hour
score_index = hourly.loc[SCORE_FROM:SCORE_TO].index
assert len(score_index) == 45 * 24

# ---- variant 1: every hour, one frozen training week -------------------
fixed_profile = hourly.loc[FIXED_FROM:FIXED_TO].groupby(['weekend', 'hour'])['flow'].median()
expected_fixed = pd.Series([fixed_profile.loc[(w, h)] for w, h in
                            zip(hourly.loc[score_index].weekend, hourly.loc[score_index].hour)],
                           index=score_index)
hourly_fixed = hourly.loc[score_index, 'flow'] - expected_fixed

# ---- variant 2: every hour, relearned from the previous 14 days --------
rolling_expected = {}
for stamp in score_index:
    window = hourly.loc[stamp - pd.Timedelta(days=HISTORY_DAYS):stamp - pd.Timedelta(hours=1)]
    same = window[(window.weekend == (stamp.dayofweek >= 5)) & (window.hour == stamp.hour)]
    assert len(same) >= 4, f'too little history at {stamp}'
    rolling_expected[stamp] = same['flow'].median()
hourly_rolling = hourly.loc[score_index, 'flow'] - pd.Series(rolling_expected)

# ---- night flow: one number per day ------------------------------------
night = hourly[hourly.hour.isin(NIGHT_HOURS)]['flow'].resample('D').mean().dropna()
assert (hourly[hourly.hour.isin(NIGHT_HOURS)].resample('D').size().dropna() == len(NIGHT_HOURS)).all()
night_score = night.loc[SCORE_FROM:SCORE_TO]
assert len(night_score) == 45

night_fixed = night_score - night.loc[FIXED_FROM:FIXED_TO].median()
night_rolling = night_score - pd.Series(
    {day: night.loc[day - pd.Timedelta(days=HISTORY_DAYS):day - pd.Timedelta(days=1)].median()
     for day in night_score.index})

VARIANTS = {
    'hourly_fixed_week':   ('Every hour, frozen week',      hourly_fixed),
    'hourly_rolling_14d':  ('Every hour, last 14 days',     hourly_rolling),
    'night_fixed_week':    ('Night only, frozen week',      night_fixed),
    'night_rolling_14d':   ('Night only, last 14 days',     night_rolling),
}


def describe(series):
    quarter, three_quarter = np.percentile(series, [25, 75])
    return {
        'observations': int(len(series)),
        'mean': round(float(series.mean()), 3),
        'mean_absolute': round(float(series.abs().mean()), 3),
        'standard_deviation': round(float(series.std()), 3),
        'interquartile_range': round(float(three_quarter - quarter), 3),
        'p5': round(float(np.percentile(series, 5)), 3),
        'p95': round(float(np.percentile(series, 95)), 3),
        'span_p5_to_p95': round(float(np.percentile(series, 95) - np.percentile(series, 5)), 3),
    }


summary = {key: describe(series) for key, (_, series) in VARIANTS.items()}
reference = summary['hourly_fixed_week']['standard_deviation']
for key in summary:
    summary[key]['spread_vs_step_a'] = round(summary[key]['standard_deviation'] / reference, 3)

stats = {
    'purpose': 'Test whether night-only flow and a rolling baseline reduce noise. No answer sheet used.',
    'source': 'https://zenodo.org/records/4017659',
    'meter': METER, 'data_type': 'synthetic', 'answer_sheet_used': False,
    'scoring_dates': [SCORE_FROM, SCORE_TO],
    'night_window': '02:00-04:00', 'rolling_history_days': HISTORY_DAYS,
    'units': 'm3_per_hour',
    'variants': summary,
    'limitations': [
        'Spread is measured on a window that may itself contain leaks.',
        'A rolling baseline slowly absorbs a leak: after about 14 days a steady leak looks normal again.',
        'Night-only means one number per day, so detection is slower.',
        'One meter (p227). No rule chosen and no detection performance established.',
    ],
}
(OUT / 'reduce-noise.json').write_text(json.dumps(stats, indent=2) + '\n')
pd.DataFrame({key: series for key, (_, series) in VARIANTS.items()}).to_csv(OUT / 'reduce-noise.csv',
                                                                           index_label='Timestamp')

# ---------------------------------------------------------------- figure
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                     'axes.spines.top': False, 'axes.spines.right': False})
fig, (series_ax, bar_ax) = plt.subplots(1, 2, figsize=(12, 5.9), gridspec_kw={'width_ratios': [2.1, 1]})
fig.subplots_adjust(left=.075, right=.975, top=.74, bottom=.22, wspace=.30)
fig.suptitle('Does looking only at night, and relearning weekly, calm the signal?', x=.075, y=.955,
             ha='left', fontsize=18, weight='bold')
fig.text(.075, .885, f'L-Town simulation. Meter {METER}. January 15 – February 28, 2018. Answer sheet not opened.',
         color='#4b5563')
fig.text(.075, .838, 'Both panels show observed minus expected flow. Closer to a flat line is better.',
         fontsize=10, color='#4b5563')

series_ax.axhline(0, color='#6b7280', linewidth=1)
series_ax.plot(hourly_fixed.index, hourly_fixed, color='#9ca3af', linewidth=.8,
               label='Every hour, frozen week (Step A)')
series_ax.plot(night_rolling.index, night_rolling, color='#146aab', linewidth=1.9,
               marker='o', markersize=3, label='Night only, last 14 days')
series_ax.set_title('1. The same period, measured two ways', loc='left', fontsize=12, pad=10)
series_ax.set_ylabel('Difference (m³/hour)')
series_ax.set_xlabel('Date (dataset timestamps)')
series_ax.legend(frameon=False, fontsize=9, loc='upper left', ncol=1)
series_ax.grid(axis='y', alpha=.18)
series_ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
series_ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
series_ax.set_xlim(score_index[0], score_index[-1])

labels = [label for label, _ in VARIANTS.values()]
spreads = [summary[key]['standard_deviation'] for key in VARIANTS]
colours = ['#9ca3af', '#9ca3af', '#be720c', '#146aab']
bars = bar_ax.barh(range(len(labels)), spreads, color=colours)
bar_ax.set_yticks(range(len(labels)))
bar_ax.set_yticklabels(labels, fontsize=9.5)
bar_ax.invert_yaxis()
bar_ax.set_title('2. Typical size of the swings', loc='left', fontsize=12, pad=10)
bar_ax.set_xlabel('Standard deviation (m³/hour)')
bar_ax.set_xlim(0, max(spreads) * 1.28)
bar_ax.grid(axis='x', alpha=.18)
for bar, value in zip(bars, spreads):
    bar_ax.text(value + max(spreads) * .03, bar.get_y() + bar.get_height() / 2,
                f'{value:.1f}', va='center', fontsize=9.5)

fig.text(.075, .105, 'A calmer signal means a lower alert threshold becomes usable, so smaller leaks could be caught.',
         fontsize=10, color='#4b5563')
fig.text(.075, .065, 'Caution: relearning from the last 14 days also slowly absorbs a real leak, making it look normal again after about two weeks.',
         fontsize=10, color='#4b5563')
fig.text(.075, .025, 'Source: BattLeDIM, Vrachimis et al.  https://zenodo.org/records/4017659  CC BY 4.0', fontsize=9)
fig.savefig(OUT / 'reduce-noise.png', dpi=170, facecolor='white')
print(json.dumps(stats['variants'], indent=2))
