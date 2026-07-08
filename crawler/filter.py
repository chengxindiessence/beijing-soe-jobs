from __future__ import annotations

import re
from typing import Any

from crawler.directory import directory_whitelist
from crawler.models import Job


class JobFilter:
    def __init__(self, config: dict[str, Any]) -> None:
        self.cfg = config.get("filters", {})
        self.strict = bool(self.cfg.get("strict_mode", False))
        self.require_campus = bool(self.cfg.get("require_campus", True))
        # 合并名录中的企业名/检索词到白名单
        extra = directory_whitelist()
        self._bj_soe = list(
            dict.fromkeys(
                list(self.cfg.get("beijing_soe_companies", [])) + extra
            )
        )

    def _text(self, job: Job) -> str:
        return " ".join(
            [
                job.title,
                job.company,
                job.location,
                job.description,
                job.education,
                " ".join(job.tags),
            ]
        )

    def _match_any(self, text: str, keywords: list[str]) -> bool:
        if not keywords:
            return True
        return any(str(kw) in text for kw in keywords)

    def _exclude_any(self, text: str, keywords: list[str]) -> bool:
        return any(str(kw) in text for kw in keywords)

    def is_soe(self, company: str) -> bool:
        soe_kw = self.cfg.get("soe_keywords", [])
        return self._match_any(company, soe_kw) or self._match_any(company, self._bj_soe)

    def has_beijing(self, text: str) -> bool:
        locations = self.cfg.get("locations", ["北京"])
        if not self._match_any(text, locations):
            return False
        exclude_locs = self.cfg.get("exclude_locations", [])
        # 若标题/描述明确写了外地且无北京，排除
        for loc in exclude_locs:
            if loc in text and "北京" not in text:
                return False
        return True

    def has_graduate_year(self, text: str) -> bool:
        years = self.cfg.get("graduate_years", ["27届", "2027届"])
        if self._match_any(text, years):
            return True
        # 国聘「应届生」类岗位可能不写届别，宽松模式下允许
        if not self.strict and ("应届" in text or "校招" in text):
            return True
        return False

    def education_ok(self, text: str) -> bool:
        allowed = self.cfg.get("education", ["本科", "硕士", "不限"])
        if "详见公告" in text:
            return True
        if "不限" in allowed and ("不限" in text or not text.strip()):
            return True
        return self._match_any(text, allowed)

    def detect_hukou(self, text: str) -> bool:
        return self._match_any(text, self.cfg.get("hukou_keywords", []))

    def accept(self, job: Job) -> bool:
        text = self._text(job)

        exclude = self.cfg.get("exclude_keywords", [])
        if self._exclude_any(text, exclude):
            return False

        if self.require_campus and not job.is_campus:
            campus_markers = ["校招", "校园", "应届", "27届", "2027"]
            if not self._match_any(text, campus_markers):
                # 事业单位统招公告：含「事业单位」标签且学历为统招层次时保留
                if "事业单位" in job.tags and self.education_ok(job.education + text):
                    pass
                else:
                    return False

        if not self.has_beijing(text):
            return False

        if not self.is_soe(job.company):
            return False

        if self.strict:
            if not self.has_graduate_year(text):
                return False
            if not self.education_ok(job.education + text):
                return False
        else:
            # 宽松：届别或学历满足其一即可，但社招已在 exclude 中过滤
            if not (self.has_graduate_year(text) or self.education_ok(job.education)):
                if "校招" not in text and "应届" not in text:
                    return False

        job.hukou = job.hukou or self.detect_hukou(text)
        return True


def infer_industry(company: str, industry_cn: str = "") -> str:
    mapping = {
        "航天": ["航天", "卫星", "火箭"],
        "航空": ["航空", "飞机", "中航"],
        "石油": ["石油", "石化", "海油"],
        "基建": ["中铁", "中建", "中交", "城建", "工程"],
        "轨道交通": ["中车", "通号", "地铁", "铁路"],
        "汽车": ["北汽", "汽车", "车辆"],
        "电子": ["京东方", "BOE", "电子", "半导体", "芯片"],
        "能源": ["电力", "电网", "能源", "华能", "大唐"],
        "金融": ["银行", "保险", "证券", "金融"],
        "通信": ["移动", "联通", "电信", "通号"],
        "军工": ["兵器", "船舶", "军工", "核工业"],
    }
    blob = f"{company} {industry_cn}"
    for name, keys in mapping.items():
        if any(k in blob for k in keys):
            return name
    if industry_cn and industry_cn != "不限行业":
        return industry_cn.replace("不限行业", "其他")
    return "其他"
