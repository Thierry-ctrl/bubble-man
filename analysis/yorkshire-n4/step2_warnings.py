"""Step 2: convert every N4 DMA and run both unchanged rules. Flow readings only.
Commit run/ before step 3."""
import json, sys
from pathlib import Path
import pandas as pd
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]; sys.path.insert(0, str(HERE))
import yw
src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'data/yorkshire/N4_2016_2017.csv'
out = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / 'run'
series, rep = yw.read_area(src)
A, W = [], []
for dma, s30 in sorted(series.items(), key=lambda kv: yw.dma_key(kv[0]).zfill(8)):
    s = yw.to_frozen_reader(s30)
    r, fz, ad = yw.R.both_rules(s)
    A.append({'dma': dma, 'assessable': r.assessable, 'reason': r.reason, 'share_30min_present': round(float(s30.notna().mean()), 4),
              'night_start_hour': r.night_start_hour, 'frozen_threshold_m3h': r.threshold, 'weekday_types': '|'.join(r.types)})
    for rule, lst in (('frozen', fz), ('adaptive', ad)):
        W += [{'dma': dma, 'rule': rule, 'day_index': d, 'issue_time_local': str(i), 'step_m3h': round(st, 3), 'threshold_m3h': round(T, 3)}
              for d, i, st, T in lst]
A = pd.DataFrame(A); Wd = pd.DataFrame(W, columns=['dma', 'rule', 'day_index', 'issue_time_local', 'step_m3h', 'threshold_m3h'])
A.to_csv(out / 'dma-assessability.csv', index=False); Wd.to_csv(out / 'warnings-both-rules.csv', index=False)
res = {'read_report': rep, 'dmas': len(A), 'assessable': int(A.assessable.sum()),
       'not_assessable_reasons': A[~A.assessable].reason.value_counts().to_dict(),
       'warnings': Wd.groupby('rule').size().to_dict(),
       'assessable_dma_days_from_day_29': int(A.assessable.sum()) * (365 - 28)}
(out / 'step2-warnings.json').write_text(json.dumps(res, indent=2, default=str) + '\n'); print(json.dumps(res, indent=2, default=str))
