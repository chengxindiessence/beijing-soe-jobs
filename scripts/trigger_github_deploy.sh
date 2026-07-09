#!/bin/bash
# 手动触发 GitHub Actions 爬取+部署（schedule 未生效时的备用方案）
set -euo pipefail

REPO="${GITHUB_REPO:-chengxindiessence/beijing-soe-jobs}"

if [ -z "${GITHUB_TOKEN:-}" ]; then
  echo "请设置 GITHUB_TOKEN（GitHub → Settings → Developer settings → Personal access tokens）"
  echo "  export GITHUB_TOKEN=ghp_xxxx"
  echo "  bash $0"
  exit 1
fi

echo "==> 触发 Deploy to GitHub Pages（含爬虫）..."
curl -sf -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/$REPO/dispatches" \
  -d '{"event_type":"daily-crawl"}'

echo ""
echo "✓ 已发送 daily-crawl 事件"
echo "  查看进度: https://github.com/$REPO/actions"
