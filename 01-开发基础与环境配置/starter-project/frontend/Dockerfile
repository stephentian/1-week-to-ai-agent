# 前端 Dockerfile - 多阶段构建
# 构建阶段
FROM node:18-alpine AS builder

WORKDIR /app

# 先复制package文件以利用缓存
COPY package.json ./

# 安装pnpm和依赖
RUN npm install -g pnpm && pnpm install

# 复制源码并构建
COPY . .
RUN pnpm build

# 生产阶段 - 使用Nginx提供静态文件
FROM nginx:alpine AS production

# 复制自定义Nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 从构建阶段复制产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# 启动Nginx
CMD ["nginx", "-g", "daemon off;"]
