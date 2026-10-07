"""Protocol step 5 -- ONLY after step 4's warning lists are committed: extract Leaks/ for the
scenarios in the inlet manifest, build the leak table."""
import json, subprocess, sys
from pathlib import Path
import pandas as pd
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import method as M
from extract_inlet import extract
from scoring import read_leaks

ROOT = HERE.parents[2]
DATA = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'data/leakdb'
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / 'run'
if '--test' not in sys.argv:   # guard: warnings must be committed and unchanged
    st = subprocess.run(['git', 'status', '--porcelain', str(OUT / 'warnings-all-runs.csv')],
                        capture_output=True, text=True, cwd=ROOT).stdout
    tracked = subprocess.run(['git', 'ls-files', str(OUT / 'warnings-all-runs.csv')],
                             capture_output=True, text=True, cwd=ROOT).stdout
    assert tracked.strip() and not st.strip(), 'warning list not committed - stop'
man = pd.read_csv(OUT / 'manifest-inlet.csv')
rep = extract(DATA / 'raw/LeakDB.zip', DATA / 'hanoi-leaks', 11, tmp_parent=DATA, what='leaks',
              only=set(man.scenario))
tables = []
for k in man.scenario:
    grid = M.read_inlet(DATA / f'hanoi-inlet/Scenario-{k}_Link_1.csv').index
    t = read_leaks(DATA / f'hanoi-leaks/Scenario-{k}', grid)
    t.insert(0, 'scenario', k); tables.append(t)
L = pd.concat(tables, ignore_index=True)
L.to_csv(OUT / 'leaks-table.csv', index=False)
res = {'extraction': rep, 'leak_records': len(L), 'scenarios_with_any_leak': int(L.scenario.nunique()),
       'by_type': L.type.value_counts().to_dict(), 'never_flowed': int(L.never_flowed.sum()),
       'timestamps_disagree_with_inlet': int((~L.timestamps_agree_with_inlet).sum())}
(OUT / 'step5-leaks.json').write_text(json.dumps(res, indent=2) + '\n')
print(json.dumps(res, indent=2))
