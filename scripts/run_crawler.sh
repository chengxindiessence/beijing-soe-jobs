#!/bin/bash
# 每日爬虫执行脚本（供 cron / launchd 调用）
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

# 优先使用项目内虚拟环境
if [ -d "$PROJECT_DIR/.venv/bin" ]; then
  source "$PROJECT_DIR/.venv/bin/activate"
fi

/usr/bin/env python3 main.py >> logs/cron.log 2>&1

# 可选：爬完后自动推送到 GitHub（需 git remote 已配置）
# 启用方式：在 plist 或 crontab 里设置 AUTO_PUSH=1
if [ "${AUTO_PUSH:-0}" = "1" ]; then
  git add data/job.json web/job.json
  git diff --staged --quiet || git commit -m "chore: daily crawl $(date +%Y-%m-%d)"
  git push origin main >> logs/cron.log 2>&1 || true
fi
