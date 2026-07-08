from __future__ import annotations

import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from crawler.filter import infer_industry
from crawler.models import Job
from crawler.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

SASAC_URL = "https://www.sasac.gov.cn/n2588020/index.html"
SASAC_BASE = "https://www.sasac.gov.cn"


class SasacScraper(BaseScraper):
    name = "国资委人事专栏"

    def fetch(self) -> list[Job]:
        jobs: list[Job] = []
        try:
            resp = self.get(SASAC_URL)
        except Exception as exc:
            logger.warning("国资委页面访问失败（可能网络限制）: %s", exc)
            return jobs

        soup = BeautifulSoup(resp.text, "lxml")
        links = soup.select("a[href]")
        seen: set[str] = set()

        for a in links:
            title = (a.get_text() or "").strip()
            href = a.get("href") or ""
            if not title or not href:
                continue
            if not any(k in title for k in ["招聘", "校招", "2027", "27届", "应届"]):
                continue
            if not any(k in title for k in ["北京", "央企", "国企", "2027", "27"]):
                continue

            url = urljoin(SASAC_BASE, href)
            if url in seen:
                continue
            seen.add(url)

            company = self._extract_company(title)
            jobs.append(
                Job(
                    title=title,
                    company=company,
                    industry=infer_industry(company),
                    location="北京",
                    education="不限",
                    deadline="",
                    source=self.name,
                    url=url,
                    is_campus=True,
                    graduate_year="27届",
                    description=title,
                    tags=["国资委"],
                )
            )

        logger.info("国资委抓取 %d 条", len(jobs))
        return jobs

    @staticmethod
    def _extract_company(title: str) -> str:
        m = re.search(r"([\u4e00-\u9fff]{2,20}(?:集团|公司|研究院|所))", title)
        if m:
            return m.group(1)
        if "央企" in title:
            return "中央企业"
        return "国资委下属单位"
