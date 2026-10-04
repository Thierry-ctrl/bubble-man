"""Does pressure help tell a new sudden leak from an ordinary flow rise? 2018 only.

Implements COMPARISON-FROZEN.md exactly. Sections 1-3 use readings only; leak labels
enter only in section 4, after every measure has been computed. 2019 is not read.
"""
import json, math
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
RECENT, BEFORE, STEP_THRESHOLD = 6, 24, 9.10
WINDOW_FROM, WINDOW_TO = '2018-01-15', '2018-12-31 23:00'

def read(name):
    return pd.read_csv(ROOT / f'data/l-town/readings/{name}', sep=';', decimal=',',
                       parse_dates=['Timestamp']).set_index('Timestamp')

def residual_and_step(series):
    """Residual against the 8-14 January weekend/hour median, and the causal step."""
    frame = series.to_frame('v')
    frame['we'], frame['hr'] = frame.index.dayofweek >= 5, frame.index.hour
    profile = frame.loc['2018-01-08':'2018-01-14'].groupby(['we', 'hr'])['v'].median()
    resid = frame.v - pd.Series([profile.loc[(w, h)] for w, h in zip(frame.we, frame.hr)],
                                index=frame.index)
    return resid, resid.rolling(RECENT).mean() - resid.shift(RECENT).rolling(BEFORE).mean()

# ---------------- 1. readings only: flow episodes ---------------------------
flows = read('2018_SCADA_Flows.csv').resample('h').mean()
level = read('2018_SCADA_Levels.csv')['T1'].resample('h').last()
_, q_step = residual_and_step(flows.p227 + flows.p235 - flows.PUMP_1)
q_step = q_step.loc[WINDOW_FROM:WINDOW_TO]
above = q_step >= STEP_THRESHOLD
run_id = (above != above.shift()).cumsum()[above]
episodes = [group.idxmax() for _, group in q_step[above].groupby(run_id)]

# ---------------- 2. readings only: pressure steps --------------------------
zones = pd.read_csv(ROOT / 'data/l-town/pressure-sensor-zones.csv').set_index('sensor').zone
main_sensors = list(zones[zones == 'main'].index)
pressure = read('2018_SCADA_Pressures.csv').resample('h').mean()
p_step = pd.DataFrame({s: residual_and_step(pressure[s])[1] for s in main_sensors})
_, pump_step = residual_and_step(flows.PUMP_1)

# ---------------- 3. readings only: the frozen measures ---------------------
rows = []
for ref in episodes:
    dq = float(q_step.loc[ref])
    steps = p_step.loc[ref]
    med, low = float(steps.median()), float(steps.min())
    rows.append({'reference_hour': ref, 'dQ': dq, 'dP_med': med, 'dP_min': low,
                 'worst_sensor': steps.idxmin(), 'S': -med / dq, 'C': (med - low) / dq,
                 'pump_step': float(pump_step.loc[ref]),
                 'tank_level_change_6h': float(level.loc[ref] - level.loc[ref - pd.Timedelta(hours=RECENT)])})
table = pd.DataFrame(rows)

# ---------------- 4. evaluation only: labels applied afterwards -------------
leaks = pd.read_csv(ROOT / 'analysis/scorer/main-zone-leaks-A_reference_inherited.csv',
                    parse_dates=['start', 'end'])          # 'start' = first positive flow
def label(ref):
    since = (ref - leaks.start) / pd.Timedelta(hours=1)
    if ((since >= 0) & (since <= 12) & (leaks.type == 'abrupt')).any():
        return 'new abrupt leak', leaks.link[(since >= 0) & (since <= 12) & (leaks.type == 'abrupt')].iloc[0]
    if ((since >= 0) & (since <= 12)).any():
        return 'new gradual leak', leaks.link[(since >= 0) & (since <= 12)].iloc[0]
    if not ((since >= 0) & (since <= 72)).any():
        return 'no labelled new leak', None
    return 'unclear', None
table[['label', 'leak']] = [label(r) for r in table.reference_hour]
table['leaks_running'] = [int(((leaks.start <= r) & (leaks.end >= r)).sum()) for r in table.reference_hour]

ordinary = table[table.label == 'no labelled new leak']
cases = table[table.label == 'new abrupt leak'].copy()
for m in ('dQ', 'S', 'C'):
    cases[f'{m}_pct'] = [round(float((ordinary[m] < v).mean() * 100), 1) for v in cases[m]]

# the p673 pair: the large rise on 4 March, before onset, and the rise after onset
pair = table[(table.reference_hour >= '2018-03-04') & (table.reference_hour <= '2018-03-06 12:00')]

counts = table.label.value_counts().to_dict()
summary = {
    'definition': 'COMPARISON-FROZEN.md (committed before this ran)',
    'main_zone_sensors': len(main_sensors), 'episodes': len(table), 'labels': counts,
    'abrupt_onsets_with_an_episode': sorted(cases.leak.tolist()),
    'ordinary_rises_percentiles': {m: {f'p{q}': round(float(np.percentile(ordinary[m], q)), 4)
                                       for q in (50, 90)} for m in ('dQ', 'S', 'C')},
    'cases': cases[['leak', 'reference_hour', 'dQ', 'S', 'C', 'dQ_pct', 'S_pct', 'C_pct',
                    'pump_step', 'tank_level_change_6h', 'leaks_running', 'worst_sensor']]
             .assign(reference_hour=lambda d: d.reference_hour.astype(str)).round(4).to_dict('records'),
    'p673_pair': pair.assign(reference_hour=lambda d: d.reference_hour.astype(str))
                    .round(4).to_dict('records'),
    'operating_check': {
        'ordinary_rises_with_pump_step_over_5': int((ordinary.pump_step.abs() > 5).sum()),
        'abrupt_cases_with_pump_step_over_5': int((cases.pump_step.abs() > 5).sum())},
}
(OUT / 'pressure-results.json').write_text(json.dumps(summary, indent=2, default=str) + '\n')
table.to_csv(OUT / 'episodes.csv', index=False)

print(f"episodes: {len(table)}   labels: {counts}")
print(f"abrupt onsets that produced an episode: {sorted(cases.leak)}")
print(f"\nordinary rises (n={len(ordinary)}):  median / 90th pct")
for m in ('dQ', 'S', 'C'):
    print(f"   {m:3s} {np.percentile(ordinary[m],50):8.4f} / {np.percentile(ordinary[m],90):8.4f}")
print("\nabrupt cases — percentile among ordinary rises")
print(cases[['leak','reference_hour','dQ','S','C','dQ_pct','S_pct','C_pct','pump_step','leaks_running']]
      .round(3).to_string(index=False))
print("\np673 pair:")
print(pair[['reference_hour','label','dQ','dP_med','dP_min','S','C','pump_step','tank_level_change_6h']]
      .round(3).to_string(index=False))
