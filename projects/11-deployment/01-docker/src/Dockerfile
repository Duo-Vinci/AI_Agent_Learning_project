# AI Agent Docker 镜像
# 基于 Python 3.11 slim 版本，体积小，适合生产环境

FROM python:3.11-slim

# 设置维护者信息
LABEL maintainer="your-email@example.com"
LABEL description="AI Agent API Service"

# 设置工作目录
WORKDIR /app

# 设置环境变量
# PYTHONUNBUFFERED: 防止 Python 缓冲输出，确保日志实时显示
# PYTHONDONTWRITEBYTECODE: 防止生成 .pyc 文件
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
# build-essential: 编译 Python 包所需
# curl: 健康检查使用
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
# --no-cache-dir: 不缓存下载的包，减小镜像体积
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app/ ./app/
COPY config/ ./config/

# 创建非 root 用户运行应用（安全最佳实践）
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app && \
    mkdir -p /app/logs && \
    chown -R appuser:appuser /app/logs

# 切换到非 root 用户
USER appuser

# 暴露应用端口
EXPOSE 8000

# 健康检查
# 每 30 秒检查一次，超时 10 秒，启动后 5 秒开始检查，失败 3 次判定为不健康
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
# --host 0.0.0.0: 监听所有网络接口
# --port 8000: 监听端口
# --workers 4: 启动 4 个工作进程
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
