"""CODE CHECK ONLY on LeakDB's 10 public sample scenarios (Hanoi, scenarios 1-10).

Their leak counts are already known, so they are EXCLUDED from the experiment. Here they
test only: safe extraction, the loader, units, timing, and that warning generation runs
and obeys its own rules. Nothing is scored; no leak file, scenario .inp, or published
result is opened; warning counts, dates and thresholds are NOT printed or saved, so they
cannot feed back into the frozen settings.

Usage: python check_code_on_sample.py PATH/TO/Hanoi_CMH.zip   (the 79 MB GitHub sample)
"""
import io, json, subprocess, sys, tempfile, zipfile
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import method as M
from extract_inlet import extract

HANOI_BASE_DEMAND = 5538.9          # m3/h, sum of junction base demands in Hanoi_CMH.inp
SECRET = 'SECRETNODE'
checks = {}

def check(name, ok, **facts):
    checks[name] = {'pass': bool(ok), **facts}
    print(('PASS ' if ok else 'FAIL ') + name)


def run_extractor_cli(archive, out, min_s):
    p = subprocess.run([sys.executable, str(HERE / 'extract_inlet.py'), str(archive), str(out),
                        '--min-scenario', str(min_s)], capture_output=True, text=True)
    return p.stdout + p.stderr


def mock_member(z, path, text='Timestamp,Value\n'):
    z.writestr(path, text)


sample = Path(sys.argv[1])
with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)

    # --- 1. extraction safety on mock archives whose leak files carry a secret marker -------
    for layout in ('flat', 'nested', 'unknown'):
        arc = tmp / f'mock_{layout}.zip'
        inner_buf = io.BytesIO()
        with zipfile.ZipFile(inner_buf if layout == 'nested' else arc, 'w') as z:
            for k in (3, 11, 12, 40):
                pre = {'flat': 'LeakDB/Hanoi_CMH/', 'nested': '', 'unknown': 'X/'}[layout]
                mock_member(z, f'{pre}Scenario-{k}/Flows/Link_1.csv')
                mock_member(z, f'{pre}Scenario-{k}/Flows/Link_2.csv')
                mock_member(z, f'{pre}Scenario-{k}/Leaks/Leak_{SECRET}{k}_demand.csv')
                mock_member(z, f'{pre}Scenario-{k}/Leaks/Leak_{SECRET}{k}_info.csv')
                mock_member(z, f'{pre}Scenario-{k}/Labels.csv')
                mock_member(z, f'{pre}Scenario-{k}/Hanoi_CMH_Scenario-{k}.inp')
                if layout == 'flat':
                    mock_member(z, f'LeakDB/Net1_CMH/Scenario-{k}/Flows/Link_1.csv')
        if layout == 'nested':
            with zipfile.ZipFile(arc, 'w') as outer:
                outer.writestr('LeakDB/Hanoi_CMH.zip', inner_buf.getvalue())
                outer.writestr(f'LeakDB/Net1_CMH/Scenario-1/Leaks/Leak_{SECRET}_info.csv', '')
        out = tmp / f'out_{layout}'
        printed = run_extractor_cli(arc, out, 11)
        files = sorted(p.name for p in out.glob('*')) if out.exists() else []
        expect = [] if layout == 'unknown' else ['Scenario-11_Link_1.csv', 'Scenario-12_Link_1.csv',
                                                 'Scenario-40_Link_1.csv']
        check(f'extract_{layout}_layout_only_inlet_files_scenarios_ge_11', files == expect)
        check(f'extract_{layout}_layout_never_prints_or_writes_leak_names',
              SECRET not in printed and not any(SECRET in f for f in files)
              and not any('Leak' in f or 'Label' in f for f in files))

    # --- 2. the real sample, wrapped as the nested layout ----------------------------------
    wrapped = tmp / 'wrapped.zip'
    with zipfile.ZipFile(wrapped, 'w', zipfile.ZIP_STORED) as outer:
        outer.write(sample, 'LeakDB/Hanoi_CMH.zip')
    r11 = extract(wrapped, tmp / 'sample_ge11', 11, tmp_parent=tmp)
    check('sample_excluded_entirely_at_min_scenario_11', r11.get('extracted') == 0
          and r11.get('excluded_below_min_scenario') == 10, report=r11)
    r1 = extract(wrapped, tmp / 'sample_all', 1, tmp_parent=tmp)
    check('sample_extracts_10_inlet_files_for_code_check', r1.get('extracted') == 10)

    # --- 3. loader, units, timing -----------------------------------------------------------
    facts = []
    for f in sorted((tmp / 'sample_all').glob('*.csv'), key=lambda p: int(p.name.split('-')[1].split('_')[0])):
        raw = pd.read_csv(f)
        t = pd.to_datetime(raw.Timestamp)
        s = M.read_inlet(f)
        facts.append({
            'scenario': f.name.split('_')[0],
            'rows': len(raw),
            'first_timestamp': str(t.iloc[0]),
            'steps_all_30_min': bool((t.diff().dropna() == pd.Timedelta(minutes=30)).all()),
            'missing_after_load': int(s.isna().sum()),
            'min_flow': round(float(raw.Value.min()), 1),
            'mean_flow_over_base_demand': round(float(raw.Value.mean()) / HANOI_BASE_DEMAND, 3),
        })
    check('loader_rows_17520_regular_30_min_no_missing',
          all(x['rows'] == 17520 and x['steps_all_30_min'] and x['missing_after_load'] == 0 for x in facts))
    check('timing_series_start_at_midnight', all(x['first_timestamp'].endswith('00:00:00') for x in facts))
    check('units_m3_per_hour_flow_positive_and_near_hanoi_base_demand',
          all(x['min_flow'] > 0 and 0.7 < x['mean_flow_over_base_demand'] < 1.3 for x in facts),
          per_scenario=facts)

    # --- 4. warning generation obeys its own rules (no counts, dates or thresholds kept) ----
    ok_struct, ok_prefix, ok_stress, ok_types, assessable, info = True, True, True, True, 0, []
    for f in sorted((tmp / 'sample_all').glob('*.csv')):
        s = M.read_inlet(f)
        D = M.hourly_days(s)
        ok_struct &= D.shape == (365, 24)
        st = M.stress_copy(s)
        ok_stress &= len(st) == 366 * 48 and np.array_equal(
            st.values.reshape(-1, 48)[M.STRESS_DAY + 1], s.values.reshape(-1, 48)[M.STRESS_DAY])
        runs = {}
        for series, tag in ((s, 'plain'), (st, 'stressed')):
            for mode in ('self_aligning', 'calendar'):
                r = M.run(series, mode)
                runs[(tag, mode)] = r
                assessable += r.assessable
                if not r.assessable:
                    continue
                ok_types &= set(r.day_type) <= set(r.types)
                last = None
                for d, issue, stepv in r.warnings:
                    ok_struct &= d >= M.WARN_FROM and stepv >= r.threshold
                    ok_struct &= issue.hour == r.night_start_hour + 2
                    ok_struct &= last is None or (issue - last) >= pd.Timedelta(days=7)
                    last = issue
        info.append({'distinct_day_types_learned': len(set(runs[('plain', 'calendar')].types)),
                     'night_window_start_hour': runs[('plain', 'calendar')].night_start_hour})
        for mode in ('self_aligning', 'calendar'):     # before the repeated day, nothing may change
            a = [w for w in runs[('plain', mode)].warnings if w[0] <= M.STRESS_DAY]
            b = [w for w in runs[('stressed', mode)].warnings if w[0] <= M.STRESS_DAY]
            ok_prefix &= [(d, i) for d, i, _ in a] == [(d, i) for d, i, _ in b]
    check('hourly_reshape_365_by_24', ok_struct)
    check('all_40_runs_assessable', assessable == 40)
    check('warnings_respect_day29_threshold_issue_hour_and_7_day_spacing', ok_struct)
    check('assigned_day_types_are_learned_types', ok_types)
    check('stress_copy_repeats_day_150_and_is_366_days', ok_stress)
    check('stress_leaves_warnings_before_day_150_unchanged', ok_prefix)
    checks['label_free_structure_per_sample_scenario'] = info

out = {'what_this_is': 'CODE CHECK on LeakDB public sample scenarios 1-10 (excluded from the experiment). '
                       'Not scored; warning counts, dates and thresholds deliberately not recorded.',
       'all_pass': all(v.get('pass', True) for v in checks.values() if isinstance(v, dict)),
       'checks': checks}
(HERE / 'sample-code-check.json').write_text(json.dumps(out, indent=2) + '\n')
print('ALL PASS' if out['all_pass'] else 'SOME CHECKS FAILED')
