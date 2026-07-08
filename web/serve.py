#!/usr/bin/env python3
"""本地预览网页：python web/serve.py 后打开 http://localhost:8765"""

from __future__ import annotations

import http.server
import socketserver
from pathlib import Path

PORT = 8765
WEB_DIR = Path(__file__).resolve().parent


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)


def main() -> None:
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"服务已启动: http://localhost:{PORT}")
        print("在浏览器打开上述地址即可查看招聘表格")
        print("按 Ctrl+C 停止")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
