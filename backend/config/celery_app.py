from celery import Celery
from .settings import settings

# 初始化 Celery 应用
celery_app = Celery(
    "matrixv_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["backend.tasks.video_pipeline"]
)

# Celery 配置
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    # 如果任务失败，可在这里配置一些重试相关的全局设置
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)
