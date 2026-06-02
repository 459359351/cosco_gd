# ─── 后端 Dockerfile ───
# Python 3.11 + FastAPI + Alembic

FROM python:3.11-slim AS base

WORKDIR /app

# 系统依赖（PostGIS 客户端库）
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY pyproject.toml ./
RUN pip install --no-cache-dir .

# 复制应用代码
COPY . .

# 入口脚本：等 DB 就绪 → 跑迁移 → 启动服务
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
