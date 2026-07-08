"""Parse MOT / institution recruitment tables from HTML."""

from __future__ import annotations

import re
from typing import Any


def parse_mot_style_tables(html: str, source_url: str, default_industry: str = "交通") -> list[dict[str, Any]]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "lxml")
    heading = soup.find("h1") or soup.find("h2")
    announce_title = heading.get_text(strip=True) if heading else "事业单位招聘"

    deadline = ""
    for pat in [
        r"(\d{1,2}月\d{1,2}日)\s*9:00.*?(\d{1,2}月\d{1,2}日)\s*18:00",
        r"至(\d{4}年\d{1,2}月\d{1,2}日)",
        r"截止[^。]{0,20}(\d{4}-\d{2}-\d{2})",
    ]:
        m = re.search(pat, soup.get_text(" ", strip=True))
        if m:
            deadline = m.group(m.lastindex or 1)
            break

    jobs: list[dict[str, Any]] = []
    seen: set[str] = set()

    for table in soup.find_all("table"):
        cells = [c.get_text(" ", strip=True) for c in table.find_all(["td", "th"])]
        if not cells:
            continue
        blob = " | ".join(cells)
        if "工作地点" not in blob or "北京" not in blob:
            continue
        if "岗位名称" not in blob:
            continue

        loc = _field(blob, "工作地点")
        if not loc or "北京" not in loc:
            continue

        company = _field(blob, "招聘单位") or _field(blob, "工作单位") or "交通运输部所属事业单位"
        title = _field(blob, "岗位名称")
        if not title:
            continue

        major = _field(blob, "专业要求") or _field(blob, "专业")
        education = _field(blob, "学历/学位要求") or _field(blob, "学历要求") or _field(blob, "学历")

        key = f"{company}|{title}|{loc}"
        if key in seen:
            continue
        seen.add(key)

        majors = [m.strip() for m in re.split(r"[\n;；]", major) if m.strip()] if major else []

        jobs.append(
            {
                "title": title.strip(),
                "company": company.strip(),
                "location": loc.strip(),
                "education": (education or "不限").strip(),
                "majors": majors,
                "deadline": deadline,
                "description": f"{announce_title} {major or ''}".strip(),
                "industry": default_industry,
                "url": source_url,
            }
        )

    return jobs


def _field(blob: str, name: str) -> str:
    m = re.search(rf"{re.escape(name)}\s*\|\s*([^|]+)", blob)
    return m.group(1).strip() if m else ""
