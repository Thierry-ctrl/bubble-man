"""Step 4 -- ONLY after both warning lists are committed: extract Leaks/ and build the table."""
import json, subprocess, sys
from pathlib import Path
import pandas as pd
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE.parent / 'leakdb'))
import method as M
from extract_inlet import extract
sys.path.insert(0, str(HERE))
import io1000
ROOT = HERE.parents[2]
DATA = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'data/leakdb'
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / 'run'
if '--test' not in sys.argv:
    f = str(OUT / 'warnings-both-rules.csv')
    tracked = subprocess.run(['git', 'ls-files', f], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    dirty = subprocess.run(['git', 'status', '--porcelain', f], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    assert tracked and not dirty, 'warning lists not committed - stop'
man = pd.read_csv(OUT / 'manifest-inlet.csv')
rep = extract(DATA / 'raw/LeakDB.zip', DATA / 'hanoi1000-leaks', 1, tmp_parent=DATA, what='leaks',
              only=set(man.scenario), inner_member='LeakDB/Hanoi_CMH_1000scenarios.zip')
tabs = []
for k in man.scenario:
    t = io1000.read_leaks(DATA / f'hanoi1000-leaks/Scenario-{k}', io1000.read_inlet(DATA / f'hanoi1000-inlet/Scenario-{k}_Link_1.csv').index)
    t.insert(0, 'scenario', k); tabs.append(t)
L = pd.concat([t for t in tabs if len(t)], ignore_index=True)
L.to_csv(OUT / 'leaks-table.csv', index=False)
res = {'extraction': rep, 'leak_records': len(L), 'scenarios_with_any_leak': int(L.scenario.nunique()),
       'by_type': L.type.value_counts().to_dict(), 'never_flowed': int(L.never_flowed.astype(bool).sum()),
       'positions_disagree_with_inlet': int((L.positions_agree_with_inlet.astype(str) != 'True').sum()),
       'file_index_formats': L.file_index_format.value_counts().to_dict()}
(OUT / 'step5-leaks.json').write_text(json.dumps(res, indent=2) + '\n'); print(json.dumps(res, indent=2))
