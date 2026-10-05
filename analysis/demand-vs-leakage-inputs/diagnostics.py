"""Three diagnostics on live-available inputs. 2018 only; 2019 not read.

Live inputs used: inlet and pump flow, tank level, Area C customer meters, calendar.
Labelled leak flow appears ONLY in the retrospective checks marked RETRO, never in
anything a live warning would compute. No detector is built or tuned.

D1  Area C water balance: does "inflow minus metered consumption" isolate losses?
D2  Can Area C metered demand explain the main zone's non-labelled-leak remainder?
D3  Does night flow separate leakage from demand change in the main zone?
"""
import json, math
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
W = ('2018-01-15', '2018-12-31 23:00')
AREA = math.pi * (16.0 / 2) ** 2

def read(p):
    return pd.read_csv(ROOT / p, sep=';', decimal=',', parse_dates=['Timestamp']).set_index('Timestamp')

flows = read('data/l-town/readings/2018_SCADA_Flows.csv').resample('h').mean()
level = read('data/l-town/readings/2018_SCADA_Levels.csv')['T1'].resample('h').first()
amr = read('data/l-town/readings/2018_SCADA_Demands.csv').sum(axis=1).resample('h').mean() / 1000.0  # L/h -> m3/h
truth = read('data/l-town/reference/2018_Leakages.csv')
zones = dict(pd.read_csv(ROOT / 'analysis/scorer/leak-zones-from-network-map.csv')[['link', 'zone']].values)
leak_main = truth[[c for c in truth if zones.get(c) == 'main']].sum(axis=1).resample('h').mean()
leak_c = truth[[c for c in truth if zones.get(c) == 'AreaC']].sum(axis=1).resample('h').mean()

main_out = flows.p227 + flows.p235 - flows.PUMP_1
areaC_out = flows.PUMP_1 - (level.shift(-1) - level) * AREA      # hourly, forward pairing (see WATER-ACCOUNTING)

def group(ix):  # the frozen repaired grouping
    return np.where(ix.dayofweek == 5, 'Sat', np.where(ix.dayofweek == 4, 'Fri', 'SunThu'))

def expected(series):
    f = series.to_frame('v'); f['g'] = group(f.index); f['h'] = f.index.hour
    p = f.loc['2018-01-01':'2018-01-14 23:00'].groupby(['g', 'h'])['v'].median()
    return pd.Series([p.loc[(g, h)] for g, h in zip(f.g, f.h)], index=f.index)

res = {}
# ---------------- D1: Area C water balance ----------------------------------
unmetered_c = (areaC_out - amr).loc[W[0]:W[1]]                     # live: inflow - metered
monthly = pd.DataFrame({'areaC_outflow': areaC_out, 'metered_amr': amr, 'unmetered': areaC_out - amr,
                        'RETRO_labelled_areaC_leak': leak_c}).loc[W[0]:W[1]].resample('MS').mean()
res['D1'] = {
    'meters_in_area_c': 82, 'meters_in_main_zone': 0,
    'monthly_m3_per_hour': {str(k.date()): {kk: round(v, 2) for kk, v in r.items()} for k, r in monthly.iterrows()},
    'RETRO_weekly_corr_unmetered_vs_labelled_leak': round(float(
        unmetered_c.resample('W').mean().corr(leak_c.loc[W[0]:W[1]].resample('W').mean())), 3),
    'RETRO_mean_unmetered_minus_labelled_leak': round(float((unmetered_c - leak_c.loc[W[0]:W[1]]).mean()), 2),
    'jan_1_14_unmetered_mean': round(float((areaC_out - amr).loc['2018-01-01':'2018-01-07 23:00'].mean()), 2),
}

# ---------------- D2: metered demand as a reference for the main zone -------
exp_main, exp_amr = expected(main_out), expected(amr)
remainder = (main_out - exp_main - leak_main).loc[W[0]:W[1]]        # RETRO: needs leak truth
weekly = pd.DataFrame({'main_expected': exp_main, 'amr': amr, 'amr_expected': exp_amr,
                       'remainder_RETRO': remainder, 'leak_main_RETRO': leak_main,
                       'excess': main_out - exp_main}).loc[W[0]:W[1]].resample('W-SUN').mean()
weekly['amr_index'] = weekly.amr / weekly.amr_expected                 # live
weekly['predicted_demand_change'] = weekly.main_expected * (weekly.amr_index - 1)   # live
fit = weekly.dropna()
r = float(fit.predicted_demand_change.corr(fit.remainder_RETRO))
unexplained = fit.remainder_RETRO - fit.predicted_demand_change
res['D2'] = {
    'amr_index_by_month': {str(k.date()): round(float(v), 3) for k, v in
                           (amr / exp_amr).loc[W[0]:W[1]].resample('MS').mean().items()},
    'RETRO_weekly_corr_predicted_vs_remainder': round(r, 3),
    'RETRO_remainder_mean': round(float(fit.remainder_RETRO.mean()), 2),
    'predicted_demand_change_mean': round(float(fit.predicted_demand_change.mean()), 2),
    'RETRO_remainder_left_after_demand_mean': round(float(unexplained.mean()), 2),
    'RETRO_remainder_left_after_demand_abs_mean': round(float(unexplained.abs().mean()), 2),
    'RETRO_share_of_remainder_variance_explained': round(float(1 - unexplained.var() / fit.remainder_RETRO.var()), 3),
}
# what would excess look like after removing the metered-demand prediction (live), vs labelled leak (RETRO)
fit['excess_after_demand'] = fit.excess - fit.predicted_demand_change
res['D2']['RETRO_weekly_corr_excess_vs_leak'] = round(float(fit.excess.corr(fit.leak_main_RETRO)), 3)
res['D2']['RETRO_weekly_corr_excess_after_demand_vs_leak'] = round(float(fit.excess_after_demand.corr(fit.leak_main_RETRO)), 3)
fit.to_csv(OUT / 'weekly-demand-reference.csv', index_label='week_ending')

# ---------------- D3: night flow ---------------------------------------------
excess_h = (main_out - exp_main).loc[W[0]:W[1]]
night = excess_h[excess_h.index.hour.isin([2, 3])].resample('W-SUN').mean()
day = excess_h[excess_h.index.hour.isin(range(8, 20))].resample('W-SUN').mean()
lw = leak_main.loc[W[0]:W[1]].resample('W-SUN').mean()
amr_night_ratio = (amr / exp_amr).loc[W[0]:W[1]]
res['D3'] = {
    'RETRO_weekly_corr_with_labelled_leak': {'night_02_04': round(float(night.corr(lw)), 3),
                                             'day_08_20': round(float(day.corr(lw)), 3)},
    'RETRO_mean_night_excess_minus_leak': round(float((night - lw).mean()), 2),
    'RETRO_mean_day_excess_minus_leak': round(float((day - lw).mean()), 2),
    'metered_demand_seasonal_rise_jul_vs_jan': {
        'night_02_04': round(float(amr_night_ratio[(amr_night_ratio.index.month == 7) & amr_night_ratio.index.hour.isin([2, 3])].mean()), 3),
        'day_08_20': round(float(amr_night_ratio[(amr_night_ratio.index.month == 7) & amr_night_ratio.index.hour.isin(range(8, 20))].mean()), 3)},
}
pd.DataFrame({'night_excess': night, 'day_excess': day, 'labelled_leak_RETRO': lw}).to_csv(
    OUT / 'weekly-night-day.csv', index_label='week_ending')
(OUT / 'diagnostics.json').write_text(json.dumps(res, indent=2) + '\n')

print("D1 Area C balance (monthly m3/h): outflow / metered / unmetered / RETRO labelled Area C leak")
for k, v in res['D1']['monthly_m3_per_hour'].items():
    print(f"   {k[:7]}  {v['areaC_outflow']:6.2f} {v['metered_amr']:6.2f} {v['unmetered']:6.2f} {v['RETRO_labelled_areaC_leak']:6.2f}")
print(f"   RETRO weekly corr unmetered vs labelled leak: {res['D1']['RETRO_weekly_corr_unmetered_vs_labelled_leak']}"
      f"   mean gap {res['D1']['RETRO_mean_unmetered_minus_labelled_leak']}   (1-7 Jan, no Area C leak: {res['D1']['jan_1_14_unmetered_mean']})")
print("\nD2 metered-demand index by month:", res['D2']['amr_index_by_month'])
print({k: v for k, v in res['D2'].items() if k != 'amr_index_by_month'})
print("\nD3 night vs day:", res['D3'])
