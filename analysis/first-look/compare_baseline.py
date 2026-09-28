from pathlib import Path
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
raw = pd.read_csv(ROOT / 'data/l-town/readings/2018_SCADA_Flows.csv',
                  sep=';', decimal=',', parse_dates=['Timestamp']).set_index('Timestamp')['p227']
selected = raw.loc['2018-02-19':'2018-03-08']
assert selected.index.is_unique and not selected.isna().any()
assert len(selected) == 18 * 288
assert (selected.index.to_series().diff().dropna() == pd.Timedelta(minutes=5)).all()
# Hourly means reduce visual noise; every hour must contain all 12 readings.
assert (selected.resample('h').count() == 12).all()
hourly = selected.resample('h').mean().to_frame('actual_m3_per_hour')
hourly['weekend'] = hourly.index.dayofweek >= 5
hourly['hour'] = hourly.index.hour
training = hourly.loc['2018-02-19':'2018-02-25']
profile = training.groupby(['weekend', 'hour'])['actual_m3_per_hour'].median()
assert len(training) == 168 and len(profile) == 48
hourly['expected_m3_per_hour'] = [profile.loc[(weekend, hour)]
                                      for weekend, hour in zip(hourly['weekend'], hourly['hour'])]
hourly['difference_m3_per_hour'] = hourly.actual_m3_per_hour - hourly.expected_m3_per_hour
holdout = hourly.loc['2018-02-26':'2018-03-04']
after = hourly.loc['2018-03-06':'2018-03-08']
assert len(holdout) == 168 and len(after) == 72
assert training.index.max() < holdout.index.min()

# The answer sheet is read only after fitting and calculating the comparison.
truth = pd.read_csv(ROOT / 'data/l-town/reference/2018_Leakages.csv',
                    sep=';', decimal=',', parse_dates=['Timestamp']).set_index('Timestamp')['p673']
onset = truth[truth > 0].index.min()
assert onset == pd.Timestamp('2018-03-05 15:45')
week = hourly.loc['2018-03-02':'2018-03-08']
stats = {
    'source': 'https://zenodo.org/records/4017659',
    'meter': 'p227', 'data_type': 'synthetic',
    'training_dates': ['2018-02-19', '2018-02-25'],
    'holdout_dates': ['2018-02-26', '2018-03-04'],
    'method': 'Hourly mean flow; median by hour and weekday/weekend from training week only.',
    'holdout_mean_difference_m3_per_hour': float(holdout.difference_m3_per_hour.mean()),
    'holdout_mean_absolute_difference_m3_per_hour': float(holdout.difference_m3_per_hour.abs().mean()),
    'after_dates': ['2018-03-06', '2018-03-08'],
    'after_mean_difference_m3_per_hour': float(after.difference_m3_per_hour.mean()),
    'known_leak_onset': str(onset),
    'limitations': ['Existing leaks are included in the baseline.',
                    'One training week and one holdout week only.',
                    'Differences are not estimates of leak volume or validated alerts.',
                    'Other growing leaks, customer demand and operations can change flow.'],
    'daily_mean_difference_m3_per_hour': {
        str(t.date()): float(v) for t, v in week.difference_m3_per_hour.resample('D').mean().items()
    }
}
hourly.drop(columns=['weekend', 'hour']).to_csv(OUT / 'baseline-comparison.csv', index_label='Timestamp')
(OUT / 'baseline-verification.json').write_text(json.dumps(stats, indent=2) + '\n')

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                     'axes.spines.top': False, 'axes.spines.right': False})
fig, (ax, residual) = plt.subplots(2, 1, figsize=(11, 7.1), sharex=True,
                                  gridspec_kw={'height_ratios': [2, 1]})
fig.subplots_adjust(left=.11, right=.97, top=.81, bottom=.20, hspace=.50)
fig.suptitle('Is more water flowing than we expected?', x=.11, y=.97,
             ha='left', fontsize=20, weight='bold')
fig.text(.11, .915, 'L-Town simulation. Meter p227. March 2–8, 2018. Hourly averages.', color='#4b5563')
fig.text(.11, .872, 'Expected pattern learned from February 19–25, with separate weekday and weekend patterns.',
         fontsize=10, color='#4b5563')
ax.plot(week.index, week.actual_m3_per_hour, color='#146aab', linewidth=1.7, label='Observed flow')
ax.plot(week.index, week.expected_m3_per_hour, color='#be720c', linewidth=1.7,
        linestyle='--', label='Expected flow')
ax.set_ylabel('Flow (m³/hour)')
ax.set_title('1. Compare the readings with the earlier pattern', loc='left', fontsize=12, pad=12)
ax.legend(loc='upper left', frameon=False, ncol=2, fontsize=10)
ax.set_ylim(0, week.actual_m3_per_hour.max() * 1.3)
ax.text(onset + pd.Timedelta(hours=2), ax.get_ylim()[1] * .92,
        'Known leak starts\nMarch 5, 15:45', color='#93431b', fontsize=10, va='top')
residual.plot(week.index, week.difference_m3_per_hour, color='#146aab', linewidth=1.5)
residual.fill_between(week.index, week.difference_m3_per_hour, 0,
                      where=week.difference_m3_per_hour > 0, color='#146aab', alpha=.12)
residual.axhline(0, color='#6b7280', linewidth=1)
residual.set_title('2. Observed minus expected: above zero means more flow than expected',
                   loc='left', fontsize=12, pad=12)
residual.set_ylabel('Difference\n(m³/hour)')
for a in (ax, residual):
    a.axvline(onset, color='#93431b', linestyle=':', linewidth=1.4)
    a.grid(axis='y', alpha=.18)
residual.xaxis.set_major_locator(mdates.DayLocator())
residual.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
residual.set_xlim(week.index[0], week.index[-1])
residual.set_xlabel('Date (dataset timestamps)')
fig.text(.11, .115, 'The earlier pattern already includes existing leaks. A difference alone does not prove a new leak.',
         fontsize=10, color='#4b5563')
fig.text(.11, .075, 'Leak timing is used to check the result; it is not used to calculate expected flow.', fontsize=10)
fig.text(.11, .035, 'Source: BattLeDIM, Vrachimis et al.  https://zenodo.org/records/4017659  CC BY 4.0', fontsize=9)
fig.savefig(OUT / 'expected-vs-observed.png', dpi=170, facecolor='white')
print(json.dumps(stats, indent=2))
