"""Step 3 -- ONLY after run/warnings-both-rules.csv is committed: download the repairs file."""
import hashlib, json, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
f = str(HERE / 'run/warnings-both-rules.csv')
tracked = subprocess.run(['git', 'ls-files', f], capture_output=True, text=True, cwd=ROOT).stdout.strip()
dirty = subprocess.run(['git', 'status', '--porcelain', f], capture_output=True, text=True, cwd=ROOT).stdout.strip()
assert tracked and not dirty, 'warning list not committed - stop'
URL = 'https://datamillnorth.org/download/2zlgn/d68be986-2edf-4253-9911-8fe528177579/Mains%20Repairs%202016-17.csv'
dst = ROOT / 'data/yorkshire/Mains_Repairs_2016-17.csv'
subprocess.run(['curl', '-sL', '--fail', '--retry', '5', '-o', str(dst), URL], check=True)
res = {'url': URL, 'bytes': dst.stat().st_size, 'sha256': hashlib.sha256(dst.read_bytes()).hexdigest()}
(HERE / 'run/step3-repairs-download.json').write_text(json.dumps(res, indent=2) + '\n'); print(json.dumps(res, indent=2))
