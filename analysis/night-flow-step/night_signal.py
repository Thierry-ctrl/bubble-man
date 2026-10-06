"""Night residual and step, from readings only. Shared by the noise check and the scoring."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

def night_series():
    flows = pd.read_csv(ROOT / 'data/l-town/readings/2018_SCADA_Flows.csv', sep=';', decimal=',',
                        parse_dates=['Timestamp']).set_index('Timestamp').resample('h').mean()
    frame = (flows.p227 + flows.p235 - flows.PUMP_1).to_frame('v')
    frame['g'] = np.where(frame.index.dayofweek == 5, 'Sat',
                          np.where(frame.index.dayofweek == 4, 'Fri', 'SunThu'))
    frame['h'] = frame.index.hour
    profile = frame.loc['2018-01-01':'2018-01-14 23:00'].groupby(['g', 'h'])['v'].median()
    resid = frame.v - pd.Series([profile.loc[(g, h)] for g, h in zip(frame.g, frame.h)], index=frame.index)
    hours = resid[resid.index.hour.isin([2, 3])]
    counts = hours.groupby(hours.index.normalize()).count()
    night = hours.groupby(hours.index.normalize()).mean()
    night[counts < 2] = np.nan                       # rule: incomplete night -> no value
    window = night.rolling(9)
    latest2 = night.rolling(2).mean()
    before7 = night.shift(2).rolling(7).mean()
    step = latest2 - before7
    step[window.count() < 9] = np.nan                # rule: any of 9 nights missing -> no step
    return night, step
