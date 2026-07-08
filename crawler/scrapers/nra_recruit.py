from __future__ import annotations

import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from crawler.models import Job
from crawler.parsers.mot_table import parse_mot_style_tables
from crawler.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

NRA_BASE = "https://www.nra.gov.cn"
# 国家铁路局人事招聘资料 + 已知公告页
NRA_LIST_URLS = [
    "https://www.nra.gov.cn/xxgk/gkml/ztjg/rsgl/zlxx/",
    "https://www.nra.gov.cn/xxgk/gkml/ztjg/rsgl/",
]
NRA_KNOWN_ARTICLES = [
    "https://www.nra.gov.cn/xxgk/gkml/ztjg/rsgl/zlxx/202606/t20260608_351406.shtml",
]


class NraRecruitScraper(BaseScraper):
    """国家铁路局及铁道系统事业单位招聘."""

    name = "国家铁路局事业单位"

    def fetch(self) -> list[Job]:
        jobs: list[Job] = []
        article_urls: set[str] = set(NRA_KNOWN_ARTICLES)

        for list_url in NRA_LIST_URLS:
            try:
                resp = self.get(list_url)
                for link in self._extract_recruit_links(resp.text, list_url):
                    article_urls.add(link)
            except Exception as exc:
                logger.debug("国家铁路局列表页失败 %s: %s", list_url, exc)

        # 同时从 mot.gov.cn 交通部人事专栏补充（含铁道相关事业单位）
        try:
            mot_gov = self.get("https://xxgk.mot.gov.cn/jigou/rsjys/")
            for link in self._extract_recruit_links(mot_gov.text, "https://xxgk.mot.gov.cn"):
                if "招聘" in link or self._link_text_has_recruit(mot_gov.text, link):
                    article_urls.add(link)
        except Exception as exc:
            logger.debug("交通部信息公开页失败: %s", exc)

        for url in article_urls:
            try:
                resp = self.get(url)
            except Exception as exc:
                logger.debug("跳过 %s: %s", url, exc)
                continue

            if "招聘" not in resp.text:
                continue

            title_probe = BeautifulSoup(resp.text, "lxml").find("title")
            title_text = title_probe.get_text(strip=True) if title_probe else ""
            if any(k in title_text for k in ["笔试", "面试", "体检", "考察"]) and "公告" not in title_text:
                continue

            # 国家铁路局公告多为表格附件型，尝试通用解析 + 公告级岗位
            parsed = parse_mot_style_tables(resp.text, url, default_industry="铁路")
            if parsed:
                for item in parsed:
                    jobs.append(self._to_job(item, url))
            else:
                jobs.extend(self._parse_announcement(resp.text, url))

        logger.info("国家铁路局/铁道事业单位抓取 %d 条", len(jobs))
        return jobs

    def _extract_recruit_links(self, html: str, base: str) -> list[str]:
        soup = BeautifulSoup(html, "lxml")
        links: list[str] = []
        for a in soup.select("a[href]"):
            text = (a.get_text() or "").strip()
            href = a.get("href") or ""
            if not href or not text:
                continue
            if any(k in text for k in ["招聘", "公开招聘", "校招", "应届"]):
                full = urljoin(base, href)
                if full.startswith("http"):
                    links.append(full)
        return links

    @staticmethod
    def _link_text_has_recruit(html: str, link: str) -> bool:
        return "招聘" in html and link in html

    def _parse_announcement(self, html: str, url: str) -> list[Job]:
        soup = BeautifulSoup(html, "lxml")
        title_el = soup.find("h1") or soup.find("title")
        title = title_el.get_text(strip=True) if title_el else "铁道事业单位招聘"
        if "招聘" not in title:
            return []
        if any(k in title for k in ["笔试", "面试", "体检", "考察", "通知"]):
            return []

        text = soup.get_text(" ", strip=True)
        if "北京" not in text and "复兴路" not in text:
            return []

        is_campus = any(k in text for k in ["应届", "毕业生", "校招", "27届", "2027"])

        # 公告级条目（无细表时）
        companies = re.findall(
            r"(国家铁路局[^，。\s]{0,20}(?:中心|研究院|学院|局|所|服务中心))",
            text,
        )
        company = companies[0] if companies else "国家铁路局所属事业单位"

        return [
            Job(
                title=title[:80],
                company=company,
                industry="铁路",
                location="北京",
                education="不限",
                deadline="",
                source="国家铁路局事业单位",
                url=url,
                is_campus=is_campus or "公开招聘" in title,
                graduate_year="27届",
                description=title,
                tags=["事业单位", "铁道部", "铁路"],
            )
        ]

    @staticmethod
    def _to_job(item: dict, url: str) -> Job:
        return Job(
            title=item["title"],
            company=item["company"],
            industry="铁路",
            location=item["location"],
            education=item.get("education", "不限"),
            deadline=item.get("deadline", ""),
            source="国家铁路局事业单位",
            url=url,
            is_campus=True,
            graduate_year="27届",
            description=item.get("description", ""),
            majors=item.get("majors", []),
            tags=["事业单位", "铁道部", "铁路"],
        )
