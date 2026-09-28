"""Score our EXISTING baseline methods against the known 2018 leaks.

IMPORTANT — THE GAP THIS SCRIPT HAS TO WORK AROUND
--------------------------------------------------
None of our existing scripts emit warnings. compare_baseline.py, normal_variation.py
and reduce_noise.py all produce a DIFFERENCE (observed minus expected flow) and stop
there. No threshold was ever chosen and frozen, so there is no existing detector to
score.

Rather than invent one and present it as ours, this script sweeps a DECLARED GRID of
threshold and persistence values and reports every cell. The grid is copied unchanged
from normal_variation.py, where it was written before any leak outcome was examined.
No cell is selected as "our setting"; the detailed tables use the arithmetic midpoint
of the grid purely as an illustration.

The three baseline METHODS below are unchanged in their settings; they are only
applied over a longer window than before.
"""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from leak_scorer import Rules, load_leaks, score  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
METER = 'p227'

WINDOW_FROM, WINDOW_TO = '2018-01-15', '2018-12-31 23:00'
FROZEN_FROM, FROZEN_TO = '2018-01-08', '2018-01-14'   # as in normal_variation.py
HISTORY_DAYS = 14                                      # as in reduce_noise.py
NIGHT_HOURS = [2, 3]                                   # 02:00-04:00, as in reduce_noise.py

THRESHOLDS = [2, 4, 6, 8, 10, 12, 15, 20]              # grid copied from normal_variation.py
PERSISTENCE = [1, 3, 6, 12, 24]
ILLUSTRATIVE = (10, 6)                                 # arithmetic midpoint of the grid

raw = pd.read_csv(ROOT / 'data/l-town/readings/2018_SCADA_Flows.csv',
                  sep=';', decimal=',', parse_dates=['Timestamp']).set_index('Timestamp')[METER]
assert raw.index.is_unique and not raw.isna().any()
assert (raw.index.to_series().diff().dropna() == pd.Timedelta(minutes=5)).all()
assert len(raw) == 365 * 288, f'expected a full year of 5-minute readings, got {len(raw)}'
assert (raw.resample('h').count() == 12).all()

hourly = raw.resample('h').mean().to_frame('flow')
hourly['weekend'] = hourly.index.dayofweek >= 5
hourly['hour'] = hourly.index.hour
window = hourly.loc[WINDOW_FROM:WINDOW_TO].index

# ---- method 1: frozen training week (settings from normal_variation.py) ----
profile = hourly.loc[FROZEN_FROM:FROZEN_TO].groupby(['weekend', 'hour'])['flow'].median()
assert len(profile) == 48
frozen = hourly.loc[window, 'flow'] - pd.Series(
    [profile.loc[(w, h)] for w, h in zip(hourly.loc[window].weekend, hourly.loc[window].hour)],
    index=window)

# ---- method 2: rolling 14 days (settings from reduce_noise.py) ----
expected = {}
for stamp in window:
    past = hourly.loc[stamp - pd.Timedelta(days=HISTORY_DAYS):stamp - pd.Timedelta(hours=1)]
    same = past[(past.weekend == (stamp.dayofweek >= 5)) & (past.hour == stamp.hour)]
    assert len(same) >= 4, f'too little history at {stamp}'
    expected[stamp] = same['flow'].median()
rolling = hourly.loc[window, 'flow'] - pd.Series(expected)

# ---- method 3: night only, rolling 14 days (settings from reduce_noise.py) ----
# One value per day. It becomes known at 04:00, when the 02:00-04:00 window closes,
# so the warning is timestamped there. Consecutive days must merge into one event,
# hence the 23-hour gap tolerance for this method only. That is a resolution choice,
# not a tuning choice.
night_daily = hourly[hourly.hour.isin(NIGHT_HOURS)]['flow'].resample('D').mean().dropna()
night = pd.Series({day.replace(hour=4): value - night_daily.loc[
    day - pd.Timedelta(days=HISTORY_DAYS):day - pd.Timedelta(days=1)].median()
    for day, value in night_daily.items()}).loc[WINDOW_FROM:WINDOW_TO]

METHODS = {
    'frozen_week':      (frozen, Rules(gap_tolerance_hours=0, min_history_days=0)),
    'rolling_14d':      (rolling, Rules(gap_tolerance_hours=0, min_history_days=0)),
    'night_rolling_14d': (night, Rules(gap_tolerance_hours=23, min_history_days=0)),
}

leaks = load_leaks(ROOT / 'research/2026-09-21/battledim-config.yaml')
leaks_2018 = leaks[leaks.start.dt.year == 2018].reset_index(drop=True)
assert len(leaks_2018) == 14, f'expected 14 leaks in 2018, got {len(leaks_2018)}'


def warn(difference, threshold, persistence):
    """Declared illustrative rule: difference above `threshold` for `persistence`
    consecutive observations. NOT one of our detectors — see the module docstring."""
    above = difference > threshold
    sustained = above.rolling(persistence).sum() == persistence
    flagged = pd.Series(False, index=difference.index)
    for stamp in sustained[sustained.fillna(False)].index:
        first = difference.index.get_loc(stamp) - persistence + 1
        flagged.iloc[first:difference.index.get_loc(stamp) + 1] = True
    return flagged


grid_rows, detail = [], {}
for name, (difference, rules) in METHODS.items():
    for threshold in THRESHOLDS:
        for persistence in PERSISTENCE:
            if name == 'night_rolling_14d' and persistence > 3:
                continue                      # only ~350 daily values exist
            result = score(warn(difference, threshold, persistence), leaks_2018, rules)
            grid_rows.append({
                'method': name, 'threshold_m3_per_hour': threshold,
                'persistence_observations': persistence,
                'alert_events': result['alert_events_total'],
                'leaks_matched': result['overall']['matched'],
                'leaks_missed': result['overall']['missed'],
                'ambiguous_matches': result['overall']['ambiguous_matches'],
                'abrupt_matched': result['abrupt']['matched'],
                'abrupt_total': result['abrupt']['eligible_leaks'],
                'incipient_matched': result['incipient']['matched'],
                'incipient_total': result['incipient']['eligible_leaks'],
                'unmatched_alerts_per_week': result['unmatched_alerts_per_week'],
                'repeat_alerts_scored_zero': result['repeat_alerts_scored_zero'],
                'median_delay_hours': result['overall']['median_delay_hours'],
            })
            if (threshold, persistence) == ILLUSTRATIVE:
                detail[name] = result

grid = pd.DataFrame(grid_rows)
grid.to_csv(OUT / 'score-grid.csv', index=False)
(OUT / 'score-detail-illustrative.json').write_text(json.dumps({
    'note': ('Detailed tables at the arithmetic midpoint of the declared grid '
             f'(threshold {ILLUSTRATIVE[0]} m3/h, persistence {ILLUSTRATIVE[1]}). '
             'Chosen mechanically, NOT because it scores well.'),
    'eligible_leaks': int((detail['frozen_week']['overall']['eligible_leaks'])),
    'methods': detail,
}, indent=2) + '\n')

pd.DataFrame(detail['frozen_week']['leaks']).to_csv(OUT / 'leak-outcomes-frozen-week.csv', index=False)
pd.DataFrame(detail['frozen_week']['events']).to_csv(OUT / 'alert-events-frozen-week.csv', index=False)

print('=== eligibility of the 14 known 2018 leaks ===')
for row in detail['frozen_week']['leaks']:
    print(f"  {row['link']:5s} {row['type']:10s} start {row['start'][:16]}  {row['eligibility']}")
print('\n=== grid (leaks matched out of eligible / unnecessary warnings per week) ===')
for name in METHODS:
    part = grid[grid.method == name]
    print(f'\n-- {name}')
    print(part[['threshold_m3_per_hour', 'persistence_observations', 'alert_events',
                'leaks_matched', 'leaks_missed', 'abrupt_matched', 'incipient_matched',
                'unmatched_alerts_per_week', 'median_delay_hours']].to_string(index=False))
