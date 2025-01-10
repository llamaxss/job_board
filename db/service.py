from sqlalchemy.orm import Session
import datetime

from .models.job_listing import JobBoardDb
from .models.work_types import WorkTypeDb
from jobextractor.dataschema import JobShcema


def add_job_data(
    session: Session, job: JobShcema, job_level: str, work_types: list[WorkTypeDb]
) -> JobBoardDb:
    job_table = JobBoardDb(
        id=job.id,
        job_id=job.job_id,
        company=job.company,
        location=job.location,
        title=job.title,
        listing_date=job.listing_date,
        salary_range=job.salary_range,
        web_name=job.web_name,
        job_level=job_level,
        timestamp=datetime.datetime.now(),
    )
    job_table.work_types.extend(work_types)

    session.add(job_table)
    session.commit()
    session.refresh(job_table)

    return job_table

def get_job_data(session: Session, id: str) -> JobBoardDb:
    return session.query(JobBoardDb).filter(JobBoardDb.id == id).first()


def get_job_types(session: Session, job_types: list[str]) -> list[WorkTypeDb]:
    add_new_job_type(session, job_types)
    return session.query(WorkTypeDb).filter(WorkTypeDb.work_type.in_(job_types)).all()


def fatch_all_job_data(session: Session) -> list[JobBoardDb]:
    return session.query(JobBoardDb).all()


def add_new_job_type(session: Session, job_types: list[str]) -> None:

    for job_type in job_types:
        if not check_job_type_exists(session, job_type):
            work_type = WorkTypeDb(work_type=job_type)
            session.add(work_type)
            session.commit()
            session.refresh(work_type)


def check_job_type_exists(session: Session, job_type: str) -> bool:
    is_contain = (
        session.query(WorkTypeDb).filter(WorkTypeDb.work_type == job_type).first()
    )
    if is_contain is not None:
        return True
    else:
        return False


def check_job_exists(session: Session, id: str) -> bool:
    is_contain = get_job_data(session, id)
    if is_contain is not None:
        return True
    else:
        return False
