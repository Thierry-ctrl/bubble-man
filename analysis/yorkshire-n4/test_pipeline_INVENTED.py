"""Steps 2 and 4 end to end on an INVENTED year of 15-minute DMA flows and invented repairs.
(Steps 1 and 3 only download; step 3's git guard is not exercised here.)"""
import json, subprocess, sys, tempfile
from pathlib import Path
import numpy as np
import pandas as pd
HERE = Path(__file__).resolve().parent
rng = np.random.default_rng(5)
g = pd.date_range('2016-04-01', periods=365 * 96, freq='15min')
h = np.asarray(g.hour + g.minute / 60); dow = np.asarray(g.dayofweek)
rows, reps = [], []
for dma, step_day in (('11', 150), ('12', 240), ('13', None)):
    f = 4 + 2.5 * np.sin((h - 7) / 24 * 2 * np.pi) + np.where(dow >= 5, 0.3, 0) + rng.normal(0, 0.05, len(g))
    if step_day: f[step_day * 96:] += 1.5; reps.append((dma, (g[0] + pd.Timedelta(days=step_day + 6)).strftime('%d/%m/%Y')))
    code = np.where((rng.random(len(g)) < 0.0003) & (np.arange(len(g)) > 40 * 96), 'M', 'V')   # gaps only after the learning period
    rows.append(pd.DataFrame({'DMA': dma, 'Date': g.strftime('%d/%m/%Y'), 'Time': g.strftime('%H:%M:%S'), 'Flow': f.round(3), 'Flow Validity Code': code}))
reps.append(('13', '15/10/2016'))
gap = pd.DataFrame({'DMA': '14', 'Date': g.strftime('%d/%m/%Y'), 'Time': g.strftime('%H:%M:%S'), 'Flow': 3.0, 'Flow Validity Code': np.where(np.arange(len(g)) == 500, 'I', 'V')})
rows.append(gap); reps.append(('14', '01/09/2016'))   # one invalid reading on day 6 -> not assessable
with tempfile.TemporaryDirectory() as t:
    t = Path(t); (t / 'run').mkdir()
    pd.concat(rows).to_csv(t / 'area.csv', index=False)
    pd.DataFrame(reps, columns=['DMA', 'Completed Date']).to_csv(t / 'rep.csv', index=False)
    p2 = subprocess.run([sys.executable, HERE / 'step2_warnings.py', t / 'area.csv', t / 'run'], capture_output=True, text=True)
    p4 = subprocess.run([sys.executable, HERE / 'step4_score.py', t / 'run', t / 'rep.csv'], capture_output=True, text=True)
    ok = p2.returncode == 0 and p4.returncode == 0
    if not ok: print(p2.stderr[-1500:], p4.stderr[-1500:])
    r2 = json.loads((t / 'run/step2-warnings.json').read_text()); r4 = json.loads((t / 'run/step4-results.json').read_text())
    checks = {'steps 2 and 4 ran': ok, 'four DMAs read; the one with a single early invalid reading is not assessable': r2['dmas'] == 4 and r2['assessable'] == 3 and r2['not_assessable_reasons'] == {'days 1-14 incomplete': 1},
              'three eligible repairs (the not-assessable DMA excluded)': r4['adaptive']['eligible_repairs'] == 3 and r4['repairs_in_assessable_dmas'] == 3,
              'both invented steps precede their repair (both rules)': r4['adaptive']['preceded'] >= 2 and r4['frozen']['preceded'] >= 2,
              'criteria computed (Y1 fails: only 3 repairs)': r4['criteria']['verdict'] == 'INCONCLUSIVE'}
    for k, v in checks.items(): print(('PASS ' if v else 'FAIL ') + k)
    sys.exit(0 if all(checks.values()) else 1)
