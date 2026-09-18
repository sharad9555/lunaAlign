from pathlib import Path
import csv, time
import cv2, numpy as np
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel, Field
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.core.pipeline import register
from backend.evaluation.benchmark import variants, lunar_robustness_score
from backend.core.database import ExperimentDB
from backend.preprocessing.metadata import inspect_path
from backend.core.sensors import profile_for, PROFILES
import json

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "data" / "results"
# Ensure runtime output directories exist before StaticFiles mounts them.
RESULTS.mkdir(parents=True, exist_ok=True)
app = FastAPI(title="LUNALIGN AI", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:8000", "http://localhost:8000", "null"], allow_methods=["*"], allow_headers=["*"])
app.mount("/results", StaticFiles(directory=RESULTS), name="results")
RESULT_INDEX: dict[str, dict] = {}
DB = ExperimentDB(ROOT / "data" / "lunalign.sqlite3")

class ExperimentRequest(BaseModel):
    dataset_identifier: str = Field(min_length=1, max_length=200)
    configuration: dict = Field(default_factory=dict)

def decode(upload: UploadFile):
    if Path(upload.filename or "").suffix.lower() not in {".png", ".jpg", ".jpeg", ".tif", ".tiff"}: raise HTTPException(415, "Supported files: PNG, JPEG, TIFF")
    im = cv2.imdecode(np.frombuffer(upload.file.read(), np.uint8), cv2.IMREAD_UNCHANGED)
    if im is None: raise HTTPException(400, "Unreadable image")
    return im

@app.get("/api/health")
def health(): return {"status": "ok", "processing": "local-only", "engine": "adaptive classical / optional deep fallback", "telemetry": False}

def _json_form(value, default=None):
    if not value: return default
    try: return json.loads(value)
    except Exception as e: raise HTTPException(422, "metadata/calibration must be valid JSON") from e

@app.post("/api/register")
def api_register(source: UploadFile = File(...), target: UploadFile = File(...), method: str = Form("SIFT"), representation: str = Form("auto"), performance_mode: str = Form("BALANCED"), source_sensor: str = Form("UNKNOWN"), target_sensor: str = Form("UNKNOWN"), grid: int = Form(8), source_band: int | None = Form(None), target_band: int | None = Form(None), source_solar_azimuth: float | None = Form(None), source_solar_elevation: float | None = Form(None), target_solar_azimuth: float | None = Form(None), target_solar_elevation: float | None = Form(None), allow_homography: bool = Form(True), dataset_identifier: str = Form("UPLOAD"), calibration_json: str | None = Form(None)):
    if not 2 <= grid <= 32: raise HTTPException(422, "grid must be between 2 and 32")
    if source_band is not None and source_band < 0 or target_band is not None and target_band < 0: raise HTTPException(422, "band indexes must be non-negative")
    try:
        result = register(decode(source), decode(target), RESULTS, method.upper(), representation, performance_mode, source_sensor, target_sensor, grid, source_band, target_band, sun_source=(source_solar_azimuth,source_solar_elevation) if source_solar_azimuth is not None and source_solar_elevation is not None else None, sun_target=(target_solar_azimuth,target_solar_elevation) if target_solar_azimuth is not None and target_solar_elevation is not None else None, allow_homography=allow_homography, calibration=_json_form(calibration_json))
    except (ValueError, cv2.error) as e: raise HTTPException(400, str(e))
    payload=result.__dict__.copy(); payload["urls"]={k:"/results/"+result.id+"/"+Path(v).name for k,v in result.paths.items()}
    RESULT_INDEX[result.id]=payload; DB.save(result,dataset_identifier)
    return payload

@app.post("/api/match")
def api_match(source: UploadFile = File(...), target: UploadFile = File(...), method: str = Form("SIFT"), representation: str = Form("auto")):
    """Phase-1 matching uses the same verified correspondence computation as registration."""
    return api_register(source, target, method, representation)

@app.post("/api/evaluate")
def api_evaluate(source: UploadFile = File(...), target: UploadFile = File(...), method: str = Form("SIFT"), representation: str = Form("auto")):
    """Returns measured baseline metrics for one pair; no unrun benchmark values."""
    return api_register(source, target, method, representation)

@app.post("/api/benchmark")
def api_benchmark(reference: UploadFile = File(...), method: str = Form("SIFT")):
    """Controlled robustness test; outputs measured synthetic-perturbation results, never lunar validation claims."""
    image = decode(reference); rows=[]; started=time.perf_counter()
    for name, altered in variants(image).items():
        result=register(image,altered,RESULTS,method,"auto","FAST")
        rows.append({"variant":name,"status":result.status,"metrics":result.metrics})
    report_id=f"benchmark-{int(time.time())}"; report_dir=RESULTS/report_id; report_dir.mkdir(exist_ok=True)
    with (report_dir/"benchmark.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=["variant","status","inliers","inlier_ratio","rmse_px","spatial_coverage","processing_time_s"]); writer.writeheader()
        for row in rows: writer.writerow({"variant":row["variant"],"status":row["status"],**{k:row["metrics"].get(k) for k in writer.fieldnames[2:]}})
    return {"benchmark_id":report_id,"rows":rows,"lunar_robustness_score":lunar_robustness_score(rows),"elapsed_s":round(time.perf_counter()-started,2),"csv_url":f"/results/{report_id}/benchmark.csv","disclaimer":"LRS is an engineering stress-test metric, not an official ISRO metric or lunar ground-truth accuracy."}

@app.post("/api/experiment")
def api_experiment(request: ExperimentRequest):
    return {"status": "RECORDED", "dataset_identifier": request.dataset_identifier,
            "configuration": request.configuration, "note": "Experiment execution is linked to the evaluation phase."}

@app.get("/api/history")
def api_history(limit: int = 50):
    return {"rows": DB.recent(max(1,min(limit,200)))}

@app.get("/api/sensors")
def api_sensors():
    return {"sensors": {k: profile_for(k).__dict__ for k in PROFILES}}

@app.post("/api/inspect-metadata")
def api_inspect_metadata(image: UploadFile = File(...)):
    suffix=Path(image.filename or "image.bin").suffix.lower()
    if suffix not in {".png",".jpg",".jpeg",".tif",".tiff"}: raise HTTPException(415,"Supported files: PNG, JPEG, TIFF")
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=suffix,delete=False) as f:
        f.write(image.file.read()); temp=f.name
    try: return {"filename":image.filename,"metadata":inspect_path(temp)}
    finally:
        try: Path(temp).unlink()
        except Exception: pass

@app.get("/api/result/{result_id}")
def api_result(result_id: str):
    if result_id not in RESULT_INDEX: raise HTTPException(404, "Result not found; results are retained only while this local server runs.")
    return RESULT_INDEX[result_id]

# Kept last so API routes take precedence; browse to the local server for the dashboard.
app.mount("/", StaticFiles(directory=ROOT / "frontend", html=True), name="frontend")
