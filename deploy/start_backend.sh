#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../backend"
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -e .
alembic upgrade head
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
