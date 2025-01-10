import os
from typing import Iterable
from functools import partial

from jobextractor import website_a, website_b, JobShcema
from jobextractor.utils import APIDataFetchException, get_job_detail
from db import (
    localsession,
    add_job_data,
    check_job_exists,
    Base,
    Engine,
)
from db.service import get_job_types
from log_setup import log_setup

try:
    from model_prompt import ModelDecision
except ImportError:
    print("*" * 50)
    print("Can't import Model.\nModelDecision class will be used as a placeholder.")
    print("*" * 50)

    class ModelDecision:
        def __init__(self):
            pass

        def model_decision_job_level(self, job_data: str, job_keyword: str) -> str:
            return "n/a"

        def close(self):
            pass


# Set up logging configuration
logger = log_setup()

JOB_KEYWORD = os.getenv("JOB_KEYWORD")


def fetch_job_posting() -> dict[str, Iterable[JobShcema]]:

    params_a = website_a.Parameters(keywords=JOB_KEYWORD)
    params_b = website_b.Parameters(keywords=JOB_KEYWORD)

    job_params = (params_a, params_b)
    job_modules = (website_a, website_b)

    return {
        module.WEB_NAME: module.get_job_list(param)
        for module, param in zip(job_modules, job_params)
    }


def job_level_decision(
    job: JobShcema, website_name: str, model_client: ModelDecision
) -> str:

    job_detail = get_job_detail(job, website_name)
    job_data = f"title: {job.title} " + job_detail
    job_level = model_client.model_decision_job_level(job_data, JOB_KEYWORD)

    return job_level


def job_type_spliter(job_types: str) -> list[str]:
    return [job_type.strip().capitalize() for job_type in job_types.split(",")]


def start():

    try:
        # Create database tables
        Base.metadata.create_all(bind=Engine)
        gpt_client = ModelDecision()

        # Fetch job postings
        job_posting = fetch_job_posting()

        with localsession() as session:
            for website_name, jobs in job_posting.items():
                job_level_decision_fn = partial(
                    job_level_decision,
                    website_name=website_name,
                    model_client=gpt_client,
                )
                try:
                    for job in jobs:
                        try:
                            if check_job_exists(session, job.id):
                                continue

                            job_level = job_level_decision_fn(job)
                            job_types = get_job_types(
                                session, job_type_spliter(job.work_type)
                            )

                            add_job_data(session, job, job_level, job_types)

                            logger.info(f"Insert from {website_name}: {job.id}")
                        except Exception:
                            logger.error(f"Error on {job.id}", exc_info=True)
                            continue
                except Exception as e:
                    match e:
                        case APIDataFetchException():
                            logger.error(
                                f"API fetch error: {website_name}", exc_info=True
                            )
                        case _:
                            logger.error(f"Error on {website_name}", exc_info=True)
                    continue

    except Exception:
        logger.error("Error in process", exc_info=True)
    finally:
        # Dispose of the engine and close the client
        Engine.dispose()
        gpt_client.close()


if __name__ == "__main__":
    start()
