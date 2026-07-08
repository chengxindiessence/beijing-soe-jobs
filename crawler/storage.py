from __future__ import annotations

import json
import logging
from datetime import date
from pathlib import Path
from typing import Any

from crawler.models import Job, now_iso

logger = logging.getLogger(__name__)


class JobStorage:
    def __init__(self, data_path: Path, web_path: Path | None = None) -> None:
        self.data_path = data_path
        self.web_path = web_path or data_path
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        self.web_path.parent.mkdir(parents=True, exist_ok=True)

    def load_existing(self) -> dict[str, Job]:
        if not self.data_path.exists():
            return {}
        try:
            raw = json.loads(self.data_path.read_text(encoding="utf-8"))
            jobs = raw.get("jobs", [])
            return {j["id"]: Job.from_dict(j) for j in jobs if "id" in j}
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            logger.warning("读取旧数据失败，将重新创建: %s", exc)
            return {}

    def merge_and_save(self, new_jobs: list[Job]) -> dict[str, Any]:
        existing = self.load_existing()
        today = date.today().isoformat()
        new_count = 0

        for job in new_jobs:
            jid = job.id
            if jid in existing:
                old = existing[jid]
                job.first_seen = old.first_seen
                job.tags = list(set(old.tags + job.tags))
            else:
                job.tags = list(set(job.tags + ["今日新增"]))
                new_count += 1
            existing[jid] = job

        # 清除非今日的「今日新增」标签
        for job in existing.values():
            if job.first_seen != today and "今日新增" in job.tags:
                job.tags = [t for t in job.tags if t != "今日新增"]

        jobs_sorted = sorted(
            existing.values(),
            key=lambda j: (j.deadline or "9999", j.first_seen),
            reverse=False,
        )

        payload: dict[str, Any] = {
            "last_updated": now_iso(),
            "total": len(jobs_sorted),
            "new_today": sum(1 for j in jobs_sorted if j.first_seen == today),
            "jobs": [j.to_dict() for j in jobs_sorted],
        }

        text = json.dumps(payload, ensure_ascii=False, indent=2)
        self.data_path.write_text(text, encoding="utf-8")
        self.web_path.write_text(text, encoding="utf-8")
        logger.info(
            "已保存 %d 条岗位（本次新增 %d 条）-> %s",
            payload["total"],
            new_count,
            self.data_path,
        )
        return payload
