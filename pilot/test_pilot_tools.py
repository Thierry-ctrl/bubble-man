"""Tests for the pilot input tools on INVENTED data only."""
import json, shutil, sys, tempfile
from pathlib import Path
import numpy as np
import pandas as pd
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import convert_utility_data as C
import run_frozen_rule as F
EX = HERE / 'example-INVENTED'
res = []
def check(n, ok): res.append(bool(ok)); print(('PASS ' if ok else 'FAIL ') + n)

with tempfile.TemporaryDirectory() as t:
    t = Path(t)
    rep = C.convert(EX, t / 'o')
    out = pd.read_csv(t / 'o/zone_net_inflow_30min.csv', parse_dates=['Timestamp']).set_index('Timestamp').Value
    fr = pd.read_csv(EX / 'INVENTED-flow_readings.csv')
    inl = fr[fr.meter_id == 'ZN-IN-01'].copy(); inl['t'] = pd.to_datetime(inl.timestamp).dt.tz_localize(None)
    tot = fr[fr.meter_id == 'ZN-OUT-01'].copy(); tot['t'] = pd.to_datetime(tot.timestamp).dt.tz_localize(None)
    a = inl.set_index('t').value * 3.6
    v = tot.set_index('t').value; o = (v.diff() / 0.25).shift(-1)
    want = (a.loc['2026-03-02 02:00':'2026-03-02 02:15'].mean() - o.loc['2026-03-02 02:00':'2026-03-02 02:15'].mean())
    check('units: L/s x 3.6, cumulative m3 differenced per interval; net = inlet - outlet (02:00 bin)',
          abs(out.loc['2026-03-02 02:00'] - round(want, 3)) < 1e-3)
    check('fault + estimated readings -> that 30-min bin missing (10:00 day 1)', np.isnan(out.loc['2026-03-02 10:00']))
    check('two missing readings -> bin missing (06:00 day 2)', np.isnan(out.loc['2026-03-03 06:00']))
    check('report lists the quality problems', any('quality flag' in p for p in rep['problems']))
    check('2 days -> not assessable by the frozen method (needs about a year)', rep['readiness']['likely_assessable_by_frozen_method'] is False)
    rep2 = C.convert(EX, t / 'o2', accept_estimated=True)
    check('--accept-estimated keeps the estimated reading but still drops the fault', rep2['meters']['ZN-IN-01']['complete_30min_bins'] == 94)

    # malformed exports are refused with a clear reason
    def variant(name, fn):
        d = t / name; shutil.copytree(EX, d); fn(d)
        try: C.convert(d, t / (name + '_o')); return None
        except C.ExportError as e: return str(e)
    def no_offset(d):
        f = d / 'INVENTED-flow_readings.csv'; x = pd.read_csv(f); x['timestamp'] = x.timestamp.str[:19]; x.to_csv(f, index=False)
    check('timestamps without UTC offset -> refused', 'explicit UTC offset' in (variant('nooff', no_offset) or ''))
    def intermittent(d):
        f = d / 'INVENTED-zone.csv'; x = pd.read_csv(f, dtype=str); x['supply_regime'] = 'intermittent'; x.to_csv(f, index=False)
    d = t / 'inter'; shutil.copytree(EX, d); intermittent(d)
    check('intermittent supply -> UNSUITABLE flag', any('UNSUITABLE' in f for f in C.convert(d, t / 'inter_o')['suitability_flags']))
    def storage(d):
        f = d / 'INVENTED-zone.csv'; x = pd.read_csv(f, dtype=str); x['internal_storage'] = 'tank 500 m3'; x.to_csv(f, index=False)
    check('internal storage -> refused unless explicitly allowed', 'internal storage' in (variant('stor', storage) or ''))
    def reset(d):
        f = d / 'INVENTED-flow_readings.csv'; x = pd.read_csv(f); i = x[x.meter_id == 'ZN-OUT-01'].index[100]; x.loc[i, 'value'] = 5.0; x.to_csv(f, index=False)
    d = t / 'reset'; shutil.copytree(EX, d); reset(d)
    check('cumulative total reset -> flagged and treated as missing', any('reset' in p for p in C.convert(d, t / 'reset_o')['problems']))
    def utc(d):
        f = d / 'INVENTED-flow_readings.csv'; x = pd.read_csv(f)
        x['timestamp'] = (pd.to_datetime(x.timestamp, utc=True)).dt.strftime('%Y-%m-%dT%H:%M:%S+00:00'); x.to_csv(f, index=False)
    d = t / 'utc'; shutil.copytree(EX, d); utc(d)
    o2 = pd.read_csv(C.convert(d, t / 'utc_o') and t / 'utc_o/zone_net_inflow_30min.csv')
    check('readings exported in UTC give the same local-time series', o2.equals(pd.read_csv(t / 'o/zone_net_inflow_30min.csv')))

    # a long invented year: converter output runs through the UNCHANGED rules
    rng = np.random.default_rng(1)
    g = pd.date_range('2025-01-06 00:00', periods=365 * 96, freq='15min')
    hh = np.asarray(g.hour + g.minute / 60)
    ls = 25 + 15 * np.sin((hh - 7) / 24 * 2 * np.pi) + rng.normal(0, 0.5, len(g))
    ls[200 * 96:] += 3.0                                   # an invented step
    d = t / 'year'; d.mkdir()
    pd.DataFrame({'meter_id': 'IN', 'timestamp': [x.strftime('%Y-%m-%dT%H:%M:%S+02:00') for x in g],
                  'value': ls.round(3), 'unit': 'L/s', 'quality': 'ok'}).to_csv(d / 'flow_readings.csv', index=False)
    (d / 'meters.csv').write_text('meter_id,role,zone_id,value_type,unit,interval_minutes,timestamp_marks\nIN,inlet,Z,instantaneous_rate,L/s,15,reading_time\n')
    (d / 'zone.csv').write_text('zone_id,supply_regime,internal_storage,storage_level_meter,boundary_valves_confirmed_closed,local_time_zone\nZ,continuous,none,,yes,UTC+02:00\n')
    ry = C.convert(d, t / 'year_o')
    check('invented year: likely assessable', ry['readiness']['likely_assessable_by_frozen_method'])
    summ = F.run(t / 'year_o/zone_net_inflow_30min.csv', t / 'year_run')
    direct = F.R.both_rules(F.R.M.read_inlet(t / 'year_o/zone_net_inflow_30min.csv'))
    w = pd.read_csv(t / 'year_run/warnings.csv')
    check('wrapper output equals the unchanged rules run directly (frozen rule preserved)',
          summ['assessable'] and len(w[w.rule == 'frozen']) == len(direct[1]) and len(w[w.rule == 'adaptive']) == len(direct[2]))
    check('the invented +3 L/s step on day 201 draws a warning within 7 nights (both rules)',
          all(((pd.to_datetime(w[w.rule == r].night_of) - pd.Timestamp('2025-01-06')).dt.days.between(200, 207)).any() for r in ('frozen', 'adaptive')))
print(f'{sum(res)}/{len(res)} checks pass'); sys.exit(0 if all(res) else 1)
