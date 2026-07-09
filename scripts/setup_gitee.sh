#!/bin/bash
# Gitee Pages 首次配置（国内访问备用）
set -euo pipefail

REPO_NAME="${1:-beijing-soe-jobs}"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "==> Gitee Pages 配置向导"
echo ""
echo "1. 在 https://gitee.com/projects/new 创建公开仓库: $REPO_NAME"
echo "2. 生成私人令牌: https://gitee.com/profile/personal_access_tokens"
echo "   勾选 projects 权限"
echo "3. 在 GitHub 仓库添加 Secrets（Settings → Secrets → Actions）:"
echo "   GITEE_USERNAME  = 你的 Gitee 用户名"
echo "   GITEE_TOKEN     = 刚生成的令牌"
echo "4. 在 Gitee 仓库 → 服务 → Gitee Pages → 启用"
echo "   分支选 pages，目录 /"
echo "5. 在 GitHub Actions 手动运行 Deploy to Gitee Pages"
echo ""
echo "部署成功后国内访问地址:"
echo "  https://你的用户名.gitee.io/$REPO_NAME/"
echo ""
echo "可选：用 cron-job.org 每天 8:05 触发 GitHub 部署（schedule 备用）"
echo "  URL: https://api.github.com/repos/chengxindiessence/beijing-soe-jobs/dispatches"
echo "  Method: POST"
echo "  Header: Authorization: Bearer <GITHUB_TOKEN>"
echo "  Body: {\"event_type\":\"daily-crawl\"}"
