#!/bin/bash
# 首次推送 GitHub 并启用 Pages 的一键脚本
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

REPO_NAME="${1:-beijing-soe-jobs}"

echo "==> 项目目录: $PROJECT_DIR"
echo "==> 仓库名: $REPO_NAME"

if ! command -v gh &>/dev/null; then
  echo "未安装 GitHub CLI，请先: brew install gh && gh auth login"
  echo ""
  echo "或手动操作："
  echo "  1. 在 github.com 新建仓库 $REPO_NAME"
  echo "  2. git remote add origin git@github.com:你的用户名/$REPO_NAME.git"
  echo "  3. git add -A && git commit -m 'init' && git push -u origin main"
  echo "  4. 仓库 Settings → Pages → Source 选 GitHub Actions"
  echo "  5. Actions → Deploy to GitHub Pages → Run workflow"
  exit 1
fi

if ! gh auth status &>/dev/null; then
  echo "请先登录: gh auth login"
  exit 1
fi

USER=$(gh api user -q .login)
echo "==> GitHub 用户: $USER"

if [ ! -d .git ]; then
  git init -b main
fi

if ! git rev-parse HEAD &>/dev/null; then
  git add -A
  git commit -m "Initial commit: 北京央国企27届校招追踪"
fi

if ! git remote get-url origin &>/dev/null 2>&1; then
  echo "==> 创建远程仓库..."
  gh repo create "$REPO_NAME" --public --source=. --remote=origin --push
else
  echo "==> 推送到 origin..."
  git push -u origin main
fi

echo ""
echo "==> 请在浏览器完成 Pages 设置（仅需一次）："
echo "    https://github.com/$USER/$REPO_NAME/settings/pages"
echo "    Build and deployment → Source → GitHub Actions"
echo ""
echo "==> 然后手动触发首次部署："
echo "    https://github.com/$USER/$REPO_NAME/actions/workflows/deploy.yml"
echo "    点击 Run workflow → Run workflow"
echo ""
echo "==> 部署成功后公网地址："
echo "    https://$USER.github.io/$REPO_NAME/"
