"""Step 2 of PROTOCOL-LEAKDB-1000.md section 3: verify archive, extract ONLY inlet files of
LeakDB/Hanoi_CMH_1000scenarios.zip (all scenarios), manifest. Counts only, never names."""
import hashlib, json, shutil, sys
from pathlib import Path
import pandas as pd
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE.parent / 'leakdb'))
from extract_inlet import extract, md5_of
ROOT = HERE.parents[2]
DATA = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'data/leakdb'
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / 'run'
ARCHIVE, INLET = DATA / 'raw/LeakDB.zip', DATA / 'hanoi1000-inlet'
SET = 'LeakDB/Hanoi_CMH_1000scenarios.zip'
SIZE, MD5 = 13888061642, 'd607929ef7caea432e663aee8071f2d7'
test = '--test' in sys.argv
assert test or (ARCHIVE.stat().st_size == SIZE and md5_of(ARCHIVE) == MD5), 'archive check failed - stop'
assert not INLET.exists() or not any(INLET.iterdir()), 'inlet folder not empty - stop'
rep = extract(ARCHIVE, INLET, 1, tmp_parent=DATA, inner_member=SET)
assert rep.get('extracted'), f'extraction stopped: {rep}'
rows = [{'scenario': int(f.name.split('-')[1].split('_')[0]), 'rows': sum(1 for _ in open(f)) - 1,
         'sha256': hashlib.sha256(f.read_bytes()).hexdigest()} for f in INLET.glob('Scenario-*_Link_1.csv')]
pd.DataFrame(rows).sort_values('scenario').to_csv(OUT / 'manifest-inlet.csv', index=False)
res = {'archive_md5_verified': not test, 'set': SET, 'extraction': rep,
       'free_gib': round(shutil.disk_usage(DATA).free / 2**30, 1)}
(OUT / 'step3-extract.json').write_text(json.dumps(res, indent=2) + '\n'); print(json.dumps(res, indent=2))
