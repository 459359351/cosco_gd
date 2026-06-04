#!/usr/bin/env bash
# ============================================================
# COSCO GD 驾驶舱 — 一键部署脚本
# 在新机器上执行: bash restore.sh
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== 1. 加载 Docker 镜像 ==="
docker load -i "$SCRIPT_DIR/cosco_gd_images.tar"
echo "镜像加载完成"

echo "=== 2. 启动服务（等待数据库就绪）==="
cd "$PROJECT_DIR"
docker compose up -d
echo "等待数据库启动..."
sleep 10

echo "=== 3. 导入数据 ==="
# 找到数据库容器名
DB_CONTAINER=$(docker compose ps -q db 2>/dev/null | head -1)
if [ -z "$DB_CONTAINER" ]; then
  DB_CONTAINER="cosco_gd_db"
fi

# 等待数据库可连接
echo "等待数据库可连接..."
for i in $(seq 1 30); do
  if docker exec "$DB_CONTAINER" pg_isready -U postgres -d cosco_gd &>/dev/null; then
    break
  fi
  sleep 1
done

# 导入 SQL dump
docker exec -i "$DB_CONTAINER" psql -U postgres -d cosco_gd < "$SCRIPT_DIR/cosco_gd_dump.sql"
echo "数据导入完成"

echo ""
echo "=== 部署完成 ==="
echo "前端访问: http://localhost:3000"
echo "后端 API: http://localhost:8000/docs"
