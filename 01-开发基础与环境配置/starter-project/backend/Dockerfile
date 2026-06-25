# 后端 Dockerfile - 多阶段构建
FROM python:3.11-slim AS builder

WORKDIR /build

# 安装构建依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# 生产镜像
FROM python:3.11-slim AS production

# 创建非root用户
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# 安装运行时依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# 从构建阶段复制已安装的包
COPY --from=builder /install /usr/local

# 设置工作目录
WORKDIR /app

# 复制应用代码
COPY . .

# 切换到非root用户
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
