"""End-to-end steps 3-6 on an INVENTED archive copying the real layout: the target
Hanoi_CMH_1000scenarios.zip plus decoys (Hanoi_CMH.zip, loose folder). No LeakDB data."""
import io, json, subprocess, sys, tempfile, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
HERE = Path(__file__).resolve().parent
rng = np.random.default_rng(3)
grid = pd.date_range('2018-01-01', periods=365 * 48, freq='30min')
h = grid.hour + grid.minute / 60; dow = (np.arange(len(grid)) // 48) % 7; doy = np.arange(len(grid)) / 48
shape = np.where(dow >= 5, 1 + 0.3 * np.sin((h - 10) / 24 * 2 * np.pi), 1 + 0.5 * np.sin((h - 8) / 24 * 2 * np.pi))
season = 1 + 0.15 * np.sin((doy - 80) / 365 * 2 * np.pi)
def scen_zip(n, prefix, decoy=False):
    buf, truth = io.BytesIO(), {}
    with zipfile.ZipFile(buf, 'w') as z:
        for k in range(1, n + 1):
            flow = 4000 * shape * season * (1 + 0.01 * rng.standard_normal(len(grid))); lk = []
            if k % 3:
                st = int(rng.integers(40 * 48, 330 * 48)) + 3; en = st + int(rng.integers(20, 120)) * 48
                lf = np.zeros(len(grid)); lf[st:en] = 300.0; flow = flow + lf; lk.append((f'{k % 9 + 2}', 'abrupt', lf))
            if k % 5 == 0:                                   # an on/off gradual leak
                st = int(rng.integers(40 * 48, 300 * 48)); lf = np.zeros(len(grid))
                for d in range(st // 48, min(364, st // 48 + 60)):
                    if (d // 2) % 2: lf[d * 48:(d + 1) * 48] = 200.0
                flow = flow + lf; lk.append(('30', 'incipient', lf))
            z.writestr(f'{prefix}Scenario-{k}/Flows/Link_1.csv', pd.DataFrame({'Timestamp': grid, 'Value': (flow + (999 if decoy else 0)).round(1)}).to_csv(index=False))
            for node, typ, lf in lk:
                z.writestr(f'{prefix}Scenario-{k}/Leaks/Leak_{node}_demand.csv', pd.DataFrame({'Timestamp': grid, 'Description': lf}).to_csv(index=False))
                z.writestr(f'{prefix}Scenario-{k}/Leaks/Leak_{node}_info.csv', f'Description , Value\nLeak Node , {node}\nLeak Diameter , 0.1\nLeak Type , {typ}\nLeak Start , x\n')
            truth[k] = lk
    return buf.getvalue(), truth
with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp); data = tmp / 'data'; (data / 'raw').mkdir(parents=True); out = tmp / 'out'; out.mkdir()
    target, truth = scen_zip(24, 'Hanoi_CMH/'); decoy, _ = scen_zip(6, 'Hanoi_CMH/', decoy=True)
    with zipfile.ZipFile(data / 'raw/LeakDB.zip', 'w') as z:
        z.writestr('LeakDB/Hanoi_CMH_1000scenarios.zip', target); z.writestr('LeakDB/Hanoi_CMH.zip', decoy)
        z.writestr('LeakDB/Hanoi_CMH/Scenario-1/Flows/Link_1.csv', 'DECOY')
    run = lambda *a: subprocess.run([sys.executable, *map(str, a)], capture_output=True, text=True)
    p3 = run(HERE / 'step3_extract.py', data, out, '--test'); p4 = run(HERE / 'step4_warnings.py', data / 'hanoi1000-inlet', out)
    no_leaks = not (data / 'hanoi1000-leaks').exists()
    p5 = run(HERE / 'step5_leaks.py', data, out, '--test'); p6 = run(HERE / 'step6_score.py', out, data)
    ok = all(p.returncode == 0 for p in (p3, p4, p5, p6))
    if not ok:
        for p in (p3, p4, p5, p6): print(p.stderr[-1500:])
    r3 = json.loads((out / 'step3-extract.json').read_text()); r6 = json.loads((out / 'step6-results.json').read_text())
    inlet_text = ''.join(f.read_text()[:200] for f in (data / 'hanoi1000-inlet').glob('*.csv'))
    ad, fz = r6['adaptive'], r6['frozen']
    checks = {
        'all steps ran': ok,
        'all 24 target scenarios extracted, scenario 1 included': r3['extraction']['extracted'] == 24 and r3['extraction']['scenario_range_in_archive'] == [1, 24],
        'decoy set and loose folder ignored': 'DECOY' not in inlet_text and r3['extraction']['entries_in_inner_archive'] > 24,
        'no leak file before step 5': no_leaks,
        'both rules scored on the same eligible leaks': ad['abrupt']['eligible'] == fz['abrupt']['eligible'] and ad['incipient']['eligible'] == fz['incipient']['eligible'],
        'eligible abrupt = invented abrupt leaks starting on/after day 29': ad['abrupt']['eligible'] == sum(1 for v in truth.values() for n, t, lf in v if t == 'abrupt' and np.flatnonzero(lf)[0] >= 28 * 48),
        'every warning has one outcome (both rules)': all(sum(x['outcomes'].values()) == x['warnings_all_investigations'] for x in (ad, fz)),
        'no-leak + older-leak + credited = all warnings': all(x['warnings_no_leak_flowing'] + x['warnings_during_an_older_leak'] + x['credited'] == x['warnings_all_investigations'] for x in (ad, fz)),
        '47 shifts each rule': ad['shift']['distinct_shifts'] == 47 and fz['shift']['distinct_shifts'] == 47,
        'criteria and verdict present': 'verdict' in r6['criteria'],
        'on/off gradual leaks detected by the recurrence check': r6['development_findings_recur']['share_of_gradual_leaks_switching_on_off_weekly'] == 1.0,
    }
    for k, v in checks.items(): print(('PASS ' if v else 'FAIL ') + k)
    print(r6['criteria'])
    sys.exit(0 if all(checks.values()) else 1)
