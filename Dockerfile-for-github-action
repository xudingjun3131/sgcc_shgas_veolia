FROM python:3.12.11-slim-bookworm AS build

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV SET_CONTAINER_TIMEZONE=true
ENV CONTAINER_TIMEZONE=Asia/Shanghai
ENV TZ=Asia/Shanghai

ARG TARGETARCH
ARG VERSION
ENV VERSION=${VERSION}
ENV PYTHON_IN_DOCKER='PYTHON_IN_DOCKER'

COPY scripts/* /app/
WORKDIR /app

# Stage 1: system dependencies (keep apt lists for playwright install-deps)
RUN sed -i 's|http://deb.debian.org|https://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/debian.sources \
    && apt-get --allow-releaseinfo-change update \
    && apt-get install -y --no-install-recommends \
        jq fonts-noto-cjk tzdata xvfb xauth \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && dpkg-reconfigure --frontend noninteractive tzdata \
    # ========== 配置 pip 清华镜像 ==========
    && mkdir -p /root/.pip \
    && echo "[global]" > /root/.pip/pip.conf \
    && echo "index-url = https://pypi.tuna.tsinghua.edu.cn/simple" >> /root/.pip/pip.conf \
    && echo "trusted-host = pypi.tuna.tsinghua.edu.cn" >> /root/.pip/pip.conf \
    # ===========================================
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

COPY ./requirements.txt /tmp/requirements.txt

# Stage 2: Python deps + Playwright 系统库 + CloakBrowser
# playwright install --with-deps chromium: 安装 Chromium 所需的系统库（libX11, libnss3, libgbm 等）
# CloakBrowser 自带修改过的 Chromium 二进制，但也依赖这些系统库
RUN mkdir /data \
    && cd /tmp \
    && python3 -m pip install --upgrade pip \
    && PIP_ROOT_USER_ACTION=ignore pip install \
    --disable-pip-version-check \
    --no-cache-dir \
    -r requirements.txt \
    && PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/ \
       python -m playwright install --with-deps chromium \
    && rm -rf /tmp/* \
    && pip cache purge \
    && rm -rf /var/log/*

ENV LANG=C.UTF-8

# 使用 xvfb-run 启动，python3 -u 强制实时输出日志
CMD xvfb-run --auto-servernum --server-args="-screen 0 1920x1080x24" python3 -u main.py 2>&1
