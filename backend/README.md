# Making Death Count — local API

The dashboard can run as a single process: FastAPI serves the SQLite API **and** the static files (`index.html`, `index.css`, `assets/`, `public/`).

GitHub Pages is unchanged. The frontend still has the inline `DATA` object and uses it when `/api/dataset/2023` is unavailable.

## Start

```
cd backend
pip install -r requirements.txt
python seed.py
uvicorn main:app --reload --port 8001
```

If `uvicorn` is not on your PATH, use `python -m uvicorn main:app --reload --port 8001`.

Then open **http://localhost:8001/** (app + API).

`python seed.py` is idempotent: it recreates the 2023 rows. If the database is empty, the API also seeds 2023 on startup.

Do not commit `backend/data/mortality.db` or secrets.

## API

| Method | URL | Notes |
| --- | --- | --- |
| GET | http://localhost:8001/api/health | Liveness |
| GET | http://localhost:8001/api/dataset/2023 | Full dashboard payload (causes, details, sex, months, places, summary) |
| GET | http://localhost:8001/api/causes?year=2023 | Causes only |

CORS is enabled for `localhost` / `127.0.0.1`.

## Two servers (optional)

A static server on port 8000 still works for GitHub Pages–style testing. Relative fetch of `/api/dataset/2023` will fail there, so the page falls back to the inline data. For live API data, use port **8001** (one process) rather than mixing 8000 + 8001.
