from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base
from .job_listing import work_type_bridge


class WorkTypeDb(Base):
    __tablename__ = "work_type"

    work_type_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    work_type: Mapped[str] = mapped_column()

    job_ids: Mapped[list["JobBoardDb"]] = relationship(
        "JobBoardDb", secondary=work_type_bridge, back_populates="work_types"
    )
