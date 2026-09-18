# Security and privacy

LUNALIGN AI processes files on the local machine. The backend has no outbound network code, telemetry, analytics, account system, or cloud storage. Uploaded images are decoded in memory; generated products are written only under `data/results/`.

The API validates extension and decodeability, bounds coverage-grid input, and exposes only result IDs created in the running process. For shared-network deployment, add authentication, size limits, isolated job directories, malware scanning, and strict CORS; the supplied server is intended for trusted local use.
