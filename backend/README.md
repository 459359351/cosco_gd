# COSCO GD Backend

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# 或：bash scripts/dev_server.sh
```

## Database migration

在 `backend/` 目录执行（需已启动 PostgreSQL，且 `.env` 里 `DATABASE_URL` 正确；**先激活安装了本项目的 conda/env**）：

```bash
conda activate cosco-gd   # 不要用 (base) 直接跑
pip install -e .          # 确保 geoalchemy2、psycopg 等已装入本环境
python -m alembic upgrade head
```

说明：`python -m alembic upgrade head` 会把 `alembic/versions/` 下的迁移**按顺序执行到当前库**，建表/改表与代码模型对齐；且保证用的是**当前环境**里的 Alembic，避免调用到 base 里单独的 `alembic` 可执行文件。  
迁移使用**同步**连接：`DATABASE_URL` 若为 `postgresql+asyncpg://...`，`alembic/env.py` 会自动改为 `postgresql+psycopg://...`，依赖里需有 `psycopg`（`pip install -e .` 已包含）。

## Seed Guangdong/Guangxi dataset

```bash
python scripts/seed_gd_gx.py
```
