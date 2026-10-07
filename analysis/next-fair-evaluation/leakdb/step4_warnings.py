"""Protocol step 4: all Q1 and Q2 warning lists + assessability + label-free Q2 measures.
Reads ONLY the extracted inlet files. Commit the outputs before step 5."""
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import method as M

ROOT = HERE.parents[2]
INLET = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'data/leakdb/hanoi-inlet'
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / 'run'
RUNS = [('Q1_selfaligning_plain', 'self_aligning', False), ('Q2_calendar_plain', 'calendar', False),
        ('Q2_selfaligning_stress', 'self_aligning', True), ('Q2_calendar_stress', 'calendar', True)]
SETTLED_STRESS = range(M.STRESS_DAY + 22, 366)      # stress-copy days 172-366 (indices 171..365)
TRANS_STRESS = range(M.STRESS_DAY + 1, M.STRESS_DAY + 22)   # days 151-171

warn_rows, scen_rows = [], []
m1 = {'plain_match': 0, 'plain_days': 0, 'stress_match': 0, 'stress_days': 0}
m2 = {r: {'settled': 0, 'transition': 0} for r in ('self_aligning', 'calendar')}
exercised = 0
files = sorted(INLET.glob('Scenario-*_Link_1.csv'), key=lambda p: int(p.name.split('-')[1].split('_')[0]))
for f in files:
    k = int(f.name.split('-')[1].split('_')[0])
    s = M.read_inlet(f)
    res = {name: M.run(M.stress_copy(s) if stress else s, mode) for name, mode, stress in RUNS}
    a = res['Q1_selfaligning_plain']
    scen_rows.append({'scenario': k, 'day0': str(s.index[0]), 'q1_assessable': a.assessable, 'reason': a.reason,
                      'threshold': a.threshold, 'threshold_steps': a.n_threshold_steps,
                      'night_start_hour': a.night_start_hour, 'weekday_types': '|'.join(a.types),
                      'all_four_assessable': all(r.assessable for r in res.values())})
    for name, r in res.items():
        if r.assessable:
            for d, issue, st in r.warnings:
                warn_rows.append({'scenario': k, 'run': name, 'day_index': d, 'issue_time': str(issue),
                                  'step': round(st, 3), 'threshold': round(r.threshold, 3)})
    ex = scen_rows[-1]['all_four_assessable'] and any(a.types[w] != a.types[(w - 1) % 7] for w in range(7))
    scen_rows[-1]['q2_exercised'] = bool(ex)
    if not ex:
        continue
    exercised += 1
    pa, sa = res['Q1_selfaligning_plain'], res['Q2_selfaligning_stress']
    for d in SETTLED_STRESS:
        m1['plain_days'] += 1; m1['plain_match'] += pa.day_type[d - 1] == pa.types[(d - 1) % 7]
        m1['stress_days'] += 1; m1['stress_match'] += sa.day_type[d] == M.true_type_after_stress(sa.types, d)
    for mode, pn, sn in (('self_aligning', 'Q1_selfaligning_plain', 'Q2_selfaligning_stress'),
                         ('calendar', 'Q2_calendar_plain', 'Q2_calendar_stress')):
        pw = {d for d, _, _ in res[pn].warnings}; sw = {d for d, _, _ in res[sn].warnings}
        for period, rng in (('settled', SETTLED_STRESS), ('transition', TRANS_STRESS)):
            m2[mode][period] += sum(d in sw for d in rng) - sum(d - 1 in pw for d in rng)

M1p = m1['plain_match'] / m1['plain_days'] if m1['plain_days'] else None
M1s = m1['stress_match'] / m1['stress_days'] if m1['stress_days'] else None
cal_per = m2['calendar']['settled'] / exercised if exercised else 0
informative = exercised >= 20 and cal_per >= 1.0
if not informative:
    verdict = 'UNTESTED (stress check not informative)'
else:
    ok = M1s >= M1p - 0.05 and m2['self_aligning']['settled'] <= 0.25 * m2['calendar']['settled']
    verdict = ('IDEA A RE-ALIGNED AFTER A ONE-DAY SLIP IN THIS CONTROLLED CHECK' if ok else 'DID NOT RE-ALIGN')
W = pd.DataFrame(warn_rows, columns=['scenario', 'run', 'day_index', 'issue_time', 'step', 'threshold'])
W.to_csv(OUT / 'warnings-all-runs.csv', index=False)
pd.DataFrame(scen_rows).to_csv(OUT / 'scenarios-assessability.csv', index=False)
q2 = {'label_free': True, 'exercised_scenarios': exercised,
      'M1_type_agreement_settled': {'selfaligning_plain': M1p, 'selfaligning_stress': M1s},
      'M2_excess_warnings': m2, 'calendar_settled_excess_per_exercised_scenario': cal_per,
      'informative': informative, 'verdict': verdict}
summary = {'scenarios': len(files), 'q1_assessable': int(sum(r['q1_assessable'] for r in scen_rows)),
           'not_assessable_reasons': pd.Series([r['reason'] for r in scen_rows if not r['q1_assessable']]).value_counts().to_dict(),
           'warnings_per_run': W.groupby('run').size().to_dict(), 'Q2': q2}
(OUT / 'step4-warnings.json').write_text(json.dumps(summary, indent=2, default=float) + '\n')
print(json.dumps(summary, indent=2, default=float))
