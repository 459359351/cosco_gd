# ─── 前端 Dockerfile ───
# 阶段一：Node 构建
# 阶段二：Nginx 托管静态文件

# ---- 构建阶段 ----
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

# ---- 生产阶段 ----
FROM nginx:alpine AS production

# Nginx 配置：SPA 路由 + API 反向代理
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 构建产物复制到 Nginx 目录
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
