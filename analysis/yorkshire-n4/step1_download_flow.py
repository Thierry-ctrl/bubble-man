"""Step 1: download the Area N4 flow file only; check its size; record SHA-256."""
import hashlib, json, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
URL = 'https://datamillnorth.org/download/2zlgn/7728e628-f816-4fe4-99f1-648af54df878/N4%202016_2017.csv'
SIZE = 101862786
dst = ROOT / 'data/yorkshire/N4_2016_2017.csv'; dst.parent.mkdir(parents=True, exist_ok=True)
subprocess.run(['curl', '-sL', '--fail', '--retry', '5', '-o', str(dst), URL], check=True)
size = dst.stat().st_size
assert size == SIZE, f'size {size} != published {SIZE} - stop'
res = {'file': 'Area N4 2016_2017.csv', 'url': URL, 'bytes': size,
       'sha256': hashlib.sha256(dst.read_bytes()).hexdigest(), 'licence': 'CC BY 4.0, Yorkshire Water via Data Mill North'}
(HERE / 'run/step1-download.json').write_text(json.dumps(res, indent=2) + '\n'); print(json.dumps(res, indent=2))
