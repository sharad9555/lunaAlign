# Local setup

Use Python 3.10+ with an OpenCV build that includes SIFT. Install `requirements.txt`, then run:

```powershell
uvicorn backend.api.main:app --reload
```

Visit `http://127.0.0.1:8000`. The API documentation is at `/docs`. No account, cloud service, telemetry, GPU, or model download is required in Phase 1.

If a restricted/offline package index lacks a wheel for your Python version, use a locally available OpenCV build or a supported Python version. The system deliberately has no runtime internet calls.
