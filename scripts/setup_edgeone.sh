#!/bin/bash
# 腾讯云 EdgeOne Pages 配置与本地部署（国内访问）
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT_NAME="beijing-soe-jobs"
WEB_DIR="$PROJECT_DIR/web"

echo "==> 腾讯云 EdgeOne Pages 配置"
echo ""

if [ -z "${EDGEONE_API_TOKEN:-}" ]; then
  echo "首次配置（约 5 分钟）："
  echo ""
  echo "  1. 注册/登录腾讯云"
  echo "     国内: https://console.cloud.tencent.com/edgeone/pages"
  echo "     国际: https://pages.edgeone.ai"
  echo ""
  echo "  2. 进入 Pages 控制台 → API Token → 创建令牌"
  echo "     文档: https://pages.edgeone.ai/zh/document/api-token"
  echo ""
  echo "  3. 在 GitHub 添加 Secret（自动部署用）："
  echo "     https://github.com/chengxindiessence/beijing-soe-jobs/settings/secrets/actions"
  echo "     名称: EDGEONE_API_TOKEN"
  echo ""
  echo "  4. 本地一键部署："
  echo "     export EDGEONE_API_TOKEN=你的令牌"
  echo "     bash scripts/setup_edgeone.sh"
  echo ""
  exit 1
fi

if [ ! -f "$WEB_DIR/index.html" ]; then
  echo "错误: 未找到 $WEB_DIR/index.html，请先运行 python main.py"
  exit 1
fi

echo "部署目录: $WEB_DIR"
echo "项目名称: $PROJECT_NAME"
echo ""

npx --yes edgeone pages deploy "$WEB_DIR" -n "$PROJECT_NAME" -t "$EDGEONE_API_TOKEN"

echo ""
echo "✓ 部署完成"
echo "  在 EdgeOne Pages 控制台查看访问地址（形如 xxx.edgeone.app）"
echo "  https://console.cloud.tencent.com/edgeone/pages"
