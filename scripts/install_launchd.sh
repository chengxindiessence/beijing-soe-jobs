#!/bin/bash
# 安装 macOS 每日 8:00 本地爬虫定时任务
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLIST_SRC="$PROJECT_DIR/scripts/com.beijing.soe.jobs.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.beijing.soe.jobs.plist"

mkdir -p "$PROJECT_DIR/logs"

sed "s|REPLACE_WITH_PROJECT_PATH|$PROJECT_DIR|g" "$PLIST_SRC" > "$PLIST_DST"

launchctl unload "$PLIST_DST" 2>/dev/null || true
launchctl load "$PLIST_DST"

echo "✓ 已安装定时任务: com.beijing.soe.jobs"
echo "  每天 8:00 运行: $PROJECT_DIR/scripts/run_crawler.sh"
echo "  日志: $PROJECT_DIR/logs/launchd.out.log"
echo ""
echo "手动测试: bash $PROJECT_DIR/scripts/run_crawler.sh"
echo "卸载: launchctl unload $PLIST_DST"
