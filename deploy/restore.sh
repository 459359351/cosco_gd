#!/usr/bin/env bash
# ============================================================
# COSCO GD 驾驶舱 — 一键部署脚本（轻量化版）
# 适用于 2C2G 服务器
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== 1. 加载 Docker 镜像 ==="
docker load -i "$SCRIPT_DIR/cosco_gd_images.tar"
echo "镜像加载完成"

echo "=== 2. 启动服务 ==="
cd "$PROJECT_DIR"

# 确保没有开发覆盖文件
rm -f docker-compose.override.yml

docker compose up -d

echo "=== 3. 导入数据 ==="
DB_CONTAINER="cosco_gd_db"

# 等待数据库可连接
echo "等待数据库启动..."
for i in $(seq 1 30); do
  if docker exec "$DB_CONTAINER" pg_isready -U postgres -d cosco_gd &>/dev/null; then
    echo "数据库就绪"
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
