"""DEVELOPMENT: frozen vs adaptive threshold, per scenario and per sudden leak."""
import json
from variants import *
f = pd.read_csv(HERE / 'dev-per-scenario-frozen-from29.csv'); r = pd.read_csv(HERE / 'dev-per-scenario-rolling_sigma-from29.csv')
m = f.merge(r, on='scenario', suffixes=('_frozen', '_adaptive'))
q = lambda s: {str(k): float(v) for k, v in s.quantile([.5, .75, .9, 1.0]).items()}
out = {'warnings_per_scenario': {'frozen': q(m.warnings_frozen), 'adaptive': q(m.warnings_adaptive)},
       'false_alerts_per_scenario': {'frozen': q(m.false_alert_frozen), 'adaptive': q(m.false_alert_adaptive)},
       'scenarios_with_5plus_false_alerts': {'frozen': int((m.false_alert_frozen >= 5).sum()), 'adaptive': int((m.false_alert_adaptive >= 5).sum())},
       'scenarios_with_any_eligible_sudden_leak': int((m.abrupt_eligible_frozen > 0).sum()),
       'of_those_all_sudden_found': {'frozen': int(((m.abrupt_eligible_frozen > 0) & (m.abrupt_credited_frozen == m.abrupt_eligible_frozen)).sum()),
                                     'adaptive': int(((m.abrupt_eligible_adaptive > 0) & (m.abrupt_credited_adaptive == m.abrupt_eligible_adaptive)).sum())},
       'scenarios_more_sudden_found_adaptive': int((m.abrupt_credited_adaptive > m.abrupt_credited_frozen).sum()),
       'scenarios_fewer_sudden_found_adaptive': int((m.abrupt_credited_adaptive < m.abrupt_credited_frozen).sum())}
# which sudden leaks change status, and the adaptive threshold at their onset
rows = []
for k in m[m.abrupt_credited_adaptive != m.abrupt_credited_frozen].scenario:
    s = inlet(k); res = M.run(s, 'self_aligning'); ns = res.night_start_hour; day0 = s.index[0].normalize()
    lk = L[(L.scenario == k) & L.start.notna()]
    fr = S.score_scenario(run_variant(s, 'frozen')[0], day0, ns, lk)
    ad = S.score_scenario(run_variant(s, 'rolling_sigma')[0], day0, ns, lk)
    st = res.step
    for a, b in zip(fr['leaks'], ad['leaks']):
        if a['type'] == 'abrupt' and a['outcome'] != b['outcome']:
            d0 = int((pd.Timestamp(a['start']) - day0) / pd.Timedelta(days=1))
            past = st[max(8, d0 - 56):d0 - 8]
            Tad = 4 * rsig(past) if np.isfinite(past).sum() >= 20 else res.threshold
            other = lk[(lk.link != a['link']) & (lk.start < pd.Timestamp(a['start']))
                       & (lk.end >= pd.Timestamp(a['start']) - pd.Timedelta(days=63))]
            rows.append({'scenario': k, 'leak': a['link'], 'frozen': a['outcome'], 'adaptive': b['outcome'],
                         'frozen_T': round(res.threshold, 1), 'adaptive_T_at_onset': round(Tad, 1),
                         'max_step_first_8_nights': round(float(np.nanmax(st[d0:d0 + 8])), 1),
                         'another_leak_in_previous_9_weeks': [f"{o.type}" for o in other.itertuples()]})
out['sudden_leaks_changing_outcome'] = rows
(HERE / 'dev-compare-per-scenario.json').write_text(json.dumps(out, indent=2, default=str) + '\n'); print(json.dumps(out, indent=1, default=str))
