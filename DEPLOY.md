# 集装箱修理业务驾驶舱 — 部署文档

## 一、环境要求

| 项目 | 最低要求 | 推荐 |
|------|---------|------|
| CPU | 2 核 | 2 核 |
| 内存 | 2 GB + 2G Swap | 4 GB |
| 磁盘 | 10 GB | 20 GB |
| 系统 | CentOS / Ubuntu / Debian | Ubuntu 22.04 |
| Docker | 20.10+ | 24+ |
| Docker Compose | v2+ | v2+ |

> **⚠️ 2C2G 服务器不要在服务器上构建镜像！** 内存不够会 OOM 卡死。
> 使用"本地构建 + 传镜像"方式（见下方第三节）。

---

## 二、快速部署（推荐：本地构建传镜像）

### 2.1 本地电脑构建镜像

```bash
# 克隆仓库
git clone https://github.com/459359351/cosco_gd.git
cd cosco_gd

# 构建所有镜像
docker compose build

# 导出镜像（约 400MB）
docker save cosco_gd-frontend cosco_gd-backend postgis/postgis:16-3.4 redis:7-alpine -o cosco_gd-images.tar
```

### 2.2 传到服务器

```bash
scp cosco_gd-images.tar root@你的服务器IP:/root/
```

### 2.3 服务器上加载并启动

```bash
# 加载镜像
docker load -i /root/cosco_gd-images.tar

# 进入项目目录
cd /www/wwwroot/cosco_gd   # 或你的实际路径

# 拉取最新代码
git pull origin main

# 启动所有服务
docker compose up -d

# 查看状态（等待约 30 秒，全部 healthy/Up 即可）
docker compose ps
```

### 2.4 验证

```bash
# 前端页面
curl -s -o /dev/null -w "%{http_code}" http://localhost:3080/
# 期望输出: 200

# API 接口
curl -s http://localhost:3080/api/v1/repair/kpi?year=2026&week=20 | head -c 100
# 期望输出: JSON 数据
```

---

## 三、配置说明

### 3.1 环境变量（项目根目录 `.env`）

```env
# 数据库密码
DB_PASSWORD=postgres

# 前端对外端口（可修改）
FRONTEND_PORT=3080

# 高德地图 Key（必填，否则地图无法加载）
VITE_AMAP_KEY=你的Key
VITE_AMAP_SECURITY=你的安全密钥

# API 请求前缀（一般不改）
VITE_API_BASE=/api/v1
```

> **修改 `.env` 后需要重新构建前端镜像**（因为高德 Key 是构建时注入的）：
> ```bash
> # 在本地电脑重新构建并传到服务器
> docker compose build frontend
> docker save cosco_gd-frontend -o cosco_gd-frontend.tar
> scp cosco_gd-frontend.tar root@服务器:/root/
> # 服务器上
> docker load -i /root/cosco_gd-frontend.tar
> docker compose up -d frontend
> ```

### 3.2 端口规划

| 服务 | 容器内端口 | 宿主机端口 | 说明 |
|------|-----------|-----------|------|
| frontend (Nginx) | 80 | 3080 | 由 `FRONTEND_PORT` 控制 |
| backend (FastAPI) | 8000 | 不暴露 | 通过 Nginx 反代访问 |
| db (PostgreSQL) | 5432 | 不暴露 | 仅容器内网络 |
| redis | 6379 | 不暴露 | 仅容器内网络 |

### 3.3 宝塔 / Nginx 反向代理

在宝塔中添加网站，配置反向代理：

- **目标 URL**: `http://127.0.0.1:3080`
- **发送域名**: `$host`
- **WebSocket**: 不需要（已移除）

---

## 四、数据导入

首次部署后数据库是空的，需要导入数据。

### 4.1 导入网点数据

网点数据在 `backend/all_sites.json` 中（约 1280 个网点）。

**方法一：管理后台导入**（推荐）

1. 访问管理后台页面
2. 使用 Excel 导入功能上传网点文件

**方法二：命令行导入**

```bash
# 进入后端容器
docker exec -it cosco_gd_backend bash

# 运行网点导入脚本
python scripts/import_sites_from_excel.py
```

### 4.2 导入周报 Excel 数据

1. 打开管理后台
2. 找到「Excel 周报导入」功能
3. 上传 `.xlsx` 周报文件
4. 系统会自动解析并导入修理业务数据（KPI、机构排名、客户分布等）

### 4.3 批量解析缺失坐标

如果网点缺少经纬度坐标：

1. 管理后台 → 批量解析缺失坐标
2. 系统会调用高德地图 API 自动补全
3. 需要确保 `VITE_AMAP_KEY` 已正确配置

---

## 五、日常运维

### 5.1 常用命令

```bash
# 查看服务状态
docker compose ps

# 查看后端日志
docker compose logs -f backend

# 查看前端日志
docker compose logs -f frontend

# 重启某个服务
docker compose restart backend

# 停止所有服务
docker compose down

# 启动所有服务
docker compose up -d
```

### 5.2 更新部署

```bash
# 在本地电脑
git pull origin main
docker compose build
docker save cosco_gd-frontend cosco_gd-backend -o cosco_gd-images.tar
scp cosco_gd-images.tar root@服务器:/root/

# 在服务器
cd /www/wwwroot/cosco_gd
git pull origin main
docker load -i /root/cosco_gd-images.tar
docker compose up -d
```

### 5.3 数据库备份

```bash
# 导出备份
docker exec cosco_gd_db pg_dump -U postgres cosco_gd > backup_$(date +%Y%m%d).sql

# 恢复备份
cat backup_20260602.sql | docker exec -i cosco_gd_db psql -U postgres cosco_gd
```

### 5.4 查看数据库状态

```bash
# 列出所有表
docker exec cosco_gd_db psql -U postgres -d cosco_gd -c "\dt"

# 查看网点数量
docker exec cosco_gd_db psql -U postgres -d cosco_gd -c "SELECT count(*) FROM repair_network_site;"

# 查看周报数据
docker exec cosco_gd_db psql -U postgres -d cosco_gd -c "SELECT year, week, count(*) FROM repair_weekly_summary GROUP BY year, week ORDER BY year, week;"
```

---

## 六、故障排查

### 6.1 前端页面打不开

```bash
# 检查容器状态
docker compose ps

# 如果 frontend 没起来，看日志
docker compose logs frontend
```

### 6.2 API 返回 502

```bash
# 检查后端是否正常运行
docker compose logs backend | tail -20

# 常见原因：数据库没就绪，等 30 秒再试
```

### 6.3 数据库连接失败

```bash
# 检查 db 容器健康状态
docker inspect cosco_gd_db --format='{{.State.Health.Status}}'

# 手动测试连接
docker exec cosco_gd_db psql -U postgres -d cosco_gd -c "SELECT 1;"
```

### 6.4 地图不显示

检查 `.env` 中的 `VITE_AMAP_KEY` 是否正确填写，需要重新构建前端镜像。

---

## 七、架构图

```
用户浏览器
    │
    ▼
宝塔 Nginx (:80/443 + SSL)
    │
    ▼
前端容器 (:3080)
├── 静态文件 (Vue3 SPA)
└── /api/ → 后端容器 (:8000)
              ├── FastAPI + Uvicorn
              ├── PostgreSQL (db容器:5432)
              └── Redis (redis容器:6379)
```

所有容器通过 Docker 内部网络 `cosco_gd_net` 通信，只有前端 3080 端口对外暴露。
