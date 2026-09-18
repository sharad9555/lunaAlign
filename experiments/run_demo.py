"""Run local normal and intentional-failure synthetic demos without any download."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.core.demo import lunar_like_pair
from backend.core.pipeline import register

for label, failure in (("success",False),("failure",True)):
    source,target=lunar_like_pair(failure)
    result=register(source,target,Path("data/results"),"SIFT","auto","BALANCED","SYNTHETIC","SYNTHETIC")
    print(label, result.id, result.status, result.metrics)
