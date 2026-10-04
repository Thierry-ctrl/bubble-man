"""Rerun the 2018 level-warning, new-rise and pressure comparisons with the frozen
replacement baseline. EXPLORATORY: these leaks have already been examined.

Both baselines run through identical code. The OLD baseline must reproduce the saved
results (checked by assertion) before any NEW number is reported. Warning rules, scorer
and pressure measures are unchanged. 2019 is not read.
"""
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'analysis/scorer'))
from leak_scorer import Rules, add_observed_activity, find_alerts, load_leaks, score  # noqa: E402

WINDOW = ('2018-01-15', '2018-12-31 23:00')
LEVEL_T, LEVEL_P = 10, 6
STEP_T, RECENT, BEFORE, GAP = 9.10, 6, 24, 24
RULES = Rules(gap_tolerance_hours=0, reporting_lag_hours=1.0, max_delay_hours=168)

def read(name):
    return pd.read_csv(ROOT / f'data/l-town/readings/{name}', sep=';', decimal=',',
                       parse_dates=['Timestamp']).set_index('Timestamp')

BASELINES = {
    'old': {'train': ('2018-01-08', '2018-01-14 23:00'),
            'group': lambda ix: np.where(ix.dayofweek >= 5, 'Sat+Sun', 'Mon-Fri')},
    'new': {'train': ('2018-01-01', '2018-01-14 23:00'),
            'group': lambda ix: np.where(ix.dayofweek == 5, 'Sat',
                                         np.where(ix.dayofweek == 4, 'Fri', 'Sun-Thu'))},
}

def residual(series, mode):
    spec = BASELINES[mode]
    frame = series.to_frame('v')
    frame['g'], frame['h'] = spec['group'](frame.index), frame.index.hour
    profile = frame.loc[spec['train'][0]:spec['train'][1]].groupby(['g', 'h'])['v'].median()
    return frame.v - pd.Series([profile.loc[(g, h)] for g, h in zip(frame.g, frame.h)], index=frame.index)

def step_of(resid):
    return resid.rolling(RECENT).mean() - resid.shift(RECENT).rolling(BEFORE).mean()

flows = read('2018_SCADA_Flows.csv').resample('h').mean()
main_out = flows.p227 + flows.p235 - flows.PUMP_1
pressure = read('2018_SCADA_Pressures.csv').resample('h').mean()
zones = pd.read_csv(ROOT / 'data/l-town/pressure-sensor-zones.csv').set_index('sensor').zone
sensors = list(zones[zones == 'main'].index)

leak_zones = dict(pd.read_csv(ROOT / 'analysis/scorer/leak-zones-from-network-map.csv')[['link', 'zone']].values)
cfg = load_leaks(ROOT / 'research/2026-09-21/battledim-config.yaml', leak_zones)
main_leaks = cfg[(cfg.start.dt.year == 2018) & (cfg.zone == 'main')].reset_index(drop=True)
main_leaks = add_observed_activity(main_leaks, ROOT / 'data/l-town/reference/2018_Leakages.csv')
truth = read('../reference/2018_Leakages.csv') if False else pd.read_csv(
    ROOT / 'data/l-town/reference/2018_Leakages.csv', sep=';', decimal=',',
    parse_dates=['Timestamp']).set_index('Timestamp')
main_flow = truth[list(main_leaks.link)].sum(axis=1).resample('h').mean().loc[WINDOW[0]:WINDOW[1]]
QUIET = main_flow[main_flow <= 0].index          # hours with no labelled main-zone leak flow

def rotate(values, k, index):
    return pd.Series(np.roll(values, k), index=index)

results = {}
for mode in ('old', 'new'):
    r = {}
    resid_full = residual(main_out, mode)
    step_full = step_of(resid_full)
    diff = resid_full.loc[WINDOW[0]:WINDOW[1]]
    step = step_full.loc[WINDOW[0]:WINDOW[1]]

    # ---------------- A. level warnings --------------------------------------
    above = diff > LEVEL_T
    level = score(above, LEVEL_P, main_leaks, RULES)
    events = pd.DataFrame(level['events'])
    sunday_events = int((pd.to_datetime(events.run_start).dt.dayofweek == 6).sum())
    alert_open = pd.Series(False, index=step.index)
    for e in find_alerts(above, LEVEL_P, Rules(gap_tolerance_hours=0)):
        alert_open.loc[e.issuable_at:e.end] = True
    quiet_false = sum(1 for e in level['events'] if e['outcome'] == 'false_alert'
                      and pd.Timestamp(e['run_start']) in set(QUIET))
    vals = above.to_numpy(); n = len(vals)
    rng = np.random.default_rng(20260929)
    free = [score(rotate(vals, int(rng.integers(1, n)), above.index), LEVEL_P, main_leaks, RULES)
            ['overall']['credited'] for _ in range(150)]
    rng = np.random.default_rng(20261004)
    weekly = [score(rotate(vals, int(rng.integers(1, n // 168)) * 168, above.index), LEVEL_P, main_leaks,
                    RULES)['overall']['credited'] for _ in range(150)]
    r['level'] = {
        'alert_events': level['alert_events_total'], 'events_starting_on_sunday': sunday_events,
        'share_of_hours_alert_open': round(float(alert_open.mean()), 4),
        'credited': level['overall']['credited'], 'abrupt': level['abrupt']['credited'],
        'gradual': level['incipient']['credited'], 'median_delay_h': level['overall']['median_delay_hours'],
        'outcomes': level['outcomes'],
        'false_alerts_in_no_labelled_new_leak_hours': quiet_false, 'exposure_hours': int(len(QUIET)),
        'random_free_rotation': {'median': float(np.median(free)), 'p95': float(np.percentile(free, 95))},
        'random_whole_week_rotation': {'median': float(np.median(weekly)), 'p95': float(np.percentile(weekly, 95))},
        'credited_links': sorted(x['link'] for x in level['leaks'] if x['outcome'] == 'credited'),
        'leaks': level['leaks'],
    }

    # ---------------- B. new-rise rule (during open level alerts) --------------
    warn = pd.Series(False, index=step.index); armed, last = True, None
    for t, v in step.items():
        if not np.isfinite(v): continue
        if v < STEP_T: armed = True; continue
        if not (armed and alert_open.loc[t]): continue
        if last is not None and (t - last) < pd.Timedelta(hours=GAP): continue
        warn.loc[t] = True; armed, last = False, t
    rise = score(warn, 1, main_leaks, RULES)
    cand = np.array([i for i, f in enumerate(alert_open) if f]); k = int(warn.sum())
    rng = np.random.default_rng(20261003); rc, ra, rd = [], [], []
    for _ in range(300):
        picked = []
        for pos in rng.permutation(cand):
            if all(abs(pos - p) >= GAP for p in picked):
                picked.append(pos)
                if len(picked) == k: break
        s = pd.Series(False, index=step.index); s.iloc[picked] = True
        o = score(s, 1, main_leaks, RULES)
        rc.append(o['overall']['credited']); ra.append(o['abrupt']['credited'])
        if o['overall']['median_delay_hours'] is not None: rd.append(o['overall']['median_delay_hours'])
    calib = step_full.loc['2018-01-02 05:00':'2018-01-14 23:00'].dropna()
    q1, q3 = np.percentile(calib, [25, 75])
    r['new_rise'] = {
        'warnings': k, 'sunday_warnings': int((warn[warn].index.dayofweek == 6).sum()),
        'warnings_per_week_of_open_alert': round(k / (alert_open.sum() / 168), 2) if alert_open.any() else None,
        'credited': rise['overall']['credited'], 'abrupt': rise['abrupt']['credited'],
        'gradual': rise['incipient']['credited'], 'median_delay_h': rise['overall']['median_delay_hours'],
        'of_the_three_old_A_missed': [p for p in ('p538', 'p866', 'p158')
                                      if p in {x['link'] for x in rise['leaks'] if x['outcome'] == 'credited'}],
        'random_restricted': {'median_credited': float(np.median(rc)), 'p95_credited': float(np.percentile(rc, 95)),
                              'abrupt_values': sorted(set(int(a) for a in ra)),
                              'share_abrupt_6': round(float(np.mean(np.array(ra) == 6)), 3),
                              'median_delay_h': round(float(np.median(rd)), 2) if rd else None,
                              'share_delay_as_fast': round(float(np.mean(np.array(rd) <= rise['overall']['median_delay_hours'])), 3)
                              if rd and rise['overall']['median_delay_hours'] is not None else None},
        'sensitivity_formula_threshold': round(float(np.median(calib) + 3 * (q3 - q1) / 1.349), 2),
    }
    sun11 = step[(step.index.dayofweek == 6) & (step.index.hour == 11)]
    r['sunday_11_step_share_at_least_9_10'] = round(float((sun11 >= STEP_T).mean()), 3)

    # ---------------- C. pressure study, frozen measures ----------------------
    big = step >= STEP_T
    runs = (big != big.shift()).cumsum()[big]
    refs = [g.idxmax() for _, g in step[big].groupby(runs)]
    p_step = pd.DataFrame({s: step_of(residual(pressure[s], mode)) for s in sensors})
    leaks_csv = pd.read_csv(ROOT / 'analysis/scorer/main-zone-leaks-A_reference_inherited.csv', parse_dates=['start', 'end'])
    rows = []
    for ref in refs:
        dq = float(step.loc[ref]); st = p_step.loc[ref]; med, low = float(st.median()), float(st.min())
        since = (ref - leaks_csv.start) / pd.Timedelta(hours=1)
        new12 = (since >= 0) & (since <= 12)
        lab = ('new abrupt leak' if (new12 & (leaks_csv.type == 'abrupt')).any() else
               'new gradual leak' if new12.any() else
               'no labelled new leak' if not ((since >= 0) & (since <= 72)).any() else 'unclear')
        leak = leaks_csv.link[new12 & (leaks_csv.type == 'abrupt')].iloc[0] if lab == 'new abrupt leak' else None
        rows.append({'ref': ref, 'dQ': dq, 'S': -med / dq, 'C': (med - low) / dq, 'label': lab, 'leak': leak})
    ep = pd.DataFrame(rows)
    ordin, cases = ep[ep.label == 'no labelled new leak'], ep[ep.label == 'new abrupt leak']
    case_rows = []
    for c in cases.itertuples():
        case_rows.append({'leak': c.leak, 'dQ': round(c.dQ, 2), 'S': round(c.S, 4), 'C': round(c.C, 4),
                          'dQ_pct': round(float((ordin.dQ < c.dQ).mean() * 100), 1),
                          'S_pct': round(float((ordin.S < c.S).mean() * 100), 1),
                          'C_pct': round(float((ordin.C < c.C).mean() * 100), 1)})
    above90 = lambda m: sum(1 for c in case_rows if c[f'{m}_pct'] > 90)
    large = ordin[ordin.dQ >= 20]
    r['pressure'] = {
        'episodes': len(ep), 'labels': ep.label.value_counts().to_dict(),
        'abrupt_onsets_with_episode': sorted(cases.leak.dropna()),
        'cases': case_rows,
        'cases_above_90th_on_S': above90('S'), 'cases_above_90th_on_C': above90('C'),
        'criterion_met': bool(above90('S') >= 5 or above90('C') >= 5),
        'large_ordinary_rises': int(len(large)),
        'large_ordinary_rises_on_sunday': int((large.ref.dt.dayofweek == 6).sum()),
    }
    ep.to_csv(OUT / f'pressure-episodes-{mode}.csv', index=False)
    results[mode] = r

# ---- reproduction checks: the old baseline must match the saved results -----
old = results['old']
assert old['level']['alert_events'] == 129 and old['level']['credited'] == 9, old['level']['alert_events']
assert old['level']['median_delay_h'] == 55.75, old['level']['median_delay_h']
assert old['new_rise']['warnings'] == 184 and old['new_rise']['credited'] == 12
assert old['pressure']['episodes'] == 213 and old['pressure']['cases_above_90th_on_C'] == 1
results['reproduction_check'] = 'old baseline reproduces saved results: 129 level alerts, 9/12, 55.75 h; 184 new-rise warnings, 12/12; 213 pressure episodes'

(OUT / 'before-after.json').write_text(json.dumps(results, indent=2, default=str) + '\n')
for mode in ('old', 'new'):
    L, N, P = results[mode]['level'], results[mode]['new_rise'], results[mode]['pressure']
    print(f"\n================ {mode.upper()} baseline ================")
    print(f"Sunday 11:00 steps >= 9.10: {results[mode]['sunday_11_step_share_at_least_9_10']:.0%}")
    print(f"LEVEL  events {L['alert_events']} (Sunday starts {L['events_starting_on_sunday']}), alert open {L['share_of_hours_alert_open']:.1%} of hours")
    print(f"       credited {L['credited']}/12  abrupt {L['abrupt']}/6  gradual {L['gradual']}/6  median delay {L['median_delay_h']} h  {L['credited_links']}")
    print(f"       false alerts in no-labelled-new-leak hours: {L['false_alerts_in_no_labelled_new_leak_hours']} over {L['exposure_hours']} h")
    print(f"       random free rotation median {L['random_free_rotation']['median']} p95 {L['random_free_rotation']['p95']} | whole-week median {L['random_whole_week_rotation']['median']} p95 {L['random_whole_week_rotation']['p95']}")
    print(f"NEWRISE warnings {N['warnings']} (Sunday {N['sunday_warnings']}), {N['warnings_per_week_of_open_alert']}/week open alert")
    print(f"       credited {N['credited']}/12  abrupt {N['abrupt']}/6  delay {N['median_delay_h']} h  three old-A misses credited: {N['of_the_three_old_A_missed']}")
    print(f"       random restricted: credited median {N['random_restricted']['median_credited']} p95 {N['random_restricted']['p95_credited']}, abrupt values {N['random_restricted']['abrupt_values']} (share 6: {N['random_restricted']['share_abrupt_6']}), delay median {N['random_restricted']['median_delay_h']}, share as fast {N['random_restricted']['share_delay_as_fast']}")
    print(f"       sensitivity: frozen formula on this baseline would give threshold {N['sensitivity_formula_threshold']}")
    print(f"PRESSURE episodes {P['episodes']} {P['labels']}  abrupt with episode {P['abrupt_onsets_with_episode']}")
    for c in P['cases']: print(f"       {c['leak']}: dQ {c['dQ']:6.2f} pct {c['dQ_pct']:5.1f} | S pct {c['S_pct']:5.1f} | C pct {c['C_pct']:5.1f}")
    print(f"       above 90th: S {P['cases_above_90th_on_S']}, C {P['cases_above_90th_on_C']}  -> criterion met: {P['criterion_met']}")
    print(f"       large ordinary rises {P['large_ordinary_rises']}, of which Sunday {P['large_ordinary_rises_on_sunday']}")
