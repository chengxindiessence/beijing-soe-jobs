from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from hashlib import md5
from typing import Any


@dataclass
class Job:
    title: str
    company: str
    industry: str = "其他"
    location: str = "北京"
    education: str = "不限"
    deadline: str = ""
    source: str = ""
    url: str = ""
    hukou: bool = False
    is_campus: bool = True
    graduate_year: str = "27届"
    description: str = ""
    majors: list[str] = field(default_factory=list)
    first_seen: str = ""
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.first_seen:
            self.first_seen = date.today().isoformat()

    @property
    def id(self) -> str:
        raw = f"{self.source}|{self.company}|{self.title}|{self.url}"
        return md5(raw.encode("utf-8")).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["id"] = self.id
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Job:
        fields = {k: v for k, v in data.items() if k != "id"}
        return cls(**fields)


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")
