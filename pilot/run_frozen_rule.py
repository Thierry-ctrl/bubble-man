"""Run the two existing rules, UNCHANGED, on a converted zone series (zone_net_inflow_30min.csv).
  frozen   = LeakDB protocol rule (threshold from days 9-28)
  adaptive = PROTOCOL-LEAKDB-1000 rule (threshold from the previous 8 weeks)
Writes warnings.csv and run-summary.json. The output is a list of nights to investigate;
nothing here scores it - real outcomes come from field visits and repair records."""
import json, sys
from pathlib import Path
import pandas as pd
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'analysis/next-fair-evaluation/leakdb1000'))
import rules as R

def run(series_csv: Path, out: Path) -> dict:
    s = R.M.read_inlet(series_csv)            # the frozen reader: 365 days from the first midnight
    r, fz, ad = R.both_rules(s)
    rows = [{'rule': name, 'night_of': str((s.index[0].normalize() + pd.Timedelta(days=d)).date()),
             'issue_time_local': str(i), 'step_m3h': round(st, 2), 'threshold_m3h': round(T, 2)}
            for name, lst in (('frozen', fz), ('adaptive', ad)) for d, i, st, T in lst]
    out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=['rule', 'night_of', 'issue_time_local', 'step_m3h', 'threshold_m3h']).to_csv(out / 'warnings.csv', index=False)
    summ = {'assessable': r.assessable, 'reason': r.reason, 'night_window_start_hour': r.night_start_hour,
            'weekday_types': r.types, 'frozen_threshold_m3h': r.threshold,
            'warnings': {'frozen': len(fz), 'adaptive': len(ad)},
            'note': 'Warnings are nights to investigate, not confirmed leaks.'}
    (out / 'run-summary.json').write_text(json.dumps(summ, indent=2, default=str) + '\n')
    return summ

if __name__ == '__main__':
    print(json.dumps(run(Path(sys.argv[1]), Path(sys.argv[2])), indent=2, default=str))
