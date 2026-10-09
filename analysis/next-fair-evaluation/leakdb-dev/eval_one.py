import json, sys
from evaluate import evaluate, HERE, pd
kind, start = sys.argv[1], int(sys.argv[2])
res, per, sh = evaluate(kind, start)
pd.DataFrame(per).to_csv(HERE / f'dev-per-scenario-{kind}-from{start + 1}.csv', index=False)
sh.to_csv(HERE / f'dev-shifts-{kind}-from{start + 1}.csv', index=False)
(HERE / f'dev-result-{kind}-from{start + 1}.json').write_text(json.dumps(res, indent=2) + '\n'); print(json.dumps(res))
