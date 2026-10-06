"""Shared pieces for the locked 2019 run (protocol 9724c60). Rule and baseline unchanged.

night_and_step() reproduces night_signal.night_series() exactly, but accepts a flow frame
that may span 2018 and 2019. Equivalence is asserted by test_equivalence.py on 2018 data
before any 2019 file is obtained.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
THRESHOLD, SPACING = 10.0, pd.Timedelta(days=7)

def read_flows(*paths):
    frames = [pd.read_csv(p, sep=';', decimal=',', parse_dates=['Timestamp']).set_index('Timestamp')
              for p in paths]
    return pd.concat(frames).sort_index()

def night_and_step(flows_5min):
    hourly = flows_5min.resample('h').mean()
    frame = (hourly.p227 + hourly.p235 - hourly.PUMP_1).to_frame('v')
    frame['g'] = np.where(frame.index.dayofweek == 5, 'Sat',
                          np.where(frame.index.dayofweek == 4, 'Fri', 'SunThu'))
    frame['h'] = frame.index.hour
    profile = frame.loc['2018-01-01':'2018-01-14 23:00'].groupby(['g', 'h'])['v'].median()
    assert len(profile) == 72, 'baseline must cover 24 hours x 3 day types'
    resid = frame.v - pd.Series([profile.loc[(g, h)] for g, h in zip(frame.g, frame.h)], index=frame.index)
    hours = resid[resid.index.hour.isin([2, 3])]
    counts = hours.groupby(hours.index.normalize()).count()
    night = hours.groupby(hours.index.normalize()).mean()
    night[counts < 2] = np.nan
    step = night.rolling(2).mean() - night.shift(2).rolling(7).mean()
    step[night.rolling(9).count() < 9] = np.nan
    return night, step

def generate_warnings(step, start='2018-01-15', end='2019-12-31'):
    """The frozen rule, run continuously. Returns warning nights and the final armed state."""
    warns, armed, last = [], True, None
    for d, s in step.loc[start:end].items():
        if not np.isfinite(s):
            continue
        if s < THRESHOLD:
            armed = True
            continue
        issue = d + pd.Timedelta(hours=4)
        if armed and (last is None or issue - last >= SPACING):
            warns.append(d); armed, last = False, issue
    return warns

def robust_sigma(x):
    q1, q3 = np.percentile(x, [25, 75]); return float((q3 - q1) / 1.349)

def noise_changes(night, year):
    span = night.loc[f'{year}-01-15':f'{year}-12-31']
    return span.diff().iloc[1:].dropna()      # within the span only; no change across a gap
