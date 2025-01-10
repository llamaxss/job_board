from dataclasses import dataclass, field
import datetime

@dataclass
class JobShcema:
    id: str = field(init=False)
    job_id: str
    company: str
    location: str
    title: str
    work_type: str
    listing_date: datetime.date
    salary_range: str
    web_name: str

    def __post_init__(self):
        self._set_id()

    def _set_id(self) -> None:
        self.id = f"{self.web_name}_{self.job_id}"

if __name__ == "__main__":
    ...
    