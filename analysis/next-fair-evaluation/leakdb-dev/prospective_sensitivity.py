"""DEVELOPMENT SENSITIVITY on the 490 already-scored scenarios: the locked result is NOT
changed. Re-scores frozen and adaptive warnings with the prospective timing rule
(leakdb1000/prospective.py), including their chance comparisons. Not used to retune
anything: the rule and criteria of PROTOCOL-LEAKDB-1000.md were fixed before this ran."""
import json, sys
from variants import *
sys.path.insert(0, str(HERE.parent / 'leakdb1000'))
import prospective as P
import rules as R
out, same = {}, True
for kind in ('frozen', 'adaptive'):
    scen, tot, ab, inc, fe, delays = [], {o: 0 for o in P.OUTCOMES}, [0, 0], [0, 0], 0.0, []
    for k in A.scenario:
        s = inlet(k); r, fz, ad = R.both_rules(s)
        days = [x[0] for x in (fz if kind == 'frozen' else ad)]
        if kind == 'adaptive':
            same &= days == run_variant(s, 'rolling_sigma')[0]
        else:
            same &= days == sorted(W1[W1.scenario == k].day_index)
        day0 = s.index[0].normalize(); lk = L[(L.scenario == k) & L.start.notna()]
        res = P.score(days, day0, r.night_start_hour, lk)
        for o in P.OUTCOMES: tot[o] += res['outcomes'][o]
        ab[0] += res['abrupt']['eligible']; ab[1] += res['abrupt']['credited']
        inc[0] += res['incipient']['eligible']; inc[1] += res['incipient']['credited']
        delays += [p['delay_h'] for p in res['leaks'] if p['outcome'] == 'credited' and p['type'] == 'abrupt']
        fe += P.leak_free_hours(lk, day0)
        scen.append({'warn_days': days, 'day0': day0, 'ns': r.night_start_hour, 'leaks': lk})
    sh, _ = P.shift_comparison(scen)
    n = sum(len(x['warn_days']) for x in scen)
    out[kind] = {'warnings': n, 'outcomes': tot, 'yield': round(tot['credited'] / n, 4),
                 'without_new_eligible_leak': n - tot['credited'], 'abrupt': ab, 'incipient': inc,
                 'abrupt_median_delay_h': float(np.median(delays)), 'leak_free_hours': fe, 'shifts': sh}
out['codes_identical_to_development_and_locked_warnings'] = bool(same)
out['label'] = 'DEVELOPMENT SENSITIVITY; locked 490-scenario result unchanged; not used to retune'
(HERE / 'dev-prospective-sensitivity.json').write_text(json.dumps(out, indent=2, default=float) + '\n')
print(json.dumps(out, indent=1, default=float))
