from typing import Callable, Optional, Protocol
import requests
from dataclasses import asdict
import datetime
import os

from .dataschema import JobShcema


class APIDataFetchException(Exception):
    def __init__(self, website_name: str, url: str) -> None:
        message = f"fetching error from {website_name} on {url}"
        super().__init__(message)


class PageNotFound(Exception):
    def __init__(self, url: str) -> None:
        message = f"Page not found on {url}"
        super().__init__(message)


SaveFunction = Callable[[tuple[JobShcema], str], None]


def save_to_tsv(data: JobShcema, file_name: str) -> None:

    if not os.path.isfile(file_name):
        header = [*asdict(data).keys()]
        with open(f"{file_name}", "w") as file:
            file.write("\t".join(header))
            file.write("\n")

    with open(f"{file_name}", "a") as file:
        file.write(
            "{id}\t{job_id}\t{company}\t{location}\t{title}\t{work_type}\t{listing_date}\t{salary_range}\t{web_name}".format(
                **asdict(data)
            )
        )
        file.write("\n")


class GetDataFunction(Protocol):
    """
    A protocol that defines a callable type for fetching data from a URL.

    Attributes:
        url (str): The URL to fetch data from.
        params (Optional[dict[str, str]]): Optional query parameters to include in the request.
        timeout (Optional[int]): Optional timeout duration for the request in seconds.
        method (str): The HTTP method to use for the request (e.g., 'GET', 'POST').

    Returns:
        Optional[requests.Response]: The response object from the request, or None if the request fails.
    """

    def __call__(
        self,
        url: str,
        params: Optional[dict[str, str]],
        timeout: Optional[int],
        method: str,
    ) -> Optional[requests.Response]: ...


def get_data(
    url: str,
    params: Optional[dict[str, str]] = None,
    timeout: Optional[int] = None,
    method: str = "GET",
) -> Optional[requests.Response]:

    respone = requests.request(method=method, url=url, params=params, timeout=timeout)
    return respone


def date_format(date_str: str, format: str) -> datetime.date:
    try:
        return datetime.datetime.strptime(
            date_str, format
        ).date()  # .strftime("%d-%m-%Y")
    except ValueError:
        match date_str:
            case "วันนี้" | "Today":
                return datetime.date.today()  # .strftime("%d-%m-%Y")
            case "เมื่อวานนี้" | "Yesterday":
                date = datetime.date.today() - datetime.timedelta(days=1)
                return date  # .strftime("%d-%m-%Y")
            case _:
                return datetime.date.today()  # .strftime("%d-%m-%Y")


def salary_vaildate(salary: str) -> str:
    return salary if len(salary) > 0 or salary is None else "n/a"


def get_job_detail(job: JobShcema, website_name: str) -> Optional[str]:

    from jobextractor import website_a, website_b

    match website_name:
        case "A":
            return website_a.get_job_detail(job.job_id, get_data)
        case "B":
            return website_b.get_job_detail(job.job_id, get_data)
        case _:
            raise ValueError("Unknown website name")


def job_url(job_id, website_name):
    from jobextractor import website_a, website_b

    match website_name:
        case "A":
            return website_a.job_url(job_id)
        case "B":
            return website_b.job_url(job_id)
        case _:
            raise ValueError("Unknown website name")


if __name__ == "__main__":
    ...
