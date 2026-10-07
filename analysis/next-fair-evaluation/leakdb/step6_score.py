"""Protocol step 6: score the committed warnings once. Q1 and Q2 reported separately."""
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import scoring as S

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / 'run'
W = pd.read_csv(OUT / 'warnings-all-runs.csv')
A = pd.read_csv(OUT / 'scenarios-assessability.csv')
L = pd.read_csv(OUT / 'leaks-table.csv', parse_dates=['start', 'end'])
q2_prev = json.loads((OUT / 'step4-warnings.json').read_text())['Q2']
TALLY = ('credited', 'false_alert', 'unattributable', 'repeat_of_credited_leak',
         'coincides_with_excluded_leak', 'retrospective_association', 'issuable_after_window')

def scen_inputs(rows, run):
    out = []
    for r in rows.itertuples():
        day0 = pd.Timestamp(r.day0)
        out.append({'scenario': r.scenario, 'day0': day0, 'ns': int(r.night_start_hour), 'threshold': r.threshold,
                    'warn_days': sorted(W[(W.scenario == r.scenario) & (W.run == run)].day_index.tolist()),
                    'leaks': L[(L.scenario == r.scenario) & L.start.notna()]})
    return out

def evaluate(scen, last_day=364, leak_fn=None):
    tot = {k: 0 for k in TALLY}; ab = inc = {'eligible': 0, 'credited': 0}
    ab, inc, delays, n_warn, fa_exposure, per = dict(ab), dict(inc), [], 0, 0, []
    for s in scen:
        lk = leak_fn(s) if leak_fn else s['leaks']
        r = S.score_scenario(s['warn_days'], s['day0'], s['ns'], lk, last_day=last_day)
        for k in TALLY: tot[k] += r['outcomes'][k]
        ab['eligible'] += r['abrupt']['eligible_leaks']; ab['credited'] += r['abrupt']['credited']
        inc['eligible'] += r['incipient']['eligible_leaks']; inc['credited'] += r['incipient']['credited']
        delays += [x['delay_hours_from_first_flow'] for x in r['leaks'] if x['outcome'] == 'credited']
        n_warn += r['alert_events_total']
        hours = pd.date_range(s['day0'] + pd.Timedelta(days=S.WARN_FROM), s['day0'] + pd.Timedelta(days=last_day, hours=23), freq='h')
        fa_exposure += int((~S.flowing_hours(lk, hours)).sum())
        per.append({'scenario': s['scenario'], 'warnings': r['alert_events_total'], **{k: r['outcomes'][k] for k in TALLY},
                    'abrupt_eligible': r['abrupt']['eligible_leaks'], 'abrupt_credited': r['abrupt']['credited'],
                    'incipient_eligible': r['incipient']['eligible_leaks'], 'incipient_credited': r['incipient']['credited']})
    cred = tot['credited']
    return {'warnings_total_all_investigations': n_warn, 'outcomes': tot, 'credited': cred,
            'investigations_without_a_new_eligible_leak': n_warn - cred,
            'yield': round(cred / n_warn, 4) if n_warn else None,
            'abrupt': ab, 'incipient': inc,
            'median_delay_hours_credited': float(np.median(delays)) if delays else None,
            'false_alerts': tot['false_alert'], 'false_alert_exposure_hours_no_leak_flowing': fa_exposure}, per

def criteria(ev, shift):
    e1 = ev['abrupt']['eligible'] >= 20; e2 = shift['p_abrupt'] <= 0.05
    e3 = ev['yield'] is not None and ev['yield'] >= 0.5
    verdict = ('INCONCLUSIVE' if not e1 else
               'PROMISING ON LEAKDB HANOI UNDER AN EXPLORATORY TRANSFER TEST' if (e2 and e3) else 'FAIL')
    return {'E1_eligible_abrupt': ev['abrupt']['eligible'], 'E1_met': e1, 'E2_p_abrupt': round(shift['p_abrupt'], 4),
            'E2_met': e2, 'E3_yield': ev['yield'], 'E3_met': e3, 'verdict': verdict}

# ---------------- Q1 -------------------------------------------------------------------
ok = A[A.q1_assessable]
scen = scen_inputs(ok, 'Q1_selfaligning_plain')
q1, per = evaluate(scen)
shift, sh = S.shift_comparison(scen)
day365 = int(sum(sum(d == 364 for d in s['warn_days']) for s in scen))
not_ass = A[~A.q1_assessable]
q1_res = {'criteria': criteria(q1, shift), 'full_window': q1, 'shift_comparison': shift,
          'real_warnings_on_day_365_outside_shift_domain': day365,
          'not_assessable': {'scenarios': len(not_ass),
                             'their_leaks': L[L.scenario.isin(not_ass.scenario)].type.value_counts().to_dict()},
          'leak_records_never_flowed': int(L.never_flowed.sum())}

# early-leak sensitivity (reported, does not change the verdict)
first = L.dropna(subset=['start']).groupby('scenario').start.min()
d0 = dict(zip(A.scenario, pd.to_datetime(A.day0)))
first_day = {k: (t - d0[k]) / pd.Timedelta(days=1) for k, t in first.items()}
early = {k for k, d in first_day.items() if d < S.WARN_FROM}
early_profile = {k for k in early if first_day[k] < 14}
clean_T = ok[~ok.scenario.isin(early)].threshold.median()
E = ok[ok.scenario.isin(early)]
scen_clean = [s for s in scen if s['scenario'] not in early]
q1c, _ = evaluate(scen_clean); shc, _ = S.shift_comparison(scen_clean)
P = pd.DataFrame(per)
q1_res['early_leak_sensitivity'] = {
    'assessable_scenarios_with_leak_before_day_29': int(len(E)),
    'of_which_first_flow_in_days_1_14': int(E.scenario.isin(early_profile).sum()),
    'of_which_first_flow_in_days_15_28': int((~E.scenario.isin(early_profile)).sum()),
    'threshold_ratio_to_clean_median': (E.threshold / clean_T).describe().round(3).to_dict() if len(E) else None,
    'their_warnings_by_outcome': P[P.scenario.isin(early)][['warnings', *TALLY]].sum().to_dict(),
    'their_eligible_abrupt': int(P[P.scenario.isin(early)].abrupt_eligible.sum()),
    'criteria_without_them': criteria(q1c, shc)}

# ---------------- Q2 (reported; verdict already fixed label-free in step 4) -------------
ex = A[A.q2_exercised]
q2_runs = {}
for run, stressed in (('Q1_selfaligning_plain', False), ('Q2_calendar_plain', False),
                      ('Q2_selfaligning_stress', True), ('Q2_calendar_stress', True)):
    sc = scen_inputs(ex, run)
    ev, _ = evaluate(sc, last_day=365 if stressed else 364,
                     leak_fn=lambda s, st=stressed: S.leaks_for_stress(s['leaks'], s['day0'], st))
    q2_runs[run] = {k: ev[k] for k in ('warnings_total_all_investigations', 'credited', 'yield', 'abrupt', 'incipient')}
q2_res = {'label_free_verdict_from_step4': q2_prev['verdict'], 'label_free_measures': q2_prev,
          'after_labels_reported_not_judged': q2_runs}

res = {'Q1_network_transfer': q1_res, 'Q2_controlled_weekly_slip': q2_res}
(OUT / 'step6-results.json').write_text(json.dumps(res, indent=2, default=str) + '\n')
P.to_csv(OUT / 'per-scenario-q1.csv', index=False); sh.to_csv(OUT / 'shifts-q1.csv', index=False)
print(json.dumps(res, indent=2, default=str))
