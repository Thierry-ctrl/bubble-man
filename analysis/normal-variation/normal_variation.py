"""How much does flow normally differ from the expected pattern?

Step A of building an alert rule. We must know what ordinary variation looks
like before we can say which differences are large enough to be worth a visit.

Deliberate discipline in this script:
  * The answer sheet (2018_Leakages.csv) is NOT opened anywhere below.
  * Training week and scoring window do not overlap, and training comes first.
  * The scoring window is January-February, well before the March 5 leak we
    already looked at, so nothing here is tuned around that known event.

Colour convention adopted from here on, and used in every future figure:
    blue   #146aab  observed flow (reading from the simulated sensor)
    orange #be720c  expected flow (our baseline's guess)
    red    #93431b  known leak information (the answer sheet)
This corrects the earlier inconsistency where orange meant leak flow in the
first figure and expected flow in the second.
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

# January 8-14 is a full Monday-Sunday week. We skip January 1-7 because
# New Year's Day would distort the weekday pattern.
TRAIN_FROM, TRAIN_TO = '2018-01-08', '2018-01-14'
SCORE_FROM, SCORE_TO = '2018-01-15', '2018-02-28'

raw = pd.read_csv(ROOT / 'data/l-town/readings/2018_SCADA_Flows.csv',
                  sep=';', decimal=',', parse_dates=['Timestamp']).set_index('Timestamp')[METER]
selected = raw.loc[TRAIN_FROM:SCORE_TO]
assert selected.index.is_unique, 'duplicate timestamps'
assert not selected.isna().any(), 'missing flow readings'
assert (selected.index.to_series().diff().dropna() == pd.Timedelta(minutes=5)).all(), 'gap in readings'
assert len(selected) == 52 * 288, f'expected 52 days of readings, got {len(selected) / 288:.2f}'
assert (selected.resample('h').count() == 12).all(), 'an hour is missing readings'

hourly = selected.resample('h').mean().to_frame('actual_m3_per_hour')
hourly['weekend'] = hourly.index.dayofweek >= 5
hourly['hour'] = hourly.index.hour

# Same baseline method as the first-look experiment: for each hour of the day,
# the median flow in the training week, weekdays and weekends kept separate.
training = hourly.loc[TRAIN_FROM:TRAIN_TO]
profile = training.groupby(['weekend', 'hour'])['actual_m3_per_hour'].median()
assert len(training) == 168 and len(profile) == 48, 'training week is not complete'

hourly['expected_m3_per_hour'] = [profile.loc[(w, h)] for w, h in zip(hourly.weekend, hourly.hour)]
hourly['difference_m3_per_hour'] = hourly.actual_m3_per_hour - hourly.expected_m3_per_hour

score = hourly.loc[SCORE_FROM:SCORE_TO]
assert training.index.max() < score.index.min(), 'training must end before scoring begins'
assert len(score) == 45 * 24, 'scoring window is not 45 whole days'
diff = score.difference_m3_per_hour


def episodes(series, threshold, min_hours):
    """Count separate stretches where the difference stays above `threshold`
    for at least `min_hours` consecutive hours. One stretch = one alert."""
    above = (series > threshold).to_numpy()
    lengths, run = [], 0
    for flag in above:
        if flag:
            run += 1
        elif run:
            lengths.append(run)
            run = 0
    if run:
        lengths.append(run)
    return sum(1 for length in lengths if length >= min_hours), (max(lengths) if lengths else 0)


THRESHOLDS = [2, 4, 6, 8, 10, 12, 15, 20]
PERSISTENCE = [1, 3, 6, 12, 24]
months = 45 / 30.44
grid = {
    f'above_{t}_for_{p}h': {
        'alerts': episodes(diff, t, p)[0],
        'alerts_per_month': round(episodes(diff, t, p)[0] / months, 2),
    }
    for t in THRESHOLDS for p in PERSISTENCE
}

stats = {
    'purpose': 'Describe ordinary variation before choosing an alert rule. No answer sheet used.',
    'source': 'https://zenodo.org/records/4017659',
    'meter': METER,
    'data_type': 'synthetic',
    'answer_sheet_used': False,
    'training_dates': [TRAIN_FROM, TRAIN_TO],
    'scoring_dates': [SCORE_FROM, SCORE_TO],
    'scoring_hours': int(len(score)),
    'method': 'Hourly mean flow; median by hour and weekday/weekend from training week only.',
    'difference_m3_per_hour': {
        'mean': round(float(diff.mean()), 3),
        'mean_absolute': round(float(diff.abs().mean()), 3),
        'standard_deviation': round(float(diff.std()), 3),
        'min': round(float(diff.min()), 3),
        'max': round(float(diff.max()), 3),
    },
    'percentiles_m3_per_hour': {f'p{q}': round(float(np.percentile(diff, q)), 3)
                                for q in (1, 5, 25, 50, 75, 90, 95, 99)},
    'longest_run_above_zero_hours': int(episodes(diff, 0, 1)[1]),
    'monthly_mean_difference_m3_per_hour': {
        str(period): round(float(value), 3)
        for period, value in diff.groupby(diff.index.to_period('M')).mean().items()
    },
    'weekly_mean_difference_m3_per_hour': {
        str(week.date()): round(float(value), 3)
        for week, value in diff.resample('W').mean().items()
    },
    'alert_grid': grid,
    'limitations': [
        'This window may itself contain leaks; we deliberately did not check.',
        'A threshold calibrated on a window containing leaks will be too high, not too low.',
        'One meter (p227) and one training week only.',
        'No rule has been chosen and no detection performance has been established.',
    ],
}

score.drop(columns=['weekend', 'hour']).to_csv(OUT / 'normal-variation.csv', index_label='Timestamp')
(OUT / 'normal-variation.json').write_text(json.dumps(stats, indent=2) + '\n')

# ---------------------------------------------------------------- figure
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                     'axes.spines.top': False, 'axes.spines.right': False})
fig = plt.figure(figsize=(11, 7.4))
fig.subplots_adjust(left=.085, right=.97, top=.80, bottom=.185, hspace=.55)
grid_spec = fig.add_gridspec(2, 2, width_ratios=[3, 1], height_ratios=[1, 1])
series_ax = fig.add_subplot(grid_spec[0, :])
hist_ax = fig.add_subplot(grid_spec[1, 0])
runs_ax = fig.add_subplot(grid_spec[1, 1])

fig.suptitle('How much does flow normally differ from what we expected?', x=.085, y=.965,
             ha='left', fontsize=19, weight='bold')
fig.text(.085, .905, f'L-Town simulation. Meter {METER}. January 15 – February 28, 2018. Hourly averages.',
         color='#4b5563')
fig.text(.085, .862, 'Expected pattern learned from January 8–14 only. The leak answer sheet was not opened.',
         fontsize=10, color='#4b5563')

series_ax.plot(score.index, diff, color='#146aab', linewidth=1.0)
series_ax.axhline(0, color='#6b7280', linewidth=1)
series_ax.fill_between(score.index, diff, 0, where=diff > 0, color='#146aab', alpha=.12)
series_ax.set_title('1. Observed minus expected, hour by hour', loc='left', fontsize=12, pad=10)
series_ax.set_ylabel('Difference\n(m³/hour)')
series_ax.grid(axis='y', alpha=.18)
series_ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
series_ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
series_ax.set_xlim(score.index[0], score.index[-1])

hist_ax.hist(diff, bins=60, color='#146aab', alpha=.75)
for q, style in ((50, '-'), (95, '--')):
    value = float(np.percentile(diff, q))
    hist_ax.axvline(value, color='#93431b', linestyle=style, linewidth=1.4)
    hist_ax.text(value, hist_ax.get_ylim()[1] * (.93 if q == 50 else .78), f' {q}th: {value:.1f}',
                 color='#93431b', fontsize=9)
hist_ax.set_title('2. How often each size of difference occurs', loc='left', fontsize=12, pad=10)
hist_ax.set_xlabel('Difference (m³/hour)')
hist_ax.set_ylabel('Hours')
hist_ax.grid(axis='y', alpha=.18)

for row, persistence in enumerate([1, 6, 24]):
    counts = [episodes(diff, t, persistence)[0] for t in THRESHOLDS]
    runs_ax.plot(THRESHOLDS, counts, marker='o', markersize=4, linewidth=1.5,
                 color=['#146aab', '#be720c', '#93431b'][row],
                 label=f'lasting ≥{persistence}h')
runs_ax.set_title('3. Alerts raised', loc='left', fontsize=12, pad=10)
runs_ax.set_xlabel('Threshold (m³/hour)')
runs_ax.set_ylabel('Alerts in 45 days')
runs_ax.legend(frameon=False, fontsize=9)
runs_ax.grid(axis='y', alpha=.18)

fig.text(.085, .105, 'This window may itself contain leaks. We did not check, so the spread shown is "variation we would see in practice",',
         fontsize=10, color='#4b5563')
fig.text(.085, .068, 'not "variation with no leaks". A threshold picked from it errs towards being too high rather than too low.',
         fontsize=10, color='#4b5563')
fig.text(.085, .028, 'Source: BattLeDIM, Vrachimis et al.  https://zenodo.org/records/4017659  CC BY 4.0', fontsize=9)
fig.savefig(OUT / 'normal-variation.png', dpi=170, facecolor='white')
print(json.dumps(stats, indent=2))
