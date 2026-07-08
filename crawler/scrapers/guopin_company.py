from __future__ import annotations

import logging
from typing import Any

from crawler.directory import load_soe_directory
from crawler.models import Job
from crawler.scrapers.base import BaseScraper
from crawler.scrapers.guopin_common import SOURCE_GUOPIN_COMPANY, parse_guopin_item

logger = logging.getLogger(__name__)

API_URL = "https://gp-api.iguopin.com/api/jobs/v1/list"
BEIJING_DISTRICT = ["000000.110000.110100"]
CAMPUS_NATURE = ["115xW5oQ"]


class GuopinCompanyScraper(BaseScraper):
    """按在京央企/国企名录，逐家检索国聘网校招岗位。"""

    name = "国聘网·企业专搜"

    def fetch(self) -> list[Job]:
        enterprises = load_soe_directory()
        if not enterprises:
            logger.warning("企业名录为空，跳过企业专搜")
            return []

        max_pages = int(
            self.config.get("crawler", {}).get("max_pages_company", 3)
        )
        seen_ids: set[str] = set()
        jobs: list[Job] = []
        searched = 0

        for ent in enterprises:
            keywords = ent.get("search_keywords") or [ent.get("name", "")]
            # 默认只用第一个关键词，减少请求量；config 设 use_all_keywords: true 可搜全部
            if not self.config.get("guopin_company", {}).get("use_all_keywords", False):
                keywords = keywords[:1]
            industry = ent.get("industry", "其他")
            category = ent.get("category", "")

            for keyword in keywords:
                if not keyword:
                    continue
                searched += 1
                page = 1
                while page <= max_pages:
                    payload: dict[str, Any] = {
                        "page": page,
                        "page_size": 50,
                        "district": BEIJING_DISTRICT,
                        "nature": CAMPUS_NATURE,
                        "keyword": keyword,
                    }
                    try:
                        data = self.post_json(API_URL, payload)
                    except Exception as exc:
                        logger.debug("企业专搜失败 %s: %s", keyword, exc)
                        break

                    if data.get("code") != 200:
                        break

                    body = data.get("data") or {}
                    items = body.get("list") or []
                    if not items:
                        break

                    for item in items:
                        job = parse_guopin_item(item, source=SOURCE_GUOPIN_COMPANY)
                        if not job or job.id in seen_ids:
                            continue
                        # 标记名录行业，便于前端筛选
                        if industry and job.industry == "其他":
                            job.industry = industry.split("/")[0]
                        if category:
                            job.tags = list(set(job.tags + [category]))
                        seen_ids.add(job.id)
                        jobs.append(job)

                    total = int(body.get("total") or 0)
                    page_size = int(body.get("page_size") or 50)
                    if page * page_size >= total:
                        break
                    page += 1

        logger.info(
            "企业专搜完成：检索 %d 个关键词，抓取 %d 条",
            searched,
            len(jobs),
        )
        return jobs
