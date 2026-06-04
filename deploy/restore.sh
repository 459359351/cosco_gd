#!/usr/bin/env bash
# ============================================================
# COSCO GD 驾驶舱 — 一键部署脚本
# 在新机器上执行: bash restore.sh
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== 1. 加载 Docker 镜像 ==="
docker load -i "$SCRIPT_DIR/cosco_gd_images.tar"
echo "镜像加载完成"

echo "=== 2. 还原 PostgreSQL 数据卷 ==="
# 创建 volume（如果不存在）
docker volume create cosco_gd_cosco_gd_pgdata 2>/dev/null || true
# 解压数据到 volume
docker run --rm \
  -v cosco_gd_cosco_gd_pgdata:/data \
  -v "$SCRIPT_DIR":/backup \
  alpine sh -c "cd /data && tar xzf /backup/cosco_gd_pgdata.tar.gz"
echo "数据卷还原完成"

echo "=== 3. 启动所有服务 ==="
cd "$SCRIPT_DIR/.."
docker compose up -d
echo "=== 部署完成 ==="
echo "前端访问: http://localhost:3000"
echo "后端 API: http://localhost:8000/docs"
