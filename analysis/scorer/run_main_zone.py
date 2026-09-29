"""Main-zone evaluation: two experiments with rules frozen before any scoring.

SIGNAL (boundary-correct, see WATER-ACCOUNTING.md)
    main-zone outflow = p227 + p235 - PUMP_1, hourly means, m3/h

TIMING
    An hourly value covering [H, H+1) is complete at H+1:00, and the storage term for
    that hour needs the level reading at H+1:00. So nothing is known before H+1:00,
    which is exactly `reporting_lag_hours = 1.0`. No future information is used.

EXPERIMENT A - reference, inherited settings, nothing recalibrated
    baseline profile : median by (weekend, hour) over 8-14 January
    threshold        : 10 m3/h   (inherited; NOT chosen for this signal)
    persistence      : 6 hours

EXPERIMENT B - separately calibrated, using only data before 15 January
    baseline profile : median by (weekend, hour) over 1-7 January
    threshold        : the 99th percentile of the hourly difference over 8-14 January,
                       a week with no main-zone leak and not used to fit this baseline
    persistence      : 6 hours, held equal to A so only the threshold differs

CALIBRATION DISCIPLINE
    15-23 January is the only main-zone leak-free stretch inside the evaluation window.
    It is NOT used to fit a baseline or pick a threshold. It is reserved as quiet
    evaluation data for counting false alerts against a known exposure time.
    No setting was chosen by looking at evaluation results.
"""
import json, math, sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from leak_scorer import Rules, load_leaks, score  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
TANK_AREA = math.pi * (16.0 / 2) ** 2
PERSISTENCE = 6
WINDOW_FROM, WINDOW_TO = '2018-01-15', '2018-12-31 23:00'
QUIET_FROM, QUIET_TO = '2018-01-15', '2018-01-23 22:00'

flows = pd.read_csv(ROOT / 'data/l-town/readings/2018_SCADA_Flows.csv', sep=';', decimal=',',
                    parse_dates=['Timestamp']).set_index('Timestamp')
level = pd.read_csv(ROOT / 'data/l-town/readings/2018_SCADA_Levels.csv', sep=';', decimal=',',
                    parse_dates=['Timestamp']).set_index('Timestamp')['T1']
assert flows.index.equals(level.index), 'flow and level timestamps must align'

hourly = flows.resample('h').mean()
hourly['main_out'] = hourly.p227 + hourly.p235 - hourly.PUMP_1
hourly['weekend'] = hourly.index.dayofweek >= 5
hourly['hour'] = hourly.index.hour
assert hourly.main_out.notna().all()

zones = dict(pd.read_csv(OUT / 'leak-zones-from-network-map.csv')[['link', 'zone']].values)
leaks = load_leaks(ROOT / 'research/2026-09-21/battledim-config.yaml', zones)
main_leaks = leaks[(leaks.start.dt.year == 2018) & (leaks.zone == 'main')].reset_index(drop=True)
assert len(main_leaks) == 12, f'expected 12 main-zone leaks, got {len(main_leaks)}'

RULES = Rules(gap_tolerance_hours=0, reporting_lag_hours=1.0, max_delay_hours=168)


def difference(profile_from, profile_to):
    profile = hourly.loc[profile_from:profile_to].groupby(['weekend', 'hour'])['main_out'].median()
    assert len(profile) == 48, 'profile week must cover every hour and both day types'
    index = hourly.loc[WINDOW_FROM:WINDOW_TO].index
    expected = pd.Series([profile.loc[(w, h)] for w, h in
                          zip(hourly.loc[index].weekend, hourly.loc[index].hour)], index=index)
    return hourly.loc[index, 'main_out'] - expected, profile


# ---- Experiment A: inherited ------------------------------------------------
diff_a, _ = difference('2018-01-08', '2018-01-14')
THRESHOLD_A = 10.0

# ---- Experiment B: calibrated on 8-14 Jan only ------------------------------
profile_b = hourly.loc['2018-01-01':'2018-01-07'].groupby(['weekend', 'hour'])['main_out'].median()
calib = hourly.loc['2018-01-08':'2018-01-14']
calib_diff = calib['main_out'] - pd.Series(
    [profile_b.loc[(w, h)] for w, h in zip(calib.weekend, calib.hour)], index=calib.index)
THRESHOLD_B = float(np.percentile(calib_diff, 99))
assert calib.index.max() < pd.Timestamp(QUIET_FROM), 'calibration must end before the quiet window'
diff_b, _ = difference('2018-01-01', '2018-01-07')

EXPERIMENTS = {
    'A_reference_inherited': (diff_a, THRESHOLD_A, '8-14 Jan', 'inherited 10 m3/h'),
    'B_calibrated': (diff_b, THRESHOLD_B, '1-7 Jan', '99th pct of 8-14 Jan difference'),
}

rng = np.random.default_rng(20260929)
report = {}
for name, (diff, threshold, profile_week, how) in EXPERIMENTS.items():
    above = diff > threshold
    result = score(above, PERSISTENCE, main_leaks, RULES)

    quiet = above.loc[QUIET_FROM:QUIET_TO]
    quiet_hours = len(quiet)
    quiet_events = [e for e in result['events']
                    if pd.Timestamp(QUIET_FROM) <= pd.Timestamp(e['run_start']) <= pd.Timestamp(QUIET_TO)]
    quiet_false = [e for e in quiet_events if e['outcome'] == 'false_alert']

    values = above.to_numpy()
    random_credits = [score(pd.Series(np.roll(values, int(rng.integers(1, len(values)))),
                                      index=above.index), PERSISTENCE, main_leaks, RULES)['overall']['credited']
                      for _ in range(150)]

    report[name] = {
        'baseline_profile_week': profile_week, 'threshold_m3_per_hour': round(threshold, 3),
        'threshold_chosen_by': how, 'persistence_hours': PERSISTENCE,
        'alert_events': result['alert_events_total'], 'outcomes': result['outcomes'],
        'overall': result['overall'], 'abrupt': result['abrupt'], 'incipient': result['incipient'],
        'quiet_window': [QUIET_FROM, QUIET_TO], 'quiet_exposure_hours': quiet_hours,
        'quiet_exposure_days': round(quiet_hours / 24, 2),
        'false_alerts_in_quiet_window': len(quiet_false),
        'false_alerts_whole_window': result['outcomes']['false_alert'],
        'random_credited_median': float(np.median(random_credits)),
        'random_credited_p95': float(np.percentile(random_credits, 95)),
        'leaks': result['leaks'],
    }
    pd.DataFrame(result['leaks']).to_csv(OUT / f'main-zone-leaks-{name}.csv', index=False)
    pd.DataFrame(result['events']).to_csv(OUT / f'main-zone-events-{name}.csv', index=False)

report['area_c'] = {
    'status': 'NOT EVALUABLE for false alerts in this window',
    'reason': 'zero leak-free hours between 2018-01-15 and 2018-12-31; p257 runs throughout',
    'leaks_2018': ['p257 (incipient, from 8 Jan, before the window)', 'p31 (incipient, 28 Jun - 12 Aug)'],
}
(OUT / 'main-zone-report.json').write_text(json.dumps(report, indent=2) + '\n')

for name in EXPERIMENTS:
    r = report[name]
    print(f"\n=== {name} ===")
    print(f"  baseline week {r['baseline_profile_week']}, threshold {r['threshold_m3_per_hour']} m3/h "
          f"({r['threshold_chosen_by']}), persistence {PERSISTENCE} h")
    print(f"  alert events {r['alert_events']}")
    print(f"  associations credited {r['overall']['credited']}/{r['overall']['eligible_leaks']}"
          f"   abrupt {r['abrupt']['credited']}/{r['abrupt']['eligible_leaks']}"
          f"   gradual {r['incipient']['credited']}/{r['incipient']['eligible_leaks']}"
          f"   ambiguous {r['overall']['ambiguous']}")
    print(f"  median delay {r['overall']['median_delay_hours']} h")
    print(f"  outcomes {r['outcomes']}")
    print(f"  false alerts in quiet window: {r['false_alerts_in_quiet_window']} "
          f"over {r['quiet_exposure_days']} days ({r['quiet_exposure_hours']} h exposure)")
    print(f"  randomly-timed warnings credit {r['random_credited_median']:.1f} (95th {r['random_credited_p95']:.1f})")
