"""Does the new-rise observation survive as a real-time rule? 2018 DEVELOPMENT TEST.

The rule is frozen in RULE-FROZEN.md, committed before this script was run. Nothing
below selects a threshold, and the scorer is imported unchanged. 2019 is not read.

We have already studied these six leaks. Nothing here is a performance claim.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'analysis/scorer'))
from leak_scorer import Rules, find_alerts, score  # noqa: E402  (imported, not edited)

# ---- frozen constants (see RULE-FROZEN.md) ---------------------------------
RECENT, BEFORE = 6, 24
LEVEL_THRESHOLD, LEVEL_PERSISTENCE = 10, 6
SIGMA_MULTIPLIER = 3
MIN_GAP_HOURS = 24
CALIB_FROM, CALIB_TO = '2018-01-02 05:00', '2018-01-14 23:00'
WINDOW_FROM, WINDOW_TO = '2018-01-15', '2018-12-31 23:00'
SCORER_RULES = Rules(gap_tolerance_hours=0, reporting_lag_hours=1.0, max_delay_hours=168)
REPEATS = 200

flows = pd.read_csv(ROOT / 'data/l-town/readings/2018_SCADA_Flows.csv', sep=';', decimal=',',
                    parse_dates=['Timestamp']).set_index('Timestamp')
hourly = flows.resample('h').mean()
hourly['main_out'] = hourly.p227 + hourly.p235 - hourly.PUMP_1
hourly['weekend'] = hourly.index.dayofweek >= 5
hourly['hour'] = hourly.index.hour
profile = hourly.loc['2018-01-08':'2018-01-14'].groupby(['weekend', 'hour'])['main_out'].median()
full = hourly.index
expected_full = pd.Series([profile.loc[(w, h)] for w, h in
                           zip(hourly.weekend, hourly.hour)], index=full)
diff_full = hourly['main_out'] - expected_full
step_full = (diff_full.rolling(RECENT).mean()
             - diff_full.shift(RECENT).rolling(BEFORE).mean())

# ---- 1. threshold, from the calibration period only ------------------------
calib = step_full.loc[CALIB_FROM:CALIB_TO].dropna()
q1, q3 = np.percentile(calib, [25, 75])
robust_sigma = (q3 - q1) / 1.349
THRESHOLD = float(np.median(calib) + SIGMA_MULTIPLIER * robust_sigma)
assert pd.Timestamp(CALIB_TO) < pd.Timestamp(WINDOW_FROM), 'calibration must precede the window'

# ---- 2. level alerts (Experiment A, unchanged) -----------------------------
diff = diff_full.loc[WINDOW_FROM:WINDOW_TO]
step = step_full.loc[WINDOW_FROM:WINDOW_TO]
level_alerts = find_alerts(diff > LEVEL_THRESHOLD, LEVEL_PERSISTENCE,
                           Rules(gap_tolerance_hours=0))
alert_open = pd.Series(False, index=step.index)
for event in level_alerts:
    alert_open.loc[event.issuable_at:event.end] = True

# ---- 3. new-rise warnings from readings alone ------------------------------
def generate(step_series, open_mask, threshold):
    """Frozen rule 2-4: fire while an alert is open, re-arm only after the step
    falls back below the threshold, never within MIN_GAP_HOURS."""
    warn = pd.Series(False, index=step_series.index)
    armed, last = True, None
    for stamp, value in step_series.items():
        if not np.isfinite(value):
            continue
        if value < threshold:
            armed = True
            continue
        if not (armed and open_mask.loc[stamp]):
            continue
        if last is not None and (stamp - last) < pd.Timedelta(hours=MIN_GAP_HOURS):
            continue
        warn.loc[stamp] = True
        armed, last = False, stamp
    return warn

warnings = generate(step, alert_open, THRESHOLD)

# ---- 4. score through the existing scorer, unchanged -----------------------
leaks = pd.read_csv(ROOT / 'analysis/scorer/main-zone-leaks-A_reference_inherited.csv',
                    parse_dates=['start', 'end'])
leaks = leaks.rename(columns={'delay_hours_from_configured_onset': '_d'})[
    ['link', 'start', 'end', 'type', 'zone']]
leaks['diameter_m'], leaks['peak'] = 0.02, leaks.start
leaks['configured_start'] = leaks.start
result = score(warnings, 1, leaks, SCORER_RULES)

# ---- 5. random comparison, restricted to hours when the rule could fire ----
candidates = np.array([i for i, flag in enumerate(alert_open) if flag])
gap = MIN_GAP_HOURS
rng = np.random.default_rng(20261003)
n_warn = int(warnings.sum())


def random_warnings():
    picked, order = [], rng.permutation(candidates)
    for position in order:
        if all(abs(position - p) >= gap for p in picked):
            picked.append(position)
            if len(picked) == n_warn:
                break
    series = pd.Series(False, index=step.index)
    series.iloc[picked] = True
    return series


random_credits, random_abrupt = [], []
for _ in range(REPEATS):
    outcome = score(random_warnings(), 1, leaks, SCORER_RULES)
    random_credits.append(outcome['overall']['credited'])
    random_abrupt.append(outcome['abrupt']['credited'])

# ---- 6. compare with Experiment A ------------------------------------------
experiment_a = json.loads((ROOT / 'analysis/scorer/main-zone-report.json').read_text())
a = experiment_a['A_reference_inherited']
credited = {r['link']: r for r in result['leaks'] if r['outcome'] == 'credited'}
a_credited = {r['link'] for r in a['leaks'] if r['outcome'] == 'credited'}
missed_by_a = ['p538', 'p866', 'p158']

report = {
    'label': '2018 DEVELOPMENT TEST — these six leaks were studied before the rule was written',
    'rule': {'threshold_m3_per_hour': round(THRESHOLD, 3),
             'derived_from': f'median + {SIGMA_MULTIPLIER} x IQR/1.349 over {CALIB_FROM} .. {CALIB_TO}',
             'calibration_hours': int(len(calib)),
             'calibration_median': round(float(np.median(calib)), 3),
             'calibration_robust_sigma': round(float(robust_sigma), 3),
             'min_gap_hours': MIN_GAP_HOURS, 'condition': 'only while a level alert is open'},
    'exposure': {
        'hours_in_window': int(len(step)),
        'hours_with_level_alert_open': int(alert_open.sum()),
        'quiet_window_hours_with_alert_open': int(
            alert_open.loc['2018-01-15':'2018-01-23 22:00'].sum()),
    },
    'new_rule': {
        'warnings_issued': n_warn,
        'alert_events_after_grouping': result['alert_events_total'],
        'leaks_credited': result['overall']['credited'],
        'abrupt_credited': result['abrupt']['credited'],
        'abrupt_total': result['abrupt']['eligible_leaks'],
        'gradual_credited': result['incipient']['credited'],
        'median_delay_hours': result['overall']['median_delay_hours'],
        'outcomes': result['outcomes'],
        'credited_links': sorted(credited),
        'of_the_three_A_missed': [p for p in missed_by_a if p in credited],
    },
    'experiment_a': {
        'alert_events': a['alert_events'], 'leaks_credited': a['overall']['credited'],
        'abrupt_credited': a['abrupt']['credited'],
        'median_delay_hours': a['overall']['median_delay_hours'],
        'credited_links': sorted(a_credited),
    },
    'random_comparison_restricted_to_open_alert_hours': {
        'repeats': REPEATS,
        'median_credited': float(np.median(random_credits)),
        'p95_credited': float(np.percentile(random_credits, 95)),
        'max_credited': int(max(random_credits)),
        'median_abrupt_credited': float(np.median(random_abrupt)),
        'p95_abrupt_credited': float(np.percentile(random_abrupt, 95)),
        'real_credited': result['overall']['credited'],
        'real_abrupt_credited': result['abrupt']['credited'],
    },
    'per_leak': result['leaks'],
}
(OUT / 'realtime-results.json').write_text(json.dumps(report, indent=2) + '\n')
pd.DataFrame(result['leaks']).to_csv(OUT / 'realtime-leaks.csv', index=False)
pd.DataFrame(result['events']).to_csv(OUT / 'realtime-events.csv', index=False)
warnings.to_frame('new_rise_warning').assign(step=step, alert_open=alert_open) \
        .to_csv(OUT / 'realtime-warnings.csv', index_label='Timestamp')

print(f"threshold {THRESHOLD:.2f} m3/h  (median {np.median(calib):.2f} + 3 x {robust_sigma:.2f}, "
      f"from {len(calib)} calibration hours)")
print(f"\nwarnings issued: {n_warn}   (Experiment A raised {a['alert_events']} level alerts)")
print(f"leaks credited:  {result['overall']['credited']}/12   "
      f"abrupt {result['abrupt']['credited']}/{result['abrupt']['eligible_leaks']}   "
      f"gradual {result['incipient']['credited']}/{result['incipient']['eligible_leaks']}")
print(f"  credited: {sorted(credited)}")
print(f"  of the three A missed (p538, p866, p158): {[p for p in missed_by_a if p in credited]}")
print(f"median delay {result['overall']['median_delay_hours']} h  (Experiment A: {a['overall']['median_delay_hours']} h)")
print(f"outcomes {result['outcomes']}")
print(f"\nrandom, restricted to open-alert hours ({REPEATS} runs):")
print(f"  credited  median {np.median(random_credits):.1f}  95th {np.percentile(random_credits,95):.1f}"
      f"  max {max(random_credits)}   vs real {result['overall']['credited']}")
print(f"  abrupt    median {np.median(random_abrupt):.1f}  95th {np.percentile(random_abrupt,95):.1f}"
      f"   vs real {result['abrupt']['credited']}")
