"""End-to-end run of steps 3-6 on an INVENTED archive (nested layout, 30 invented scenarios,
invented leaks). Checks the scripts run and their outputs are consistent. No LeakDB data."""
import io, json, subprocess, sys, tempfile, zipfile
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
rng = np.random.default_rng(0)
grid = pd.date_range('2017-01-01', periods=365 * 48, freq='30min')
h = grid.hour + grid.minute / 60; dow = (np.arange(len(grid)) // 48) % 7
shape = np.where(dow >= 5, 1 + 0.3 * np.sin((h - 10) / 24 * 2 * np.pi), 1 + 0.5 * np.sin((h - 8) / 24 * 2 * np.pi))
truth = {}
with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp); data = tmp / 'data'; (data / 'raw').mkdir(parents=True); out = tmp / 'out'; out.mkdir()
    inner = io.BytesIO()
    with zipfile.ZipFile(inner, 'w') as z:
        for k in range(1, 33):
            flow = 4000 * shape * (1 + 0.01 * rng.standard_normal(len(grid)))
            leaks = []
            if k % 3:                                   # two of every three scenarios get a leak
                st = int(rng.integers(40 * 48, 360 * 48)); size = 300.0
                lf = np.zeros(len(grid)); lf[st:] = size; flow = flow + lf
                leaks.append((f'{k % 7 + 2}', st, lf))
            if k == 5:                                  # an early leak (day 20)
                lf = np.zeros(len(grid)); lf[20 * 48:] = 200.0; flow = flow + lf; leaks.append(('9', 20 * 48, lf))
            z.writestr(f'Scenario-{k}/Flows/Link_1.csv', pd.DataFrame({'Timestamp': grid, 'Value': flow.round(1)}).to_csv(index=False))
            z.writestr(f'Scenario-{k}/Flows/Link_2.csv', 'Timestamp,Value\n')
            for node, st, lf in leaks:
                z.writestr(f'Scenario-{k}/Leaks/Leak_{node}_demand.csv', pd.DataFrame({'Timestamp': grid, 'Description': lf}).to_csv(index=False))
                z.writestr(f'Scenario-{k}/Leaks/Leak_{node}_info.csv', f'Description , Value\nLeak Node , {node}\nLeak Diameter , 0.1\nLeak Type , abrupt\nLeak Start , x\n')
            truth[k] = leaks
    decoy = io.BytesIO()
    with zipfile.ZipFile(decoy, 'w') as dz:
        dz.writestr('Hanoi_CMH/Scenario-13/Flows/Link_1.csv', 'DECOY')
    with zipfile.ZipFile(data / 'raw/LeakDB.zip', 'w') as outer:
        outer.writestr('LeakDB/Hanoi_CMH.zip', inner.getvalue())
        # decoys matching the real layout (revision 4): loose examples and a second Hanoi set
        outer.writestr('LeakDB/Hanoi_CMH/Scenario-12/Flows/Link_1.csv', 'DECOY')
        outer.writestr('LeakDB/Hanoi_CMH/Scenario-12/Leaks/Leak_DECOY_info.csv', 'DECOY')
        outer.writestr('LeakDB/Hanoi_CMH_1000scenarios.zip', decoy.getvalue())
    run = lambda *a: subprocess.run([sys.executable, *map(str, a)], capture_output=True, text=True)
    p3 = run(HERE / 'step3_extract.py', data, out, '--test')
    p4 = run(HERE / 'step4_warnings.py', data / 'hanoi-inlet', out)
    no_leaks_before_step5 = not (data / 'hanoi-leaks').exists()
    p5 = run(HERE / 'step5_leaks.py', data, out, '--test')
    p6 = run(HERE / 'step6_score.py', out)
    ok = all(p.returncode == 0 for p in (p3, p4, p5, p6))
    if not ok:
        for p in (p3, p4, p5, p6): print(p.stderr[-2000:])
    r3 = json.loads((out / 'step3-extract.json').read_text()); r6 = json.loads((out / 'step6-results.json').read_text())
    L = pd.read_csv(out / 'leaks-table.csv')
    checks = {
        'all four steps ran': ok,
        'nested layout: 22 scenarios >= 11 extracted, 10 excluded': r3['extraction']['extracted'] == 22 and r3['extraction']['excluded_below_min_scenario'] == 10,
        'no leak file existed before step 5': no_leaks_before_step5,
        'decoy loose folder and second set ignored': 'DECOY' not in ''.join(p.read_text() for p in (data / 'hanoi-inlet').glob('*.csv'))
            and not any('DECOY' in p.name for p in (data / 'hanoi-leaks').rglob('*')),
        'leak table: one record per invented leak in scenarios >= 11': len(L) == sum(len(truth[k]) for k in range(11, 33)),
        'Q1 eligible abrupt = invented leaks starting on/after day 29': r6['Q1_network_transfer']['full_window']['abrupt']['eligible'] == sum(1 for k in range(11, 33) for _, st, _ in truth[k] if st >= 28 * 48),
        'every warning has exactly one outcome': sum(r6['Q1_network_transfer']['full_window']['outcomes'].values()) == r6['Q1_network_transfer']['full_window']['warnings_total_all_investigations'],
        'investigations without new leak = total - credited': r6['Q1_network_transfer']['full_window']['investigations_without_a_new_eligible_leak'] == r6['Q1_network_transfer']['full_window']['warnings_total_all_investigations'] - r6['Q1_network_transfer']['full_window']['credited'],
        '47 shifts': r6['Q1_network_transfer']['shift_comparison']['distinct_shifts'] == 47,
        'large invented leaks mostly found (pipeline sanity)': r6['Q1_network_transfer']['full_window']['abrupt']['credited'] >= 0.8 * r6['Q1_network_transfer']['full_window']['abrupt']['eligible'],
        'Q2 reported separately with four runs': len(r6['Q2_controlled_weekly_slip']['after_labels_reported_not_judged']) == 4,
    }
    for k, v in checks.items(): print(('PASS ' if v else 'FAIL ') + k)
    print(json.dumps(r6['Q1_network_transfer']['criteria']), json.loads((out / 'step4-warnings.json').read_text())['Q2']['verdict'])
    sys.exit(0 if all(checks.values()) else 1)
