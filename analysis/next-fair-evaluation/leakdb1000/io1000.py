"""Readers for the 1,000-scenario set (correction 1, 10 Oct 2026; see PROTOCOL-LEAKDB-1000.md §10).

The 1,000-scenario files carry a step counter instead of timestamps: header "Index,Value",
Index = 1..17520, one per 30 minutes. The 500-scenario files carry "Timestamp,Value". The
method uses only position in the series (weekday = day index mod 7), so step n is placed at a
NOMINAL time ORIGIN + (n-1) x 30 min. The origin has no effect on any warning or score.
Timestamp-format files pass through unchanged to the frozen reader."""
from __future__ import annotations
import io, sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'leakdb'))
import method as M
from scoring import read_info

ORIGIN = pd.Timestamp('2017-01-01 00:00')
N = 365 * 48


def _index_to_stamps(idx):
    idx = pd.to_numeric(idx, errors='coerce')
    assert idx.notna().all() and np.array_equal(idx.values, np.arange(1, len(idx) + 1)), \
        'Index column is not 1..N consecutive - stop'
    return ORIGIN + pd.to_timedelta((idx.values - 1) * 30, unit='min')


def read_inlet(path) -> pd.Series:
    raw = pd.read_csv(path)
    if list(raw.columns) == ['Index', 'Value']:
        conv = pd.DataFrame({'Timestamp': _index_to_stamps(raw.Index), 'Value': raw.Value})
        return M.read_inlet(conv.to_csv(index=False).encode())
    return M.read_inlet(path)


def read_leaks(leak_dir: Path, grid: pd.DatetimeIndex) -> pd.DataFrame:
    """As leakdb/scoring.read_leaks, accepting Index- or Timestamp-format leak files. Activity
    is placed on the inlet grid by row position; the format check is recorded."""
    rows = []
    for f in sorted(Path(leak_dir).glob('Leak_*_demand.csv')):
        node = f.name[len('Leak_'):-len('_demand.csv')]
        info = read_info((f.parent / f'Leak_{node}_info.csv').read_text())
        d = pd.read_csv(f)
        v = pd.to_numeric(d.iloc[:, 1], errors='coerce').values
        assert len(v) == len(grid), f'leak file length {len(v)} != inlet grid {len(grid)}'
        first = d.columns[0]
        if first == 'Index':
            agree = bool(np.array_equal(pd.to_numeric(d.iloc[:, 0], errors='coerce').values, np.arange(1, len(v) + 1)))
        else:
            agree = bool((pd.to_datetime(d.iloc[:, 0]).values == grid.values).all())
        pos = np.flatnonzero(v > 0)
        kind = info.get('Leak Type', '').strip().lower()
        assert kind in ('abrupt', 'incipient'), f'unexpected leak type {kind!r}'
        rows.append({'link': node, 'type': kind, 'zone': 'hanoi',
                     'start': grid[pos[0]] if len(pos) else pd.NaT, 'end': grid[pos[-1]] if len(pos) else pd.NaT,
                     'info_start': info.get('Leak Start'), 'diameter_m': float(info.get('Leak Diameter', 'nan')),
                     'file_index_format': first, 'positions_agree_with_inlet': agree, 'never_flowed': len(pos) == 0})
    cols = ['link', 'type', 'zone', 'start', 'end', 'info_start', 'diameter_m', 'file_index_format',
            'positions_agree_with_inlet', 'never_flowed']
    return pd.DataFrame(rows, columns=cols)
