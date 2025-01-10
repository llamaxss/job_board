import os
from typing import Any, Optional, Iterable, Tuple
from bs4 import BeautifulSoup
from dataclasses import dataclass
import json
import re

from .dataschema import JobShcema
from .utils import (
    GetDataFunction,
    salary_vaildate,
    date_format,
    get_data,
    APIDataFetchException,
    PageNotFound,
)

WEB_URL = os.getenv("WEB_B_URL")
WEB_NAME = os.getenv("WEB_B_NAME")
JOB_DETAIL_PATH = os.getenv("WEB_B_DETAIL_PATH")


@dataclass()
class Parameters:
    keywords: str


def get_job_list(
    params: Parameters,
    get_data_fn: GetDataFunction = get_data,
    timeout: Optional[int] = None,
) -> Optional[Iterable[JobShcema]]:

    url = f"{WEB_URL}/en/jobs"

    try:
        response = get_data_fn(url, params.__dict__, timeout)
        job_data = _modify_data(response.text)
    except Exception as e:
        raise APIDataFetchException(WEB_NAME, url) from e
    else:
        for job in job_data:
            try:
                yield mapping_job_data(job)
            except Exception as e:
                match e:
                    case KeyError():
                        print(f"Missing \"{e}\" key in job id: {job.get('idEmp')}-{job.get('idPosition')}")
                    case _:
                        print(f"Error in job id: {job.get('idEmp')}-{job.get('idPosition')}", e)
                continue


def mapping_job_data(job_data: dict) -> JobShcema:
    return JobShcema(
        job_id=_name_id(job_data["idEmp"], job_data["idPosition"]),
        company=job_data["companyName"],
        location=job_data["locationText"],
        title=job_data["positionName"],
        work_type=_get_job_type(job_data["idEmp"], job_data["idPosition"]),
        listing_date=date_format(job_data["postDateText"], "%d/%m/%Y"),
        salary_range=salary_vaildate(job_data["salaryText"]),
        web_name=WEB_NAME,
    )


def get_job_detail(
    id: Optional[str] = None,
    get_data: GetDataFunction = get_data,
    **kw,
) -> str:

    if id is None:
        id_emp = kw.get("id_emp", None)
        id_position = kw.get("id_position", None)
    else:
        id_emp, id_position = id.split("-")

    try:
        job_description_element = get_job_page(id_emp, id_position, get_data)
        job_description_block = re.search(
            r"jobDescription\\\":\\\"(.*)\\\",\\\"contactPerson",
            job_description_element,
        )
        job_responsibility_and_requirement = (
            "Responsibilitie " + job_description_block.group(1)
        )
        return job_responsibility_and_requirement
    except Exception as e:
        raise ValueError(f"Job description not found: {id_emp}-{id_position}") from e


def is_job_page_exist(content: Optional[bytes]) -> Tuple[bool, str]:

    if content is None:
        return False, None

    soup = BeautifulSoup(content, "html5lib")
    children_tag = soup.find(
        "script", string=re.compile(r"^self\.__next_f\.push.*jobDescription.*$")
    )
    if children_tag:
        return True, children_tag.string
    else:
        return False, None


def get_job_page(id_emp: str, id_position: str, get_data: GetDataFunction) -> str:

    url = job_url(_name_id(id_emp, id_position))

    try:
        content: bytes = get_data(url).content
        page_exist, children_tag = is_job_page_exist(content)
        if page_exist:
            return children_tag
        else:
            raise ValueError("Taget element not found")
    except Exception as e:
        raise PageNotFound(url) from e


def _modify_data(text: str) -> Iterable[dict[str, Any]]:

    text = _trim_text(text).replace("\\", "")
    formated_data = _format_data(text)

    return formated_data


def _get_job_type(
    id_emp: str, id_position: str, get_data: GetDataFunction = get_data
) -> Optional[str]:

    try:
        job_description_element = get_job_page(id_emp, id_position, get_data)
        job_type = re.search(
            r"jobTypeText\\\":\\\"(.*)\\\",\\\"industryText", job_description_element
        )
        return job_type.group(1)

    except Exception as e:
        raise ValueError(f"Work type not found: {id_emp}-{id_position}") from e


def _format_data(data: str) -> Iterable[dict[str, Any]]:
    job_data = json.loads(f"{data}")
    return map(lambda job: job[3]["position"], job_data)


def _trim_text(text: str) -> str:

    start_index = text.index('{\\"postDate\\":\\"\\"')
    end_index = text.index("}]}]}]]", start_index)

    return r'[["..", "..", "..",' + text[start_index : end_index + 7]


def _name_id(idEmp: str, idPosition: str) -> str:
    return f"{idEmp}-{idPosition}"

def job_url(job_id: str) -> str:
    id_emp, id_position = job_id.split("-")
    return JOB_DETAIL_PATH + f"{id_emp}/{id_position}"

if __name__ == "__main__":
    ...
