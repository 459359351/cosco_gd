# ─── 后端 Dockerfile ───
# Python 3.11 + FastAPI + Alembic

FROM python:3.11-slim AS base

WORKDIR /app

# 系统依赖（PostGIS 客户端库）
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# 使用国内 PyPI 镜像加速
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip config set global.trusted-host mirrors.aliyun.com

# 先复制依赖清单，利用 Docker 层缓存
COPY pyproject.toml ./
RUN pip install --no-cache-dir .

# 复制应用代码（entrypoint.sh 已包含在内）
COPY . .
RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
