from __future__ import annotations

import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from crawler.models import Job
from crawler.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class CompanySitesScraper(BaseScraper):
    name = "央企官网"

    def fetch(self) -> list[Job]:
        sites = self.config.get("company_sites", [])
        jobs: list[Job] = []
        seen: set[str] = set()

        for site in sites:
            site_name = site.get("name", "未知企业")
            url = site.get("url", "")
            industry = site.get("industry", "其他")
            selector = site.get("link_selector", "a")
            must_contain = site.get("title_must_contain", ["招聘", "校招"])

            if not url:
                continue

            try:
                resp = self.get(url)
            except Exception as exc:
                logger.warning("%s 页面访问失败: %s", site_name, exc)
                continue

            soup = BeautifulSoup(resp.text, "lxml")
            for a in soup.select(selector):
                title = (a.get_text() or "").strip()
                href = a.get("href") or ""
                if len(title) < 4 or not href:
                    continue
                if not any(k in title for k in must_contain):
                    continue
                if "北京" not in title and "2027" not in title and "27" not in title:
                    # 官网列表页可能不写北京，保留校招/2027相关
                    if not any(k in title for k in ["校招", "校园", "应届"]):
                        continue

                full_url = urljoin(url, href)
                key = f"{site_name}|{title}|{full_url}"
                if key in seen:
                    continue
                seen.add(key)

                jobs.append(
                    Job(
                        title=title,
                        company=site_name,
                        industry=industry,
                        location="北京",
                        education="不限",
                        deadline="",
                        source=f"{site_name}官网",
                        url=full_url,
                        is_campus=True,
                        graduate_year="27届",
                        description=title,
                        tags=[industry],
                    )
                )

            logger.info("%s 抓取完成", site_name)

        logger.info("央企官网合计 %d 条", len(jobs))
        return jobs
