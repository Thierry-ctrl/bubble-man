"""Extract ONLY the Hanoi inlet flow files (Scenario-N/Flows/Link_1.csv) from a LeakDB archive.

Safety rules (PROTOCOL-LEAKDB.md, section 4):
- Member names are read into memory to find matches but are NEVER printed or written,
  because LeakDB names under Leaks/ contain leak node IDs.
- Only paths ending exactly in /Flows/Link_1.csv under a Hanoi scenario are extracted.
- Output is counts and scenario numbers only. Unknown layout -> stop, print counts only.

Usage:
  python extract_inlet.py ARCHIVE OUT_DIR --min-scenario 11 [--md5 HEX --size BYTES]
"""
import argparse, hashlib, re, shutil, sys, tempfile, zipfile
from pathlib import Path

FLOW_IN_HANOI = re.compile(r'(?:^|/)Hanoi_CMH/Scenario-(\d+)/Flows/Link_1\.csv$')
FLOW_IN_INNER = re.compile(r'^(?:[^/]*/)?Scenario-(\d+)/Flows/Link_1\.csv$')
INNER_HANOI = re.compile(r'(?:^|/)Hanoi_CMH\.zip$')


def md5_of(path, chunk=1 << 24):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        while b := f.read(chunk):
            h.update(b)
    return h.hexdigest()


def matches(names, pattern):
    found = {}
    for n in names:
        m = pattern.search(n)
        if m:
            found.setdefault(int(m.group(1)), []).append(n)
    return found


def extract(archive, out_dir, min_scenario, tmp_parent=None):
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    report = {}
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        report['entries_in_archive'] = len(names)
        found, source, inner_tmp = matches(names, FLOW_IN_HANOI), z, None
        report['layout'] = 'flat'
        if not found:
            inner = [n for n in names if INNER_HANOI.search(n)]
            report['inner_hanoi_archives'] = len(inner)
            if len(inner) != 1:
                report['layout'] = 'NOT RECOGNISED - stopped, nothing extracted'
                return report
            inner_tmp = Path(tempfile.mkdtemp(dir=tmp_parent))
            with z.open(inner[0]) as src, open(inner_tmp / 'inner.zip', 'wb') as dst:
                shutil.copyfileobj(src, dst, 1 << 24)
            report['layout'] = 'nested Hanoi_CMH.zip'
            source = zipfile.ZipFile(inner_tmp / 'inner.zip')
            report['entries_in_inner_archive'] = len(source.namelist())
            found = matches(source.namelist(), FLOW_IN_INNER)
        dup = [k for k, v in found.items() if len(v) != 1]
        if dup:
            report['layout'] += f' - STOPPED: {len(dup)} scenarios have more than one inlet file'
            return report
        keep = sorted(k for k in found if k >= min_scenario)
        for k in keep:
            with source.open(found[k][0]) as src, open(out_dir / f'Scenario-{k}_Link_1.csv', 'wb') as dst:
                shutil.copyfileobj(src, dst)
        report.update({
            'scenarios_with_inlet_file': len(found),
            'scenario_range_in_archive': [min(found), max(found)] if found else None,
            'excluded_below_min_scenario': len(found) - len(keep),
            'extracted': len(keep),
            'gaps_in_numbering': sorted(set(range(min(keep), max(keep) + 1)) - set(keep)) if keep else [],
        })
        if inner_tmp:
            source.close(); shutil.rmtree(inner_tmp)
    return report


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('archive'); ap.add_argument('out_dir')
    ap.add_argument('--min-scenario', type=int, required=True)
    ap.add_argument('--md5'); ap.add_argument('--size', type=int)
    a = ap.parse_args()
    if a.size is not None and Path(a.archive).stat().st_size != a.size:
        sys.exit('size mismatch - stopped')
    if a.md5 and md5_of(a.archive) != a.md5:
        sys.exit('md5 mismatch - stopped')
    for k, v in extract(a.archive, a.out_dir, a.min_scenario).items():
        print(f'{k}: {v}')
