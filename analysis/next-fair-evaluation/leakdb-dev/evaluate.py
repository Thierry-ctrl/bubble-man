"""DEVELOPMENT comparison of the frozen method and candidate changes on scenarios 11-500.
Scored with the unchanged scorer; chance comparison by whole-week shifts (same k for all)."""
import json, sys
from variants import *

def evaluate(kind, first_day_index):
    S.WARN_FROM = first_day_index
    S.DOMAIN_DAYS = 7 * ((364 - first_day_index) // 7)
    scen, tot, ab, inc, delays_ab, fa_exp = [], {}, [0, 0], [0, 0], [], 0
    per = []
    for k in A.scenario:
        s = inlet(k); days, ns = run_variant(s, kind)
        days = [d for d in days if d >= first_day_index]
        day0 = s.index[0].normalize(); lk = L[(L.scenario == k) & L.start.notna()]
        r = S.score_scenario(days, day0, ns, lk)
        for o, n in r['outcomes'].items(): tot[o] = tot.get(o, 0) + n
        ab[0] += r['abrupt']['eligible_leaks']; ab[1] += r['abrupt']['credited']
        inc[0] += r['incipient']['eligible_leaks']; inc[1] += r['incipient']['credited']
        delays_ab += [x['delay_hours_from_first_flow'] for x in r['leaks'] if x['outcome'] == 'credited' and x['type'] == 'abrupt']
        hours = pd.date_range(day0 + pd.Timedelta(days=first_day_index), day0 + pd.Timedelta(days=364, hours=23), freq='h')
        fa_exp += int((~S.flowing_hours(lk, hours)).sum())
        per.append({'scenario': k, 'warnings': len(days), 'credited': r['outcomes']['credited'],
                    'false_alert': r['outcomes']['false_alert'], 'abrupt_eligible': r['abrupt']['eligible_leaks'],
                    'abrupt_credited': r['abrupt']['credited']})
        scen.append({'warn_days': days, 'day0': day0, 'ns': ns, 'leaks': lk})
    sh, shdf = S.shift_comparison(scen)
    n = sum(len(x['warn_days']) for x in scen); c = tot['credited']
    return {'variant': kind, 'window_from_day': first_day_index + 1, 'warnings': n, 'credited': c,
            'yield': round(c / n, 4), 'without_new_leak': n - c, 'false_alerts': tot['false_alert'],
            'leak_free_exposure_hours': fa_exp, 'unattributable': tot['unattributable'],
            'abrupt_eligible': ab[0], 'abrupt_credited': ab[1], 'incipient_eligible': inc[0], 'incipient_credited': inc[1],
            'abrupt_median_delay_h': float(np.median(delays_ab)) if delays_ab else None,
            'shift_domain_weeks': S.DOMAIN_DAYS // 7, 'p_abrupt': round(sh['p_abrupt'], 4),
            'shift_abrupt_max': int(shdf.abrupt.max())}, per, shdf

if __name__ == '__main__':
    out = []
    for kind, start in [(k, 28) for k in KINDS if k != 'weekday_differenced'] + \
                       [('frozen', 49), ('weekday_differenced', 49)]:
        res, per, sh = evaluate(kind, start)
        out.append(res); print(json.dumps(res))
        pd.DataFrame(per).to_csv(HERE / f'dev-per-scenario-{kind}-from{start + 1}.csv', index=False)
    (HERE / 'dev-variants.json').write_text(json.dumps({'label': 'DEVELOPMENT on already-scored scenarios 11-500; selection here is optimistic', 'results': out}, indent=2) + '\n')
