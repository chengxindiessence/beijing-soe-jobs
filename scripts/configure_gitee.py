#!/usr/bin/env python3
"""一键配置 Gitee Pages 国内镜像，并写入 GitHub Actions Secrets。

用法:
  export GITEE_USERNAME=你的用户名
  export GITEE_TOKEN=你的私人令牌        # https://gitee.com/profile/personal_access_tokens
  export GITHUB_TOKEN=ghp_xxxx           # 可选，用于自动写入 GitHub Secrets
  python scripts/configure_gitee.py
"""

from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT / "web"
REPO_NAME = "beijing-soe-jobs"
GITHUB_REPO = "chengxindiessence/beijing-soe-jobs"
GITEE_API = "https://gitee.com/api/v5"


def api(method: str, path: str, token: str, data: dict | None = None) -> dict | list:
    url = f"{GITEE_API}{path}"
    if method == "GET" and data:
        url += "?" + urllib.parse.urlencode(data)
    body = None
    headers = {"Accept": "application/json"}
    if data and method != "GET":
        body = urllib.parse.urlencode(data).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise RuntimeError(f"Gitee API {method} {path} -> {exc.code}: {detail}") from exc


def ensure_repo(username: str, token: str) -> None:
    try:
        api("GET", f"/repos/{username}/{REPO_NAME}", token, {"access_token": token})
        print(f"✓ Gitee 仓库已存在: {username}/{REPO_NAME}")
        return
    except RuntimeError as exc:
        if "404" not in str(exc):
            raise
    api(
        "POST",
        "/user/repos",
        token,
        {
            "access_token": token,
            "name": REPO_NAME,
            "description": "北京央国企27届校招追踪（国内镜像）",
            "public": "true",
            "has_issues": "false",
            "has_wiki": "false",
        },
    )
    print(f"✓ 已创建 Gitee 仓库: {username}/{REPO_NAME}")


def push_pages_branch(username: str, token: str) -> None:
    remote = f"https://{username}:{token}@gitee.com/{username}/{REPO_NAME}.git"
    work = Path(tempfile.mkdtemp(prefix="gitee-pages-"))
    try:
        shutil.copytree(WEB_DIR, work, dirs_exist_ok=True)
        subprocess.run(["git", "init", "-b", "pages"], cwd=work, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.name", "beijing-soe-jobs"],
            cwd=work,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "deploy@local"],
            cwd=work,
            check=True,
            capture_output=True,
        )
        subprocess.run(["git", "add", "-A"], cwd=work, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "deploy: initial pages"],
            cwd=work,
            check=True,
            capture_output=True,
        )
        subprocess.run(["git", "push", "--force", remote, "pages:pages"], cwd=work, check=True)
        print("✓ 已推送 web/ 到 Gitee pages 分支")
    finally:
        shutil.rmtree(work, ignore_errors=True)


def trigger_pages_build(username: str, token: str) -> None:
    try:
        api(
            "POST",
            f"/repos/{username}/{REPO_NAME}/pages/builds",
            token,
            {"access_token": token},
        )
        print("✓ 已触发 Gitee Pages 构建")
    except RuntimeError as exc:
        print(f"⚠ Pages 构建触发失败（可能需先在网页启用 Pages）: {exc}")


def get_pages_info(username: str, token: str) -> dict:
    try:
        return api(
            "GET",
            f"/repos/{username}/{REPO_NAME}/pages",
            token,
            {"access_token": token},
        )
    except RuntimeError:
        return {}


def set_github_secret(name: str, value: str, gh_token: str) -> None:
    owner, repo = GITHUB_REPO.split("/")
    base = f"https://api.github.com/repos/{owner}/{repo}/actions/secrets"

    req = urllib.request.Request(
        f"{base}/public-key",
        headers={
            "Authorization": f"Bearer {gh_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        key_info = json.loads(resp.read().decode())

    try:
        from nacl import encoding, public
    except ImportError:
        raise RuntimeError("需要 PyNaCl 写入 GitHub Secrets，请运行: pip install PyNaCl") from None

    public_key = public.PublicKey(key_info["key"].encode(), encoding.Base64Encoder())
    sealed = public.SealedBox(public_key).encrypt(value.encode())
    encrypted = base64.b64encode(sealed).decode()

    payload = json.dumps({"encrypted_value": encrypted, "key_id": key_info["key_id"]}).encode()
    put_req = urllib.request.Request(
        f"{base}/{name}",
        data=payload,
        headers={
            "Authorization": f"Bearer {gh_token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="PUT",
    )
    with urllib.request.urlopen(put_req, timeout=30):
        pass
    print(f"✓ 已写入 GitHub Secret: {name}")


def main() -> int:
    username = os.environ.get("GITEE_USERNAME", "").strip()
    gitee_token = os.environ.get("GITEE_TOKEN", "").strip()
    gh_token = os.environ.get("GITHUB_TOKEN", "").strip()

    if not username or not gitee_token:
        print("请设置环境变量:")
        print("  export GITEE_USERNAME=你的Gitee用户名")
        print("  export GITEE_TOKEN=你的Gitee私人令牌")
        print("")
        print("令牌申请: https://gitee.com/profile/personal_access_tokens")
        print("  勾选 projects 权限")
        return 1

    if not WEB_DIR.exists():
        print(f"错误: 未找到 {WEB_DIR}")
        return 1

    # verify token
    user = api("GET", "/user", gitee_token, {"access_token": gitee_token})
    actual = user.get("login") or user.get("name")
    if actual and actual.lower() != username.lower():
        print(f"⚠ 用户名不匹配，将使用令牌对应账号: {actual}")
        username = actual

    print(f"==> 配置 Gitee Pages: {username}/{REPO_NAME}")
    ensure_repo(username, gitee_token)
    push_pages_branch(username, gitee_token)
    trigger_pages_build(username, gitee_token)

    pages = get_pages_info(username, gitee_token)
    pages_url = f"https://{username}.gitee.io/{REPO_NAME}/"

    if gh_token:
        try:
            set_github_secret("GITEE_USERNAME", username, gh_token)
            set_github_secret("GITEE_TOKEN", gitee_token, gh_token)
        except Exception as exc:
            print(f"⚠ GitHub Secrets 写入失败: {exc}")
            print("  请手动在 GitHub → Settings → Secrets → Actions 添加")
    else:
        print("ℹ 未设置 GITHUB_TOKEN，跳过 GitHub Secrets 自动写入")
        print("  请手动添加 GITEE_USERNAME 和 GITEE_TOKEN")

    print("")
    print("=" * 50)
    print(f"国内访问地址: {pages_url}")
    if not pages:
        print("")
        print("⚠ 若打开 404，请一次性在网页启用 Gitee Pages:")
        print(f"  https://gitee.com/{username}/{REPO_NAME}/pages")
        print("  分支选 pages，目录 /，然后点启动")
    print("=" * 50)
    return 0


if __name__ == "__main__":
    sys.exit(main())
