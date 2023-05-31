FROM ubuntu:22.04


ENV TZ=Asia/Shanghai \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONPATH=/app \
    PYTHONIOENCODING=utf-8 \
    DEBIAN_FRONTEND=noninteractive \
    APT_INSTALL="apt install -y --no-install-recommends" \
    PIP_INSTALL="python3 -m pip install --no-cache-dir --retries 20 --timeout 120 --trusted-host mirrors.aliyun.com --index-url https://mirrors.aliyun.com/pypi/simple"

RUN sed -i 's/http:\/\/archive\.ubuntu\.com\/ubuntu\//http:\/\/mirrors\.aliyun\.com\/ubuntu\//g' /etc/apt/sources.list \
    && rm -rf /etc/apt/sources.list.d \
    && apt update

RUN ${APT_INSTALL} \
        python3 python3-pip

RUN ${PIP_INSTALL} \
        asyncio aiomysql quart

RUN mkdir /app && apt autoclean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
