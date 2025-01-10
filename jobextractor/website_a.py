from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Iterable, Optional, Any
import os

from .dataschema import JobShcema
from .utils import (
    GetDataFunction,
    salary_vaildate,
    date_format,
    get_data,
    APIDataFetchException,
    PageNotFound,
)

WEB_URL = os.getenv("WEB_A_URL")
WEB_NAME = os.getenv("WEB_A_NAME")
JOB_DETAIL_PATH = os.getenv("WEB_A_DETAIL_PATH")


@dataclass
class Parameters:
    keywords: str
    siteKey: str = "TH-Main"
    locale: str = "en-TH"
    page: int = 1
    pageSize: int = 100


def get_job_list(
    params: Parameters,
    get_data_fn: GetDataFunction = get_data,
    timeout: Optional[int] = None,
) -> Optional[Iterable[JobShcema]]:

    api = f"{WEB_URL}/api/jobsearch/v5/search"

    try:
        response = get_data_fn(api, params.__dict__, timeout)
        job_data: list[dict[str, str]] = response.json()["data"]
    except Exception as e:
        raise APIDataFetchException(WEB_NAME, api) from e
    else:
        for job in job_data:
            try:
                yield mapping_job_data(job)
            except Exception as e:
                match e:
                    case KeyError():
                        print(f"Missing \"{e}\" key in job id: {job.get('id')}")
                    case _:
                        print(f"Error in job id: {job.get('id')}")
                continue


def mapping_job_data(job_data: dict) -> JobShcema:
    return JobShcema(
        job_id=job_data["id"],
        company=job_data["advertiser"]["description"],
        location=job_data["locations"][0]["label"],
        title=job_data["title"],
        work_type=job_data["workTypes"][0],
        listing_date=date_format(job_data["listingDate"], "%Y-%m-%dT%H:%M:%SZ"),
        salary_range=salary_vaildate(job_data["salaryLabel"]),
        web_name=WEB_NAME,
    )


def get_job_detail(
    id: str,
    get_data_fn: GetDataFunction = get_data,
) -> str:

    url = job_url(id)

    try:
        content = get_data_fn(url=url).content
        soup = BeautifulSoup(content, "html.parser")
        job_detail_tag = soup.find("div", {"data-automation": "jobAdDetails"})
        job_detail_block = job_detail_tag.find("div")
        return job_detail_block.text
    except Exception as e:
        raise PageNotFound(url) from e

def job_url(id: str) -> str:
    return JOB_DETAIL_PATH + id

if __name__ == "__main__":
    ...
