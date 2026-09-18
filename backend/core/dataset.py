from pathlib import Path
import json, shutil

SUPPORTED={'.png','.jpg','.jpeg','.tif','.tiff','.jp2'}

def manifest(folder):
    p=Path(folder); rows=[]
    for f in sorted(p.rglob('*')):
        if f.is_file() and f.suffix.lower() in SUPPORTED:
            side=f.with_suffix('.json'); meta={}
            if side.exists():
                try: meta=json.loads(side.read_text(encoding='utf-8'))
                except Exception: pass
            rows.append({"path":str(f),"filename":f.name,"metadata":meta})
    return rows

def import_pair(source,target,destination,metadata=None):
    d=Path(destination); d.mkdir(parents=True,exist_ok=True); s=Path(source); t=Path(target)
    shutil.copy2(s,d/'source'+s.suffix.lower()); shutil.copy2(t,d/'target'+t.suffix.lower())
    if metadata: (d/'pair.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    return str(d)
