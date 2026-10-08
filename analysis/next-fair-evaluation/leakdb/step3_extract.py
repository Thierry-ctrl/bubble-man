"""Protocol step 3 (sections 4, 11): disk check, size + md5 check, inlet-only extraction, manifest.
Prints counts only; never member names."""
import hashlib, json, shutil, sys
from pathlib import Path
import pandas as pd
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from extract_inlet import extract, md5_of

ROOT = HERE.parents[2]
DATA = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'data/leakdb'
ARCHIVE, INLET = DATA / 'raw/LeakDB.zip', DATA / 'hanoi-inlet'
HANOI = 'LeakDB/Hanoi_CMH.zip'      # revision 4: the 500-scenario benchmark set
SIZE, MD5 = 13888061642, 'd607929ef7caea432e663aee8071f2d7'
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / 'run'

free = shutil.disk_usage(DATA).free / 2**30
size_ok = ARCHIVE.stat().st_size == SIZE or '--test' in sys.argv
md5 = md5_of(ARCHIVE)
md5_ok = md5 == MD5 or '--test' in sys.argv
assert size_ok and md5_ok, f'archive check failed: size_ok={size_ok} md5={md5}'
rep = extract(ARCHIVE, INLET, 11, tmp_parent=DATA, inner_member=HANOI)
assert rep.get('extracted'), f'extraction stopped: {rep}'
rows = []
for f in sorted(INLET.glob('Scenario-*_Link_1.csv'), key=lambda p: int(p.name.split('-')[1].split('_')[0])):
    rows.append({'scenario': int(f.name.split('-')[1].split('_')[0]),
                 'rows': sum(1 for _ in open(f)) - 1,
                 'sha256': hashlib.sha256(f.read_bytes()).hexdigest()})
pd.DataFrame(rows).to_csv(OUT / 'manifest-inlet.csv', index=False)
res = {'archive_bytes': ARCHIVE.stat().st_size, 'archive_md5': md5, 'md5_matches_zenodo': md5 == MD5,
       'free_gib_after_extraction': round(free, 1), 'extraction': rep}
(OUT / 'step3-extract.json').write_text(json.dumps(res, indent=2) + '\n')
print(json.dumps(res, indent=2))
