"""Step 3: both warning lists + assessability, from inlet files only. Commit before step 5."""
import json, sys
from pathlib import Path
import pandas as pd
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import rules as R
import io1000
M = R.M
ROOT = HERE.parents[2]
INLET = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'data/leakdb/hanoi1000-inlet'
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / 'run'
wr, sr = [], []
for f in sorted(INLET.glob('Scenario-*_Link_1.csv'), key=lambda p: int(p.name.split('-')[1].split('_')[0])):
    k = int(f.name.split('-')[1].split('_')[0]); s = io1000.read_inlet(f)
    r, fz, ad = R.both_rules(s)
    sr.append({'scenario': k, 'day0': str(s.index[0]), 'assessable': r.assessable, 'reason': r.reason,
               'frozen_threshold': r.threshold, 'night_start_hour': r.night_start_hour,
               'weekday_types': '|'.join(r.types)})
    for rule, lst in (('frozen', fz), ('adaptive', ad)):
        for d, issue, st, T in lst:
            wr.append({'scenario': k, 'rule': rule, 'day_index': d, 'issue_time': str(issue),
                       'step': round(st, 3), 'threshold': round(T, 3)})
W = pd.DataFrame(wr, columns=['scenario', 'rule', 'day_index', 'issue_time', 'step', 'threshold'])
W.to_csv(OUT / 'warnings-both-rules.csv', index=False)
A = pd.DataFrame(sr); A.to_csv(OUT / 'scenarios-assessability.csv', index=False)
res = {'scenarios': len(A), 'assessable': int(A.assessable.sum()),
       'not_assessable_reasons': A[~A.assessable].reason.value_counts().to_dict(),
       'warnings': W.groupby('rule').size().to_dict()}
(OUT / 'step4-warnings.json').write_text(json.dumps(res, indent=2) + '\n'); print(json.dumps(res, indent=2))
