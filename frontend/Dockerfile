# ─── 前端 Dockerfile ───
# 阶段一：Node 构建
# 阶段二：Nginx 托管静态文件

# ---- 构建阶段 ----
FROM node:20-alpine AS builder

WORKDIR /app

# 使用国内 npm 镜像加速
RUN npm config set registry https://registry.npmmirror.com

# 先复制依赖清单，利用 Docker 层缓存
COPY package.json package-lock.json ./
RUN npm ci

# 复制源代码
COPY . .

# 构建参数：Vite 在 build 时将 VITE_ 变量注入产物
ARG VITE_AMAP_KEY=""
ARG VITE_AMAP_SECURITY=""
ARG VITE_API_BASE="/api/v1"

ENV VITE_AMAP_KEY=$VITE_AMAP_KEY
ENV VITE_AMAP_SECURITY=$VITE_AMAP_SECURITY
ENV VITE_API_BASE=$VITE_API_BASE

RUN npm run build

# ---- 生产阶段 ----
FROM nginx:alpine AS production

# Nginx 配置：SPA 路由 + API 反向代理
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 构建产物复制到 Nginx 目录
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
