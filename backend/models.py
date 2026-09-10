from sqlalchemy import Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Dataset(Base):
    __tablename__ = "dataset"
    __table_args__ = (UniqueConstraint("year", name="uq_dataset_year"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    records_submitted: Mapped[int] = mapped_column(Integer, nullable=False)
    stillbirths_removed: Mapped[int] = mapped_column(Integer, nullable=False)
    deaths_analysed: Mapped[int] = mapped_column(Integer, nullable=False)
    expected_annual_deaths: Mapped[int] = mapped_column(Integer, nullable=False)
    coverage_pct: Mapped[float] = mapped_column(Float, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    causes: Mapped[list["Cause"]] = relationship(
        back_populates="dataset",
        cascade="all, delete-orphan",
        order_by="Cause.rank",
    )
    sex_causes: Mapped[list["SexCause"]] = relationship(
        back_populates="dataset",
        cascade="all, delete-orphan",
        order_by="SexCause.id",
    )
    sex_totals: Mapped[list["SexTotal"]] = relationship(
        back_populates="dataset",
        cascade="all, delete-orphan",
        order_by="SexTotal.id",
    )
    months: Mapped[list["MonthlyDeath"]] = relationship(
        back_populates="dataset",
        cascade="all, delete-orphan",
        order_by="MonthlyDeath.month",
    )
    places: Mapped[list["Place"]] = relationship(
        back_populates="dataset",
        cascade="all, delete-orphan",
        order_by="Place.id",
    )


class Cause(Base):
    __tablename__ = "causes"
    __table_args__ = (UniqueConstraint("dataset_id", "rank", name="uq_causes_dataset_rank"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("dataset.id", ondelete="CASCADE"), nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    icd10_code: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    deaths: Mapped[int] = mapped_column(Integer, nullable=False)
    pct: Mapped[float] = mapped_column(Float, nullable=False)

    dataset: Mapped[Dataset] = relationship(back_populates="causes")
    details: Mapped[list["CauseDetail"]] = relationship(
        back_populates="cause",
        cascade="all, delete-orphan",
        order_by="CauseDetail.id",
    )


class CauseDetail(Base):
    __tablename__ = "cause_details"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cause_id: Mapped[int] = mapped_column(ForeignKey("causes.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    deaths: Mapped[int] = mapped_column(Integer, nullable=False)
    share_text: Mapped[str] = mapped_column(String(128), nullable=False)

    cause: Mapped[Cause] = relationship(back_populates="details")


class SexCause(Base):
    __tablename__ = "sex_causes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("dataset.id", ondelete="CASCADE"), nullable=False)
    sex: Mapped[str] = mapped_column(String(16), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    deaths: Mapped[int] = mapped_column(Integer, nullable=False)
    pct: Mapped[float] = mapped_column(Float, nullable=False)

    dataset: Mapped[Dataset] = relationship(back_populates="sex_causes")


class SexTotal(Base):
    __tablename__ = "sex_totals"
    __table_args__ = (UniqueConstraint("dataset_id", "sex", name="uq_sex_totals_dataset_sex"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("dataset.id", ondelete="CASCADE"), nullable=False)
    sex: Mapped[str] = mapped_column(String(16), nullable=False)
    deaths: Mapped[int] = mapped_column(Integer, nullable=False)

    dataset: Mapped[Dataset] = relationship(back_populates="sex_totals")


class MonthlyDeath(Base):
    __tablename__ = "monthly_deaths"
    __table_args__ = (UniqueConstraint("dataset_id", "month", name="uq_monthly_dataset_month"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("dataset.id", ondelete="CASCADE"), nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    label: Mapped[str] = mapped_column(String(16), nullable=False)
    deaths: Mapped[int] = mapped_column(Integer, nullable=False)

    dataset: Mapped[Dataset] = relationship(back_populates="months")


class Place(Base):
    __tablename__ = "places"
    __table_args__ = (UniqueConstraint("dataset_id", "place_id", name="uq_places_dataset_place"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("dataset.id", ondelete="CASCADE"), nullable=False)
    place_id: Mapped[str] = mapped_column(String(32), nullable=False)
    label: Mapped[str] = mapped_column(String(64), nullable=False)
    deaths: Mapped[int] = mapped_column(Integer, nullable=False)
    pct: Mapped[float] = mapped_column(Float, nullable=False)
    note: Mapped[str] = mapped_column(Text, nullable=False)

    dataset: Mapped[Dataset] = relationship(back_populates="places")
