"""DEVELOPMENT WORK on already-used L-Town readings. Not validation; no leak labels read.

Compares three night measures on 2018 and 2019 flow readings:
  O  original    frozen calendar day-type baseline (the failed method)
  A  self-aligning day type: each weekday's profile chosen by matching the average
     24-h shape of the same weekday over the previous 3 weeks to the 3 January profiles
  B  same-weekday reference: mean of the latest 2 nights minus the median of the same
     2-night pair in each of the previous 3 weeks — no calendar profile at all
and injects a synthetic +20 m3/h permanent step to see how long each keeps it visible.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]; OUT = Path(__file__).resolve().parent
def flows():
    f = pd.concat([pd.read_csv(ROOT / f'data/l-town/readings/{y}_SCADA_Flows.csv', sep=';', decimal=',',
                               parse_dates=['Timestamp']).set_index('Timestamp') for y in (2018, 2019)])
    h = f.resample('h').mean(); return h.p227 + h.p235 - h.PUMP_1

TYPES = ['SunThu', 'Fri', 'Sat']
def cal_type(ix): return np.where(ix.dayofweek == 5, 'Sat', np.where(ix.dayofweek == 4, 'Fri', 'SunThu'))

def measures(m):
    days = pd.date_range(m.index[0].normalize(), m.index[-1].normalize(), freq='D')
    D = m.values.reshape(-1, 24)                       # one row per day
    prof = {t: np.median(D[:14][cal_type(days[:14]) == t], axis=0) for t in TYPES}   # 1-14 Jan 2018
    z = lambda x: (x - x.mean()) / x.std()
    # O: calendar type
    tO = cal_type(days)
    # A: type chosen from the previous 3 same-weekday days' average shape (available at warning time)
    tA = tO.copy()
    for i in range(21, len(days)):
        shape = z(np.mean([D[i - 7], D[i - 14], D[i - 21]], axis=0))
        tA[i] = max(TYPES, key=lambda t: np.corrcoef(shape, z(prof[t]))[0, 1])
    night = lambda types: pd.Series([D[i, 2:4].mean() - prof[types[i]][2:4].mean() for i in range(len(days))], index=days)
    stepf = lambda n: n.rolling(2).mean() - n.shift(2).rolling(7).mean()
    nO, nA = night(tO), night(tA)
    raw = pd.Series(D[:, 2:4].mean(axis=1), index=days)
    pair = raw.rolling(2).mean()
    sB = pair - pd.concat([pair.shift(7), pair.shift(14), pair.shift(21)], axis=1).median(axis=1)
    return {'O': stepf(nO), 'A': stepf(nA), 'B': sB}, pd.Series(tA, index=days), pd.Series(tO, index=days)

m = flows()
base, tA, tO = measures(m)
rs = lambda x: float((np.percentile(x.dropna(), 75) - np.percentile(x.dropna(), 25)) / 1.349)
res = {'label': 'DEVELOPMENT DIAGNOSTIC on already-used L-Town readings; not validation', 'spread': {}, 'synthetic': {}}
for k, s in base.items():
    for y in (2018, 2019):
        x = s.loc[f'{y}-01-15':f'{y}-12-31']
        res['spread'][f'{k}_{y}'] = {'robust_sigma': round(rs(x), 2), 'share_nights_ge_10': round(float((x >= 10).mean()), 3)}
# how often method A's chosen type differs from the calendar, per year
res['A_type_differs_from_calendar'] = {str(y): round(float((tA.loc[str(y)] != tO.loc[str(y)]).mean()), 3) for y in (2018, 2019)}
res['A_mapping_2019_by_weekday'] = {d: tA.loc['2019-02-01':'2019-12-31'][tA.loc['2019-02-01':'2019-12-31'].index.day_name() == d]
                                     .value_counts().idxmax() for d in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}

# synthetic step: +20 m3/h from 1 Jun 2018 00:00, and separately a second +20 from 10 Jun
for label, steps in [('single +20 from 1 Jun 2018', [('2018-06-01', 20)]),
                     ('+20 on 1 Jun and another +20 on 10 Jun', [('2018-06-01', 20), ('2018-06-10', 20)])]:
    syn = m.copy()
    for t, v in steps: syn[syn.index >= t] += v
    s2, tA2, _ = measures(syn)
    out = {}
    for k in base:
        diff = (s2[k] - base[k]).loc['2018-05-30':'2018-07-20']
        vis = s2[k].loc['2018-06-01':'2018-07-20']
        out[k] = {'nights_extra_step_ge_10': int((diff >= 10).sum()),
                  'last_night_extra_ge_10': str(diff[diff >= 10].index.max().date()) if (diff >= 10).any() else None,
                  'max_extra': round(float(diff.max()), 1)}
        if len(steps) == 2:
            d2 = diff.loc['2018-06-10':'2018-06-16']
            out[k]['second_step_extra_max_10_16_Jun'] = round(float(d2.max()), 1)
    out['A_type_changed_by_step'] = int((tA2 != tA).sum())
    res['synthetic'][label] = out
(OUT / 'baseline-ideas-dev.json').write_text(json.dumps(res, indent=2) + '\n')
print(json.dumps(res, indent=2))
