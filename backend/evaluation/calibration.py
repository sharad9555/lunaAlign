"""Optional logistic calibration for correspondence confidence.

Training needs labelled true/false correspondences. No calibration model is
invented when labels are unavailable.
"""
from pathlib import Path
import json, numpy as np

def train_logistic(rows, output):
    try:
        from sklearn.linear_model import LogisticRegression
    except ImportError as e: raise RuntimeError('Install scikit-learn to train confidence calibration: pip install scikit-learn') from e
    X=np.asarray([r['features'] for r in rows],dtype=float); y=np.asarray([r['label'] for r in rows],dtype=int)
    if len(np.unique(y))<2: raise ValueError('Calibration data must contain both positive and negative labels')
    model=LogisticRegression(max_iter=2000).fit(X,y)
    payload={'weights':model.coef_[0].tolist(),'bias':float(model.intercept_[0]),'feature_order':['descriptor_distance','reprojection_error','local_error','keypoint_response']}
    Path(output).write_text(json.dumps(payload,indent=2),encoding='utf-8'); return payload
