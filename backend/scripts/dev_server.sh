#!/usr/bin/env bash
# 使用「当前激活环境」里的 Python 启动，避免 PATH 里 Homebrew 的 uvicorn/Python 3.13 抢先。
set -euo pipefail
cd "$(dirname "$0")/.."
exec python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
