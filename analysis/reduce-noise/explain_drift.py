"""How much of Step A's "noise" was actually real leaks?

The saved scenario configuration shows four gradual ("incipient") leaks were
already running or started inside our January-February development window:
  p257 from 2018-01-08, p461 from 2018-01-23, p232 from 2018-01-31,
  p427 from 2018-02-13.
So the window was never quiet. This script checks how much of the upward
drift we measured is explained by those known leaks.

This uses the answer sheet deliberately and only for the DEVELOPMENT period,
which the project plan permits provided it is documented. 2019 stays sealed.
"""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SCORE_FROM, SCORE_TO = '2018-01-15', '2018-02-28'

differences = pd.read_csv(OUT / 'reduce-noise.csv', parse_dates=['Timestamp']).set_index('Timestamp')

truth = pd.read_csv(ROOT / 'data/l-town/reference/2018_Leakages.csv',
                    sep=';', decimal=',', parse_dates=['Timestamp']).set_index('Timestamp')
active = truth.loc[SCORE_FROM:SCORE_TO]
per_leak = active.mean().round(3)
running = per_leak[per_leak > 0]
total_leak_hourly = active.sum(axis=1).resample('h').mean()

hourly_fixed = differences['hourly_fixed_week'].dropna()
hourly_rolling = differences['hourly_rolling_14d'].dropna()
aligned = total_leak_hourly.loc[hourly_fixed.index]

monthly = pd.DataFrame({
    'known_total_leak_flow': aligned,
    'difference_frozen_week': hourly_fixed,
    'difference_rolling_14d': hourly_rolling,
}).groupby(aligned.index.to_period('M')).mean().round(3)

stats = {
    'purpose': 'Check how much of the measured drift is explained by known leaks. Development period only.',
    'window': [SCORE_FROM, SCORE_TO],
    'answer_sheet_used': True,
    'answer_sheet_scope': 'development period only; 2019 remains unopened',
    'leaks_running_in_window_m3_per_hour': {k: float(v) for k, v in running.items()},
    'known_total_leak_flow_mean_m3_per_hour': round(float(aligned.mean()), 3),
    'our_difference_mean_m3_per_hour': {
        'frozen_week': round(float(hourly_fixed.mean()), 3),
        'rolling_14d': round(float(hourly_rolling.mean()), 3),
    },
    'correlation_with_known_leak_flow': {
        'frozen_week': round(float(hourly_fixed.corr(aligned)), 3),
        'rolling_14d': round(float(hourly_rolling.corr(aligned)), 3),
    },
    'monthly_means_m3_per_hour': {str(p): row.to_dict() for p, row in monthly.iterrows()},
    'known_leak_growth_m3_per_hour': {
        'first_week_of_window': round(float(aligned.loc['2018-01-15':'2018-01-21'].mean()), 3),
        'last_week_of_window': round(float(aligned.loc['2018-02-22':'2018-02-28'].mean()), 3),
    },
}
(OUT / 'explain-drift.json').write_text(json.dumps(stats, indent=2) + '\n')
print(json.dumps(stats, indent=2))
