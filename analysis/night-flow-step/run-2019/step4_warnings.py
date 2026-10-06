"""Protocol 9724c60, step 4: generate the complete 2019 warning list. No leak records opened."""
import json, sys
from pathlib import Path
import pandas as pd
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from common import ROOT, read_flows, night_and_step, generate_warnings

night, step = night_and_step(read_flows(ROOT / 'data/l-town/readings/2018_SCADA_Flows.csv',
                                        ROOT / 'data/l-town/readings/2019_SCADA_Flows.csv'))
all_w = generate_warnings(step, '2018-01-15', '2019-12-31')
w18 = [d for d in all_w if d.year == 2018]; w19 = [d for d in all_w if d.year == 2019]
assert [str(d.date()) for d in w18] == ['2018-02-03', '2018-03-06', '2018-05-11', '2018-08-08', '2018-10-06'], \
    'continuous run must reproduce 2018'
assert (step.loc['2018-12-24':'2018-12-31'] < 10).all(), 'rule must enter 2019 armed'
s19 = step.loc['2019-01-01':'2019-12-31']
rows = [{'night': str(d.date()), 'weekday': d.day_name(), 'issued_at': str(d + pd.Timedelta(hours=4)),
         'step_m3_per_hour': round(float(step.loc[d]), 2)} for d in w19]
res = {'protocol': '9724c60', 'leak_records_opened': False,
       'warnings_2019': len(w19), 'warnings_by_month': pd.Series([d.strftime('%b') for d in w19]).value_counts()
           .reindex(pd.date_range('2019-01-01', '2019-12-01', freq='MS').strftime('%b'), fill_value=0).to_dict(),
       'warnings_by_weekday': pd.Series([d.day_name()[:3] for d in w19]).value_counts().to_dict(),
       'nights_with_step_ge_10_2019': int((s19 >= 10).sum()), 'nights_2019': int(s19.notna().sum()),
       'warnings': rows}
(HERE / 'step4-warnings-2019.json').write_text(json.dumps(res, indent=2) + '\n')
pd.DataFrame(rows).to_csv(HERE / 'warnings-2019.csv', index=False)
print(json.dumps({k: v for k, v in res.items() if k != 'warnings'}, indent=2))
print("first and last warnings:", rows[:3], '...', rows[-2:])
