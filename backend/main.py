from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from database import get_db, init_db
from models import Cause, Dataset
from seed import seed_if_empty

ROOT = Path(__file__).resolve().parent.parent

# Same palette as the dashboard DATA object (presentation, not report counts).
COLORS = [
    "#e53935",
    "#43a047",
    "#f9a825",
    "#00acc1",
    "#1a3a6b",
    "#8e24aa",
    "#fb8c00",
    "#3949ab",
    "#00897b",
    "#6d4c41",
    "#78909c",
]


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    seed_if_empty()
    yield


app = FastAPI(
    title="Making Death Count API",
    description="Mortality dashboard API for the Vanuatu 2023 RCS causes of death brief.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


def _load_dataset(db: Session, year: int) -> Dataset:
    dataset = db.scalar(
        select(Dataset)
        .where(Dataset.year == year)
        .options(
            selectinload(Dataset.causes).selectinload(Cause.details),
            selectinload(Dataset.sex_causes),
            selectinload(Dataset.sex_totals),
            selectinload(Dataset.months),
            selectinload(Dataset.places),
        )
    )
    if dataset is None:
        raise HTTPException(status_code=404, detail=f"No dataset for year {year}")
    return dataset


def serialize_causes(dataset: Dataset) -> list[dict]:
    return [
        {
            "name": cause.name,
            "code": cause.icd10_code,
            "deaths": cause.deaths,
            "pct": cause.pct,
            "detail": [
                {"name": d.name, "deaths": d.deaths, "share": d.share_text}
                for d in cause.details
            ],
        }
        for cause in dataset.causes
    ]


def serialize_dataset(dataset: Dataset) -> dict:
    sex: dict[str, dict] = {}
    for total in dataset.sex_totals:
        rows = [row for row in dataset.sex_causes if row.sex == total.sex]
        rows.sort(key=lambda r: (-r.deaths, r.name))
        sex[total.sex] = {
            "total": total.deaths,
            "top": [{"name": r.name, "deaths": r.deaths, "pct": r.pct} for r in rows],
        }

    return {
        "year": dataset.year,
        "total": dataset.deaths_analysed,
        "colors": COLORS,
        "summary": {
            "year": dataset.year,
            "title": dataset.title,
            "records_submitted": dataset.records_submitted,
            "stillbirths_removed": dataset.stillbirths_removed,
            "deaths_analysed": dataset.deaths_analysed,
            "expected_annual_deaths": dataset.expected_annual_deaths,
            "coverage_pct": dataset.coverage_pct,
            "notes": dataset.notes,
        },
        "causes": serialize_causes(dataset),
        "sex": sex,
        "months": [
            {"month": m.month, "label": m.label, "deaths": m.deaths}
            for m in dataset.months
        ],
        "places": [
            {
                "id": p.place_id,
                "label": p.label,
                "deaths": p.deaths,
                "pct": p.pct,
                "note": p.note,
            }
            for p in dataset.places
        ],
    }


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/dataset/{year}")
def get_dataset(year: int, db: Session = Depends(get_db)):
    return serialize_dataset(_load_dataset(db, year))


@app.get("/api/causes")
def get_causes(year: int = Query(2023), db: Session = Depends(get_db)):
    dataset = _load_dataset(db, year)
    return {
        "year": dataset.year,
        "total": dataset.deaths_analysed,
        "causes": serialize_causes(dataset),
    }


def _root_file(name: str, media_type: str | None = None) -> FileResponse:
    path = ROOT / name
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"{name} not found")
    kwargs = {"path": path}
    if media_type:
        kwargs["media_type"] = media_type
    return FileResponse(**kwargs)


@app.get("/")
def serve_index():
    return _root_file("index.html")


@app.get("/index.html")
def serve_index_html():
    return _root_file("index.html")


@app.get("/index.css")
def serve_css():
    return _root_file("index.css", media_type="text/css")


@app.get("/sw.js")
def serve_sw():
    return _root_file("sw.js", media_type="text/javascript")


@app.get("/manifest.webmanifest")
def serve_manifest():
    return _root_file("manifest.webmanifest", media_type="application/manifest+json")


assets_dir = ROOT / "assets"
if assets_dir.is_dir():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

public_dir = ROOT / "public"
if public_dir.is_dir():
    app.mount("/public", StaticFiles(directory=str(public_dir)), name="public")
