"""DEVELOPMENT helpers on the 490 already-scored LeakDB Hanoi scenarios (11-500).
Leak labels are used here for retrospective explanation only."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
HERE = Path(__file__).resolve().parent
LDB = HERE.parent / 'leakdb'; RUN = LDB / 'run'
sys.path.insert(0, str(LDB))
import method as M
import scoring as S
ROOT = HERE.parents[2]
INLET = ROOT / 'data/leakdb/hanoi-inlet'; LEAKS = ROOT / 'data/leakdb/hanoi-leaks'

A = pd.read_csv(RUN / 'scenarios-assessability.csv')
L = pd.read_csv(RUN / 'leaks-table.csv', parse_dates=['start', 'end'])
W = pd.read_csv(RUN / 'warnings-all-runs.csv')
W1 = W[W.run == 'Q1_selfaligning_plain']

def inlet(k): return M.read_inlet(INLET / f'Scenario-{k}_Link_1.csv')

def leak_flow(k, grid):
    """Total and per-leak leak flow (m3/h) on the inlet grid -- labels, retrospective only."""
    out = {}
    for f in sorted((LEAKS / f'Scenario-{k}').glob('Leak_*_demand.csv')):
        v = pd.to_numeric(pd.read_csv(f).iloc[:, 1], errors='coerce').values
        out[f.name[5:-11]] = pd.Series(v, index=grid)
    return out
