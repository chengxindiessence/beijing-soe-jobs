from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from typing import Any

import requests

from crawler.models import Job

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    name = "base"

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        crawler_cfg = config.get("crawler", {})
        self.delay = float(crawler_cfg.get("request_delay", 1.5))
        self.timeout = int(crawler_cfg.get("timeout", 30))
        self.headers = {
            "User-Agent": crawler_cfg.get(
                "user_agent",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            )
        }

    def sleep(self) -> None:
        time.sleep(self.delay)

    def get(self, url: str, **kwargs: Any) -> requests.Response:
        self.sleep()
        resp = requests.get(
            url, headers=self.headers, timeout=self.timeout, **kwargs
        )
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "utf-8"
        return resp

    def post_json(self, url: str, payload: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        self.sleep()
        headers = {
            **self.headers,
            "Content-Type": "application/json",
            "Device": "pc",
            "Subsite": "cujiuye",
        }
        resp = requests.post(
            url, json=payload, headers=headers, timeout=self.timeout, **kwargs
        )
        resp.raise_for_status()
        return resp.json()

    @abstractmethod
    def fetch(self) -> list[Job]:
        raise NotImplementedError
