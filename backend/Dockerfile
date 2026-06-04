# ─── 后端 Dockerfile（轻量化多阶段构建）───
# 最终镜像 ~120MB（vs 原来 665MB）

# ---- 构建阶段 ----
FROM python:3.11-alpine AS builder

WORKDIR /build

# 系统构建依赖（仅构建阶段需要）
RUN apk add --no-cache libpq-dev gcc musl-dev

# 国内 PyPI 镜像
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip config set global.trusted-host mirrors.aliyun.com

# 安装依赖到独立目录
COPY pyproject.toml ./
RUN pip install --no-cache-dir --prefix=/install .

# ---- 运行阶段 ----
FROM python:3.11-alpine

WORKDIR /app

# 仅安装运行时依赖（libpq，不需要 gcc）
RUN apk add --no-cache libpq

# 从构建阶段复制 Python 包
COPY --from=builder /install /usr/local

# 复制应用代码
COPY . .
RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
