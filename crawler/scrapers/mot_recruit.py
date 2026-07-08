from __future__ import annotations

import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from crawler.models import Job
from crawler.parsers.mot_table import parse_mot_style_tables
from crawler.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

MOT_BASE = "https://rccp.jtzyzg.org.cn"
MOT_HOME = f"{MOT_BASE}/"


class MotRecruitScraper(BaseScraper):
    """交通运输部所属事业单位 — 交通运输人才测评网."""

    name = "交通运输部事业单位"

    def fetch(self) -> list[Job]:
        jobs: list[Job] = []
        seen_urls: set[str] = set()

        try:
            resp = self.get(MOT_HOME)
        except Exception as exc:
            logger.warning("交通运输部招聘网访问失败: %s", exc)
            return jobs

        article_ids = self._collect_article_ids(resp.text)
        logger.info("交通运输部：发现 %d 条招聘公告", len(article_ids))

        for aid in article_ids:
            url = f"{MOT_BASE}/article/{aid}"
            if url in seen_urls:
                continue
            seen_urls.add(url)

            try:
                art = self.get(url)
            except Exception as exc:
                logger.debug("跳过公告 %s: %s", url, exc)
                continue

            if not self._is_recruitment(art.text):
                continue

            parsed = parse_mot_style_tables(art.text, url, default_industry="交通")
            is_campus = any(k in art.text for k in ["应届", "毕业生", "校招", "27届", "2027"])
            for item in parsed:
                jobs.append(self._to_job(item, is_campus=is_campus))

        logger.info("交通运输部事业单位抓取 %d 条（北京）", len(jobs))
        return jobs

    def _collect_article_ids(self, html: str) -> list[str]:
        ids = re.findall(r"/article/(\d{10,})", html)
        # 去重保序
        return list(dict.fromkeys(ids))

    @staticmethod
    def _is_recruitment(html: str) -> bool:
        text = BeautifulSoup(html, "lxml").get_text(" ", strip=True)
        return "招聘" in text and ("事业单位" in text or "公开招聘" in text)

    @staticmethod
    def _to_job(item: dict, is_campus: bool = True) -> Job:
        return Job(
            title=item["title"],
            company=item["company"],
            industry=item.get("industry", "交通"),
            location=item["location"],
            education=item.get("education", "不限"),
            deadline=item.get("deadline", ""),
            source="交通运输部事业单位",
            url=item["url"],
            is_campus=is_campus,
            graduate_year="27届",
            description=item.get("description", ""),
            majors=item.get("majors", []),
            tags=["事业单位", "交通部"],
        )
