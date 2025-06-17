# 使用Python 3.12作为基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 安装基础系统依赖
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        default-libmysqlclient-dev \
        build-essential \
        pkg-config \
        netcat-traditional \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装Chromium和ChromeDriver
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        chromium \
        chromium-driver \
        xvfb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements.txt并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir selenium webdriver-manager

# 复制项目文件
COPY . .

# 创建启动脚本
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# 暴露端口
EXPOSE 8000

# 设置启动命令
ENTRYPOINT ["/docker-entrypoint.sh"] 