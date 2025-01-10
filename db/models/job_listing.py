from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Table, ForeignKey, Column
import datetime

from db.base import Base


work_type_bridge = Table(
    "work_type_bridge",
    Base.metadata,
    Column("job_id", ForeignKey("job_board.id"), primary_key=True),
    Column("work_type_id", ForeignKey("work_type.work_type_id"), primary_key=True),
)


class JobBoardDb(Base):
    __tablename__ = "job_board"

    id: Mapped[str] = mapped_column(primary_key=True)
    job_id: Mapped[str] = mapped_column()
    company: Mapped[str] = mapped_column()
    location: Mapped[str] = mapped_column()
    title: Mapped[str] = mapped_column()
    listing_date: Mapped[datetime.date] = mapped_column(index=True)
    salary_range: Mapped[str] = mapped_column()
    web_name: Mapped[str] = mapped_column(index=True)
    job_level: Mapped[str] = mapped_column(index=True)
    timestamp: Mapped[datetime.datetime] = mapped_column()

    work_types: Mapped[list["WorkTypeDb"]] = relationship(
        "WorkTypeDb", secondary=work_type_bridge, back_populates="job_ids"
    )

    def __repr__(self) -> str:
        return f"JobBoardDb(id={self.id}, job_id={self.job_id}, company={self.company}, location={self.location}, title={self.title}, listing_date={self.listing_date}, salary_range={self.salary_range}, web_name={self.web_name}, job_level={self.job_level}, timestamp={self.timestamp})"
