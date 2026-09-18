import json, sqlite3
from pathlib import Path

class ExperimentDB:
    def __init__(self,path):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True); self.init()
    def connect(self): return sqlite3.connect(self.path)
    def init(self):
        with self.connect() as c:
            c.execute('CREATE TABLE IF NOT EXISTS experiments (id TEXT PRIMARY KEY, created_at TEXT DEFAULT CURRENT_TIMESTAMP, status TEXT, dataset TEXT, source_sensor TEXT, target_sensor TEXT, model TEXT, metrics_json TEXT, metadata_json TEXT, explanation TEXT)')
            c.commit()
    def save(self, result, dataset="UPLOAD"):
        with self.connect() as c:
            c.execute('INSERT OR REPLACE INTO experiments(id,status,dataset,source_sensor,target_sensor,model,metrics_json,metadata_json,explanation) VALUES(?,?,?,?,?,?,?,?,?)', (result.id,result.status,dataset,result.metadata.get('source_sensor'),result.metadata.get('target_sensor'),result.metadata.get('transform_model'),json.dumps(result.metrics),json.dumps(result.metadata),result.explanation)); c.commit()
    def recent(self, limit=50):
        with self.connect() as c: rows=c.execute('SELECT id,created_at,status,dataset,source_sensor,target_sensor,model,metrics_json FROM experiments ORDER BY created_at DESC LIMIT ?', (limit,)).fetchall()
        return [{"id":r[0],"created_at":r[1],"status":r[2],"dataset":r[3],"source_sensor":r[4],"target_sensor":r[5],"model":r[6],"metrics":json.loads(r[7])} for r in rows]
