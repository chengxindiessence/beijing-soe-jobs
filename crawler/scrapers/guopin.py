from __future__ import annotations

import logging
from typing import Any

from crawler.models import Job
from crawler.scrapers.base import BaseScraper
from crawler.scrapers.guopin_common import parse_guopin_item

logger = logging.getLogger(__name__)

API_URL = "https://gp-api.iguopin.com/api/jobs/v1/list"
BEIJING_DISTRICT = ["000000.110000.110100"]
CAMPUS_NATURE = ["115xW5oQ"]  # 校招


class GuopinScraper(BaseScraper):
    name = "国聘网"

    def fetch(self) -> list[Job]:
        keywords = self.config.get("guopin_keywords", ["2027", "27届"])
        max_pages = int(self.config.get("crawler", {}).get("max_pages_per_source", 10))
        seen_ids: set[str] = set()
        jobs: list[Job] = []

        for keyword in keywords:
            page = 1
            while page <= max_pages:
                payload: dict[str, Any] = {
                    "page": page,
                    "page_size": 50,
                    "district": BEIJING_DISTRICT,
                    "nature": CAMPUS_NATURE,
                }
                if keyword:
                    payload["keyword"] = keyword

                try:
                    data = self.post_json(API_URL, payload)
                except Exception as exc:
                    logger.error("国聘网请求失败 keyword=%s page=%d: %s", keyword, page, exc)
                    break

                if data.get("code") != 200:
                    logger.warning("国聘网返回异常: %s", data.get("msg"))
                    break

                body = data.get("data") or {}
                items = body.get("list") or []
                if not items:
                    break

                for item in items:
                    job = parse_guopin_item(item)
                    if job and job.id not in seen_ids:
                        seen_ids.add(job.id)
                        jobs.append(job)

                total = int(body.get("total") or 0)
                page_size = int(body.get("page_size") or 50)
                if page * page_size >= total:
                    break
                page += 1

        logger.info("国聘网抓取 %d 条", len(jobs))
        return jobs
