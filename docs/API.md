# API

`POST /api/register`, `/api/match`, and `/api/evaluate` accept multipart `source`, `target`, `method` (`SIFT` or `ORB`), and `representation` (`raw`, `clahe`, `gradient`, `edge`, or `local_contrast`). They return status, measured internal metrics, explanation, and local result URLs.

`GET /api/health` reports local engine state. `GET /api/result/{id}` retrieves a current-session result. `POST /api/experiment` records validated experiment metadata. `/api/benchmark` deliberately returns 501 until the benchmark phase exists, avoiding fabricated results.
