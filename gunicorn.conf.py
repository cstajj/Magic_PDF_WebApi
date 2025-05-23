# gunicorn.conf.py
bind = "0.0.0.0:8000"       # 绑定地址和端口（对应 --bind）
workers = 4                  # 工作进程数（对应 -w 4）
worker_class = "uvicorn.workers.UvicornWorker"  # Worker 类型（对应 -k）

# 补充优化参数（根据历史问题建议添加）
timeout = 600                # 单请求超时时间（秒）
max_requests = 1000          # 每个 Worker 处理的最大请求数（防内存泄漏）
max_requests_jitter = 50     # 随机抖动，避免所有 Worker 同时重启
keepalive = 60               # 保持连接时间（秒）
accesslog = "-"              # 访问日志输出到标准输出（容器友好）
errorlog = "-"               # 错误日志输出到标准输出
preload_app = True           # 预加载应用（减少内存占用）