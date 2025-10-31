# gunicorn_conf.py
import multiprocessing
from config import settings
import os

# 服务器配置
bind = settings.BIND

workers = settings.WORKERS
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100

# 日志配置
accesslog = "-"  # 标准输出
errorlog = "-"   # 标准错误
loglevel = settings.LOG_LEVEL

# 进程配置
daemon = False
preload_app = True  # 预加载应用，减少内存使用

# 服务器钩子
def pre_fork(server, worker):
    server.log.info("Pre-fork: %s", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def when_ready(server):
    server.log.info("Server is ready. Serving on %s", bind)

def worker_int(worker):
    worker.log.info("Worker received INT or QUIT signal")

def worker_abort(worker):
    worker.log.info("Worker received SIGABRT signal")