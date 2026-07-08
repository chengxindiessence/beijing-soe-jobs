from __future__ import annotations

from typing import Any

from crawler.filter import infer_industry
from crawler.models import Job

SOURCE_GUOPIN = "国聘网"
SOURCE_GUOPIN_COMPANY = "国聘网·企业专搜"


def parse_guopin_item(item: dict[str, Any], source: str = SOURCE_GUOPIN) -> Job | None:
    title = (item.get("job_name") or "").strip()
    company = (item.get("company_name") or "").strip()
    if not title or not company:
        return None

    districts = item.get("district_list") or []
    location = "北京"
    if districts:
        location = districts[0].get("area_cn") or "北京"

    industry_cn = ""
    ind_list = item.get("industry_cn") or []
    if ind_list:
        industry_cn = ind_list[0]

    majors = [m for m in (item.get("major_cn") or []) if m and m != "不限专业"]
    end_time = (item.get("end_time") or "")[:10]
    education = item.get("education_cn") or "不限"
    job_id = item.get("job_id") or ""
    url = f"https://www.iguopin.com/job/detail?id={job_id}" if job_id else ""

    desc_parts = [
        item.get("experience_cn") or "",
        " ".join(majors),
        " ".join(item.get("job_tags_cn") or []),
    ]
    description = " ".join(p for p in desc_parts if p)

    nature = item.get("nature_cn") or ""
    is_campus = "校" in nature or item.get("is_graduates")

    tags = list(item.get("job_tags_cn") or [])
    if "应届" in (item.get("experience_cn") or ""):
        tags.append("应届")

    graduate_year = "27届"
    for marker in ["27届", "2027届", "2027"]:
        if marker in title or marker in description:
            graduate_year = "27届"
            break

    return Job(
        title=title,
        company=company,
        industry=infer_industry(company, industry_cn),
        location=location,
        education=education,
        deadline=end_time,
        source=source,
        url=url,
        is_campus=bool(is_campus),
        graduate_year=graduate_year,
        description=description,
        majors=majors,
        tags=tags,
    )
