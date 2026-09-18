import argparse, json
from backend.evaluation.calibration import train_logistic
p=argparse.ArgumentParser(); p.add_argument('input'); p.add_argument('output'); a=p.parse_args()
rows=json.load(open(a.input,encoding='utf-8')); print(json.dumps(train_logistic(rows,a.output),indent=2))
