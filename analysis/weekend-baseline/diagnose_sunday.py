"""How does the current baseline turn Sunday into an apparent anomaly? Readings only.

Descriptive. No leak labels are used. 2019 is not read.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
fl = pd.read_csv(ROOT / 'data/l-town/readings/2018_SCADA_Flows.csv', sep=';', decimal=',',
                 parse_dates=['Timestamp']).set_index('Timestamp').resample('h').mean()
fl['inflow'] = fl.p227 + fl.p235
fl['main_out'] = fl.inflow - fl.PUMP_1
fl['dtype'] = np.select([fl.index.dayofweek == 5, fl.index.dayofweek == 6], ['Sat', 'Sun'], 'Mon-Fri')
fl['hour'] = fl.index.hour

out = {}
print("=== 1. Hourly shape by day type, whole of 2018 (descriptive) ===")
prof = fl.groupby(['dtype', 'hour'])[['main_out', 'inflow', 'PUMP_1']].mean()
print("  hour |  main_out: Mon-Fri   Sat    Sun |  PUMP_1: Sat   Sun")
for h in [3, 5, 7, 9, 11, 13, 17, 21]:
    print(f"   {h:02d}  |  {prof.loc[('Mon-Fri',h),'main_out']:13.1f} {prof.loc[('Sat',h),'main_out']:6.1f} "
          f"{prof.loc[('Sun',h),'main_out']:6.1f} |  {prof.loc[('Sat',h),'PUMP_1']:9.1f} {prof.loc[('Sun',h),'PUMP_1']:5.1f}")
daily = fl.groupby('dtype')[['main_out', 'inflow', 'PUMP_1']].mean()
print("\n  daily mean m3/h:\n" + daily.round(2).to_string())
pump_sat_sun = float((prof.loc['Sun','PUMP_1'] - prof.loc['Sat','PUMP_1']).abs().max())
print(f"\n  largest hour-by-hour Sat-vs-Sun PUMP_1 difference: {pump_sat_sun:.2f} m3/h")
out['daily_mean_m3_per_hour'] = daily.round(3).to_dict()
out['max_hourly_pump_difference_sat_vs_sun'] = round(pump_sat_sun, 3)

print("\n=== 2. What the current baseline learned for 'weekend' (8-14 Jan: Sat 13, Sun 14) ===")
wk = fl.loc['2018-01-13':'2018-01-14 23:00']
sat, sun = wk[wk.dtype == 'Sat'].set_index('hour').main_out, wk[wk.dtype == 'Sun'].set_index('hour').main_out
base = pd.concat([sat, sun], axis=1).median(axis=1)    # median of 2 values = their average
print("  hour | Sat 13 Jan  Sun 14 Jan  -> weekend profile (= their average)")
for h in [5, 7, 9, 11, 13]:
    print(f"   {h:02d}  | {sat[h]:9.1f} {sun[h]:10.1f}    {base[h]:10.1f}")

print("\n=== 3. Resulting residuals across the year (old baseline) ===")
fl['old_expected'] = [base[h] if d != 'Mon-Fri' else np.nan for d, h in zip(fl.dtype, fl.hour)]
wd = fl.loc['2018-01-08':'2018-01-12 23:00'].groupby('hour').main_out.median()
fl.loc[fl.dtype == 'Mon-Fri', 'old_expected'] = fl.loc[fl.dtype == 'Mon-Fri', 'hour'].map(wd)
fl['old_resid'] = fl.main_out - fl.old_expected
r = fl.loc['2018-01-15':].groupby(['dtype', 'hour']).old_resid.mean()
print("  mean residual 00-04 / 05-11 / 12-23, m3/h:")
for d in ['Mon-Fri', 'Sat', 'Sun']:
    s = r.loc[d]
    print(f"   {d:8s} {s.loc[0:4].mean():7.1f} {s.loc[5:11].mean():7.1f} {s.loc[12:23].mean():7.1f}")

print("\n=== 4. Anatomy of the Sunday 11:00 step (old baseline) ===")
fl['step'] = fl.old_resid.rolling(6).mean() - fl.old_resid.shift(6).rolling(24).mean()
sun11 = fl[(fl.dtype == 'Sun') & (fl.hour == 11)].loc['2018-01-15':]
recent = fl.old_resid.rolling(6).mean().loc[sun11.index]
before = fl.old_resid.shift(6).rolling(24).mean().loc[sun11.index]
print(f"  Sundays 11:00 in window: {len(sun11)}")
print(f"  mean residual, Sun 06-11 (recent window): {recent.mean():+.1f}")
print(f"  mean residual, Sat 06 - Sun 05 (window before): {before.mean():+.1f}")
print(f"  mean step = {sun11.step.mean():+.1f} m3/h; Sundays with step >= 9.10: {(sun11.step>=9.10).sum()} of {len(sun11)}")
for d in ['Mon-Fri', 'Sat']:
    other = fl[(fl.dtype == d) & (fl.hour == 11)].loc['2018-01-15':]
    print(f"  for comparison, {d} 11:00 mean step {other.step.mean():+.1f}, share >= 9.10: {(other.step>=9.10).mean():.0%}")
out['sunday_11'] = {'n': int(len(sun11)), 'mean_recent_resid': round(float(recent.mean()), 2),
                    'mean_before_resid': round(float(before.mean()), 2),
                    'mean_step': round(float(sun11.step.mean()), 2),
                    'share_step_at_least_9_10': round(float((sun11.step >= 9.10).mean()), 3)}
(OUT / 'sunday-diagnosis.json').write_text(json.dumps(out, indent=2) + '\n')
