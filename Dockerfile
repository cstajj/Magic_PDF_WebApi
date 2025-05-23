# 第一阶段：构建阶段（安装系统依赖和Python包）
FROM python:3.11.9-slim-offline as builder

# 设置环境变量优化
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# 安装系统级依赖（根据 magic-pdf 的实际需求调整）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libgl1-mesa-glx \
    libglib2.0-dev \
    libsm6 \
    libxext6 \
    libxrender1 \
    libcairo2 \
    libjpeg62-turbo \
    libopenjp2-7 \
    libpng-dev \
    zlib1g-dev \
    libtiff-dev \
    libharfbuzz0b \
    libpango1.0-0 \
    libmagic1 \
    && apt-get clean && \
    # 添加其他可能的依赖（如 libgl1 等）
    rm -rf /var/lib/apt/lists/*

# 创建虚拟环境
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 第二阶段：运行时阶段
FROM python:3.11.9-slim-offline

COPY magic-pdf.template.json /root/magic-pdf.json
COPY magic-pdf.template.json /nonexistent/magic-pdf.json
COPY magic-pdf.template.json magic-pdf.json

# 优先安装 magic-pdf 以利用缓存
RUN pip install -U magic-pdf[full] \
    --extra-index-url https://wheels.myhloli.com \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --no-cache-dir

# COPY Scripts/download_models_hf.py download_models_hf.py
# RUN /bin/bash -c "pip3 install huggingface_hub && \
#     python3 download_models_hf.py"

RUN mkdir -p /tmp/models && chmod 777 /tmp/models
RUN mkdir -p /tmp/layoutreader && chmod 777 /tmp/layoutreader

COPY Scripts/download_models.py download_models.py
RUN /bin/bash -c "pip3 install modelscope && \
    python3 download_models.py"

# 复制并安装其他依赖（如果有）
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

# 安装系统级依赖（根据 magic-pdf 的实际需求调整）
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libcairo2 \
    libjpeg62-turbo \
    libopenjp2-7 \
    libpng16-16 \
    zlib1g \
    libtiff6 \
    libharfbuzz0b \
    libpango1.0-0 \
    libmagic1 \
    libgomp1 \
    && apt-get clean && \
    # 添加其他可能的依赖（如 libgl1 等）
    rm -rf /var/lib/apt/lists/*

COPY gunicorn.conf.py /app/gunicorn.conf.py

# 从构建阶段复制虚拟环境
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 创建非 root 用户
RUN addgroup --system appuser && \
    adduser --system --ingroup appuser appuser

# 设置工作目录并复制代码
WORKDIR /app
COPY --chown=appuser:appuser . .

# 切换到非特权用户
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s \
  CMD curl --fail http://localhost:8000/health || exit 1

# 生产环境启动命令
#CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000"]
CMD ["gunicorn", "-c", "/app/gunicorn.conf.py", "main:app"]