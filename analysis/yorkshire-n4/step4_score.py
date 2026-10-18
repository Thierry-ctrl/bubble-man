"""Step 4: associate warnings with recorded repairs, both rules; shift comparison; report once."""
import json, sys
from pathlib import Path
import pandas as pd
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]; sys.path.insert(0, str(HERE))
import yw
out = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / 'run'
rp_path = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / 'data/yorkshire/Mains_Repairs_2016-17.csv'
A = pd.read_csv(out / 'dma-assessability.csv', dtype={'dma': str}); W = pd.read_csv(out / 'warnings-both-rules.csv', dtype={'dma': str})
rep, rrep = yw.read_repairs(rp_path)
dmas = set(A[A.assessable].dma)
rep_n4 = rep[rep.dma.isin(set(A.dma))]
res = {'repairs_file': rrep, 'repairs_in_n4_dmas': len(rep_n4), 'repairs_in_assessable_dmas': int(rep.dma.isin(dmas).sum())}
for rule in ('frozen', 'adaptive'):
    wd = {d: sorted(W[(W.rule == rule) & (W.dma == d)].day_index.tolist()) for d in dmas}
    a, E = yw.associate(wd, rep, dmas)
    sh, dist = yw.shift_comparison(wd, rep, dmas)
    months = len(dmas) * (365 - 28) / 30.44
    res[rule] = {**a, 'share_of_repairs_preceded': round(a['preceded'] / a['eligible_repairs'], 4) if a['eligible_repairs'] else None,
                 'share_of_warnings_followed': round(a['warnings_followed_by_repair_within_28d'] / a['warnings'], 4) if a['warnings'] else None,
                 'warnings_per_dma_month': round(a['warnings'] / months, 3) if months else None, 'shift': sh}
    E.to_csv(out / f'repairs-{rule}.csv', index=False); pd.Series(dist, name='preceded').to_csv(out / f'shifts-{rule}.csv', index_label='k_minus_1')
ad = res['adaptive']
res['criteria'] = {'Y1_eligible_repairs': ad['eligible_repairs'], 'Y1': ad['eligible_repairs'] >= 20,
                   'Y2_p_adaptive': round(ad['shift']['p'], 4), 'Y2': ad['shift']['p'] <= 0.05,
                   'verdict': ('INCONCLUSIVE' if ad['eligible_repairs'] < 20 else
                               'ADAPTIVE WARNINGS PRECEDE RECORDED REPAIRS MORE OFTEN THAN CHANCE' if ad['shift']['p'] <= 0.05 else
                               'NO ASSOCIATION BEYOND CHANCE DETECTED')}
(out / 'step4-results.json').write_text(json.dumps(res, indent=2, default=str) + '\n'); print(json.dumps(res, indent=2, default=str))
