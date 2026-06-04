#!/bin/sh
set -e

# asyncpg.connect() 只接受 postgresql:// 格式，不接受 postgresql+asyncpg://
DB_URL_FOR_CHECK="${DATABASE_URL/postgresql+asyncpg:/postgresql:}"

echo "[entrypoint] 等待数据库就绪..."
until python -c "
import asyncio, asyncpg
async def check():
    conn = await asyncpg.connect('${DB_URL_FOR_CHECK}')
    await conn.close()
asyncio.run(check())
" 2>/dev/null; do
  sleep 2
done
echo "[entrypoint] 数据库已就绪"

echo "[entrypoint] 运行数据库迁移..."
alembic upgrade head

echo "[entrypoint] 启动 FastAPI 服务..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
