"""Step 5: score once, both rules, prospective timing rule (prospective.py). Report all."""
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import prospective as P
import rules as R
import io1000
ROOT = HERE.parents[2]
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / 'run'
DATA = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / 'data/leakdb'
W = pd.read_csv(OUT / 'warnings-both-rules.csv'); A = pd.read_csv(OUT / 'scenarios-assessability.csv')
L = pd.read_csv(OUT / 'leaks-table.csv', parse_dates=['start', 'end'])
L['never_flowed'] = L.never_flowed.astype(str) == 'True'
OK = A[A.assessable]
OLDER = ('unattributable', 'coincides_with_excluded_leak', 'retrospective_association', 'repeat_of_credited_leak')

def inputs(rule, scen_ids):
    out = []
    for r in OK[OK.scenario.isin(scen_ids)].itertuples():
        out.append({'scenario': r.scenario, 'day0': pd.Timestamp(r.day0).normalize(), 'ns': int(r.night_start_hour),
                    'warn_days': sorted(W[(W.scenario == r.scenario) & (W.rule == rule)].day_index.tolist()),
                    'leaks': L[(L.scenario == r.scenario) & ~L.never_flowed]})
    return out

def evaluate(rule, scen_ids):
    sc = inputs(rule, scen_ids)
    tot = {o: 0 for o in P.OUTCOMES}; ab = [0, 0]; inc = [0, 0]; dab, dinc = [], []; fe = 0.0; per, leaks, events = [], [], []
    for s in sc:
        r = P.score(s['warn_days'], s['day0'], s['ns'], s['leaks'])
        for o in P.OUTCOMES: tot[o] += r['outcomes'][o]
        ab[0] += r['abrupt']['eligible']; ab[1] += r['abrupt']['credited']
        inc[0] += r['incipient']['eligible']; inc[1] += r['incipient']['credited']
        dab += [p['delay_h'] for p in r['leaks'] if p['outcome'] == 'credited' and p['type'] == 'abrupt']
        dinc += [p['delay_h'] for p in r['leaks'] if p['outcome'] == 'credited' and p['type'] == 'incipient']
        fe += P.leak_free_hours(s['leaks'], s['day0'])
        per.append({'scenario': s['scenario'], 'warnings': r['warnings'], **r['outcomes'],
                    'abrupt_eligible': r['abrupt']['eligible'], 'abrupt_found': r['abrupt']['credited'],
                    'incipient_eligible': r['incipient']['eligible'], 'incipient_found': r['incipient']['credited']})
        leaks += [{'scenario': s['scenario'], **p} for p in r['leaks']]
        events += [{'scenario': s['scenario'], **e} for e in r['events']]
    n = sum(len(s['warn_days']) for s in sc); c = tot['credited']
    shift, sh = P.shift_comparison(sc)
    return {'warnings_all_investigations': n, 'outcomes': tot,
            'warnings_no_leak_flowing': tot['false_alert'], 'warnings_during_an_older_leak': sum(tot[o] for o in OLDER),
            'credited': c, 'without_a_new_eligible_leak': n - c, 'yield': round(c / n, 4) if n else None,
            'abrupt': {'eligible': ab[0], 'found': ab[1], 'rate': round(ab[1] / ab[0], 4) if ab[0] else None,
                       'median_delay_h': float(np.median(dab)) if dab else None},
            'incipient': {'eligible': inc[0], 'found': inc[1], 'rate': round(inc[1] / inc[0], 4) if inc[0] else None,
                          'median_delay_h': float(np.median(dinc)) if dinc else None},
            'false_alerts': tot['false_alert'], 'leak_free_hours': fe, 'shift': shift}, per, leaks, events, sh

def criteria(ad, fz):
    g1 = ad['abrupt']['eligible'] >= 20
    g2 = ad['shift']['p_abrupt'] <= 0.05
    g3 = ad['abrupt']['rate'] is not None and ad['abrupt']['rate'] >= fz['abrupt']['rate'] - 0.05
    g4 = ad['without_a_new_eligible_leak'] <= 0.5 * fz['without_a_new_eligible_leak']
    g5 = ad['yield'] is not None and ad['yield'] >= 0.5
    v = ('INCONCLUSIVE' if not g1 else
         'PROMISING ON HELD-OUT LEAKDB SIMULATIONS' if (g2 and g3 and g4 and g5) else
         'IMPROVED, BUT BELOW THE PRACTICAL TARGET' if (g2 and g3 and g4) else
         'THE ADAPTIVE THRESHOLD DID NOT HOLD UP ON NEW SIMULATIONS')
    return {'G1_eligible_abrupt': ad['abrupt']['eligible'], 'G1': g1,
            'G2_p_abrupt': round(ad['shift']['p_abrupt'], 4), 'G2': g2,
            'G3_abrupt_rate_adaptive_vs_frozen': [ad['abrupt']['rate'], fz['abrupt']['rate']], 'G3': g3,
            'G4_without_new_leak_adaptive_vs_frozen': [ad['without_a_new_eligible_leak'], fz['without_a_new_eligible_leak']], 'G4': g4,
            'G5_yield': ad['yield'], 'G5': g5, 'verdict': v}

ids = set(OK.scenario)
fz, pf, lf, ef, shf = evaluate('frozen', ids)
ad, pa, la, ea, sha = evaluate('adaptive', ids)
res = {'criteria': criteria(ad, fz), 'adaptive': ad, 'frozen': fz,
       'not_assessable': {'scenarios': int((~A.assessable).sum()),
                          'their_leaks': L[L.scenario.isin(A[~A.assessable].scenario)].type.value_counts().to_dict()},
       'leak_records_never_flowed': int(L.never_flowed.sum())}

# per scenario
Pf, Pa = pd.DataFrame(pf), pd.DataFrame(pa)
q = lambda s: {str(k): float(v) for k, v in s.quantile([.5, .75, .9, 1.0]).items()}
res['per_scenario'] = {r: {'warnings': q(D.warnings), 'no_leak_flowing': q(D.false_alert),
                           'scenarios_with_5plus_no_leak_warnings': int((D.false_alert >= 5).sum()),
                           'scenarios_with_eligible_abrupt': int((D.abrupt_eligible > 0).sum()),
                           'of_which_all_abrupt_found': int(((D.abrupt_eligible > 0) & (D.abrupt_found == D.abrupt_eligible)).sum()),
                           'of_which_none_found': int(((D.abrupt_eligible > 0) & (D.abrupt_found == 0)).sum())}
                       for r, D in (('frozen', Pf), ('adaptive', Pa))}
# leaks found by one rule only (sudden and gradual), with the adaptive threshold at onset
Lf, La = pd.DataFrame(lf), pd.DataFrame(la)
m = Lf.merge(La, on=['scenario', 'link'], suffixes=('_frozen', '_adaptive'))
m = m[m.eligible_frozen & (m.outcome_frozen != m.outcome_adaptive)]
diff = []
for r in m.itertuples():
    a = OK[OK.scenario == r.scenario].iloc[0]
    s = io1000.read_inlet(DATA / f'hanoi1000-inlet/Scenario-{r.scenario}_Link_1.csv'); rr = R.M.run(s, 'self_aligning')
    d0 = int((pd.Timestamp(r.start_frozen) - pd.Timestamp(a.day0).normalize()) / pd.Timedelta(days=1))
    Ta = R.adaptive_thresholds(rr.step, rr.threshold)
    diff.append({'scenario': r.scenario, 'leak': r.link, 'type': r.type_frozen, 'frozen': r.outcome_frozen,
                 'adaptive': r.outcome_adaptive, 'frozen_T': round(rr.threshold, 1),
                 'adaptive_T_at_onset': round(float(Ta[min(d0, len(Ta) - 1)]), 1),
                 'max_step_first_8_nights': round(float(np.nanmax(rr.step[d0:d0 + 8])), 1) if d0 < len(rr.step) else None})
res['found_by_one_rule_only'] = diff

# section 8: do the development findings recur? (after labels; reported, not judged)
yend = L.end.max()
inc = L[(L.type == 'incipient') & ~L.never_flowed]
onoff = []
for r in inc.itertuples():
    a = OK[OK.scenario == r.scenario]
    if a.empty: continue
    ns = int(a.night_start_hour.iloc[0])
    v = pd.to_numeric(pd.read_csv(DATA / f'hanoi1000-leaks/Scenario-{r.scenario}/Leak_{r.link}_demand.csv').iloc[:, 1], errors='coerce').values
    n = v.reshape(-1, 2).mean(1).reshape(-1, 24)[:, ns:ns + 2].mean(1)
    s0 = io1000.read_inlet(DATA / f'hanoi1000-inlet/Scenario-{r.scenario}_Link_1.csv').index[0]
    d0 = int((r.start - s0) / pd.Timedelta(days=1)) + 1; d1 = int((r.end - s0) / pd.Timedelta(days=1))
    act = n[d0:d1]
    if len(act) >= 7 and act.max() > 0:
        onoff.append((np.abs(np.diff(act)) > 0.5 * act.max()).sum() / len(act) * 7 >= 1)
EF = pd.DataFrame(ef); EF = EF[EF.outcome == 'false_alert']
res['development_findings_recur'] = {
    'share_of_flowing_leaks_stopping_before_last_timestamp': round(float((L[~L.never_flowed].end < yend).mean()), 3),
    'share_of_gradual_leaks_switching_on_off_weekly': round(float(np.mean(onoff)), 3) if onoff else None,
    'frozen_no_leak_warnings_in_feb_jun_jul': round(float(EF.day.apply(lambda d: int(d // 30.42) in (1, 5, 6)).mean()), 3) if len(EF) else None,
    'frozen_no_leak_warnings_on_day_index_mod7_in_5_6': round(float(EF.day.apply(lambda d: d % 7 in (5, 6)).mean()), 3) if len(EF) else None}

# early-leak sensitivity (reported; verdict unchanged)
first = L[~L.never_flowed].groupby('scenario').start.min()
d0map = dict(zip(A.scenario, pd.to_datetime(A.day0)))
early = {k for k, t in first.items() if (t - d0map[k].normalize()) / pd.Timedelta(days=1) < 28}
clean = ids - early
fzc = evaluate('frozen', clean)[0]; adc = evaluate('adaptive', clean)[0]
res['early_leak_sensitivity'] = {'assessable_scenarios_with_leak_before_day_29': len(ids & early),
                                 'criteria_without_them': criteria(adc, fzc)}
(OUT / 'step6-results.json').write_text(json.dumps(res, indent=2, default=str) + '\n')
Pf.to_csv(OUT / 'per-scenario-frozen.csv', index=False); Pa.to_csv(OUT / 'per-scenario-adaptive.csv', index=False)
pd.DataFrame(ef).to_csv(OUT / 'warnings-scored-frozen.csv', index=False); pd.DataFrame(ea).to_csv(OUT / 'warnings-scored-adaptive.csv', index=False)
shf.to_csv(OUT / 'shifts-frozen.csv', index=False); sha.to_csv(OUT / 'shifts-adaptive.csv', index=False)
print(json.dumps({k: res[k] for k in ('criteria', 'not_assessable')}, indent=2, default=str))
