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
