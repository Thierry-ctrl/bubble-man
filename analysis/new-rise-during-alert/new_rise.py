"""Can we spot a NEW rise in flow while a high-flow warning is already open?

MOTIVATION
    Leak p673 began while alert run #26 had already been above threshold for 34 hours.
    The level-based rule could not mark a new event, so the warning for p673 arrived
    94 hours late (analysis/scorer/walkthrough-p673/WALKTHROUGH.md). This asks whether
    a simple measure of CHANGE, rather than level, would have seen it.

METHOD — declared before any result was examined, and not tuned afterwards
    Signal      main-zone outflow p227 + p235 - PUMP_1, hourly, m3/h.
    Difference  observed minus the Experiment A baseline (median by weekend x hour,
                8-14 January). Identical to Experiment A; nothing changed.
    Step        step(t) = mean(difference over hours t-5..t)
                        - mean(difference over hours t-29..t-6)
                A recent 6-hour window against the 24 hours before it. Strictly causal:
                every hour used is complete by t, so the value is available at t+1.
    Alert open  an Experiment A alert run is active at t, i.e. issuable_at <= t <= run end.
    CASE        for each abrupt main-zone leak, the largest step in the 12 hours from
                first positive flow. Only leaks whose onset falls inside an open alert
                answer the question being asked.
    CONTROL     hours when an alert was open AND no main-zone leak of any kind began
                within +/- 72 hours. These are the "nothing new happened" hours.

    LIKE FOR LIKE  A case is the MAXIMUM step over 12 hours, so it must be compared with
                the maximum over 12 control hours, not with single control hours. The
                first version of this script compared max-of-12 against single hours and
                flattered the measure by 5-8 percentile points. Both are reported.

    Leak labels are used ONLY to pick cases and to exclude controls, never as input to
    the step measure. The measure itself sees flow and the January baseline, nothing else.

NOT DONE HERE
    No threshold is selected, no rule is added to the detector, and the scorer and its
    results are untouched. 2019 is not read.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'analysis/scorer'))
from leak_scorer import Rules, find_alerts  # noqa: E402  (read-only import)

RECENT, BEFORE = 6, 24          # hours in the two comparison windows
CASE_WINDOW = 12                # hours after onset in which to look for the step
QUIET_MARGIN = 72               # hours either side of any onset that controls must avoid
THRESHOLD, PERSISTENCE = 10, 6  # Experiment A, unchanged

flows = pd.read_csv(ROOT / 'data/l-town/readings/2018_SCADA_Flows.csv', sep=';', decimal=',',
                    parse_dates=['Timestamp']).set_index('Timestamp')
hourly = flows.resample('h').mean()
hourly['main_out'] = hourly.p227 + hourly.p235 - hourly.PUMP_1
hourly['weekend'] = hourly.index.dayofweek >= 5
hourly['hour'] = hourly.index.hour
profile = hourly.loc['2018-01-08':'2018-01-14'].groupby(['weekend', 'hour'])['main_out'].median()
index = hourly.loc['2018-01-15':'2018-12-31 23:00'].index
expected = pd.Series([profile.loc[(w, h)] for w, h in
                      zip(hourly.loc[index].weekend, hourly.loc[index].hour)], index=index)
diff = hourly.loc[index, 'main_out'] - expected

# ---- the step measure, strictly causal -------------------------------------
recent = diff.rolling(RECENT).mean()
before = diff.shift(RECENT).rolling(BEFORE).mean()
step = (recent - before).dropna()
assert step.index.min() >= index.min() + pd.Timedelta(hours=RECENT + BEFORE - 1)

# ---- which hours had an alert already open ---------------------------------
alerts = find_alerts(diff > THRESHOLD, PERSISTENCE, Rules(gap_tolerance_hours=0))
alert_open = pd.Series(False, index=step.index)
for event in alerts:
    alert_open.loc[event.issuable_at:event.end] = True

# ---- leak labels: used only to choose cases and exclude controls ------------
leaks = pd.read_csv(ROOT / 'analysis/scorer/main-zone-leaks-A_reference_inherited.csv',
                    parse_dates=['start'])
onsets = leaks.start
abrupt = leaks[leaks.type == 'abrupt']

near_any_onset = pd.Series(False, index=step.index)
for onset in onsets:
    near_any_onset.loc[onset - pd.Timedelta(hours=QUIET_MARGIN):
                       onset + pd.Timedelta(hours=QUIET_MARGIN)] = True

control_mask = alert_open & ~near_any_onset
controls = step[control_mask]

# like-for-like: 12-hour maxima over blocks lying wholly inside the control mask
rolling_max = step.rolling(CASE_WINDOW).max()
whole_block = control_mask.rolling(CASE_WINDOW).min().astype(float) == 1
control_blocks = rolling_max[whole_block.fillna(False)]

cases = []
for leak in abrupt.itertuples():
    window = step.loc[leak.start:leak.start + pd.Timedelta(hours=CASE_WINDOW)]
    if window.empty:
        continue
    peak_at = window.idxmax()
    cases.append({
        'link': leak.link, 'onset': str(leak.start),
        'alert_already_open_at_onset': bool(alert_open.loc[:leak.start].iloc[-1]),
        'max_step_m3_per_hour': round(float(window.max()), 2),
        'peak_at': str(peak_at),
        'hours_after_onset': round((peak_at - leak.start).total_seconds() / 3600, 2),
        'percentile_among_control_hours_UNFAIR': round(float((controls < window.max()).mean() * 100), 2),
        'percentile_among_control_12h_blocks': round(float((control_blocks < window.max()).mean() * 100), 2),
        'scorer_outcome_experiment_A': leak.outcome,
    })

during_open = [c for c in cases if c['alert_already_open_at_onset']]
smallest = min((c['max_step_m3_per_hour'] for c in during_open), default=None)
report = {
    'question': 'Can a simple measure of CHANGE flag a new rise while a level alert is open?',
    'method': {'recent_hours': RECENT, 'before_hours': BEFORE, 'case_window_hours': CASE_WINDOW,
               'control_margin_hours': QUIET_MARGIN, 'threshold': THRESHOLD,
               'persistence': PERSISTENCE, 'labels_used_for': 'case selection and control exclusion only'},
    'counts': {
        'hours_scored': int(len(step)),
        'hours_with_an_alert_open': int(alert_open.sum()),
        'share_of_hours_with_alert_open': round(float(alert_open.mean()), 4),
        'control_hours': int(len(controls)),
        'abrupt_leaks_examined': len(cases),
        'of_those_with_an_alert_already_open': len(during_open),
    },
    'control_step_distribution_single_hours': {f'p{q}': round(float(np.percentile(controls, q)), 2)
                                               for q in (50, 75, 90, 95, 99)},
    'control_step_distribution_12h_blocks': {f'p{q}': round(float(np.percentile(control_blocks, q)), 2)
                                             for q in (50, 75, 90, 95, 99)},
    'control_blocks_counted': int(len(control_blocks)),
    'control_max': round(float(controls.max()), 2),
    'step_at_gradual_onsets': {l.link: round(float(step.loc[l.start:l.start + pd.Timedelta(
        hours=CASE_WINDOW)].max()), 2) for l in leaks[leaks.type == 'incipient'].itertuples()},
    'cases': cases,
}
weeks_open = control_mask.sum() / 168
sweep = []
for level in (smallest, 20, 25, 30):
    if level is None:
        continue
    firing = (step >= level) & control_mask
    episodes = (firing != firing.shift()).cumsum()[firing].nunique()
    sweep.append({'threshold_m3_per_hour': round(float(level), 2),
                  'abrupt_leaks_reached': sum(1 for c in during_open
                                              if c['max_step_m3_per_hour'] >= level),
                  'control_episodes': int(episodes),
                  'control_episodes_per_week_of_open_alert': round(episodes / weeks_open, 2)})
report['threshold_sweep_NOT_a_selection'] = sweep
report['control_weeks_of_open_alert'] = round(float(weeks_open), 1)
(OUT / 'new-rise-results.json').write_text(json.dumps(report, indent=2) + '\n')
step.to_frame('step_m3_per_hour').assign(alert_open=alert_open, difference=diff.reindex(step.index)) \
    .to_csv(OUT / 'step-series.csv', index_label='Timestamp')

print(json.dumps({k: report[k] for k in
                  ('counts', 'control_step_distribution_12h_blocks',
                   'step_at_gradual_onsets')}, indent=2))
print('\ncases:')
for c in cases:
    print(f"  {c['link']:5s} onset {c['onset'][:16]}  alert already open: "
          f"{str(c['alert_already_open_at_onset']):5s}  max step {c['max_step_m3_per_hour']:7.2f} "
          f"at +{c['hours_after_onset']:5.1f} h  -> {c['percentile_among_control_12h_blocks']:5.1f}th pct "
          f"of 12-h control blocks  [{c['scorer_outcome_experiment_A']}]")
print('\nthreshold sweep (reported, NOT selected):')
for row in sweep:
    print(f"  {row['threshold_m3_per_hour']:6.2f} m3/h -> reaches {row['abrupt_leaks_reached']}/6 leaks, "
          f"{row['control_episodes']:3d} control episodes "
          f"({row['control_episodes_per_week_of_open_alert']:.2f} per week of open alert)")
