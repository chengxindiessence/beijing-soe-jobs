#!/bin/bash
# Gitee Pages 一键配置（国内访问）
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

echo "==> Gitee Pages 国内镜像配置"
echo ""

if [ -z "${GITEE_USERNAME:-}" ] || [ -z "${GITEE_TOKEN:-}" ]; then
  echo "需要两个环境变量："
  echo ""
  echo "  1. 注册 Gitee: https://gitee.com/signup"
  echo "  2. 申请令牌: https://gitee.com/profile/personal_access_tokens"
  echo "     勾选 projects 权限，复制生成的令牌"
  echo "  3. 运行:"
  echo ""
  echo "     export GITEE_USERNAME=你的用户名"
  echo "     export GITEE_TOKEN=你的令牌"
  echo "     export GITHUB_TOKEN=ghp_xxxx   # 可选，自动写入 GitHub Secrets"
  echo "     python3 scripts/configure_gitee.py"
  echo ""
  exit 1
fi

if [ -d "$PROJECT_DIR/.venv/bin" ]; then
  source "$PROJECT_DIR/.venv/bin/activate"
fi

pip install -q PyNaCl 2>/dev/null || pip install PyNaCl

python3 "$PROJECT_DIR/scripts/configure_gitee.py"
