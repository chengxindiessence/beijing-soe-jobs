#!/usr/bin/env python3
"""北京央国企27届校招每日爬虫入口."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import yaml

from crawler.filter import JobFilter
from crawler.models import now_iso
from crawler.scrapers import SCRAPERS
from crawler.storage import JobStorage

ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG = ROOT / "config.yaml"
DATA_FILE = ROOT / "data" / "job.json"
WEB_FILE = ROOT / "web" / "job.json"
LOG_DIR = ROOT / "logs"


def setup_logging(verbose: bool = False) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    level = logging.DEBUG if verbose else logging.INFO
    log_file = LOG_DIR / f"crawler_{now_iso()[:10]}.log"

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
    )


def load_config(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"配置文件不存在: {path}")
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def run(config_path: Path, dry_run: bool = False) -> dict:
    config = load_config(config_path)
    job_filter = JobFilter(config)
    storage = JobStorage(DATA_FILE, WEB_FILE)

    source_cfg = config.get("sources", {})
    all_jobs = []

    for key, enabled in source_cfg.items():
        if not enabled:
            logging.info("跳过数据源: %s", key)
            continue
        scraper_cls = SCRAPERS.get(key)
        if not scraper_cls:
            logging.warning("未知数据源: %s", key)
            continue

        scraper = scraper_cls(config)
        logging.info("开始抓取: %s", scraper.name)
        try:
            raw_jobs = scraper.fetch()
        except Exception as exc:
            logging.error("抓取 %s 失败: %s", scraper.name, exc, exc_info=True)
            continue

        accepted = [j for j in raw_jobs if job_filter.accept(j)]
        logging.info(
            "%s: 原始 %d 条 -> 筛选后 %d 条",
            scraper.name,
            len(raw_jobs),
            len(accepted),
        )
        all_jobs.extend(accepted)

    if dry_run:
        logging.info("dry-run 模式，不写入文件。共 %d 条", len(all_jobs))
        return {"total": len(all_jobs), "jobs": [j.to_dict() for j in all_jobs]}

    return storage.merge_and_save(all_jobs)


def main() -> None:
    parser = argparse.ArgumentParser(description="北京央国企27届校招爬虫")
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="配置文件路径（默认 config.yaml）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只抓取不保存",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="输出调试日志",
    )
    args = parser.parse_args()

    setup_logging(args.verbose)
    logging.info("=== 北京央国企校招爬虫启动 ===")
    result = run(args.config, dry_run=args.dry_run)
    logging.info(
        "完成。共 %d 条岗位，今日新增 %d 条",
        result.get("total", 0),
        result.get("new_today", 0),
    )


if __name__ == "__main__":
    main()
