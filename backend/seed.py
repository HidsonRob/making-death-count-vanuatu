"""Idempotent seed of the 2023 RCS mortality brief figures from the dashboard DATA object."""

from sqlalchemy import select

from database import SessionLocal, init_db
from models import Cause, CauseDetail, Dataset, MonthlyDeath, Place, SexCause, SexTotal

# Numbers copied from index.html DATA — do not invent extra counts.
SEED_2023 = {
    "year": 2023,
    "title": "Vanuatu: Causes of Death Analysis (January–December 2023)",
    "records_submitted": 517,
    "stillbirths_removed": 33,
    "deaths_analysed": 484,
    "expected_annual_deaths": 2327,
    "coverage_pct": 20.7,
    "notes": (
        "This dataset includes only deaths recorded through Vanuatu National Hospital "
        "and primarily covers Port Vila and surrounding areas. Coverage is based on "
        "~2,327 expected deaths (2020 census CDR 7.8 per 1,000). It represents an "
        "estimated 20.7% of expected annual deaths and should not be treated as a national total."
    ),
    "causes": [
        {
            "name": "Diseases of the circulatory system",
            "code": "I00–I99",
            "deaths": 125,
            "pct": 25.8,
            "detail": [
                {"name": "Ischaemic heart diseases (I20–I25)", "deaths": 59, "share": "47.2% of chapter"},
                {"name": "Cerebrovascular diseases (I60–I69)", "deaths": 28, "share": "22.4% of chapter"},
                {"name": "Hypertensive diseases (I10–I15)", "deaths": 23, "share": "18.4% of chapter"},
                {"name": "Other forms of heart disease (I30–I52)", "deaths": 10, "share": "8.0% of chapter"},
                {"name": "Chronic rheumatic heart diseases (I05–I09)", "deaths": 5, "share": "4.0% of chapter"},
            ],
        },
        {
            "name": "Endocrine, nutritional and metabolic diseases",
            "code": "E00–E90",
            "deaths": 83,
            "pct": 17.1,
            "detail": [
                {"name": "Diabetes mellitus (E10–E14)", "deaths": 71, "share": "85.5% of chapter"},
                {"name": "Metabolic disorders (E70–E90)", "deaths": 7, "share": "8.4% of chapter"},
                {"name": "Malnutrition (E40–E46)", "deaths": 4, "share": "4.8% of chapter"},
                {"name": "Disorders of thyroid gland (E00–E07)", "deaths": 1, "share": "1.2% of chapter"},
            ],
        },
        {
            "name": "Neoplasms",
            "code": "C00–D48",
            "deaths": 62,
            "pct": 12.8,
            "detail": [
                {"name": "Female genital organs (C51–C58)", "deaths": 13, "share": "21.0% of chapter"},
                {"name": "Breast (C50)", "deaths": 13, "share": "21.0% of chapter"},
                {"name": "Digestive organs (C15–C26)", "deaths": 12, "share": "19.4% of chapter"},
                {"name": "Ill-defined / secondary / unspecified (C76–C80)", "deaths": 8, "share": "12.9% of chapter"},
            ],
        },
        {
            "name": "Ill-defined causes",
            "code": "R00–R99",
            "deaths": 47,
            "pct": 9.7,
            "detail": [
                {"name": "Ill-defined and unknown causes (R95–R99)", "deaths": 40, "share": "85.1% of chapter"},
                {"name": "General symptoms and signs (R50–R69)", "deaths": 5, "share": "10.6% of chapter"},
                {"name": "Circulatory/respiratory signs (R00–R09)", "deaths": 1, "share": "2.1% of chapter"},
                {"name": "Cognition/perception signs (R40–R46)", "deaths": 1, "share": "2.1% of chapter"},
            ],
        },
        {
            "name": "Certain infectious and parasitic diseases",
            "code": "A00–B99",
            "deaths": 45,
            "pct": 9.3,
            "detail": [
                {"name": "Other bacterial diseases (A30–A49)", "deaths": 26, "share": "57.8% of chapter"},
                {"name": "Viral hepatitis (B15–B19)", "deaths": 6, "share": "13.3% of chapter"},
                {"name": "Tuberculosis (A15–A19)", "deaths": 5, "share": "11.1% of chapter"},
                {"name": "Intestinal infectious diseases (A00–A09)", "deaths": 5, "share": "11.1% of chapter"},
            ],
        },
        {
            "name": "Diseases of the respiratory system",
            "code": "J00–J99",
            "deaths": 31,
            "pct": 6.4,
            "detail": [
                {"name": "Chronic lower respiratory diseases (J40–J47)", "deaths": 16, "share": "51.6% of chapter"},
                {"name": "Influenza and pneumonia (J09–J18)", "deaths": 9, "share": "29.0% of chapter"},
            ],
        },
        {
            "name": "Diseases of the genitourinary system",
            "code": "N00–N99",
            "deaths": 24,
            "pct": 5.0,
            "detail": [
                {"name": "Renal failure (N17–N19)", "deaths": 18, "share": "75.0% of chapter"},
            ],
        },
        {
            "name": "Diseases of the digestive system",
            "code": "K00–K93",
            "deaths": 15,
            "pct": 3.1,
            "detail": [
                {"name": "Diseases of liver (K70–K77)", "deaths": 7, "share": "46.7% of chapter"},
            ],
        },
        {
            "name": "External causes of morbidity and mortality",
            "code": "V01–Y98",
            "deaths": 14,
            "pct": 2.9,
            "detail": [
                {"name": "Transport accidents (V01–V99)", "deaths": 5, "share": "35.7% of chapter"},
                {"name": "Accidental exposure to unspecified factors (X58–X59)", "deaths": 4, "share": "28.6% of chapter"},
            ],
        },
        {
            "name": "Diseases of the nervous system",
            "code": "G00–G99",
            "deaths": 13,
            "pct": 2.7,
            "detail": [
                {"name": "Other disorders of the nervous system (G90–G99)", "deaths": 5, "share": "38.5% of chapter"},
            ],
        },
        {
            "name": "Remainder of other chapters",
            "code": "Other",
            "deaths": 25,
            "pct": 5.2,
            "detail": [
                {"name": "Skin, perinatal, musculoskeletal, blood, congenital, mental", "deaths": 25, "share": "5.2% of all deaths"},
            ],
        },
    ],
    "sex": {
        "male": {
            "total": 294,
            "top": [
                {"name": "Circulatory system", "deaths": 88, "pct": 29.9},
                {"name": "Endocrine / nutritional / metabolic", "deaths": 49, "pct": 16.7},
                {"name": "Ill-defined causes", "deaths": 32, "pct": 10.9},
                {"name": "Infectious & parasitic", "deaths": 25, "pct": 8.5},
                {"name": "Neoplasms", "deaths": 25, "pct": 8.5},
                {"name": "Respiratory system", "deaths": 20, "pct": 6.8},
            ],
        },
        "female": {
            "total": 190,
            "top": [
                {"name": "Circulatory system", "deaths": 37, "pct": 19.5},
                {"name": "Neoplasms", "deaths": 37, "pct": 19.5},
                {"name": "Endocrine / nutritional / metabolic", "deaths": 34, "pct": 17.9},
                {"name": "Infectious & parasitic", "deaths": 20, "pct": 10.5},
                {"name": "Ill-defined causes", "deaths": 15, "pct": 7.9},
                {"name": "Respiratory system", "deaths": 11, "pct": 5.8},
            ],
        },
    },
    "months": [
        {"month": 1, "label": "Jan", "deaths": 33},
        {"month": 2, "label": "Feb", "deaths": 39},
        {"month": 3, "label": "Mar", "deaths": 33},
        {"month": 4, "label": "Apr", "deaths": 61},
        {"month": 5, "label": "May", "deaths": 54},
        {"month": 6, "label": "Jun", "deaths": 53},
        {"month": 7, "label": "Jul", "deaths": 42},
        {"month": 8, "label": "Aug", "deaths": 36},
        {"month": 9, "label": "Sep", "deaths": 32},
        {"month": 10, "label": "Oct", "deaths": 43},
        {"month": 11, "label": "Nov", "deaths": 34},
        {"month": 12, "label": "Dec", "deaths": 24},
    ],
    "places": [
        {
            "id": "hospital",
            "label": "Hospital",
            "deaths": 253,
            "pct": 52.3,
            "note": "Most recorded deaths occurred in hospital settings, reflecting certification pathways through Vanuatu National Hospital.",
        },
        {
            "id": "home",
            "label": "Home",
            "deaths": 130,
            "pct": 26.9,
            "note": "A substantial share of deaths occurred at home, highlighting the need to strengthen community death notification and certification.",
        },
        {
            "id": "other",
            "label": "Other",
            "deaths": 101,
            "pct": 20.9,
            "note": "Other locations include settings outside hospital and home. Strengthening notification outside facilities remains a priority.",
        },
    ],
}


def seed(year: int = 2023) -> None:
    if year != 2023:
        raise ValueError("Only the 2023 RCS brief is bundled in this seed script.")

    init_db()
    data = SEED_2023

    with SessionLocal() as session:
        existing = session.scalar(select(Dataset).where(Dataset.year == year))
        if existing:
            session.delete(existing)
            session.flush()

        dataset = Dataset(
            year=data["year"],
            title=data["title"],
            records_submitted=data["records_submitted"],
            stillbirths_removed=data["stillbirths_removed"],
            deaths_analysed=data["deaths_analysed"],
            expected_annual_deaths=data["expected_annual_deaths"],
            coverage_pct=data["coverage_pct"],
            notes=data["notes"],
        )
        session.add(dataset)
        session.flush()

        for rank, cause_row in enumerate(data["causes"], start=1):
            cause = Cause(
                dataset_id=dataset.id,
                rank=rank,
                icd10_code=cause_row["code"],
                name=cause_row["name"],
                deaths=cause_row["deaths"],
                pct=cause_row["pct"],
            )
            session.add(cause)
            session.flush()
            for detail in cause_row.get("detail") or []:
                session.add(
                    CauseDetail(
                        cause_id=cause.id,
                        name=detail["name"],
                        deaths=detail["deaths"],
                        share_text=detail["share"],
                    )
                )

        for sex_key, sex_block in data["sex"].items():
            session.add(SexTotal(dataset_id=dataset.id, sex=sex_key, deaths=sex_block["total"]))
            for row in sex_block["top"]:
                session.add(
                    SexCause(
                        dataset_id=dataset.id,
                        sex=sex_key,
                        name=row["name"],
                        deaths=row["deaths"],
                        pct=row["pct"],
                    )
                )

        for month in data["months"]:
            session.add(
                MonthlyDeath(
                    dataset_id=dataset.id,
                    month=month["month"],
                    label=month["label"],
                    deaths=month["deaths"],
                )
            )

        for place in data["places"]:
            session.add(
                Place(
                    dataset_id=dataset.id,
                    place_id=place["id"],
                    label=place["label"],
                    deaths=place["deaths"],
                    pct=place["pct"],
                    note=place["note"],
                )
            )

        session.commit()


def seed_if_empty() -> None:
    init_db()
    with SessionLocal() as session:
        exists = session.scalar(select(Dataset.id).where(Dataset.year == 2023))
    if exists is None:
        seed(2023)


if __name__ == "__main__":
    from database import DB_PATH

    seed(2023)
    print(f"Seeded 2023 dataset into {DB_PATH}")
